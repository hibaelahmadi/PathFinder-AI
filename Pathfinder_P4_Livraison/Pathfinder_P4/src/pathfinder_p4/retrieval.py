"""Local hybrid retrieval: TF-IDF + latent semantic vectors (LSA), no API key."""
import asyncio,json,re,unicodedata
from functools import lru_cache
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
STOP=set('le la les de du des un une et en au aux pour sur a est dans avec par ou quelle quelles quels quel comment je tu il elle nous vous ce cette ces se son sa ses que qui the of and in to for is as'.split())
ALIASES={'aui':'al akhawayn','isic':'information communication','ensa':'sciences appliquees','encg':'commerce gestion','emsi':'marocaine ingenieur','ia':'intelligence artificielle','ai':'intelligence artificielle','code':'programmation informatique','coding':'informatique','dev':'developpement logiciel','software':'logiciel informatique','doctor':'medecine','nurse':'infirmier','business':'management gestion','computer':'informatique','data':'donnees statistiques','sma':'mathematiques','svt':'biologie'}
def tokens(s):
 s=unicodedata.normalize('NFKD',s.lower()).encode('ascii','ignore').decode()
 a=[x for x in re.findall(r'[a-z0-9]+',s) if len(x)>1 and x not in STOP]
 return a

def read_chunks(root=ROOT):return [json.loads(l) for l in (root/'documents/chunks.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]

def build_index(root=ROOT):
 from sklearn.feature_extraction.text import TfidfVectorizer
 from sklearn.decomposition import TruncatedSVD
 from scipy.sparse import save_npz
 rows=read_chunks(root);v=TfidfVectorizer(tokenizer=tokens,token_pattern=None,lowercase=False,sublinear_tf=True,dtype=np.float64)
 X=v.fit_transform([r['text'] for r in rows]);k=min(128,X.shape[0]-1,X.shape[1]-1)
 svd=TruncatedSVD(n_components=k,random_state=42);E=svd.fit_transform(X);E/=np.maximum(np.linalg.norm(E,axis=1,keepdims=True),1e-12)
 out=root/'index';out.mkdir(exist_ok=True);save_npz(out/'tfidf.npz',X)
 np.savez_compressed(out/'lsa.npz',components=svd.components_,embeddings=E,idf=v.idf_)
 (out/'vocabulary.json').write_text(json.dumps(v.vocabulary_,ensure_ascii=False),encoding='utf8')
 import hashlib
 digest=hashlib.sha256((root/'documents/chunks.jsonl').read_bytes()).hexdigest()
 (out/'model.json').write_text(json.dumps(dict(algorithm='TF-IDF + TruncatedSVD/LSA',dimensions=k,random_state=42,corpus_sha256=digest,neural_embeddings=False,documents=len(rows))),encoding='utf8')
 _index.cache_clear()
 return {'documents':len(rows),'dimensions':k}

@lru_cache(maxsize=1)
def _index():
 from scipy.sparse import load_npz
 import hashlib
 m=json.loads((ROOT/'index/model.json').read_text());digest=hashlib.sha256((ROOT/'documents/chunks.jsonl').read_bytes()).hexdigest()
 if m['corpus_sha256']!=digest:raise ValueError('Index périmé : exécuter python -m pathfinder_p4.cli build-index')
 return read_chunks(),json.loads((ROOT/'index/vocabulary.json').read_text()),load_npz(ROOT/'index/tfidf.npz'),dict(np.load(ROOT/'index/lsa.npz',allow_pickle=False))

FILTERS={'institution_id','program_id','city','sector','field','academic_year','direct_post_bac','exploration_visible','source_id'}
def search_evidence(query,filters=None,top_k=5):
 if not isinstance(query,str) or not query.strip():return []
 if not isinstance(top_k,int) or isinstance(top_k,bool) or not 1<=top_k<=50:raise ValueError('top_k doit être entre 1 et 50')
 filters=filters or {}
 if set(filters)-FILTERS:raise ValueError('Filtre inconnu: '+','.join(sorted(set(filters)-FILTERS)))
 rows,vocab,X,m=_index();terms=tokens(query)
 for t in list(terms):terms.extend(tokens(ALIASES.get(t,'')))
 from collections import Counter
 from scipy.sparse import csr_matrix
 c=Counter(t for t in terms if t in vocab)
 if not c:return []
 q=np.zeros(len(vocab))
 for t,n in c.items():q[vocab[t]]=(1+np.log(n))*m['idf'][vocab[t]]
 q/=max(np.linalg.norm(q),1e-12);lex=np.asarray(X@q).ravel();z=q@m['components'].T;z/=max(np.linalg.norm(z),1e-12);sem=m['embeddings']@z;score=.7*lex+.3*np.maximum(sem,0)
 result=[]
 for idx in np.argsort(-score):
  if lex[idx]<0.035 or score[idx]<0.05:continue
  r=rows[idx]
  if any((r.get(k) not in val if isinstance(val,list) else r.get(k)!=val) for k,val in filters.items()):continue
  result.append(dict(r,retrieval_score=round(float(score[idx]),6),retrieval_method='tfidf_lsa_hybrid',admission_verified=False))
  if len(result)>=top_k:break
 return result

async def retrieve_evidence(query,filters=None,top_k=5):
 return await asyncio.to_thread(search_evidence,query,filters,top_k)
