import type { StudentProfileRead } from '../types/profile'

const SPECIAL_LABELS: Record<string, string> = {
    data_ia: 'Data & AI',
    sciences_vie_terre: 'Sciences de la Vie et de la Terre',
    sciences_mathematiques_a: 'Sciences Mathématiques A',
    sciences_mathematiques_b: 'Sciences Mathématiques B',
    public: 'Public',
    private: 'Private',
    prive: 'Private',
    other: 'Other',
    eligible: 'Eligible',
    ineligible: 'Ineligible',
    feasible: 'Feasible',
    not_feasible: 'Not feasible',
    unknown: 'To verify',
    verified: 'Verified',
    unverified: 'Unverified',
    source_officielle_consultee: 'Official source consulted',
    registre_accreditation_a_actualiser: 'Registry — needs update',
    annuaire_a_actualiser: 'Directory — needs update',
    editorial_provisoire: 'Provisional editorial tag',
    structure_generale: 'General pathway structure',
    possibilite_generale: 'General possibility',
    illustratif: 'Illustrative pathway',
}

export function formatCodeLabel(value: string | null | undefined): string {
    if (!value) {
        return 'Not specified'
    }
    if (SPECIAL_LABELS[value]) {
        return SPECIAL_LABELS[value]
    }
    return value
        .replace(/[_-]+/g, ' ')
        .replace(/\b\w/g, (char) => char.toUpperCase())
}

export function formatMad(amount: number | string | null | undefined): string {
    if (amount === null || amount === undefined || amount === '') {
        return 'Tuition not specified'
    }
    const num = typeof amount === 'number' ? amount : Number(amount)
    if (!Number.isFinite(num)) {
        return 'Tuition not specified'
    }
    if (num === 0) {
        return '0 MAD / year (tuition)'
    }
    return `${num.toLocaleString('en-US', { maximumFractionDigits: 2 })} MAD / year`
}

export function formatDuration(months: number | null | undefined): string {
    if (!months || months <= 0) {
        return 'Duration not specified'
    }
    if (months % 12 === 0) {
        const years = months / 12
        return `${years} ${years === 1 ? 'year' : 'years'} (${months} months)`
    }
    return `${months} months`
}

export function computeAverageGrade(
    grades: Record<string, number> | null | undefined,
): number | null {
    if (!grades) {
        return null
    }
    const values = Object.values(grades).filter(
        (value) => typeof value === 'number' && Number.isFinite(value),
    )
    if (values.length === 0) {
        return null
    }
    const sum = values.reduce((acc, current) => acc + current, 0)
    return Math.round((sum / values.length) * 100) / 100
}

export function computeProfileCompletion(
    profile: StudentProfileRead | null,
): number {
    if (!profile) {
        return 0
    }
    const checks = [
        Boolean(profile.bac_type),
        Boolean(profile.interests && profile.interests.length > 0),
        Boolean(profile.skills && profile.skills.length > 0),
        Boolean(profile.grades && Object.keys(profile.grades).length > 0),
        Boolean(profile.career_goal),
        Boolean(profile.preferred_type),
        Boolean(profile.preferred_city),
        profile.can_relocate !== null && profile.can_relocate !== undefined,
        profile.max_annual_budget !== null && profile.max_annual_budget !== undefined,
    ]
    const filled = checks.filter(Boolean).length
    return Math.round((filled / checks.length) * 100)
}

export function formatDateTime(iso: string | null | undefined): string {
    if (!iso) {
        return '—'
    }
    const parsed = new Date(iso)
    if (Number.isNaN(parsed.getTime())) {
        return iso
    }
    return parsed.toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
    })
}
