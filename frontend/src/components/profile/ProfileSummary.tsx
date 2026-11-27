import type { StudentProfileRead } from '../../types/profile'
import {
    computeAverageGrade,
    computeProfileCompletion,
    formatCodeLabel,
    formatMad,
} from '../../utils/formatters'

type StatCardProps = {
    label: string
    value: string
    icon: string
}

function StatCard({ label, value, icon }: StatCardProps) {
    return (
        <div className="stat-card">
            <div className="stat-icon" aria-hidden="true">{icon}</div>
            <div>
                <p className="stat-label">{label}</p>
                <strong>{value}</strong>
            </div>
        </div>
    )
}

type ProfileSummaryProps = {
    profile: StudentProfileRead | null
    isAuthenticated: boolean
    isLoading?: boolean
    onEdit: () => void
}

function ProfileSummary({
    profile,
    isAuthenticated,
    isLoading = false,
    onEdit,
}: ProfileSummaryProps) {
    const average = computeAverageGrade(profile?.grades)
    const completion = computeProfileCompletion(profile)

    return (
        <section className="profile-section">
            <div className="profile-heading">
                <div>
                    <h2>Your student profile</h2>
                    <p>
                        {isAuthenticated
                            ? 'Keep your academic profile, preferences, and budget up to date.'
                            : 'Sign in to save your Bac series, grades, and orientation preferences.'}
                    </p>
                </div>
                <button type="button" className="edit-button" onClick={onEdit}>
                    {isAuthenticated ? 'Edit profile' : 'Sign in to edit'}
                </button>
            </div>

            <div className="stats-grid">
                <StatCard
                    label="Bac series"
                    value={
                        isLoading
                            ? 'Loading...'
                            : profile?.bac_type
                                ? formatCodeLabel(profile.bac_type)
                                : 'Not set'
                    }
                    icon="🎓"
                />
                <StatCard
                    label="Recorded average"
                    value={
                        isLoading
                            ? 'Loading...'
                            : average !== null
                                ? `${average} / 20`
                                : '—'
                    }
                    icon="📊"
                />
                <StatCard
                    label="Profile completion"
                    value={isLoading ? '...' : `${completion}%`}
                    icon="✓"
                />
                <StatCard
                    label="Preferred city & budget"
                    value={
                        isLoading
                            ? 'Loading...'
                            : profile?.preferred_city
                                ? `${profile.preferred_city}${profile.max_annual_budget ? ` · ${formatMad(profile.max_annual_budget)}` : ''}`
                                : profile?.max_annual_budget
                                    ? formatMad(profile.max_annual_budget)
                                    : 'Not set'
                    }
                    icon="📍"
                />
            </div>
        </section>
    )
}

export default ProfileSummary
