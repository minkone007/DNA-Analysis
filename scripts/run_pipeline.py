#!/usr/bin/env python3
"""
run_pipeline.py — DNA Virtual Lab unified pipeline
====================================================
Run for one person:   python3 scripts/run_pipeline.py --person Minko
Run for all people:   python3 scripts/run_pipeline.py --all
Skip slow steps:      python3 scripts/run_pipeline.py --person Minko --skip-gwas --skip-snpedia

Steps:
  1. Load & index raw DNA (once per person)
  2. Scan traits_library.json + traits/ folder
  3a. GWAS Catalog cross-reference (data/traits/*.tsv)
  3b. SNPedia deep annotation (SNPedia2025.db)
  3c. Specialist scripts (analyze_risks.py, analyze_snpedia.py)
  4. Build personal_summary.json
  5. Render HTML report
"""

import csv, json, glob, sys, subprocess, argparse, traceback, re, math
from pathlib import Path
from collections import defaultdict
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
CONFIG   = ROOT_DIR / "people.json"

PERSON_DEFAULT = "Minko"

# ── Load people.json config ───────────────────────────────────────────────────
def load_config():
    if CONFIG.exists():
        with open(CONFIG) as f:
            return json.load(f)
    # Fallback: single-person legacy mode
    return {
        "people": [{
            "name": PERSON_DEFAULT,
            "data_file": f"data/{PERSON_DEFAULT}/MyHeritage_raw_dna_data.csv",
            "results_dir": "scripts/results",
            "sex": "M",
        }],
        "shared": {
            "snpedia_db":  "data/SNPedia2025/SNPedia2025.db",
            "gwas_dir":    "data/traits",
            "traits_lib":  "scripts/traits_library.json",
            "traits_dir":  "scripts/traits",
        }
    }

def step(n, label):
    print(f"\n{'─'*52}\n  STEP {n}: {label}\n{'─'*52}")

def ok(msg):   print(f"  OK   {msg}")
def warn(msg): print(f"  WARN {msg}")
def fail(msg): print(f"  FAIL {msg}")

