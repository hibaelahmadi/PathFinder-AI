import { request } from './http'
import type { StudentProfileRead, StudentProfileUpdate } from '../types/profile'

export function getMyProfile(token: string, signal?: AbortSignal) {
    return request<StudentProfileRead>('/profiles/me', {
        token,
        signal,
    })
}

export function updateMyProfile(
    payload: StudentProfileUpdate,
    token: string,
) {
    return request<StudentProfileRead>('/profiles/me', {
        method: 'PATCH',
        body: payload,
        token,
    })
}
