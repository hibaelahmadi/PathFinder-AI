import unittest,json,asyncio,tempfile,sqlite3
from pathlib import Path
from fastapi.testclient import TestClient
from pathfinder_p4.retrieval import ROOT,search_evidence,retrieve_evidence,read_chunks
from pathfinder_p4.catalog import load,programs,card,compare
from pathfinder_p4.api import app
from pathfinder_p4.ingest import chunk_text,ingest_file
class DeliveryTests(unittest.TestCase):
 def test_unique_ids(self):
  for table,key in [('programs','program_id'),('institutions','institution_id'),('sources','source_id'),('accreditation_history','accreditation_id')]:
   r=load(table);self.assertEqual(len(r),len({x[key] for x in r}))
 def test_relations(self):
  I={x['institution_id'] for x in load('institutions')};S={x['source_id'] for x in load('sources')};P={x['program_id'] for x in load('programs')}
  for p in load('programs'):self.assertIn(p['institution_id'],I);self.assertIn(p['source_id'],S)
  for a in load('admissions'):self.assertIn(a['program_id'],P);self.assertIn(a['source_id'],S)
 def test_vocabulary(self):
  v=json.loads((ROOT/'data/vocabulary.json').read_text())['categories']
  for p in load('programs'):
   for key in ['interests','skills','career_paths']:self.assertTrue(set(p[key])<=set(v[key]))
 def test_unknown_not_zero(self):
  for p in load('programs'):self.assertIsNone(p['annual_cost']);self.assertIsNone(p['accepted_bac_types']);self.assertFalse(p['admissions_current_verified'])
 def test_durations(self):
  for p in load('programs'):
   if p['duration_months'] is not None:self.assertTrue(0<p['duration_months']<=120)
   if p['entry_route']=='apres_bac_plus_3':self.assertIs(p['direct_post_bac'],False)
 def test_no_automatic_eligibility(self):
  for p in load('admissions'):self.assertFalse(p['usable_for_hard_filter'])
 def test_retrieval_sources(self):
  r=search_evidence('ENSA Marrakech cycle préparatoire',{'institution_id':'PUB056'},3);self.assertTrue(r)
  for x in r:self.assertEqual(x['institution_id'],'PUB056');self.assertTrue(x['official_url'].startswith('https://'));self.assertTrue(x['page_or_section'])
 def test_empty_and_unknown(self):
  self.assertEqual(search_evidence(''),[]);self.assertEqual(search_evidence('zzxyqv987654'),[])
 def test_strict_filters(self):
  self.assertEqual(search_evidence('informatique',{'city':'VILLE_INEXISTANTE'}),[])
  with self.assertRaises(ValueError):search_evidence('test',{'typo':'x'})
 def test_async_contract(self):self.assertIsInstance(asyncio.run(retrieve_evidence('informatique',top_k=2)),list)
 def test_archive_filter(self):
  for p in programs():self.assertTrue(p['exploration_visible']);self.assertIs(p['direct_post_bac'],True)
 def test_cards_and_compare(self):
  p=programs()[0];r=card(p['program_id']);self.assertEqual(r['cost_label'],'Frais non renseignés');self.assertIsNone(r['compatibility_score']);self.assertEqual(len(compare([p['program_id']]*2)),1)
 def test_api(self):
  c=TestClient(app);self.assertEqual(c.get('/health').status_code,200);self.assertEqual(c.get('/api/v1/programs?limit=0').status_code,422);self.assertEqual(c.get('/api/v1/programs/unknown').status_code,404)
  r=c.post('/api/v1/evidence',json={'query':'zzxyqv987654'});self.assertEqual(r.json()['status'],'no_evidence');self.assertEqual(c.post('/api/v1/evidence',json={'query':'test','filters':{'typo':1}}).status_code,422)
 def test_chunking(self):
  t='phrase importante '*400;c=chunk_text(t,200,20);self.assertGreater(len(c),1);self.assertTrue(all(len(x)<=200 for x in c))
  with self.assertRaises(ValueError):chunk_text(t,100,100)
 def test_ingestion(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.html';p.write_text('<h1>Programme</h1><script>malicious</script><p>Mathématiques</p>')
   r=ingest_file(p,dict(source_id='X',document_title='Test',publisher='Test',official_url='https://example.org',checked_at='2026-11-18',verification_status='test'))
   self.assertNotIn('malicious',r[0]['text']);self.assertEqual(r[0]['source_id'],'X')
 def test_conflicts_excluded(self):
  for p in load('programs'):
   if p['status']=='conflit_registre_a_resoudre':self.assertFalse(p['exploration_visible'])
 def test_pipeline_validation(self):
  from pathfinder_p4.pipeline import validate
  self.assertEqual(validate()['errors'],0)
 def test_acronyms(self):self.assertTrue(search_evidence('AUI Bachelor',top_k=2))
 def test_database(self):
  db=sqlite3.connect(ROOT/'pathfinder.sqlite');self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok');self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[]);db.close()
 def test_chunk_metadata(self):
  for r in read_chunks():
   for k in ['source_id','official_url','document_title','publisher','page_or_section','checked_at','verification_status']:self.assertTrue(r[k])
if __name__=='__main__':unittest.main()
