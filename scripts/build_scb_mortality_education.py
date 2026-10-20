"""Fetch and validate SCB's published mortality/education tables through PxWeb API.
Keep official categories rather than pretending a 1:1 ICD crosswalk.
"""
import json,urllib.request,urllib.parse,time
from collections import Counter
from pathlib import Path
BASE='https://api.scb.se/OV0104/v1/doris/sv/ssd/LE/LE0201/LE0201Hälsa/'
TABLES={'age':'Tema525','education':'Tema526N'}
def request(url,payload=None):
 for attempt in range(5):
  try:
   req=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json','User-Agent':'Lulea-statistik-SCB-audit/1.0'})
   with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
  except Exception as error:
   print(url,'attempt',attempt+1,str(error),flush=True)
   if attempt==4:raise
   time.sleep(2*(attempt+1))
def main():
 out={'status':'SCB_official_source_tables','sources':{},'observations':[],'caveats':['Do not sum derived subgroups marked därav into total','Rates per 100,000 are not counts','Education table covers 35–84 and may be age-confounded','SCB and Socialstyrelsen categories require source-verified ICD crosswalk']}
 raw_cells={'status':'original_scb_cell_markers_preserved','tables':{},'cells':[]}
 for group,table in TABLES.items():
  url=BASE.replace('LE0201Hälsa','LE0201H%C3%A4lsa')+table;metadata=request(url)
  dims=metadata['variables']
  out['sources'][group]={'url':url,'title':metadata.get('title'),'dimensions':[{ 'code':v['code'],'text':v['text'],'values':v['values'],'valueTexts':v['valueTexts']} for v in dims]}
  payload=json.dumps({'query':[{'code':v['code'],'selection':{'filter':'item','values':v['values']}} for v in dims], 'response':{'format':'json'}},ensure_ascii=False).encode('utf-8')
  data=request(url,payload)
  codes=[v['code'] for v in data['columns']]
  markers=Counter()
  for row in data['data']:
   val=row['values'][0]
   val=str(val) if val is not None else ''
   try:
    number=float(val.replace(',','.'))
    is_numeric=True
   except (ValueError,AttributeError):
    number=None
    is_numeric=False
    markers[val]+=1
   dimensions=dict(zip(codes,row['key']))
   raw_cells['cells'].append({'table':group,'dimensions':dimensions,'raw_value':val,'numeric':is_numeric})
   if is_numeric:
    out['observations'].append({'table':group,'dimensions':dimensions,'value':number})
  raw_cells['tables'][group]={'returned_cells':len(data['data']),'non_numeric_markers':dict(sorted(markers.items())),'metadata_notes':metadata.get('note'),'metadata_updated':metadata.get('updated')}
  print(group,'rows',sum(r['table']==group for r in out['observations']),flush=True)
 if not all(any(row['table']==k for row in out['observations']) for k in TABLES):raise ValueError('No usable observations in at least one SCB table')
 p=Path('docs/data/scb-mortality-education.json');p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 q=Path('docs/data/scb-raw-cell-markers.json')
 q.write_text(json.dumps(raw_cells,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('Saved',p,p.stat().st_size,'and',q)
if __name__=='__main__':main()
