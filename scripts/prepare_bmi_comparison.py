"""Prepare non-causal, labelled BMI source comparison (no false age alignment)."""
import json
from pathlib import Path
d=json.loads(Path('docs/data/bmi-source-series.json').read_text())
meta=d.get('socialstyrelsen_metadata',{})
if not all(meta.get(x) for x in ('Mått','Ålder','Paritet','Region')):
    raise ValueError('Official Socialstyrelsen dimension labels absent; rerun source ingestion')
def num(v):
    try:return float(str(v).replace(',','.'))
    except (TypeError,ValueError):return None
scb=[]
for r in d['scb']:
    if r.get('kön')!='kvinnor':continue
    x=num(r.get('Body Mass Index (BMI)'))
    if x is None:continue
    scb.append({'period':r['årsintervall'],'age':r['ålder'],'bmi':r['Body Mass Index'],
                'measure':r['tabellinnehåll'],'value':x,'source':'SCB ULF'})
soc=[]
for r in d['socialstyrelsen']:
    if r.get('Paritet')!='0' or r.get('Region')!='00000':continue
    x=num(r.get('Värde'))
    if x is None:continue
    soc.append({'year':int(r['År']),'age':meta['Ålder'].get(r['Ålder'],r['Ålder']),
                'bmi':d['socialstyrelsen_bmi_variables'][r['Variabel']],
                'measure':meta['Mått'].get(r['Mått'],r['Mått']),
                'value':x,'source':'Socialstyrelsen MFR'})
out={'status':'source_series_unaligned','note':'SCB age bands and two-year periods differ from maternity series. Values must not be pooled or treated as a fertility analysis.',
     'socialstyrelsen_metadata':{k:v for k,v in meta.items() if k!='Region'},
     'scb':scb,'socialstyrelsen':soc}
target=Path('docs/data/bmi-comparison.json')
target.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print('SCB women rows',len(scb),'maternity national rows',len(soc))
print('Maternity age labels:',meta['Ålder'])
print('Maternity measure labels:',meta['Mått'])
