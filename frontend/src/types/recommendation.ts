export type RecommendationConstraints = {
    eligibility: 'eligible' | 'ineligible' | 'unknown'
    feasibility: 'feasible' | 'not_feasible' | 'unknown'
    reasons: string[]
}

export type RecommendationRead = {
    program_id: string
    program_code: string
    program: string
    score: number | null
    explanations: string[]
    constraints: RecommendationConstraints
    institution_id: string
    institution_name: string | null
    city: string | null
    annual_cost: number | null
    source_id: string
    source_locator: string
    academic_year: string | null
    status: string
    matching_status: string
    admissions_current_verified: boolean
    notes: string
}

export type SessionRecommendations = {
    session_id: number
    catalogue_kind: 'exploration'
    recommendations: RecommendationRead[]
    recommendations_total: number
    location_to_verify: RecommendationRead[]
    location_to_verify_total: number
}
