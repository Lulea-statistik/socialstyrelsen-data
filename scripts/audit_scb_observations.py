"""Validate SCB PxWeb observation keys, source dimensions and data coverage.

No comparisons of different age populations or summation of rates.
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/data/scb-mortality-education.json"
OUTPUT = ROOT / "docs/data/scb-observation-audit.json"

def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = {"status": "observation_integrity_checked_not_icd_validated", "tables": {}, "approved_for_icd_aggregation": False}
    for table in ("age", "education"):
        dims = data["sources"][table]["dimensions"]
        codes = [v["code"] for v in dims if v["code"] != "ContentsCode"]
        # PxWeb JSON puts the selected single ContentsCode in columns/values,
        # not in the observation key. Validate this singleton via metadata.
        contents = next((v for v in dims if v["code"] == "ContentsCode"), None)
        if contents is None or len(contents["values"]) != 1:
            raise ValueError(f"{table}: expected one ContentsCode measure")
        allowed = {v["code"]: set(v["values"]) for v in dims}
        rows = [r for r in data["observations"] if r["table"] == table]
        seen = set()
        observed = {code: set() for code in codes}
        failures = []
        for index, row in enumerate(rows):
            dim = row["dimensions"]
            if set(dim) != set(codes):
                failures.append(f"row {index}: unexpected dimensions")
                continue
            key = tuple(dim[code] for code in codes)
            if key in seen:
                failures.append(f"row {index}: duplicated observation key")
            seen.add(key)
            for code, value in dim.items():
                if value not in allowed[code]:
                    failures.append(f"row {index}: unknown {code} value {value}")
                observed[code].add(value)
            value = row["value"]
            if not isinstance(value, (float, int)) or isinstance(value, bool) or value < 0 or value != value or value == float("inf"):
                failures.append(f"row {index}: invalid rate value")
        possible = 1
        for v in dims:
            if v["code"] in codes:
                possible *= len(v["values"])
        result["tables"][table] = {
            "source_url": data["sources"][table]["url"],
            "rows": len(rows),
            "possible_dimension_combinations": possible,
            "missing_or_non_numeric_combinations": possible - len(seen),
            "observed_dimension_values": {code: sorted(values) for code, values in observed.items()},
            "measure_code": contents["values"][0],
            "failures": failures[:30],
        }
        if failures:
            raise ValueError(f"{table}: {len(failures)} integrity errors: {failures[:5]}")
        if not rows or len(rows) > possible:
            raise ValueError(f"{table}: implausible observation count")
    result["note"] = "Missing/non-numeric combinations cannot be classified as suppression or absent records from this filtered export alone. Re-fetch raw response to distinguish them."
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Observation integrity passed:", {name: value["rows"] for name,value in result["tables"].items()})

if __name__ == "__main__":
    main()
