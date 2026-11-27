
export type AuthCredentials = {
    email: string
    password: string
}

export type AuthResponse = {
    access_token: string
    token_type: 'bearer'
}

export type User = {
    id: number
    email: string
    role: 'student' | 'admin'
    is_active: boolean
    created_at: string
}
