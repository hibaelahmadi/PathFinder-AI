import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { getP4Vocabulary, searchEvidence } from '../../services/catalogueService'
import { ApiError } from '../../services/http'
import type {
    EvidenceFilters,
    EvidenceResponse,
    P4Vocabulary,
} from '../../types/catalogue'
import { formatCodeLabel } from '../../utils/formatters'
import {
    EmptyCard,
    LoadingCard,
    StatusBanner,
    VerificationBadge,
} from '../common/StateFeedback'

type ChatPanelProps = {
    onOpenProgram?: (programId: string) => void
}

function ChatPanel({ onOpenProgram }: ChatPanelProps) {
    const { token } = useAuth()

    const [query, setQuery] = useState('')
    const [cityFilter, setCityFilter] = useState('')
    const [sectorFilter, setSectorFilter] = useState('')
    const [fieldFilter, setFieldFilter] = useState('')
    const [directPostBac, setDirectPostBac] = useState<'any' | 'true' | 'false'>('any')
    const [explorationOnly, setExplorationOnly] = useState(true)
    const [topK, setTopK] = useState(5)

    const [vocabulary, setVocabulary] = useState<P4Vocabulary | null>(null)
    const [result, setResult] = useState<EvidenceResponse | null>(null)
    const [lastQuery, setLastQuery] = useState('')
    const [isSearching, setIsSearching] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const controller = new AbortController()
        getP4Vocabulary(controller.signal)
            .then((vocab) => {
                if (!controller.signal.aborted) {
                    setVocabulary(vocab)
                }
            })
            .catch(() => {
                // Optional filter dropdown enrichment
            })
        return () => controller.abort()
    }, [])

    async function handleSearch(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (!token) {
            return
        }

        const trimmed = query.trim()
        if (!trimmed) {
            setError('Enter a search query (1 to 2000 characters).')
            return
        }

        const filters: EvidenceFilters = {}
        if (cityFilter.trim()) {
            filters.city = cityFilter.trim()
        }
        if (sectorFilter) {
            filters.sector = sectorFilter
        }
        if (fieldFilter) {
            filters.field = fieldFilter
        }
        if (directPostBac !== 'any') {
            filters.direct_post_bac = directPostBac === 'true'
        }
        if (explorationOnly) {
            filters.exploration_visible = true
        }

        setIsSearching(true)
        setError(null)
        setLastQuery(trimmed)

        try {
            const response = await searchEvidence(
                {
                    query: trimmed,
                    filters,
                    top_k: topK,
                },
                token,
            )
            setResult(response)
        } catch (err) {
            setResult(null)
            if (err instanceof ApiError) {
                setError(err.message)
            } else {
                setError('Unable to retrieve official evidence.')
            }
        } finally {
            setIsSearching(false)
        }
    }

    return (
        <div className="workspace-stack">
            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <span className="eyebrow">POST /catalogue/evidence · TF-IDF + LSA Retrieval</span>
                        <h2>Official Evidence Assistant</h2>
                        <p>
                            Search indexed documentary passages from official Moroccan higher
                            education registries. Retrieval scores indicate text relevance only — never
                            compatibility or admission probability.
                        </p>
                    </div>
                </div>

                <StatusBanner
                    tone="warning"
                    message="Evidence results reflect archived/indexed documentary records (admission_verified: false). Always confirm current-year admission dates on the official source link."
                />

                <form className="evidence-form" onSubmit={handleSearch}>
                    <div className="evidence-search-row">
                        <input
                            type="text"
                            value={query}
                            onChange={(event) => setQuery(event.target.value)}
                            maxLength={2000}
                            placeholder="e.g., ENSA Marrakech cycle préparatoire, CPGE Rabat, médecine..."
                            aria-label="Evidence search query"
                            required
                        />
                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={isSearching}
                        >
                            {isSearching ? 'Searching...' : 'Search evidence'}
                        </button>
                    </div>

                    <div className="filters-bar">
                        <label>
                            <span>City (exact match)</span>
                            <input
                                type="text"
                                value={cityFilter}
                                onChange={(event) => setCityFilter(event.target.value)}
                                placeholder="e.g., Rabat"
                            />
                        </label>
                        <label>
                            <span>Sector</span>
                            <select
                                value={sectorFilter}
                                onChange={(event) => setSectorFilter(event.target.value)}
                            >
                                <option value="">Any sector</option>
                                <option value="public">Public</option>
                                <option value="private">Private</option>
                                <option value="partenariat_ou_autre">Partnership / Other</option>
                            </select>
                        </label>
                        <label>
                            <span>Field</span>
                            <select
                                value={fieldFilter}
                                onChange={(event) => setFieldFilter(event.target.value)}
                            >
                                <option value="">Any field</option>
                                {vocabulary?.categories.interests.map((item) => (
                                    <option key={item} value={item}>
                                        {formatCodeLabel(item)}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label>
                            <span>Direct post-Bac</span>
                            <select
                                value={directPostBac}
                                onChange={(event) =>
                                    setDirectPostBac(
                                        event.target.value as 'any' | 'true' | 'false',
                                    )
                                }
                            >
                                <option value="any">Any</option>
                                <option value="true">Yes</option>
                                <option value="false">No</option>
                            </select>
                        </label>
                        <label>
                            <span>Passages</span>
                            <select
                                value={topK}
                                onChange={(event) => setTopK(Number(event.target.value))}
                            >
                                {[3, 5, 10, 20].map((num) => (
                                    <option key={num} value={num}>
                                        Top {num}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label className="checkbox-inline">
                            <input
                                type="checkbox"
                                checked={explorationOnly}
                                onChange={(event) =>
                                    setExplorationOnly(event.target.checked)
                                }
                            />
                            <span>Exploration-visible only</span>
                        </label>
                    </div>
                </form>

                {error && <StatusBanner tone="error" message={error} />}

                {isSearching ? (
                    <LoadingCard label="Retrieving indexed documentary evidence..." />
                ) : !result ? (
                    <EmptyCard
                        title="Ask a factual question or enter keywords"
                        description="Try searching an institution acronym (ENSA, ENCG, CPGE), city, or field to retrieve exact documentary excerpts and official URLs."
                    />
                ) : result.status === 'no_evidence' || result.evidence.length === 0 ? (
                    <EmptyCard
                        title="No supporting evidence found"
                        description={`No indexed passage matched "${lastQuery}" with your active filters. Try broader terms or relax city/exploration filters.`}
                    />
                ) : (
                    <div className="workspace-stack">
                        <p className="muted-text">
                            Retrieved <strong>{result.evidence.length}</strong> documentary passage(s)
                            for &ldquo;{lastQuery}&rdquo;.
                        </p>
                        <div className="evidence-list">
                            {result.evidence.map((passage) => (
                                <article key={passage.chunk_id} className="evidence-card">
                                    <div className="evidence-card-header">
                                        <div>
                                            <span className="eyebrow">
                                                {passage.source_id ?? 'Official source'} ·{' '}
                                                {passage.publisher ?? 'Publisher unspecified'}
                                            </span>
                                            <h3>
                                                {passage.document_title ?? 'Official document'}
                                            </h3>
                                        </div>
                                        <span className="score-pill">
                                            Relevance: {passage.retrieval_score.toFixed(3)}
                                        </span>
                                    </div>

                                    <div className="badge-row">
                                        <VerificationBadge verified={passage.admission_verified} />
                                        {passage.academic_year && (
                                            <span className="badge badge-neutral">
                                                Year: {passage.academic_year}
                                            </span>
                                        )}
                                        {passage.checked_at && (
                                            <span className="badge badge-neutral">
                                                Checked: {passage.checked_at}
                                            </span>
                                        )}
                                        {passage.verification_status && (
                                            <span className="badge badge-neutral">
                                                {formatCodeLabel(passage.verification_status)}
                                            </span>
                                        )}
                                        {passage.city && (
                                            <span className="badge badge-neutral">
                                                {passage.city}
                                            </span>
                                        )}
                                    </div>

                                    <p className="evidence-text">{passage.text}</p>

                                    <div className="evidence-footer">
                                        <span className="muted-text">
                                            {passage.page_or_section ?? 'Section unspecified'}
                                            {passage.verification_date
                                                ? ` · Verified ${passage.verification_date}`
                                                : ''}
                                        </span>
                                        <div className="rec-actions">
                                            {passage.program_id && onOpenProgram && (
                                                <button
                                                    type="button"
                                                    className="btn-secondary btn-sm"
                                                    onClick={() =>
                                                        onOpenProgram(passage.program_id!)
                                                    }
                                                >
                                                    Program card ({passage.program_id})
                                                </button>
                                            )}
                                            {passage.official_url && (
                                                <a
                                                    href={passage.official_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="btn-primary btn-sm"
                                                >
                                                    Open official URL
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                </article>
                            ))}
                        </div>
                    </div>
                )}
            </section>
        </div>
    )
}

export default ChatPanel
