"""Build comparable regional education shares using SCB UF0506 PxWeb metadata.

Do not derive percentages unless an explicit total-education code is available
for exactly the same region, year, sex and age. No mortality denominator join.
"""
import json, urllib.request, time
from pathlib import Path
BASE="https://api.scb.se/OV0104/v1/doris/sv/ssd/"
CANDIDATES=["UF/UF0506/Utbildning", "UF/UF0506/UF0506B/Utbildning"]
def request(url, data=None):
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,data=data,headers={"Content-Type":"application/json","User-Agent":"Lulea-statistik-UF0506/1.0"})
            with urllib.request.urlopen(req,timeout=60) as f:return json.load(f)
        except Exception:
            if attempt==3:raise
            time.sleep(attempt+1)
def find(dims, hints):
    return next((d for d in dims if any(s in (d["code"]+" "+d["text"]).lower() for s in hints)),None)
def main():
    metadata=None;url=None;failures=[]
    for path in CANDIDATES:
        try:
            m=request(BASE+path)
            if isinstance(m.get("variables"),list):metadata=m;url=BASE+path;break
        except Exception as e:failures.append(path+": "+str(e))
    if not metadata:raise RuntimeError("UF0506 table not located; "+ "; ".join(failures))
    dims=metadata["variables"]
    region=find(dims,["region"]);sex=find(dims,["kön","kon"]);age=find(dims,["ålder","alder"])
    level=find(dims,["utbildningsnivå","utbildningsniva"])
    year=find(dims,["år","tid"])
    measure=next((d for d in dims if d["code"]=="ContentsCode"),None)
    if not all([region,sex,age,level,year]):raise ValueError("Required dimensions absent: "+str([(d["code"],d["text"]) for d in dims]))
    regional=[v for v in ("2580","25","00") if v in region["values"]]
    if len(regional)!=3:raise ValueError("Region coverage incomplete, codes: "+str(regional))
    # Total must be an explicit source value, not an inferred sum of possibly overlapping classes.
    total_candidates=[v for v,t in zip(level["values"],level["valueTexts"]) if ("samtliga" in t.casefold() or "totalt" in t.casefold() or t.casefold().strip()=="alla utbildningsnivåer")]
    if len(total_candidates)!=1:raise ValueError("Cannot identify unique explicit education total: "+str(list(zip(level["values"],level["valueTexts"]))))
    total_code=total_candidates[0]
    query=[]
    for d in dims:
        if d["code"]==region["code"]:values=regional
        elif d["code"]==measure["code"] if measure else False:values=d["values"][:1]
        else:values=d["values"]
        query.append({"code":d["code"],"selection":{"filter":"item","values":values}})
    response=request(url,json.dumps({"query":query,"response":{"format":"json"}},ensure_ascii=False).encode("utf-8"))
    cols=[c["code"] for c in response["columns"] if c["code"]!="ContentsCode"]
    records=[]
    for row in response["data"]:
        if len(cols)!=len(row["key"]) or len(row["values"])!=1:raise ValueError("Unrecognized PxWeb response layout")
        val=row["values"][0]
        try:n=float(str(val).replace(",","."))
        except (ValueError,TypeError):n=None
        records.append({"dimensions":dict(zip(cols,row["key"])),"value":n,"raw":val})
    lookup={(r["dimensions"][region["code"]],r["dimensions"][sex["code"]],r["dimensions"][age["code"]],r["dimensions"][year["code"]],r["dimensions"][level["code"]]):r["value"] for r in records}
    output=[]
    for r in records:
        d=r["dimensions"];level_code=d[level["code"]]
        den=lookup.get((d[region["code"]],d[sex["code"]],d[age["code"]],d[year["code"]],total_code))
        if level_code==total_code or not isinstance(den,(int,float)) or den<=0 or not isinstance(r["value"],(int,float)):continue
        pct=100*r["value"]/den
        if not (0<=pct<=100):continue
        output.append({"region":d[region["code"]],"sex":d[sex["code"]],"age":d[age["code"]],"year":d[year["code"]],"level":level_code,"share":round(pct,5)})
    if not output:raise ValueError("No reliable regional education shares calculated")
    result={"status":"regional_education_shares_from_explicit_total","source":url,"title":metadata.get("title"),"dimensions":{k:{"values":v["values"],"labels":v["valueTexts"]} for k,v in [("region",region),("sex",sex),("age",age),("level",level),("year",year)]},"education_total_code":total_code,"observations":output,"caveats":["Regional shares within source age/sex/year populations; not mortality risk.","Do not interpret as medelfolkmangd or the fixed 2019 education frame of Tema526N."]}
    p=Path("docs/data/scb-regional-education.json");p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print("Saved",len(output),"regional shares to",p)
if __name__=="__main__":main()
