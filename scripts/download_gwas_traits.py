#!/usr/bin/env python3
"""
download_gwas_traits.py
========================
Downloads trait-specific TSV files from the NHGRI-EBI GWAS Catalog API.
Places them in data/traits/ ready for run_pipeline.py — no other changes needed.

Usage:
  python3 scripts/download_gwas_traits.py            # download all
  python3 scripts/download_gwas_traits.py --list     # show what's available
  python3 scripts/download_gwas_traits.py --trait coronary_artery_disease
  python3 scripts/download_gwas_traits.py --tier 1   # only high-priority
  python3 scripts/download_gwas_traits.py --force    # re-download existing

Data is free, no API key required. CC-BY 4.0 licensed by NHGRI-EBI.
"""

import urllib.request
import sys
import time
import argparse
from pathlib import Path

ROOT_DIR   = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "data" / "traits"

# ── Trait catalog ──────────────────────────────────────────────────────────────
# slug → (filename, efo_id, tier, description)
TRAITS = {
    # TIER 1 — high clinical impact
    "coronary_artery_disease": ("coronary_artery_disease.tsv", "EFO_0001645", 1,
        "Coronary artery disease — major cardiac event risk"),
    "blood_pressure":          ("blood_pressure.tsv",          "EFO_0006340", 1,
        "Blood pressure (systolic / diastolic)"),
    "atrial_fibrillation":     ("atrial_fibrillation.tsv",     "EFO_0000275", 1,
        "Atrial fibrillation — stroke and heart failure risk"),
    "stroke":                  ("stroke.tsv",                  "EFO_0000712", 1,
        "Ischemic stroke"),
    "breast_cancer":           ("breast_cancer.tsv",           "EFO_0000305", 1,
        "Breast cancer risk"),
    "prostate_cancer":         ("prostate_cancer.tsv",         "EFO_0001663", 1,
        "Prostate cancer risk"),
    "colorectal_cancer":       ("colorectal_cancer.tsv",       "EFO_0005842", 1,
        "Colorectal cancer risk"),
    "melanoma":                ("melanoma.tsv",                "EFO_0000389", 1,
        "Melanoma / skin cancer risk"),
    "alzheimer":               ("alzheimer.tsv",               "EFO_0000249", 1,
        "Alzheimer's disease"),
    "parkinson":               ("parkinson.tsv",               "EFO_0002508", 1,
        "Parkinson's disease"),

    # TIER 2 — important, solid coverage
    "bmi":                     ("bmi.tsv",                     "EFO_0004340", 2,
        "Body mass index"),
    "triglycerides":           ("triglycerides.tsv",           "EFO_0004530", 2,
        "Triglyceride levels"),
    "hdl_cholesterol":         ("hdl_cholesterol.tsv",         "EFO_0004612", 2,
        "HDL cholesterol"),
    "ldl_cholesterol":         ("ldl_cholesterol.tsv",         "EFO_0004611", 2,
        "LDL cholesterol"),
    "type1_diabetes":          ("type1_diabetes.tsv",          "EFO_0001359", 2,
        "Type 1 diabetes"),
    "rheumatoid_arthritis":    ("rheumatoid_arthritis.tsv",    "EFO_0000685", 2,
        "Rheumatoid arthritis"),
    "celiac_disease":          ("celiac_disease.tsv",          "EFO_0001060", 2,
        "Celiac disease"),
    "crohn_disease":           ("crohn_disease.tsv",           "EFO_0000384", 2,
        "Crohn's disease"),
    "multiple_sclerosis":      ("multiple_sclerosis.tsv",      "EFO_0003885", 2,
        "Multiple sclerosis"),
    "depression":              ("depression.tsv",              "EFO_0003761", 2,
        "Major depressive disorder"),
    "schizophrenia":           ("schizophrenia.tsv",           "EFO_0000692", 2,
        "Schizophrenia"),
    "bipolar_disorder":        ("bipolar_disorder.tsv",        "EFO_0000289", 2,
        "Bipolar disorder"),
    "longevity":               ("longevity.tsv",               "EFO_0004378", 2,
        "Longevity / lifespan"),
    "vitamin_d":               ("vitamin_d.tsv",               "EFO_0004631", 2,
        "Vitamin D levels"),

    # TIER 3 — lifestyle, traits, niche
    "alcohol_consumption":     ("alcohol_consumption.tsv",     "EFO_0007878", 3,
        "Alcohol consumption / flush reaction"),
    "lactase_persistence":     ("lactase_persistence.tsv",     "EFO_0004761", 3,
        "Lactase persistence / lactose tolerance"),
    "sleep_duration":          ("sleep_duration.tsv",          "EFO_0005271", 3,
        "Sleep duration"),
    "chronic_kidney_disease":  ("chronic_kidney_disease.tsv",  "EFO_0003884", 3,
        "Chronic kidney disease"),
    "gout":                    ("gout.tsv",                    "EFO_0004415", 3,
        "Gout / uric acid levels"),
    "asthma":                  ("asthma.tsv",                  "EFO_0000270", 3,
        "Asthma"),
    "eye_color":               ("eye_color.tsv",               "EFO_0003840", 3,
        "Eye color / iris pigmentation"),
    "hair_color":              ("hair_color.tsv",              "EFO_0003845", 3,
        "Hair color / pigmentation"),
    "muscle_strength":         ("muscle_strength.tsv",         "EFO_0004299", 3,
        "Muscle strength / grip strength"),
    "vo2_max":                 ("vo2_max.tsv",                 "EFO_0004312", 3,
        "VO2 max / cardiorespiratory fitness"),
}

