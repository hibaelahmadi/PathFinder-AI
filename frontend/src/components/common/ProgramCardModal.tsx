import { useEffect, useState } from 'react'
import { getP4ProgramCard } from '../../services/catalogueService'
import { ApiError } from '../../services/http'
import type { P4ProgramCard } from '../../types/catalogue'
import { formatCodeLabel, formatDuration } from '../../utils/formatters'
import { LoadingCard, StatusBanner, VerificationBadge } from './StateFeedback'

type ProgramCardModalProps = {
    programId: string
    onClose: () => void
    onCompare?: (programId: string) => void
}

export function ProgramCardModal({
    programId,
    onClose,
    onCompare,
}: ProgramCardModalProps) {
    const [card, setCard] = useState<P4ProgramCard | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const controller = new AbortController()

        getP4ProgramCard(programId, controller.signal)
            .then((data) => {
                if (!controller.signal.aborted) {
                    setCard(data)
                    setError(null)
                }
            })
            .catch((err) => {
                if (controller.signal.aborted) {
                    return
                }
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to load program details.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoading(false)
                }
            })

        return () => controller.abort()
    }, [programId])

    useEffect(() => {
        function handleKey(event: KeyboardEvent) {
            if (event.key === 'Escape') {
                onClose()
            }
        }
        window.addEventListener('keydown', handleKey)
        return () => window.removeEventListener('keydown', handleKey)
    }, [onClose])

    return (
        <div
            className="modal-backdrop"
            role="presentation"
            onClick={(event) => {
                if (event.target === event.currentTarget) {
                    onClose()
                }
            }}
        >
            <div
                className="detail-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="program-modal-title"
            >
                <div className="modal-header">
                    <div>
                        <span className="eyebrow">Exploration Program Card · {programId}</span>
                        <h2 id="program-modal-title">
                            {card ? card.name : 'Program details'}
                        </h2>
                    </div>
                    <button
                        type="button"
                        className="btn-ghost"
                        onClick={onClose}
                        aria-label="Close program details"
                    >
                        Close
                    </button>
                </div>

                {isLoading && <LoadingCard label="Loading program card from catalogue..." />}
                {error && <StatusBanner tone="error" message={error} />}

                {card && !isLoading && (
                    <div className="modal-body">
                        <div className="badge-row">
                            <VerificationBadge verified={card.admissions_current_verified} />
                            <span className="badge badge-neutral">
                                {formatCodeLabel(card.institution.sector)}
                            </span>
                            {card.institution.city && (
                                <span className="badge badge-neutral">
                                    {card.institution.city}
                                </span>
                            )}
                            <span className="badge badge-neutral">
                                {card.direct_post_bac ? 'Direct post-Bac' : formatCodeLabel(card.entry_route)}
                            </span>
                        </div>

                        <p className="modal-institution">
                            <strong>{card.institution.name}</strong>
                            {card.institution.acronym ? ` (${card.institution.acronym})` : ''}
                            {card.institution.parent_name ? ` · ${card.institution.parent_name}` : ''}
                        </p>

                        <dl className="detail-grid">
                            <div>
                                <dt>Field</dt>
                                <dd>{formatCodeLabel(card.field)}</dd>
                            </div>
                            <div>
                                <dt>Degree / Cycle</dt>
                                <dd>{card.degree_type ?? 'Not specified'}</dd>
                            </div>
                            <div>
                                <dt>Duration</dt>
                                <dd>{formatDuration(card.duration_months)}</dd>
                            </div>
                            <div>
                                <dt>Annual Cost</dt>
                                <dd>{card.cost_label}</dd>
                            </div>
                            <div>
                                <dt>Academic Year</dt>
                                <dd>{card.academic_year ?? 'Not specified'}</dd>
                            </div>
                            <div>
                                <dt>Eligibility Status</dt>
                                <dd>{formatCodeLabel(card.eligibility)}</dd>
                            </div>
                        </dl>

                        {card.description && (
                            <div className="detail-block">
                                <h3>Description</h3>
                                <p>{card.description}</p>
                            </div>
                        )}

                        {card.options && (
                            <div className="detail-block">
                                <h3>Options / Specializations</h3>
                                <p>{card.options}</p>
                            </div>
                        )}

                        <div className="detail-columns">
                            <div>
                                <h3>Editorial Interest Tags</h3>
                                <div className="chip-list">
                                    {card.interests.length > 0 ? (
                                        card.interests.map((tag) => (
                                            <span key={tag} className="chip">
                                                {formatCodeLabel(tag)}
                                            </span>
                                        ))
                                    ) : (
                                        <span className="muted-text">None listed</span>
                                    )}
                                </div>
                            </div>
                            <div>
                                <h3>Editorial Career Leads</h3>
                                <div className="chip-list">
                                    {card.career_paths.length > 0 ? (
                                        card.career_paths.map((career) => (
                                            <span key={career} className="chip">
                                                {formatCodeLabel(career)}
                                            </span>
                                        ))
                                    ) : (
                                        <span className="muted-text">None listed</span>
                                    )}
                                </div>
                            </div>
                        </div>

                        {card.warnings.length > 0 && (
                            <div className="warning-box">
                                <h3>Verification Notices</h3>
                                <ul>
                                    {card.warnings.map((warning) => (
                                        <li key={warning}>{warning}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {card.notes && (
                            <div className="detail-block">
                                <h3>Documentary Notes</h3>
                                <p className="muted-text">{card.notes}</p>
                            </div>
                        )}

                        <div className="detail-block">
                            <h3>Official Sources</h3>
                            {card.sources.map((source) => (
                                <div key={source.source_id} className="source-row">
                                    <div>
                                        <strong>{source.title}</strong>
                                        <p className="muted-text">
                                            {source.publisher ?? 'Official publisher'} ·{' '}
                                            {source.academic_year ?? 'Year unspecified'}
                                            {card.source_locator ? ` · ${card.source_locator}` : ''}
                                            {source.checked_at ? ` · Checked ${source.checked_at}` : ''}
                                        </p>
                                    </div>
                                    <a
                                        href={source.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="btn-secondary btn-sm"
                                    >
                                        Open source
                                    </a>
                                </div>
                            ))}
                        </div>

                        <div className="modal-footer">
                            {onCompare && (
                                <button
                                    type="button"
                                    className="btn-primary"
                                    onClick={() => {
                                        onCompare(card.program_id)
                                        onClose()
                                    }}
                                >
                                    Add to comparison
                                </button>
                            )}
                            <button type="button" className="btn-secondary" onClick={onClose}>
                                Done
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
