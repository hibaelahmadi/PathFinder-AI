import { useState, type FormEvent } from 'react'
import type {
    JsonValue,
    QuestionnaireAnswerData,
    QuestionnaireQuestion,
    QuestionnaireState,
    Session,
} from '../../types/questionnaire'
import { formatCodeLabel, formatDateTime } from '../../utils/formatters'
import { EmptyCard, LoadingCard, StatusBanner } from '../common/StateFeedback'

type QuestionnairePanelProps = {
    sessions: Session[]
    activeSessionId: number | null
    state: QuestionnaireState | null
    question: QuestionnaireQuestion | null
    profile: Record<string, JsonValue> | null
    profileConfirmed: boolean
    answer: string
    notice: string | null
    isLoadingSessions: boolean
    isLoadingState: boolean
    isSubmitting: boolean
    error: string | null
    errorDetails: string[]
    onAnswerChange: (value: string) => void
    onSelectSession: (sessionId: number) => void
    onStartNew: () => void
    onSubmit: (overrideAnswer?: string) => void
    onCorrect: (questionCode: string, newAnswerText: string) => Promise<boolean>
    onConfirm: () => void
    onReopen: () => void
    onDismissNotice: () => void
    onViewRecommendations: (sessionId: number) => void
}

function getQuickChoices(questionCode: string): string[] {
    if (questionCode === 'mobilite') {
        return ['oui', 'non', 'je ne sais pas']
    }
    if (questionCode === 'precision_bac') {
        return ['A', 'B', 'je ne sais pas']
    }
    if (questionCode === 'type_etablissement') {
        return ['public', 'privé', 'sans préférence']
    }
    return []
}

function formatProfileValue(value: JsonValue): string {
    if (value === null || value === undefined || value === '') {
        return 'Not specified'
    }
    if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No'
    }
    if (Array.isArray(value)) {
        return value.length > 0 ? value.map(String).join(', ') : 'None'
    }
    if (typeof value === 'object') {
        const entries = Object.entries(value)
        if (entries.length === 0) {
            return 'None'
        }
        return entries.map(([k, v]) => `${formatCodeLabel(k)}: ${v}`).join(' · ')
    }
    return String(value)
}

