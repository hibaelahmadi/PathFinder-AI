import argparse,json
from .retrieval import build_index,search_evidence
p=argparse.ArgumentParser();p.add_argument('command',choices=['build-index','search']);p.add_argument('query',nargs='?',default='');p.add_argument('--top-k',type=int,default=5)
a=p.parse_args()
print(json.dumps(build_index() if a.command=='build-index' else search_evidence(a.query,top_k=a.top_k),ensure_ascii=False,indent=2))
