
import { useState } from 'react'

type DashboardTab = 'recommendations' | 'compare' | 'roadmap'

const tabs: { id: DashboardTab; label: string }[] = [
    { id: 'recommendations', label: 'Recommendations' },
    { id: 'compare', label: 'Compare' },
    { id: 'roadmap', label: 'Roadmap' },
]

function Dashboard() {
    const [activeTab, setActiveTab] =
        useState<DashboardTab>('recommendations')

    return (
        <section className="panel dashboard-panel">
            <div className="panel-heading">
                <div>
                    <h2>Your orientation dashboard</h2>
                    <p>Explore your academic opportunities.</p>
                </div>
            </div>

            <nav className="dashboard-tabs" aria-label="Dashboard sections">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        type="button"
                        className={activeTab === tab.id ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab(tab.id)}
                        aria-pressed={activeTab === tab.id}
                    >
                        {tab.label}
                    </button>
                ))}
            </nav>

            <div className="dashboard-content">
                {activeTab === 'recommendations' && (
                    <EmptyState
                        icon="🎯"
                        title="Your recommendations will appear here"
                        description="Complete your student profile to discover educational pathways suited to your interests and goals."
                    />
                )}

                {activeTab === 'compare' && (
                    <EmptyState
                        icon="⚖️"
                        title="Compare academic pathways"
                        description="Choose educational programs to compare their requirements, duration, location and opportunities."
                    />
                )}

                {activeTab === 'roadmap' && (
                    <EmptyState
                        icon="🗺️"
                        title="Your personalized roadmap"
                        description="Your roadmap will guide you through the steps toward your academic goals."
                    />
                )}
            </div>
        </section>
    )
}

type EmptyStateProps = {
    icon: string
    title: string
    description: string
}

function EmptyState({ icon, title, description }: EmptyStateProps) {
    return (
        <div className="empty-state">
            <div className="empty-state-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    )
}

export default Dashboard
