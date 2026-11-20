import json
from .retrieval import ROOT

def load(name):return json.loads((ROOT/'data'/f'{name}.json').read_text(encoding='utf8'))
def programs(city=None,sector=None,field=None,direct_post_bac=None,include_archive=False):
 institutions={i['institution_id']:i for i in load('institutions')};result=[]
 for p in load('programs'):
  if not include_archive and not p['exploration_visible']:continue
  i=institutions[p['institution_id']]
  if city is not None and i['city']!=city:continue
  if sector is not None and i['sector']!=sector:continue
  if field is not None and field not in p['interests']:continue
  if direct_post_bac is not None and p['direct_post_bac'] is not direct_post_bac:continue
  result.append(p)
 return result

def card(program_id):
 p=next((p for p in load('programs') if p['program_id']==program_id),None)
 if p is None:raise KeyError(program_id)
 i=next(i for i in load('institutions') if i['institution_id']==p['institution_id']);s=next(s for s in load('sources') if s['source_id']==p['source_id'])
 return dict(p,institution=i,sources=[s],compatibility_score=None,score_type='compatibility_not_admission_probability',eligibility='a_verifier',cost_label='Frais non renseignés' if p['annual_cost'] is None else str(p['annual_cost'])+' MAD/an',warnings=['Conditions de campagne non confirmées','Pistes métiers et intérêts éditoriaux à valider']+(['Campus à confirmer'] if i['city_status']=='rattachement_a_confirmer' or i['entity_type'].startswith('reseau') else []))

def compare(ids):
 if not 1<=len(ids)<=10:raise ValueError('1 à 10 formations')
 return [card(i) for i in dict.fromkeys(ids)]
