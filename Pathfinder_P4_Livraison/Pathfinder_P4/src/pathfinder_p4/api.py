from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from .catalog import programs,card,compare,load
from .retrieval import retrieve_evidence
app=FastAPI(title='Pathfinder P4 — Data et RAG',version='1.0.0')
class Search(BaseModel):
 query:str=Field(min_length=1,max_length=2000)
 filters:dict=Field(default_factory=dict)
 top_k:int=Field(default=5,ge=1,le=50)
class Comparison(BaseModel):
 program_ids:list[str]=Field(min_length=1,max_length=10)
@app.get('/health')
def health():return {'status':'ok','current_admissions_verified':False}
@app.get('/api/v1/programs')
def get_programs(city:str|None=None,sector:str|None=None,field:str|None=None,direct_post_bac:bool|None=None,include_archive:bool=False,offset:int=0,limit:int=50):
 if not 0<=offset or not 1<=limit<=200:raise HTTPException(422,'Pagination invalide')
 rows=programs(city,sector,field,direct_post_bac,include_archive);return {'total':len(rows),'items':rows[offset:offset+limit]}
@app.get('/api/v1/programs/{program_id}')
def get_program(program_id:str):
 try:return card(program_id)
 except KeyError:raise HTTPException(404,'Formation introuvable')
@app.get('/api/v1/institutions')
def get_institutions():return load('institutions')
@app.get('/api/v1/careers')
def get_careers():return load('careers')
@app.get('/api/v1/pathways')
def get_pathways():return load('pathways')
@app.post('/api/v1/compare')
def comparison(body:Comparison):
 try:return {'items':compare(body.program_ids)}
 except KeyError:raise HTTPException(404,'Formation introuvable')
@app.post('/api/v1/evidence')
async def evidence(body:Search):
 try:r=await retrieve_evidence(body.query,body.filters,body.top_k)
 except ValueError as e:raise HTTPException(422,str(e))
 return {'status':'ok' if r else 'no_evidence','evidence':r,'admission_verified':False}
