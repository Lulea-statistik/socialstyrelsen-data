"""Fetch Folkhalsomyndigheten BMI table via PxWeb v1 API.

The source publishes four-year rolling regional estimates, not annual data.
Keep dimensions/measure metadata and raw cell markers; never infer a pooled series.
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = "A_Folkhalsodata/A_Folkhalsodata__Z_ovrigdata__HLVkn__Hals/vikt.px"
API_CANDIDATES = [
    "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/" + TABLE_PATH,
    "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/A_Folkhalsodata__Z_ovrigdata__HLVkn__Hals/vikt.px",
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
        except urllib.error.HTTPError as exc:
            body = exc.read(1500).decode('utf-8', 'replace')
            raise RuntimeError(f'HTTP {exc.code} at {url}: {body[:600]}') from exc
        except Exception:
            if retry == 2:
                raise
            time.sleep(2 * (retry + 1))

def main():
    metadata, url = None, None
    root = "https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/A_Folkhalsodata"
    # PxWeb browser directory IDs contain db prefixes and '__' delimiters.
    # The API requires the actual catalogue IDs discovered at each level.
    path = []
    for wanted in ["Z_ovrigdata", "HLVkn", "Hals", "vikt"]:
        parent_url = root + ("/" + "/".join(path) if path else "")
        listing = request(parent_url)
        if not isinstance(listing, list):
            raise ValueError("Expected API catalogue at " + parent_url)
        print("Catalogue", parent_url, [(x.get("id"), x.get("type")) for x in listing][:80], flush=True)
        candidates = [item for item in listing if item.get("id", "").casefold().removesuffix(".px") == wanted.casefold()]
        if not candidates:
            raise ValueError("Catalogue segment " + wanted + " not found at " + parent_url +
                             "; available: " + str([(x.get("id"), x.get("text")) for x in listing][:60]))
        item = candidates[0]
        path.append(item["id"])
        print("Selected", wanted, "->", item["id"], "type", item.get("type"), flush=True)
    url = root + "/" + "/".join(path)
    metadata = request(url)
    if not isinstance(metadata, dict) or not isinstance(metadata.get("variables"), list):
        raise ValueError("BMI table did not return PxWeb variables: " + url)
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
    print("FHM metadata dimensions:", [(v["code"], v["text"], v["values"][:5]) for v in variables], flush=True)
    print("FHM response columns:", data["columns"], flush=True)
    sample = data["data"][0] if data["data"] else None
    print("FHM sample row:", sample, flush=True)
    observations = []
    for row in data["data"]:
        key = row["key"]
        values = row["values"]
        if len(key) > len(codes):
            raise ValueError("More keys than response columns")
        dimension_codes = codes[:len(key)]
        if len(values) != 1:
            raise ValueError("Unexpected multiple values per row; review FHM metadata before interpreting")
        dimensions = dict(zip(dimension_codes, key))
        original = values[0]
        value = str(original) if original is not None else ""
        try:
            number = float(value.replace(",", "."))
        except (ValueError, TypeError):
            number = None
        observations.append({"dimensions": dimensions, "raw_value": value, "value": number})
    # Preserve the native metadata: no invented ContentsCode or rate/CI labels.
    # If metrics are columns in the response keys, they already exist in dimensions.
    # If metrics are separate response values, stop rather than attach wrong labels.
    if not observations:
        raise ValueError("No observations in FHM response")
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
