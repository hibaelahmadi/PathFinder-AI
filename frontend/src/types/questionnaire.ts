export type JsonValue =
    | string
    | number
    | boolean
    | null
    | JsonValue[]
    | { [key: string]: JsonValue }

export type Session = {
    id: number
    user_id: number
    status: 'in_progress' | 'completed'
    expected_question_code: string | null
    profile: Record<string, JsonValue> | null
    profile_confirmed: boolean
    created_at: string
}

export type QuestionnaireQuestion = {
    question_code: string
    question_text: string
}

export type QuestionnaireResponse = {
    question_code: string
    answer_text: string
    question_text?: string | null
    answer_value?: JsonValue
}

export type QuestionnaireAnswerData = {
    question_code: string
    question_text: string
    answer_text: string
    answer_value: JsonValue
}

export type QuestionnaireAnswerRead = QuestionnaireAnswerData & {
    id: number
    session_id: number
    updated_at: string
}

export type QuestionnaireState = {
    status: 'in_progress' | 'completed'
    expected_question_code: string | null
    answers: Record<string, QuestionnaireAnswerData>
}

export type SessionAction =
    | 'start'
    | 'answer'
    | 'correct'
    | 'confirm'
    | 'reopen'

export type SessionActionRequest = {
    action: SessionAction
    reponse?: QuestionnaireResponse
}

export type QuestionnaireActionResponse = {
    etat: QuestionnaireState
    next_question: QuestionnaireQuestion | null
    answers_to_save: QuestionnaireAnswerData[]
    answer_codes_to_delete: string[]
    profile: Record<string, JsonValue>
    profile_confirmed: boolean
    errors: string[]
}
