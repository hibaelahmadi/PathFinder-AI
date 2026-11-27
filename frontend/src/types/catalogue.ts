export type P4Program = {
    program_id: string
    institution_id: string
    name: string
    description: string | null
    degree_type: string | null
    duration_months: number | null
    duration_scope: string | null
    entry_route: string | null
    direct_post_bac: boolean
    annual_cost: number | null
    annual_cost_currency: string | null
    accepted_bac_types: string[] | null
    required_subjects: string[] | null
    interests: string[]
    skills: string[]
    career_paths: string[]
    matching_status: string
    curriculum_summary: string | null
    options: string | null
    source_id: string
    source_locator: string | null
    academic_year: string | null
    checked_at: string | null
    status: string
    admissions_current_verified: boolean
    application_open: boolean | null
    accreditation_start: string | null
    accreditation_end: string | null
    accreditation_status: string | null
    notes: string | null
    field: string | null
    matching_basis: string | null
    career_paths_status: string | null
    exploration_visible: boolean
}

export type P4Institution = {
    institution_id: string
    name: string
    acronym: string | null
    city: string | null
    sector: string | null
    sector_detail: string | null
    entity_type: string | null
    parent_name: string | null
    address: string | null
    source_id: string | null
    source_locator: string | null
    source_year: string | null
    status: string | null
    city_status: string | null
    notes: string | null
}

export type P4Source = {
    source_id: string
    title: string
    url: string
    publisher: string | null
    academic_year: string | null
    published_at: string | null
    checked_at: string | null
    human_verified_at: string | null
    status: string | null
    scope: string | null
    notes: string | null
}

export type P4ProgramCard = P4Program & {
    institution: P4Institution
    sources: P4Source[]
    compatibility_score: number | null
    score_type: string
    eligibility: string
    cost_label: string
    warnings: string[]
}

export type P4Career = {
    career_id: string
    name: string
    description: string | null
    provenance: string | null
    employment_guaranteed: boolean
}

export type P4Pathway = {
    pathway_id: string
    title: string
    steps: string[]
    source_ids: string[]
    status: string
    notes: string | null
}

export type P4Vocabulary = {
    statut?: string
    catalogue?: string
    version_vocabulaires?: string
    categories: {
        required_subjects: string[]
        interests: string[]
        skills: string[]
        career_paths: string[]
        accepted_bac_types: string[]
    }
    annual_cost?: {
        unite?: string
        definition?: string
        exclus?: string[]
    }
}

export type CataloguePage<T> = {
    total: number
    items: T[]
}

export type EvidenceFilters = {
    institution_id?: string | string[]
    program_id?: string | string[]
    city?: string | string[]
    sector?: string | string[]
    field?: string | string[]
    academic_year?: string | string[]
    direct_post_bac?: boolean | boolean[]
    exploration_visible?: boolean | boolean[]
    source_id?: string | string[]
}

export type EvidenceSearchRequest = {
    query: string
    filters?: EvidenceFilters
    top_k?: number
}

export type EvidencePassage = {
    chunk_id: string
    text: string
    content_kind: string | null
    institution_id: string | null
    program_id: string | null
    source_id: string | null
    document_title: string | null
    publisher: string | null
    official_url: string | null
    page_or_section: string | null
    academic_year: string | null
    checked_at: string | null
    verification_date: string | null
    verification_status: string | null
    city: string | null
    sector: string | null
    field: string | null
    direct_post_bac: boolean | null
    exploration_visible: boolean | null
    retrieval_score: number
    retrieval_method: string
    admission_verified: false
}

export type EvidenceResponse = {
    status: 'ok' | 'no_evidence'
    evidence: EvidencePassage[]
    admission_verified: false
}
