
type StatCardProps = {
    label: string
    value: string
    icon: string
}

function StatCard({ label, value, icon }: StatCardProps) {
    return (
        <div className="stat-card">
            <div className="stat-icon">{icon}</div>
            <div>
                <p className="stat-label">{label}</p>
                <strong>{value}</strong>
            </div>
        </div>
    )
}

function ProfileSummary() {
    return (
        <section className="profile-section">
            <div className="profile-heading">
                <div>
                    <h2>Your student profile</h2>
                    <p>
                        Complete your profile to get personalized recommendations.
                    </p>
                </div>
                <button className="edit-button">Edit profile</button>
            </div>

            <div className="stats-grid">
                <StatCard label="Bac series" value="Not set" icon="🎓" />
                <StatCard label="Average" value="—" icon="📊" />
                <StatCard label="Profile completion" value="0%" icon="✓" />
                <StatCard label="Official sources" value="Verified data" icon="◎" />
            </div>
        </section>
    )
}

export default ProfileSummary
