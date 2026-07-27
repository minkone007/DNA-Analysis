# ⬡ DNA Virtual Lab

A fully offline personal genomics analysis pipeline. Cross-references raw MyHeritage DNA data against the NHGRI-EBI GWAS Catalog, SNPedia 2025, and curated trait libraries to generate a styled HTML health report.

---

## What It Does

- **GWAS cross-reference** — matches your 584k SNPs against 48 trait TSVs from the NHGRI-EBI GWAS Catalog (coronary artery disease, Alzheimer's, T2D, depression, longevity, pigmentation, and more)
- **SNPedia enrichment** — 108,873 SNP entries, extracts genotype-specific narrative for your exact alleles
- **Multi-SNP synthesis** — combines multiple loci into plain-English predictions with severity badges (eye color via IrisPlex panel, hair/skin pigmentation, cholesterol, T2D, Alzheimer's, CAD, BMI, triglycerides, depression, longevity, + 28 GWAS-based summary cards)
- **Styled HTML report** — dark-mode, fully self-contained, shareable as a single file

Everything runs locally. No API calls, no data sent anywhere.

---

## Project Structure

```
DNA Virtual Lab/
├── scripts/
│   ├── run_pipeline.py          # Main entry point
│   ├── snpedia_enricher.py      # SNPedia DB cross-reference
│   ├── trait_synthesizer.py     # Multi-SNP synthesis cards
│   ├── split_gwas_catalog.py    # Splits full GWAS catalog by trait
│   ├── wrap_with_password.py    # Password-protect HTML reports
│   ├── traits_library.json      # Curated SNP interpretations
│   └── traits/                  # Per-trait JSON configs
├── reports/
│   └── health_report_*.html     # Generated reports (committed)
├── data/                        # NOT in git — see Data Setup below
│   ├── SNPedia2025/
│   │   └── SNPedia2025.db
│   ├── traits/                  # Split GWAS TSVs (generated)
│   ├── gwas_catalog_full.tsv    # Downloaded from NHGRI-EBI
│   └── <Name>/
│       └── MyHeritage_raw_dna_data.csv
├── people.json                  # Person config (names, paths, sex)
└── README.md
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/minkone007/DNA-Virtual-Lab.git
cd DNA-Virtual-Lab
```

### 2. Download large data files from Google Drive

Get the shared folder link from the project owner. Download and place:

```
data/SNPedia2025/SNPedia2025.db        (~500 MB)
data/gwas_catalog_full.tsv             (~683 MB)
```

Place your own raw DNA file:
```
data/<YourName>/MyHeritage_raw_dna_data.csv
```

### 3. Split the GWAS catalog into trait files

Run once after downloading `gwas_catalog_full.tsv`:

```bash
python3 scripts/split_gwas_catalog.py \
  --input  data/gwas_catalog_full.tsv \
  --output data/traits
```

This generates ~42 trait TSVs in `data/traits/` (cholesterol, diabetes, Alzheimer's, etc.).

### 4. Configure people.json

Edit `people.json` to add yourself:

```json
{
  "people": [
    {
      "name": "YourName",
      "data_file": "data/YourName/MyHeritage_raw_dna_data.csv",
      "results_dir": "scripts/results/YourName",
      "sex": "M"
    }
  ],
  "shared": {
    "snpedia_db":  "data/SNPedia2025/SNPedia2025.db",
    "gwas_dir":    "data/traits",
    "traits_lib":  "scripts/traits_library.json",
    "traits_dir":  "scripts/traits"
  }
}
```

### 5. Run the pipeline

```bash
# Full run (~5-10 minutes first time)
python3 scripts/run_pipeline.py --person YourName

# Fast re-render using cached results (~5 seconds)
python3 scripts/run_pipeline.py --person YourName --report-only

# Run for everyone in people.json
python3 scripts/run_pipeline.py --all
```

### 6. Open your report

```bash
open scripts/results/YourName/health_report_YourName.html
```

---

## GWAS Catalog Source

The full associations file is downloaded free from:
**https://www.ebi.ac.uk/gwas/docs/file-downloads**

Click **"All associations v1.0.2"** → save as `data/gwas_catalog_full.tsv`.

Data is CC-BY 4.0 licensed by NHGRI-EBI.

---

## SNPedia

SNPedia 2025 DB contains 108,873 SNP entries scraped from [snpedia.com](https://www.snpedia.com).
Licensed CC-BY-NC-SA 3.0. For personal research use only.

---

## Pipeline Flags

| Flag | Effect |
|------|--------|
| `--person Name` | Run for one person |
| `--all` | Run for everyone in people.json |
| `--report-only` | Skip scans, re-render from cached JSON |
| `--skip-gwas` | Skip GWAS scan (reuse cached) |
| `--skip-snpedia` | Skip SNPedia enrichment |
| `--skip-report` | Skip HTML rendering |

---

## Privacy

- Raw DNA files (`data/*/MyHeritage_raw_dna_data.csv`) are excluded from git via `.gitignore`
- Generated HTML reports contain interpreted findings, not raw genotype data
- The SNPedia DB and GWAS catalog are public reference datasets
- All analysis runs locally — no data is sent to any server

---

## Requirements

Python 3.10+ with standard library only (csv, json, sqlite3, re, math, pathlib).
No external packages required.
