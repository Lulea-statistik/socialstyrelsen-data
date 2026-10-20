"""Discover official SCB PxWeb metadata before designing fertility-rate joins.
Do not assume variable codes or compute fertility ratios until verified.
"""
import json,urllib.request,urllib.error
from pathlib import Path
BASE="https://api.scb.se/OV0104/v1/doris/sv/ssd/BE/BE0101/"
TABLES={"births_pre2025":"BE0101H/FoddaK","population_pre2025":"BE0101A/BefolkningNy"}
out={"status":"metadata_inventory","source":"SCB PxWeb API v1","tables":{},"join_ready":False,
"notes":["Birth counts are liveborn children, not conception events or unique mothers.","Age-specific fertility requires age- and year-matched female population denominators.","Use exposure approximations carefully: year-end stocks differ from annual mean population.","SCB 2025 CKM publication must be assessed separately before time-series stitching."]}
for key,path in TABLES.items():
    url=BASE+path
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Lulea-statistik-research/1.0"})
        with urllib.request.urlopen(req,timeout=50) as r:
            meta=json.load(r)
        out["tables"][key]={"url":url,"title":meta.get("title"),"variables":[
            {"code":v.get("code"),"text":v.get("text"),"values":v.get("values",[]),
            "valueTexts":v.get("valueTexts",[]),"elimination":v.get("elimination")}
            for v in meta.get("variables",[])]}
    except (OSError,ValueError) as exc:
        out["tables"][key]={"url":url,"error":str(exc)}
target=Path("docs/data/scb-fertility-metadata.json");target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(out,ensure_ascii=False,indent=2))
for k,t in out["tables"].items():
    print(k,t.get("title"),[(v["code"],len(v["values"])) for v in t.get("variables",[])],t.get("error"))
if any("error" in t for t in out["tables"].values()):
    raise SystemExit("SCB metadata fetch failed; audit saved locally but not publishable as validated metadata")
