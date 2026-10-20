"""Audit BMI source JSON without inferring comparability or fertility causality."""
import collections,json
from pathlib import Path
p=Path("docs/data/bmi-source-series.json")
d=json.loads(p.read_text(encoding="utf-8"))
scb=d.get("scb",[]);soc=d.get("socialstyrelsen",[])
def grouped(rows,k):
    c=collections.Counter(str(r.get(k,"")) for r in rows)
    return [{"value":v,"count":n} for v,n in c.most_common()]
report={"status":"inventory_only_not_harmonised","scb_rows":len(scb),"socialstyrelsen_bmi_rows":len(soc),
"scb_columns":d.get("scb_columns",[]),"socialstyrelsen_bmi_variables":d.get("socialstyrelsen_bmi_variables",{}),
"scb_distinct":{k:grouped(scb,k) for k in d.get("scb_columns",[])},
"socialstyrelsen_distinct":{k:grouped(soc,k) for k in ["Mått","År","Region","Variabel","Paritet","Ålder"]},
"scb_sample":scb[:2],"socialstyrelsen_sample":soc[:2],
"validation":{"sources_nonempty":bool(scb and soc),"numerical_correlation_ready":False,
"reason":"Requires verified units, ages, periods and SCB births/population denominators"}}
assert report["validation"]["sources_nonempty"]
out=Path("docs/data/bmi-audit.json")
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("SCB observations:",len(scb))
print("Socialstyrelsen BMI observations:",len(soc))
print("BMI variables:",json.dumps(d.get("socialstyrelsen_bmi_variables",{}),ensure_ascii=False))
print("SCB categories:",json.dumps({k:[x["value"] for x in grouped(scb,k)] for k in d.get("scb_columns",[]) if k!="tabellinnehåll"},ensure_ascii=False))
