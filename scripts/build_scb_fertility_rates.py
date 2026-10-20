"""Build Sweden age-specific fertility rates directly from verified SCB PxWeb v1.
Rate denominator: mean female year-end population at t-1 and t, all civil statuses.
Births: live births by mother's exact age, summed across child's sexes.
"""
import json,urllib.request,time,collections
from pathlib import Path
META=json.loads(Path('docs/data/scb-fertility-metadata.json').read_text())
BASE=META['tables']; ages=[str(x) for x in range(15,49)]
years=list(range(1992,2025))
def post(url,selection):
    payload=json.dumps({'query':[{'code':k,'selection':{'filter':'item','values':v}} for k,v in selection.items()],'response':{'format':'json'}}).encode()
    for attempt in range(5):
        try:
            req=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json','User-Agent':'Lulea-statistik-research/1.0'})
            with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
        except Exception as exc:
            print('SCB retry',attempt+1,url,exc,flush=True)
            if attempt==4:raise
            time.sleep(3*(attempt+1))
def fetch_series(table,base):
    rows=[]
    for i in range(0,len(base),5):
        ys=[str(y) for y in base[i:i+5]]
        if table=='births_pre2025':
            query={'Region':['00'],'AlderModer':ages,'Kon':['1','2'],'ContentsCode':['BE0101E2'],'Tid':ys}
        else:
            query={'Region':['00'],'Civilstand':['OG','G','SK','ÄNKL'],'Alder':ages,'Kon':['2'],'ContentsCode':['BE0101N1'],'Tid':ys}
        d=post(BASE[table]['url'],query)
        columns=[v['code'] for v in d['columns']]
        for item in d['data']:
            row=dict(zip(columns,item['key']))
            val=item['values'][0]
            if val in ('..','.',None,''):continue
            row['value']=int(float(val.replace(',','.')))
            rows.append(row)
    return rows
def main():
    births=fetch_series('births_pre2025',years)
    pop=fetch_series('population_pre2025',list(range(1991,2025)))
    b=collections.defaultdict(int);p=collections.defaultdict(int)
    for r in births:b[(int(r['Tid']),int(r['AlderModer']))]+=r['value']
    for r in pop:p[(int(r['Tid']),int(r['Alder']))]+=r['value']
    expected=len(years)*len(ages)
    if len(b)!=expected or len(p)!=expected+len(ages):
        raise ValueError(f'Incomplete SCB cells: births {len(b)}/{expected}, population {len(p)}/{expected+len(ages)}')
    out=[]
    for yr in years:
        for a in map(int,ages):
            n=b[yr,a];den=(p[yr-1,a]+p[yr,a])/2
            if den<=0:raise ValueError('Zero population')
            out.append({'year':yr,'age':a,'births':n,'women_yearend_prev':p[yr-1,a],
                        'women_yearend':p[yr,a],'women_mean_approx':den,
                        'births_per_1000':round(1000*n/den,5)})
    result={'status':'calculated_age_specific_rates','geography':'Sweden','ages':'15–48','years':'1992–2024',
            'source_births':BASE['births_pre2025']['url'],'source_population':BASE['population_pre2025']['url'],
            'method':'live births to mothers aged 15–48 / arithmetic mean of population of women in matching exact age at end of year t-1 and t * 1000',
            'caveats':['Approximate exposure, not midyear population or exact person-years.','Counts liveborn children, not pregnancies or unique birthing women.','Excludes births to mothers under 15 and 49+.','Does not measure the probability of conception.'],
            'data':out}
    target=Path('docs/data/scb-fertility-rates.json')
    target.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
    print('Wrote',len(out),'age-year rates',target.stat().st_size,'bytes')
if __name__=='__main__':main()
