"""Validate canonical JSON, export relational DB, rebuild corpus and vector index."""
import json,re
from .retrieval import ROOT,build_index
from .catalog import load
from .database import export

def validate():
 errors=[];sources=load('sources');institutions=load('institutions');programs=load('programs');v=load('vocabulary')['categories']
 for rows,key in [(sources,'source_id'),(institutions,'institution_id'),(programs,'program_id')]:
  ids=[r[key] for r in rows]
  if len(ids)!=len(set(ids)):errors.append('Duplicate '+key)
 S={s['source_id'] for s in sources};I={i['institution_id'] for i in institutions}
 for p in programs:
  if p['source_id'] not in S or p['institution_id'] not in I:errors.append('Broken FK '+p['program_id'])
  for k in ['skills','interests','career_paths']:
   if not set(p[k])<=set(v[k]):errors.append('Unknown vocabulary '+p['program_id']+' '+k)
  if p['annual_cost'] is not None and p['annual_cost']<0:errors.append('Negative cost '+p['program_id'])
  if p['admissions_current_verified'] and not p['academic_year']:errors.append('Missing campaign '+p['program_id'])
 if errors:raise ValueError('\n'.join(errors))
 return {'errors':0,'programs':len(programs),'institutions':len(institutions)}

def clean_text(text):return re.sub(r'\s+',' ',text).strip() if isinstance(text,str) else text

def rebuild_corpus():
 S={s['source_id']:s for s in load('sources')};I={i['institution_id']:i for i in load('institutions')};rows=[]
 for p in load('programs'):
  i=I[p['institution_id']];s=S[p['source_id']]
  text=f"{i['name']} {i.get('acronym') or ''} ({i['city'] or 'campus à confirmer'}). Formation : {p['name']}. Diplôme/cycle publié : {p['degree_type']}."
  if p['duration_months']:text+=f" Durée du cycle décrit : {p['duration_months']} mois."
  if p['options']:text+=' Options publiées : '+p['options']+'.'
  if p['curriculum_summary']:text+=' Contenu résumé : '+p['curriculum_summary']
  text+=f" Voie d’accès : {p['entry_route']}. {p['notes']}"
  rows.append(dict(chunk_id='CH-'+p['program_id'],text=clean_text(text),content_kind='synthese_factuelle_structuree_non_citation',institution_id=p['institution_id'],program_id=p['program_id'],source_id=s['source_id'],document_title=s['title'],publisher=s['publisher'],official_url=s['url'],page_or_section=p['source_locator'],academic_year=p['academic_year'],checked_at=p['checked_at'],verification_date=None,verification_status=p['status'],city=i['city'],sector=i['sector'],field=p['field'],direct_post_bac=p['direct_post_bac'],exploration_visible=p['exploration_visible']))
 for i in I.values():
  s=S[i['source_id']]
  rows.append(dict(chunk_id='CHI-'+i['institution_id'],text=clean_text(f"Annuaire : {i['name']} {i.get('acronym') or ''}; ville de référence : {i['city']}. Secteur : {i['sector_detail']}. {i['notes']}"),content_kind='notice_annuaire_non_preuve_admission',institution_id=i['institution_id'],program_id=None,source_id=s['source_id'],document_title=s['title'],publisher=s['publisher'],official_url=s['url'],page_or_section=i['source_locator'],academic_year=i['source_year'],checked_at=s['checked_at'],verification_date=None,verification_status=i['status'],city=i['city'],sector=i['sector'],field=None,direct_post_bac=None,exploration_visible=False))
 # Separate user-supplied documents survive canonical rebuilds.
 extra=ROOT/'documents/additional_chunks.jsonl'
 if extra.exists():rows.extend(json.loads(l) for l in extra.read_text(encoding='utf8').splitlines() if l.strip())
 if len({r['chunk_id'] for r in rows})!=len(rows):raise ValueError('Duplicate chunk_id')
 if any(r['source_id'] not in S for r in rows):raise ValueError('Unregistered source')
 (ROOT/'documents/chunks.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf8')
 return len(rows)

if __name__=='__main__':
 print(validate());print(export());print({'chunks':rebuild_corpus()});print(build_index())
