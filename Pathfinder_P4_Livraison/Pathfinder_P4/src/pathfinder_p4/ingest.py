"""Local authorized text/HTML/PDF ingestion. No network fetch or arbitrary remote URL."""
import hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
class Cleaner(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ('script','style','nav'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style','nav'):self.skip=max(0,self.skip-1)
  if t in ('p','div','h1','h2','li'):self.parts.append('\n')
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
def chunk_text(text,max_chars=1800,overlap=180):
 if max_chars<100 or not 0<=overlap<max_chars:raise ValueError('Paramètres de découpage invalides')
 text=re.sub(r'[ \t]+',' ',text).strip();out=[];start=0
 while start<len(text):
  end=min(start+max_chars,len(text))
  if end<len(text):
   cut=text.rfind(' ',start+max_chars//2,end)
   if cut>start:end=cut
  part=text[start:end].strip()
  if part:out.append(part)
  if end==len(text):break
  start=max(start+1,end-overlap)
 return out

def ingest_file(path,metadata):
 for k in ['source_id','document_title','publisher','official_url','checked_at','verification_status']:
  if not metadata.get(k):raise ValueError('Métadonnée manquante: '+k)
 p=Path(path);pages=[]
 if p.suffix.lower()=='.pdf':
  import fitz
  with fitz.open(p) as doc:pages=[(str(n+1),page.get_text()) for n,page in enumerate(doc)]
 else:
  text=p.read_text(encoding='utf8')
  if p.suffix.lower() in ('.html','.htm'):
   c=Cleaner();c.feed(text);text=' '.join(c.parts)
  pages=[('document',text)]
 result=[]
 for page,text in pages:
  for n,part in enumerate(chunk_text(text)):
   key=metadata['source_id']+'|'+page+'|'+str(n)+'|'+part
   result.append(dict(metadata,chunk_id='DOC-'+hashlib.sha256(key.encode()).hexdigest()[:20],text=part,page_or_section=page,content_kind='extrait_document_fourni',institution_id=metadata.get('institution_id'),program_id=metadata.get('program_id'),academic_year=metadata.get('academic_year'),verification_date=metadata.get('verification_date'),exploration_visible=False,direct_post_bac=None))
 if not result:raise ValueError('Document sans texte extractible; OCR ou transcription contrôlée nécessaire')
 return result
