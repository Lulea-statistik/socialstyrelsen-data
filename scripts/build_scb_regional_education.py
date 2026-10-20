"""Build comparable regional education shares using SCB UF0506 PxWeb metadata.

Compute shares only from a complete disjoint education partition for the
same region, year, sex and age. No mortality denominator join.
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
    # SCB publishes categories 1..7 and US (unknown), without a total row.
    # They are disjoint categories; include unknowns in the denominator.
    education_codes=set(level["values"])
    if education_codes != set("1234567")|{"US"}:
        raise ValueError("Unexpected education partition: "+str(sorted(education_codes)))
    total_code=None
    query=[]
    for d in dims:
        if d["code"]==region["code"]:values=regional
        elif d["code"]==measure["code"] if measure else False:values=d["values"][:1]
        else:values=d["values"]
        query.append({"code":d["code"],"selection":{"filter":"item","values":values}})
    response=request(url,json.dumps({"query":query,"response":{"format":"json"}},ensure_ascii=False).encode("utf-8"))
    print("SCB metadata dimensions:",[(d["code"],d["text"],len(d["values"])) for d in dims],flush=True)
    print("SCB response columns:",response.get("columns"),flush=True)
    print("SCB sample row:",response["data"][0] if response.get("data") else None,flush=True)
    cols=[c["code"] for c in response["columns"]]
    records=[]
    for row in response["data"]:
        if len(cols)==len(row["key"])+1 and "ContentsCode" in cols:
            codes=[x for x in cols if x!="ContentsCode"]
        elif len(cols)==len(row["key"]):
            codes=cols
        else:
            raise ValueError("Unrecognized PxWeb dimension keys/columns: %s/%s" % (len(row["key"]),len(cols)))
        if len(row["values"])!=1:
            raise ValueError("Expected exactly one selected measure; got %s. Review metadata and content selection." % len(row["values"]))
        val=row["values"][0]
        try:n=float(str(val).replace(",","."))
        except (ValueError,TypeError):n=None
        records.append({"dimensions":dict(zip(codes,row["key"])),"value":n,"raw":val})
    from collections import defaultdict
    grouped=defaultdict(dict)
    for row in records:
        d=row["dimensions"]
        key=(d[region["code"]],d[sex["code"]],d[age["code"]],d[year["code"]])
        level_code=d[level["code"]]
        if level_code in grouped[key]:
            raise ValueError("Duplicate education cell: "+str((key,level_code)))
        grouped[key][level_code]=row["value"]
    output=[]
    excluded=0
    for (region_code,sex_code,age_code,year_code),cells in grouped.items():
        if set(cells)!=education_codes or any(not isinstance(v,(int,float)) or not (v>=0) for v in cells.values()):
            excluded+=1
            continue
        denominator=sum(cells.values())
        if denominator<=0:
            excluded+=1
            continue
        for level_code in level["values"]:
            value=cells[level_code]
            output.append({"region":region_code,"sex":sex_code,"age":age_code,"year":year_code,"level":level_code,"share":round(100*value/denominator,5)})
    print("Complete education partitions:",len(grouped)-excluded,"excluded:",excluded,flush=True)
    if not output:raise ValueError("No reliable regional education shares calculated")
    result={"status":"regional_education_shares_from_complete_partition","source":url,"title":metadata.get("title"),"dimensions":{k:{"values":v["values"],"labels":v["valueTexts"]} for k,v in [("region",region),("sex",sex),("age",age),("level",level),("year",year)]},"education_total_code":total_code,"denominator_definition":"Sum of all 8 disjoint levels 1-7 and US, with US included","excluded_incomplete_partitions":excluded,"observations":output,"caveats":["Regional shares within source age/sex/year populations; not mortality risk.","Do not interpret as medelfolkmangd or the fixed 2019 education frame of Tema526N."]}
    p=Path("docs/data/scb-regional-education.json");p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print("Saved",len(output),"regional shares to",p)
if __name__=="__main__":main()
