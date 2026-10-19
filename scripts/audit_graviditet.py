"""Inventory official maternity statistics CSV export before mapping measures."""
import csv, io, json, zipfile, urllib.request
from pathlib import Path
URL='https://sdb.socialstyrelsen.se/export/csv/statistikdatabasen-graviditeter%2c%20forlossningar%20och%20nyfodda.zip'
zpath=Path('/tmp/graviditet.zip')
urllib.request.urlretrieve(URL,zpath)
inventory=[]
with zipfile.ZipFile(zpath) as z:
    for name in z.namelist():
        if not name.lower().endswith('.csv'):continue
        with z.open(name) as stream:
            sample=io.TextIOWrapper(stream,encoding='utf-8-sig',errors='replace')
            reader=csv.reader(sample,delimiter=';')
            head=next(reader,[])
            examples=[row[:10] for _,row in zip(range(3),reader)]
        inventory.append({'file':name,'size_bytes':z.getinfo(name).file_size,'headers':head,'sample_rows':examples})
Path('docs/data').mkdir(parents=True,exist_ok=True)
Path('docs/data/graviditet-inventering.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
print('CSV files inventoried:',len(inventory))
