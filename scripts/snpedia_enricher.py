#!/usr/bin/env python3
"""
snpedia_enricher.py
====================
Cross-references a person's raw DNA against the SNPedia 2025 DB.

Since the DB contains only main SNP pages (no genotype sub-pages),
we extract allele-specific findings from the free-text narrative using
pattern matching on genotype references like:
  rs4680(A;A), (G;G) genotype, A allele carriers, homozygous G, etc.

Outputs per person (in their results_dir):
  snpedia_enriched.json   -- all enriched SNPs by category
  pigmentation.json       -- physical appearance predictions
  top_findings.json       -- highest-signal hits sorted by magnitude proxy

Usage:
  python3 scripts/snpedia_enricher.py --person Minko
  python3 scripts/snpedia_enricher.py --all
"""

import csv, json, re, sqlite3, argparse, sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
CONFIG   = ROOT_DIR / "people.json"

CATEGORY_KEYWORDS = {
    "Pigmentation":      ["eye color","hair color","skin color","melanin","pigment",
                          "MC1R","OCA2","HERC2","SLC45A2","SLC24A5","TYR ","TYRP1",
                          "freckl","albinism","redhead"],
    "Pharmacogenomics":  ["CYP2C19","CYP2D6","CYP3A4","CYP2C9","TPMT","DPYD",
                          "UGT1A1","drug metabolism","warfarin","clopidogrel",
                          "codeine","statin","tamoxifen","antidepressant"],
    "Cardiovascular":    ["heart disease","cardiovascular","blood pressure","cholesterol",
                          "LDL","HDL","myocardial","stroke","thrombosis","atrial",
                          "APOE","PCSK9","coronary"],
    "Neurotransmitter":  ["dopamine","serotonin","COMT","MAO","DRD","HTR","BDNF",
                          "norepinephrine","prefrontal","worrier","warrior"],
    "Neurology":         ["Alzheimer","Parkinson","multiple sclerosis","epilepsy",
                          "migraine","APOE","LRRK2","dementia","cognitive decline"],
    "Cancer":            ["cancer","tumor","melanoma","breast cancer","prostate",
                          "colorectal","BRCA","TP53","Lynch","carcinoma","malignant"],
    "Metabolism":        ["diabetes","insulin","glucose","obesity","BMI","adipose",
                          "TCF7L2","FTO","PPARG","metabolic","blood sugar"],
    "Immune":            ["autoimmune","inflammation","IL-6","TNF","HLA","lupus",
                          "rheumatoid","Crohn","celiac","allerg"],
    "Nutrition":         ["lactose","caffeine","alcohol","vitamin","folate","omega",
                          "gluten","MTHFR","iron","B12"],
    "Physical Traits":   ["height","muscle","athlete","VO2","endurance","ACTN3",
                          "sprinter","ACE","power","strength"],
    "Longevity":         ["longevity","lifespan","aging","telomere","FOXO","SIRT",
                          "centenarian"],
    "Ancestry":          ["haplogroup","ancestry","population","migration","ethnic"],
}

