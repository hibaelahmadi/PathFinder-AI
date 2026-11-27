import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import {
    getP4ProgramCard,
    listP4Institutions,
    listP4Programs,
} from '../../services/catalogueService'
import { ApiError } from '../../services/http'
import { getSessionRecommendations } from '../../services/recommendationService'
import { getSessions } from '../../services/sessionService'
import type {
    P4Institution,
    P4Program,
    P4ProgramCard,
} from '../../types/catalogue'
import type { RecommendationRead } from '../../types/recommendation'
import { formatCodeLabel, formatDuration } from '../../utils/formatters'
import {
    EmptyCard,
    LoadingCard,
    StatusBanner,
    VerificationBadge,
} from '../common/StateFeedback'

type ComparePageProps = {
    selectedIds: string[]
    onToggleProgram: (programId: string) => void
    onClearSelection: () => void
    onOpenProgram: (programId: string) => void
}

export function ComparePage({
    selectedIds,
    onToggleProgram,
    onClearSelection,
    onOpenProgram,
}: ComparePageProps) {
    const { token } = useAuth()

    const [catalogPrograms, setCatalogPrograms] = useState<P4Program[]>([])
    const [institutionsMap, setInstitutionsMap] = useState<Record<string, P4Institution>>({})
    const [cards, setCards] = useState<P4ProgramCard[]>([])
    const [recByProgramId, setRecByProgramId] = useState<Record<string, RecommendationRead>>({})
    const [searchText, setSearchText] = useState('')
    const [isLoadingCatalog, setIsLoadingCatalog] = useState(true)
    const [isLoadingCards, setIsLoadingCards] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const controller = new AbortController()

        Promise.all([
            listP4Programs({ limit: 100, include_archive: false }, controller.signal),
            listP4Institutions(0, 100, controller.signal),
        ])
            .then(([programsRes, instRes]) => {
                if (controller.signal.aborted) {
                    return
                }
                setError(null)
                setCatalogPrograms(programsRes.items)
                const map: Record<string, P4Institution> = {}
                for (const inst of instRes.items) {
                    map[inst.institution_id] = inst
                }
                setInstitutionsMap(map)
            })
            .catch((err) => {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to load exploration catalogue for comparison.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoadingCatalog(false)
                }
            })

        return () => controller.abort()
    }, [])

    useEffect(() => {
        if (!token) {
            return
        }
        const controller = new AbortController()

        getSessions(token, 0, 50, controller.signal)
            .then(async (sessions) => {
                if (controller.signal.aborted) {
                    return
                }
                const confirmed = [...sessions]
                    .reverse()
                    .find((s) => s.status === 'completed' && s.profile_confirmed)
                if (!confirmed) {
                    setRecByProgramId({})
                    return
                }
                const recs = await getSessionRecommendations(
                    confirmed.id,
                    token,
                    100,
                    controller.signal,
                )
                if (controller.signal.aborted) {
                    return
                }
                const map: Record<string, RecommendationRead> = {}
                for (const item of [...recs.recommendations, ...recs.location_to_verify]) {
                    map[item.program_id] = item
                }
                setRecByProgramId(map)
            })
            .catch(() => {
                // Optional enrichment from confirmed session
            })

        return () => controller.abort()
    }, [token])

    useEffect(() => {
        if (selectedIds.length === 0) {
            return
        }

        const controller = new AbortController()

        Promise.all(
            selectedIds.map((id) => getP4ProgramCard(id, controller.signal)),
        )
            .then((loaded) => {
                if (!controller.signal.aborted) {
                    setError(null)
                    setCards(loaded)
                }
            })
            .catch((err) => {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to load selected program cards.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoadingCards(false)
                }
            })

        return () => controller.abort()
    }, [selectedIds])

    const activeCards = selectedIds.length === 0 ? [] : cards
    const activeRecByProgramId = token ? recByProgramId : {}

    const filteredPrograms = useMemo(() => {
        const query = searchText.trim().toLowerCase()
        if (!query) {
            return catalogPrograms.slice(0, 12)
        }
        return catalogPrograms
            .filter((program) => {
                const inst = institutionsMap[program.institution_id]
                return (
                    program.name.toLowerCase().includes(query) ||
                    (program.field ?? '').toLowerCase().includes(query) ||
                    (inst?.name ?? '').toLowerCase().includes(query) ||
                    (inst?.city ?? '').toLowerCase().includes(query)
                )
            })
            .slice(0, 12)
    }, [catalogPrograms, institutionsMap, searchText])

    return (
        <div className="workspace-stack">
            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <span className="eyebrow">GET /catalogue/programs &amp; /catalogue/programs/&#123;id&#125;</span>
                        <h2>Compare Academic Programs</h2>
                        <p>
                            Select 2 to 4 programs from the exploration catalogue to compare costs,
                            institutions, cities, duration, and official source verification side by side.
                        </p>
                    </div>
                    {selectedIds.length > 0 && (
                        <button
                            type="button"
                            className="btn-secondary btn-sm"
                            onClick={onClearSelection}
                        >
                            Clear selection ({selectedIds.length})
                        </button>
                    )}
                </div>

                {error && <StatusBanner tone="error" message={error} />}

                <div className="compare-picker">
                    <label htmlFor="compare-search">Find programs to add (up to 4)</label>
                    <input
                        id="compare-search"
                        type="search"
                        value={searchText}
                        onChange={(event) => setSearchText(event.target.value)}
                        placeholder="Search by program name, institution, city, or field..."
                    />

                    {isLoadingCatalog ? (
                        <LoadingCard label="Loading exploration catalogue..." />
                    ) : (
                        <div className="picker-grid">
                            {filteredPrograms.map((program) => {
                                const inst = institutionsMap[program.institution_id]
                                const isSelected = selectedIds.includes(program.program_id)
                                const isFull = !isSelected && selectedIds.length >= 4
                                return (
                                    <div
                                        key={program.program_id}
                                        className={
                                            isSelected ? 'picker-item selected' : 'picker-item'
                                        }
                                    >
                                        <div>
                                            <strong>{program.name}</strong>
                                            <p className="muted-text">
                                                {inst?.name ?? program.institution_id}
                                                {inst?.city ? ` · ${inst.city}` : ''}
                                            </p>
                                        </div>
                                        <button
                                            type="button"
                                            className={
                                                isSelected ? 'btn-secondary btn-sm' : 'btn-primary btn-sm'
                                            }
                                            disabled={isFull}
                                            onClick={() => onToggleProgram(program.program_id)}
                                        >
                                            {isSelected
                                                ? 'Remove'
                                                : isFull
                                                    ? 'Max 4'
                                                    : 'Add'}
                                        </button>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>
            </section>

            <section className="panel">
                <h3>Side-by-side comparison</h3>

                {isLoadingCards ? (
                    <LoadingCard label="Loading program comparison cards..." />
                ) : activeCards.length < 2 ? (
                    <EmptyCard
                        title={
                            activeCards.length === 0
                                ? 'No programs selected'
                                : 'Select at least one more program'
                        }
                        description="Choose at least 2 programs above (or click Compare from Recommendations or Pathways) to inspect differences side by side."
                    />
                ) : (
                    <div className="table-scroll">
                        <table className="compare-table">
                            <thead>
                                <tr>
                                    <th scope="col">Criterion</th>
                                    {activeCards.map((card) => (
                                        <th key={card.program_id} scope="col">
                                            <div className="compare-col-header">
                                                <span>{card.name}</span>
                                                <button
                                                    type="button"
                                                    className="btn-link"
                                                    onClick={() => onToggleProgram(card.program_id)}
                                                >
                                                    Remove
                                                </button>
                                            </div>
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <th scope="row">Institution</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>
                                            <strong>{card.institution.name}</strong>
                                            {card.institution.acronym
                                                ? ` (${card.institution.acronym})`
                                                : ''}
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <th scope="row">City &amp; Sector</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>
                                            {card.institution.city ?? 'City to verify'} ·{' '}
                                            {formatCodeLabel(card.institution.sector)}
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <th scope="row">Academic Field</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>
                                            {formatCodeLabel(card.field)}
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <th scope="row">Degree / Duration</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>
                                            {card.degree_type ?? '—'} ·{' '}
                                            {formatDuration(card.duration_months)}
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <th scope="row">Entry Route</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>
                                            {card.direct_post_bac
                                                ? 'Direct post-Bac'
                                                : formatCodeLabel(card.entry_route)}
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <th scope="row">Annual Cost</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>{card.cost_label}</td>
                                    ))}
                                </tr>
                                <tr>
                                    <th scope="row">Compatibility (not admission prob.)</th>
                                    {activeCards.map((card) => {
                                        const rec = activeRecByProgramId[card.program_id]
                                        return (
                                            <td key={card.program_id}>
                                                {rec ? (
                                                    <>
                                                        <strong>
                                                            {rec.score !== null
                                                                ? `${rec.score.toFixed(2)}`
                                                                : 'Score unavailable'}
                                                        </strong>
                                                        <div className="muted-text">
                                                            {formatCodeLabel(
                                                                rec.constraints.eligibility,
                                                            )}{' '}
                                                            ·{' '}
                                                            {formatCodeLabel(
                                                                rec.constraints.feasibility,
                                                            )}
                                                        </div>
                                                    </>
                                                ) : (
                                                    <span className="muted-text">
                                                        Not computed (confirm questionnaire session)
                                                    </span>
                                                )}
                                            </td>
                                        )
                                    })}
                                </tr>
                                <tr>
                                    <th scope="row">Admission Verification</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>
                                            <VerificationBadge
                                                verified={card.admissions_current_verified}
                                            />
                                            <div className="muted-text">
                                                {card.academic_year ?? 'Year unspecified'} ·{' '}
                                                {formatCodeLabel(card.eligibility)}
                                            </div>
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <th scope="row">Official Sources</th>
                                    {activeCards.map((card) => (
                                        <td key={card.program_id}>
                                            {card.sources.map((src) => (
                                                <div key={src.source_id} className="compare-source">
                                                    <a
                                                        href={src.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-link"
                                                    >
                                                        {src.title}
                                                    </a>
                                                </div>
                                            ))}
                                            <button
                                                type="button"
                                                className="btn-link"
                                                onClick={() => onOpenProgram(card.program_id)}
                                            >
                                                Full program card
                                            </button>
                                        </td>
                                    ))}
                                </tr>
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </div>
    )
}

export default ComparePage
