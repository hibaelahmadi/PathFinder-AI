import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { ApiError } from '../services/http'
import {
    createSession,
    getSessions,
    getSessionState,
    sendSessionAction,
} from '../services/sessionService'
import type {
    JsonValue,
    QuestionnaireQuestion,
    QuestionnaireState,
    Session,
} from '../types/questionnaire'

export function useQuestionnaire() {
    const { token } = useAuth()

    const [sessions, setSessions] = useState<Session[]>([])
    const [activeSessionId, setActiveSessionId] = useState<number | null>(null)
    const [state, setState] = useState<QuestionnaireState | null>(null)
    const [currentQuestion, setCurrentQuestion] =
        useState<QuestionnaireQuestion | null>(null)
    const [profile, setProfile] = useState<Record<string, JsonValue> | null>(null)
    const [profileConfirmed, setProfileConfirmed] = useState(false)
    const [answer, setAnswer] = useState('')
    const [notice, setNotice] = useState<string | null>(null)
    const [isLoadingSessions, setIsLoadingSessions] = useState(false)
    const [isLoadingState, setIsLoadingState] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [errorDetails, setErrorDetails] = useState<string[]>([])

    const applyActionResponse = useCallback(
        (result: Awaited<ReturnType<typeof getSessionState>>, sessionId: number) => {
            setState(result.etat)
            setCurrentQuestion(result.next_question)
            setProfile(result.profile)
            setProfileConfirmed(result.profile_confirmed)

            setSessions((prev) =>
                prev.map((item) =>
                    item.id === sessionId
                        ? {
                              ...item,
                              status: result.etat.status,
                              expected_question_code: result.etat.expected_question_code,
                              profile: result.profile,
                              profile_confirmed: result.profile_confirmed,
                          }
                        : item,
                ),
            )

            if (result.answer_codes_to_delete.length > 0) {
                setNotice(
                    `Updated answer cleared dependent question(s): ${result.answer_codes_to_delete.join(', ')}.`,
                )
            }
        },
        [],
    )

    const selectSession = useCallback(
        async (sessionId: number, signal?: AbortSignal) => {
            if (!token) {
                return
            }
            setActiveSessionId(sessionId)
            setIsLoadingState(true)
            setError(null)
            setErrorDetails([])
            setNotice(null)

            try {
                const result = await getSessionState(sessionId, token, signal)
                if (signal?.aborted) {
                    return
                }
                applyActionResponse(result, sessionId)
                setAnswer('')
            } catch (err) {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                if (err instanceof ApiError) {
                    setError(err.message)
                    setErrorDetails(err.details)
                } else {
                    setError('Unable to load questionnaire session state.')
                }
            } finally {
                if (!signal?.aborted) {
                    setIsLoadingState(false)
                }
            }
        },
        [token, applyActionResponse],
    )

    const loadSessions = useCallback(
        async (signal?: AbortSignal) => {
            if (!token) {
                setSessions([])
                setActiveSessionId(null)
                setState(null)
                setCurrentQuestion(null)
                setProfile(null)
                setProfileConfirmed(false)
                return
            }

            setIsLoadingSessions(true)
            setError(null)
            setErrorDetails([])

            try {
                const list = await getSessions(token, 0, 50, signal)
                if (signal?.aborted) {
                    return
                }
                setSessions(list)

                if (list.length > 0) {
                    const latest = list[list.length - 1]
                    await selectSession(latest.id, signal)
                } else {
                    setActiveSessionId(null)
                    setState(null)
                    setCurrentQuestion(null)
                    setProfile(null)
                    setProfileConfirmed(false)
                }
            } catch (err) {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                if (err instanceof ApiError) {
                    setError(err.message)
                    setErrorDetails(err.details)
                } else {
                    setError('Unable to load your questionnaire sessions.')
                }
            } finally {
                if (!signal?.aborted) {
                    setIsLoadingSessions(false)
                }
            }
        },
        [token, selectSession],
    )

    useEffect(() => {
        const controller = new AbortController()
        void Promise.resolve().then(() => loadSessions(controller.signal))
        return () => controller.abort()
    }, [loadSessions])

    const startNewSession = useCallback(async () => {
        if (!token) {
            setError('Please sign in to start an orientation questionnaire.')
            return
        }

        setIsSubmitting(true)
        setError(null)
        setErrorDetails([])
        setNotice(null)

        try {
            const created = await createSession(token)
            setSessions((prev) => [...prev, created])
            await selectSession(created.id)
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message)
                setErrorDetails(err.details)
            } else {
                setError('Unable to create a new questionnaire session.')
            }
        } finally {
            setIsSubmitting(false)
        }
    }, [token, selectSession])

    const submitAnswer = useCallback(
        async (overrideAnswerText?: string) => {
            if (!token || activeSessionId === null || !currentQuestion) {
                return
            }

            const answerText = overrideAnswerText ?? answer
            setIsSubmitting(true)
            setError(null)
            setErrorDetails([])
            setNotice(null)

            try {
                const result = await sendSessionAction(
                    activeSessionId,
                    {
                        action: 'answer',
                        reponse: {
                            question_code: currentQuestion.question_code,
                            question_text: currentQuestion.question_text,
                            answer_text: answerText,
                        },
                    },
                    token,
                )
                applyActionResponse(result, activeSessionId)
                setAnswer('')
            } catch (err) {
                if (err instanceof ApiError) {
                    setError(err.message)
                    setErrorDetails(err.details)
                } else {
                    setError('Unable to submit your answer.')
                }
            } finally {
                setIsSubmitting(false)
            }
        },
        [token, activeSessionId, currentQuestion, answer, applyActionResponse],
    )

    const correctAnswer = useCallback(
        async (questionCode: string, newAnswerText: string): Promise<boolean> => {
            if (!token || activeSessionId === null) {
                return false
            }

            setIsSubmitting(true)
            setError(null)
            setErrorDetails([])
            setNotice(null)

            try {
                const result = await sendSessionAction(
                    activeSessionId,
                    {
                        action: 'correct',
                        reponse: {
                            question_code: questionCode,
                            answer_text: newAnswerText,
                        },
                    },
                    token,
                )
                applyActionResponse(result, activeSessionId)
                return true
            } catch (err) {
                if (err instanceof ApiError) {
                    setError(err.message)
                    setErrorDetails(err.details)
                } else {
                    setError('Unable to save correction.')
                }
                return false
            } finally {
                setIsSubmitting(false)
            }
        },
        [token, activeSessionId, applyActionResponse],
    )

    const confirmSession = useCallback(async () => {
        if (!token || activeSessionId === null) {
            return
        }

        setIsSubmitting(true)
        setError(null)
        setErrorDetails([])
        setNotice(null)

        try {
            const result = await sendSessionAction(
                activeSessionId,
                { action: 'confirm' },
                token,
            )
            applyActionResponse(result, activeSessionId)
            setNotice('Profile confirmed. Recommendations are now unlocked for this session.')
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message)
                setErrorDetails(err.details)
            } else {
                setError('Unable to confirm questionnaire session.')
            }
        } finally {
            setIsSubmitting(false)
        }
    }, [token, activeSessionId, applyActionResponse])

    const reopenSession = useCallback(async () => {
        if (!token || activeSessionId === null) {
            return
        }

        setIsSubmitting(true)
        setError(null)
        setErrorDetails([])
        setNotice(null)

        try {
            const result = await sendSessionAction(
                activeSessionId,
                { action: 'reopen' },
                token,
            )
            applyActionResponse(result, activeSessionId)
            setNotice(
                'Session reopened for edits. Remember to confirm again before viewing recommendations.',
            )
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message)
                setErrorDetails(err.details)
            } else {
                setError('Unable to reopen questionnaire session.')
            }
        } finally {
            setIsSubmitting(false)
        }
    }, [token, activeSessionId, applyActionResponse])

    const isLoading = isLoadingSessions || isLoadingState || isSubmitting

    return {
        sessions,
        activeSessionId,
        state,
        currentQuestion,
        profile,
        profileConfirmed,
        answer,
        notice,
        isLoading,
        isLoadingSessions,
        isLoadingState,
        isSubmitting,
        error,
        errorDetails,
        setAnswer,
        setError,
        clearNotice: () => setNotice(null),
        reloadSessions: () => loadSessions(),
        selectSession,
        startNewSession,
        submitAnswer,
        correctAnswer,
        confirmSession,
        reopenSession,
    }
}