PIGMENTATION_SNPS = {
    "rs12913832": {
        "gene": "HERC2/OCA2", "trait": "Eye Color",
        "GG": ("Blue eyes -- strongest genetic predictor of blue eye color in Europeans", "very high"),
        "AG": ("Blue or green eyes (likely); heterozygous at the key HERC2 eye color locus", "high"),
        "AA": ("Brown eyes -- non-blue allele at the primary eye color determinant", "very high"),
    },
    "rs1129038": {
        "gene": "HERC2", "trait": "Eye Color",
        "AA": ("Blue-eye haplotype -- part of the 13-SNP block found in 97% of blue-eyed Europeans", "high"),
        "AG": ("Mixed signal at HERC2 blue-eye haplotype locus", "medium"),
        "GG": ("Non-blue eye color signal at HERC2", "medium"),
    },
    "rs12203592": {
        "gene": "IRF4", "trait": "Eye / Skin / Hair Color",
        "CC": ("Darker eye, skin, and hair pigmentation -- common in non-European populations", "medium"),
        "CT": ("Intermediate pigmentation at IRF4 locus", "low"),
        "TT": ("Lighter eye, skin, and hair -- IRF4 variant associated with reduced pigmentation", "medium"),
    },
    "rs4778241": {
        "gene": "OCA2", "trait": "Eye Color",
        "CC": ("Brown eye color signal at OCA2", "medium"),
        "AC": ("Mixed OCA2 signal -- intermediate or green eye color possible", "low"),
        "AA": ("Blue/green eye color signal at OCA2", "medium"),
    },
    "rs1805007": {
        "gene": "MC1R", "trait": "Hair Color -- Red (Arg151Cys)",
        "CC": ("No Arg151Cys MC1R variant -- no red hair contribution from this locus", "high"),
        "CT": ("One copy of Arg151Cys -- possible reddish tints or auburn; increased sun sensitivity; higher melanoma risk", "high"),
        "TT": ("Homozygous Arg151Cys -- strong red hair phenotype; significantly increased melanoma risk; altered anesthetic response", "very high"),
    },
    "rs1805008": {
        "gene": "MC1R", "trait": "Hair Color -- Red (Arg160Trp)",
        "CC": ("No Arg160Trp MC1R variant", "high"),
        "CT": ("One copy of Arg160Trp MC1R red hair variant -- fair skin, sun sensitivity", "high"),
        "TT": ("Homozygous Arg160Trp -- red hair, very fair skin, high UV sensitivity", "very high"),
    },
    "rs11547464": {
        "gene": "MC1R", "trait": "Hair Color -- Red (Arg163Gln)",
        "GG": ("No Arg163Gln MC1R variant", "high"),
        "AG": ("One copy of Arg163Gln -- minor red hair / fair skin contribution", "medium"),
        "AA": ("Homozygous Arg163Gln -- red hair, pale skin association", "high"),
    },
    "rs12896399": {
        "gene": "SLC45A2", "trait": "Hair Color -- Light/Dark",
        "GG": ("Associated with darker hair pigmentation", "medium"),
        "GT": ("Intermediate hair pigmentation at SLC45A2", "low"),
        "TT": ("Associated with lighter / blonde hair", "medium"),
    },
    "rs16891982": {
        "gene": "SLC45A2", "trait": "Skin / Hair Color",
        "CC": ("Lighter skin and hair -- European depigmentation variant in SLC45A2", "high"),
        "CG": ("Intermediate pigmentation", "medium"),
        "GG": ("Darker skin / hair -- ancestral allele at SLC45A2", "high"),
    },
    "rs1800414": {
        "gene": "OCA2", "trait": "Skin Color",
        "AA": ("East Asian skin lightening variant -- lighter skin in Asian populations", "high"),
        "AG": ("Intermediate", "low"),
        "GG": ("Ancestral allele -- darker skin baseline at OCA2", "medium"),
    },
    "rs1042602": {
        "gene": "TYR", "trait": "Freckling / Sun Sensitivity",
        "AA": ("Increased freckling tendency and sun sensitivity", "medium"),
        "AC": ("Moderate freckling tendency", "low"),
        "CC": ("Lower freckling tendency at TYR locus", "low"),
    },
    "rs1393350": {
        "gene": "TYR", "trait": "Tanning Ability",
        "AA": ("Reduced tanning ability -- higher UV sensitivity", "medium"),
        "AG": ("Intermediate tanning response", "low"),
        "GG": ("Better tanning ability at TYR locus", "low"),
    },
    "rs1426654": {
        "gene": "SLC24A5", "trait": "Skin Color (SLC24A5)",
        "AA": ("Lighter skin -- derived European/South Asian allele at SLC24A5, the largest-effect skin color locus known", "very high"),
        "AG": ("One ancestral + one derived allele at SLC24A5", "high"),
        "GG": ("Ancestral allele -- associated with darker skin (African/East Asian baseline)", "very high"),
    },
}

def strip_html(html):
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>',  ' ', text,  flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&amp;',  '&', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    # Remove wikitext templates that leak through
    text = re.sub(r'\{\{[^}]{0,500}\}\}', ' ', text)
    text = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', text)
    text = re.sub(r'\[http[^\]]+\]', ' ', text)
    text = re.sub(r"'{2,}", '', text)
    return re.sub(r'\s+', ' ', text).strip()

def norm_geno(g):
    alleles = re.findall(r'[ACGT]', g.upper())
    return "".join(sorted(alleles[:2]))

