"""Audit source-specific SCB PxWeb dimensions against existing official data snapshot.

Does not establish ICD equivalence or aggregate mortality values.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/data/scb-mortality-education.json"
CROSSWALK = ROOT / "docs/data/scb-icd-crosswalk-audit.json"
OUTPUT = ROOT / "docs/data/scb-source-metadata-audit.json"

def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    audit = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    valid_codes = {g["scb_code"] for g in audit["groups"]}
    sources = {}
    for name in ("age", "education"):
        source = data["sources"][name]
        dimensions = source["dimensions"]
        cause = next(v for v in dimensions if v["code"] == "Dodsorsak")
        years = next(v for v in dimensions if v["code"] == "Tid")
        codes = cause["values"]
        if len(codes) != len(set(codes)):
            raise ValueError(f"Duplicate cause codes in {name}")
        if len(codes) != len(cause["valueTexts"]):
            raise ValueError(f"Misaligned cause labels in {name}")
        unknown = sorted(set(codes) - valid_codes)
        if unknown:
            raise ValueError(f"Unreviewed SCB codes in {name}: {unknown}")
        sources[name] = {
            "source_url": source["url"],
            "title": source["title"],
            "cause_codes": codes,
            "cause_labels": dict(zip(codes, cause["valueTexts"])),
            "years": years["values"],
            "dimension_codes": [v["code"] for v in dimensions],
            "observations": sum(r["table"] == name for r in data["observations"]),
        }
        if not sources[name]["observations"]:
            raise ValueError(f"No observations for {name}")
    result = {
        "status": "source_metadata_checked_icd_equivalence_not_approved",
        "source": str(SOURCE.relative_to(ROOT)),
        "sources": sources,
        "age_only_causes": sorted(set(sources["age"]["cause_codes"]) - set(sources["education"]["cause_codes"])),
        "education_only_causes": sorted(set(sources["education"]["cause_codes"]) - set(sources["age"]["cause_codes"])),
        "approved_for_icd_aggregation": False,
        "warning": "SCB source category presence does not prove Socialstyrelsen ICD equivalence. No rates were summed.",
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Source metadata inspected; category mismatches:", result["age_only_causes"], result["education_only_causes"])
if __name__ == "__main__":
    main()
