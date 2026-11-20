"""Deterministic JSON -> SQLite and PostgreSQL SQL exports, with FK constraints."""
import json,sqlite3
from .retrieval import ROOT
ORDER=['sources','institutions','programs','careers','accreditation_history','admissions','program_careers','program_sources','pathways','id_crosswalk','quality_issues']
PK={'sources':'source_id','institutions':'institution_id','programs':'program_id','careers':'career_id','accreditation_history':'accreditation_id','admissions':'admission_id','pathways':'pathway_id','quality_issues':'issue_id'}
FK={'source_id':('sources','source_id'),'institution_id':('institutions','institution_id'),'program_id':('programs','program_id'),'career_id':('careers','career_id')}
def export():
 dbpath=ROOT/'pathfinder.sqlite'
 if dbpath.exists():dbpath.unlink()
 db=sqlite3.connect(dbpath);db.execute('PRAGMA foreign_keys=ON');pg=['BEGIN;','CREATE SCHEMA IF NOT EXISTS pathfinder_p4;','SET search_path TO pathfinder_p4;'];ddl=[]
 for table in ORDER:
  rows=json.loads((ROOT/'data'/f'{table}.json').read_text());keys=list(dict.fromkeys(k for r in rows for k in r));types={}
  for k in keys:
   vals=[r[k] for r in rows if r.get(k) is not None]
   types[k]='BOOLEAN' if vals and all(isinstance(v,bool) for v in vals) else 'INTEGER' if vals and all(isinstance(v,int) for v in vals) else 'REAL' if k=='annual_cost' else 'TEXT'
  defs=['"'+k+'" '+types[k]+(' PRIMARY KEY' if PK.get(table)==k else '') for k in keys]
  for k in keys:
   if k in FK and PK.get(table)!=k:
    parent,pk=FK[k];defs.append(f'FOREIGN KEY("{k}") REFERENCES "{parent}"("{pk}")')
  statement='CREATE TABLE "'+table+'" ('+', '.join(defs)+');';db.execute(statement);pg.append(statement);ddl.append(statement)
  def val(v):return json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v
  data=[[val(r.get(k)) for k in keys] for r in rows]
  db.executemany('INSERT INTO "'+table+'" VALUES ('+','.join('?' for k in keys)+')',data)
  def sqlval(v):
   if v is None:return 'NULL'
   if isinstance(v,bool):return 'TRUE' if v else 'FALSE'
   if isinstance(v,(int,float)):return str(v)
   return "'"+str(v).replace("'","''")+"'"
  for row in data:pg.append('INSERT INTO "'+table+'" VALUES ('+','.join(sqlval(v) for v in row)+');')
 assert not db.execute('PRAGMA foreign_key_check').fetchall()
 assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 db.commit();db.close();pg.append('COMMIT;')
 (ROOT/'sql/postgresql_import.sql').write_text('\n'.join(pg),encoding='utf8')
 (ROOT/'sql/schema.sql').write_text('\n'.join(ddl),encoding='utf8')
 return {'sqlite_integrity':'ok','tables':len(ORDER)}
if __name__=='__main__':print(export())
