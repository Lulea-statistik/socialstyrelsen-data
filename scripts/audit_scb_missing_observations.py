"""Describe absent/non-numeric combinations in the parsed SCB export.

Cannot infer whether the original API cells were suppressed, blank, or non-numeric.
"""
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / "docs/data/scb-mortality-education.json").read_text(encoding="utf-8"))
out = {"status": "missing_numeric_cells_not_classified", "tables": {}}
for name, item in source["sources"].items():
    dims = [d for d in item["dimensions"] if d["code"] != "ContentsCode"]
    keys = [d["code"] for d in dims]
    values = [d["values"] for d in dims]
    observed = {tuple(row["dimensions"][k] for k in keys)
                for row in source["observations"] if row["table"] == name}
    absent = [dict(zip(keys, combo)) for combo in itertools.product(*values)
              if combo not in observed]
    by_dimension = {dim: dict(sorted(Counter(row[dim] for row in absent).items()))
                    for dim in keys}
    out["tables"][name] = {
        "expected": len(observed) + len(absent),
        "numeric_observations": len(observed),
        "absent_or_non_numeric": len(absent),
        "by_dimension": by_dimension,
        "combinations": absent,
        "interpretation": "Not classified: original raw API response must be inspected.",
    }
path = ROOT / "docs/data/scb-missing-observations-audit.json"
path.write_text(json.dumps(out, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print("Missing/non-numeric combinations:", {k:v["absent_or_non_numeric"] for k,v in out["tables"].items()})