function QuestionnairePanel({
    sessions,
    activeSessionId,
    state,
    question,
    profile,
    profileConfirmed,
    answer,
    notice,
    isLoadingSessions,
    isLoadingState,
    isSubmitting,
    error,
    errorDetails,
    onAnswerChange,
    onSelectSession,
    onStartNew,
    onSubmit,
    onCorrect,
    onConfirm,
    onReopen,
    onDismissNotice,
    onViewRecommendations,
}: QuestionnairePanelProps) {
    const [editingCode, setEditingCode] = useState<string | null>(null)
    const [editText, setEditText] = useState('')

    const savedAnswers: QuestionnaireAnswerData[] = state
        ? Object.values(state.answers)
        : []
    const isCompleted = state?.status === 'completed'
    const isReadyToConfirm =
        state?.status === 'in_progress' && question === null && activeSessionId !== null

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        onSubmit()
    }

    async function handleSaveCorrection(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (!editingCode) {
            return
        }
        const ok = await onCorrect(editingCode, editText)
        if (ok) {
            setEditingCode(null)
            setEditText('')
        }
    }

    const quickChoices = question ? getQuickChoices(question.question_code) : []

    return (
        <div className="workspace-stack">
            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <span className="eyebrow">Adaptive orientation engine</span>
                        <h2>Orientation Questionnaire</h2>
                        <p>
                            The backend engine selects each question based on your previous responses.
                            You can resume a session, correct earlier answers, and confirm when ready.
                        </p>
                    </div>
                    <button
                        type="button"
                        className="btn-primary"
                        onClick={onStartNew}
                        disabled={isSubmitting || isLoadingSessions}
                    >
                        {isSubmitting && !activeSessionId ? 'Creating...' : 'New session'}
                    </button>
                </div>

                {sessions.length > 0 && (
                    <div className="session-bar" aria-label="Saved questionnaire sessions">
                        <span className="session-bar-label">Your sessions:</span>
                        <div className="session-pills">
                            {sessions.map((session) => {
                                const isActive = session.id === activeSessionId
                                return (
                                    <button
                                        key={session.id}
                                        type="button"
                                        className={
                                            isActive ? 'session-pill active' : 'session-pill'
                                        }
                                        onClick={() => onSelectSession(session.id)}
                                        disabled={isLoadingState || isSubmitting}
                                    >
                                        <span>Session #{session.id}</span>
                                        <span
                                            className={
                                                session.profile_confirmed
                                                    ? 'pill-dot confirmed'
                                                    : 'pill-dot'
                                            }
                                            title={
                                                session.profile_confirmed
                                                    ? 'Confirmed'
                                                    : 'In progress'
                                            }
                                        />
                                    </button>
                                )
                            })}
                        </div>
                    </div>
                )}

                {notice && (
                    <StatusBanner
                        tone="info"
                        message={notice}
                        onDismiss={onDismissNotice}
                    />
                )}

                {error && (
                    <StatusBanner
                        tone="error"
                        message={error}
                        details={errorDetails}
                    />
                )}

                {isLoadingSessions || isLoadingState ? (
                    <LoadingCard label="Loading questionnaire session..." />
                ) : activeSessionId === null ? (
                    <EmptyCard
                        title="No orientation session yet"
                        description="Start a new session to tell PathFinder AI about your Bac stream, preferred cities, interests, and budget."
                        action={
                            <button
                                type="button"
                                className="btn-primary"
                                onClick={onStartNew}
                                disabled={isSubmitting}
                            >
                                Start questionnaire
                            </button>
                        }
                    />
                ) : (
                    <div className="questionnaire-grid">
                        <div className="questionnaire-main">
                            <div className="session-meta-strip">
                                <span>
                                    <strong>Session #{activeSessionId}</strong>
                                </span>
                                <span>
                                    Status:{' '}
                                    <strong className={profileConfirmed ? 'text-verified' : ''}>
                                        {profileConfirmed
                                            ? 'Confirmed'
                                            : isReadyToConfirm
                                                ? 'Ready for confirmation'
                                                : 'In progress'}
                                    </strong>
                                </span>
                                <span>
                                    Answered: <strong>{savedAnswers.length}</strong>
                                </span>
                            </div>

                            {question && state?.status === 'in_progress' && (
                                <form className="question-card" onSubmit={handleSubmit}>
                                    <div className="question-code-badge">
                                        Question: <code>{question.question_code}</code>
                                    </div>
                                    <h3>{question.question_text}</h3>

                                    {quickChoices.length > 0 && (
                                        <div className="quick-choices" role="group" aria-label="Suggested options">
                                            {quickChoices.map((choice) => (
                                                <button
                                                    key={choice}
                                                    type="button"
                                                    className={
                                                        answer.trim().toLowerCase() === choice.toLowerCase()
                                                            ? 'chip chip-selected'
                                                            : 'chip'
                                                    }
                                                    onClick={() => onAnswerChange(choice)}
                                                >
                                                    {choice}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                    <label htmlFor="question-answer">Your answer</label>
                                    <input
                                        id="question-answer"
                                        type="text"
                                        value={answer}
                                        onChange={(event) => onAnswerChange(event.target.value)}
                                        placeholder="Type your response (or leave blank to skip if optional)"
                                        disabled={isSubmitting}
                                    />

                                    <div className="form-actions">
                                        <button
                                            type="submit"
                                            className="btn-primary"
                                            disabled={isSubmitting}
                                        >
                                            {isSubmitting ? 'Sending...' : 'Submit answer'}
                                        </button>
                                        <button
                                            type="button"
                                            className="btn-secondary"
                                            disabled={isSubmitting}
                                            onClick={() => onSubmit('')}
                                        >
                                            Skip / Send blank
                                        </button>
                                    </div>
                                </form>
                            )}

                            {isReadyToConfirm && (
                                <div className="question-card confirm-card">
                                    <h3>All applicable questions are answered</h3>
                                    <p>
                                        Review your extracted profile snapshot and saved answers.
                                        Confirming locks this snapshot so you can generate recommendations.
                                    </p>
                                    <div className="form-actions">
                                        <button
                                            type="button"
                                            className="btn-primary"
                                            onClick={onConfirm}
                                            disabled={isSubmitting}
                                        >
                                            {isSubmitting
                                                ? 'Confirming...'
                                                : 'Confirm profile & unlock recommendations'}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {isCompleted && profileConfirmed && (
                                <div className="question-card confirmed-card">
                                    <h3>Questionnaire confirmed</h3>
                                    <p>
                                        Your session is confirmed. You can view your personalized
                                        exploration recommendations or reopen the session to edit answers.
                                        Reopening temporarily disables recommendations until you confirm again.
                                    </p>
                                    <div className="form-actions">
                                        <button
                                            type="button"
                                            className="btn-primary"
                                            onClick={() => onViewRecommendations(activeSessionId)}
                                        >
                                            View recommendations
                                        </button>
                                        <button
                                            type="button"
                                            className="btn-secondary"
                                            onClick={onReopen}
                                            disabled={isSubmitting}
                                        >
                                            {isSubmitting ? 'Reopening...' : 'Reopen for corrections'}
                                        </button>
                                    </div>
                                </div>
                            )}

                            {profile && (
                                <div className="profile-snapshot-box">
                                    <h4>Session Profile Snapshot</h4>
                                    <dl className="snapshot-grid">
                                        {Object.entries(profile).map(([key, value]) => (
                                            <div key={key}>
                                                <dt>{formatCodeLabel(key)}</dt>
                                                <dd>{formatProfileValue(value)}</dd>
                                            </div>
                                        ))}
                                    </dl>
                                </div>
                            )}
                        </div>

                        <aside className="questionnaire-sidebar">
                            <h4>Saved Answers ({savedAnswers.length})</h4>
                            {savedAnswers.length === 0 ? (
                                <p className="muted-text">
                                    Your submitted answers will appear here so you can review or correct them.
                                </p>
                            ) : (
                                <ul className="saved-answers-list">
                                    {savedAnswers.map((item) => {
                                        const isEditing = editingCode === item.question_code
                                        return (
                                            <li key={item.question_code} className="saved-answer-item">
                                                <div className="saved-answer-header">
                                                    <code>{item.question_code}</code>
                                                    {state?.status === 'in_progress' && !isEditing && (
                                                        <button
                                                            type="button"
                                                            className="btn-link"
                                                            onClick={() => {
                                                                setEditingCode(item.question_code)
                                                                setEditText(item.answer_text)
                                                            }}
                                                        >
                                                            Correct
                                                        </button>
                                                    )}
                                                </div>
                                                <p className="saved-question-text">{item.question_text}</p>
                                                {!isEditing ? (
                                                    <p className="saved-answer-value">
                                                        {item.answer_text.trim()
                                                            ? item.answer_text
                                                            : '(Skipped / blank)'}
                                                    </p>
                                                ) : (
                                                    <form
                                                        className="inline-edit-form"
                                                        onSubmit={handleSaveCorrection}
                                                    >
                                                        <input
                                                            type="text"
                                                            value={editText}
                                                            onChange={(event) =>
                                                                setEditText(event.target.value)
                                                            }
                                                            aria-label={`Correct answer for ${item.question_code}`}
                                                            disabled={isSubmitting}
                                                        />
                                                        <div className="inline-edit-actions">
                                                            <button
                                                                type="submit"
                                                                className="btn-primary btn-sm"
                                                                disabled={isSubmitting}
                                                            >
                                                                Save
                                                            </button>
                                                            <button
                                                                type="button"
                                                                className="btn-ghost btn-sm"
                                                                onClick={() => setEditingCode(null)}
                                                            >
                                                                Cancel
                                                            </button>
                                                        </div>
                                                    </form>
                                                )}
                                            </li>
                                        )
                                    })}
                                </ul>
                            )}
                            {sessions.find((s) => s.id === activeSessionId)?.created_at && (
                                <p className="muted-text sidebar-footnote">
                                    Started{' '}
                                    {formatDateTime(
                                        sessions.find((s) => s.id === activeSessionId)?.created_at,
                                    )}
                                </p>
                            )}
                        </aside>
                    </div>
                )}
            </section>
        </div>
    )
}

export default QuestionnairePanel
