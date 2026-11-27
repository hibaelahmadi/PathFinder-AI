import { buildQueryString, request } from './http'
import type {
    Session,
    SessionActionRequest,
    QuestionnaireActionResponse,
    QuestionnaireAnswerRead,
} from '../types/questionnaire'

export function createSession(token: string) {
    return request<Session>('/sessions', {
        method: 'POST',
        token,
    })
}

export function getSessions(
    token: string,
    offset = 0,
    limit = 50,
    signal?: AbortSignal,
) {
    const qs = buildQueryString({ offset, limit })
    return request<Session[]>(`/sessions${qs}`, {
        token,
        signal,
    })
}

export function getSession(sessionId: number, token: string, signal?: AbortSignal) {
    return request<Session>(`/sessions/${sessionId}`, {
        token,
        signal,
    })
}

export function getSessionState(
    sessionId: number,
    token: string,
    signal?: AbortSignal,
) {
    return request<QuestionnaireActionResponse>(`/sessions/${sessionId}/state`, {
        token,
        signal,
    })
}

export function getSessionAnswers(
    sessionId: number,
    token: string,
    offset = 0,
    limit = 100,
    signal?: AbortSignal,
) {
    const qs = buildQueryString({ offset, limit })
    return request<QuestionnaireAnswerRead[]>(`/sessions/${sessionId}/answers${qs}`, {
        token,
        signal,
    })
}

export function sendSessionAction(
    sessionId: number,
    action: SessionActionRequest,
    token: string,
) {
    return request<QuestionnaireActionResponse>(
        `/sessions/${sessionId}/actions`,
        {
            method: 'POST',
            body: action,
            token,
        },
    )
}
