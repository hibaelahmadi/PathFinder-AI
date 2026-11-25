// P4 data contract. P5 supplies compatibility scores; P3 supplies generated wording.
export interface Evidence {
  chunk_id: string;
  text: string;
  content_kind: string;
  institution_id: string | null;
  program_id: string | null;
  source_id: string;
  document_title: string;
  publisher: string;
  official_url: string;
  page_or_section: string;
  academic_year: string | null;
  checked_at: string;
  verification_date: string | null;
  verification_status: string;
  retrieval_score: number;
  admission_verified: false;
}
export interface Program {
  program_id: string;
  institution_id: string;
  name: string;
  degree_type: string;
  duration_months: number | null;
  duration_scope: 'cycle_decrit';
  entry_route: string;
  direct_post_bac: boolean | null;
  annual_cost: number | null; // MAD/year, tuition only
  accepted_bac_types: string[] | null;
  interests: string[];
  skills: string[];
  career_paths: string[];
  curriculum_summary: string | null;
  academic_year: string | null;
  checked_at: string;
  status: string;
  exploration_visible: boolean;
  admissions_current_verified: boolean;
}
