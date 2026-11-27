import {
    createContext,
    useCallback,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from 'react'

import type { User, AuthCredentials } from '../types/auth'
import { login as loginRequest, getCurrentUser } from '../services/authService'
import { saveToken, getToken, removeToken } from '../services/authStorage'
import { ApiError, setUnauthorizedHandler } from '../services/http'

type AuthContextType = {
    user: User | null
    token: string | null
    isLoading: boolean
    isAdmin: boolean
    sessionExpiredMessage: string | null
    clearSessionExpiredMessage: () => void
    login: (credentials: AuthCredentials) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

type AuthProviderProps = {
    children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(() => getToken())
    const [isLoading, setIsLoading] = useState(true)
    const [sessionExpiredMessage, setSessionExpiredMessage] = useState<string | null>(null)

    const clearSessionExpiredMessage = useCallback(() => {
        setSessionExpiredMessage(null)
    }, [])

    const handleExpiredSession = useCallback(() => {
        removeToken()
        setToken(null)
        setUser(null)
        setSessionExpiredMessage('Your session expired or is invalid. Please sign in again.')
    }, [])

    useEffect(() => {
        setUnauthorizedHandler(handleExpiredSession)
        return () => setUnauthorizedHandler(null)
    }, [handleExpiredSession])

    useEffect(() => {
        const controller = new AbortController()

        async function restoreSession() {
            const storedToken = getToken()

            if (!storedToken) {
                setToken(null)
                setIsLoading(false)
                return
            }

            try {
                const currentUser = await getCurrentUser(storedToken)
                if (!controller.signal.aborted) {
                    setToken(storedToken)
                    setUser(currentUser)
                }
            } catch (error) {
                if (controller.signal.aborted) {
                    return
                }
                if (error instanceof ApiError && error.status === 401) {
                    removeToken()
                    setToken(null)
                    setUser(null)
                    setSessionExpiredMessage(
                        'Your previous session expired. Please sign in again.',
                    )
                } else {
                    // Preserve token if backend is temporarily unreachable; user stays unverified until backend responds
                    removeToken()
                    setToken(null)
                    setUser(null)
                }
            } finally {
                if (!controller.signal.aborted) {
                    setIsLoading(false)
                }
            }
        }

        restoreSession()
        return () => controller.abort()
    }, [])

    async function login(credentials: AuthCredentials) {
        setSessionExpiredMessage(null)
        const response = await loginRequest(credentials)

        saveToken(response.access_token)
        setToken(response.access_token)

        const currentUser = await getCurrentUser(response.access_token)
        setUser(currentUser)
    }

    const logout = useCallback(() => {
        removeToken()
        setToken(null)
        setUser(null)
        setSessionExpiredMessage(null)
    }, [])

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                isLoading,
                isAdmin: user?.role === 'admin',
                sessionExpiredMessage,
                clearSessionExpiredMessage,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)

    if (!context) {
        throw new Error('useAuth must be used inside AuthProvider')
    }

    return context
}
