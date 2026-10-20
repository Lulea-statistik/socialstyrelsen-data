"""Audit regional education shares and publish compact coverage summary."""
import json
from collections import defaultdict,Counter
from pathlib import Path
src=Path("docs/data/scb-regional-education.json")
data=json.loads(src.read_text(encoding="utf-8"))
groups=defaultdict(list)
for row in data["observations"]:
    groups[(row["region"],row["sex"],row["age"],row["year"])].append(row)
errors=[]
region_counts=Counter()
for key,rows in groups.items():
    region_counts[key[0]]+=1
    if len(rows)!=8 or len({r["level"] for r in rows})!=8:
        errors.append({"key":key,"problem":"invalid level partition"})
    total=sum(r["share"] for r in rows)
    if abs(total-100)>0.001:
        errors.append({"key":key,"problem":"shares do not sum to 100","sum":total})
    if any(not (0<=r["share"]<=100) for r in rows):
        errors.append({"key":key,"problem":"share outside 0-100"})
by_selection=defaultdict(set)
for region,sex,age,year in groups:
    by_selection[(sex,age,year)].add(region)
for key,regions in by_selection.items():
    if regions!={"2580","25","00"}:
        errors.append({"key":key,"problem":"incomplete regional comparison","regions":sorted(regions)})
output={"status":"passed" if not errors else "failed","source_status":data["status"],
        "observation_count":len(data["observations"]),"complete_partitions":len(groups),
        "partition_count_by_region":dict(sorted(region_counts.items())),
        "excluded_incomplete_partitions":data["excluded_incomplete_partitions"],
        "age_codes":data["dimensions"]["age"]["values"],
        "sex_codes":data["dimensions"]["sex"]["values"],
        "first_year":data["dimensions"]["year"]["values"][0],
        "last_year":data["dimensions"]["year"]["values"][-1],
        "error_count":len(errors),"errors":errors[:20]}
p=Path("docs/data/scb-regional-education-audit.json")
p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in output.items() if k not in ("age_codes","errors")},ensure_ascii=False))
if errors:raise SystemExit("Regional education quality gates failed")
