import { useAuth } from '../../contexts/AuthContext'
import type { AppPage } from '../../types/navigation'

type NavItem = {
    id: AppPage
    label: string
    requiresAuth?: boolean
    adminOnly?: boolean
}

const NAV_ITEMS: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'questionnaire', label: 'Questionnaire', requiresAuth: true },
    { id: 'profile', label: 'Profile', requiresAuth: true },
    { id: 'recommendations', label: 'Recommendations', requiresAuth: true },
    { id: 'compare', label: 'Compare' },
    { id: 'pathways', label: 'Pathways' },
    { id: 'assistant', label: 'Evidence Search', requiresAuth: true },
    { id: 'admin', label: 'Admin', requiresAuth: true, adminOnly: true },
]

type HeaderProps = {
    currentPage: AppPage
    onNavigate: (page: AppPage) => void
    onSignIn: () => void
    comparisonCount: number
}

function Header({
    currentPage,
    onNavigate,
    onSignIn,
    comparisonCount,
}: HeaderProps) {
    const { user, isAdmin, logout } = useAuth()

    const visibleItems = NAV_ITEMS.filter((item) => {
        if (item.adminOnly && !isAdmin) {
            return false
        }
        return true
    })

    return (
        <header className="app-header">
            <div className="header-top">
                <button
                    type="button"
                    className="brand brand-button"
                    onClick={() => onNavigate('dashboard')}
                >
                    <div className="brand-icon" aria-hidden="true">PF</div>
                    <div>
                        <h1>PathFinder AI</h1>
                        <p>Moroccan post-Bac academic orientation</p>
                    </div>
                </button>

                <div className="header-actions">
                    {!user ? (
                        <>
                            <span className="guest-badge">Guest mode</span>
                            <button
                                type="button"
                                className="btn-primary"
                                onClick={onSignIn}
                            >
                                Sign in
                            </button>
                        </>
                    ) : (
                        <>
                            <span className="role-pill" title={`Role: ${user.role}`}>
                                {user.role === 'admin' ? 'Admin' : 'Student'}
                            </span>
                            <span className="guest-badge">{user.email}</span>
                            <button
                                type="button"
                                className="btn-secondary"
                                onClick={logout}
                            >
                                Sign out
                            </button>
                        </>
                    )}
                </div>
            </div>

            <nav className="main-nav" aria-label="Primary navigation">
                {visibleItems.map((item) => {
                    const isActive = currentPage === item.id
                    return (
                        <button
                            key={item.id}
                            type="button"
                            className={isActive ? 'nav-link active' : 'nav-link'}
                            aria-current={isActive ? 'page' : undefined}
                            onClick={() => onNavigate(item.id)}
                        >
                            <span>{item.label}</span>
                            {item.id === 'compare' && comparisonCount > 0 && (
                                <span className="nav-count">{comparisonCount}</span>
                            )}
                            {item.requiresAuth && !user && (
                                <span className="nav-lock" aria-label="Requires sign in">
                                    •
                                </span>
                            )}
                        </button>
                    )
                })}
            </nav>
        </header>
    )
}

export default Header
