import { buildQueryString, request } from './http'
import type {
    CataloguePage,
    EvidenceResponse,
    EvidenceSearchRequest,
    P4Career,
    P4Institution,
    P4Pathway,
    P4Program,
    P4ProgramCard,
    P4Source,
    P4Vocabulary,
} from '../types/catalogue'

export type ProgramListParams = {
    city?: string
    sector?: string
    field?: string
    direct_post_bac?: boolean
    include_archive?: boolean
    offset?: number
    limit?: number
}

export function getHealthStatus(signal?: AbortSignal) {
    return request<{ status: string }>('/health', { signal })
}

export function listP4Programs(
    params: ProgramListParams = {},
    signal?: AbortSignal,
) {
    const qs = buildQueryString({
        city: params.city,
        sector: params.sector,
        field: params.field,
        direct_post_bac: params.direct_post_bac,
        include_archive: params.include_archive,
        offset: params.offset ?? 0,
        limit: params.limit ?? 100,
    })
    return request<CataloguePage<P4Program>>(`/catalogue/programs${qs}`, {
        signal,
    })
}

export function getP4ProgramCard(programId: string, signal?: AbortSignal) {
    return request<P4ProgramCard>(
        `/catalogue/programs/${encodeURIComponent(programId)}`,
        { signal },
    )
}

export function listP4Institutions(
    offset = 0,
    limit = 100,
    signal?: AbortSignal,
) {
    const qs = buildQueryString({ offset, limit })
    return request<CataloguePage<P4Institution>>(`/catalogue/institutions${qs}`, {
        signal,
    })
}

export function listP4Careers(
    offset = 0,
    limit = 100,
    signal?: AbortSignal,
) {
    const qs = buildQueryString({ offset, limit })
    return request<CataloguePage<P4Career>>(`/catalogue/careers${qs}`, {
        signal,
    })
}

export function listP4Sources(
    offset = 0,
    limit = 100,
    signal?: AbortSignal,
) {
    const qs = buildQueryString({ offset, limit })
    return request<CataloguePage<P4Source>>(`/catalogue/sources${qs}`, {
        signal,
    })
}

export function listP4Pathways(
    offset = 0,
    limit = 100,
    signal?: AbortSignal,
) {
    const qs = buildQueryString({ offset, limit })
    return request<CataloguePage<P4Pathway>>(`/catalogue/pathways${qs}`, {
        signal,
    })
}

export function getP4Vocabulary(signal?: AbortSignal) {
    return request<P4Vocabulary>('/catalogue/vocabulary/current', { signal })
}

export function searchEvidence(
    payload: EvidenceSearchRequest,
    token: string,
    signal?: AbortSignal,
) {
    return request<EvidenceResponse>('/catalogue/evidence', {
        method: 'POST',
        body: payload,
        token,
        signal,
    })
}
