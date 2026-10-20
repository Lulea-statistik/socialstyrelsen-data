"""Check raw SCB cell markers against filtered numeric observations.

A marker such as '..' is retained without inferring a suppression reason.
"""
import json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
raw = json.loads((ROOT/"docs/data/scb-raw-cell-markers.json").read_text(encoding="utf-8"))
parsed = json.loads((ROOT/"docs/data/scb-mortality-education.json").read_text(encoding="utf-8"))
result = {"status":"raw_cell_markers_audited","tables":{},"interpretation":"Non-numeric symbols are not converted to zero. Consult the official table notes for their meaning."}
for table, metadata in parsed["sources"].items():
    dims = [x["code"] for x in metadata["dimensions"] if x["code"]!="ContentsCode"]
    expected = 1
    for d in metadata["dimensions"]:
        if d["code"]!="ContentsCode": expected*=len(d["values"])
    cells = [c for c in raw["cells"] if c["table"]==table]
    numeric = [o for o in parsed["observations"] if o["table"]==table]
    keys = [tuple(c["dimensions"][k] for k in dims) for c in cells]
    if len(keys)!=len(set(keys)): raise ValueError(f"{table}: duplicate raw keys")
    parsed_keys = {tuple(c["dimensions"][k] for k in dims) for c in numeric}
    numeric_raw_keys = {tuple(c["dimensions"][k] for k in dims) for c in cells if c["numeric"]}
    if numeric_raw_keys != parsed_keys: raise ValueError(f"{table}: numeric keys disagree")
    markers = dict(sorted(Counter(c["raw_value"] for c in cells if not c["numeric"]).items()))
    if len(cells)!=expected: raise ValueError(f"{table}: expected {expected} raw cells, got {len(cells)}")
    result["tables"][table]={"expected":expected,"raw_cells":len(cells),"numeric_cells":len(numeric),"non_numeric_cells":len(cells)-len(numeric),"markers":markers}
(ROOT/"docs/data/scb-raw-cell-audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Raw cell coverage validated:",result["tables"])
