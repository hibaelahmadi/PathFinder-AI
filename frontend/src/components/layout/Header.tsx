type HeaderProps = {
    isAuthenticated: boolean
}

function Header({ isAuthenticated }: HeaderProps) {
    return (
        <header className="app-header">
            <div className="brand">
                <div className="brand-icon">PF</div>
                <div>
                    <h1>PathFinder AI</h1>
                    <p>Your academic orientation assistant</p>
                </div>
            </div>

            <div className="header-actions">
                {!isAuthenticated && (
                    <span className="guest-badge">Guest mode</span>
                )}

                <button className="login-button">
                    {isAuthenticated ? 'My account' : 'Sign in'}
                </button>
            </div>
        </header>
    )
}

export default Header