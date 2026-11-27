
import { request } from './http'
import type { AuthCredentials, AuthResponse, User } from '../types/auth'

export function register(credentials: AuthCredentials) {
    return request<User>('/auth/register', {
        method: 'POST',
        body: credentials,
    })
}

export function login(credentials: AuthCredentials) {
    return request<AuthResponse>('/auth/login', {
        method: 'POST',
        body: credentials,
    })
}

export function getCurrentUser(token: string) {
    return request<User>('/auth/me', {
        token,
    })
}
