"""Generate a bounded browser dataset from the official Socialstyrelsen ZIP export."""
import csv, io, json, os, urllib.request, zipfile
from pathlib import Path
URL='https://sdb.socialstyrelsen.se/export/csv/statistikdatabasen-dodsorsaker.zip'
ZIP=Path(os.environ.get('SOURCE_ZIP','/tmp/dodsorsaker.zip'))
OUT=Path('docs/data/dodsorsaker.json')
def main():
    if not ZIP.exists():
        print('Downloading official export...')
        urllib.request.urlretrieve(URL, ZIP)
    meta={}
    rows=[]
    # Limit first release to selected broad categories to reduce browser payload;
    # never aggregate overlapping cause groups.
    diagnoses=None  # Include every published diagnosis interval plus special categories
    with zipfile.ZipFile(ZIP) as archive:
        for dim,label in [('diagnos','diagnoser'),('region','regioner'),('kon','kön'),('alder','åldrar')]:
            name=next(n for n in archive.namelist() if 'meta - '+label+'.csv' in n)
            with archive.open(name) as stream:
                rdr=csv.DictReader(io.TextIOWrapper(stream,encoding='utf-8-sig'),delimiter=';')
                field={'diagnos':'Diagnos','region':'Region','kon':'Kön','alder':'Ålder'}[dim]
                meta[dim]={row[field]:row['Text'] for row in rdr}
                if dim=='diagnos':
                    diagnoses={k for k in meta[dim] if '-' in k or k in {'99','Alk','U07','Spec1'}}
        for fname in archive.namelist():
            if 'data - antal döda' not in fname:continue
            with archive.open(fname) as stream:
                rdr=csv.reader(io.TextIOWrapper(stream,encoding='utf-8-sig'),delimiter=';')
                next(rdr)
                for parts in rdr:
                    if len(parts)<7:continue
                    measure,year,region,diagnos,sex,age,value=parts[:7]
                    if diagnos not in diagnoses or age!='99':continue
                    try:val=float(value.replace(',','.'))
                    except ValueError:continue # suppressed / absent data not zero
                    rows.append([int(measure),int(year),region,diagnos,sex,age,val])
    meta['diagnos']={k:v for k,v in meta['diagnos'].items() if k in diagnoses}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({'meta':meta,'data':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    if OUT.stat().st_size > 95_000_000:
        raise RuntimeError('Webbdata över 95 MB, måste delas upp i flera filer')
    print(f'Wrote {len(rows)} rows ({OUT.stat().st_size:,} bytes)')
if __name__=='__main__':main()