HEADERS = {"User-Agent": "DNA-Virtual-Lab/1.0 (personal genomics research)"}

def fetch_trait(efo_id, output_file):
    url = (f"https://www.ebi.ac.uk/gwas/api/search/downloads/associations"
           f"?efoId={efo_id}&download=true&content=association")
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return 0, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return 0, str(e)
    except Exception as e:
        return 0, str(e)

    lines = [l for l in data.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return 0, "empty response"

    output_file.write_text("\n".join(lines), encoding="utf-8")
    return len(lines) - 1, "ok"

def main():
    parser = argparse.ArgumentParser(description="Download GWAS Catalog TSVs")
    parser.add_argument("--trait",   help="Single trait slug to download")
    parser.add_argument("--tier",    choices=["1","2","3"], help="Download only this tier")
    parser.add_argument("--list",    action="store_true")
    parser.add_argument("--force",   action="store_true", help="Re-download existing")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.list:
        print(f"\n{'SLUG':35s} {'EFO':15s} T  DESCRIPTION")
        print("─" * 90)
        for slug, (fname, efo, tier, desc) in TRAITS.items():
            exists = "✓" if (OUTPUT_DIR / fname).exists() else " "
            print(f"[{exists}] {slug:33s} {efo:15s} {tier}  {desc}")
        print(f"\n✓ = already downloaded to {OUTPUT_DIR}")
        return

    if args.trait:
        if args.trait not in TRAITS:
            print(f"ERROR: '{args.trait}' not found. Use --list to see options.")
            sys.exit(1)
        targets = {args.trait: TRAITS[args.trait]}
    elif args.tier:
        t = int(args.tier)
        targets = {k: v for k, v in TRAITS.items() if v[2] <= t}
    else:
        targets = TRAITS

    print(f"\nGWAS Catalog Downloader")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Traits: {len(targets)}\n")

    if args.dry_run:
        for slug, (fname, efo, tier, desc) in targets.items():
            exists = (OUTPUT_DIR / fname).exists()
            status = "EXISTS" if exists else "DOWNLOAD"
            print(f"  {status:8s}  Tier {tier}  {slug}")
        return

    success, failed = 0, []
    for slug, (fname, efo, tier, desc) in targets.items():
        out = OUTPUT_DIR / fname
        if not args.force and out.exists() and out.stat().st_size > 1000:
            print(f"  SKIP     {slug} ({out.stat().st_size//1024} KB already)")
            success += 1
            continue

        print(f"  Tier {tier}  {slug}...", end=" ", flush=True)
        n, status = fetch_trait(efo, out)
        if n > 0:
            print(f"OK  {n:,} rows ({out.stat().st_size//1024} KB)")
            success += 1
        else:
            print(f"FAILED: {status}")
            failed.append(slug)
            if out.exists(): out.unlink()
        time.sleep(0.5)

    print(f"\n{'─'*50}")
    print(f"  Done: {success}/{len(targets)} traits")
    if failed:
        print(f"  Failed: {', '.join(failed)}")
    print(f"\nNow run:")
    print(f"  python3 scripts/run_pipeline.py --all")

if __name__ == "__main__":
    main()