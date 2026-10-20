"""Fetch Folkhalsomyndigheten BMI table via PxWeb v1 API.

The source publishes four-year rolling regional estimates, not annual data.
Keep dimensions/measure metadata and raw cell markers; never infer a pooled series.
"""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = "A_Folkhalsodata/A_Folkhalsodata__Z_ovrigdata__HLVkn__Hals/vikt.px"
API_CANDIDATES = [
    "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/" + TABLE_PATH,
    "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/" + TABLE_PATH.removesuffix(".px"),
    "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/" + TABLE_PATH + "/",
    "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/pxweb/api/v1/sv/" + TABLE_PATH,
]

def request(url, payload=None):
    for retry in range(3):
        try:
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "User-Agent": "Lulea-statistik-BMI-source-audit/1.0",
            })
            with urllib.request.urlopen(req, timeout=50) as response:
                return json.load(response)
        except Exception:
            if retry == 2:
                raise
            time.sleep(2 * (retry + 1))

def main():
    metadata, url = None, None
    errors = []
    for candidate in API_CANDIDATES:
        try:
            obj = request(candidate)
            if isinstance(obj, dict) and isinstance(obj.get("variables"), list):
                metadata, url = obj, candidate
                break
            errors.append(candidate + ": no PxWeb variables array")
        except Exception as exc:
            errors.append(candidate + ": " + str(exc))
    if metadata is None:
        raise RuntimeError("Could not establish FHM PxWeb v1 metadata URL; check API link in PxWeb interface: " + " | ".join(errors))
    variables = metadata["variables"]
    for dim in variables:
        if len(dim["values"]) != len(dim["valueTexts"]):
            raise ValueError("Metadata code-label mismatch: " + dim["code"])
    # Target national, Norrbotten and Lulea geographic comparisons when published.
    selection = []
    for dim in variables:
        values = dim["values"]
        if "region" in dim["text"].casefold() or dim["code"].casefold() in ("region", "omrade"):
            preferred = [v for v in ("00", "25", "2580") if v in values]
            if not preferred:
                raise ValueError("Expected geographic code 00/25/2580 not present; inspect FHM metadata")
            chosen = preferred
        else:
            chosen = values
        selection.append({"code": dim["code"], "selection": {"filter": "item", "values": chosen}})
    payload = json.dumps({"query": selection, "response": {"format": "json"}}, ensure_ascii=False).encode("utf-8")
    data = request(url, payload)
    if not isinstance(data.get("data"), list):
        raise ValueError("Expected PxWeb JSON data records")
    codes = [v["code"] for v in data["columns"]]
    observations = []
    for row in data["data"]:
        if len(row["key"]) != len(codes):
            raise ValueError("PxWeb key and column length mismatch")
        for index, original in enumerate(row["values"]):
            value = str(original) if original is not None else ""
            try:
                number = float(value.replace(",", "."))
            except (ValueError, TypeError):
                number = None
            observations.append({"dimensions": dict(zip(codes, row["key"])), "measure_index": index,
                                 "raw_value": value, "value": number})
    result = {
        "status": "official_FHM_BMI_source_separate_from_SCB",
        "url": url,
        "table_url": "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/pxweb/sv/" + TABLE_PATH + "/",
        "title": metadata.get("title"),
        "variables": variables,
        "observations": observations,
        "caveats": [
            "Regional estimates use four-year moving periods, not independent annual values.",
            "Self-reported BMI; population and methodology differ from SCB ULF and medical birth register.",
            "Non age-standardized; never combine or average with SCB observations.",
            "Preserve uncertainty and source time period on every observation.",
        ],
    }
    if not observations:
        raise ValueError("No FHM records returned")
    path = ROOT / "docs/data/fhm-bmi.json"
    path.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Saved", path, len(observations), "cells from", url)

if __name__ == "__main__":
    main()
