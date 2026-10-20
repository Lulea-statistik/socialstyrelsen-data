"""Audit candidate SCB death-cause crosswalk against Socialstyrelsen metadata.
Matching code presence is not equivalent to matching official definitions.
No mortality values are aggregated by this audit.
"""
import json
from pathlib import Path
p=Path('docs/data/dodsorsaker.json')
meta=json.loads(p.read_text(encoding='utf-8'))['meta']['diagnos']
groups={
 'tot':('totalt',['99'],'candidate_exact_total'),
 'tot2':('totalt 35–84 år',['99'],'candidate_age_restricted'),
 'and':('andningsorganens sjukdomar',['J00-J99'],'candidate_icd_chapter'),
 'hjärt':('hjärt-kärlsjukdomar',['I00-I99'],'candidate_icd_chapter'),
 'tum':('tumörer',['C00-D48'],'candidate_icd_chapter'),
 'alk':('alkoholrelaterad dödlighet',['Alk'],'definition_review_required'),
 'daalk':('därav alkoholrelaterad dödlighet',['Alk'],'definition_review_required'),
 'dacov':('därav Covid-19',['U07'],'definition_review_required'),
 'sjalv':('självmord och skadehändelse med oklar avsikt',['X60-X84','Y10-Y34'],'compound_definition_review_required'),
 'skad':('skador och förgiftningar, exkl. oklar avsikt',['V01-Y98'],'compound_definition_review_required'),
 'övr':('övrigt',[],'residual_definition_review_required'),
}
result={'status':'candidate_crosswalk_not_approved_for_aggregation',
 'principle':'No ICD aggregation without checked SCB official cause inclusion rules, age coverage, sex and rate denominator.',
 'groups':[]}
for code,(label,candidates,status) in groups.items():
 result['groups'].append({'scb_code':code,'label':label,'candidate_socialstyrelsen_codes':candidates,
    'code_presence':{candidate:candidate in meta for candidate in candidates},
    'socialstyrelsen_labels':{candidate:meta.get(candidate) for candidate in candidates},
    'validation_status':status,'approved_for_aggregation':False})
out=Path('docs/data/scb-icd-crosswalk-audit.json')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('\n'.join(f"{r['scb_code']}: {r['validation_status']} {r['code_presence']}" for r in result['groups']))
