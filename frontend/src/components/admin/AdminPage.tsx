import { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import {
    getHealthStatus,
    listP4Institutions,
    listP4Pathways,
    listP4Programs,
    listP4Sources,
} from '../../services/catalogueService'
import { ApiError } from '../../services/http'
import { formatDateTime } from '../../utils/formatters'
import { LoadingCard, StatusBanner } from '../common/StateFeedback'

type CatalogueStats = {
    apiHealthy: boolean
    programsTotal: number
    archivedTotal: number
    institutionsTotal: number
    sourcesTotal: number
    pathwaysTotal: number
}

export function AdminPage() {
    const { user, isAdmin } = useAuth()
    const [stats, setStats] = useState<CatalogueStats | null>(null)
    const [isLoading, setIsLoading] = useState(isAdmin)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!isAdmin) {
            return
        }
        const controller = new AbortController()

        Promise.all([
            getHealthStatus(controller.signal),
            listP4Programs({ include_archive: false, limit: 1 }, controller.signal),
            listP4Programs({ include_archive: true, limit: 1 }, controller.signal),
            listP4Institutions(0, 1, controller.signal),
            listP4Sources(0, 1, controller.signal),
            listP4Pathways(0, 1, controller.signal),
        ])
            .then(([health, visibleProgs, allProgs, insts, srcs, paths]) => {
                if (controller.signal.aborted) {
                    return
                }
                setError(null)
                setStats({
                    apiHealthy: health.status === 'ok',
                    programsTotal: visibleProgs.total,
                    archivedTotal: allProgs.total,
                    institutionsTotal: insts.total,
                    sourcesTotal: srcs.total,
                    pathwaysTotal: paths.total,
                })
            })
            .catch((err) => {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to load backend diagnostics.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoading(false)
                }
            })

        return () => controller.abort()
    }, [isAdmin])

    if (!user || !isAdmin) {
        return (
            <section className="panel gate-panel">
                <h2>Administrator access required</h2>
                <p>
                    This workspace is restricted to accounts with the <code>admin</code> role.
                    Student accounts have access to orientation questionnaires, profiles,
                    recommendations, comparison, pathways, and evidence search.
                </p>
            </section>
        )
    }

    return (
        <div className="workspace-stack">
            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <span className="eyebrow">Role: admin · Read-only diagnostics</span>
                        <h2>Administration Overview</h2>
                        <p>
                            Inspect authenticated admin account metadata and live P4 catalogue totals.
                        </p>
                    </div>
                </div>

                <StatusBanner
                    tone="info"
                    title="Backend admin capability notice"
                    message="The current FastAPI backend recognizes the 'admin' role on /auth/me, but does not yet expose dedicated admin management or verification mutation endpoints (see BACKEND_ISSUES.md ISSUE-002). Only verified read-only diagnostics are shown here."
                />

                {error && <StatusBanner tone="error" message={error} />}

                {isLoading ? (
                    <LoadingCard label="Loading live backend diagnostics..." />
                ) : (
                    <div className="workspace-stack">
                        <div className="profile-snapshot-box">
                            <h3>Authenticated Admin Account</h3>
                            <dl className="snapshot-grid">
                                <div>
                                    <dt>User ID</dt>
                                    <dd>{user.id}</dd>
                                </div>
                                <div>
                                    <dt>Email</dt>
                                    <dd>{user.email}</dd>
                                </div>
                                <div>
                                    <dt>Role</dt>
                                    <dd>{user.role}</dd>
                                </div>
                                <div>
                                    <dt>Status</dt>
                                    <dd>{user.is_active ? 'Active' : 'Disabled'}</dd>
                                </div>
                                <div>
                                    <dt>Created</dt>
                                    <dd>{formatDateTime(user.created_at)}</dd>
                                </div>
                            </dl>
                        </div>

                        {stats && (
                            <div className="stats-grid">
                                <div className="stat-card">
                                    <div className="stat-icon" aria-hidden="true">API</div>
                                    <div>
                                        <p className="stat-label">Backend /health</p>
                                        <strong>{stats.apiHealthy ? 'Healthy (ok)' : 'Unavailable'}</strong>
                                    </div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-icon" aria-hidden="true">PRG</div>
                                    <div>
                                        <p className="stat-label">Exploration / Total Programs</p>
                                        <strong>
                                            {stats.programsTotal} / {stats.archivedTotal}
                                        </strong>
                                    </div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-icon" aria-hidden="true">INS</div>
                                    <div>
                                        <p className="stat-label">P4 Institutions</p>
                                        <strong>{stats.institutionsTotal}</strong>
                                    </div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-icon" aria-hidden="true">SRC</div>
                                    <div>
                                        <p className="stat-label">Official Sources / Pathways</p>
                                        <strong>
                                            {stats.sourcesTotal} / {stats.pathwaysTotal}
                                        </strong>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </section>
        </div>
    )
}

export default AdminPage
