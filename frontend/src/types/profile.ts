export type PreferredType = 'public' | 'private' | 'other'

export type StudentProfileRead = {
    user_id: number
    bac_type: string | null
    interests: string[] | null
    skills: string[] | null
    grades: Record<string, number> | null
    career_goal: string | null
    preferred_type: PreferredType | null
    preferred_city: string | null
    can_relocate: boolean | null
    max_annual_budget: string | null
}

export type StudentProfileUpdate = {
    bac_type?: string | null
    interests?: string[] | null
    skills?: string[] | null
    grades?: Record<string, number> | null
    career_goal?: string | null
    preferred_type?: PreferredType | null
    preferred_city?: string | null
    can_relocate?: boolean | null
    max_annual_budget?: number | string | null
}
