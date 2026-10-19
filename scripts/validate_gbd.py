"""Validate reviewed GBD estimates; never silently publish unapproved risk values."""
import csv, json, math, sys
from pathlib import Path
inp=Path(sys.argv[1]) if len(sys.argv)>1 else Path('data/gbd-reviewed.csv')
out=Path('docs/data/gbd-verified.json')
fields=['gbd_release','location','year','sex','age','gbd_cause_id','gbd_risk_id','measure','value','lower','upper','source_url','mapping_review_status','license_review_status']
if not inp.exists():
    print('No reviewed dataset; leave public GBD estimates empty.')
    sys.exit(0)
rows=[]
with inp.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f)
    if not set(fields).issubset(reader.fieldnames or []):
        raise ValueError('Missing required fields')
    for n,r in enumerate(reader,2):
        if r['mapping_review_status']!='approved' or r['license_review_status']!='approved':
            raise ValueError(f'Line {n} is not approved')
        if not r['source_url'].startswith('https://'):
            raise ValueError(f'Line {n} lacks HTTPS source')
        if r['measure']!='PAF':
            raise ValueError(f'Line {n}: only PAF is supported in this importer')
        vals=[float(r[k]) for k in ['value','lower','upper']]
        if not all(math.isfinite(v) and 0<=v<=1 for v in vals) or not vals[1]<=vals[0]<=vals[2]:
            raise ValueError(f'Line {n}: invalid PAF interval (fraction 0..1)')
        if not 1990<=int(r['year'])<=2100:
            raise ValueError(f'Line {n}: invalid year')
        rows.append({k:r[k] for k in fields})
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'status':'verified','records':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('Validated',len(rows),'reviewed GBD records')
