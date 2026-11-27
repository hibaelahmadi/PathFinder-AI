import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { ApiError } from '../../services/http'
import { getSessionRecommendations } from '../../services/recommendationService'
import { getSessions } from '../../services/sessionService'
import type { Session } from '../../types/questionnaire'
import type {
    RecommendationRead,
    SessionRecommendations,
} from '../../types/recommendation'
import { formatCodeLabel, formatMad } from '../../utils/formatters'
import {
    EmptyCard,
    LoadingCard,
    StatusBanner,
    VerificationBadge,
} from '../common/StateFeedback'

type RecommendationsPageProps = {
    preferredSessionId: number | null
    onOpenProgram: (programId: string) => void
    onAddToCompare: (programId: string) => void
    onGoToQuestionnaire: () => void
}

function RecommendationCard({
    item,
    onOpenProgram,
    onAddToCompare,
}: {
    item: RecommendationRead
    onOpenProgram: (programId: string) => void
    onAddToCompare: (programId: string) => void
}) {
    return (
        <article className="rec-card">
            <div className="rec-card-header">
                <div>
                    <span className="eyebrow">
                        {item.program_code} · {item.institution_id}
                    </span>
                    <h3>{item.program}</h3>
                    <p className="muted-text">
                        {item.institution_name ?? 'Institution name not specified'}
                        {item.city ? ` · ${item.city}` : ' · City to verify'}
                    </p>
                </div>

                <div className="rec-score-box">
                    <span className="score-label">Compatibility</span>
                    <strong>
                        {item.score !== null ? item.score.toFixed(2) : 'Missing score'}
                    </strong>
                </div>
            </div>

            <div className="badge-row">
                <VerificationBadge verified={item.admissions_current_verified} />
                <span className="badge badge-neutral">
                    Eligibility: {formatCodeLabel(item.constraints.eligibility)}
                </span>
                <span className="badge badge-neutral">
                    Feasibility: {formatCodeLabel(item.constraints.feasibility)}
                </span>
                <span className="badge badge-neutral">
                    {formatMad(item.annual_cost)}
                </span>
                {item.academic_year && (
                    <span className="badge badge-neutral">
                        Year {item.academic_year}
                    </span>
                )}
            </div>

            {item.explanations.length > 0 && (
                <div className="rec-section">
                    <h4>Why this matches your profile</h4>
                    <ul>
                        {item.explanations.map((line, idx) => (
                            <li key={`${item.program_id}-exp-${idx}`}>{line}</li>
                        ))}
                    </ul>
                </div>
            )}

            {item.constraints.reasons.length > 0 && (
                <div className="rec-section">
                    <h4>Constraints &amp; notes</h4>
                    <ul>
                        {item.constraints.reasons.map((reason, idx) => (
                            <li key={`${item.program_id}-reason-${idx}`}>{reason}</li>
                        ))}
                    </ul>
                </div>
            )}

            <p className="muted-text rec-meta">
                Source: <strong>{item.source_id}</strong> ({item.source_locator}) · Status:{' '}
                {formatCodeLabel(item.status)} · Matching: {formatCodeLabel(item.matching_status)}
            </p>
            {item.notes && <p className="muted-text rec-notes">{item.notes}</p>}

            <div className="rec-actions">
                <button
                    type="button"
                    className="btn-primary btn-sm"
                    onClick={() => onOpenProgram(item.program_id)}
                >
                    Inspect card &amp; official source
                </button>
                <button
                    type="button"
                    className="btn-secondary btn-sm"
                    onClick={() => onAddToCompare(item.program_id)}
                >
                    Compare
                </button>
            </div>
        </article>
    )
}

