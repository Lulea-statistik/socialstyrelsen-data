"""Inventory SCB table 5.15 CSV bulk ZIP before interpreting survey categories."""
import csv,io,json,urllib.request,zipfile
from pathlib import Path
url='https://www.statistikdatabasen.scb.se/Resources/PX/bulk/ssd/sv/TAB6607_sv.zip'
target=Path('/tmp/scb-bmi.zip')
urllib.request.urlretrieve(url,target)
results=[]
with zipfile.ZipFile(target) as z:
    for name in z.namelist():
        info=z.getinfo(name)
        obj={'name':name,'size':info.file_size}
        if name.lower().endswith(('.csv','.txt')):
            with z.open(name) as raw:
                sample=io.TextIOWrapper(raw,encoding='utf-8-sig',errors='replace')
                obj['sample']=[line.strip()[:500] for _,line in zip(range(8),sample)]
        results.append(obj)
out=Path('docs/data/scb-bmi-inventering.json')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'source':url,'files':results},ensure_ascii=False,indent=2))
print('SCB files',len(results))
