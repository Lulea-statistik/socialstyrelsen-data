"""Exploratory ecological correlation: women's BMI (SCB ULF 16-29) versus SCB fertility rate.
No interpretation as conception probability, causal effect, or individual association.
"""
import json, math, statistics
from collections import defaultdict
from pathlib import Path
bmi=json.loads(Path('docs/data/bmi-comparison.json').read_text())
fert=json.loads(Path('docs/data/scb-fertility-rates.json').read_text())
ages=set(range(16,30))
annual=defaultdict(lambda:[0,0.])
for r in fert['data']:
 if r['age'] in ages:
  annual[r['year']][0]+=r['births']
  annual[r['year']][1]+=r['women_mean_approx']
assert all(annual[y][1]>0 for y in range(1992,2025))
lookup=defaultdict(dict)
for r in bmi['scb']:
 if r['age']=='16-29 år' and r['measure']=='Body Mass Index (BMI)':
  lookup[r['period']][r['bmi']]=r['value']
groups={'overweight_or_obesity':['övervikt (BMI mellan 25,0 och 29,9)','obesitas (BMI är 30,0 eller mer)'],
        'obesity':['obesitas (BMI är 30,0 eller mer)']}
def pearson(x,y):
 if len(x)<4:return None
 mx=statistics.mean(x);my=statistics.mean(y)
 a=sum((t-mx)**2 for t in x);b=sum((t-my)**2 for t in y)
 return sum((u-mx)*(v-my) for u,v in zip(x,y))/math.sqrt(a*b) if a*b>0 else None
out={'status':'exploratory_ecological_association','population':'Women aged 16-29, Sweden',
 'note':'Correlations between population survey BMI and live-birth rate do not estimate effects of BMI on conception or childbirth.',
 'correlations':{},'series':{}}
for key,cats in groups.items():
 rows=[]
 for period,catvals in lookup.items():
  if not all(k in catvals for k in cats):continue
  try:first,last=map(int,period.split('-'))
  except ValueError:continue
  if first<1992 or last>2024:continue
  birth=sum(annual[y][0] for y in range(first,last+1))
  exposure=sum(annual[y][1] for y in range(first,last+1))
  if exposure<=0:continue
  rows.append({'period':period,'period_start':first,'period_end':last,'bmi_pct':sum(catvals[k] for k in cats),
               'births_per_1000':1000*birth/exposure,'birth_count':birth,'female_exposure_approx':exposure})
 rows.sort(key=lambda r:r['period_start'])
 levels=pearson([r['bmi_pct'] for r in rows],[r['births_per_1000'] for r in rows])
 diffs=[(rows[i]['bmi_pct']-rows[i-1]['bmi_pct'],rows[i]['births_per_1000']-rows[i-1]['births_per_1000']) for i in range(1,len(rows))]
 out['correlations'][key]={'n_periods':len(rows),'r_levels':levels,'r_consecutive_differences':pearson([x for x,y in diffs],[y for x,y in diffs]),
    'warning':'Descriptive ecological correlation; long-term trends, autocorrelation, survey sampling uncertainty and changing childbearing patterns not controlled.'}
 out['series'][key]=rows
assert any(len(r)>=10 for r in out['series'].values()),'Insufficient observed periods'
p=Path('docs/data/bmi-fertility-exploratory.json')
p.write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('Created exploratory comparisons',json.dumps(out['correlations'],ensure_ascii=False))
