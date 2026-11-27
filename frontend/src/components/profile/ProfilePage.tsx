import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { getP4Vocabulary } from '../../services/catalogueService'
import { ApiError } from '../../services/http'
import { getMyProfile, updateMyProfile } from '../../services/profileService'
import type { P4Vocabulary } from '../../types/catalogue'
import type {
    PreferredType,
    StudentProfileRead,
    StudentProfileUpdate,
} from '../../types/profile'
import {
    computeAverageGrade,
    computeProfileCompletion,
    formatCodeLabel,
} from '../../utils/formatters'
import { LoadingCard, StatusBanner } from '../common/StateFeedback'

type GradeRow = {
    id: string
    subject: string
    score: string
}

type ProfilePageProps = {
    onProfileSaved?: (profile: StudentProfileRead) => void
}

function parseTagList(input: string): string[] {
    return Array.from(
        new Set(
            input
                .split(',')
                .map((item) => item.trim())
                .filter(Boolean),
        ),
    )
}

export function ProfilePage({ onProfileSaved }: ProfilePageProps) {
    const { token } = useAuth()

    const [vocabulary, setVocabulary] = useState<P4Vocabulary | null>(null)
    const [profileExists, setProfileExists] = useState(false)
    const [isLoading, setIsLoading] = useState(true)
    const [isSaving, setIsSaving] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [errorDetails, setErrorDetails] = useState<string[]>([])
    const [success, setSuccess] = useState<string | null>(null)

    const [bacType, setBacType] = useState('')
    const [careerGoal, setCareerGoal] = useState('')
    const [interestsText, setInterestsText] = useState('')
    const [skillsText, setSkillsText] = useState('')
    const [preferredType, setPreferredType] = useState<PreferredType | ''>('')
    const [preferredCity, setPreferredCity] = useState('')
    const [canRelocate, setCanRelocate] = useState<'unset' | 'yes' | 'no'>('unset')
    const [maxAnnualBudget, setMaxAnnualBudget] = useState('')
    const [gradeRows, setGradeRows] = useState<GradeRow[]>([])

    function applyProfileToForm(profile: StudentProfileRead) {
        setBacType(profile.bac_type ?? '')
        setCareerGoal(profile.career_goal ?? '')
        setInterestsText((profile.interests ?? []).join(', '))
        setSkillsText((profile.skills ?? []).join(', '))
        setPreferredType(profile.preferred_type ?? '')
        setPreferredCity(profile.preferred_city ?? '')
        setCanRelocate(
            profile.can_relocate === null || profile.can_relocate === undefined
                ? 'unset'
                : profile.can_relocate
                    ? 'yes'
                    : 'no',
        )
        setMaxAnnualBudget(profile.max_annual_budget ?? '')
        const entries = Object.entries(profile.grades ?? {})
        setGradeRows(
            entries.map(([subject, score], idx) => ({
                id: `${subject}-${idx}`,
                subject,
                score: String(score),
            })),
        )
    }

    useEffect(() => {
        if (!token) {
            return
        }
        const controller = new AbortController()

        Promise.allSettled([
            getMyProfile(token, controller.signal),
            getP4Vocabulary(controller.signal),
        ])
            .then(([profileRes, vocabRes]) => {
                if (controller.signal.aborted) {
                    return
                }
                if (vocabRes.status === 'fulfilled') {
                    setVocabulary(vocabRes.value)
                }
                if (profileRes.status === 'fulfilled') {
                    setProfileExists(true)
                    setError(null)
                    applyProfileToForm(profileRes.value)
                } else {
                    const reason = profileRes.reason
                    if (reason instanceof ApiError && reason.status === 404) {
                        setProfileExists(false)
                        setError(null)
                    } else if (reason instanceof ApiError) {
                        setError(reason.message)
                    } else {
                        setError('Unable to load your student profile.')
                    }
                }
            })
            .finally(() => {
                if (!controller.signal.aborted) {
                    setIsLoading(false)
                }
            })

        return () => controller.abort()
    }, [token])

    function toggleTag(currentText: string, tag: string, setter: (value: string) => void) {
        const list = parseTagList(currentText)
        const next = list.includes(tag)
            ? list.filter((item) => item !== tag)
            : [...list, tag]
        setter(next.join(', '))
    }

    function addGradeRow(subject = '') {
        setGradeRows((prev) => [
            ...prev,
            { id: `grade-${Date.now()}-${prev.length}`, subject, score: '' },
        ])
    }

    function updateGradeRow(id: string, field: 'subject' | 'score', value: string) {
        setGradeRows((prev) =>
            prev.map((row) => (row.id === id ? { ...row, [field]: value } : row)),
        )
    }

    function removeGradeRow(id: string) {
        setGradeRows((prev) => prev.filter((row) => row.id !== id))
    }

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (!token) {
            return
        }

        setError(null)
        setErrorDetails([])
        setSuccess(null)

        const gradesMap: Record<string, number> = {}
        for (const row of gradeRows) {
            const subject = row.subject.trim()
            const scoreStr = row.score.trim()
            if (!subject && !scoreStr) {
                continue
            }
            if (!subject) {
                setError('Please enter a subject name for every grade entry.')
                return
            }
            const parsed = Number(scoreStr)
            if (!scoreStr || !Number.isFinite(parsed) || parsed < 0 || parsed > 20) {
                setError(`Grade for "${subject}" must be a number between 0 and 20.`)
                return
            }
            gradesMap[subject] = parsed
        }

        let budgetValue: number | null = null
        if (maxAnnualBudget.trim() !== '') {
            const parsedBudget = Number(maxAnnualBudget.trim())
            if (!Number.isFinite(parsedBudget) || parsedBudget < 0) {
                setError('Annual tuition budget must be a nonnegative number.')
                return
            }
            budgetValue = parsedBudget
        }

        const interests = parseTagList(interestsText)
        const skills = parseTagList(skillsText)

        const payload: StudentProfileUpdate = {
            bac_type: bacType.trim() || null,
            career_goal: careerGoal.trim() || null,
            interests: interests.length > 0 ? interests : null,
            skills: skills.length > 0 ? skills : null,
            grades: Object.keys(gradesMap).length > 0 ? gradesMap : null,
            preferred_type: preferredType === '' ? null : preferredType,
            preferred_city: preferredCity.trim() || null,
            can_relocate:
                canRelocate === 'unset' ? null : canRelocate === 'yes',
            max_annual_budget: budgetValue,
        }

        setIsSaving(true)
        try {
            const saved = await updateMyProfile(payload, token)
            setProfileExists(true)
            applyProfileToForm(saved)
            setSuccess('Student profile saved.')
            onProfileSaved?.(saved)
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message)
                setErrorDetails(err.details)
            } else {
                setError('Unable to save your student profile.')
            }
        } finally {
            setIsSaving(false)
        }
    }

    const previewGrades: Record<string, number> = {}
    for (const row of gradeRows) {
        const num = Number(row.score)
        if (row.subject.trim() && row.score.trim() !== '' && Number.isFinite(num)) {
            previewGrades[row.subject.trim()] = num
        }
    }
    const previewAverage = computeAverageGrade(previewGrades)
    const currentCompletion = computeProfileCompletion({
        user_id: 0,
        bac_type: bacType.trim() || null,
        interests: parseTagList(interestsText),
        skills: parseTagList(skillsText),
        grades: Object.keys(previewGrades).length > 0 ? previewGrades : null,
        career_goal: careerGoal.trim() || null,
        preferred_type: preferredType === '' ? null : preferredType,
        preferred_city: preferredCity.trim() || null,
        can_relocate: canRelocate === 'unset' ? null : canRelocate === 'yes',
        max_annual_budget: maxAnnualBudget.trim() || null,
    })

    if (isLoading) {
        return (
            <section className="panel">
                <LoadingCard label="Loading student profile..." />
            </section>
        )
    }

    const selectedInterests = parseTagList(interestsText)
    const selectedSkills = parseTagList(skillsText)

    return (
        <div className="workspace-stack">
            <section className="panel">
                <div className="panel-heading">
                    <div>
                        <span className="eyebrow">GET / PATCH /profiles/me</span>
                        <h2>Student Profile</h2>
                        <p>
                            Store your Bac series, subject grades, interests, skills, city, mobility,
                            and tuition budget. Note: personalized recommendations use your confirmed
                            orientation questionnaire session snapshot.
                        </p>
                    </div>
                    <div className="completion-pill">
                        Completion: <strong>{currentCompletion}%</strong>
                        {previewAverage !== null && ` · Avg ${previewAverage}/20`}
                    </div>
                </div>

                {!profileExists && !error && (
                    <StatusBanner
                        tone="info"
                        message="No profile record has been saved yet. Fill in any fields below and save to create your profile."
                    />
                )}

                {error && (
                    <StatusBanner
                        tone="error"
                        message={error}
                        details={errorDetails}
                    />
                )}

                {success && (
                    <StatusBanner
                        tone="success"
                        message={success}
                        onDismiss={() => setSuccess(null)}
                    />
                )}

                <form className="profile-form" onSubmit={handleSubmit}>
                    <div className="form-grid-2">
                        <div className="form-field">
                            <label htmlFor="profile-bac">Baccalaureate series (`bac_type`)</label>
                            <input
                                id="profile-bac"
                                type="text"
                                list="bac-series-options"
                                maxLength={100}
                                value={bacType}
                                onChange={(event) => setBacType(event.target.value)}
                                placeholder="e.g., sciences_mathematiques_a"
                            />
                            {vocabulary && (
                                <datalist id="bac-series-options">
                                    {vocabulary.categories.accepted_bac_types.map((code) => (
                                        <option key={code} value={code}>
                                            {formatCodeLabel(code)}
                                        </option>
                                    ))}
                                </datalist>
                            )}
                        </div>

                        <div className="form-field">
                            <label htmlFor="profile-career-goal">Career goal (`career_goal`)</label>
                            <input
                                id="profile-career-goal"
                                type="text"
                                maxLength={255}
                                value={careerGoal}
                                onChange={(event) => setCareerGoal(event.target.value)}
                                placeholder="e.g., Software engineering or healthcare"
                            />
                        </div>

                        <div className="form-field">
                            <label htmlFor="profile-city">Preferred city (`preferred_city`)</label>
                            <input
                                id="profile-city"
                                type="text"
                                maxLength={100}
                                value={preferredCity}
                                onChange={(event) => setPreferredCity(event.target.value)}
                                placeholder="e.g., Rabat, Casablanca, Marrakech"
                            />
                        </div>

                        <div className="form-field">
                            <label htmlFor="profile-type">Preferred institution type (`preferred_type`)</label>
                            <select
                                id="profile-type"
                                value={preferredType}
                                onChange={(event) =>
                                    setPreferredType(event.target.value as PreferredType | '')
                                }
                            >
                                <option value="">No preference (cleared)</option>
                                <option value="public">Public</option>
                                <option value="private">Private</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div className="form-field">
                            <label htmlFor="profile-relocate">Willing to relocate (`can_relocate`)</label>
                            <select
                                id="profile-relocate"
                                value={canRelocate}
                                onChange={(event) =>
                                    setCanRelocate(event.target.value as 'unset' | 'yes' | 'no')
                                }
                            >
                                <option value="unset">Not specified</option>
                                <option value="yes">Yes — open to studying in another city</option>
                                <option value="no">No — prefer staying in preferred city</option>
                            </select>
                        </div>

                        <div className="form-field">
                            <label htmlFor="profile-budget">
                                Max annual tuition budget in MAD (`max_annual_budget`)
                            </label>
                            <input
                                id="profile-budget"
                                type="number"
                                min={0}
                                step="0.01"
                                value={maxAnnualBudget}
                                onChange={(event) => setMaxAnnualBudget(event.target.value)}
                                placeholder="Annual tuition only (0 for free/public)"
                            />
                        </div>
                    </div>

                    <div className="form-field">
                        <label htmlFor="profile-interests">
                            Interests (comma-separated, or toggle standard vocabulary tags below)
                        </label>
                        <input
                            id="profile-interests"
                            type="text"
                            value={interestsText}
                            onChange={(event) => setInterestsText(event.target.value)}
                            placeholder="e.g., informatique, data_ia, mathematiques"
                        />
                        {vocabulary && (
                            <div className="chip-list">
                                {vocabulary.categories.interests.map((tag) => (
                                    <button
                                        key={tag}
                                        type="button"
                                        className={
                                            selectedInterests.includes(tag)
                                                ? 'chip chip-selected'
                                                : 'chip'
                                        }
                                        onClick={() =>
                                            toggleTag(interestsText, tag, setInterestsText)
                                        }
                                    >
                                        {formatCodeLabel(tag)}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="form-field">
                        <label htmlFor="profile-skills">
                            Skills (comma-separated, or toggle standard vocabulary tags below)
                        </label>
                        <input
                            id="profile-skills"
                            type="text"
                            value={skillsText}
                            onChange={(event) => setSkillsText(event.target.value)}
                            placeholder="e.g., analyse, programmation, communication"
                        />
                        {vocabulary && (
                            <div className="chip-list">
                                {vocabulary.categories.skills.map((tag) => (
                                    <button
                                        key={tag}
                                        type="button"
                                        className={
                                            selectedSkills.includes(tag)
                                                ? 'chip chip-selected'
                                                : 'chip'
                                        }
                                        onClick={() =>
                                            toggleTag(skillsText, tag, setSkillsText)
                                        }
                                    >
                                        {formatCodeLabel(tag)}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="form-field">
                        <div className="grades-header">
                            <label>Subject Grades (0 to 20)</label>
                            <button
                                type="button"
                                className="btn-secondary btn-sm"
                                onClick={() => addGradeRow()}
                            >
                                Add subject grade
                            </button>
                        </div>

                        {gradeRows.length === 0 ? (
                            <p className="muted-text">No subject grades recorded yet.</p>
                        ) : (
                            <div className="grades-list">
                                {gradeRows.map((row) => (
                                    <div key={row.id} className="grade-row">
                                        <input
                                            type="text"
                                            list="subject-options"
                                            maxLength={100}
                                            value={row.subject}
                                            onChange={(event) =>
                                                updateGradeRow(row.id, 'subject', event.target.value)
                                            }
                                            placeholder="Subject code or name"
                                            aria-label="Subject name"
                                        />
                                        <input
                                            type="number"
                                            min={0}
                                            max={20}
                                            step="0.01"
                                            value={row.score}
                                            onChange={(event) =>
                                                updateGradeRow(row.id, 'score', event.target.value)
                                            }
                                            placeholder="0–20"
                                            aria-label="Grade out of 20"
                                        />
                                        <button
                                            type="button"
                                            className="btn-ghost btn-sm"
                                            onClick={() => removeGradeRow(row.id)}
                                        >
                                            Remove
                                        </button>
                                    </div>
                                ))}
                                {vocabulary && (
                                    <datalist id="subject-options">
                                        {vocabulary.categories.required_subjects.map((subject) => (
                                            <option key={subject} value={subject}>
                                                {formatCodeLabel(subject)}
                                            </option>
                                        ))}
                                    </datalist>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="form-actions">
                        <button type="submit" className="btn-primary" disabled={isSaving}>
                            {isSaving ? 'Saving profile...' : 'Save profile'}
                        </button>
                    </div>
                </form>
            </section>
        </div>
    )
}

export default ProfilePage
