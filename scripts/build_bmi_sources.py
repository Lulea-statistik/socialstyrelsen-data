"""Prepare auditable BMI series from SCB ULF and Socialstyrelsen exports.
Does not infer fertility from birth-registry data or silently harmonise survey age bands.
"""
import csv, io, json, re, urllib.request, zipfile
from pathlib import Path
SCB='https://www.statistikdatabasen.scb.se/Resources/PX/bulk/ssd/sv/TAB6607_sv.zip'
SOC='https://sdb.socialstyrelsen.se/export/csv/statistikdatabasen-graviditeter%2c%20forlossningar%20och%20nyfodda.zip'
OUT=Path('docs/data/bmi-source-series.json')
def load_zip(url,filename):
    p=Path('/tmp')/filename
    if not p.exists():urllib.request.urlretrieve(url,p)
    return zipfile.ZipFile(p)
def decode_csv(z,name):
    data=z.read(name)
    for enc in ('utf-8-sig','cp1252'):
        try:return data.decode(enc)
        except UnicodeDecodeError:pass
    raise ValueError('Unknown encoding: '+name)
def main():
    out={'method':'source_series_only_no_correlation_without_age_and_period_alignment','scb':[],'socialstyrelsen':[],'notes':[]}
    with load_zip(SCB,'scb-ulf-bmi.zip') as z:
        name=next(n for n in z.namelist() if n.lower().endswith('.csv'))
        reader=csv.DictReader(io.StringIO(decode_csv(z,name)))
        out['scb_columns']=reader.fieldnames
        for r in reader:
            # Preserve source labels and uncertainty measures; never transform interval estimates into annual observations.
            out['scb'].append(r)
    with load_zip(SOC,'socialstyrelsen-graviditet.zip') as z:
        n=next(n for n in z.namelist() if 'meta - variabler.csv' in n)
        variables={r['Variabel']:r for r in csv.DictReader(io.StringIO(decode_csv(z,n)),delimiter=';')}
        out['socialstyrelsen_metadata']={}\n        for meta_name,field in [('meta - mått.csv','Mått'),('meta - åldrar.csv','Ålder'),('meta - paritet.csv','Paritet'),('meta - region.csv','Region')]:\n            filename=next(n for n in z.namelist() if meta_name in n)\n            out['socialstyrelsen_metadata'][field]={row[field]:row['Text'] for row in csv.DictReader(io.StringIO(decode_csv(z,filename)),delimiter=';')}\n        candidates={k:v['Text'] for k,v in variables.items() if re.search(r'BMI|övervikt|fetma|obesitas|kroppsmasseindex',v['Text'],re.I)}
        out['socialstyrelsen_bmi_variables']=candidates
        for name in z.namelist():
            if ' - data - ' not in name or not name.endswith('.csv'):continue
            for r in csv.DictReader(io.StringIO(decode_csv(z,name)),delimiter=';'):
                if r.get('Variabel') in candidates:
                    out['socialstyrelsen'].append(r)
    out['notes']=['SCB ULF is a population sample. Socialstyrelsen captures pregnancies ending in childbirth.',
                  'Source age bands, units, definition, uncertainty and collection periods must be inspected before correlations.',
                  'No records in this dataset measure conception probability among women trying to conceive.',
                  'Do not treat missing values or suppression marks as zeros.']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
    print('SCB rows:',len(out['scb']),'Socialstyrelsen BMI rows:',len(out['socialstyrelsen']))
    print('BMI variables:',candidates)
    assert out['scb'] and candidates and out['socialstyrelsen']
    if OUT.stat().st_size>95_000_000:raise RuntimeError('Output too large; partition required')
if __name__=='__main__':main()
