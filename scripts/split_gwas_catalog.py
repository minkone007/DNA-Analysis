#!/usr/bin/env python3
"""
split_gwas_catalog.py
======================
Takes the full GWAS Catalog associations TSV (downloaded once from
https://www.ebi.ac.uk/gwas/docs/file-downloads) and splits it into
per-trait TSV files ready for run_pipeline.py.

Usage:
  python3 scripts/split_gwas_catalog.py \
    --input data/gwas_catalog_full.tsv \
    --output data/traits

The full catalog is ~200MB. This script reads it once and writes
one TSV per trait group into data/traits/.
"""

import csv
import argparse
import sys
from pathlib import Path
from collections import defaultdict

# ── Trait grouping map ────────────────────────────────────────────────────────
# Maps keywords found in DISEASE/TRAIT or MAPPED_TRAIT columns
# to a clean output filename.
# Order matters — first match wins.
TRAIT_MAP = [
    # Cardiovascular
    ("coronary_artery_disease", [
        "coronary artery disease","coronary heart disease","myocardial infarction",
        "ischemic heart disease","angina"]),
    ("blood_pressure", [
        "blood pressure","hypertension","systolic","diastolic"]),
    ("atrial_fibrillation", [
        "atrial fibrillation","atrial flutter"]),
    ("stroke", [
        "ischemic stroke","stroke","cerebral infarction"]),
    ("heart_failure", [
        "heart failure","cardiac failure"]),

    # Cancer
    ("breast_cancer", ["breast cancer","breast carcinoma"]),
    ("prostate_cancer", ["prostate cancer","prostate carcinoma"]),
    ("colorectal_cancer", ["colorectal cancer","colon cancer","rectal cancer"]),
    ("melanoma", ["melanoma","skin cancer","cutaneous melanoma"]),
    ("lung_cancer", ["lung cancer","lung carcinoma"]),
    ("bladder_cancer", ["bladder cancer"]),

    # Neurological
    ("alzheimer", ["alzheimer","alzheimer's disease"]),
    ("parkinson", ["parkinson","parkinson's disease"]),
    ("multiple_sclerosis", ["multiple sclerosis"]),
    ("depression", ["major depressive disorder","depression","depressive"]),
    ("schizophrenia", ["schizophrenia"]),
    ("bipolar_disorder", ["bipolar disorder","bipolar"]),
    ("adhd", ["attention deficit","adhd"]),
    ("autism", ["autism","autistic"]),

    # Metabolic
    ("cholesterol", ["ldl cholesterol","hdl cholesterol","total cholesterol",
                     "cholesterol levels","cholesterol measurement"]),
    ("triglycerides", ["triglyceride","triglycerides"]),
    ("bmi", ["body mass index","bmi","obesity"]),
    ("diabetes", ["type 2 diabetes","t2d","type 2 diabetes mellitus"]),
    ("type1_diabetes", ["type 1 diabetes","t1d","type 1 diabetes mellitus"]),
    ("gout", ["gout","uric acid"]),
    ("vitamin_d", ["vitamin d","25-hydroxyvitamin"]),

    # Autoimmune
    ("rheumatoid_arthritis", ["rheumatoid arthritis"]),
    ("celiac_disease", ["celiac disease","coeliac disease"]),
    ("crohn_disease", ["crohn","crohn's disease"]),
    ("inflammatory_bowel", ["inflammatory bowel disease","ibd","ulcerative colitis"]),
    ("asthma", ["asthma"]),
    ("lupus", ["lupus","systemic lupus"]),
    ("psoriasis", ["psoriasis"]),

    # Longevity / ageing
    ("longevity", ["longevity","lifespan","healthspan","aging","ageing","centenarian"]),

    # Physical traits
    ("height", ["height","body height","standing height"]),
    ("hair_loss", ["alopecia","androgenetic alopecia","male-pattern baldness",
                   "hair loss","baldness"]),
    ("eye_color", ["eye color","eye colour","iris","iris pigmentation"]),
    ("hair_color", ["hair color","hair colour","hair pigmentation"]),
    ("skin_color", ["skin color","skin colour","skin pigmentation","skin tone"]),

    # Lifestyle / nutrition
    ("alcohol_consumption", ["alcohol consumption","alcohol intake","alcohol flush"]),
    ("lactase_persistence", ["lactase persistence","lactose tolerance","lactase"]),
    ("caffeine_metabolism", ["caffeine","coffee consumption"]),
    ("sleep_duration", ["sleep duration","sleep","chronotype","insomnia"]),

    # Kidney / other organs
    ("chronic_kidney_disease", ["chronic kidney disease","kidney function",
                                 "renal function","egfr"]),

    # Intelligence / education
    ("intelligence", ["intelligence","cognitive ability","educational attainment",
                      "cognitive performance"]),

    # Fitness
    ("muscle_strength", ["grip strength","muscle strength","muscle mass"]),
    ("vo2_max", ["vo2 max","cardiorespiratory fitness","aerobic capacity"]),

    # Pharmacogenomics
    ("pharmacogenomics", ["drug response","medication","warfarin","clopidogrel",
                          "statin response","adverse drug"]),
]