def parse_rsnum(text):
    m = re.search(r'\{\{Rsnum\s*(.*?)\}\}', text, re.DOTALL | re.IGNORECASE)
    if not m:
        return {}
    fields = {}
    for pair in re.finditer(r'\|(\w+)\s*=\s*([^|\n}]+)', m.group(1)):
        fields[pair.group(1).strip()] = pair.group(2).strip()
    return fields

def extract_categories(text):
    tl = text.lower()
    cats = [cat for cat, kws in CATEGORY_KEYWORDS.items()
            if any(kw.lower() in tl for kw in kws)]
    return cats  # empty list = skip this SNP, no "General" dumping ground

def extract_allele_sentences(text, rsid, your_geno_norm):
    prose = re.sub(r'\{\{[^}]{0,500}\}\}', ' ', text)
    prose = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', prose)
    prose = re.sub(r'https?://\S+', '', prose)
    prose = re.sub(r'\s+', ' ', prose).strip()

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', prose) if len(s.strip()) > 30]

    if len(your_geno_norm) < 2:
        return ""
    a1, a2 = your_geno_norm[0], your_geno_norm[1]
    is_homo = a1 == a2
    rsid_short = rsid.replace('rs','')

    scored = []
    for s in sentences:
        sl = s.lower()
        score = 0

        if re.search(rf'rs{rsid_short}\s*\({a1}\s*;?\s*{a2}\)', s, re.IGNORECASE): score += 10
        if re.search(rf'\({a1}\s*;?\s*{a2}\)\s*(genotype|allele|carriers?)', s, re.IGNORECASE): score += 8
        if re.search(rf'genotype\s+\({a1}\s*;?\s*{a2}\)', s, re.IGNORECASE): score += 8
        if is_homo:
            if any(w in sl for w in ['homozygous','homozygote','two copies']): score += 5
        else:
            if any(w in sl for w in ['heterozygous','heterozygote','one copy','carrier']): score += 5
        for allele in set([a1, a2]):
            if re.search(rf'\({allele}\)\s*=', s): score += 4
            if re.search(rf'{allele}\s+allele\s+(carriers?|homozygotes?)', s, re.IGNORECASE): score += 4
            if re.search(rf'rs{rsid_short}\s*\({allele}\)', s, re.IGNORECASE): score += 3
        if any(w in sl for w in ['associated','risk','linked','effect','increases','decreases',
                                   'carrier','phenotype','expression']): score += 2
        if any(w in sl for w in ['color','hair','skin','eye','height','dopamine','serotonin',
                                   'enzyme','metabolism','pain','stress']): score += 1
        if any(w in sl for w in ['hapmap','revision','genotyping','platform','chip',
                                   'pubmed','doi','pmid']): score -= 3
        # Penalise residual wikitext that leaked through
        if re.search(r'\{\{|\}\}|\|rsid=|\|Gene=', s): score -= 5
        if score > 0:
            scored.append((score, s))

    scored.sort(key=lambda x: -x[0])
    best = [s for _, s in scored[:3]]
    out  = " ".join(best)
    return (out[:500] + "...") if len(out) > 500 else out
    prose = re.sub(r'\s+', ' ', prose).strip()

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', prose) if len(s.strip()) > 30]

    if len(your_geno_norm) < 2:
        return ""
    a1, a2 = your_geno_norm[0], your_geno_norm[1]
    is_homo = a1 == a2
    rsid_short = rsid.replace('rs','')

    scored = []
    for s in sentences:
        sl = s.lower()
        score = 0

        if re.search(rf'rs{rsid_short}\s*\({a1}\s*;?\s*{a2}\)', s, re.IGNORECASE): score += 10
        if re.search(rf'\({a1}\s*;?\s*{a2}\)\s*(genotype|allele|carriers?)', s, re.IGNORECASE): score += 8
        if re.search(rf'genotype\s+\({a1}\s*;?\s*{a2}\)', s, re.IGNORECASE): score += 8
        if is_homo:
            if any(w in sl for w in ['homozygous','homozygote','two copies']): score += 5
        else:
            if any(w in sl for w in ['heterozygous','heterozygote','one copy','carrier']): score += 5
        for allele in set([a1, a2]):
            if re.search(rf'\({allele}\)\s*=', s): score += 4
            if re.search(rf'{allele}\s+allele\s+(carriers?|homozygotes?)', s, re.IGNORECASE): score += 4
            if re.search(rf'rs{rsid_short}\s*\({allele}\)', s, re.IGNORECASE): score += 3
        if any(w in sl for w in ['associated','risk','linked','effect','increases','decreases',
                                   'carrier','phenotype','expression']): score += 2
        if any(w in sl for w in ['color','hair','skin','eye','height','dopamine','serotonin',
                                   'enzyme','metabolism','pain','stress']): score += 1
        if any(w in sl for w in ['hapmap','revision','genotyping','platform','chip',
                                   'pubmed','doi','pmid']): score -= 3
        if score > 0:
            scored.append((score, s))

    scored.sort(key=lambda x: -x[0])
    best = [s for _, s in scored[:3]]
    out  = " ".join(best)
    return (out[:500] + "...") if len(out) > 500 else out

