"""Build browser dataset for Socialstyrelsen birth and maternity statistics."""
import csv, io, json, os, urllib.request, zipfile
from pathlib import Path
URL='https://sdb.socialstyrelsen.se/export/csv/statistikdatabasen-graviditeter%2c%20forlossningar%20och%20nyfodda.zip'
ZIP=Path(os.environ.get('GRAVIDITET_ZIP','/tmp/graviditet.zip'))
OUT=Path('docs/data/graviditet.json')
def main():
    if not ZIP.exists(): urllib.request.urlretrieve(URL,ZIP)
    rows=[];meta={}
    with zipfile.ZipFile(ZIP) as z:
        for key,needle,code in [('region','meta - region.csv','Region'),('variabel','meta - variabler.csv','Variabel'),('matt','meta - mått.csv','Mått'),('alder','meta - åldrar.csv','Ålder'),('paritet','meta - paritet.csv','Paritet')]:
            fname=next(n for n in z.namelist() if needle in n)
            with z.open(fname) as stream:
                data=csv.DictReader(io.TextIOWrapper(stream,encoding='utf-8-sig'),delimiter=';')
                meta[key]={r[code]:r['Text'] for r in data}
        for fname in z.namelist():
            if ' - data - ' not in fname or not fname.endswith('.csv'):continue
            with z.open(fname) as stream:
                data=csv.DictReader(io.TextIOWrapper(stream,encoding='utf-8-sig'),delimiter=';')
                for r in data:
                    if r['Ålder']!='0' or r['Paritet']!='0': continue
                    try:v=float(r['Värde'].replace(',','.'))
                    except (ValueError,KeyError):continue
                    rows.append([int(r['Mått']),int(r['År']),r['Region'],r['Variabel'],v])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({'meta':meta,'data':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('maternity rows',len(rows),'bytes',OUT.stat().st_size)
    if not rows:raise RuntimeError('No maternity statistics extracted')
    if OUT.stat().st_size>95000000:raise RuntimeError('Output too large for Pages')
if __name__=='__main__':main()
