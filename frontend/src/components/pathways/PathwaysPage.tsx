import { useEffect, useMemo, useState } from 'react'
import {
    getP4Vocabulary,
    listP4Careers,
    listP4Institutions,
    listP4Pathways,
    listP4Programs,
    listP4Sources,
} from '../../services/catalogueService'
import { ApiError } from '../../services/http'
import type {
    P4Career,
    P4Institution,
    P4Pathway,
    P4Program,
    P4Source,
    P4Vocabulary,
} from '../../types/catalogue'
import {
    formatCodeLabel,
    formatDuration,
    formatMad,
} from '../../utils/formatters'
import {
    EmptyCard,
    LoadingCard,
    StatusBanner,
    VerificationBadge,
} from '../common/StateFeedback'

type PathwaysTab = 'pathways' | 'programs' | 'careers'

type PathwaysPageProps = {
    onOpenProgram: (programId: string) => void
    onAddToCompare: (programId: string) => void
    selectedCompareIds: string[]
}

export function PathwaysPage({
    onOpenProgram,
    onAddToCompare,
    selectedCompareIds,
}: PathwaysPageProps) {
    const [activeTab, setActiveTab] = useState<PathwaysTab>('pathways')
    const [pathways, setPathways] = useState<P4Pathway[]>([])
    const [careers, setCareers] = useState<P4Career[]>([])
    const [institutions, setInstitutions] = useState<P4Institution[]>([])
    const [sources, setSources] = useState<P4Source[]>([])
    const [vocabulary, setVocabulary] = useState<P4Vocabulary | null>(null)
    const [programs, setPrograms] = useState<P4Program[]>([])
    const [programsTotal, setProgramsTotal] = useState(0)

    const [cityFilter, setCityFilter] = useState('')
    const [sectorFilter, setSectorFilter] = useState('')
    const [fieldFilter, setFieldFilter] = useState('')
    const [directPostBacFilter, setDirectPostBacFilter] = useState<'all' | 'true' | 'false'>('all')
    const [includeArchive, setIncludeArchive] = useState(false)
    const [selectedCareerId, setSelectedCareerId] = useState<string | null>(null)

    const [isLoadingBase, setIsLoadingBase] = useState(true)
    const [isLoadingPrograms, setIsLoadingPrograms] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const controller = new AbortController()

        Promise.all([
            listP4Pathways(0, 100, controller.signal),
            listP4Careers(0, 100, controller.signal),
            listP4Institutions(0, 100, controller.signal),
            listP4Sources(0, 100, controller.signal),
            getP4Vocabulary(controller.signal),
        ])
            .then(([pathwaysRes, careersRes, instRes, sourcesRes, vocabRes]) => {
                if (controller.signal.aborted) {
                    return
                }
                setError(null)
                setPathways(pathwaysRes.items)
                setCareers(careersRes.items)
                setInstitutions(instRes.items)
                setSources(sourcesRes.items)
                setVocabulary(vocabRes)
            })
            .catch((err) => {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to load academic pathways catalogue.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoadingBase(false)
                }
            })

        return () => controller.abort()
    }, [])

    useEffect(() => {
        const controller = new AbortController()

        listP4Programs(
            {
                city: cityFilter || undefined,
                sector: sectorFilter || undefined,
                field: fieldFilter || undefined,
                direct_post_bac:
                    directPostBacFilter === 'all'
                        ? undefined
                        : directPostBacFilter === 'true',
                include_archive: includeArchive,
                offset: 0,
                limit: 100,
            },
            controller.signal,
        )
            .then((page) => {
                if (!controller.signal.aborted) {
                    setPrograms(page.items)
                    setProgramsTotal(page.total)
                }
            })
            .catch((err) => {
                if (err instanceof DOMException && err.name === 'AbortError') {
                    return
                }
                setError(
                    err instanceof ApiError
                        ? err.message
                        : 'Unable to filter programs.',
                )
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoadingPrograms(false)
                }
            })

        return () => controller.abort()
    }, [cityFilter, sectorFilter, fieldFilter, directPostBacFilter, includeArchive])

    const institutionsById = useMemo(() => {
        const map: Record<string, P4Institution> = {}
        for (const inst of institutions) {
            map[inst.institution_id] = inst
        }
        return map
    }, [institutions])

    const sourcesById = useMemo(() => {
        const map: Record<string, P4Source> = {}
        for (const src of sources) {
            map[src.source_id] = src
        }
        return map
    }, [sources])

    const cities = useMemo(
        () =>
            Array.from(
                new Set(institutions.map((item) => item.city).filter((c): c is string => Boolean(c))),
            ).sort(),
        [institutions],
    )

    const sectors = useMemo(
        () =>
            Array.from(
                new Set(
                    institutions
                        .map((item) => item.sector)
                        .filter((s): s is string => Boolean(s)),
                ),
            ).sort(),
        [institutions],
    )

    const careerFilteredPrograms = useMemo(() => {
        if (!selectedCareerId) {
            return programs
        }
        return programs.filter((program) =>
            program.career_paths.includes(selectedCareerId),
        )
    }, [programs, selectedCareerId])

    return (
        <div className="workspace-stack">
            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <span className="eyebrow">P4 Exploration Catalogue</span>
                        <h2>Academic &amp; Career Pathways</h2>
                        <p>
                            Explore Moroccan higher education pathways, programs, institutions,
                            and career directions sourced from official registries.
                        </p>
                    </div>
                </div>

                <div className="dashboard-tabs" role="tablist" aria-label="Pathways views">
                    <button
                        type="button"
                        role="tab"
                        aria-selected={activeTab === 'pathways'}
                        className={activeTab === 'pathways' ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab('pathways')}
                    >
                        General Pathways ({pathways.length})
                    </button>
                    <button
                        type="button"
                        role="tab"
                        aria-selected={activeTab === 'programs'}
                        className={activeTab === 'programs' ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab('programs')}
                    >
                        Programs &amp; Institutions ({programsTotal})
                    </button>
                    <button
                        type="button"
                        role="tab"
                        aria-selected={activeTab === 'careers'}
                        className={activeTab === 'careers' ? 'tab active' : 'tab'}
                        onClick={() => setActiveTab('careers')}
                    >
                        Career Leads ({careers.length})
                    </button>
                </div>

                {error && <StatusBanner tone="error" message={error} />}

                {isLoadingBase ? (
                    <LoadingCard label="Loading academic pathways catalogue..." />
                ) : (
                    <>
                        {activeTab === 'pathways' && (
                            <div className="cards-grid tab-panel-space">
                                {pathways.length === 0 ? (
                                    <EmptyCard
                                        title="No general pathways available"
                                        description="The catalogue returned no pathway records."
                                    />
                                ) : (
                                    pathways.map((pathway) => (
                                        <article key={pathway.pathway_id} className="pathway-card">
                                            <div className="pathway-header">
                                                <span className="badge badge-neutral">
                                                    {formatCodeLabel(pathway.status)}
                                                </span>
                                                <h3>{pathway.title}</h3>
                                            </div>
                                            <ol className="pathway-steps">
                                                {pathway.steps.map((step, idx) => (
                                                    <li key={`${pathway.pathway_id}-step-${idx}`}>
                                                        {step}
                                                    </li>
                                                ))}
                                            </ol>
                                            {pathway.notes && (
                                                <p className="muted-text">{pathway.notes}</p>
                                            )}
                                            <div className="pathway-sources">
                                                {pathway.source_ids.map((srcId) => {
                                                    const src = sourcesById[srcId]
                                                    return src ? (
                                                        <a
                                                            key={srcId}
                                                            href={src.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="chip"
                                                        >
                                                            {src.title}
                                                        </a>
                                                    ) : (
                                                        <span key={srcId} className="chip">
                                                            Source: {srcId}
                                                        </span>
                                                    )
                                                })}
                                            </div>
                                        </article>
                                    ))
                                )}
                            </div>
                        )}

                        {activeTab === 'programs' && (
                            <div className="workspace-stack tab-panel-space">
                                <div className="filters-bar">
                                    <label>
                                        <span>City</span>
                                        <select
                                            value={cityFilter}
                                            onChange={(event) => setCityFilter(event.target.value)}
                                        >
                                            <option value="">All cities</option>
                                            {cities.map((city) => (
                                                <option key={city} value={city}>
                                                    {city}
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                    <label>
                                        <span>Sector</span>
                                        <select
                                            value={sectorFilter}
                                            onChange={(event) => setSectorFilter(event.target.value)}
                                        >
                                            <option value="">All sectors</option>
                                            {sectors.map((sector) => (
                                                <option key={sector} value={sector}>
                                                    {formatCodeLabel(sector)}
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                    <label>
                                        <span>Field / Interest</span>
                                        <select
                                            value={fieldFilter}
                                            onChange={(event) => setFieldFilter(event.target.value)}
                                        >
                                            <option value="">All fields</option>
                                            {vocabulary?.categories.interests.map((field) => (
                                                <option key={field} value={field}>
                                                    {formatCodeLabel(field)}
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                    <label>
                                        <span>Direct post-Bac</span>
                                        <select
                                            value={directPostBacFilter}
                                            onChange={(event) =>
                                                setDirectPostBacFilter(
                                                    event.target.value as 'all' | 'true' | 'false',
                                                )
                                            }
                                        >
                                            <option value="all">Any entry route</option>
                                            <option value="true">Direct post-Bac only</option>
                                            <option value="false">Non-direct / later entry</option>
                                        </select>
                                    </label>
                                    <label className="checkbox-inline">
                                        <input
                                            type="checkbox"
                                            checked={includeArchive}
                                            onChange={(event) =>
                                                setIncludeArchive(event.target.checked)
                                            }
                                        />
                                        <span>Include archive</span>
                                    </label>
                                </div>

                                {selectedCareerId && (
                                    <StatusBanner
                                        tone="info"
                                        message={`Showing programs linked to career lead: ${formatCodeLabel(selectedCareerId)}`}
                                        action={
                                            <button
                                                type="button"
                                                className="btn-secondary btn-sm"
                                                onClick={() => setSelectedCareerId(null)}
                                            >
                                                Clear career filter
                                            </button>
                                        }
                                    />
                                )}

                                {isLoadingPrograms ? (
                                    <LoadingCard label="Filtering programs..." />
                                ) : careerFilteredPrograms.length === 0 ? (
                                    <EmptyCard
                                        title="No matching programs"
                                        description="Try clearing one of the filters or enabling archived programs."
                                    />
                                ) : (
                                    <div className="cards-grid">
                                        {careerFilteredPrograms.map((program) => {
                                            const inst = institutionsById[program.institution_id]
                                            const isInCompare = selectedCompareIds.includes(
                                                program.program_id,
                                            )
                                            return (
                                                <article
                                                    key={program.program_id}
                                                    className="rec-card"
                                                >
                                                    <div className="rec-card-header">
                                                        <div>
                                                            <span className="eyebrow">
                                                                {program.program_id}
                                                            </span>
                                                            <h4>{program.name}</h4>
                                                            <p className="muted-text">
                                                                {inst?.name ?? program.institution_id}
                                                                {inst?.city ? ` · ${inst.city}` : ''}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="badge-row">
                                                        <VerificationBadge
                                                            verified={
                                                                program.admissions_current_verified
                                                            }
                                                        />
                                                        <span className="badge badge-neutral">
                                                            {formatCodeLabel(program.field)}
                                                        </span>
                                                        <span className="badge badge-neutral">
                                                            {formatDuration(program.duration_months)}
                                                        </span>
                                                        <span className="badge badge-neutral">
                                                            {formatMad(program.annual_cost)}
                                                        </span>
                                                    </div>
                                                    {program.career_paths.length > 0 && (
                                                        <div className="chip-list">
                                                            {program.career_paths.map((career) => (
                                                                <span key={career} className="chip">
                                                                    {formatCodeLabel(career)}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}
                                                    <div className="rec-actions">
                                                        <button
                                                            type="button"
                                                            className="btn-primary btn-sm"
                                                            onClick={() =>
                                                                onOpenProgram(program.program_id)
                                                            }
                                                        >
                                                            Inspect card
                                                        </button>
                                                        <button
                                                            type="button"
                                                            className="btn-secondary btn-sm"
                                                            onClick={() =>
                                                                onAddToCompare(program.program_id)
                                                            }
                                                        >
                                                            {isInCompare
                                                                ? 'In comparison'
                                                                : 'Compare'}
                                                        </button>
                                                    </div>
                                                </article>
                                            )
                                        })}
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'careers' && (
                            <div className="cards-grid tab-panel-space">
                                {careers.map((career) => (
                                    <article key={career.career_id} className="pathway-card">
                                        <span className="badge badge-neutral">
                                            {formatCodeLabel(career.provenance)} · Employment not guaranteed
                                        </span>
                                        <h3>{formatCodeLabel(career.career_id)}</h3>
                                        <p>{career.description ?? 'No description available.'}</p>
                                        <button
                                            type="button"
                                            className="btn-secondary btn-sm"
                                            onClick={() => {
                                                setSelectedCareerId(career.career_id)
                                                setActiveTab('programs')
                                            }}
                                        >
                                            Explore related programs
                                        </button>
                                    </article>
                                ))}
                            </div>
                        )}
                    </>
                )}
            </section>
        </div>
    )
}

export default PathwaysPage