# ── STEP 1 — Load DNA ─────────────────────────────────────────────────────────
def load_dna_index(file_path):
    index = {}
    if not file_path.exists():
        fail(f"DNA file not found: {file_path}")
        sys.exit(1)
    with open(file_path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 4 and row[0].startswith("rs"):
                index[row[0].lower()] = row[3].strip().upper()
    ok(f"Indexed {len(index):,} SNPs from {file_path.name}")
    return index

# ── STEP 2 — Trait scan ───────────────────────────────────────────────────────
def scan_traits(dna_index, shared_cfg, results_dir):
    lib_path    = ROOT_DIR / shared_cfg["traits_lib"]
    traits_dir  = ROOT_DIR / shared_cfg["traits_dir"]
    grouped     = defaultdict(list)

    if lib_path.exists():
        raw = lib_path.read_text(encoding="utf-8")
        raw = re.sub(r':\s*\{\s*\.\.\.\s*\}', ': {}', raw)  # fix placeholders
        try:
            library = json.loads(raw)
        except json.JSONDecodeError as e:
            warn(f"traits_library.json invalid JSON: {e}")
            library = {}

        for rsid, info in library.items():
            category   = info.get("category", "General")
            genotype   = dna_index.get(rsid, "N/A")
            interp     = info.get("interpretations", {}).get(genotype, "No interpretation for this genotype.")
            grouped[category].append({
                "rsid": rsid, "name": info.get("name", rsid),
                "genotype": genotype, "interpretation": interp,
                "category": category, "priority": info.get("priority","normal"),
                "pmid_count": len(info.get("pmids",[])), "found": genotype != "N/A",
            })
    else:
        warn("traits_library.json not found")

    if traits_dir.exists():
        for tf in sorted(traits_dir.glob("*.json")):
            try:
                trait_data = json.load(open(tf))
                category   = tf.stem.replace("_"," ").title()
                for rsid, info in trait_data.items():
                    if not rsid.startswith("rs"): continue
                    genotype = dna_index.get(rsid, "N/A")
                    interp   = info.get("interpretations",{}).get(genotype,"No interpretation.")
                    grouped[category].append({
                        "rsid": rsid, "name": info.get("name",rsid),
                        "genotype": genotype, "interpretation": interp,
                        "category": category, "priority": info.get("priority","normal"),
                        "pmid_count": len(info.get("pmids",[])), "found": genotype != "N/A",
                    })
            except Exception as e:
                warn(f"Could not load {tf.name}: {e}")

    results_dir.mkdir(parents=True, exist_ok=True)
    for category, entries in grouped.items():
        slug = category.lower().replace(" ","_")
        with open(results_dir / f"{slug}_results.json","w") as f:
            json.dump({"category": category, "results": entries}, f, indent=2)

    ok(f"Trait scan: {len(grouped)} categories, {sum(len(v) for v in grouped.values())} SNPs")
    return grouped

# ── STEP 3a — GWAS scanner ────────────────────────────────────────────────────
PVAL_SUGGESTIVE = 1e-5
MIN_OR          = 1.05
QUANT_KEYWORDS  = {"height","bmi","cholesterol","ldl","hdl","glucose",
                   "intelligence","educational","cognitive","body mass"}

def is_quantitative(trait_name):
    return any(k in trait_name.lower() for k in QUANT_KEYWORDS)

def dosage(genotype, risk_allele):
    if not genotype or genotype in ("--","N/A",""): return -1
    return sum(1 for a in genotype.upper() if a == risk_allele.upper())

def risk_level(dos, effect, is_quant):
    if dos < 0 or effect is None: return "baseline"
    if not is_quant:
        if dos == 2 and effect >= 1.75:  return "elevated"
        if dos == 2 and effect >= 1.35:  return "moderately elevated"
        if dos == 1 and effect >= 1.75:  return "moderately elevated"
        if effect >= 1.15:               return "slightly elevated"
        return "baseline"
    else:
        if abs(effect) >= 0.5 and dos == 2: return "strong signal"
        if abs(effect) >= 0.2:              return "moderate signal"
        return "mild signal"

def make_gwas_finding(row, dos, trait_name, is_quant):
    gene    = (row.get("MAPPED_GENE") or row.get("REPORTED GENE(S)","")).split(",")[0].strip()[:30] or "unknown locus"
    disease = row.get("DISEASE/TRAIT", trait_name).strip()
    try:    effect = float(row.get("OR or BETA",""))
    except: effect = None
    ci      = row.get("95% CI (TEXT)","").strip()
    context = row.get("CONTEXT","").replace("_"," ")

    if dos == 0:   carrier = "You do not carry the risk allele"
    elif dos == 1: carrier = "You carry one copy of the risk allele (heterozygous)"
    else:          carrier = "You carry two copies of the risk allele (homozygous)"

    if effect is not None:
        if not is_quant:
            ci_str = f", 95% CI {ci}" if ci and ci not in ("NR","") else ""
            eff_str = f" -- OR {effect:.2f}{ci_str} for {disease}"
        else:
            direction = "higher" if effect > 0 else "lower"
            eff_str = f" -- associated with {direction} {disease} (beta {effect:+.3g})"
    else:
        eff_str = ""

    loc = f" Variant near {gene}"
    if context and context.lower() not in ("nr","intergenic variant",""):
        loc += f" ({context})"
    return f"{carrier}{eff_str}.{loc}."

def parse_gwas_tsv(tsv_path, dna_index):
    trait_name = tsv_path.stem.replace("_"," ").title()
    is_quant   = is_quantitative(trait_name)
    hits       = []

    with open(tsv_path, newline="", encoding="utf-8") as f:
        reader = __import__("csv").DictReader(f, delimiter="\t")
        for row in reader:
            snp_field  = row.get("STRONGEST SNP-RISK ALLELE","").strip()
            snps_field = row.get("SNPS","").strip()
            rsid_match = re.search(r"(rs\d+)", snp_field) or re.search(r"(rs\d+)", snps_field)
            if not rsid_match: continue
            rsid = rsid_match.group(1)
            ra_match = re.search(r"rs\d+-([ACGT?])", snp_field, re.IGNORECASE)
            risk_allele = ra_match.group(1).upper() if ra_match else None
            try:    pval = float(row.get("P-VALUE","1"))
            except: pval = 1.0
            if pval > PVAL_SUGGESTIVE: continue
            try:    effect = float(row.get("OR or BETA",""))
            except: effect = None
            if not is_quant and effect is not None and 0 < effect < MIN_OR: continue
            geno  = dna_index.get(rsid)
            dos   = dosage(geno, risk_allele) if (geno and risk_allele) else -1
            gene  = (row.get("MAPPED_GENE") or row.get("REPORTED GENE(S)","")).split(",")[0].strip()[:40]
            rl    = risk_level(dos, effect, is_quant)
            finding = make_gwas_finding(row, dos, trait_name, is_quant) if dos >= 0 else \
                      f"Variant near {gene} -- not on your chip."
            hits.append({
                "rsid": rsid, "risk_allele": risk_allele,
                "your_genotype": geno or "Not on chip", "dosage": dos,
                "gene": gene, "disease": row.get("DISEASE/TRAIT",trait_name).strip(),
                "effect": effect, "is_or": not is_quant, "pvalue": pval,
                "suggestive": pval > 5e-8, "pubmedid": row.get("PUBMEDID","").strip(),
                "risk_level": rl, "finding": finding, "on_chip": geno is not None,
            })

    pgs, pgs_n = 0.0, 0
    for h in hits:
        if h["dosage"] >= 0 and h["effect"] is not None and h["on_chip"]:
            ef = h["effect"]
            pgs += h["dosage"] * (math.log(ef) if (h["is_or"] and ef > 0) else ef)
            pgs_n += 1

    risk_order = {"elevated":0,"moderately elevated":1,"strong signal":2,
                  "slightly elevated":3,"moderate signal":4,"mild signal":5,"baseline":6}
    hits.sort(key=lambda h:(0 if h["on_chip"] else 1, risk_order.get(h["risk_level"],9), h["pvalue"]))

    return {
        "trait": trait_name, "is_quantitative": is_quant,
        "total_gwas_snps": len(hits),
        "on_chip": sum(1 for h in hits if h["on_chip"]),
        "elevated_hits": sum(1 for h in hits if h["risk_level"] in
                            ("elevated","moderately elevated","strong signal")),
        "pgs_score": round(pgs,4), "pgs_snps_used": pgs_n, "results": hits,
    }

TRAIT_CONTEXT = {
    "cholesterol": "Cholesterol is 50-80% heritable. LDL variants affect cardiovascular risk directly. Diet, exercise, and statins are effective regardless of genotype.",
    "diabetes":    "Type 2 diabetes heritability 40-70%. Most variants affect beta-cell function or insulin sensitivity. Lifestyle factors interact strongly with genetic risk.",
    "hair loss":   "Male-pattern baldness is ~80% heritable. The AR/EDA2R locus on the X chromosome (inherited maternally) is the strongest signal, with ORs above 2.0.",
    "height":      "Adult height is ~80% heritable. Individual SNP effects are tiny (0.02-0.1 cm each); your polygenic score reflects cumulative direction.",
    "intelligence":"Cognitive ability heritability 50-80%. Polygenic scores explain ~10-15% of variance. Gene-environment interaction is substantial.",
}

def run_gwas_scanner(dna_index, shared_cfg, results_dir):
    gwas_dir  = ROOT_DIR / shared_cfg["gwas_dir"]
    tsv_files = sorted(gwas_dir.glob("*.tsv")) if gwas_dir.exists() else []
    if not tsv_files:
        warn(f"No TSV files in {gwas_dir}")
        return {}

    gwas_results = {}
    for tsv in tsv_files:
        trait_name = tsv.stem.replace("_"," ").title()
        print(f"  Scanning {tsv.name}...", end=" ", flush=True)
        try:
            result = parse_gwas_tsv(tsv, dna_index)
            ctx_key = next((k for k in TRAIT_CONTEXT if k in trait_name.lower()), None)
            result["context"] = TRAIT_CONTEXT.get(ctx_key,"")
            with open(results_dir / f"gwas_{tsv.stem}.json","w") as f:
                json.dump(result, f, indent=2)
            print(f"OK  {result['total_gwas_snps']} sig SNPs | {result['on_chip']} on chip | "
                  f"{result['elevated_hits']} elevated | PGS {result['pgs_score']:+.3f}")
            gwas_results[trait_name] = result
        except Exception as e:
            print(f"FAILED: {e}")
    ok(f"GWAS: {len(gwas_results)} traits scanned")
    return gwas_results

# ── STEP 3b — SNPedia enrichment ──────────────────────────────────────────────
def run_snpedia_enricher(person_cfg, shared_cfg):
    try:
        # Import from same directory
        import importlib.util
        enricher_path = BASE_DIR / "snpedia_enricher.py"
        if not enricher_path.exists():
            warn("snpedia_enricher.py not found -- skipping SNPedia step")
            return {}
        spec   = importlib.util.spec_from_file_location("snpedia_enricher", enricher_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.enrich_person(person_cfg, shared_cfg)
    except Exception as e:
        warn(f"SNPedia enricher failed: {e}")
        traceback.print_exc()
        return {}

# ── STEP 3c — Specialist scripts ──────────────────────────────────────────────
SPECIALIST_SCRIPTS = ["analyze_risks.py", "analyze_snpedia.py"]

def run_specialist_scripts():
    for script_name in SPECIALIST_SCRIPTS:
        script = BASE_DIR / script_name
        if not script.exists(): continue
        try:
            result = subprocess.run([sys.executable, str(script)],
                                    capture_output=True, text=True, timeout=120)
            if result.returncode == 0: ok(f"Ran {script_name}")
            else: warn(f"{script_name}: {result.stderr[:150]}")
        except subprocess.TimeoutExpired:
            warn(f"{script_name} timed out")
        except Exception as e:
            warn(f"{script_name}: {e}")

# ── STEP 4 — Build summary ────────────────────────────────────────────────────
def build_summary(grouped, gwas_results, snpedia_enriched, results_dir):
    summary = {}

    for category, entries in grouped.items():
        cat_sum = {}
        for e in entries:
            if e["genotype"] == "N/A": continue
            interp = e["interpretation"]
            if interp and "No interpretation" not in interp:
                key = e["name"].replace(" ","_").lower()
                cat_sum[key] = {
                    "rsid": e["rsid"], "genotype": e["genotype"],
                    "finding": interp[:140] + ("..." if len(interp)>140 else ""),
                    "priority": e.get("priority","normal"), "source": "curated",
                }
        if cat_sum:
            summary[category] = cat_sum

    for trait_name, result in gwas_results.items():
        elevated = [h for h in result["results"]
                    if h["on_chip"] and h["risk_level"] in
                    ("elevated","moderately elevated","strong signal","slightly elevated")][:5]
        if not elevated: continue
        cat_sum = {}
        for h in elevated:
            key = f"{h['gene'] or h['rsid']}_{h['rsid']}"
            cat_sum[key] = {
                "rsid": h["rsid"], "genotype": h["your_genotype"],
                "finding": h["finding"][:140] + ("..." if len(h["finding"])>140 else ""),
                "priority": "high" if h["risk_level"]=="elevated" else "medium",
                "source": "gwas", "pgs": result["pgs_score"],
            }
        if cat_sum:
            summary[f"GWAS - {trait_name}"] = cat_sum

    # SNPedia top pigmentation findings into summary
    if snpedia_enriched:
        pig = snpedia_enriched.get("pigmentation",[])
        pig_sum = {}
        for p in pig:
            if p["your_geno"] == "Not on chip": continue
            if p["confidence"] in ("very high","high"):
                key = p["trait"].replace(" ","_").lower()
                pig_sum[key] = {
                    "rsid": p["rsid"], "genotype": p["your_geno"],
                    "finding": p["description"][:140],
                    "priority": "high" if p["confidence"]=="very high" else "medium",
                    "source": "snpedia",
                }
        if pig_sum:
            summary["Pigmentation (SNPedia)"] = pig_sum

    with open(results_dir / "personal_summary.json","w") as f:
        json.dump(summary, f, indent=2)
    total = sum(len(v) for v in summary.values())
    ok(f"Summary: {total} findings across {len(summary)} categories")
    return summary

# ── STEP 5 — HTML report ──────────────────────────────────────────────────────
PRIORITY_BADGE = {
    "high":   ('<span class="badge high">High</span>', 3),
    "medium": ('<span class="badge medium">Med</span>', 2),
    "normal": ('', 1), "low": ('', 0),
}
RISK_BADGE = {
    "elevated":            '<span class="badge high">Elevated</span>',
    "moderately elevated": '<span class="badge medium">Mod. Elevated</span>',
    "strong signal":       '<span class="badge high">Strong</span>',
    "slightly elevated":   '<span class="badge info">Slight +</span>',
    "moderate signal":     '<span class="badge info">Moderate</span>',
    "mild signal":         '<span class="badge muted">Mild</span>',
    "baseline":            '',
}

def clean(text, n=220):
    t = str(text or "").replace("[[","").replace("]]","")
    return (t[:n]+"...") if len(t)>n else t

def load_all_results(results_dir):
    all_data = defaultdict(list)
    seen     = set()
    for fp in sorted(results_dir.glob("*_results.json")):
        if fp.name.startswith("gwas_"): continue
        try:    data = json.load(open(fp))
        except: continue
        if "results" in data:
            for item in data["results"]:
                rsid = item.get("rsid","")
                cat  = item.get("category") or data.get("category") or \
                       fp.stem.replace("_results","").replace("_"," ").title()
                uid  = f"{rsid}_{cat}"
                if uid not in seen:
                    seen.add(uid)
                    all_data[cat].append(item)
    return all_data

def render_gwas_html(gwas_results, synthesis=None):
    if not gwas_results: return ""

    # Traits where raw OR language is misleading — show synthesis card instead
    PIGMENTATION_TRAITS = {"eye color", "eye_color", "hair color", "hair_color",
                           "skin color", "skin_color", "hair color pigmentation",
                           "hair_color_pigmentation"}

    # Strict trait mapping — T1D and T2D must NOT cross-match
    SYNTHESIS_TRAIT_MAP = {
        "eye_color":   ["eye color", "eye_color"],
        "hair_color":  ["hair color", "hair_color", "hair color pigmentation"],
        "skin_tone":   ["skin color", "skin_color"],
        "cholesterol": ["cholesterol", "ldl cholesterol", "hdl cholesterol"],
        "t2d":         ["diabetes"],  # matches 'Diabetes' trait name exactly
        "alzheimer":   ["alzheimer"],
        "cad":         ["coronary artery disease"],
        "bmi":         ["bmi"],
        "triglycerides":["triglycerides"],
        "depression":  ["depression"],
        "longevity":   ["longevity"],
        # T1D intentionally excluded — no synthesis card for it
    }

    def get_synthesis_banner(trait_name, synthesis):
        if not synthesis:
            return ""
        tn = trait_name.lower().strip()
        # Explicit exclusions
        if "type 1" in tn or "type1" in tn or "t1d" in tn:
            return ""
        for key, names in SYNTHESIS_TRAIT_MAP.items():
            if tn in [n.lower() for n in names]:
                r = synthesis.get(key)
                if r:
                    pred  = r.get("prediction","")
                    snps  = r.get("snps_used", 0)
                    total = r.get("total_snps", snps)
                    narr  = r.get("narrative","")[:300]
                    agree = r.get("agreement","")
                    badge = (f'<span class="badge info">{snps} of {total} markers agree</span>'
                             if agree else "")
                    return (f'<div class="synth-banner">'
                            f'<strong>Combined prediction: {pred}</strong> {badge}'
                            f'<p class="synth-banner-narr">{narr}</p>'
                            f'</div>')
        return ""

    risk_order = {"elevated":0,"moderately elevated":1,"strong signal":2,
                  "slightly elevated":3,"moderate signal":4,"mild signal":5,"baseline":6}
    sections = '<h2 class="section-divider">GWAS Catalog Cross-Reference</h2>'
    sections += '<p class="gwas-intro">Cross-referenced against NHGRI-EBI GWAS Catalog (p&lt;1e-5). For each trait, your genotype at each locus is matched and a polygenic score computed. Duplicate studies per rsID are collapsed — only the most significant association shown.</p>'

    for trait_name, result in sorted(gwas_results.items()):
        pgs     = result["pgs_score"]
        pgs_cls = "pgs-high" if pgs > 0.3 else ("pgs-low" if pgs < -0.3 else "pgs-mid")
        pgs_dir = "above average" if pgs > 0.1 else ("below average" if pgs < -0.1 else "average")
        anchor  = trait_name.lower().replace(" ","_")
        ctx     = result.get("context","")
        banner  = get_synthesis_banner(trait_name, synthesis)
        is_pig  = trait_name.lower().replace(" ","_") in PIGMENTATION_TRAITS

        if is_pig and banner:
            sections += f"""<section class="category-section gwas-section" id="{anchor}">
          <div class="gwas-header">
            <h2 class="cat-title">{trait_name}</h2>
            <div class="gwas-meta">
              <span class="stat-chip">{result['on_chip']} on chip</span>
              <span class="stat-chip pgs-chip {pgs_cls}">PGS {pgs:+.3f} ({pgs_dir})</span>
            </div>
          </div>
          {banner}
          <p class="trait-context">Raw association table suppressed for pigmentation traits —
          OR language is directional (not disease risk). See the Combined Predictions section
          above for a plain-English interpretation of your genotypes.</p>
        </section>"""
            continue

        # Deduplicate: keep best (lowest p-value) hit per rsid
        seen_rsids: dict[str, dict] = {}
        hits_sorted = sorted(result["results"],
                             key=lambda h:(0 if h["on_chip"] else 1,
                                           risk_order.get(h["risk_level"],9),
                                           h["pvalue"]))
        for h in hits_sorted:
            if not h["on_chip"]: continue
            rsid = h["rsid"]
            if rsid not in seen_rsids:
                seen_rsids[rsid] = h
            else:
                # Keep whichever has lower p-value
                if h["pvalue"] < seen_rsids[rsid]["pvalue"]:
                    seen_rsids[rsid] = h

        rows = ""
        for h in seen_rsids.values():
            badge  = RISK_BADGE.get(h["risk_level"],"")
            pmid   = h.get("pubmedid","")
            pmid_l = (f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pmid}/" target="_blank" '
                      f'class="rsid-link">{pmid}</a>' if pmid else "--")
            ef_str = f"{h['effect']:.3g}" if h.get("effect") is not None else "--"
            sug    = " *" if h.get("suggestive") else ""
            rc     = "not-found" if h["risk_level"]=="baseline" else "found"
            rows += f"""<tr class="{rc}">
              <td><a href="https://www.snpedia.com/index.php/{h['rsid']}" target="_blank"
                     class="rsid-link">{h['rsid']}</a></td>
              <td>{h['gene'] or '--'}</td>
              <td><code>{h['your_genotype']}</code>
                  <span class="ra-label">risk:{h.get('risk_allele','?')}</span></td>
              <td>{badge} {clean(h['finding'],180)}</td>
              <td class="num">{ef_str}</td>
              <td class="num">{h['pvalue']:.2e}{sug}</td>
              <td>{pmid_l}</td>
            </tr>"""

        sections += f"""<section class="category-section gwas-section" id="{anchor}">
          <div class="gwas-header">
            <h2 class="cat-title">{trait_name}</h2>
            <div class="gwas-meta">
              <span class="stat-chip">{len(seen_rsids)} unique SNPs</span>
              <span class="stat-chip">{result['elevated_hits']} elevated</span>
              <span class="stat-chip pgs-chip {pgs_cls}">PGS {pgs:+.3f} ({pgs_dir})</span>
            </div>
          </div>
          {banner}
          {"<p class='trait-context'>" + ctx + "</p>" if ctx else ""}
          <table class="detail-table">
            <thead><tr>
              <th>rsID</th><th>Gene</th><th>Genotype</th><th>Finding</th>
              <th>OR/&beta;</th><th>p-val</th><th>PMID</th>
            </tr></thead>
            <tbody>{rows or "<tr><td colspan='7' class='empty'>No on-chip variants found.</td></tr>"}</tbody>
          </table>
        </section>"""
    return sections

def render_html(person, summary, report_data, gwas_results, snpedia_enriched, synthesis, results_dir):
    categories   = sorted(report_data.keys())
    today        = date.today().strftime("%B %d, %Y")
    total_snps   = sum(len(v) for v in report_data.values())
    found_snps   = sum(1 for v in report_data.values() for e in v if e.get("found"))
    high_pri     = sum(1 for v in report_data.values() for e in v if e.get("priority")=="high")
    gwas_traits  = len(gwas_results)
    gwas_elev    = sum(r["elevated_hits"] for r in gwas_results.values())
    snpedia_hits = snpedia_enriched.get("enriched_snps",0) if snpedia_enriched else 0

    # Dashboard
    dashboard_rows = ""
    for cat, traits in summary.items():
        is_gwas = cat.startswith("GWAS")
        is_pig  = "Pigmentation" in cat
        hcls    = "cat-header gwas-hdr" if is_gwas else ("cat-header pig-hdr" if is_pig else "cat-header")
        dashboard_rows += f'<tr class="{hcls}"><td colspan="3">{cat.upper()}</td></tr>'
        for tkey, info in traits.items():
            badge, _ = PRIORITY_BADGE.get(info.get("priority","normal"),("",1))
            src = info.get("source","")
            src_tag = (f'<span class="src-tag gwas-tag">GWAS</span>' if src=="gwas" else
                       f'<span class="src-tag pig-tag">PIG</span>' if src=="snpedia" else "")
            pgs_note = (f' <span class="pgs-note">PGS {info["pgs"]:+.3f}</span>'
                        if "pgs" in info else "")
            dashboard_rows += f"""<tr>
          <td class="trait-name">{src_tag}{tkey.replace("_"," ").capitalize()}</td>
          <td class="geno-cell"><code>{info['genotype']}</code></td>
          <td class="finding-cell">{badge} {clean(info['finding'],160)}{pgs_note}</td>
        </tr>"""

    # Curated trait sections
    detail_sections = ""
    for cat in categories:
        entries = sorted(report_data[cat],
                         key=lambda e:(-PRIORITY_BADGE.get(e.get("priority","normal"),("",1))[1],
                                       -e.get("pmid_count",0)))
        rows = ""
        for e in entries:
            rsid  = e.get("rsid","--")
            geno  = e.get("genotype","N/A")
            interp = clean(e.get("interpretation") or "No interpretation available.")
            badge, _ = PRIORITY_BADGE.get(e.get("priority","normal"),("",1))
            fc = "found" if e.get("found") else "not-found"
            rows += f"""<tr class="{fc}">
            <td><a href="https://www.snpedia.com/index.php/{rsid}" target="_blank" class="rsid-link">{rsid}</a></td>
            <td>{e.get('name',rsid)}</td><td><code>{geno}</code></td>
            <td>{badge}{interp}</td>
          </tr>"""
        anchor = cat.lower().replace(" ","_")
        detail_sections += f"""<section class="category-section" id="{anchor}">
        <h2 class="cat-title">{cat}</h2>
        <table class="detail-table">
          <thead><tr><th>rsID</th><th>Trait</th><th>Genotype</th><th>Finding</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </section>"""

    # SNPedia section
    snpedia_html = ""
    if snpedia_enriched:
        try:
            import importlib.util
            ep = BASE_DIR / "snpedia_enricher.py"
            spec = importlib.util.spec_from_file_location("snpedia_enricher", ep)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            snpedia_html = mod.render_snpedia_html(snpedia_enriched)
        except Exception as e:
            snpedia_html = f'<p class="gwas-intro">SNPedia section failed to render: {e}</p>'

    gwas_html = render_gwas_html(gwas_results, synthesis)

    # Synthesis HTML
    synthesis_html = ""
    if synthesis:
        try:
            import importlib.util
            sp   = BASE_DIR / "trait_synthesizer.py"
            spec = importlib.util.spec_from_file_location("trait_synthesizer", sp)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            synthesis_html = mod.render_synthesis_html(synthesis)
        except Exception as e:
            synthesis_html = f'<p class="gwas-intro">Synthesis render failed: {e}</p>'

    # Nav pills
    nav_curated = "".join(f'<a class="nav-pill" href="#{cat.lower().replace(" ","_")}">{cat}</a>'
                          for cat in categories)
    nav_gwas    = "".join(f'<a class="nav-pill gwas-pill" href="#{t.lower().replace(" ","_")}">{t}</a>'
                          for t in sorted(gwas_results.keys()))
    nav_snpedia = ('<a class="nav-pill pig-pill" href="#pigmentation_snpedia">Pigmentation</a>'
                   '<a class="nav-pill pig-pill" href="#snpedia_top">SNPedia Top</a>'
                   if snpedia_enriched else "")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{person} -- DNA Report</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0d0f14;--surface:#161a22;--border:#262c38;
  --accent:#4fc3f7;--accent2:#b39ddb;--accent3:#80cbc4;--accent4:#f48fb1;
  --high:#ef5350;--medium:#ffa726;--info:#42a5f5;
  --text:#dde3ee;--muted:#7a8499;--code-bg:#1e2534;
  font-family:"SF Mono","Fira Code","Cascadia Code",monospace;
}}
body{{background:var(--bg);color:var(--text);font-size:14px;line-height:1.6}}
header{{background:linear-gradient(135deg,#0d1520,#0d1a2e);border-bottom:1px solid var(--border);padding:2.5rem 3rem 2rem}}
.header-top{{display:flex;align-items:baseline;gap:1rem}}
h1{{font-size:2rem;font-weight:700;letter-spacing:-.03em;color:var(--accent)}}
.subtitle{{font-size:.85rem;color:var(--muted);font-family:system-ui,sans-serif}}
.meta{{margin-top:.4rem;font-size:.78rem;color:var(--muted);font-family:system-ui,sans-serif}}
.stats-bar{{display:flex;flex-wrap:wrap;gap:2rem;padding:1.2rem 3rem;background:var(--surface);border-bottom:1px solid var(--border)}}
.stat{{display:flex;flex-direction:column}}
.stat-val{{font-size:1.5rem;font-weight:700;color:var(--accent)}}
.stat-val.gwas{{color:var(--accent3)}}.stat-val.pig{{color:var(--accent4)}}
.stat-label{{font-size:.72rem;color:var(--muted);font-family:system-ui,sans-serif;text-transform:uppercase;letter-spacing:.05em}}
.nav-bar{{display:flex;flex-wrap:wrap;gap:.4rem;padding:.8rem 3rem;background:var(--surface);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}}
.nav-pill{{background:var(--code-bg);color:var(--accent2);border:1px solid var(--border);padding:.2rem .65rem;border-radius:999px;text-decoration:none;font-size:.72rem;transition:background .15s,color .15s}}
.nav-pill:hover{{background:var(--accent2);color:var(--bg)}}
.nav-pill.gwas-pill{{color:var(--accent3);border-color:var(--accent3)}}.nav-pill.gwas-pill:hover{{background:var(--accent3);color:var(--bg)}}
.nav-pill.pig-pill{{color:var(--accent4);border-color:var(--accent4)}}.nav-pill.pig-pill:hover{{background:var(--accent4);color:var(--bg)}}
main{{padding:2rem 3rem 4rem;max-width:1500px;margin:0 auto}}
.dashboard-wrap{{margin-bottom:3rem}}
.section-title{{font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-family:system-ui,sans-serif;margin-bottom:.65rem}}
.dashboard-table{{width:100%;border-collapse:collapse;font-size:.82rem}}
.dashboard-table td{{padding:.4rem .7rem;border-bottom:1px solid var(--border);vertical-align:top}}
.cat-header td{{background:var(--code-bg);color:var(--accent);font-weight:600;letter-spacing:.08em;font-size:.68rem;text-transform:uppercase;padding:.45rem .7rem}}
.cat-header.gwas-hdr td{{color:var(--accent3)}}.cat-header.pig-hdr td{{color:var(--accent4)}}
.trait-name{{color:var(--text);font-family:system-ui,sans-serif;width:22%}}
.geno-cell{{width:10%;text-align:center}}.finding-cell{{font-family:system-ui,sans-serif;color:var(--muted)}}
.category-section{{margin-bottom:2.5rem}}
.section-divider{{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent3);border-top:1px solid var(--border);padding-top:2rem;margin:2.5rem 0 1.5rem}}
.gwas-intro{{font-family:system-ui,sans-serif;color:var(--muted);font-size:.82rem;margin-bottom:2rem;max-width:780px}}
.cat-title{{font-size:1rem;font-weight:600;color:var(--accent2);border-bottom:1px solid var(--border);padding-bottom:.35rem;margin-bottom:.65rem}}
.cat-title.pig-title{{color:var(--accent4)}}
.gwas-section .cat-title{{color:var(--accent3)}}
.gwas-header{{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:.5rem}}
.gwas-meta{{display:flex;gap:.5rem;flex-wrap:wrap}}
.stat-chip{{font-size:.7rem;padding:.15rem .55rem;border-radius:999px;background:var(--code-bg);border:1px solid var(--border);color:var(--muted);font-family:system-ui,sans-serif}}
.pgs-chip{{font-weight:700}}.pgs-high{{color:var(--high);border-color:var(--high)}}.pgs-low{{color:var(--info);border-color:var(--info)}}.pgs-mid{{color:var(--accent2)}}
.trait-context{{font-family:system-ui,sans-serif;font-size:.8rem;color:var(--muted);background:var(--code-bg);border-left:3px solid var(--accent3);padding:.6rem 1rem;margin-bottom:.8rem;border-radius:0 4px 4px 0;max-width:800px}}
.detail-table{{width:100%;border-collapse:collapse;font-size:.78rem}}
.detail-table th{{background:var(--code-bg);color:var(--muted);text-align:left;padding:.35rem .55rem;font-weight:600;letter-spacing:.06em;font-size:.68rem;text-transform:uppercase;border-bottom:1px solid var(--border)}}
.detail-table td{{padding:.38rem .55rem;border-bottom:1px solid var(--border);vertical-align:top;font-family:system-ui,sans-serif}}
.detail-table tr.found:hover td{{background:rgba(79,195,247,.04)}}
.detail-table tr.not-found td{{opacity:.42}}
.detail-table .num{{text-align:right;font-family:monospace;font-size:.75rem}}
.empty{{text-align:center;color:var(--muted);padding:1rem;font-style:italic}}
.ra-label{{font-size:.68rem;color:var(--muted);margin-left:.2rem}}
.pgs-note{{font-size:.72rem;color:var(--accent3);margin-left:.4rem}}
.ctx-text{{font-size:.75rem;color:var(--muted);display:block;margin-top:.2rem}}
.badge{{display:inline-block;font-size:.62rem;font-weight:700;padding:.08rem .4rem;border-radius:999px;margin-right:.25rem;vertical-align:middle;font-family:system-ui,sans-serif;letter-spacing:.04em;text-transform:uppercase}}
.badge.high{{background:var(--high);color:#fff}}.badge.medium{{background:var(--medium);color:#111}}
.badge.info{{background:var(--info);color:#fff}}.badge.muted{{background:#3a4255;color:#aab0c0;border:none}}
.src-tag{{font-size:.6rem;font-weight:700;padding:.05rem .35rem;border-radius:3px;margin-right:.3rem;vertical-align:middle;font-family:system-ui,sans-serif;text-transform:uppercase}}
.gwas-tag{{background:rgba(128,203,196,.15);color:var(--accent3);border:1px solid var(--accent3)}}
.pig-tag{{background:rgba(244,143,177,.15);color:var(--accent4);border:1px solid var(--accent4)}}
.synth-banner{{background:rgba(79,195,247,.07);border-left:3px solid var(--accent);border-radius:0 6px 6px 0;padding:.8rem 1.2rem;margin-bottom:.8rem}}
.synth-banner strong{{color:var(--accent);font-size:.9rem}}
.synth-banner-narr{{font-family:system-ui,sans-serif;font-size:.8rem;color:var(--muted);margin-top:.3rem;line-height:1.5}}
code{{background:var(--code-bg);padding:.08rem .3rem;border-radius:3px;font-size:.83em}}
.rsid-link{{color:var(--accent);text-decoration:none}}.rsid-link:hover{{text-decoration:underline}}
.synth-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:1.2rem;margin-bottom:2.5rem}}
.synth-card{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1.2rem 1.4rem}}
.synth-header{{display:flex;align-items:center;gap:.7rem;flex-wrap:wrap;margin-bottom:.7rem}}
.synth-icon{{font-size:1.3rem}}
.synth-label{{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-family:system-ui,sans-serif}}
.synth-pred{{font-size:.95rem;font-weight:700;color:var(--accent);margin-left:auto}}
.synth-conf{{font-size:.7rem;color:var(--muted);font-family:system-ui,sans-serif;white-space:nowrap}}
.synth-narrative{{font-family:system-ui,sans-serif;font-size:.84rem;color:var(--text);line-height:1.65;margin-bottom:.6rem}}
.synth-details{{margin-top:.5rem}}
.synth-details summary{{font-size:.71rem;color:var(--muted);cursor:pointer;font-family:system-ui,sans-serif;letter-spacing:.04em}}
.support-list{{list-style:none;margin-top:.4rem}}
.support-item{{font-size:.71rem;font-family:system-ui,sans-serif;color:var(--muted);padding:.15rem 0;border-bottom:1px solid var(--border)}}
.support-item::before{{content:"→ ";color:var(--accent3)}}
@media(max-width:768px){{header,main,.stats-bar,.nav-bar{{padding-left:1rem;padding-right:1rem}}}}
</style>
</head>
<body>
<header>
  <div class="header-top"><h1>&#x2B21; {person}</h1><span class="subtitle">DNA Health Report</span></div>
  <p class="meta">Generated {today} &nbsp;&middot;&nbsp; MyHeritage &nbsp;&middot;&nbsp; SNPedia 2025 &nbsp;&middot;&nbsp; NHGRI-EBI GWAS Catalog &nbsp;&middot;&nbsp; Offline</p>
</header>
<div class="stats-bar">
  <div class="stat"><span class="stat-val">{total_snps}</span><span class="stat-label">Curated SNPs</span></div>
  <div class="stat"><span class="stat-val">{found_snps}</span><span class="stat-label">Genotyped</span></div>
  <div class="stat"><span class="stat-val">{len(categories)}</span><span class="stat-label">Categories</span></div>
  <div class="stat"><span class="stat-val gwas">{gwas_traits}</span><span class="stat-label">GWAS Traits</span></div>
  <div class="stat"><span class="stat-val gwas">{gwas_elev}</span><span class="stat-label">Elevated GWAS</span></div>
  <div class="stat"><span class="stat-val pig">{snpedia_hits}</span><span class="stat-label">SNPedia Hits</span></div>
</div>
<nav class="nav-bar">
  <a class="nav-pill" href="#synthesis_top">▶ Predictions</a>
  <a class="nav-pill" href="#dashboard">Dashboard</a>
  {nav_curated}
  {"<span style='color:var(--border);margin:0 .3rem'>|</span>" + nav_gwas if nav_gwas else ""}
  {"<span style='color:var(--border);margin:0 .3rem'>|</span>" + nav_snpedia if nav_snpedia else ""}
</nav>
<main>
  {synthesis_html}
  <div class="dashboard-wrap" id="dashboard">
    <p class="section-title">Executive Dashboard -- Key Findings</p>
    <table class="dashboard-table">
      <tbody>{dashboard_rows or "<tr><td colspan='3' class='empty'>No curated findings yet</td></tr>"}</tbody>
    </table>
  </div>
  {detail_sections}
  {gwas_html}
  {snpedia_html}
</main>
</body>
</html>"""

    out    = results_dir / f"health_report_{person}_{date.today().strftime('%Y%m%d')}.html"
    latest = results_dir / f"health_report_{person}.html"
    for p in (out, latest):
        with open(p,"w",encoding="utf-8") as f:
            f.write(html)
    ok(f"Report: {out.name}")
    ok(f"Latest: {latest.name}")
    return out

# ── STEP 3d — Multi-SNP trait synthesis ──────────────────────────────────────
def run_synthesizer(person_cfg, gwas_results):
    try:
        import importlib.util
        synth_path = BASE_DIR / "trait_synthesizer.py"
        if not synth_path.exists():
            warn("trait_synthesizer.py not found -- skipping synthesis")
            return {}
        spec   = importlib.util.spec_from_file_location("trait_synthesizer", synth_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data_file   = ROOT_DIR / person_cfg["data_file"]
        results_dir = ROOT_DIR / person_cfg["results_dir"]
        dna         = module.load_dna(data_file)
        synthesis   = module.synthesize_all(dna, gwas_results)
        with open(results_dir / "synthesis.json", "w") as f:
            json.dump(synthesis, f, indent=2)
        ok("Synthesis: " + " | ".join(
            f"{v['trait']}: {v['prediction']} "
            f"({v['snps_used']} of {v.get('total_snps', v['snps_used'])} markers)"
            for v in synthesis.values()))
        return synthesis
    except Exception as e:
        warn(f"Synthesizer failed: {e}")
        traceback.print_exc()
        return {}

# ── Run one person ────────────────────────────────────────────────────────────
def run_person(person_cfg, shared_cfg, args):
    name        = person_cfg["name"]
    data_file   = ROOT_DIR / person_cfg["data_file"]
    results_dir = ROOT_DIR / person_cfg["results_dir"]

    print(f"\n{'='*52}\n  DNA Virtual Lab -- {name}\n{'='*52}")
    errors = []

    # ── Report-only mode: reload cached JSON, skip all scans ─────────────────
    if getattr(args, 'report_only', False):
        step("R", "Report-only mode — loading cached results")
        gwas_results = {}
        for f in sorted(results_dir.glob("gwas_*.json")):
            try:
                d = json.load(open(f))
                gwas_results[d["trait"]] = d
            except: pass
        ok(f"Loaded {len(gwas_results)} cached GWAS results")

        snpedia_enriched = {}
        enr = results_dir / "snpedia_enriched.json"
        if enr.exists():
            snpedia_enriched = json.load(open(enr))
            ok(f"Loaded cached SNPedia enrichment")

        grouped = {}
        for f in sorted(results_dir.glob("*_results.json")):
            if f.name.startswith("gwas_"): continue
            try:
                d = json.load(open(f))
                cat = d.get("category", f.stem)
                grouped[cat] = d.get("results", [])
            except: pass

        step("3d", "Multi-SNP trait synthesis")
        synthesis = run_synthesizer(person_cfg, gwas_results)

        step(4, "Build personal summary")
        try:
            summary = build_summary(grouped, gwas_results, snpedia_enriched, results_dir)
        except Exception as e:
            fail(f"Summary: {e}"); summary = {}

        step(5, "Render HTML report")
        try:
            report_data = load_all_results(results_dir)
            render_html(name, summary, report_data, gwas_results,
                       snpedia_enriched, synthesis, results_dir)
        except Exception as e:
            fail(f"Report: {e}"); traceback.print_exc()

        print(f"\n{'='*52}\n  OK    Report-only complete -- {results_dir}\n{'='*52}")
        return

    step(1, "Load & index DNA data")
    try:
        dna_index = load_dna_index(data_file)
    except SystemExit:
        return

    step(2, "Scan traits library")
    try:
        grouped = scan_traits(dna_index, shared_cfg, results_dir)
    except Exception as e:
        fail(f"Trait scan: {e}"); traceback.print_exc()
        grouped = {}; errors.append("trait_scan")

    gwas_results = {}
    if not args.skip_gwas:
        step("3a", "GWAS Catalog cross-reference")
        try:
            gwas_results = run_gwas_scanner(dna_index, shared_cfg, results_dir)
        except Exception as e:
            fail(f"GWAS: {e}"); traceback.print_exc(); errors.append("gwas")

    snpedia_enriched = {}
    if not args.skip_snpedia:
        step("3b", "SNPedia deep annotation")
        snpedia_enriched = run_snpedia_enricher(person_cfg, shared_cfg)
        if not snpedia_enriched:
            errors.append("snpedia")

    if not args.skip_specialist:
        step("3c", "Specialist scripts")
        run_specialist_scripts()

    step("3d", "Multi-SNP trait synthesis")
    synthesis = run_synthesizer(person_cfg, gwas_results)

    step(4, "Build personal summary")
    try:
        summary = build_summary(grouped, gwas_results, snpedia_enriched, results_dir)
    except Exception as e:
        fail(f"Summary: {e}"); traceback.print_exc()
        summary = {}; errors.append("summary")

    if not args.skip_report:
        step(5, "Render HTML report")
        try:
            report_data = load_all_results(results_dir)
            render_html(name, summary, report_data, gwas_results, snpedia_enriched, synthesis, results_dir)
        except Exception as e:
            fail(f"Report: {e}"); traceback.print_exc(); errors.append("report")

    print(f"\n{'='*52}")
    if errors:
        print(f"  WARN  Issues: {', '.join(errors)}")
    else:
        print(f"  OK    Pipeline complete -- {results_dir}")
    print(f"{'='*52}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="DNA Virtual Lab -- unified pipeline")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--person",   default=None, help="Person name (from people.json)")
    grp.add_argument("--all",      action="store_true", help="Run for all people")
    parser.add_argument("--skip-report",     action="store_true")
    parser.add_argument("--skip-gwas",       action="store_true")
    parser.add_argument("--skip-snpedia",    action="store_true")
    parser.add_argument("--skip-specialist", action="store_true")
    parser.add_argument("--report-only",     action="store_true",
                        help="Skip all scans, reuse cached JSON, just re-render HTML")
    args = parser.parse_args()

    cfg    = load_config()
    shared = cfg["shared"]
    people = cfg["people"]

    if args.all:
        targets = people
    elif args.person:
        targets = [p for p in people if p["name"].lower() == args.person.lower()]
        if not targets:
            print(f"ERROR: '{args.person}' not in people.json. Available: {[p['name'] for p in people]}")
            sys.exit(1)
    else:
        # Default: first person (legacy single-person mode)
        targets = [people[0]]

    for person_cfg in targets:
        run_person(person_cfg, shared, args)

if __name__ == "__main__":
    main()