def magnitude_proxy(text):
    tl = text.lower()
    score = 0.0
    if any(w in tl for w in ['cancer','melanoma','alzheimer','parkinson',
                               'pathogenic','disease-causing']): score += 4
    if any(w in tl for w in ['increased risk','elevated risk','significantly associated',
                               'strong association']): score += 3
    if any(w in tl for w in ['associated with','linked to','risk factor']): score += 1.5
    if any(w in tl for w in ['minor','modest','slight','weak association']): score -= 1
    if any(w in tl for w in ['eye color','hair color','skin color','melanin']): score += 2
    if any(w in tl for w in ['dopamine','serotonin','norepinephrine']): score += 1.5
    if any(w in tl for w in ['drug','medication','dose','toxicity','adverse']): score += 2
    return min(round(score, 1), 10.0)

def enrich_person(person_cfg, shared_cfg, verbose=True):
    name        = person_cfg["name"]
    data_file   = ROOT_DIR / person_cfg["data_file"]
    results_dir = ROOT_DIR / person_cfg["results_dir"]
    db_path     = ROOT_DIR / shared_cfg["snpedia_db"]

    results_dir.mkdir(parents=True, exist_ok=True)

    def log(msg):
        if verbose: print(f"  {msg}")

    if not data_file.exists():
        log(f"WARNING: DNA file not found: {data_file}")
        return {}

    dna = {}
    with open(data_file, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 4 and row[0].startswith("rs"):
                dna[row[0].lower()] = row[3].strip().upper()
    log(f"OK  {name}: {len(dna):,} SNPs loaded")

    if not db_path.exists():
        log(f"WARNING: SNPedia DB not found: {db_path}")
        return {}

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT rsid FROM snps WHERE rsid LIKE 'Rs%'")
    db_map = {r[0].lower(): r[0] for r in cur.fetchall()}
    log(f"  DB: {len(db_map):,} SNP entries")

    overlap = [(lo, db_map[lo]) for lo in dna if lo in db_map]
    log(f"  Overlap: {len(overlap):,} of your SNPs in SNPedia DB")

    by_category = defaultdict(list)
    all_enriched = []

    batch_size = 500
    for i in range(0, len(overlap), batch_size):
        batch = overlap[i:i+batch_size]
        db_rsids = [db_rsid for _, db_rsid in batch]
        placeholders = ",".join("?" * len(db_rsids))
        cur.execute(f"SELECT rsid, content FROM snps WHERE rsid IN ({placeholders})", db_rsids)
        content_map = {row[0]: row[1] for row in cur.fetchall()}

        for rsid_lo, db_rsid in batch:
            raw = content_map.get(db_rsid, "")
            if not raw:
                continue
            your_geno      = dna[rsid_lo]
            your_geno_norm = norm_geno(your_geno)
            text           = strip_html(raw)
            rsnum          = parse_rsnum(text)
            gene           = rsnum.get("Gene", rsnum.get("Gene_s","")).split(",")[0].strip()
            snp_sum        = rsnum.get("Summary","").strip()
            cats           = extract_categories(text)
            mag            = magnitude_proxy(text)

            if mag < 1.5 and rsid_lo not in PIGMENTATION_SNPS:
                continue

            # Skip if no category matched and not a pigmentation SNP
            if not cats and rsid_lo not in PIGMENTATION_SNPS:
                continue

            narrative = extract_allele_sentences(text, rsid_lo, your_geno_norm)
            if not narrative and snp_sum:
                narrative = f"{snp_sum} (your genotype: {your_geno})"

            # Skip if still no useful narrative
            if not narrative:
                continue

            entry = {
                "rsid": rsid_lo, "gene": gene, "your_geno": your_geno,
                "magnitude": mag, "summary": snp_sum,
                "narrative": narrative, "categories": cats,
            }
            all_enriched.append(entry)
            for cat in cats:
                by_category[cat].append(entry)

    log(f"  Enriched: {len(all_enriched)} SNPs with meaningful signal")

    pigmentation = []
    pig_by_trait = defaultdict(list)
    for rsid, pig in PIGMENTATION_SNPS.items():
        your_geno = dna.get(rsid)
        if not your_geno:
            entry = {"rsid": rsid, "gene": pig["gene"], "trait": pig["trait"],
                     "your_geno": "Not on chip", "description": "SNP not genotyped",
                     "confidence": "none", "snpedia_context": ""}
        else:
            gn     = norm_geno(your_geno)
            interp = pig.get(gn) or pig.get(your_geno)
            desc, conf = interp if interp else (
                f"Genotype {your_geno} -- no specific interpretation curated", "low")
            snpedia_ctx = ""
            db_rsid = db_map.get(rsid)
            if db_rsid:
                cur.execute("SELECT content FROM snps WHERE rsid = ?", (db_rsid,))
                row = cur.fetchone()
                if row:
                    snpedia_ctx = extract_allele_sentences(strip_html(row[0]), rsid, gn)
            entry = {"rsid": rsid, "gene": pig["gene"], "trait": pig["trait"],
                     "your_geno": your_geno, "description": desc,
                     "confidence": conf, "snpedia_context": snpedia_ctx}
        pigmentation.append(entry)
        trait_group = pig["trait"].split("--")[0].split("(")[0].strip()
        pig_by_trait[trait_group].append(entry)

    top_hits = sorted(all_enriched, key=lambda e: -e["magnitude"])[:40]

    output = {
        "person": name, "snps_in_db": len(overlap),
        "enriched_snps": len(all_enriched), "top_hits": top_hits,
        "pigmentation": pigmentation, "pig_by_trait": dict(pig_by_trait),
        "by_category": {cat: sorted(entries, key=lambda e: -e["magnitude"])
                        for cat, entries in sorted(by_category.items())},
    }

    with open(results_dir / "snpedia_enriched.json", "w") as f:
        json.dump(output, f, indent=2)
    with open(results_dir / "pigmentation.json", "w") as f:
        json.dump({"person": name, "by_trait": dict(pig_by_trait)}, f, indent=2)
    with open(results_dir / "top_findings.json", "w") as f:
        json.dump({"person": name, "hits": top_hits}, f, indent=2)

    log(f"OK  Written: snpedia_enriched.json, pigmentation.json, top_findings.json")
    con.close()
    return output

CONFIDENCE_BADGE = {
    "very high": '<span class="badge high">Very High</span>',
    "high":      '<span class="badge high">High</span>',
    "medium":    '<span class="badge medium">Medium</span>',
    "low":       '<span class="badge muted">Low</span>',
    "none":      '',
}

def render_snpedia_html(enriched):
    if not enriched:
        return ""
    pig_by_trait = enriched.get("pig_by_trait", {})
    top_hits     = enriched.get("top_hits", [])
    by_category  = enriched.get("by_category", {})
    n_enriched   = enriched.get("enriched_snps", 0)
    n_db         = enriched.get("snps_in_db", 0)

    pig_rows = ""
    for trait_group, entries in pig_by_trait.items():
        pig_rows += f'<tr class="cat-header"><td colspan="4">{trait_group.upper()}</td></tr>'
        for p in entries:
            badge = CONFIDENCE_BADGE.get(p["confidence"], "")
            ctx   = (p.get("snpedia_context","") or "")[:180]
            gc    = "not-found" if p["your_geno"] == "Not on chip" else "found"
            pig_rows += f"""<tr class="{gc}">
          <td><a href="https://www.snpedia.com/index.php/{p['rsid']}" target="_blank" class="rsid-link">{p['rsid']}</a></td>
          <td>{p['gene']}</td><td><code>{p['your_geno']}</code></td>
          <td>{badge} <strong>{p['description']}</strong>{"<br><span class='ctx-text'>" + ctx + "...</span>" if ctx else ""}</td>
        </tr>"""

    top_rows = ""
    for e in top_hits[:25]:
        cats = ", ".join(e["categories"][:2])
        narr = (e["narrative"] or e["summary"] or "")[:200]
        top_rows += f"""<tr class="found">
          <td><a href="https://www.snpedia.com/index.php/{e['rsid']}" target="_blank" class="rsid-link">{e['rsid']}</a></td>
          <td>{e['gene']}</td><td><code>{e['your_geno']}</code></td>
          <td><span class="badge info">{cats}</span></td><td>{narr}</td>
        </tr>"""

    cat_sections = ""
    for cat, entries in sorted(by_category.items()):
        if cat == "Pigmentation":
            continue
        rows = "".join(f"""<tr class="found">
          <td><a href="https://www.snpedia.com/index.php/{e['rsid']}" target="_blank" class="rsid-link">{e['rsid']}</a></td>
          <td>{e['gene']}</td><td><code>{e['your_geno']}</code></td>
          <td>{(e['narrative'] or e['summary'] or '')[:180]}</td>
        </tr>""" for e in entries[:30])
        anchor = "snpedia_" + cat.lower().replace(" ","_")
        cat_sections += f"""<section class="category-section" id="{anchor}">
      <h2 class="cat-title">{cat}</h2>
      <table class="detail-table">
        <thead><tr><th>rsID</th><th>Gene</th><th>Genotype</th><th>Finding</th></tr></thead>
        <tbody>{rows}</tbody>
      </table></section>"""

    return f"""
    <h2 class="section-divider">&#x2B21; SNPedia 2025 -- Deep Annotation</h2>
    <p class="gwas-intro">{n_db:,} of your SNPs matched the SNPedia 2025 database
    ({n_enriched:,} with meaningful annotations). Allele-specific findings extracted
    from SNPedia curated narrative text for your exact genotype.</p>

    <section class="category-section" id="pigmentation_snpedia">
      <h2 class="cat-title pig-title">Pigmentation &amp; Physical Appearance</h2>
      <p class="trait-context">Predicted physical traits based on MC1R, HERC2/OCA2,
      SLC24A5, SLC45A2, TYR, IRF4. Confidence reflects genetic evidence strength.</p>
      <table class="detail-table">
        <thead><tr><th>rsID</th><th>Gene</th><th>Your Genotype</th><th>Prediction</th></tr></thead>
        <tbody>{pig_rows}</tbody>
      </table>
    </section>

    <section class="category-section" id="snpedia_top">
      <h2 class="cat-title">SNPedia Top Findings</h2>
      <table class="detail-table">
        <thead><tr><th>rsID</th><th>Gene</th><th>Genotype</th><th>Category</th><th>Finding</th></tr></thead>
        <tbody>{top_rows or "<tr><td colspan='5' class='empty'>No high-signal findings extracted.</td></tr>"}</tbody>
      </table>
    </section>
    {cat_sections}"""

def load_config():
    if not CONFIG.exists():
        print(f"ERROR: people.json not found at {CONFIG}")
        sys.exit(1)
    with open(CONFIG) as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--person")
    grp.add_argument("--all", action="store_true")
    args = parser.parse_args()
    cfg    = load_config()
    shared = cfg["shared"]
    people = cfg["people"]
    targets = people if args.all else [p for p in people if p["name"].lower() == args.person.lower()]
    if not targets:
        print(f"ERROR: '{args.person}' not in people.json. Available: {[p['name'] for p in people]}")
        sys.exit(1)
    for pcfg in targets:
        print(f"\n{'─'*50}\n  Enriching: {pcfg['name']}\n{'─'*50}")
        r = enrich_person(pcfg, cfg["shared"])
        if r:
            print(f"  {r['enriched_snps']} enriched | {len(r['top_hits'])} top hits | {len(r['pigmentation'])} pigmentation traits")

if __name__ == "__main__":
    main()