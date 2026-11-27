import type { ReactNode } from 'react'

type BannerTone = 'error' | 'warning' | 'info' | 'success'

type StatusBannerProps = {
    tone: BannerTone
    title?: string
    message: string
    details?: string[]
    action?: ReactNode
    onDismiss?: () => void
}

export function StatusBanner({
    tone,
    title,
    message,
    details,
    action,
    onDismiss,
}: StatusBannerProps) {
    return (
        <div
            className={`status-banner status-banner-${tone}`}
            role={tone === 'error' || tone === 'warning' ? 'alert' : 'status'}
        >
            <div className="status-banner-body">
                {title && <strong>{title}</strong>}
                <p>{message}</p>
                {details && details.length > 1 && (
                    <ul className="status-banner-list">
                        {details.map((detail, idx) => (
                            <li key={`${detail}-${idx}`}>{detail}</li>
                        ))}
                    </ul>
                )}
            </div>
            <div className="status-banner-actions">
                {action}
                {onDismiss && (
                    <button
                        type="button"
                        className="btn-ghost btn-sm"
                        onClick={onDismiss}
                        aria-label="Dismiss notification"
                    >
                        Dismiss
                    </button>
                )}
            </div>
        </div>
    )
}

type LoadingCardProps = {
    label?: string
}

export function LoadingCard({ label = 'Loading data...' }: LoadingCardProps) {
    return (
        <div className="state-card" role="status" aria-live="polite">
            <div className="spinner" aria-hidden="true" />
            <p>{label}</p>
        </div>
    )
}

type EmptyCardProps = {
    title: string
    description: string
    action?: ReactNode
}

export function EmptyCard({ title, description, action }: EmptyCardProps) {
    return (
        <div className="state-card">
            <h3>{title}</h3>
            <p>{description}</p>
            {action && <div className="state-card-action">{action}</div>}
        </div>
    )
}

type VerificationBadgeProps = {
    verified: boolean
    label?: string
}

export function VerificationBadge({ verified, label }: VerificationBadgeProps) {
    const text =
        label ?? (verified ? 'Admission verified' : 'Admission unverified — check official source')
    return (
        <span className={verified ? 'badge badge-verified' : 'badge badge-unverified'}>
            {text}
        </span>
    )
}

type ProtectedGateProps = {
    title: string
    description: string
    onSignIn: () => void
}

export function ProtectedGate({ title, description, onSignIn }: ProtectedGateProps) {
    return (
        <section className="panel gate-panel">
            <h2>{title}</h2>
            <p>{description}</p>
            <div className="gate-actions">
                <button type="button" className="btn-primary" onClick={onSignIn}>
                    Sign in or create a student account
                </button>
            </div>
        </section>
    )
}