def classify_row(row: dict) -> str | None:
    """Return the trait slug for a row, or None if no match."""
    # Check both DISEASE/TRAIT and MAPPED_TRAIT columns
    text = " ".join([
        row.get("DISEASE/TRAIT", ""),
        row.get("MAPPED_TRAIT", ""),
    ]).lower()

    for slug, keywords in TRAIT_MAP:
        if any(kw in text for kw in keywords):
            return slug
    return None

def main():
    parser = argparse.ArgumentParser(description="Split full GWAS Catalog TSV by trait")
    parser.add_argument("--input",  required=True,
                        help="Full GWAS Catalog TSV (e.g. data/gwas_catalog_full.tsv)")
    parser.add_argument("--output", default="data/traits",
                        help="Output directory for per-trait TSVs (default: data/traits)")
    parser.add_argument("--pval",   type=float, default=1e-5,
                        help="P-value threshold to include (default: 1e-5)")
    parser.add_argument("--skip-existing", action="store_true",
                        help="Skip traits that already have a TSV in output dir")
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_dir  = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        print(f"Download from: https://www.ebi.ac.uk/gwas/docs/file-downloads")
        sys.exit(1)

    file_size_mb = input_path.stat().st_size / 1024 / 1024
    print(f"\nSplit GWAS Catalog")
    print(f"Input:  {input_path} ({file_size_mb:.0f} MB)")
    print(f"Output: {output_dir}")
    print(f"P-val:  < {args.pval:.0e}\n")

    # Collect rows per trait
    trait_rows: dict[str, list] = defaultdict(list)
    header = None
    total  = 0
    kept   = 0
    no_match = 0

    print("Reading catalog...", end=" ", flush=True)
    with open(input_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter="\t")
        header = reader.fieldnames

        for row in reader:
            total += 1

            # P-value filter
            try:
                pval = float(row.get("P-VALUE", "1") or "1")
            except ValueError:
                pval = 1.0
            if pval > args.pval:
                continue

            slug = classify_row(row)
            if slug is None:
                no_match += 1
                continue

            trait_rows[slug].append(row)
            kept += 1

    print(f"done. {total:,} rows → {kept:,} kept ({no_match:,} unclassified)\n")

    if not header:
        print("ERROR: Could not read header from input file")
        sys.exit(1)

    # Write per-trait files
    written = []
    skipped = []

    for slug, rows in sorted(trait_rows.items()):
        out_path = output_dir / f"{slug}.tsv"

        if args.skip_existing and out_path.exists() and out_path.stat().st_size > 5000:
            skipped.append(slug)
            continue

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header, delimiter="\t",
                                    extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        size_kb = out_path.stat().st_size // 1024
        print(f"  OK  {slug:35s} {len(rows):6,} rows  ({size_kb} KB)")
        written.append(slug)

    print(f"\n{'─'*60}")
    print(f"  Written: {len(written)} trait files")
    if skipped:
        print(f"  Skipped (existing): {len(skipped)}")
    print(f"  Location: {output_dir}")
    print(f"\nNow run:")
    print(f"  python3 scripts/run_pipeline.py --all")

if __name__ == "__main__":
    main()