export function RecommendationsPage({
    preferredSessionId,
    onOpenProgram,
    onAddToCompare,
    onGoToQuestionnaire,
}: RecommendationsPageProps) {
    const { token } = useAuth()

    const [sessions, setSessions] = useState<Session[]>([])
    const [selectedSessionId, setSelectedSessionId] = useState<number | null>(
        preferredSessionId,
    )
    const [topN, setTopN] = useState(10)
    const [data, setData] = useState<SessionRecommendations | null>(null)
    const [isLoadingSessions, setIsLoadingSessions] = useState(true)
    const [isLoadingRecs, setIsLoadingRecs] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!token) {
            return
        }
        const controller = new AbortController()

        getSessions(token, 0, 50, controller.signal)
            .then((list) => {
                if (controller.signal.aborted) {
                    return
                }
                setError(null)
                setSessions(list)

                const confirmed = list.filter(
                    (item) => item.status === 'completed' && item.profile_confirmed,
                )
                if (
                    preferredSessionId &&
                    confirmed.some((item) => item.id === preferredSessionId)
                ) {
                    setSelectedSessionId(preferredSessionId)
                } else if (confirmed.length > 0) {
                    setSelectedSessionId(confirmed[confirmed.length - 1].id)
                } else if (list.length > 0) {
                    setSelectedSessionId(list[list.length - 1].id)
                } else {
                    setSelectedSessionId(null)
                }
            })
            .catch((err) => {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to load questionnaire sessions.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoadingSessions(false)
                }
            })

        return () => controller.abort()
    }, [token, preferredSessionId])

    useEffect(() => {
        if (!token || selectedSessionId === null) {
            return
        }

        const controller = new AbortController()

        getSessionRecommendations(selectedSessionId, token, topN, controller.signal)
            .then((result) => {
                if (!controller.signal.aborted) {
                    setError(null)
                    setData(result)
                }
            })
            .catch((err) => {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                setData(null)
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to load recommendations.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoadingRecs(false)
                }
            })

        return () => controller.abort()
    }, [token, selectedSessionId, topN])

    const visibleData = selectedSessionId === null ? null : data

    return (
        <div className="workspace-stack">
            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <span className="eyebrow">GET /sessions/&#123;id&#125;/recommendations</span>
                        <h2>Academic Recommendations</h2>
                        <p>
                            Ranked exploration matches computed from your confirmed questionnaire
                            profile and the P4 exploration catalogue.
                        </p>
                    </div>
                    {sessions.length > 0 && (
                        <div className="controls-row">
                            <label className="inline-control">
                                <span>Session</span>
                                <select
                                    value={selectedSessionId ?? ''}
                                    onChange={(event) =>
                                        setSelectedSessionId(Number(event.target.value))
                                    }
                                >
                                    {sessions.map((session) => (
                                        <option key={session.id} value={session.id}>
                                            Session #{session.id} (
                                            {session.profile_confirmed ? 'Confirmed' : 'Unconfirmed'})
                                        </option>
                                    ))}
                                </select>
                            </label>
                            <label className="inline-control">
                                <span>Results</span>
                                <select
                                    value={topN}
                                    onChange={(event) => setTopN(Number(event.target.value))}
                                >
                                    {[5, 10, 20, 50, 100].map((val) => (
                                        <option key={val} value={val}>
                                            Top {val}
                                        </option>
                                    ))}
                                </select>
                            </label>
                        </div>
                    )}
                </div>

                <StatusBanner
                    tone="warning"
                    title="Important orientation notice"
                    message="A compatibility score reflects alignment with your declared preferences and known criteria — it is NOT an admission probability. Always verify active admission requirements on the official source."
                />

                {error && <StatusBanner tone="error" message={error} />}

                {isLoadingSessions || isLoadingRecs ? (
                    <LoadingCard label="Computing recommendations from backend..." />
                ) : sessions.length === 0 ? (
                    <EmptyCard
                        title="No questionnaire sessions found"
                        description="Complete and confirm an orientation questionnaire session first to receive personalized recommendations."
                        action={
                            <button
                                type="button"
                                className="btn-primary"
                                onClick={onGoToQuestionnaire}
                            >
                                Start questionnaire
                            </button>
                        }
                    />
                ) : !visibleData ? (
                    <EmptyCard
                        title="Session not ready for recommendations"
                        description="Confirm your questionnaire session first (or reopen and fix any invalid saved profile fields)."
                        action={
                            <button
                                type="button"
                                className="btn-primary"
                                onClick={onGoToQuestionnaire}
                            >
                                Open questionnaire
                            </button>
                        }
                    />
                ) : (
                    <div className="workspace-stack">
                        <div>
                            <h3 className="section-subtitle">
                                Primary Recommendations ({visibleData.recommendations.length} shown of{' '}
                                {visibleData.recommendations_total})
                            </h3>
                            {visibleData.recommendations.length === 0 ? (
                                <EmptyCard
                                    title="No direct matches found"
                                    description="No programs matched all of your current constraints directly. Check the 'Locations to verify' section below or adjust your questionnaire answers."
                                />
                            ) : (
                                <div className="cards-grid">
                                    {visibleData.recommendations.map((item) => (
                                        <RecommendationCard
                                            key={item.program_id}
                                            item={item}
                                            onOpenProgram={onOpenProgram}
                                            onAddToCompare={onAddToCompare}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>

                        {visibleData.location_to_verify_total > 0 && (
                            <div>
                                <h3 className="section-subtitle">
                                    Programs with Location to Verify ({visibleData.location_to_verify.length}{' '}
                                    shown of {visibleData.location_to_verify_total})
                                </h3>
                                <p className="muted-text">
                                    Because relocation was declined, programs without a confirmed
                                    campus city are listed separately here for verification.
                                </p>
                                <div className="cards-grid">
                                    {visibleData.location_to_verify.map((item) => (
                                        <RecommendationCard
                                            key={item.program_id}
                                            item={item}
                                            onOpenProgram={onOpenProgram}
                                            onAddToCompare={onAddToCompare}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </section>
        </div>
    )
}

export default RecommendationsPage
