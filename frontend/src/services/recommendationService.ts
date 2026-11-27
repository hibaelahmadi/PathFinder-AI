import { buildQueryString, request } from './http'
import type { SessionRecommendations } from '../types/recommendation'

export function getSessionRecommendations(
    sessionId: number,
    token: string,
    topN = 20,
    signal?: AbortSignal,
) {
    const qs = buildQueryString({ top_n: topN })
    return request<SessionRecommendations>(
        `/sessions/${sessionId}/recommendations${qs}`,
        {
            token,
            signal,
        },
    )
}
