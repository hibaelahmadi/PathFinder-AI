import { API_BASE_URL } from './api'

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE'

type RequestOptions = {
    method?: HttpMethod
    body?: unknown
    token?: string
    signal?: AbortSignal
}

export class ApiError extends Error {
    readonly status: number
    readonly details: string[]
    readonly isNetworkError: boolean

    constructor(
        message: string,
        status: number,
        details: string[] = [],
        isNetworkError = false,
    ) {
        super(message)
        this.name = 'ApiError'
        this.status = status
        this.details = details
        this.isNetworkError = isNetworkError
    }
}

type UnauthorizedHandler = () => void

let unauthorizedHandler: UnauthorizedHandler | null = null

export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
    unauthorizedHandler = handler
}

function formatValidationEntry(entry: unknown): string | null {
    if (typeof entry === 'string') {
        return entry
    }
    if (entry && typeof entry === 'object') {
        const record = entry as { loc?: unknown; msg?: unknown }
        if (typeof record.msg === 'string') {
            if (Array.isArray(record.loc) && record.loc.length > 0) {
                const field = String(record.loc[record.loc.length - 1])
                return `${field}: ${record.msg}`
            }
            return record.msg
        }
    }
    return null
}

function parseErrorPayload(rawText: string, status: number): { message: string; details: string[] } {
    if (status === 502 || status === 504) {
        return {
            message: 'Backend API is unreachable (HTTP ' + status + '). Make sure FastAPI is running on port 8000.',
            details: [],
        }
    }

    const trimmed = rawText.trim()
    if (!trimmed) {
        return {
            message: `Request failed with HTTP ${status}.`,
            details: [],
        }
    }

    try {
        const parsed = JSON.parse(trimmed) as { detail?: unknown; message?: unknown }
        if (typeof parsed.detail === 'string') {
            return { message: parsed.detail, details: [parsed.detail] }
        }
        if (Array.isArray(parsed.detail)) {
            const details = parsed.detail
                .map(formatValidationEntry)
                .filter((item): item is string => Boolean(item))
            if (details.length > 0) {
                return { message: details[0], details }
            }
        }
        if (typeof parsed.message === 'string') {
            return { message: parsed.message, details: [parsed.message] }
        }
    } catch {
        // Non-JSON text response
    }

    return { message: trimmed, details: [trimmed] }
}

export function buildQueryString(
    params: Record<string, string | number | boolean | null | undefined>,
): string {
    const searchParams = new URLSearchParams()
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== '') {
            searchParams.set(key, String(value))
        }
    }
    const qs = searchParams.toString()
    return qs ? `?${qs}` : ''
}

export async function request<T>(
    endpoint: string,
    options: RequestOptions = {},
): Promise<T> {
    const { method = 'GET', body, token, signal } = options

    const headers: Record<string, string> = {}
    if (body !== undefined) {
        headers['Content-Type'] = 'application/json'
    }
    if (token) {
        headers.Authorization = `Bearer ${token}`
    }

    let response: Response
    try {
        response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method,
            headers,
            body: body === undefined ? undefined : JSON.stringify(body),
            signal,
        })
    } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
            throw error
        }
        throw new ApiError(
            'Unable to reach the PathFinder AI server. Check your local connection and ensure the backend is running.',
            0,
            [],
            true,
        )
    }

    if (!response.ok) {
        const errorText = await response.text()
        const { message, details } = parseErrorPayload(errorText, response.status)

        if (response.status === 401 && token && unauthorizedHandler) {
            unauthorizedHandler()
        }

        throw new ApiError(message, response.status, details)
    }

    if (response.status === 204) {
        return undefined as T
    }

    return response.json() as Promise<T>
}
