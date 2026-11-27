import { useState, type FormEvent } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { register } from '../../services/authService'
import { ApiError } from '../../services/http'

type AuthFormProps = {
    onClose: () => void
    initialMode?: 'login' | 'register'
}

function AuthForm({ onClose, initialMode = 'login' }: AuthFormProps) {
    const { login } = useAuth()

    const [mode, setMode] = useState<'login' | 'register'>(initialMode)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [message, setMessage] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        setError('')
        setMessage('')

        const trimmedEmail = email.trim()
        if (!trimmedEmail) {
            setError('Please enter your email address.')
            return
        }
        if (password.length < 15 || password.length > 128) {
            setError('Password must be between 15 and 128 characters.')
            return
        }

        setIsSubmitting(true)

        try {
            const credentials = { email: trimmedEmail, password }

            if (mode === 'register') {
                await register(credentials)

                setMode('login')
                setPassword('')
                setMessage('Student account created successfully. You can now sign in.')
            } else {
                await login(credentials)
                onClose()
            }
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message)
            } else {
                setError(
                    err instanceof Error
                        ? err.message
                        : 'Something went wrong. Please try again.',
                )
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <section className="auth-form">
            <h2 id="auth-title">
                {mode === 'login' ? 'Welcome back' : 'Create your student account'}
            </h2>

            <p>
                {mode === 'login'
                    ? 'Sign in to access your orientation questionnaire, profile, recommendations, and evidence search.'
                    : 'Join PathFinder AI to explore higher education pathways in Morocco.'}
            </p>

            <form onSubmit={handleSubmit} noValidate>
                <label htmlFor="auth-email">Email</label>
                <input
                    id="auth-email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="student@example.com"
                    autoComplete="email"
                    required
                    maxLength={254}
                />

                <label htmlFor="auth-password">Password</label>
                <input
                    id="auth-password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="15 to 128 characters"
                    autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                    minLength={15}
                    maxLength={128}
                    required
                />
                <span className="field-hint">
                    {mode === 'register'
                        ? 'New accounts are created as student accounts (15–128 characters required).'
                        : 'Minimum 15 characters.'}
                </span>

                {error && <p className="auth-error" role="alert">{error}</p>}
                {message && <p className="auth-success" role="status">{message}</p>}

                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting
                        ? 'Please wait...'
                        : mode === 'login'
                            ? 'Sign in'
                            : 'Create account'}
                </button>
            </form>

            <p className="auth-switch">
                {mode === 'login'
                    ? "Don't have an account?"
                    : 'Already have an account?'}
                {' '}
                <button
                    type="button"
                    onClick={() => {
                        setMode(mode === 'login' ? 'register' : 'login')
                        setError('')
                        setMessage('')
                    }}
                >
                    {mode === 'login' ? 'Create one' : 'Sign in'}
                </button>
            </p>

            <button type="button" className="auth-close" onClick={onClose}>
                Continue browsing public catalogue
            </button>
        </section>
    )
}

export default AuthForm
