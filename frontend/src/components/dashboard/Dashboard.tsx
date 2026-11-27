import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { ApiError } from '../../services/http'
import { getMyProfile } from '../../services/profileService'
import { getSessionRecommendations } from '../../services/recommendationService'
import { getSessions } from '../../services/sessionService'
import type { AppPage } from '../../types/navigation'
import type { StudentProfileRead } from '../../types/profile'
import type { Session } from '../../types/questionnaire'
import type { SessionRecommendations } from '../../types/recommendation'
import {
    computeProfileCompletion,
    formatDateTime,
    formatMad,
} from '../../utils/formatters'
import { EmptyCard, LoadingCard, StatusBanner, VerificationBadge } from '../common/StateFeedback'
import ProfileSummary from '../profile/ProfileSummary'

type DashboardProps = {
    onNavigate: (page: AppPage) => void
    onSignIn: () => void
    onOpenProgram: (programId: string) => void
    profileRefreshKey: number
}

function Dashboard({
    onNavigate,
    onSignIn,
    onOpenProgram,
    profileRefreshKey,
}: DashboardProps) {
    const { user, token, isAdmin } = useAuth()

    const [profile, setProfile] = useState<StudentProfileRead | null>(null)
    const [sessions, setSessions] = useState<Session[]>([])
    const [recPreview, setRecPreview] = useState<SessionRecommendations | null>(null)
    const [isLoading, setIsLoading] = useState(Boolean(token))
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!token) {
            return
        }

        const controller = new AbortController()

        Promise.allSettled([
            getMyProfile(token, controller.signal),
            getSessions(token, 0, 20, controller.signal),
        ])
            .then(async ([profileRes, sessionsRes]) => {
                if (controller.signal.aborted) {
                    return
                }
                setError(null)

                if (profileRes.status === 'fulfilled') {
                    setProfile(profileRes.value)
                } else {
                    const reason = profileRes.reason
                    if (reason instanceof ApiError && reason.status !== 404) {
                        setError(reason.message)
                    }
                    setProfile(null)
                }

                if (sessionsRes.status === 'fulfilled') {
                    const list = sessionsRes.value
                    setSessions(list)

                    const confirmed = [...list]
                        .reverse()
                        .find((s) => s.status === 'completed' && s.profile_confirmed)
                    if (confirmed) {
                        try {
                            const recs = await getSessionRecommendations(
                                confirmed.id,
                                token,
                                3,
                                controller.signal,
                            )
                            if (!controller.signal.aborted) {
                                setRecPreview(recs)
                            }
                        } catch {
                            // Handled gracefully by Recommendations page
                        }
                    } else {
                        setRecPreview(null)
                    }
                } else {
                    const reason = sessionsRes.reason
                    if (reason instanceof ApiError) {
                        setError((prev) => prev ?? reason.message)
                    }
                }
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoading(false)
                }
            })

        return () => controller.abort()
    }, [token, profileRefreshKey])

    const activeProfile = token ? profile : null
    const activeSessions = token ? sessions : []
    const activeRecPreview = token ? recPreview : null
    const activeError = token ? error : null
    const latestSession =
        activeSessions.length > 0 ? activeSessions[activeSessions.length - 1] : null
    const confirmedSession = [...activeSessions]
        .reverse()
        .find((s) => s.status === 'completed' && s.profile_confirmed)
    const completion = computeProfileCompletion(activeProfile)

    const nextAction = !user
        ? {
              title: 'Sign in to personalize your orientation',
              description:
                  'Create a student account or sign in to complete the adaptive questionnaire, save your profile, and receive personalized recommendations.',
              buttonLabel: 'Sign in / Register',
              action: onSignIn,
          }
        : !latestSession
            ? {
                  title: 'Start your orientation questionnaire',
                  description:
                      'Answer the adaptive backend questionnaire about your Bac stream, preferred cities, interests, and budget.',
                  buttonLabel: 'Start questionnaire',
                  action: () => onNavigate('questionnaire'),
              }
            : !confirmedSession
                ? {
                      title: `Continue Session #${latestSession.id}`,
                      description:
                          latestSession.expected_question_code === null
                              ? 'Your questions are answered — review and confirm your profile snapshot to unlock recommendations.'
                              : `Resume from question "${latestSession.expected_question_code}" to complete your orientation profile.`,
                      buttonLabel: 'Resume questionnaire',
                      action: () => onNavigate('questionnaire'),
                  }
                : completion < 50
                    ? {
                          title: 'Complete your saved student profile',
                          description: `Your student profile is ${completion}% complete. Add your subject grades and goals for your permanent record.`,
                          buttonLabel: 'Edit profile',
                          action: () => onNavigate('profile'),
                      }
                    : {
                          title: 'Explore your recommendations and official evidence',
                          description:
                              'Review your matched programs, compare options side by side, and verify official sources.',
                          buttonLabel: 'View all recommendations',
                          action: () => onNavigate('recommendations'),
                      }

    return (
        <div className="workspace-stack">
            <section className="hero-banner">
                <div>
                    <span className="eyebrow">Moroccan Post-Bac Orientation Platform</span>
                    <h2>
                        {user
                            ? `Welcome back, ${user.email}`
                            : 'Explore verified higher education pathways in Morocco'}
                    </h2>
                    <p>
                        PathFinder AI connects your Baccalaureate profile and preferences with an
                        exploration catalogue backed by official Moroccan institutional registries.
                        Compatibility scores help you explore options — always verify active
                        admissions directly with official sources.
                    </p>
                </div>
                <div className="hero-action-card">
                    <span className="eyebrow">Recommended next step</span>
                    <h3>{nextAction.title}</h3>
                    <p>{nextAction.description}</p>
                    <button
                        type="button"
                        className="btn-primary"
                        onClick={nextAction.action}
                    >
                        {nextAction.buttonLabel}
                    </button>
                </div>
            </section>

            {activeError && <StatusBanner tone="error" message={activeError} />}

            <ProfileSummary
                profile={activeProfile}
                isAuthenticated={Boolean(user)}
                isLoading={isLoading}
                onEdit={() => (user ? onNavigate('profile') : onSignIn())}
            />

            {isLoading ? (
                <LoadingCard label="Loading your orientation progress..." />
            ) : (
                <div className="dashboard-grid">
                    <section className="panel">
                        <div className="panel-heading">
                            <div>
                                <h3>Questionnaire Progress</h3>
                                <p>Adaptive orientation sessions</p>
                            </div>
                            <button
                                type="button"
                                className="btn-secondary btn-sm"
                                onClick={() =>
                                    user ? onNavigate('questionnaire') : onSignIn()
                                }
                            >
                                {user ? 'Open questionnaire' : 'Sign in'}
                            </button>
                        </div>

                        {!user ? (
                            <EmptyCard
                                title="Sign in required"
                                description="Questionnaire sessions are saved privately under your student account."
                            />
                        ) : !latestSession ? (
                            <EmptyCard
                                title="No session started yet"
                                description="Start your first orientation session to answer guided questions and generate recommendations."
                                action={
                                    <button
                                        type="button"
                                        className="btn-primary"
                                        onClick={() => onNavigate('questionnaire')}
                                    >
                                        Start questionnaire
                                    </button>
                                }
                            />
                        ) : (
                            <div className="progress-summary">
                                <div className="progress-row">
                                    <span>Latest session</span>
                                    <strong>Session #{latestSession.id}</strong>
                                </div>
                                <div className="progress-row">
                                    <span>Status</span>
                                    <strong>
                                        {latestSession.profile_confirmed
                                            ? 'Confirmed'
                                            : latestSession.expected_question_code === null
                                                ? 'Ready to confirm'
                                                : `In progress (${latestSession.expected_question_code})`}
                                    </strong>
                                </div>
                                <div className="progress-row">
                                    <span>Total sessions</span>
                                    <strong>{activeSessions.length}</strong>
                                </div>
                                <div className="progress-row">
                                    <span>Started</span>
                                    <strong>{formatDateTime(latestSession.created_at)}</strong>
                                </div>
                            </div>
                        )}
                    </section>

                    <section className="panel">
                        <div className="panel-heading">
                            <div>
                                <h3>Recommendation Overview</h3>
                                <p>Top exploration matches from your confirmed session</p>
                            </div>
                            <button
                                type="button"
                                className="btn-secondary btn-sm"
                                onClick={() =>
                                    user ? onNavigate('recommendations') : onSignIn()
                                }
                            >
                                {user ? 'View all' : 'Sign in'}
                            </button>
                        </div>

                        {!user ? (
                            <EmptyCard
                                title="Personalized matches await"
                                description="Sign in and confirm an orientation questionnaire to view compatible programs."
                            />
                        ) : !activeRecPreview ? (
                            <EmptyCard
                                title="No confirmed recommendations yet"
                                description="Complete and confirm an orientation questionnaire session to unlock your exploration matches."
                                action={
                                    <button
                                        type="button"
                                        className="btn-primary"
                                        onClick={() => onNavigate('questionnaire')}
                                    >
                                        Go to questionnaire
                                    </button>
                                }
                            />
                        ) : activeRecPreview.recommendations.length === 0 ? (
                            <EmptyCard
                                title="0 direct city matches"
                                description={`Location-to-verify candidates: ${activeRecPreview.location_to_verify_total}. Open Recommendations to inspect all details.`}
                            />
                        ) : (
                            <div className="mini-rec-list">
                                {activeRecPreview.recommendations.map((rec) => (
                                    <article key={rec.program_id} className="mini-rec-card">
                                        <div className="mini-rec-top">
                                            <div>
                                                <h4>{rec.program}</h4>
                                                <p className="muted-text">
                                                    {rec.institution_name ?? rec.institution_id}
                                                    {rec.city ? ` · ${rec.city}` : ''}
                                                </p>
                                            </div>
                                            <span className="score-pill">
                                                {rec.score !== null
                                                    ? `${Math.round(rec.score * 100) / 100}`
                                                    : 'Score N/A'}
                                            </span>
                                        </div>
                                        <div className="mini-rec-bottom">
                                            <VerificationBadge
                                                verified={rec.admissions_current_verified}
                                                label={
                                                    rec.admissions_current_verified
                                                        ? 'Verified'
                                                        : 'Verify source'
                                                }
                                            />
                                            <span className="muted-text">
                                                {formatMad(rec.annual_cost)}
                                            </span>
                                            <button
                                                type="button"
                                                className="btn-link"
                                                onClick={() => onOpenProgram(rec.program_id)}
                                            >
                                                Details
                                            </button>
                                        </div>
                                    </article>
                                ))}
                            </div>
                        )}
                    </section>
                </div>
            )}

            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <h3>Quick Access</h3>
                        <p>Explore every PathFinder AI workspace</p>
                    </div>
                </div>
                <div className="quick-access-grid">
                    <button
                        type="button"
                        className="quick-card"
                        onClick={() => onNavigate('compare')}
                    >
                        <strong>Compare Programs</strong>
                        <span>Side-by-side cost, duration, sector, and official sources.</span>
                    </button>
                    <button
                        type="button"
                        className="quick-card"
                        onClick={() => onNavigate('pathways')}
                    >
                        <strong>Academic &amp; Career Pathways</strong>
                        <span>Browse Moroccan post-Bac routes, careers, and institutions.</span>
                    </button>
                    <button
                        type="button"
                        className="quick-card"
                        onClick={() => (user ? onNavigate('assistant') : onSignIn())}
                    >
                        <strong>Evidence Search</strong>
                        <span>Query indexed official documentary passages with source links.</span>
                    </button>
                    {isAdmin && (
                        <button
                            type="button"
                            className="quick-card"
                            onClick={() => onNavigate('admin')}
                        >
                            <strong>Admin Overview</strong>
                            <span>Inspect catalogue status and backend admin capabilities.</span>
                        </button>
                    )}
                </div>
            </section>
        </div>
    )
}

export default Dashboard
