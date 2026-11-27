import { useCallback, useEffect, useState } from 'react'
import './App.css'

import { useAuth } from './contexts/AuthContext'
import { useQuestionnaire } from './hooks/useQuestionnaire'
import type { AppPage } from './types/navigation'

import AdminPage from './components/admin/AdminPage'
import AuthForm from './components/auth/AuthForm'
import ChatPanel from './components/chat/ChatPanel'
import { ProgramCardModal } from './components/common/ProgramCardModal'
import {
    LoadingCard,
    ProtectedGate,
    StatusBanner,
} from './components/common/StateFeedback'
import ComparePage from './components/compare/ComparePage'
import Dashboard from './components/dashboard/Dashboard'
import Header from './components/layout/Header'
import PathwaysPage from './components/pathways/PathwaysPage'
import ProfilePage from './components/profile/ProfilePage'
import QuestionnairePanel from './components/questionnaire/QuestionnairePanel'
import RecommendationsPage from './components/recommendations/RecommendationsPage'

const VALID_PAGES: AppPage[] = [
    'dashboard',
    'questionnaire',
    'profile',
    'recommendations',
    'compare',
    'pathways',
    'assistant',
    'admin',
]

function parsePageFromHash(): AppPage {
    const raw = window.location.hash.replace(/^#\/?/, '').trim() as AppPage
    return VALID_PAGES.includes(raw) ? raw : 'dashboard'
}

function App() {
    const {
        user,
        isLoading: isAuthLoading,
        sessionExpiredMessage,
        clearSessionExpiredMessage,
    } = useAuth()
    const questionnaire = useQuestionnaire()

    const [currentPage, setCurrentPage] = useState<AppPage>(parsePageFromHash)
    const [isAuthOpen, setIsAuthOpen] = useState(false)
    const [selectedCompareIds, setSelectedCompareIds] = useState<string[]>([])
    const [inspectedProgramId, setInspectedProgramId] = useState<string | null>(null)
    const [preferredSessionId, setPreferredSessionId] = useState<number | null>(null)
    const [profileRefreshKey, setProfileRefreshKey] = useState(0)

    const navigate = useCallback((page: AppPage) => {
        setCurrentPage(page)
        const targetHash = `#/${page}`
        if (window.location.hash !== targetHash) {
            window.location.hash = targetHash
        }
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }, [])

    useEffect(() => {
        function handleHashChange() {
            setCurrentPage(parsePageFromHash())
        }
        window.addEventListener('hashchange', handleHashChange)
        return () => window.removeEventListener('hashchange', handleHashChange)
    }, [])

    useEffect(() => {
        if (!isAuthOpen) {
            return
        }
        function handleKey(event: KeyboardEvent) {
            if (event.key === 'Escape') {
                setIsAuthOpen(false)
            }
        }
        window.addEventListener('keydown', handleKey)
        return () => window.removeEventListener('keydown', handleKey)
    }, [isAuthOpen])

    function toggleCompareProgram(programId: string) {
        setSelectedCompareIds((prev) => {
            if (prev.includes(programId)) {
                return prev.filter((id) => id !== programId)
            }
            if (prev.length >= 4) {
                return prev
            }
            return [...prev, programId]
        })
    }

    function addToCompareAndOpen(programId: string) {
        setSelectedCompareIds((prev) => {
            if (prev.includes(programId) || prev.length >= 4) {
                return prev
            }
            return [...prev, programId]
        })
        navigate('compare')
    }

    function renderMainContent() {
        if (isAuthLoading) {
            return (
                <section className="panel">
                    <LoadingCard label="Restoring session..." />
                </section>
            )
        }

        switch (currentPage) {
            case 'dashboard':
                return (
                    <Dashboard
                        onNavigate={navigate}
                        onSignIn={() => setIsAuthOpen(true)}
                        onOpenProgram={setInspectedProgramId}
                        profileRefreshKey={profileRefreshKey}
                    />
                )

            case 'questionnaire':
                if (!user) {
                    return (
                        <ProtectedGate
                            title="Sign in to access the orientation questionnaire"
                            description="Your questionnaire sessions, answers, and profile snapshot are stored privately under your account."
                            onSignIn={() => setIsAuthOpen(true)}
                        />
                    )
                }
                return (
                    <QuestionnairePanel
                        sessions={questionnaire.sessions}
                        activeSessionId={questionnaire.activeSessionId}
                        state={questionnaire.state}
                        question={questionnaire.currentQuestion}
                        profile={questionnaire.profile}
                        profileConfirmed={questionnaire.profileConfirmed}
                        answer={questionnaire.answer}
                        notice={questionnaire.notice}
                        isLoadingSessions={questionnaire.isLoadingSessions}
                        isLoadingState={questionnaire.isLoadingState}
                        isSubmitting={questionnaire.isSubmitting}
                        error={questionnaire.error}
                        errorDetails={questionnaire.errorDetails}
                        onAnswerChange={questionnaire.setAnswer}
                        onSelectSession={(id) => questionnaire.selectSession(id)}
                        onStartNew={questionnaire.startNewSession}
                        onSubmit={questionnaire.submitAnswer}
                        onCorrect={questionnaire.correctAnswer}
                        onConfirm={questionnaire.confirmSession}
                        onReopen={questionnaire.reopenSession}
                        onDismissNotice={questionnaire.clearNotice}
                        onViewRecommendations={(sessionId) => {
                            setPreferredSessionId(sessionId)
                            navigate('recommendations')
                        }}
                    />
                )

            case 'profile':
                if (!user) {
                    return (
                        <ProtectedGate
                            title="Sign in to view and edit your student profile"
                            description="Store your Bac stream, subject grades, interests, skills, city, and budget."
                            onSignIn={() => setIsAuthOpen(true)}
                        />
                    )
                }
                return (
                    <ProfilePage
                        onProfileSaved={() => setProfileRefreshKey((count) => count + 1)}
                    />
                )

            case 'recommendations':
                if (!user) {
                    return (
                        <ProtectedGate
                            title="Sign in to view personalized recommendations"
                            description="Recommendations are computed from your confirmed orientation questionnaire session."
                            onSignIn={() => setIsAuthOpen(true)}
                        />
                    )
                }
                return (
                    <RecommendationsPage
                        preferredSessionId={
                            preferredSessionId ?? questionnaire.activeSessionId
                        }
                        onOpenProgram={setInspectedProgramId}
                        onAddToCompare={addToCompareAndOpen}
                        onGoToQuestionnaire={() => navigate('questionnaire')}
                    />
                )

            case 'compare':
                return (
                    <ComparePage
                        selectedIds={selectedCompareIds}
                        onToggleProgram={toggleCompareProgram}
                        onClearSelection={() => setSelectedCompareIds([])}
                        onOpenProgram={setInspectedProgramId}
                    />
                )

            case 'pathways':
                return (
                    <PathwaysPage
                        onOpenProgram={setInspectedProgramId}
                        onAddToCompare={addToCompareAndOpen}
                        selectedCompareIds={selectedCompareIds}
                    />
                )

            case 'assistant':
                if (!user) {
                    return (
                        <ProtectedGate
                            title="Sign in to search official documentary evidence"
                            description="Evidence search queries the backend retrieval index and requires an authenticated student or admin account."
                            onSignIn={() => setIsAuthOpen(true)}
                        />
                    )
                }
                return <ChatPanel onOpenProgram={setInspectedProgramId} />

            case 'admin':
                if (!user) {
                    return (
                        <ProtectedGate
                            title="Sign in with an admin account"
                            description="Administrative diagnostics require an authenticated administrator account."
                            onSignIn={() => setIsAuthOpen(true)}
                        />
                    )
                }
                return <AdminPage />
        }
    }

    return (
        <div className="app-container">
            <Header
                currentPage={currentPage}
                onNavigate={navigate}
                onSignIn={() => setIsAuthOpen(true)}
                comparisonCount={selectedCompareIds.length}
            />

            {sessionExpiredMessage && (
                <div className="top-banner-wrap">
                    <StatusBanner
                        tone="warning"
                        message={sessionExpiredMessage}
                        action={
                            <button
                                type="button"
                                className="btn-primary btn-sm"
                                onClick={() => setIsAuthOpen(true)}
                            >
                                Sign in
                            </button>
                        }
                        onDismiss={clearSessionExpiredMessage}
                    />
                </div>
            )}

            <main className="page-main">{renderMainContent()}</main>

            <footer className="app-footer">
                <p>
                    PathFinder AI · Moroccan post-Bac orientation platform · Compatibility scores
                    are not admission probabilities. Verify requirements via official sources.
                </p>
            </footer>

            {isAuthOpen && (
                <div
                    className="auth-modal-backdrop"
                    role="presentation"
                    onClick={(event) => {
                        if (event.target === event.currentTarget) {
                            setIsAuthOpen(false)
                        }
                    }}
                >
                    <div
                        className="auth-modal"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="auth-title"
                    >
                        <AuthForm onClose={() => setIsAuthOpen(false)} />
                    </div>
                </div>
            )}

            {inspectedProgramId && (
                <ProgramCardModal
                    programId={inspectedProgramId}
                    onClose={() => setInspectedProgramId(null)}
                    onCompare={addToCompareAndOpen}
                />
            )}
        </div>
    )
}

export default App
