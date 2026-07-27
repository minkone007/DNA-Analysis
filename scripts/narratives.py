#!/usr/bin/env python3

# ─────────────────────────────────────────────────────────────────────────────
# SECTIONS CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SECTIONS = [
    ("appearance",     "Physical Appearance & Traits",
     ["eye_color", "hair_color", "skin_tone", "hair_loss", "height"]),
    ("cardiovascular", "Cardiovascular Health",
     ["cholesterol", "triglycerides", "cad", "heart_failure",
      "atrial_fibrillation", "stroke", "blood_pressure"]),
    ("metabolic",      "Metabolic Health",
     ["t2d", "bmi", "gout", "chronic_kidney_disease", "vitamin_d", "mthfr"]),
    ("neurological",   "Brain, Cognition & Neurological Health",
     ["intelligence", "alzheimer", "parkinson", "depression", "adhd", "autism",
      "bipolar_disorder", "schizophrenia", "sleep_duration"]),
    ("cancer",         "Cancer Risk",
     ["melanoma", "breast_cancer", "prostate_cancer",
      "colorectal_cancer", "lung_cancer", "bladder_cancer"]),
    ("immune",         "Immune & Inflammatory Conditions",
     ["lupus", "rheumatoid_arthritis", "inflammatory_bowel",
      "crohn_disease", "multiple_sclerosis", "psoriasis", "asthma"]),
    ("longevity",      "Longevity & Ageing",
     ["longevity"]),
    ("lifestyle",      "Lifestyle, Nutrition & Drug Metabolism",
     ["caffeine_metabolism", "alcohol_consumption",
      "lactase_persistence", "pharmacogenomics"]),
]

RISK_LABELS = {
    "Elevated": "Повишен",
    "Favourable": "Благоприятен",
    "Typical": "Типичен"
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPER & SYNTHESIS FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def risk_label(pred):
    p = str(pred).lower()
    if "elevated" in p: return "Elevated"
    if "favourable" in p or "below average" in p or "low risk" in p: return "Favourable"
    return "Typical"

def risk_label_bg(pred):
    en = risk_label(pred)
    return RISK_LABELS.get(en, en)

def n_gwas_summary(r, trait_name):
    pred = r.get("prediction", "Standard")
    elevated = r.get("snps_used", 0)
    pgs = r.get("pgs_score", 0.0)
    narrative = r.get("narrative", "")
    
    support = r.get("supporting", [])
    if support:
        clean_support = [s.replace(" \u2192 ", " — ").replace("→", " — ").replace(" -> ", " — ") for s in support]
        sample_support = " ".join(clean_support[:2])
        locus_details = f"Observed variant alleles across {elevated} evaluated loci indicate combined polygenic contribution. Supporting markers show localized effects: {sample_support}"
    else:
        locus_details = "Detailed locus breakdown indicates polygenic load distributed across multiple regulatory blocks."

    return f"""
    <p><strong>Prediction:</strong> {pred} (PGS: {pgs:+.1f} across {elevated} loci analyzed in genome-wide association studies).</p>
    <p>{narrative}</p>
    <p><em>{locus_details}</em></p>
    """

def n_gwas_summary_bg(r, trait_name):
    pred = r.get("prediction", "N/A")
    elevated = r.get("snps_used", 0)
    pgs = r.get("pgs_score", r.get("gwas_pgs"))
    narrative = r.get("narrative", "")

    pgs_clause = f" (PGS: {pgs:+.1f} за {elevated} анализирани локуса в геномни асоциационни изследвания)." if pgs is not None else "."

    support = r.get("supporting", [])
    if support:
        clean_support = [s.replace(" \u2192 ", " — ").replace("→", " — ").replace(" -> ", " — ") for s in support]
        sample_support = " ".join(clean_support[:2])
        locus_details = f"Наблюдаваните варианти алели в {elevated} оценени локуса показват комбиниран полигенен принос. Поддържащи маркери показват локализирани ефекти: {sample_support}"
    else:
        locus_details = "Подробната разбивка по локуси показва полигенно натоварване, разпределено в множество регулаторни блокове."

    return f"""
    <p><strong>Прогноза:</strong> {pred}{pgs_clause}</p>
    <p>{narrative}</p>
    <p><em>{locus_details}</em></p>
    """

def n_immune(r, trait):
    themes = {
        "Lupus": ("STAT4 and IRF5", "interferon signalling", "sun protection and stress management"),
        "Rheumatoid Arthritis": ("HLA-DQB1 and TYK2", "HLA-mediated autoimmunity", "early joint symptom monitoring"),
        "Inflammatory Bowel": ("IL23R and HLA-DRB9", "intestinal immune regulation", "dietary triggers and microbiome health"),
        "Crohn Disease": ("IL23R (multiple hits)", "IL-23/Th17 pathway dysregulation", "dietary and stress management"),
        "Psoriasis": ("TYK2 and IL12B", "IL-23/IL-17 inflammatory axis", "skin monitoring and UV management"),
    }
    gene, pathway, management = themes.get(trait, ("HLA and immune genes", "immune regulation", "standard monitoring"))
    elevated = r.get('snps_used', 0)
    pgs = r.get('pgs_score', 0)

    return f"""
    <p>Your {trait} genetics show elevated signal, driven primarily by {gene}
    variants affecting the {pathway}. With {elevated} elevated loci and a PGS of
    {pgs:+.1f}, this is a meaningful genetic signal rather than statistical noise.</p>

    <p>An important pattern across your immune profile: elevated signals appear
    consistently across lupus, rheumatoid arthritis, inflammatory bowel disease,
    Crohn's disease, and psoriasis. This is not coincidental. These conditions share
    genetic architecture - particularly in the HLA region and cytokine signalling
    pathways. TYK2 GG (rs34536443) appears in both your psoriasis and rheumatoid
    arthritis data, and IL23R variants drive both your Crohn's and inflammatory
    bowel signals. This pattern suggests a genuine underlying theme of immune pathway
    sensitivity rather than five independent risk elevations.</p>

    <p>The shared genetic basis of these autoimmune conditions means that the same
    lifestyle factors that reduce one tend to reduce others: anti-inflammatory diet
    (Mediterranean pattern, omega-3s, low processed food), stress management,
    adequate sleep, and maintaining a diverse gut microbiome. Practical focus:
    {management}. These are real biological levers, not generic advice, for
    someone with this immune genetic profile.</p>

    <p>It is worth being aware of this cluster when discussing family history
    with your GP - autoimmune conditions are frequently underdiagnosed, and
    having a clear picture of your genetic predispositions can inform appropriate
    monitoring thresholds.</p>
    """

def n_cancer(r, trait):
    specifics = {
        "Breast Cancer": (
            "rs637644 GG (OR 32.50) and rs3844412 AA (OR 5.22) are the headline hits, "
            "but these ORs likely reflect population-specific or rare variant effects "
            "rather than common risk applicable to all ancestries. rs78378222 TT at TP53 "
            "is more universally relevant - TP53 is the genome's master tumour suppressor, "
            "and this intronic variant has been associated with modest breast cancer risk "
            "across multiple populations. rs140068132 AA at ESR1 (oestrogen receptor alpha) "
            "reflects the hormone-pathway component of breast cancer genetics. "
            "Standard screening recommendations apply; if family history of breast or "
            "ovarian cancer exists, clinical BRCA1/2 testing is more informative than "
            "polygenic scores for high-penetrance risk."
        ),
        "Prostate Cancer": (
            "rs17632542 TT at KLK3 (the PSA gene itself) and rs138213197 CC at HOXB13 "
            "are the most clinically relevant hits. HOXB13 G84E is a rare but high-risk "
            "variant for prostate cancer - however, CC at rs138213197 is the common "
            "non-G84E allele, so this may reflect a nearby regulatory variant rather "
            "than the high-risk coding change. KLK3 variants affect PSA levels "
            "independently of prostate cancer, which complicates PSA-based screening "
            "interpretation for carriers. Discussing this with a urologist before "
            "any PSA testing would be worthwhile."
        ),
        "Colorectal Cancer": (
            "Several hits show very high ORs (rs10920654 OR 76.85, rs78144988 OR 54.90) "
            "which almost certainly reflect population-specific rare variants rather "
            "than common risk. The more robustly replicated signals are rs885036 AA at "
            "MGAT4A and rs716897 TT at RASGRF2. Lifestyle modification is highly "
            "effective for colorectal cancer: high dietary fibre, limited red and "
            "processed meat, regular physical activity, and colonoscopy screening "
            "from age 45-50. Aspirin has demonstrated protective effects in high-genetic-risk "
            "individuals in some trials."
        ),
        "Melanoma": (
            "The melanoma signal is particularly coherent and actionable. SLC45A2 GG "
            "(rs16891982 and rs35407, both elevated OR ~2.0) is the ancestral darker "
            "pigmentation allele - but here it appears in the melanoma data because "
            "some studies find this allele pattern in melanoma cohorts reflecting "
            "ancestry confounding. More relevant is IRF4 CT (rs12203592, OR 1.76) - "
            "IRF4 genuinely affects melanocyte biology and melanoma risk. TP53 TT "
            "(rs78378222) is a cross-cancer signal. Combined with your TYR CA "
            "melanin-reducing variant from the pigmentation analysis, the UV sensitivity "
            "picture is clear and actionable: consistent SPF50, annual skin checks, "
            "and shade-seeking behaviour are genuinely warranted for your specific "
            "genetic profile. Melanoma caught at Stage I has >95% five-year survival."
        ),
        "Lung Cancer": (
            "rs17879961 AA at CHEK2 is the dominant signal, appearing multiple times "
            "with ORs of 1.54-2.63. CHEK2 is a DNA damage checkpoint gene - carriers "
            "of loss-of-function variants have elevated risk across multiple cancer types "
            "including lung, breast, and colorectal. However, rs17879961 is an intronic "
            "variant, not the classic CHEK2 I157T coding change, so its functional "
            "significance is less certain. rs11571818 TT at BRCA2 is also notable - "
            "again an intronic variant near rather than within the high-risk coding region. "
            "The critical contextual point: genetic lung cancer risk is dominated and "
            "modified by smoking status. If you are a non-smoker, your absolute lung "
            "cancer risk from these variants is very low. If you smoke, these variants "
            "represent genuine additional risk on top of the dominant environmental factor."
        ),
    }
    detail = specifics.get(trait, "")
    elevated = r.get('snps_used', 0)
    pgs = r.get('pgs_score', 0)

    return f"""
    <p>Your {trait} GWAS data shows {elevated} elevated loci with a PGS of {pgs:+.1f}.
    {detail}</p>
    """

def n_lifestyle(r, trait):
    specifics = {
        "Alcohol Consumption": """
    <p>Your alcohol genetics contain the most striking individual OR in this entire
    report: rs1229984 CC at ADH1B with OR 24.56. This requires careful interpretation.
    ADH1B encodes alcohol dehydrogenase, which converts alcohol to acetaldehyde.
    The CC genotype at rs1229984 is associated with slower ADH1B activity - meaning
    acetaldehyde accumulates more slowly, which in some populations is associated
    with higher alcohol consumption because the aversive flushing effect is reduced.
    However, an OR of 24.56 for alcohol consumption quantity (not a disease outcome)
    reflects the enormous population-level variation in drinking behaviour, not a
    personal risk for any specific harm.</p>

    <p>rs13107325 CC at SLC39A8 (OR 11.45) and rs1260326 CC at GCKR (OR 7.39-8.22)
    are additional metabolic variants associated with alcohol-related traits. GCKR
    is a glucokinase regulatory protein that affects both alcohol and glucose
    metabolism - its CC genotype is the risk allele here.</p>

    <p>The practical interpretation: these variants may reflect differences in
    alcohol metabolism efficiency and reward pathway response. They do not predict
    alcohol use disorder - that is a complex behavioural outcome with distinct
    genetics. What they do suggest is awareness of individual metabolic response
    to alcohol, particularly given the triglyceride picture (APOA5 AG means alcohol
    has a disproportionate effect on your triglyceride levels).</p>
    """,
        "Caffeine Metabolism": """
    <p>rs56113850 TC at CYP2A6 drives your caffeine signal, appearing three times
    with ORs of 4.59-9.59. CYP2A6 is primarily known for nicotine metabolism but
    also contributes to caffeine breakdown. The heterozygous TC genotype suggests
    intermediate metabolic activity at this locus.</p>

    <p>The primary caffeine metabolism gene - CYP1A2 - was not directly captured
    in your GWAS data, which limits the interpretation. CYP1A2 is the enzyme that
    handles roughly 95% of caffeine clearance, and its variants (particularly
    rs762551) are the strongest determinants of whether you are a fast or slow
    caffeine metaboliser. A direct CYP1A2 genotype test would give a clearer
    picture of your optimal caffeine timing.</p>

    <p>The practical takeaway from CYP2A6 TC: likely intermediate caffeine
    metabolism. If you notice caffeine affecting sleep quality even when consumed
    in the early afternoon, this is consistent with a slower-than-average
    clearance profile - cutting off caffeine by noon rather than 2-3pm would be
    a worthwhile experiment.</p>
    """,
        "Pharmacogenomics": """
    <p>Your pharmacogenomics GWAS data captured three elevated loci: rs77375493
    GG at JAK2 (OR 1.94), rs749671 GA at ZNF646 (OR 20.40), and rs245880 AG
    at CPVL (OR 4.69). The very high OR for rs749671 likely reflects a
    population-specific or rare variant effect rather than a broadly applicable
    drug response signal.</p>

    <p>The most clinically actionable pharmacogenomics variants - CYP2D6, CYP2C19,
    CYP2C9, TPMT, DPYD - were not captured in this GWAS dataset. These are the
    variants that directly affect metabolism of commonly prescribed drugs including
    antidepressants, antipsychotics, blood thinners, and chemotherapy agents.</p>

    <p>If you are starting any new medication - particularly antidepressants,
    antiplatelet drugs (clopidogrel), or pain medications involving codeine or
    tramadol - a pharmacogenomics panel from a clinical genetics service is worth
    discussing with your prescriber. These panels cost £100-300 and can prevent
    ineffective dosing or adverse reactions that would otherwise only be discovered
    through trial and error.</p>
    """,
    }
    return specifics.get(trait, f"<p>{r.get('narrative','')}</p>")


# ─────────────────────────────────────────────────────────────────────────────
# DETAILED BESPOKE NARRATIVES
# ─────────────────────────────────────────────────────────────────────────────
def n_eye_color(r):
    return """
    <p>Your eye colour prediction sits at the blue-green boundary, which is exactly
    where your genotype combination places you. The dominant signal is rs12913832 GG -
    this single variant in the HERC2 gene is the strongest known predictor of eye colour
    in humans, and GG is the classic blue-associated genotype found in roughly 97% of
    blue-eyed Europeans. On its own, this would predict blue.</p>

    <p>What introduces the green element is the combination of secondary signals pulling
    in different directions. SLC24A4 GT and IRF4 CT are both intermediate - they neither
    fully reinforce the blue signal nor push toward brown. SLC45A2 GG is the ancestral
    allele, which doesn't contribute the European lightening variant, adding a small
    counterweight. TYR AG (heterozygous) reduces melanin synthesis modestly across all
    tissues including the iris.</p>

    <p>The net result: a strongly reduced OCA2-driven melanin signal from HERC2, partially
    modulated by intermediate alleles at supporting loci. This produces a lighter-than-brown
    iris with the specific hue sitting somewhere between blue and green depending on
    lighting conditions and iris structure. Blue-green or green-blue are both plausible
    phenotypic outcomes. Brown is effectively ruled out - you carry none of the
    classic brown-promoting allele combinations at the key loci.</p>

    <p>One practical note: TYR CA's melanin-reducing effect extends beyond eye colour.
    The same enzyme reduction that lightens the iris also reduces UV-protective eumelanin
    in skin. This is not merely a cosmetic footnote - it has genuine implications for
    sun damage accumulation over a lifetime, addressed further in the skin section.</p>
    """

def n_hair_color(r):
    return """
    <p>Your hair colour genetics tell a clean, consistent story: medium to dark brown,
    with no red component. The MC1R gene - which functions as the primary switch between
    red/yellow pheomelanin and dark eumelanin - shows no risk variants across all four
    tested positions (Arg151Cys, Arg160Trp, Arg163Gln, Cys289Arg). This effectively
    rules out red hair entirely. You inherited a fully functional MC1R receptor, which
    means your melanocytes default to eumelanin production.</p>

    <p>The dominant pigmentation signal is SLC45A2 GG. This is the ancestral allele -
    common in non-European and darker-pigmented populations - which does not contribute
    the European hair-lightening variant. Combined with the absence of MC1R variants,
    this firmly establishes a dark baseline.</p>

    <p>The only modest lightening signal comes from TYR AC (heterozygous at rs1042602),
    which reduces tyrosinase enzyme efficiency. This is a moderate effect - it may
    contribute some softening of the darkest possible hue, which is why the prediction
    is medium-to-dark rather than jet black. SLC24A4 GT is intermediate and adds
    no meaningful lightening.</p>

    <p>The overall picture: dark brown hair driven by intact eumelanin machinery,
    with a modest TYR-mediated reduction that prevents the very darkest end of the
    spectrum. Environmental factors (sun exposure causing pheomelanin accumulation,
    ageing) will modify this over time, but the genetic baseline is clearly dark.</p>
    """

def n_skin_tone(r):
    return """
    <p>Your skin pigmentation genetics reveal an interesting tension between two
    opposing forces, which produces a medium rather than extreme result in either
    direction.</p>

    <p>The lightening signal is substantial: SLC24A5 AA is the derived European allele
    at the single most influential skin colour locus known. This variant spread through
    European and South Asian populations roughly 8,000 years ago, likely as an
    adaptation to low-UV environments requiring efficient vitamin D synthesis. Its effect
    size is large enough that it alone explains a significant fraction of the
    pigmentation difference between European and West African populations.</p>

    <p>Counterbalancing this is SLC45A2 GG - the ancestral allele at a second major
    pigmentation gene. Unlike the CC European variant at SLC45A2, GG does not contribute
    additional lightening. This creates a genuine partial offset: SLC24A5 pushes
    strongly toward lighter skin; SLC45A2 holds back from adding further lightening,
    producing a light-to-medium rather than very fair result.</p>

    <p>TYR CA (heterozygous) adds a third layer: reduced tyrosinase activity means
    less eumelanin output across all skin cells. This contributes to freckling tendency
    and, critically, to reduced UV protection. The skin's tanning response depends on
    tyrosinase upregulation in response to UV - with one reduced-function TYR allele,
    this response is blunted. The practical consequence: your skin burns more readily
    than it tans, and UV damage accumulates faster than in someone with full tyrosinase
    activity. SPF50 is not overcautious for this profile - it is the appropriate
    baseline, used consistently rather than occasionally.</p>

    <p>The Fitzpatrick Type III prediction (medium skin, tans after initial burn) fits
    this genotype combination accurately.</p>
    """

def n_cholesterol(r):
    return """
    <p>Your cholesterol genetics present a mixed but ultimately moderate picture.
    The most important finding is what is absent: you carry rs7412 CC, which is the
    APOE ε2 signal - associated with lower LDL and reduced cardiovascular risk compared
    to the common ε3/ε3 genotype. This is a genuinely favourable finding at the most
    clinically significant cholesterol locus.</p>

    <p>The note of caution is that rs429358 - the second SNP needed to fully call
    APOE genotype - was not on your chip. This means we cannot rule out a mixed
    ε2/ε4 genotype, which would partially offset the ε2 protection. A clinical APOE
    genotype test (inexpensive, available through your GP) would resolve this definitively
    and is worth doing given its implications for both cardiovascular and Alzheimer risk.</p>

    <p>Beyond APOE, the LDL-relevant variants show: rs629301 TT at SORT1/CELSR2 carries
    two copies of the LDL-raising allele - this locus modestly elevates LDL through
    effects on hepatic SORT1 expression and LDL receptor trafficking. rs11591147 GG at
    PCSK9 shows no protective loss-of-function allele, meaning you don't have the natural
    PCSK9 inhibition that some individuals carry (which can lower LDL by 30% without
    medication). LPA rs10455872 AA is non-risk - you do not carry the Lp(a)-elevating
    variant, which is a meaningful protective finding since elevated Lp(a) is an
    independent cardiovascular risk factor not captured by standard lipid panels.</p>

    <p>Overall: the SORT1 variant creates a modest LDL-raising tendency that is likely
    counterbalanced somewhat by the APOE ε2 signal. Diet and exercise remain the
    first-line approach. Annual lipid panels are appropriate, and resolving the full
    APOE status would meaningfully sharpen this picture.</p>
    """

def n_t2d(r):
    return """
    <p>Your Type 2 diabetes genetic profile deserves a careful reading because the
    headline number - elevated risk - obscures an important pattern in the detail.</p>

    <p>You are heterozygous at almost every major T2D locus. TCF7L2 CT (one risk copy),
    KCNJ11 CT (one risk copy), SLC30A8 TC (one risk copy), CDKN2A/B CT (one risk copy),
    HHEX TC (one risk copy), IGF2BP2 GT (one risk copy), FTO CA (one risk copy). This
    consistent heterozygosity across seven independent loci is the defining feature of
    your profile. It means you have accumulated moderate genetic loading broadly, rather
    than severe loading at any single gene.</p>

    <p>The three homozygous risk hits (rs76895963 TT, rs10741243 GG, rs1631619 GG)
    strengthen the signal, but rs1631619 GG deserves special mention: its OR of 5.0
    comes from a Korean cohort study. Population-specific effect sizes frequently do not
    replicate at full magnitude in other ancestries, and this variant should be
    interpreted with that caveat in mind.</p>

    <p>TCF7L2 is the most important finding here. It is the strongest and most widely
    replicated common T2D variant, operating through the Wnt signalling pathway to
    impair beta-cell function. Heterozygous carriers have approximately 1.4x baseline
    risk. Crucially, TCF7L2 risk carriers respond particularly well to lifestyle
    intervention - the Diabetes Prevention Program trial showed that carriers who
    underwent lifestyle modification had the same T2D incidence reduction as non-carriers,
    meaning the genetic effect is not fixed.</p>

    <p>The practical message: your genetic profile warrants attention to modifiable
    risk factors - weight, physical activity, dietary glycaemic load - but the
    predominantly heterozygous pattern means lifestyle intervention is genuinely
    effective at this level of loading. Fasting glucose and HbA1c monitoring every
    few years is appropriate regardless of symptoms.</p>
    """

def n_alzheimer(r):
    return """
    <p>Your Alzheimer's risk profile contains arguably the most reassuring finding in
    this entire report. rs7412 CC corresponds to the APOE ε2 allele - and APOE ε2
    is the strongest known protective variant against late-onset Alzheimer's disease.
    ε2 carriers have approximately 50% lower Alzheimer's risk compared to the common
    ε3/ε3 genotype, and are significantly overrepresented among cognitively healthy
    individuals aged 85 and older.</p>

    <p>The caveat, as noted in the cholesterol section, is that rs429358 was not on
    your chip - so we cannot fully exclude an ε2/ε4 mixed genotype. However, even
    ε2/ε4 carriers have attenuated risk compared to ε4/ε4 homozygotes, and the
    protective signal from ε2 is real and substantial regardless.</p>

    <p>The GWAS data shows 50 elevated loci and a PGS of +171.6, which appears to
    contradict the APOE finding. This apparent contradiction is important to understand:
    the GWAS TSV for Alzheimer's contains many study types including education-Alzheimer
    pleiotropic studies (variants that affect both educational attainment and Alzheimer
    risk via shared pathways). The APOE genotype, which is the dominant factor in
    clinical Alzheimer risk, is not always the dominant driver of GWAS polygenic
    scores in research studies. Weight APOE status heavily in your interpretation.</p>

    <p>Secondary loci: CLU CC (rs9331888) is a modest risk signal at the clusterin
    gene, which is involved in amyloid clearance. This is a small effect relative to
    APOE. The other curated loci (BIN1, CR1, PICALM) were either not on chip or showed
    no risk alleles in your data.</p>

    <p>The overall Alzheimer picture is genuinely favourable given the ε2 signal.
    The most evidence-based protective behaviours - cardiovascular health maintenance,
    regular aerobic exercise, quality sleep (critical for amyloid clearance via the
    glymphatic system), and cognitive engagement - remain worthwhile regardless of
    genotype, and are especially effective in ε2 carriers who already have a protective
    biological baseline.</p>
    """

def n_vitamin_d(r):
    return """
    <p>Your Vitamin D genetics show a nuanced picture that goes beyond the "mild" polygenic label. 
    While the overall GWAS score is only modestly elevated (+11.4), your specific variants reveal 
    inefficiencies at two critical stages: transport and cellular uptake.</p>

    <p><strong>Transport stage (GC gene):</strong> You carry rs7041 CA (heterozygous) and rs4588 GG. 
    This combination produces a mix of Vitamin D Binding Proteins, resulting in moderately reduced 
    efficiency in delivering Vitamin D to your tissues. It is not severely impaired, but it lowers 
    the amount of bioavailable Vitamin D compared to individuals with optimal GC genotypes.</p>

    <p><strong>Receptor stage (VDR gene):</strong> More significant are your VDR variants 
    - rs731236 AA (TaqI) and rs7975232 CC (ApaI). These are well-studied markers associated with 
    reduced Vitamin D receptor sensitivity. This means that even when Vitamin D reaches your cells, 
    the receptors that should trigger calcium absorption and bone mineralization respond less effectively.</p>

    <p>The combined effect creates a two-stage "volume reduction" on Vitamin D activity. You are not unable 
    to process Vitamin D, but you have a higher physiological requirement to achieve the same level of 
    calcium absorption and bone mineralization as someone with more efficient genetics. This aligns with 
    your earlier observation about reduced calcium storage capacity in bones.</p>

    <p><strong>Practical implications:</strong> Aim to maintain higher serum Vitamin D levels (ideally 50-70 ng/mL). 
    Because this is partly a receptor sensitivity issue, optimizing cofactors is crucial:</p>
    <ul>
      <li><strong>Magnesium</strong> (300-400 mg/day) - required for Vitamin D activation.</li>
      <li><strong>Vitamin K2 (MK-7)</strong> (100-200 mcg/day) - directs calcium into bones rather than soft tissues.</li>
    </ul>
    <p>Regular blood testing (25(OH)D, calcium, PTH) is recommended to fine-tune your levels.</p>
    """

def n_cad(r):
    return """
    <p>Coronary artery disease is where your genetic profile shows its most clinically
    significant elevation. The '9p21' locus (CDKN2B-AS1) - the single most replicated
    common CAD variant in the literature - appears twice in your data: rs4977574 AG
    (one risk copy) and rs1333049 CG (one risk copy at the secondary variant).
    These two variants are additive and their effects are well-established across
    multiple large cohort studies.</p>

    <p>What makes the '9p21' locus particularly important is that it acts independently
    of LDL cholesterol. Its mechanism involves regulation of cell proliferation in
    vascular smooth muscle and inflammatory pathways - meaning standard lipid testing
    will not capture this risk. Someone with normal cholesterol and '9p21' risk alleles
    still has meaningfully elevated CAD risk compared to population baseline.</p>

    <p>Additional signals: rs646776 TT at CELSR2/SORT1 (the same locus relevant to
    LDL) carries two copies of the risk allele and contributes via the LDL pathway.
    rs1122608 GG at LDLR is the LDL receptor region variant. The LPL rs264 GG is
    the protective allele - a gain-of-function variant that raises lipoprotein lipase
    activity and improves triglyceride clearance. This partial offset from LPL is
    a genuine counterbalancing factor.</p>

    <p>The GWAS shows 25 elevated loci and a PGS of +111, confirming meaningful
    polygenic loading across multiple CAD pathways. Given this profile, attention
    to the full cardiovascular risk picture is warranted: blood pressure monitoring,
    regular lipid panels (with awareness that '9p21' risk is not captured by LDL alone),
    smoking avoidance, and physical activity. High-sensitivity CRP (hsCRP) testing
    is worth discussing with your GP as an inflammatory risk marker relevant to
    the '9p21' pathway.</p>
    """

def n_bmi(r):
    return """
    <p>Your BMI genetics show moderate loading, with the key finding being FTO
    heterozygosity. rs9939609 AT means you carry one copy of the FTO risk allele
    (A) - each A allele adds approximately 0.4 kg/m^2 to average BMI, putting you
    at modest rather than strong genetic BMI elevation. The secondary FTO variant
    rs17817449 GT adds a small additional signal.</p>

    <p>A critically important counterbalance: rs2815752 AG at NEGR1 carries the
    protective allele (A) in heterozygous form. NEGR1 is involved in neuronal growth
    and appetite regulation - the protective variant is associated with lower BMI,
    and its presence here partially offsets the FTO signal.</p>

    <p>The most important thing to know about your FTO genotype is what the research
    shows about modifiability. The Kilpeläinen et al. 2011 meta-analysis (PLOS Medicine,
    218,000 participants) demonstrated that FTO risk allele carriers who were physically
    active had BMI values essentially identical to non-carriers. The genetic effect of
    FTO on BMI was almost completely abolished by regular physical activity. This is one
    of the clearest gene-environment interaction findings in all of genomics - and it is
    directly actionable. The genetic tendency exists; whether it expresses depends
    substantially on activity level.</p>
    """

def n_triglycerides(r):
    return """
    <p>Your triglyceride genetics show a pattern of moderate elevation with one
    important protective counterweight. The primary risk signal is APOA5 AG
    (rs662799 heterozygous) - APOA5 is the dominant triglyceride locus, and the G
    allele impairs APOA5's role in activating lipoprotein lipase, leading to slower
    triglyceride clearance. Heterozygous carriers typically show mild-to-moderate
    triglyceride elevation, with the effect amplified substantially by carbohydrate
    intake and alcohol.</p>

    <p>APOC3 AG (rs2266788) adds a secondary signal - APOC3 normally inhibits LPL,
    and the promoter variant increases APOC3 expression, further reducing triglyceride
    clearance. MTNR1B CG (heterozygous) affects fasting triglycerides via melatonin
    receptor signalling - a more modest contribution.</p>

    <p>The key protective finding is LPL rs328 CC - the S447X gain-of-function
    variant. This is genuinely protective: the C allele creates a truncated but
    hyperactive form of lipoprotein lipase that substantially improves triglyceride
    clearance. This is one of the few cases in lipid genetics where a variant provides
    real biological protection, and its presence meaningfully counterbalances the APOA5
    and APOC3 risk signals.</p>

    <p>Dietary implications are direct: your APOA5 heterozygosity means carbohydrate
    and alcohol intake have an amplified effect on your triglyceride levels compared
    to someone without this variant. Omega-3 supplementation (EPA/DHA, 2-4g daily)
    is particularly effective in APOA5 risk carriers - clinical trials show 20-30%
    triglyceride reduction. Low-carbohydrate diets are more effective for you than
    for the average person. The LPL protective allele means you have better baseline
    clearance capacity than your risk alleles alone would suggest.</p>
    """

def n_depression(r):
    return """
    <p>Your depression genetics tell a nuanced story that requires careful context
    to interpret correctly. The headline - elevated genetic signal with 32 GWAS loci
    and PGS +71.8 - reflects genuine polygenic loading. But depression genetics have
    important interpretive limitations that are as important as the numbers themselves.</p>

    <p>The most personally relevant findings are in the curated SNPs. BDNF rs6265 CT
    means you carry one copy of the Val66Met variant - the T (Met) allele is associated
    with reduced activity-dependent BDNF secretion. BDNF is the brain's primary
    neurotrophic factor, supporting neuronal survival, plasticity, and stress recovery.
    The Met allele has been associated with reduced hippocampal volume, increased
    anxiety response, and greater vulnerability to stress-induced mood changes.
    Importantly, BDNF levels are highly responsive to aerobic exercise - physical
    activity is one of the most robust BDNF upregulators known, and this is one
    mechanism by which exercise reduces depression risk.</p>

    <p>COMT rs4680 GG is the Warrior profile (Val/Val) - higher dopamine breakdown
    in the prefrontal cortex, which typically means better stress resilience and
    executive function under pressure, at the cost of slightly lower baseline
    dopamine tone. For depression, this is generally neutral-to-protective rather
    than a risk factor.</p>

    <p>NEGR1 AG (rs1545843) and TMEM161B TT (rs10514299) are the first wave of
    genome-wide significant depression hits, but their individual effect sizes are
    very small - important at the population level, less meaningful individually.</p>

    <p>The overarching message: the BDNF Val66Met heterozygosity is the most
    interpretively meaningful finding here. It suggests somewhat higher biological
    sensitivity to stress and environmental adversity - not a predetermined outcome,
    but a profile that responds particularly well to protective factors: regular
    aerobic exercise (the most evidence-based BDNF upregulator), quality sleep,
    and strong social connection. These are not generic lifestyle advice - for
    your specific genotype, they have direct neurobiological relevance.</p>
    """

def n_longevity(r):
    pgs = r.get("pgs_score", 62.4)
    return f"""
    <p>Your longevity genetics show moderate positive signals, with the APOE picture
    being the centrepiece. As noted in the Alzheimer section, rs7412 CC corresponds
    to the APOE ε2 allele - and ε2 is consistently overrepresented among centenarians
    in multiple independent cohort studies. The mechanism is multifactorial: lower LDL,
    reduced neuroinflammation, more efficient lipid metabolism, and lower Alzheimer risk
    all contribute to the survival advantage.</p>

    <p>The CETP variants add genuine additional longevity signal. CETP rs3764814 CT
    (one protective C allele) and CETP rs5882 AG (one protective allele) both point
    toward higher HDL cholesterol - and elevated HDL has been consistently associated
    with longevity in centenarian studies, particularly in Ashkenazi Jewish and
    Japanese cohorts. The CETP variants work by reducing cholesterol ester transfer
    activity, allowing HDL particles to remain larger and more functional for longer.</p>

    <p>FOXO3 was not on your chip - this is the single most replicated longevity
    locus outside APOE, active across five independent national cohorts. It is worth
    checking via a clinical or research genetic test if longevity genetics are of
    particular interest to you.</p>

    <p>The GWAS shows a stable polygenic score of {pgs:+.1f}. Combined with the APOE ε2
    signal and CETP variants, the overall longevity picture is moderately favourable
    at the genetic level. Genetic contributions to lifespan become increasingly powerful
    at extreme old age, while mid-life healthspan is governed largely by the cumulative
    management of modifiable cardiovascular, metabolic, and inflammatory risks.</p>

    <p>The overarching theme of your entire genetic report is that your destiny is not
    determined by a single extreme monogenic flaw, but by a complex web of moderate
    polygenic predispositions. Because your primary risks—cardiovascular loading,
    metabolic efficiency, and immune reactivity—are entirely addressable through
    targeted lifestyle, dietary, and supplemental choices, your actual healthspan
    remains firmly within your control.</p>
    """

def n_schizophrenia(r):
    return """
    <p>The schizophrenia GWAS signal deserves careful contextualisation before anything
    else is said. Your PGS of +125.2 and 29 elevated loci sound alarming, but this
    requires two important corrections before interpretation.</p>

    <p>First, schizophrenia polygenic risk scores have very poor individual predictive
    value. Even in the highest PGS decile of the general population, lifetime
    schizophrenia incidence remains around 3-4% - compared to ~1% population baseline.
    The score distinguishes statistical groups, not individuals. The vast majority of
    people with high schizophrenia PGS never develop the condition.</p>

    <p>Second, the specific variants driving your elevated score include several with
    very high ORs from small studies (rs117673608 at PRKN with OR 26.32, rs7116879
    at DKK3 with OR 14.70). Large ORs in GWAS almost always reflect either
    population-specific effects, small study sizes with inflated estimates, or rare
    variants with limited generalisability. The schizophrenia GWAS literature has
    known issues with winner's curse and population stratification in some datasets.</p>

    <p>The most meaningful biological signal here is the HLA/MHC component - many
    schizophrenia risk variants cluster in the major histocompatibility complex,
    reflecting the well-established immune and complement system involvement in
    schizophrenia pathophysiology. This shared genetic architecture with immune
    conditions (you also show elevated signals for lupus, rheumatoid arthritis,
    and inflammatory bowel disease) suggests a genuine biological theme of immune
    pathway sensitivity rather than classic psychiatric risk in isolation.</p>

    <p>There is no actionable clinical recommendation from this finding beyond what
    applies to everyone: good sleep, limited cannabis use (the strongest environmental
    schizophrenia risk factor in genetically susceptible individuals), and maintaining
    social and cognitive engagement.</p>
    """

def n_type_1_diabetes(r):
    pgs = r.get("pgs_score", 15.2)
    return f"""
    <p>Your Type 1 Diabetes genetics show an overall polygenic risk score of {pgs:+.1f}.
    T1D is a classic autoimmune condition characterized by the destruction of insulin-producing
    beta cells in the pancreatic islets, driven by a strong genetic interaction centered
    around the HLA-DR and HLA-DQ loci on chromosome 6.</p>

    <p>While consumer arrays cannot phase the high-resolution human leukocyte antigen haplotypes
    directly, the broader polygenic score captures secondary susceptibility variants across
    the genome. Your profile shows moderate background loading without the high-risk
    protective or predisposing footprints often seen in familial early-onset cohorts.</p>

    <p>Contextualising this within your broader immune profile, your T1D signal shares
    mechanistic territory with your other autoimmune-relevant findings (such as multiple
    sclerosis and thyroid-related markers). The underlying theme remains a tendency toward
    immune system over-reactivity in specific signaling pathways, reinforcing the value
    of broad anti-inflammatory lifestyle habits, gut microbiome support, and optimal
    micronutrient balance.</p>
    """

def n_rheumatoid_arthritis(r):
    pgs = r.get("pgs_score", 40.4)
    return f"""
    <p>Your rheumatoid arthritis genetics show 10 elevated loci with a PGS of {pgs:+.1f}.
    RA heritability is approximately 60%, with HLA-DRB1 alleles
    accounting for roughly 30% of genetic variance — the largest single
    genetic contribution to any common autoimmune disease.</p>

    <p>Beyond HLA, your elevated loci include PTPN22 (protein tyrosine
    phosphatase N22 — a major T-cell and B-cell signal regulator whose
    risk variant is the single strongest non-HLA RA locus), STAT4
    (shared with your lupus signal, confirming the interferon pathway
    theme), and PAD14 (peptidylarginine deiminase 4 — the enzyme that
    citrullinates proteins to create the anti-CCP antibodies that define
    seropositive RA).</p>

    <p>TYK2 GG appears here again — your homozygous TYK2 variant is the
    single genetic finding most consistently shared across your lupus,
    RA, psoriasis, and Crohn's elevated signals. It is the molecular
    common denominator of your autoimmune genetic profile.</p>

    <p>Early morning joint stiffness lasting more than 30 minutes is the
    classic prodromal symptom worth monitoring. Anti-CCP antibodies can
    be detected years before clinical RA onset — if joint symptoms develop,
    requesting anti-CCP testing early (rather than waiting for full
    diagnostic criteria) is supported by your PTPN22 and PAD14 genetic loading.
    Omega-3 fatty acids have the strongest evidence base of any nutritional
    intervention for RA risk reduction, operating through prostaglandin
    pathway modulation of the same Th17 inflammation your TYK2 variant amplifies.</p>
    """

def n_inflammatory_bowel_disease(r):
    pgs = r.get("pgs_score", 25.4)
    return f"""
    <p>Your inflammatory bowel disease (IBD) genetics show 8 elevated loci with a PGS
    of {pgs:+.1f}. IBD encompasses both Crohn's disease and ulcerative colitis, sharing
    deep genetic roots in mucosal immunity, epithelial barrier maintenance, and bacterial
    recognition pathways.</p>

    <p>The elevated loci in your profile include variants near genes involved in autophagy
    and cytokine signaling (such as NOD2-related pathways or secondary regulators), which
    influence how intestinal lining cells interact with the gut microbiome. When the gut
    barrier faces challenges from diet, stress, or dysbiosis, these genetic variants
    can modulate the local inflammatory response.</p>

    <p>Given the strong connection between gut health, systemic inflammation, and your
    alternative dietary routines (such as water kefir, nattō, and high-fiber additions),
    supporting microbial diversity and mucosal integrity is an exceptionally high-leverage
    action for your specific genetic architecture.</p>
    """

def n_celiac_disease(r):
    pgs = r.get("pgs_score", 9.1)
    return f"""
    <p>Your celiac disease genetics show a low polygenic loading with a PGS of {pgs:+.1f}.
    Celiac disease has one of the strongest genetic associations in all of medicine,
    primarily driven by the HLA-DQ2.2, DQ2.5, and DQ8 heterodimers.</p>

    <p>Without the primary HLA risk alleles, the development of classic autoimmune celiac
    enteropathy is statistically improbable. Your low polygenic score confirms that
    your genomic architecture lacks the core susceptibility framework required for
    gluten-induced autoimmune enteritis.</p>

    <p>While you may still experience individual digestive sensitivities to certain
    grains or fermentable carbohydrates due to general gut barrier dynamics or microbiome
    composition, your genetics indicate you do not carry the specific immunological
    vulnerability underlying celiac disease.</p>
    """

def n_eczema(r):
    pgs = r.get("pgs_score", 34.6)
    return f"""
    <p>Your eczema (atopic dermatitis) genetics show 11 elevated loci with a PGS of
    {pgs:+.1f} - a robust signal that connects directly with your asthma and immune
    profile as part of the classic atopic triad.</p>

    <p>Atopic dermatitis heritability is high, driven largely by genes involved in epidermal
    barrier function. The most famous locus in this domain is filaggrin (FLG), alongside
    various Th2 immune-regulation genes like IL13 and IL4R that dictate skin barrier
    permeability and local immune hyper-responsiveness.</p>

    <p>Your skin barrier's response to environmental stressors, detergents, and dry conditions
    is partly modulated by these pathways. The management strategy mirrors your systemic
    approach: maintaining optimal hydration, supporting skin lipid barriers externally,
    and keeping systemic Th2-driven inflammation in check through diet and lifestyle.</p>
    """

def n_psoriasis(r):
    pgs = r.get("pgs_score", 32.0)
    return f"""
    <p>Your psoriasis genetics show 13 elevated loci with a PGS of {pgs:+.1f}.
    Psoriasis heritability is 60–70%, with HLA-C*06:02 being the major risk
    allele — not directly interrogated by consumer arrays but with surrounding
    variants inferring its likely presence.</p>

    <p>The mechanistic core of your psoriasis signal is the IL-23/IL-17 axis —
    the same pathway dominant in your Crohn's disease data. TYK2 GG
    (rs34536443) is the linchpin: TYK2 phosphorylates STAT3 in response to
    IL-23, driving keratinocyte hyperproliferation (the defining feature of
    psoriatic plaques) and systemic inflammation. IL12B variants in your
    elevated set complete the IL-12/IL-23 heterodimer picture.</p>

    <p>Psoriasis and Crohn's disease co-occur at rates far above chance,
    and your genetics explain precisely why: you carry amplifying variants
    in the shared IL-23/TYK2 pathway that drives both conditions simultaneously.
    Biologic therapies that target IL-23 (risankizumab, guselkumab) or
    IL-17 (secukinumab, ixekizumab) are effective for both conditions —
    your TYK2 GG genotype would make you an especially strong responder
    to TYK2 inhibitors if pharmacotherapy becomes relevant.</p>

    <p>Environmental triggers that activate the IL-23 pathway: streptococcal
    throat infections (guttate psoriasis trigger), skin trauma (Koebner
    phenomenon), certain medications (lithium, beta-blockers), and
    psychological stress (which directly activates keratinocyte IL-17
    production via neuropeptide signalling). Awareness of these triggers
    is particularly valuable given your genetic loading.</p>
    """

def n_thyroid_function(r):
    pgs = r.get("pgs_score", 14.8)
    return f"""
    <p>Thyroid function genetics in your profile show a polygenic score of {pgs:+.1f}
    across several loci regulating thyroid-stimulating hormone (TSH) set points and
    peripheral thyroxine metabolism.</p>

    <p>Thyroid hormones act as the master regulator of basal metabolic rate, cellular
    energy production, and neural tempo. Minor genetic variations in feedback loops
    can influence how efficiently your tissues convert T4 to active T3 or how your
    pituitary gland gauges circulating hormone levels.</p>

    <p>In the context of your energy levels, sleep architecture, and metabolic markers,
    keeping a periodic check on standard thyroid panels (TSH, Free T3, Free T4) provides
    real-world ground truth that complements your genetic predispositions.</p>
    """

def n_obesity_bmi(r):
    pgs = r.get("pgs_score", 72.5)
    return f"""
    <p>Your body mass index and obesity genetics show a substantial polygenic score of
    {pgs:+.1f} across multiple elevated loci, representing one of the highest metabolic
    polygenic scores in your entire report.</p>

    <p>Obesity heritability is exceptionally high (40-70%), with the genetic architecture
    concentrated heavily in the central nervous system-specifically within hypothalamic
    circuits that regulate appetite, satiety signaling, and energy expenditure set points.
    Key loci like FTO and MC4R pathways dominate this genetic loading.</p>

    <p>This does not represent a lack of willpower; it represents a neuro-hormonal drive
    that naturally pushes toward higher energy storage in environments with constant food
    availability. Understanding this genetic bias allows you to structure your environment
    and nutrition proactively-relying on high-fiber foods, adequate protein, and consistent
    physical activity to manage metabolic set points rather than fighting biological
    hunger signals unassisted.</p>
    """

def n_atrial_fibrillation(r):
    pgs = r.get("pgs_score", 13.1)
    return f"""
    <p>Your atrial fibrillation GWAS data shows a polygenic score of {pgs:+.1f} with
    1 elevated locus out of 141 genotyped. AF has a heritability of approximately
    20–30% — lower than most cardiovascular conditions — meaning environmental
    and lifestyle factors play an unusually dominant role relative to genetics here.</p>

    <p>The primary elevated signal is in the PITX2 region, which is the single
    most replicated AF locus in the literature and controls left-right asymmetry
    in cardiac development. However, one elevated locus at moderate OR represents
    a mild signal rather than a strong predisposition.</p>

    <p>The more actionable picture from your overall profile: your coronary artery
    disease genetic loading (9p21 locus, PGS +111) and your triglyceride-raising
    variants are the primary cardiac risk drivers. AF is frequently downstream of
    the same cardiovascular risk factors — hypertension, coronary disease, and
    sleep apnoea. Controlling those primary risks is the most effective AF
    prevention strategy, and your genetics make that picture very clear.</p>

    <p><strong>Practical focus:</strong> blood pressure monitoring, regular lipid
    panels, maintaining healthy weight, and limiting alcohol (which has the
    strongest acute AF-triggering effect of any modifiable factor). Caffeine
    at your intermediate CYP1A2 level does not meaningfully elevate AF risk
    at moderate intake.</p>
    """

def n_stroke(r):
    pgs = r.get("pgs_score", 31.4)
    return f"""
    <p>Your stroke genetics show 9 elevated loci with a PGS of {pgs:+.1f} — a
    moderate signal that warrants attention, particularly in the context of your
    broader cardiovascular profile. Stroke heritability is approximately 40%,
    with substantial genetic overlap with coronary artery disease, atrial
    fibrillation, and blood pressure.</p>

    <p>The most notable finding in your stroke GWAS data is rs146092501 CC at
    COL6A3 with OR 12.5 for ischemic stroke — an unusually high odds ratio.
    Large ORs at single loci in stroke GWAS frequently reflect rare variant
    effects or population-specific findings rather than common high-penetrance
    risk, so this should be interpreted with caution. The more robustly replicated
    signals in your data include variants near ARNT2 (cardioembolic stroke subtype),
    which connects to the atrial fibrillation pathway.</p>

    <p>The critical context: your MTHFR compound heterozygosity (C677T + A1298C)
    is directly relevant here. Impaired homocysteine clearance from reduced MTHFR
    activity is an independent risk factor for ischemic stroke — elevated plasma
    homocysteine damages endothelial cells and promotes thrombosis. This is one
    of the clearest mechanistic connections in your entire genetic profile:
    the MTHFR variants and the stroke signal are biologically linked, and
    the intervention is the same — methylfolate supplementation to normalise
    homocysteine levels. This is not a coincidence to note and move on from;
    it is an actionable finding with a known, low-risk intervention.</p>
    """

def n_heart_failure(r):
    pgs = r.get("pgs_score", 61.4)
    return f"""
    <p>Your heart failure GWAS data shows 22 elevated loci with a PGS of {pgs:+.1f} —
    the highest cardiovascular polygenic score in your profile after BMI. This deserves
    careful interpretation because heart failure is almost always downstream of
    other conditions rather than a primary genetic disease in its own right.</p>

    <p>The majority of heart failure GWAS signals overlap with coronary artery disease,
    hypertension, diabetes, and atrial fibrillation pathways. Your elevated HF signal
    likely reflects the cumulative genetic loading across these upstream conditions
    rather than a direct myocardial defect. In your specific profile, the most
    probable upstream drivers are your 9p21 CAD signal and your moderate T2D loading
    — both of which are established causes of heart failure when untreated over decades.</p>

    <p>The clinical message is therefore not "you are at risk for heart failure"
    as a discrete condition, but rather that your cardiovascular and metabolic
    genetic loading collectively points toward the same prevention strategy:
    blood pressure control, lipid management, metabolic health, and regular
    cardiovascular exercise. These interventions protect against CAD, T2D,
    and heart failure simultaneously — the genetic signal converges on the
    same lifestyle prescription from multiple directions.</p>

    <p><strong>Specific loci of note:</strong> variants near HSPB7 and CLCNKA
    appear in your elevated hits — these are among the more robustly replicated
    genuine heart failure loci, associated with cardiac muscle protein quality
    control and renal sodium handling respectively.</p>
    """

def n_gout(r):
    pgs = r.get("pgs_score", 24.2)
    return f"""
    <p>Your gout genetics show 8 elevated loci with a PGS of {pgs:+.1f}. Gout
    is caused by hyperuricaemia — elevated uric acid crystallising in joints —
    and has a heritability of 35–60% with remarkably well-understood genetic
    architecture. The dominant loci in your data are SLC2A9 and ABCG2, the
    two major uric acid transporters that together account for roughly 3–4%
    of population variance in uric acid levels.</p>

    <p>SLC2A9 variants affect renal urate reabsorption — risk alleles reduce
    urate excretion, allowing levels to build. ABCG2 (rs2231142) affects
    intestinal urate secretion and is particularly associated with early-onset
    gout in populations with high purine intake. Your compound loading across
    multiple uric acid pathway variants suggests a genetic tendency toward
    higher baseline uric acid that is strongly amplified by dietary factors.</p>

    <p>The dietary interaction is among the strongest gene-environment effects
    in your entire profile. Fructose (including fruit juice and high-fructose
    corn syrup) is the single most potent dietary uric acid driver — more
    so than purines in meat — because fructose metabolism generates uric acid
    as a direct byproduct via the ATP depletion pathway. Alcohol, especially
    beer (which contains purines), has a compounding effect. Your triglyceride
    genetics (APOA5, GCKR) and gout genetics share this fructose-sensitivity
    pathway — the same dietary pattern that elevates your triglycerides also
    elevates uric acid.</p>

    <p><strong>Practical focus:</strong> limiting fructose-containing drinks,
    moderating alcohol (especially beer), adequate hydration, and maintaining
    healthy weight. Serum uric acid is cheap to test and gives a direct measure
    that makes genetic inference actionable — worth including in routine bloods.</p>
    """

def n_chronic_kidney_disease(r):
    pgs = r.get("pgs_score", 18.6)
    return f"""
    <p>Your chronic kidney disease genetics show 7 elevated loci with a PGS of
    {pgs:+.1f}. CKD heritability is approximately 45%, with the dominant genetic
    signals clustering around GFR regulation and renal tubular transport.</p>

    <p>The most relevant finding in the context of your overall profile is the
    mechanistic overlap between your CKD genetic signal and your other risk factors.
    Your T2D genetic loading and your hypertension-relevant signals are the primary
    known causes of CKD at the population level — diabetic nephropathy and hypertensive
    nephrosclerosis account for approximately 60% of all CKD cases. Your genetics
    are not pointing to a rare kidney-specific disease; they are amplifying the upstream
    metabolic and cardiovascular risk that you already carry.</p>

    <p>Your UMOD locus signal (uromodulin, the most abundant urinary protein)
    is worth noting — UMOD variants are among the more robustly replicated
    CKD loci and operate through tubular salt transport mechanisms. SHROOM3
    variants affecting podocyte structure also appear in your elevated set.</p>

    <p><strong>The MTHFR connection:</strong> homocysteine elevation from your
    MTHFR C677T + A1298C compound heterozygosity has documented nephrotoxic
    effects — elevated homocysteine damages glomerular endothelial cells by
    mechanisms similar to its arterial effects. Once again, methylfolate
    supplementation addresses multiple downstream risks simultaneously.</p>
    """

def n_sleep_duration(r):
    pgs = r.get("pgs_score", 7.8)
    return f"""
    <p>Your sleep duration genetics show 4 elevated loci with a PGS of {pgs:+.1f} —
    a mild but real signal. Sleep duration heritability is approximately 30–40%,
    with circadian gene variants playing the primary role.</p>

    <p>The elevated loci in your data include variants near PAX8 and VRK2 —
    PAX8 is involved in thyroid gland development (and thyroid function directly
    regulates sleep architecture), while VRK2 has broad neurological expression
    and overlaps with multiple psychiatric trait GWAS datasets.</p>

    <p>Reading your sleep genetics in the context of your full profile adds
    important layers. Your BDNF CT heterozygosity (Val66Met) affects sleep
    quality independently — reduced BDNF secretion impairs slow-wave sleep
    depth and hippocampal memory consolidation during sleep. Your COMT GG
    (Warrior, Val/Val) produces lower prefrontal dopamine, which is associated
    with better sustained attention but may affect the transition to sleep
    under high cognitive arousal. Your intermediate CYP1A2 caffeine metabolism
    means afternoon caffeine lingers significantly into the evening sleep window.</p>

    <p>These three factors — BDNF, COMT, and CYP1A2 — form a coherent
    picture for sleep optimisation: prioritise sleep consistency over duration,
    cut caffeine by noon, maximise deep sleep quality through exercise (which
    directly upregulates BDNF), and maintain low-light evenings to support
    melatonin onset despite the higher cortical arousal that the Warrior COMT
    profile can produce at end of day.</p>
    """

def n_adhd(r):
    pgs = r.get("pgs_score", 10.4)
    return f"""
    <p>Your ADHD genetics show 2 elevated loci with a PGS of {pgs:+.1f}. ADHD
    heritability is approximately 70–80%, making it one of the most heritable
    psychiatric conditions — but polygenic scores for ADHD currently explain
    only 5–10% of variance, meaning the genetic architecture is highly complex
    and individual prediction from common variants remains limited.</p>

    <p>The two elevated loci in your data include a variant near ST3GAL3,
    which appeared in early large ADHD GWAS studies and is thought to affect
    neuronal glycosylation pathways. The signal is real but modest.</p>

    <p>What is more interpretively meaningful in your profile is the convergence
    of several genetic signals that together describe an elevated-dopamine,
    high-arousal neurological profile. Your COMT GG (Val/Val, Warrior) produces
    higher dopamine breakdown in the prefrontal cortex — a profile associated
    with better performance under stress but potentially lower baseline attention
    in low-stimulation environments. Your DRD2 A2/A2 genotype means higher D2
    receptor density in the striatum. These variants together suggest a
    dopamine system that performs well under high external demand but may
    under-regulate in routine, low-stimulation contexts — a dimensional trait
    that sits on the same continuum as ADHD without necessarily reaching
    clinical threshold.</p>
    """

def n_autism(r):
    pgs = r.get("pgs_score", 8.2)
    return f"""
    <p>Your autism spectrum genetics show 4 elevated loci with a PGS of {pgs:+.1f}.
    Autism heritability is approximately 80%, but the genetic architecture is
    unusual: a substantial fraction of autism risk comes from rare de novo
    mutations not captured by GWAS arrays, making common-variant polygenic
    scores less predictive than for most other heritable conditions.</p>

    <p>The elevated loci in your data include variants near MACROD2 and KMT2E —
    both involved in chromatin remodelling and synaptic gene regulation. These
    are genuine biological signals in autism neurobiology, operating through
    pathways that regulate synaptic pruning and neuronal connectivity during
    development.</p>

    <p>The most important interpretive note: autism genetic variants at the
    sub-clinical polygenic level overlap substantially with traits associated
    with systematic, detail-focused cognitive styles, heightened sensory
    processing, and pattern recognition strengths. The same genetic architecture
    that confers autism risk in one configuration appears to confer cognitive
    advantages in others — this is not a rhetorical point but a documented
    empirical finding from large-scale phenome-wide studies. Your overall
    cognitive genetics (COMT GG, intelligence PGS +1064, systematic processing
    tendency) are coherent with a mild autism-spectrum-associated cognitive style
    without pathological expression.</p>
    """

def n_bipolar_disorder(r):
    pgs = r.get("pgs_score", 16.7)
    return f"""
    <p>Your bipolar disorder genetics show 7 elevated loci with a PGS of {pgs:+.1f}.
    Bipolar disorder heritability is approximately 70–80%, and crucially, shares
    substantial genetic overlap with schizophrenia (approximately 60% genetic
    correlation) and major depression (~35%). Your elevated signals across
    all three psychiatric conditions are therefore not independent findings —
    they reflect shared genetic architecture in pathways governing monoamine
    neurotransmission, voltage-gated calcium channels, and circadian regulation.</p>

    <p>The most replicated BD loci in your elevated set include variants near
    CACNA1C (calcium channel, the single most replicated BD gene), ANK3
    (ankyrin G, involved in axon initial segment organisation), and NCAN
    (neurocan, a synaptic proteoglycan). These represent genuine biological
    signals in mood regulation circuitry.</p>

    <p>The shared genetic signal across depression, bipolar disorder, and
    schizophrenia in your profile — combined with your RGS2 CC (elevated anxiety
    susceptibility), BDNF Val66Met (reduced plasticity buffer), and high
    intelligence PGS — describes a neurological profile with elevated sensitivity
    to environmental stressors and potentially wider mood range than average.
    This is a dimensional trait description, not a diagnosis. The protective
    factors are well-established: sleep regularity is the single most powerful
    mood stabiliser available without prescription — irregular sleep is the
    primary environmental trigger for mood episodes even in clinically diagnosed
    individuals.</p>
    """

def n_parkinson(r):
    pgs = r.get("pgs_score", 27.9)
    return f"""
    <p>Your Parkinson's disease genetics show 9 elevated loci with a PGS of
    {pgs:+.1f}. Parkinson's heritability is approximately 27% for common variants —
    lower than most conditions in this report — meaning environmental factors
    (pesticide exposure, head trauma, gut microbiome) play a proportionally
    larger role than genetics here.</p>

    <p>The key loci in your elevated set include variants near SNCA (alpha-synuclein,
    the protein that forms Lewy bodies — the defining pathological feature of PD),
    LRRK2 (leucine-rich repeat kinase 2, the most common genetic cause of familial
    PD), and GBA-adjacent variants. Your signal does not include the high-penetrance
    LRRK2 G2019S mutation — which would show as a specific genotype call —
    but rather common low-effect regulatory variants in the same locus.</p>

    <p>The most actionable protective finding from the literature: regular
    aerobic exercise reduces Parkinson's risk by 30–40% across multiple
    large prospective studies, and this effect is particularly pronounced in
    SNCA-locus variant carriers. The mechanism involves exercise-induced
    upregulation of DJ-1 (PARK7) and Parkin protein activity, which protect
    dopaminergic neurons from oxidative stress — the same pathway where your
    elevated variants operate. Coffee consumption (which you metabolise
    at intermediate speed via CYP1A2) has a well-replicated inverse association
    with PD risk via adenosine receptor antagonism in dopaminergic circuits.</p>
    """

def n_multiple_sclerosis(r):
    pgs = r.get("pgs_score", 28.1)
    return f"""
    <p>Your multiple sclerosis genetics show 5 elevated loci with a PGS of
    {pgs:+.1f}. MS heritability is approximately 50%, with the HLA region on
    chromosome 6 contributing roughly 20–30% of genetic variance on its own —
    making MS one of the most HLA-dependent common diseases known.</p>

    <p>The dominant genetic risk allele for MS is HLA-DRB1*15:01, which is
    not directly interrogated by consumer arrays but whose presence can be
    partially inferred from surrounding variants. Your elevated loci include
    signals in the HLA region alongside variants near CLEC16A (which regulates
    autophagy in antigen-presenting cells) and IL7R (interleukin-7 receptor,
    involved in T-cell homeostasis).</p>

    <p>Reading your MS signal in the context of your full immune profile is
    important. Your elevated signals across lupus, rheumatoid arthritis,
    inflammatory bowel disease, MS, and psoriasis collectively reflect a
    genuine theme of heightened immune pathway reactivity — particularly in
    T-cell mediated autoimmune signalling. These are not five independent
    findings; they are five windows into the same underlying biological
    predisposition. The intervention prescription is identical across all
    of them: vitamin D optimisation (your VDR variants make this particularly
    relevant — adequate vitamin D is the most consistently protective
    environmental factor for MS specifically), omega-3 supplementation,
    and maintenance of gut microbiome diversity.</p>
    """

def n_asthma(r):
    pgs = r.get("pgs_score", 40.4)
    return f"""
    <p>Your asthma genetics show 14 elevated loci with a PGS of {pgs:+.1f} —
    one of the higher signals in the immune category. Asthma heritability is
    60–80%, with strong genetic overlap with eczema and allergic rhinitis
    (the atopic triad), reflecting their shared Th2-polarised immune pathway.</p>

    <p>The dominant signals in your elevated loci include variants near
    IL33 (interleukin-33, an epithelial alarm cytokine that initiates Th2
    responses), ORMDL3/GSDMB on chromosome 17q21 (the strongest and most
    replicated asthma locus, affecting sphingolipid metabolism and epithelial
    barrier function), and IL1RL1/IL18R1 (the IL-33 receptor complex).</p>

    <p>The convergence of your asthma signal with your broader immune profile
    is coherent: your elevated signals across multiple autoimmune conditions
    suggest a generally reactive immune system. The Th2 pathway elevated in
    asthma and the Th17 pathway elevated in psoriasis and IBD are both branches
    of the same over-reactive immune architecture.</p>

    <p>Your vitamin D genetics are directly relevant here. VDR variants that
    reduce receptor sensitivity (your TaqI AA and ApaI CC genotypes) are
    associated with increased asthma severity — vitamin D strongly suppresses
    Th2 polarisation and promotes regulatory T-cell activity. Optimising
    vitamin D levels (supplementing to 50–70 ng/mL with methylated forms
    given your transport and receptor variants) has documented benefit for
    asthma control in genetically susceptible individuals.</p>
    """

def n_melanoma(r):
    pgs = r.get("pgs_score", 14.1)
    return f"""
    <p>Your melanoma genetics show 6 elevated loci with a PGS of {pgs:+.1f}. Melanoma
    is approximately 50% heritable for common variants, but the key insight here
    is that your genetic profile creates a layered risk picture where pigmentation
    genetics, UV sensitivity genetics, and melanoma GWAS signals all converge
    on the same actionable conclusion.</p>

    <p>The elevated GWAS loci include IRF4 CT (rs12203592) — your heterozygous
    IRF4 genotype appears in both your pigmentation analysis and the melanoma
    GWAS because IRF4 genuinely regulates melanocyte biology and melanoma
    susceptibility simultaneously. SLC45A2 GG (rs16891982) appears multiple
    times at OR ~2.0; this is partly an ancestry signal (the ancestral darker
    pigmentation allele appearing in fair-skinned melanoma cohorts as an
    outlier) but partly a genuine melanocyte function signal. TYR variants
    (including rs1042602 CA, your heterozygous tyrosinase variant) complete
    the picture — reduced tyrosinase activity both lightens skin and reduces
    the UV-protective eumelanin response.</p>

    <p>Reading across your full profile: TYR CA (reduced melanin output),
    SLC24A5 AA (lightened skin baseline), HERC2 GG (blue-eye haplotype
    reducing iris melanin), and the melanoma GWAS signal create a coherent
    portrait of a genome optimised for low-UV northern European environments
    but now operating in a higher-UV world. This is not alarming — it is
    clarifying. The intervention is straightforward and highly effective:
    melanoma caught at Stage I has greater than 95% five-year survival.
    SPF50 applied consistently (not occasionally), annual skin checks with
    a dermatologist, and shade-seeking between 11am and 3pm are genuinely
    warranted by your specific combination of genetic signals. This is
    one area where genetic knowledge directly translates to behaviour change
    with documented mortality benefit.</p>
    """

def n_breast_cancer(r):
    pgs = r.get("pgs_score", 80.9)
    return f"""
    <p>Your breast cancer genetics show 18 elevated loci with a PGS of {pgs:+.1f} —
    the highest cancer polygenic score in your profile. However, several important
    interpretive caveats apply before this number is taken at face value.</p>

    <p>First, some of the highest ORs in your elevated loci (rs637644 GG at OR
    32.50, rs3844412 AA at OR 5.22) almost certainly reflect population-specific
    or rare variant effects from smaller studies rather than commonly applicable
    risk. Large ORs in cancer GWAS are frequently subject to winner's curse —
    the tendency for initial discoveries to overestimate effect sizes. The more
    robustly replicated signals are rs78378222 TT near TP53 (the genome's master
    tumour suppressor) and rs140068132 AA near ESR1 (oestrogen receptor alpha),
    which is directly relevant to hormone-sensitive breast cancer pathophysiology.</p>

    <p>Second, the most clinically significant breast cancer variants — BRCA1
    and BRCA2 loss-of-function mutations — are rare, high-penetrance, and
    not captured by consumer GWAS arrays. If there is a family history of
    breast or ovarian cancer, clinical genetic testing for BRCA1/2 through
    your GP provides far more actionable information than polygenic risk scores
    for this specific condition.</p>

    <p>Third, your TP53 signal connects to a broader theme in your cancer
    genetics: TP53 TT (rs78378222) appears in both your breast cancer and
    lung cancer elevated sets. TP53 is the genome's primary DNA damage
    checkpoint — variants that modulate its activity affect cancer risk
    across multiple tissue types simultaneously rather than conferring
    tissue-specific risk.</p>

    <p><strong>Practical recommendation:</strong> standard mammography screening
    from age 40 (or earlier if family history exists), maintaining healthy
    weight (adipose tissue is the primary source of post-menopausal oestrogen),
    and moderating alcohol intake (which raises oestrogen levels and has the
    strongest lifestyle association with breast cancer of any modifiable factor).</p>
    """

def n_prostate_cancer(r):
    pgs = r.get("pgs_score", 61.2)
    return f"""
    <p>Your prostate cancer genetics show 12 elevated loci with a PGS of {pgs:+.1f}.
    Prostate cancer is the most heritable common cancer at approximately 57%,
    making genetic risk genuinely informative here in a way that it is not for
    less heritable cancers.</p>

    <p>The dominant signal in your data is the 8q24 locus — a gene desert
    (a region with no annotated protein-coding genes) that nevertheless contains
    the strongest common prostate cancer susceptibility region known. Multiple
    independent variants within 8q24 have been identified; your profile shows
    several hits in this region. The mechanism likely involves long-range
    enhancer regulation of MYC (c-Myc oncogene) located 300kb away. rs17632542
    TT near KLK3 (the PSA gene itself) is clinically notable: KLK3 variants
    directly affect PSA levels independently of prostate cancer, which means
    your PSA readings may behave differently than population averages. This
    is worth discussing with a urologist before any PSA-based screening —
    your genetic baseline PSA may be naturally different from population
    reference ranges, which could affect screening interpretation.</p>

    <p>HOXB13 rs138213197 appears in your data — CC here is the common
    non-risk allele at the position adjacent to the rare but high-penetrance
    HOXB13 G84E variant. You do not appear to carry the G84E high-risk
    variant itself, but this locus warrants a specific clinical query if
    prostate cancer family history exists on the paternal side.</p>

    <p><strong>Practical recommendation:</strong> PSA discussion with a
    urologist from age 45–50, noting the KLK3 genotype effect on baseline
    PSA interpretation. Lycopene-rich diet (tomatoes, watermelon) has
    the strongest epidemiological support for prostate cancer prevention
    among dietary factors.</p>
    """

def n_colorectal_cancer(r):
    pgs = r.get("pgs_score", 55.1)
    return f"""
    <p>Your colorectal cancer genetics show 10 elevated loci with a PGS of
    {pgs:+.1f}. CRC heritability is approximately 35% for common variants,
    making lifestyle factors proportionally more influential here than in
    more heritable cancers.</p>

    <p>Several elevated loci show very high ORs (rs10920654 at OR 76.85,
    rs78144988 at OR 54.90) which almost certainly represent population-specific
    rare variants rather than broadly applicable common risk. The more robustly
    replicated signals in your data include rs885036 AA near MGAT4A (involved
    in N-glycosylation of intestinal mucins — the protective mucus layer lining
    the colon) and rs716897 TT near RASGRF2 (a guanine nucleotide exchange
    factor affecting RAS signalling in colonic epithelium).</p>

    <p>Your inflammatory bowel genetics are directly relevant here: chronic
    intestinal inflammation is a major pathway to colorectal cancer, and
    your elevated signals across IBD, Crohn's, and CRC share overlapping
    biological mechanisms in intestinal epithelial integrity and immune
    surveillance. This is not three separate findings — it is a consistent
    biological theme centred on intestinal epithelial health.</p>

    <p>Colorectal cancer is one of the most lifestyle-modifiable cancers:
    dietary fibre (fermented by gut bacteria to short-chain fatty acids
    that protect colonocytes), regular physical activity (30% risk reduction
    in active vs sedentary individuals), limited red and processed meat,
    and colonoscopy screening from age 45. Aspirin has shown protective
    effects in genetically high-risk CRC individuals in clinical trials
    — worth discussing with your GP in the context of your genetic profile.</p>
    """

def n_lung_cancer(r):
    pgs = r.get("pgs_score", 31.6)
    return f"""
    <p>Your lung cancer genetics show 13 elevated loci with a PGS of {pgs:+.1f}.
    The critical interpretive context for lung cancer genetics is that smoking
    status completely dominates genetic risk — genetic variants modify risk on
    top of smoking exposure, but in a non-smoker, absolute lung cancer risk
    from these variants is very low regardless of polygenic score.</p>

    <p>The dominant signal in your data is rs17879961 AA at CHEK2, appearing
    multiple times at ORs of 1.54–2.63. CHEK2 (checkpoint kinase 2) is a
    DNA damage response gene that functions downstream of BRCA1 and ATM.
    Loss-of-function CHEK2 variants are associated with elevated risk across
    multiple cancer types. However, rs17879961 is an intronic regulatory
    variant rather than the classic CHEK2 I157T coding change, making its
    functional significance less certain. rs11571818 TT near BRCA2 connects
    to the same DNA repair pathway — this is consistent with your TP53 signal
    in breast cancer and your overall genetic theme of DNA damage checkpoint
    pathway variants contributing across multiple cancer sites.</p>

    <p>The coherent picture across your cancer genetics: breast cancer (TP53,
    ESR1), lung cancer (CHEK2, BRCA2-adjacent), and colorectal cancer (RASGRF2,
    MGAT4A) all show signals in DNA damage response and cellular checkpoint
    pathways. This suggests a genetic background with somewhat less robust
    DNA repair buffering — which is most relevant to carcinogen exposure.
    For a non-smoker, the absolute risk from these variants is modest.
    For anyone who has smoked, the genetic variants multiply an already
    high environmental exposure, making cessation the single highest-impact
    intervention available.</p>
    """

def n_bladder_cancer(r):
    pgs = r.get("pgs_score", 13.0)
    return f"""
    <p>Your bladder cancer genetics show 3 elevated loci with a PGS of {pgs:+.1f} —
    a mild signal. Bladder cancer is approximately 50% heritable for common
    variants, but smoking is the single dominant risk factor (accounting for
    ~50% of all bladder cancers) through the concentration of carcinogens
    in urine that directly contact the bladder epithelium.</p>

    <p>The elevated loci in your data include variants near PSCA (prostate
    stem cell antigen — despite the name, expressed in bladder epithelium
    and one of the most replicated bladder cancer loci), MYC on 8q24
    (the same oncogene-regulatory desert locus elevated in your prostate
    cancer data — a genuine cross-tissue cancer susceptibility region),
    and a variant near NAT2. NAT2 is particularly relevant: it encodes
    N-acetyltransferase 2, the enzyme that metabolises aromatic amines
    (found in tobacco smoke, hair dye, and some occupational exposures).
    Slow NAT2 acetylators allow aromatic amines to accumulate in urine
    longer, increasing bladder epithelial carcinogen exposure. Your NAT2
    variant status is worth noting if you have ever had significant occupational
    chemical exposure or prolonged hair dye use.</p>

    <p>For a non-smoker with no significant chemical exposures, the absolute
    bladder cancer risk from this genetic profile is low. Adequate hydration
    (which dilutes urinary carcinogens and reduces bladder wall contact time)
    is the most practical protective measure.</p>
    """

def n_lupus(r):
    pgs = r.get("pgs_score", 49.4)
    return f"""
    <p>Your lupus genetics show 32 elevated loci with a PGS of {pgs:+.1f} — one of
    the strongest immune signals in your profile. Lupus (systemic lupus
    erythematosus, SLE) heritability is approximately 44%, with a strong
    HLA component and several well-replicated non-HLA loci now established.</p>

    <p>The primary genetic theme in your lupus data is interferon pathway
    dysregulation. STAT4 variants (signal transducer for interferon-gamma),
    IRF5 (interferon regulatory factor 5), and multiple complement pathway
    variants collectively describe a genome primed toward excessive type I
    interferon production. This is the core immune mechanism in lupus — the
    so-called "interferon signature" that precedes and drives autoimmune
    tissue damage. Your elevated signals in this pathway are among the most
    robustly replicated findings in lupus genetics.</p>

    <p>Connecting this to your broader immune profile: the same interferon
    pathway dysregulation that underlies lupus genetic risk overlaps with
    your multiple sclerosis and rheumatoid arthritis signals. TYK2 GG
    (rs34536443), which you carry homozygously, is a pleiotropic variant
    affecting JAK-STAT signalling that appears across lupus, RA, and psoriasis
    datasets — a single gene variant simultaneously amplifying risk across
    three autoimmune conditions.</p>

    <p>UV light exposure is particularly relevant for lupus genetically
    susceptible individuals: UV-B directly activates the interferon pathway
    in skin, which can trigger systemic autoimmune flares in at-risk individuals.
    Combined with your TYR CA skin sensitivity and overall lighter pigmentation
    profile, sun protection has a double benefit — reducing both skin cancer
    risk and potential autoimmune pathway activation. Vitamin D optimisation
    (paradoxically requiring sun avoidance while supplementing orally) is the
    most evidence-based environmental modifier of lupus risk.</p>
    """

def n_inflammatory_bowel(r):
    pgs = r.get("pgs_score", 56.6)
    return f"""
    <p>Your inflammatory bowel disease genetics show 18 elevated loci with a
    PGS of {pgs:+.1f} — the highest immune signal in your profile. IBD
    heritability is approximately 75% for Crohn's disease and 70% for
    ulcerative colitis, making this one of the most genetically determined
    complex diseases known.</p>

    <p>The dominant loci in your elevated set are the NOD2 region (the first
    and most replicated IBD gene, involved in bacterial recognition in intestinal
    epithelium), ATG16L1 (autophagy — the cellular clean-up process that manages
    bacterial debris in intestinal cells), and the IL23R/IL17 axis (the primary
    inflammatory cytokine pathway driving intestinal inflammation). These three
    pathways — bacterial sensing, autophagy, and Th17 inflammation — are the
    mechanistic core of IBD pathophysiology.</p>

    <p>Your overlapping signals across IBD, Crohn's disease, and colorectal
    cancer form a coherent biological narrative: impaired epithelial barrier
    function allows bacterial translocation, NOD2-mediated recognition drives
    inflammatory response, dysregulated autophagy fails to resolve the
    inflammatory cycle, and sustained intestinal inflammation over decades
    creates the environment for epithelial transformation. These are not
    independent genetic findings — they describe a connected chain of
    intestinal biology.</p>

    <p>The gut microbiome is the primary environmental interface with your
    IBD genetics. Diversity-promoting interventions — dietary fibre from
    diverse plant sources, fermented foods, avoiding unnecessary antibiotics —
    directly support the microbial environment that NOD2 and ATG16L1 are
    genetically less equipped to manage. Omega-3 supplementation reduces
    intestinal IL-17 signalling through the same prostaglandin pathway that
    connects your triglyceride genetics to inflammation.</p>
    """

def n_crohn_disease(r):
    pgs = r.get("pgs_score", 48.6)
    return f"""
    <p>Your Crohn's disease genetics show 13 elevated loci with a PGS of
    {pgs:+.1f}. Crohn's is the more genetically complex of the two major IBD
    forms — affecting any part of the gastrointestinal tract rather than
    just the colon — and has a higher heritability (~75%) than ulcerative
    colitis (~70%).</p>

    <p>The dominant signal in your Crohn's data is IL23R, appearing multiple
    times across your elevated loci. IL-23 is the master cytokine driving
    Th17 cell differentiation — the inflammatory pathway that causes granuloma
    formation, the pathological hallmark of Crohn's disease. TYK2 GG
    (rs34536443), your homozygous JAK kinase variant, directly affects
    IL-23 signalling efficiency. You are homozygous for a variant that
    amplifies the primary inflammatory cytokine pathway in Crohn's — this
    is the most specific mechanistic finding in your immune genetics.</p>

    <p>This TYK2 finding has a direct pharmacological implication worth
    knowing even in the absence of current symptoms: TYK2 inhibitors
    (deucravacitinib is the first approved) represent a new class of
    targeted therapy specifically developed for TYK2-pathway-driven
    autoimmune diseases. Should Crohn's-like symptoms ever develop,
    your TYK2 GG genotype would make you an especially strong candidate
    for this mechanism of action over general immunosuppressants.</p>

    <p>The same dietary and lifestyle recommendations apply as for IBD
    generally — with particular emphasis on stress management, since the
    gut-brain axis is especially relevant in Crohn's: psychological stress
    directly activates intestinal mast cells and alters tight junction
    permeability via the same neural pathways that regulate your
    noradrenergic stress response (relevant to your RGS2 CC finding).</p>
    """

def n_alcohol_consumption(r):
    pgs = r.get("pgs_score", 37.8)
    return f"""
    <p>Your alcohol consumption genetics show 10 elevated loci with a PGS of
    {pgs:+.1f}. The headline finding — rs1229984 CC at ADH1B with OR 24.56 —
    is the most striking individual odds ratio in your entire report and
    requires careful interpretation before drawing conclusions.</p>

    <p>ADH1B encodes alcohol dehydrogenase 1B, the primary enzyme converting
    ethanol to acetaldehyde in the liver. The rs1229984 CC genotype at ADH1B
    corresponds to the *1/*1 allele combination — slower ADH1B activity compared
    to the *2 allele (common in East Asian populations). Slower ADH1B means
    alcohol is converted to acetaldehyde more slowly, reducing the aversive
    flushing response that deters drinking in fast-metaboliser populations.
    The OR of 24.56 reflects population-level variation in drinking quantity —
    it is not a health risk OR but rather a behavioural pharmacology finding
    describing who tends to drink more.</p>

    <p>Connecting this to your other genetics creates a clinically meaningful
    picture. Your ADH1B *1/*1 genotype means alcohol is tolerated without
    flushing — no built-in biological deterrent. Your APOA5 AG triglyceride
    genetics mean alcohol has an amplified effect on triglyceride levels —
    each unit of alcohol raises your triglycerides more than it would for
    someone without the APOA5 risk allele. Your IBD and Crohn's genetic
    loading means alcohol directly damages the intestinal epithelium in a
    context where your gut barrier genetics are already less robust. And
    your breast cancer TP53 and DNA repair variant signals mean alcohol's
    well-established carcinogenic mechanism (acetaldehyde DNA adduct formation)
    operates against a background of somewhat reduced DNA damage response.</p>

    <p>None of this means abstinence is mandated — the genetics describe
    tendencies and sensitivities, not destinies. But the convergence across
    four separate biological pathways (triglycerides, gut integrity, DNA
    repair, and cancer risk) suggests that for your specific genetic profile,
    the risk-benefit calculation for regular alcohol consumption is less
    favourable than for the average person. Moderate intake (1–2 units
    on occasion rather than daily) and avoiding alcohol specifically with
    high-purine meals (given your gout signal) represents a genotype-informed
    approach.</p>
    """

def n_caffeine_metabolism(r):
    pgs = r.get("pgs_score", 5.5)
    return f"""
    <p>Your caffeine metabolism genetics show 3 elevated loci with a PGS of
    {pgs:+.1f}. The primary signal is rs56113850 TC at CYP2A6, appearing
    three times with ORs of 4.59–9.59. CYP2A6 primarily metabolises
    nicotine but contributes to caffeine clearance as a secondary substrate.</p>

    <p>The more clinically relevant caffeine genetics come from your
    pharmacogenomics data: rs762551 CA at CYP1A2 (heterozygous, confirmed
    from your SNPedia enrichment) places you in the intermediate caffeine
    metaboliser category. CYP1A2 handles approximately 95% of caffeine
    clearance — the primary determinant of whether you are a fast or slow
    metaboliser. CA heterozygosity at rs762551 means CYP1A2 inducibility
    by caffeine itself is partial, giving approximately 5–7 hour half-life
    versus 3–4 hours in fast metabolisers (AA genotype).</p>

    <p>The practical pharmacokinetics for your profile: a morning espresso
    at 8am is largely cleared by 2–3pm. An afternoon coffee at 2pm still
    has significant caffeine remaining at 9–10pm bedtime. This directly
    connects to your sleep genetics (BDNF CT, sleep duration elevated loci)
    and your COMT GG profile: the Warrior COMT variant produces higher
    prefrontal cortical arousal under cognitive load, and residual evening
    caffeine compounds this arousal during the sleep-onset window.</p>

    <p>Caffeine's protective associations with Parkinson's disease (adenosine
    receptor antagonism in dopaminergic circuits) and cognitive function are
    relevant for your neurological profile. At your intermediate metabolism
    rate, two cups before noon captures these benefits without the sleep
    disruption that undermines the same cognitive and neurological goals
    caffeine is meant to support.</p>
    """

def n_lactase_persistence(r):
    return """
    <p>Your lactase persistence genotype is AG (heterozygous) at rs4988235
    (LCT/MCM6) — confirmed from your raw DNA data. The T allele (derived,
    persistence-conferring) is present in one copy, which is sufficient for
    full lactase enzyme production into adulthood. You are lactose tolerant.</p>

    <p>This variant originated approximately 7,500–10,000 years ago in the
    Pontic-Caspian steppe or northern Europe and spread dramatically with
    cattle-herding cultures because of the substantial caloric and nutritional
    advantage of digesting fresh milk. It is one of the most studied examples
    of recent positive selection in the human genome — its frequency went from
    near-zero to dominance in northern European populations in fewer than
    400 generations, one of the fastest selective sweeps documented in modern
    humans.</p>

    <p>Your heterozygous AG status is consistent with your ancestry profile:
    homozygous TT (full lactase persistence from both parental lineages) is
    most common in populations with the longest cattle-herding tradition
    (Scandinavians, Irish, northern Germans). AG heterozygosity is typical
    of populations at the southern/eastern edge of the lactase persistence
    gradient — exactly where the Eastern Balkan ancestry profile sits, at
    the boundary between the northern European high-persistence zone and
    the southern European/Middle Eastern lower-persistence zone.</p>

    <p>Functionally, AG heterozygotes produce sufficient lactase for
    comfortable dairy digestion throughout life, though enzyme production
    may be somewhat lower than in TT homozygotes. Full-fat dairy is
    digested without issue; very large quantities of skim milk on an
    empty stomach may occasionally produce mild symptoms in some AG
    individuals, but this is an edge case rather than the rule.</p>
    """

def n_hair_loss(r):
    return """
    <p>Your hair loss genetics tell a reassuring story. The X-linked AR/EDA2R locus
    - the single strongest signal for male pattern baldness, with ORs above 2.0
    in published GWAS - shows rs2497938 CC, which is the non-risk genotype.
    This locus is inherited maternally (on the X chromosome), meaning the signal
    you carry from your mother's side does not confer the classic androgenetic
    alopecia predisposition at this dominant position.</p>

    <p>The GWAS confirms this: only 1 elevated locus out of 15 genotyped, with a
    PGS of +2.8 - the lowest meaningful polygenic score in your entire profile.
    Male pattern baldness is approximately 80% heritable, making this one of the
    most genetically determined traits in the report. The low genetic signal here
    is therefore genuinely informative rather than a data gap.</p>

    <p>AR receptor sensitivity and DHT conversion rates have additional genetic
    determinants (5-alpha reductase, androgen receptor CAG repeat length) that
    were not captured on your chip, so a small residual uncertainty remains.
    But the primary signal is clear and favourable.</p>
    """

def n_height(r):
    return """
    <p>Height is one of the most polygenic traits in the human genome - thousands
    of variants each contributing fractions of a millimetre. Your polygenic score
    of +401 from 29 elevated loci is the second-highest quantitative score in
    your profile (after intelligence), and it consistently points above the
    population mean.</p>

    <p>HMGA2 rs1042725 TT is the one well-characterised curated locus on your chip.
    HMGA2 (High Mobility Group AT-hook 2) is a transcription factor that regulates
    growth and development - TT at this position is the taller-associated genotype,
    contributing approximately 0.4 cm per allele in large-scale studies.</p>

    <p>The GWAS elevated loci include hits across pathways governing bone growth,
    IGF-1 signalling, and skeletal development. A PGS of +401 in the height GWAS
    (which uses beta coefficients in cm units) translates to a meaningful cumulative
    signal toward above-average stature. Height is approximately 80% heritable in
    well-nourished populations, and your genetic signal is consistent with
    above-average genetic potential for height - though actual realised height
    depends substantially on childhood nutrition, sleep, and health.</p>
    """

def n_intelligence(r):
    return """
    <p>Your cognitive genetics contain the highest polygenic score in this entire
    report: PGS +1064 from 8 elevated loci in the intelligence GWAS. Before
    interpreting this, the important methodological context: intelligence GWAS
    studies frequently include educational attainment as a proxy phenotype, and
    many hits reflect pleiotropic variants that affect both educational achievement
    and Alzheimer's risk via shared biological pathways. The PGS score therefore
    reflects a mixture of cognitive ability, educational propensity, and
    neurological resilience signals - not a pure intelligence measure.</p>

    <p>The curated SNPs provide the most interpretable layer. COMT rs4680 GG is
    the Val/Val (Warrior) genotype - higher COMT enzymatic activity means faster
    dopamine breakdown in the prefrontal cortex. This produces better working
    memory performance and executive function under high cognitive load and stress,
    at the cost of slightly lower baseline dopamine tone and potentially reduced
    exploratory behaviour. Critically, Val/Val carriers show superior cognitive
    performance specifically under pressure and in complex task-switching - the
    profile associated with performance in demanding professional environments.</p>

    <p>BDNF rs6265 CT (Val66Met heterozygous) is the one nuancing factor. The
    Met allele reduces activity-dependent BDNF secretion, which affects synaptic
    plasticity and learning consolidation. However, heterozygosity means one
    functional Val allele remains - this is a partial rather than full reduction.
    In practice, Val66Met heterozygotes show modestly reduced episodic memory
    performance in some studies but maintain normal working memory.</p>

    <p>The combination - COMT Warrior profile with heterozygous BDNF - suggests
    a cognitive profile that excels under cognitive demand and structured tasks,
    while being somewhat more dependent than average on sleep quality and
    aerobic exercise for optimal memory consolidation. BDNF is one of the
    most exercise-responsive genes known: regular aerobic exercise upregulates
    BDNF expression and substantially compensates for the Met allele's reduced
    baseline secretion.</p>
    """

def n_mthfr(r):
    return """
    <p>Your folate and B-vitamin metabolism genetics are the most clinically
    actionable nutritional finding in this report, and they deserve careful
    attention because they were missing from the main health report entirely.</p>

    <p>You carry two MTHFR variants simultaneously - compound heterozygosity
    that is more significant than either variant alone:</p>

    <p><strong>MTHFR C677T (rs1801133) GA - heterozygous.</strong> The T allele
    reduces MTHFR enzyme activity by approximately 35% in heterozygotes. MTHFR
    (methylenetetrahydrofolate reductase) is the key enzyme that converts folate
    into the active form (5-methylTHF) used to recycle homocysteine back to
    methionine. Reduced activity means slower homocysteine clearance and
    potentially elevated plasma homocysteine - a cardiovascular and neurological
    risk factor.</p>

    <p><strong>MTHFR A1298C (rs1801131) GT - heterozygous.</strong> The C allele
    at this position reduces MTHFR activity through a different mechanism,
    affecting the regulatory domain of the enzyme. Alone, A1298C heterozygosity
    has modest effects. Combined with C677T heterozygosity (compound
    heterozygosity), the functional enzyme activity can be reduced by 50-60% -
    approaching the level seen in C677T homozygotes.</p>

    <p><strong>MTR A2756G (rs1805087) AA</strong> - this is the wild-type at the
    methionine synthase gene, meaning no additional impairment of the B12-dependent
    remethylation pathway from this locus.</p>

    <p><strong>MTRR A66G (rs1801394) GG</strong> - this is the AA wild-type at
    methionine synthase reductase (the enzyme that recycles the B12 cofactor for
    MTR). GG here means no MTRR-related impairment.</p>

    <p><strong>MTHFD1 (rs2236225) AG</strong> - heterozygous at the
    methylenetetrahydrofolate dehydrogenase gene, which feeds into the folate cycle.
    This adds a modest additional strain on the overall one-carbon metabolism pathway.</p>

    <p>The practical implications of compound MTHFR heterozygosity are direct and
    well-supported by clinical evidence:</p>

    <p>First, standard folic acid (the synthetic form in most supplements) requires
    conversion to active 5-methylTHF by MTHFR itself - a step that is inefficient
    in your case. The solution is to supplement with <strong>methylfolate
    (5-MTHF)</strong> directly, bypassing the impaired conversion step entirely.
    400-800 mcg of methylfolate daily is the standard recommendation for MTHFR
    compound heterozygotes.</p>

    <p>Second, B12 status matters more for you than for the average person.
    The homocysteine-to-methionine conversion requires both active folate and
    B12 as cofactors. Methylcobalamin (the active form of B12) rather than
    cyanocobalamin is preferable for the same bypass reasoning. Testing
    homocysteine, folate, and B12 blood levels is worth doing to establish
    your actual metabolic status - genetics tell you the predisposition,
    blood tests tell you whether it is expressing.</p>

    <p>Third, the cardiovascular relevance: elevated homocysteine is an
    independent risk factor for coronary artery disease and stroke - two areas
    where your GWAS data already shows elevated signals. This is not coincidental;
    the MTHFR-homocysteine-cardiovascular connection is well-established and
    represents a direct intervention opportunity. Adequate methylfolate and
    methylcobalamin supplementation has been shown to normalise homocysteine
    in MTHFR carriers.</p>

    <p>This is one area where a relatively simple nutritional intervention
    (switching supplement forms) has genuine mechanistic rationale specific
    to your genotype.</p>
    """

def n_blood_pressure(r):
    pgs = r.get("pgs_score", 0.0)
    return f"""
    <p>Your blood pressure genetics show a polygenic score of {pgs:+.1f}. Blood pressure 
    regulation is governed by multiple physiological pathways, including renal sodium 
    handling, vascular tone, and the renin-angiotensin-aldosterone system.</p>
    
    <p>While polygenic scores provide a baseline probabilistic view, actual blood pressure 
    is heavily modulated by modifiable factors such as sodium-to-potassium intake ratios, 
    cardiovascular exercise, stress management, and metabolic health.</p>
    """

def n_pharmacogenomics(r):
    return f"""
    <p>Your pharmacogenomics GWAS data captured elevated loci including rs77375493 GG at JAK2 (OR 1.94), 
    rs749671 GA at ZNF646 (OR 20.40), and rs245880 AG at CPVL (OR 4.69). The very high OR for 
    rs749671 likely reflects a population-specific or rare variant effect rather than a broadly 
    applicable drug response signal.</p>

    <p>The most clinically actionable pharmacogenomics variants—CYP2D6, CYP2C19, CYP2C9, TPMT, 
    DPYD—were not captured in this GWAS dataset. If you are starting any new medication, a 
    pharmacogenomics panel from a clinical genetics service is worth discussing with your prescriber.</p>
    """


# ─────────────────────────────────────────────────────────────────────────────
# GENERIC & FALLBACK NARRATIVES (For remaining traits without bespoke overrides)
# ─────────────────────────────────────────────────────────────────────────────
def n_freckles(r): 
    return "<p>MC1R variants indicate moderate propensity for freckling under sun exposure.</p>"

def n_earlobe_type(r): 
    return "<p>Standard anatomical expression for earlobe attachment.</p>"

def n_bitter_taste(r): 
    return "<p>TAS2R38 bitter tasting genotype indicates standard sensitivity to glucosinolates.</p>"

def n_facial_hair(r): 
    return "<p>Standard genetic markers for facial hair density and distribution.</p>"

def n_hdl_cholesterol(r): 
    return "<p>Standard clearance markers for high-density lipoprotein transport.</p>"

def n_ldl_cholesterol(r): 
    return "<p>Polygenic markers indicating standard hepatic clearance of low-density lipoproteins.</p>"

def n_metabolic_syndrome(r): 
    return "<p>Combined lipid and glycemic markers warranting active metabolic tracking.</p>"

def n_fasting_glucose(r): 
    return "<p>Standard hepatic glucose output and insulin sensitivity markers.</p>"

def n_insulin_resistance(r): 
    return "<p>Normal baseline tissue response to circulating insulin.</p>"

def n_neuroticism(r): 
    return "<p>Baseline genetic predisposition regarding emotional stability and stress reactivity.</p>"

def n_cognitive_decline(r): 
    return "<p>Standard cognitive maintenance markers across aging trajectories.</p>"

def n_anxiety(r): 
    return "<p>Serotonergic and GABAergic pathway markers associated with baseline stress response.</p>"

def n_insomnia(r): 
    return "<p>Circadian clock gene variations influencing sleep-onset latency.</p>"

def n_seasonal_affective(r): 
    return "<p>Melanopsin and photoperiod response markers.</p>"

def n_gastric_cancer(r): 
    return "<p>Standard gastric mucosal resilience markers.</p>"

def n_pancreatic_cancer(r): 
    return "<p>Standard exocrine and endocrine pancreatic structural markers.</p>"

def n_kidney_cancer(r): 
    return "<p>Standard renal cell carcinoma genetic risk baseline.</p>"

def n_thyroid_cancer(r): 
    return "<p>Standard follicular and papillary thyroid profile markers.</p>"

def n_leukemia_risk(r): 
    return "<p>Standard hematopoiesis and bone marrow genomic stability profile.</p>"

def n_hay_fever(r): 
    return "<p>Atopic predisposition markers indicating seasonal allergic rhinitis tendencies.</p>"

def n_ulcerative_colitis(r): 
    return "<p>Mucosal immune regulation markers overlapping with broader IBD pathways.</p>"

def n_ankylosing_spondylitis(r): 
    return "<p>HLA-B27 and related inflammatory pathway assessment markers.</p>"

def n_sarcoidosis(r): 
    return "<p>Granulomatous inflammatory pathway genetic baseline.</p>"

def n_allergy_susceptibility(r): 
    return "<p>General atopic reactivity and IgE pathway markers.</p>"

def n_nicotine_dependence(r): 
    return "<p>Nicotinic acetylcholine receptor subunit variations affecting addictive response.</p>"

def n_cannabis_response(r): 
    return "<p>Endocannabinoid system receptor and metabolizing enzyme markers.</p>"

def n_sweet_preference(r): 
    return "<p>Gustatory and reward-circuitry markers influencing dietary sugar intake.</p>"

def n_salt_taste_sensitivity(r): 
    return "<p>Renin-angiotensin and gustatory receptors affecting sodium preference.</p>"

def n_circadian_preference(r): 
    return "<p>PER and CRY clock gene variants determining chronotype preference.</p>"


# ─────────────────────────────────────────────────────────────────────────────
# BULGARIAN OVERRIDES & LOCALIZATION
# ─────────────────────────────────────────────────────────────────────────────
def n_eye_color_bg(r):
    return """
    <p>Вашата прогноза за цвят на очите се намира на границата между синьо и зелено,
    точно както предполага генотипната ви комбинация. Доминиращият сигнал е rs12913832 GG —
    този единичен вариант в гена HERC2 е най-силният известен предиктор на цвета на очите
    при хората, а GG е класическият генотип, свързан със синьо, срещан при около 97% от
    синеоките европейци.</p>

    <p>Зеленият елемент се въвежда от комбинацията на второстепенни сигнали, действащи
    в различни посоки. SLC24A4 GT и IRF4 CT са и двата междинни — те нито затвърждават
    напълно синия сигнал, нито го теглят към кафяво. SLC45A2 GG е предшестващият алел,
    който не допринася за европейския просветляващ вариант. TYR AG (хетерозиготен)
    умерено намалява синтеза на меланин във всички тъкани, включително ириса.</p>

    <p>Резултатът: силно намален меланинов сигнал от HERC2, частично модулиран от
    междинни алели в поддържащите локуси. Кафявото практически е изключено — не носите
    нито една от класическите комбинации, свързани с кафяв цвят на очите.</p>
    """

def n_hair_color_bg(r):
    return """
    <p>Генетиката на цвета на косата ви разказва ясна и последователна история: средно
    до тъмнокафяв цвят, без червен компонент. Генът MC1R — който функционира като основен
    превключвател между червено-жълт феомеланин и тъмен еумеланин — не показва рискови
    варианти в нито една от четирите тествани позиции. Това практически изключва червената
    коса. Наследили сте напълно функционален MC1R рецептор.</p>

    <p>Доминиращият пигментационен сигнал е SLC45A2 GG — предшестващият алел, характерен
    за по-тъмно пигментирани популации, който не допринася за европейския просветляващ
    вариант. В комбинация с липсата на MC1R варианти, това затвърждава тъмна изходна база.</p>

    <p>Единственият лек просветляващ сигнал идва от TYR AC (хетерозиготен), който намалява
    ефективността на ензима тирозиназа — умерен ефект, обясняващ защо прогнозата е средно
    до тъмнокафяво, а не абаносово черно.</p>
    """

def n_skin_tone_bg(r):
    return """
    <p>Генетиката на пигментацията на кожата ви разкрива интересно противопоставяне
    между две противоположни сили, което води до среден, а не краен резултат в която и
    да е посока.</p>

    <p>Просветляващият сигнал е значителен: SLC24A5 AA е производният европейски алел
    в най-влиятелния известен локус за цвят на кожата. Ефектът му е достатъчно голям,
    за да обясни сам по себе си голяма част от разликата в пигментацията между европейски
    и западноафрикански популации.</p>

    <p>Противодействащ фактор е SLC45A2 GG — предшестващият алел във втори основен
    пигментационен ген, който не добавя допълнително просветляване, създавайки по-скоро 
    светло до средно, отколкото екстремно светло крайно ниво.</p>

    <p>TYR CA (хетерозиготен) добавя трети пласт: намалена тирозиназна активност
    означава по-малко еумеланин във всички кожни клетки — допринася за склонност към
    лунички и намалена UV защита. SPF50 не е прекомерна предпазливост за този профил —
    той е подходящата основа, използвана последователно.</p>
    """

def n_hair_loss_bg(r):
    return """
    <p>Генетиката на косопада ви разказва обнадеждаваща история. X-свързаният локус
    AR/EDA2R — най-силният сигнал за мъжки тип плешивост — показва rs2497938 CC,
    което е нерисковият генотип. Този локус се наследява по майчина линия, което означава,
    че сигналът, който носите от майчина страна, не предразполага към класическата
    андрогенетична алопеция на тази доминантна позиция.</p>

    <p>GWAS данните потвърждават това: само 1 повишен локус от 15 генотипирани,
    с PGS от +2.8 — най-ниският значим полигенен резултат в целия ви профил. Мъжкият
    тип плешивост е приблизително 80% наследствен, което прави тази находка истински
    информативна, а не просто липса на данни.</p>
    """

def n_height_bg(r):
    return """
    <p>Ръстът е една от най-полигенните черти в човешкия геном — хиляди варианти,
    всеки допринасящ с частица от милиметър. Вашият полигенен резултат от +401 от
    29 повишени локуса е вторият по височина количествен резултат във вашия профил
    и последователно сочи над средното за популацията.</p>

    <p>HMGA2 rs1042725 TT е добре характеризираният куриран локус на вашия чип.
    HMGA2 е транскрипционен фактор, регулиращ растежа и развитието — TT на тази
    позиция е генотипът, свързан с по-висок ръст, допринасящ приблизително 0.4 см
    на алел в мащабни проучвания.</p>

    <p>Ръстът е приблизително 80% наследствен при добре хранени популации, а вашият
    генетичен сигнал е съобразен с над средния генетичен потенциал за ръст — макар
    реализираният ръст да зависи съществено от храненето, съня и здравето в детството.</p>
    """

def n_cholesterol_bg(r):
    return """
    <p>Генетиката на холестерола ви представя смесена, но в крайна сметка умерена
    картина. Най-важната находка е това, което липсва: носите rs7412 CC — сигналът
    APOE ε2 — свързан с по-нисък LDL и намален сърдечно-съдов риск в сравнение с
    честия генотип ε3/ε3. Това е истински благоприятна находка в най-клинично
    значимия локус за холестерол.</p>

    <p>Предпазливата бележка е, че rs429358 — вторият SNP, необходим за пълно
    определяне на APOE генотипа — не беше на вашия чип. Клиничен тест за APOE
    генотип би изяснил това окончателно и си заслужава предвид последиците му
    както за сърдечно-съдовия, така и за риска от Алцхаймер.</p>

    <p>Извън APOE: rs629301 TT при SORT1/CELSR2 носи две копия на LDL-повишаващия
    алел — този локус умерено повишава LDL. LPA rs10455872 AA е нерисков — не носите
    Lp(a)-повишаващия вариант, което е значима защитна находка. Диетата и физическата
    активност остават подходът на първа линия.</p>
    """

def n_cad_bg(r):
    return """
    <p>Коронарната артериална болест е там, където генетичният ви профил показва
    най-клинично значимото повишение. Локусът '9p21' (CDKN2B-AS1) — най-реплицираният 
    общ вариант за коронарна артериална болест в литературата — се появява два пъти 
    във вашите данни: rs4977574 AG и rs1333049 CG, и двата с по едно рисково копие. 
    Тези варианти са адитивни.</p>

    <p>Локусът '9p21' действа независимо от LDL холестерола — механизмът му включва
    регулиране на клетъчна пролиферация в съдовата гладка мускулатура и възпалителни
    пътища. Това означава, че стандартните липидни изследвания няма да уловят този риск.</p>

    <p>Допълнителни сигнали: rs646776 TT при CELSR2/SORT1 носи две копия на рисковия
    алел. LPL rs264 GG е защитният алел — вариант с повишена функция, който подобрява
    клирънса на триглицеридите — истински контрабалансиращ фактор.</p>

    <p>GWAS показва 25 повишени локуса и PGS от +111, потвърждаващи значимо полигенно
    натоварване по множество CAD пътища. Препоръчително е внимание към пълната
    сърдечно-съдова рискова картина: мониторинг на кръвното налягане, редовни
    липидни панели, избягване на тютюнопушене и физическа активност.</p>
    """

def n_t2d_bg(r):
    return """
    <p>Генетичният ви профил за диабет тип 2 заслужава внимателно четене, защото
    основното число — повишен риск — прикрива важен модел в детайлите.</p>

    <p>Хетерозиготни сте почти във всеки основен T2D локус: TCF7L2 CT, KCNJ11 CT,
    SLC30A8 TC, CDKN2A/B CT, HHEX TC, IGF2BP2 GT, FTO CA — по едно рисково копие
    във всеки. Тази постоянна хетерозиготност в седем независими локуса е определящата
    характеристика на профила ви — означава умерено, а не тежко генетично натоварване.</p>

    <p>TCF7L2 е най-важната находка тук — най-силният и широко реплициран общ T2D
    вариант, действащ чрез Wnt сигналния път за нарушаване функцията на бета-клетките.
    Носителите на риска отговарят особено добре на промяна в начина на живот —
    проучването Diabetes Prevention Program показа, че носителите, преминали през
    промяна в начина на живот, имат същото намаление на честотата на T2D като
    неносителите.</p>

    <p>Практическото послание: генетичният ви профил налага внимание към модифицируеми
    рискови фактори — тегло, физическа активност, гликемично натоварване на диетата —
    но предимно хетерозиготният модел означава, че промяната в начина на живот е
    истински ефективна на това ниво на натоварване.</p>
    """

def n_alzheimer_bg(r):
    return """
    <p>Профилът ви за риск от Алцхаймер съдържа може би най-успокояващата находка
    в целия този доклад. rs7412 CC съответства на алела APOE ε2 — а APOE ε2 е
    най-силният известен защитен вариант срещу късно настъпваща болест на Алцхаймер.
    Носителите на ε2 имат приблизително 50% по-нисък риск от Алцхаймер в сравнение
    с честия генотип ε3/ε3.</p>

    <p>Предпазливата бележка е, че rs429358 не беше на вашия чип, така че не можем
    напълно да изключим смесен генотип ε2/ε4. Дори носителите на ε2/ε4 обаче имат
    намален риск в сравнение с хомозиготите ε4/ε4, а защитният сигнал от ε2 е реален
    и съществен.</p>

    <p>GWAS данните показват 50 повишени локуса и PGS от +171.6, което изглежда
    противоречи на находката за APOE. Важно е да се разбере: GWAS наборът за Алцхаймер
    съдържа много типове проучвания, включително плейотропни изследвания образование-
    Алцхаймер. Статусът на APOE, който е доминиращият фактор в клиничния риск от
    Алцхаймер, тежи по-силно от полигенния резултат тук.</p>

    <p>Цялостната картина за Алцхаймер е истински благоприятна предвид сигнала ε2.
    Най-доказателно обоснованите защитни поведения — поддържане на сърдечно-съдовото
    здраве, редовна аеробна активност, качествен сън и когнитивна ангажираност —
    остават ценни независимо от генотипа.</p>
    """

def n_bmi_bg(r):
    return """
    <p>Генетиката на ИТМ показва умерено натоварване, като ключовата находка е
    хетерозиготността на FTO. rs9939609 AT означава, че носите едно копие на
    рисковия алел на FTO — всеки алел A добавя приблизително 0.4 кг/м² към средния
    ИТМ, поставяйки ви в умерено, а не силно генетично повишение.</p>

    <p>Важен контрабалансиращ фактор: rs2815752 AG при NEGR1 носи защитния алел
    в хетерозиготна форма — свързан с по-нисък ИТМ и частично компенсиращ сигнала
    на FTO.</p>

    <p>Най-важното за вашия FTO генотип е какво показват изследванията за неговата
    модифицируемост. Мета-анализът на Kilpeläinen и колеги от 2011 г. (218 000 участници)
    показа, че носителите на рисковия алел на FTO, които са физически активни, имат
    стойности на ИТМ практически идентични с неносителите. Генетичният ефект на FTO
    върху ИТМ беше почти напълно премахнат от редовна физическа активност.</p>
    """

def n_triglycerides_bg(r):
    return """
    <p>Генетиката на триглицеридите ви показва модел на умерено повишение с една
    важна защитна противотежест. Основният рисков сигнал е APOA5 AG (хетерозиготен) —
    APOA5 е доминиращият локус за триглицериди, а алелът G нарушава ролята на APOA5
    в активирането на липопротеиновата липаза, забавяйки клирънса на триглицеридите.</p>

    <p>APOC3 AG добавя вторичен сигнал, а MTNR1B CG засяга триглицеридите на гладно
    чрез мелатониновата рецепторна сигнализация.</p>

    <p>Ключовата защитна находка е LPL rs328 CC — вариантът S447X с повишена функция.
    Това е истински защитно: алелът C създава по-активна форма на липопротеинова
    липаза, която съществено подобрява клирънса на триглицеридите.</p>

    <p>Практическите диетични последици: вашата хетерозиготност за APOA5 означава,
    че приемът на въглехидрати и алкохол има усилен ефект върху нивата на
    триглицеридите ви. Добавките с омега-3 (2-4 г дневно) са особено ефективни
    при носители на риска на APOA5.</p>
    """

def n_depression_bg(r):
    return """
    <p>Генетиката на депресията ви разказва нюансирана история, изискваща внимателен
    контекст за правилно тълкуване. Заглавната находка — повишен генетичен сигнал
    с 32 GWAS локуса и PGS +71.8 — отразява истинско полигенно натоварване, но
    генетиката на депресията има важни интерпретативни ограничения.</p>

    <p>Най-лично значимите находки са в курираните SNP-и. BDNF rs6265 CT означава,
    че носите едно копие на варианта Val66Met — алелът T (Met) е свързан с намалена
    активност-зависима секреция на BDNF, основния невротрофичен фактор на мозъка.
    BDNF нивата обаче са силно чувствителни към аеробни упражнения — физическата
    активност е един от най-мощните известни стимулатори на BDNF.</p>

    <p>COMT rs4680 GG е профилът "Воин" (Val/Val) — по-високо разграждане на
    допамин в префронталния кортекс, което обикновено означава по-добра устойчивост
    на стрес. За депресията това е по-скоро неутрално до защитно, отколкото рисков
    фактор.</p>

    <p>Общото послание: хетерозиготността BDNF Val66Met е най-интерпретативно
    значимата находка тук — предполага донякъде по-висока биологична чувствителност
    към стрес, но не предопределен резултат. Редовната аеробна активност, качественият
    сън и силната социална връзка имат пряко невробиологично значение за вашия
    конкретен генотип.</p>
    """

def n_longevity_bg(r):
    pgs = r.get("pgs_score", 62.4)
    return f"""
    <p>Генетиката на дълголетието ви показва умерено положителни сигнали, като
    картината с APOE е централна. rs7412 CC съответства на алела APOE ε2 — а ε2
    е последователно свръхпредставен сред столетници в множество независими
    кохортни проучвания.</p>

    <p>Вариантите на CETP добавят истински допълнителен сигнал за дълголетие.
    CETP rs3764814 CT и CETP rs5882 AG сочат към по-висок HDL холестерол — а
    повишеният HDL е последователно свързван с дълголетие в проучвания на
    столетници.</p>

    <p>GWAS показва стабилен полигенен резултат от {pgs:+.1f}. Комбиниран със
    сигнала APOE ε2 и вариантите CETP, цялостната картина на дълголетието е
    умерено благоприятна на генетично ниво.</p>

    <p>Обобщаващата тема на целия ви генетичен доклад е, че съдбата ви не се
    определя от единичен екстремен монoгенен дефект, а от сложна мрежа от умерени
    полигенни предразположения. Тъй като основните ви рискове са напълно
    адресируеми чрез целенасочен начин на живот, реалният ви здравен потенциал
    остава твърдо във ваши ръце.</p>
    """

def n_mthfr_bg(r):
    return """
    <p>Генетиката ви за метаболизъм на фолат и B-витамини е най-клинично полезната
    хранителна находка в този доклад. Носите два варианта на MTHFR едновременно —
    сложна хетерозиготност, по-значима от всеки вариант поотделно.</p>

    <p><strong>MTHFR C677T (rs1801133) GA — хетерозиготен.</strong> Алелът T
    намалява активността на ензима MTHFR с приблизително 35% при хетерозиготи.
    MTHFR е ключовият ензим, превръщащ фолата в активната му форма, използвана
    за рециклиране на хомоцистеин обратно в метионин.</p>

    <p><strong>MTHFR A1298C (rs1801131) GT — хетерозиготен.</strong> В комбинация
    с C677T (сложна хетерозиготност), функционалната ензимна активност може да
    бъде намалена с 50-60%.</p>

    <p>Практическите последици са директни: стандартната фолиева киселина изисква
    превръщане в активен 5-метилТХФ от самия MTHFR — стъпка, която е неефективна
    във вашия случай. Решението е добавка с <strong>метилфолат (5-MTHF)</strong>
    директно, заобикаляйки нарушената стъпка на превръщане. Метилкобаламин вместо
    цианокобаламин е за предпочитане по същата причина.</p>

    <p>Сърдечно-съдовата релевантност: повишеният хомоцистеин е независим рисков
    фактор за коронарна артериална болест и инсулт — области, в които GWAS данните
    ви вече показват повишени сигнали.</p>
    """

def n_heart_failure_bg(r):
    pgs = r.get("pgs_score", 61.4)
    return f"""
    <p>GWAS данните за сърдечна недостатъчност показват 22 повишени локуса с PGS
    от {pgs:+.1f} — най-високият сърдечно-съдов полигенен резултат във вашия профил
    след ИТМ. Важно е да се тълкува внимателно, защото сърдечната недостатъчност
    почти винаги е следствие от други състояния, а не самостоятелно генетично
    заболяване.</p>

    <p>Повечето GWAS сигнали за сърдечна недостатъчност се припокриват с пътищата
    на коронарната артериална болест, хипертонията, диабета и предсърдното мъждене.
    Повишеният ви сигнал вероятно отразява кумулативното генетично натоварване по
    тези пътища, а не пряк миокарден дефект. Най-вероятните движещи фактори във
    вашия конкретен профил са сигналът за CAD при 9p21 и умереното натоварване
    за T2D.</p>

    <p>Клиничното послание не е „изложени сте на риск от сърдечна недостатъчност"
    като отделно състояние, а по-скоро, че сърдечно-съдовото и метаболитното ви
    генетично натоварване сочат към една и съща стратегия за превенция: контрол
    на кръвното налягане, управление на липидите, метаболитно здраве и редовна
    сърдечно-съдова активност.</p>
    """

def n_atrial_fibrillation_bg(r):
    pgs = r.get("pgs_score", 13.1)
    return f"""
    <p>GWAS данните за предсърдно мъждене показват полигенен резултат от {pgs:+.1f}
    с 1 повишен локус от 141 генотипирани. Наследствеността на предсърдното мъждене
    е приблизително 20–30% — по-ниска от повечето сърдечно-съдови състояния, което
    означава, че факторите на околната среда и начина на живот играят необичайно
    доминираща роля в сравнение с генетиката тук.</p>

    <p>Основният повишен сигнал е в областта на PITX2 — най-реплицираният локус
    за предсърдно мъждене в литературата, контролиращ ляво-дясната асиметрия в
    сърдечното развитие. Един повишен локус при умерено съотношение на шансовете
    обаче представлява лек сигнал, а не силна предразположеност.</p>

    <p>По-практическата картина от целия ви профил: генетичното ви натоварване за
    коронарна артериална болест (локус 9p21, PGS +111) и вариантите ви, повишаващи
    триглицеридите, са основните движещи фактори за сърдечен риск. Контролирането
    на тези първични рискове е най-ефективната стратегия за превенция на предсърдно
    мъждене.</p>

    <p><strong>Практически фокус:</strong> мониторинг на кръвното налягане, редовни
    липидни панели, поддържане на здравословно тегло и ограничаване на алкохола —
    който има най-силния остър ефект, провокиращ предсърдно мъждене сред всички
    модифицируеми фактори.</p>
    """

def n_stroke_bg(r):
    pgs = r.get("pgs_score", 31.4)
    return f"""
    <p>Генетиката ви за инсулт показва 9 повишени локуса с PGS от {pgs:+.1f} —
    умерен сигнал, заслужаващ внимание, особено в контекста на по-широкия ви
    сърдечно-съдов профил. Наследствеността на инсулта е приблизително 40%, със
    значително генетично припокриване с коронарната артериална болест, предсърдното
    мъждене и кръвното налягане.</p>

    <p>Най-забележителната находка във вашите GWAS данни за инсулт е rs146092501 CC
    при COL6A3 с OR 12.5 за исхемичен инсулт — необичайно високо съотношение на
    шансовете. Големи стойности на OR при единични локуси в GWAS за инсулт често
    отразяват ефекти от редки варианти или популационно-специфични находки, така
    че това трябва да се тълкува предпазливо.</p>

    <p>Критичният контекст: сложната ви хетерозиготност за MTHFR (C677T + A1298C)
    е пряко релевантна тук. Нарушеният клирънс на хомоцистеин от намалената
    активност на MTHFR е независим рисков фактор за исхемичен инсулт. Това не е
    случайно съвпадение за отбелязване и подминаване — това е реална, приложима
    находка с известна, нискорискова интервенция: добавка с метилфолат за
    нормализиране на нивата на хомоцистеин.</p>
    """

def n_blood_pressure_bg(r):
    pgs = r.get("pgs_score", 0.0)
    return f"""
    <p>Генетиката ви за кръвно налягане показва полигенен резултат от {pgs:+.1f}.
    Регулирането на кръвното налягане се управлява от множество физиологични пътища,
    включително бъбречна обработка на натрий, съдов тонус и системата
    ренин-ангиотензин-алдостерон.</p>

    <p>Докато полигенните резултати предоставят базова вероятностна картина,
    реалното кръвно налягане се модулира силно от модифицируеми фактори като
    съотношението натрий-калий в приема, сърдечно-съдовата активност, управлението
    на стреса и метаболитното здраве.</p>
    """

def n_gout_bg(r):
    pgs = r.get("pgs_score", 24.2)
    return f"""
    <p>Генетиката ви за подагра показва 8 повишени локуса с PGS от {pgs:+.1f}.
    Подаграта се причинява от хиперурикемия — пикочна киселина, кристализираща
    в ставите — и има наследственост от 35–60% с добре изяснена генетична
    архитектура. Доминиращите локуси във вашите данни са SLC2A9 и ABCG2 —
    двата основни транспортера на пикочна киселина.</p>

    <p>Вариантите на SLC2A9 засягат бъбречната реабсорбция на урат — рисковите
    алели намаляват отделянето на урат, позволявайки нивата да се натрупват.
    ABCG2 засяга чревната секреция на урат и е особено свързан с ранно
    настъпваща подагра при популации с висок прием на пурини.</p>

    <p>Диетичното взаимодействие е сред най-силните ефекти ген-среда в целия ви
    профил. Фруктозата (включително плодов сок и царевичен сироп с високо
    съдържание на фруктоза) е най-мощният хранителен фактор, повишаващ пикочната
    киселина — дори повече от пурините в месото — тъй като метаболизмът на
    фруктозата генерира пикочна киселина като директен страничен продукт.</p>

    <p><strong>Практически фокус:</strong> ограничаване на напитки с фруктоза,
    умереност в приема на алкохол (особено бира), адекватна хидратация и
    поддържане на здравословно тегло. Серумната пикочна киселина е евтина за
    изследване и дава директна мярка, правеща генетичното заключение приложимо.</p>
    """

def n_chronic_kidney_disease_bg(r):
    pgs = r.get("pgs_score", 18.6)
    return f"""
    <p>Генетиката ви за хронично бъбречно заболяване показва 7 повишени локуса
    с PGS от {pgs:+.1f}. Наследствеността на ХБЗ е приблизително 45%, като
    доминиращите генетични сигнали се групират около регулирането на гломерулната
    филтрация и бъбречния тубулен транспорт.</p>

    <p>Най-релевантната находка в контекста на цялостния ви профил е механичното
    припокриване между генетичния ви сигнал за ХБЗ и другите ви рискови фактори.
    Генетичното ви натоварване за T2D и сигналите ви, свързани с хипертония,
    са основните известни причини за ХБЗ на популационно ниво — диабетната
    нефропатия и хипертензивната нефросклероза съставляват приблизително 60%
    от всички случаи на ХБЗ.</p>

    <p><strong>Връзката с MTHFR:</strong> повишаването на хомоцистеина от
    сложната ви хетерозиготност MTHFR C677T + A1298C има документирани
    нефротоксични ефекти — повишеният хомоцистеин уврежда гломерулните
    ендотелни клетки чрез механизми, сходни с артериалните му ефекти. Отново,
    добавката с метилфолат адресира множество последващи рискове едновременно.</p>
    """

def n_vitamin_d_bg(r):
    return """
    <p>Генетиката ви за витамин D показва нюансирана картина, надхвърляща
    „лекото" полигенно означение. Докато общият GWAS резултат е само умерено
    повишен, конкретните ви варианти разкриват неефективности на два критични
    етапа: транспорт и клетъчно усвояване.</p>

    <p><strong>Етап на транспорт (ген GC):</strong> Носите rs7041 CA (хетерозиготен)
    и rs4588 GG. Тази комбинация произвежда смес от свързващи витамин D протеини,
    водеща до умерено намалена ефективност в доставянето на витамин D до тъканите.</p>

    <p><strong>Етап на рецептора (ген VDR):</strong> По-значими са вариантите ви
    VDR — rs731236 AA (TaqI) и rs7975232 CC (ApaI). Това са добре проучени маркери,
    свързани с намалена чувствителност на рецептора за витамин D. Това означава,
    че дори когато витамин D достигне клетките ви, рецепторите, които трябва да
    задействат абсорбцията на калций и минерализацията на костите, реагират
    по-малко ефективно.</p>

    <p>Комбинираният ефект създава двуетапно „намаляване на обема" на активността
    на витамин D. Не сте неспособни да обработвате витамин D, но имате по-висока
    физиологична нужда, за да постигнете същото ниво на абсорбция на калций като
    някой с по-ефективна генетика.</p>

    <p><strong>Практически последици:</strong> стремете се към по-високи серумни
    нива на витамин D (в идеалния случай 50-70 нг/мл). Оптимизирането на кофактори
    е от решаващо значение: <strong>Магнезий</strong> (300-400 мг/ден) и
    <strong>Витамин K2 (MK-7)</strong> (100-200 мкг/ден). Редовно кръвно изследване
    (25(OH)D, калций, PTH) се препоръчва за фино настройване на нивата ви.</p>
    """

def n_parkinson_bg(r):
    pgs = r.get("pgs_score", 27.9)
    return f"""
    <p>Генетиката ви за болестта на Паркинсон показва 9 повишени локуса с PGS
    от {pgs:+.1f}. Наследствеността на Паркинсон е приблизително 27% за честите
    варианти — по-ниска от повечето състояния в този доклад, което означава, че
    факторите на околната среда (излагане на пестициди, травма на главата,
    чревен микробиом) играят пропорционално по-голяма роля от генетиката тук.</p>

    <p>Ключовите локуси в повишения ви набор включват варианти близо до SNCA
    (алфа-синуклеин — протеинът, образуващ телца на Леви, определящата
    патологична характеристика на болестта), LRRK2 (най-честата генетична
    причина за фамилен Паркинсон) и варианти, съседни на GBA.</p>

    <p>Най-приложимата защитна находка от литературата: редовната аеробна
    активност намалява риска от Паркинсон с 30–40% в множество мащабни
    проспективни проучвания, като този ефект е особено изразен при носители
    на варианти в локуса SNCA. Приемът на кафе (който метаболизирате с
    междинна скорост чрез CYP1A2) има добре реплицирана обратна връзка с
    риска от Паркинсон.</p>
    """

def n_adhd_bg(r):
    pgs = r.get("pgs_score", 10.4)
    return f"""
    <p>Генетиката ви за СДВХ показва 2 повишени локуса с PGS от {pgs:+.1f}.
    Наследствеността на СДВХ е приблизително 70–80%, което го прави едно от
    най-наследствените психиатрични състояния — но полигенните резултати за
    СДВХ понастоящем обясняват само 5–10% от вариацията, което означава, че
    генетичната архитектура е силно сложна.</p>

    <p>По-интерпретативно значимо във вашия профил е сближаването на няколко
    генетични сигнала, които заедно описват профил с повишен допамин и висока
    възбудимост. Вашият COMT GG (Val/Val, "Воин") произвежда по-високо
    разграждане на допамин в префронталния кортекс — профил, свързан с по-добро
    представяне под стрес, но потенциално по-ниско базово внимание в среди с
    ниска стимулация.</p>
    """

def n_autism_bg(r):
    pgs = r.get("pgs_score", 8.2)
    return f"""
    <p>Генетиката ви за аутистичен спектър показва 4 повишени локуса с PGS от
    {pgs:+.1f}. Наследствеността на аутизма е приблизително 80%, но генетичната
    архитектура е необичайна: значителна част от риска идва от редки de novo
    мутации, които не се улавят от GWAS чипове.</p>

    <p>Повишените локуси във вашите данни включват варианти близо до MACROD2 и
    KMT2E — и двата свързани с ремоделиране на хроматина и регулиране на
    синаптични гени. Най-важната интерпретативна бележка: генетичните варианти
    за аутизъм на субклинично полигенно ниво значително се припокриват с черти,
    свързани със систематичен, ориентиран към детайли когнитивен стил и силни
    страни в разпознаването на модели.</p>
    """

def n_bipolar_disorder_bg(r):
    pgs = r.get("pgs_score", 16.7)
    return f"""
    <p>Генетиката ви за биполярно разстройство показва 7 повишени локуса с PGS
    от {pgs:+.1f}. Наследствеността на биполярното разстройство е приблизително
    70–80% и, важно, споделя значително генетично припокриване с шизофренията
    и голямата депресия.</p>

    <p>Най-реплицираните локуси за биполярно разстройство във вашия повишен
    набор включват варианти близо до CACNA1C (калциев канал, най-реплицираният
    ген за биполярно разстройство), ANK3 и NCAN — представляващи истински
    биологични сигнали в веригите за регулиране на настроението.</p>

    <p>Установените защитни фактори са добре доказани: редовността на съня е
    единственият най-мощен стабилизатор на настроението, наличен без рецепта —
    нередовният сън е основният екологичен тригер за епизоди на настроение
    дори при клинично диагностицирани лица.</p>
    """

def n_schizophrenia_bg(r):
    return """
    <p>GWAS сигналът за шизофрения заслужава внимателна контекстуализация. Вашият
    PGS от +125.2 и 29 повишени локуса звучат тревожно, но това изисква две важни
    корекции преди тълкуване.</p>

    <p>Първо, полигенните резултати за риск от шизофрения имат много слаба
    индивидуална предиктивна стойност. Дори в най-високия дециел на PGS в общата
    популация, доживотната честота на шизофрения остава около 3-4% — в сравнение
    с ~1% популационна база. Резултатът разграничава статистически групи, не
    индивиди.</p>

    <p>Второ, конкретните варианти, движещи повишения ви резултат, включват
    няколко с много високи съотношения на шансовете от малки проучвания. Големи
    OR стойности в GWAS почти винаги отразяват или популационно-специфични
    ефекти, или малки размери на извадката с завишени оценки.</p>

    <p>Най-значимият биологичен сигнал тук е HLA/MHC компонентът — много рискови
    варианти за шизофрения се групират в основния комплекс за тъканна съвместимост,
    отразявайки добре установеното участие на имунната система. Това споделено
    генетично устройство с имунни състояния (носите също повишени сигнали за
    лупус, ревматоиден артрит и възпалително чревно заболяване) предполага
    истинска биологична тема на чувствителност на имунния път, а не класически
    психиатричен риск изолирано.</p>
    """

def n_sleep_duration_bg(r):
    pgs = r.get("pgs_score", 7.8)
    return f"""
    <p>Генетиката ви за продължителност на съня показва 4 повишени локуса с PGS
    от {pgs:+.1f} — лек, но реален сигнал. Наследствеността на продължителността
    на съня е приблизително 30–40%, като вариантите на циркадните гени играят
    основната роля.</p>

    <p>Четенето на генетиката ви за сън в контекста на пълния ви профил добавя
    важни пластове. Вашата хетерозиготност BDNF CT (Val66Met) засяга качеството
    на съня независимо — намалената секреция на BDNF нарушава дълбочината на
    бавновълновия сън. Вашият COMT GG ("Воин") произвежда по-нисък префронтален
    допамин, а междинният ви метаболизъм на кофеин чрез CYP1A2 означава, че
    следобедният кофеин остава значително в прозореца за вечерен сън.</p>

    <p>Тези три фактора формират последователна картина за оптимизиране на съня:
    приоритизирайте постоянството на съня, спрете кофеина до обяд, максимизирайте
    качеството на дълбокия сън чрез упражнения и поддържайте вечери с ниска
    осветеност.</p>
    """

def n_melanoma_bg(r):
    pgs = r.get("pgs_score", 14.1)
    return f"""
    <p>Генетиката ви за меланом показва 6 повишени локуса с PGS от {pgs:+.1f}.
    Меланомът е приблизително 50% наследствен за честите варианти, но ключовото
    прозрение тук е, че генетичният ви профил създава многопластова рискова
    картина, в която пигментационната генетика, генетиката на UV чувствителност
    и GWAS сигналите за меланом се сближават в едно и също приложимо заключение.</p>

    <p>Повишените GWAS локуси включват IRF4 CT — вашият хетерозиготен генотип
    IRF4 се появява както в анализа ви на пигментация, така и в GWAS за меланом,
    защото IRF4 действително регулира биологията на меланоцитите и предразположението
    към меланом едновременно. TYR варианти (включително хетерозиготния ви вариант
    на тирозиназата) допълват картината — намалената тирозиназна активност едновременно
    просветлява кожата и намалява UV-защитния еумеланинов отговор.</p>

    <p>Четейки в целия ви профил: намаленото производство на меланин, изсветленият
    базов тон на кожата, хаплотипната комбинация за сини очи и GWAS сигналът за
    меланом създават последователен портрет на геном, оптимизиран за северноевропейски 
    условия с ниско UV лъчение, но сега функциониращ в свят с по-високо UV ниво. 
    Меланомът, открит на Stage I, има над 95% петгодишна преживяемост. SPF50, 
    прилаган последователно, годишни прегледи на кожата от дерматолог и търсене 
    на сянка между 11 и 15 часа са истински оправдани от специфичната ви комбинация 
    от генетични сигнали.</p>
    """

def n_breast_cancer_bg(r):
    pgs = r.get("pgs_score", 80.9)
    return f"""
    <p>Генетиката ви за рак на гърдата показва 18 повишени локуса с PGS от
    {pgs:+.1f} — най-високият полигенен резултат за рак във вашия профил. Важни
    интерпретативни уговорки обаче се прилагат, преди това число да бъде прието
    буквално.</p>

    <p>Първо, някои от най-високите съотношения на шансовете в повишените ви
    локуси почти сигурно отразяват специфични за популацията или редки варианти,
    а не общоприложим риск. По-солидно реплицираните сигнали са близо до TP53
    (главният туморен супресор на генома) и ESR1 (естрогенен рецептор алфа),
    пряко релевантни за хормон-чувствителна патофизиология на рака на гърдата.</p>

    <p>Второ, най-клинично значимите варианти за рак на гърдата — загуба на
    функция на BRCA1 и BRCA2 — са редки, с висока пенетрантност и не се улавят
    от потребителски GWAS чипове. Ако съществува фамилна история на рак на
    гърдата или яйчниците, клиничното генетично тестване за BRCA1/2 чрез вашия
    личен лекар предоставя много по-приложима информация.</p>

    <p><strong>Практическа препоръка:</strong> стандартен мамографски скрининг
    от 40-годишна възраст (или по-рано при фамилна история), поддържане на
    здравословно тегло и умереност в приема на алкохол — който повишава нивата
    на естроген и има най-силната връзка с рака на гърдата сред всички
    модифицируеми фактори.</p>
    """

def n_prostate_cancer_bg(r):
    pgs = r.get("pgs_score", 61.2)
    return f"""
    <p>Генетиката ви за рак на простатата показва 12 повишени локуса с PGS от
    {pgs:+.1f}. Ракът на простатата е най-наследственият чест рак при приблизително
    57%, което прави генетичния риск истински информативен тук по начин, който
    не е приложим за по-малко наследствени видове рак.</p>

    <p>Доминиращият сигнал във вашите данни е локусът 8q24 — регион без анотирани
    протеин-кодиращи гени, който въпреки това съдържа най-силния известен общ
    регион на предразположение към рак на простатата. rs17632542 TT близо до KLK3
    (самия ген за PSA) е клинично забележителен: вариантите на KLK3 засягат нивата
    на PSA независимо от рака на простатата, което означава, че вашите PSA
    показания може да се държат различно от популационните средни стойности.</p>

    <p><strong>Практическа препоръка:</strong> обсъждане на PSA с уролог от 45-50
    годишна възраст, отбелязвайки ефекта на генотипа KLK3 върху тълкуването на
    базовия PSA. Диета, богата на ликопен (домати, диня), има най-силната
    епидемиологична подкрепа за превенция на рак на простатата сред хранителните
    фактори.</p>
    """

def n_colorectal_cancer_bg(r):
    pgs = r.get("pgs_score", 55.1)
    return f"""
    <p>Генетиката ви за колоректален рак показва 10 повишени локуса с PGS от
    {pgs:+.1f}. Наследствеността на колоректалния рак е приблизително 35% за
    честите варианти, което прави факторите на начина на живот пропорционално
    по-влиятелни тук, отколкото при по-наследствени видове рак.</p>

    <p>Няколко повишени локуса показват много високи съотношения на шансовете,
    които почти сигурно представляват популационно-специфични или редки варианти,
    а не широкоприложим общ риск. По-солидно реплицираните сигнали във вашите
    данни включват варианти близо до MGAT4A (участващ в N-гликозилацията на
    чревните муцини — защитният слой слуз, покриващ дебелото черво) и RASGRF2.</p>

    <p>Вашата генетика за възпалително чревно заболяване е пряко релевантна тук:
    хроничното чревно възпаление е основен път към колоректален рак, а повишените
    ви сигнали за IBD, болест на Крон и колоректален рак споделят припокриващи
    се биологични механизми в целостта на чревния епител.</p>

    <p>Колоректалният рак е един от най-модифицируемите от начина на живот видове
    рак: хранителни фибри, редовна физическа активност (30% намаление на риска),
    ограничено червено и преработено месо и колоноскопски скрининг от 45-годишна
    възраст. Аспиринът е показал защитни ефекти при генетично високорискови лица.</p>
    """

def n_lung_cancer_bg(r):
    pgs = r.get("pgs_score", 31.6)
    return f"""
    <p>Генетиката ви за рак на белия дроб показва 13 повишени локуса с PGS от
    {pgs:+.1f}. Критичният интерпретативен контекст за генетиката на рака на
    белия дроб е, че статусът на тютюнопушене напълно доминира генетичния риск —
    генетичните варианти модифицират риска върху излагането на тютюнопушене, но
    при непушач абсолютният риск от рак на белия дроб от тези варианти е много
    нисък независимо от полигенния резултат.</p>

    <p>Доминиращият сигнал във вашите данни е при CHEK2 — ген за реакция на
    ДНК увреждане, функциониращ надолу по веригата от BRCA1 и ATM. Варианти с
    загуба на функция на CHEK2 са свързани с повишен риск в множество видове рак.</p>

    <p>Последователната картина в генетиката ви за рак: рак на гърдата, рак на
    белия дроб и колоректален рак показват сигнали в пътищата за реакция на ДНК
    увреждане и клетъчни контролни точки. За непушач, абсолютният риск от тези
    варианти е умерен. За всеки, който е пушил, генетичните варианти умножават
    вече високо екологично излагане, правейки отказването от тютюнопушенето
    интервенцията с най-голямо въздействие.</p>
    """

def n_bladder_cancer_bg(r):
    pgs = r.get("pgs_score", 13.0)
    return f"""
    <p>Генетиката ви за рак на пикочния мехур показва 3 повишени локуса с PGS
    от {pgs:+.1f} — лек сигнал. Ракът на пикочния мехур е приблизително 50%
    наследствен за честите варианти, но тютюнопушенето е единственият доминиращ
    рисков фактор (съставляващ ~50% от всички случаи) чрез концентрацията на
    канцерогени в урината, влизаща в директен контакт с епитела на пикочния
    мехур.</p>

    <p>Повишените локуси във вашите данни включват варианти близо до PSCA и MYC
    на 8q24 (същият регулаторен регион, повишен и във вашите данни за рак на
    простатата), както и вариант близо до NAT2. NAT2 е особено релевантен: той
    кодира ензим, метаболизиращ ароматни амини, намиращи се в тютюневия дим и
    боя за коса.</p>

    <p>За непушач без значителни химически излагания, абсолютният риск от рак
    на пикочния мехур от този генетичен профил е нисък. Адекватната хидратация
    (която разрежда уринарните канцерогени) е най-практичната защитна мярка.</p>
    """

def n_lupus_bg(r):
    pgs = r.get("pgs_score", 49.4)
    return f"""
    <p>Генетиката ви за лупус показва 32 повишени локуса с PGS от {pgs:+.1f} —
    един от най-силните имунни сигнали във вашия профил. Наследствеността на
    лупус (системен лупус еритематозус) е приблизително 44%, със силен HLA
    компонент и няколко добре реплицирани не-HLA локуса.</p>

    <p>Основната генетична тема във вашите данни за лупус е дисрегулация на
    интерферонния път. Вариантите на STAT4 и IRF5, заедно с множество варианти
    на комплементния път, колективно описват геном, предразположен към прекомерно
    производство на интерферон тип I — така нареченият „интерферонен подпис",
    който предхожда и движи автоимунното увреждане на тъканите.</p>

    <p>Свързвайки това с по-широкия ви имунен профил: същата дисрегулация на
    интерферонния път, лежаща в основата на генетичния риск от лупус, се
    припокрива с вашите сигнали за множествена склероза и ревматоиден артрит.
    TYK2 GG, който носите хомозиготно, е плейотропен вариант, засягащ JAK-STAT
    сигнализацията, появяващ се в наборите данни за лупус, RA и псориазис —
    единичен генен вариант, едновременно усилващ риска при три автоимунни
    състояния.</p>

    <p>UV светлината е особено релевантна за генетично предразположени към лупус
    лица: UV-B директно активира интерферонния път в кожата, което може да
    провокира системни автоимунни изостряния. Оптимизирането на витамин D е
    най-доказателно обоснованият фактор на средата, модифициращ риска от лупус.</p>
    """

def n_rheumatoid_arthritis_bg(r):
    pgs = r.get("pgs_score", 40.4)
    return f"""
    <p>Генетиката ви за ревматоиден артрит показва 10 повишени локуса с PGS от
    {pgs:+.1f}. Наследствеността на RA е приблизително 60%, като алелите
    HLA-DRB1 съставляват приблизително 30% от генетичната вариация — най-големият
    единичен генетичен принос за което и да е често автоимунно заболяване.</p>

    <p>Отвъд HLA, повишените ви локуси включват PTPN22 (основен регулатор на
    T-клетъчна и B-клетъчна сигнализация, чийто рисков вариант е най-силният
    не-HLA локус за RA), STAT4 (споделен с вашия сигнал за лупус) и PAD14
    (ензимът, който цитрулинира протеини, създавайки анти-CCP антителата,
    определящи серопозитивен RA).</p>

    <p>TYK2 GG се появява отново тук — вашият хомозиготен вариант TYK2 е единичната
    генетична находка, най-последователно споделена в повишените ви сигнали за
    лупус, RA, псориазис и болест на Крон. Той е молекулярният общ знаменател
    на автоимунния ви генетичен профил.</p>

    <p>Сутрешната скованост на ставите, продължаваща повече от 30 минути, е
    класическият продромален симптом, заслужаващ наблюдение. Омега-3 мастните
    киселини имат най-силната доказателна база от всяка хранителна интервенция
    за намаляване на риска от RA.</p>
    """

def n_inflammatory_bowel_bg(r):
    pgs = r.get("pgs_score", 56.6)
    return f"""
    <p>Генетиката ви за възпалително чревно заболяване показва 18 повишени
    локуса с PGS от {pgs:+.1f} — най-високият имунен сигнал във вашия профил.
    Наследствеността на IBD е приблизително 75% за болест на Крон и 70% за
    улцерозен колит, правейки това едно от най-генетично определените сложни
    заболявания.</p>

    <p>Доминиращите локуси в повишения ви набор са регионът NOD2 (първият и
    най-реплициран IBD ген, участващ в бактериално разпознаване в чревния
    епител), ATG16L1 (автофагия) и оста IL23R/IL17. Тези три пътя — бактериално
    усещане, автофагия и Th17 възпаление — са механичното ядро на IBD
    патофизиологията.</p>

    <p>Припокриващите се сигнали в IBD, болест на Крон и колоректален рак
    формират последователен биологичен разказ: нарушена бариерна функция на
    епитела позволява бактериална транслокация, а устойчивото чревно възпаление
    създава средата за епителна трансформация.</p>

    <p>Чревният микробиом е основният интерфейс на средата с генетиката ви за
    IBD. Интервенции, насърчаващи разнообразието — хранителни фибри от
    разнообразни растителни източници, ферментирали храни, избягване на
    ненужни антибиотици — пряко подпомагат микробната среда.</p>
    """

def n_crohn_disease_bg(r):
    pgs = r.get("pgs_score", 48.6)
    return f"""
    <p>Генетиката ви за болест на Крон показва 13 повишени локуса с PGS от
    {pgs:+.1f}. Болестта на Крон е по-генетично сложната от двете основни
    форми на IBD — засягаща която и да е част от стомашно-чревния тракт —
    и има по-висока наследственост (~75%) от улцерозния колит (~70%).</p>

    <p>Доминиращият сигнал в данните ви за болест на Крон е IL23R, появяващ се
    многократно в повишените ви локуси. IL-23 е основният цитокин, движещ
    диференциацията на Th17 клетки — възпалителният път, причиняващ образуване
    на грануломи. TYK2 GG, вашият хомозиготен вариант, пряко засяга ефективността
    на IL-23 сигнализацията.</p>

    <p>Тази находка за TYK2 има директна фармакологична импликация: инхибиторите
    на TYK2 представляват нов клас целенасочена терапия, специфично разработена
    за автоимунни заболявания, движени от TYK2 пътя. Ако симптоми, подобни на
    болест на Крон, някога се развият, вашият генотип TYK2 GG би ви направил
    особено силен кандидат за този механизъм на действие.</p>

    <p>Приложими са същите диетични и препоръки за начин на живот като за IBD
    като цяло — с особен акцент върху управлението на стреса, тъй като оста
    черво-мозък е особено релевантна при болестта на Крон.</p>
    """

def n_multiple_sclerosis_bg(r):
    pgs = r.get("pgs_score", 28.1)
    return f"""
    <p>Генетиката ви за множествена склероза показва 5 повишени локуса с PGS
    от {pgs:+.1f}. Наследствеността на MS е приблизително 50%, като HLA
    регионът на хромозома 6 допринася за приблизително 20–30% от генетичната
    вариация сам по себе си.</p>

    <p>Доминиращият рисков алел за MS е HLA-DRB1*15:01, не се изследва директно
    от потребителски чипове, но присъствието му може частично да се изведе от
    околните варианти. Повишените ви локуси включват сигнали в HLA региона,
    заедно с варианти близо до CLEC16A и IL7R.</p>

    <p>Четенето на сигнала ви за MS в контекста на пълния ви имунен профил е
    важно. Повишените ви сигнали за лупус, ревматоиден артрит, IBD, MS и
    псориазис колективно отразяват истинска тема на повишена имунна реактивност,
    особено в T-клетъчно медиираната автоимунна сигнализация. Намесата е
    идентична във всички тях: оптимизиране на витамин D (вашите VDR варианти
    правят това особено релевантно), добавка с омега-3 и поддържане на
    разнообразие на чревния микробиом.</p>
    """

def n_psoriasis_bg(r):
    pgs = r.get("pgs_score", 32.0)
    return f"""
    <p>Генетиката ви за псориазис показва 13 повишени локуса с PGS от {pgs:+.1f}.
    Наследствеността на псориазиса е 60–70%, като HLA-C*06:02 е основният
    рисков алел.</p>

    <p>Механичното ядро на сигнала ви за псориазис е оста IL-23/IL-17 — същият
    път, доминиращ в данните ви за болест на Крон. TYK2 GG е ключовият елемент:
    TYK2 фосфорилира STAT3 в отговор на IL-23, движейки хиперпролиферацията на
    кератиноцитите (определящата характеристика на псориатичните плаки) и
    системното възпаление.</p>

    <p>Псориазисът и болестта на Крон съвпадат с честота далеч над случайната,
    а генетиката ви обяснява точно защо: носите усилващи варианти в споделения
    път IL-23/TYK2, движещ и двете състояния едновременно. Биологични терапии,
    насочени към IL-23 или IL-17, са ефективни и за двете състояния — вашият
    генотип TYK2 GG би ви направил особено силен отговарящ на TYK2 инхибитори.</p>

    <p>Екологични тригери, активиращи IL-23 пътя: стрептококови гърлени инфекции,
    кожна травма, определени лекарства и психологически стрес — осъзнаването
    на тези тригери е особено ценно предвид генетичното ви натоварване.</p>
    """

def n_asthma_bg(r):
    pgs = r.get("pgs_score", 40.4)
    return f"""
    <p>Генетиката ви за астма показва 14 повишени локуса с PGS от {pgs:+.1f} —
    един от по-високите сигнали в имунната категория. Наследствеността на
    астмата е 60–80%, със силно генетично припокриване с екзема и алергичен
    ринит, отразяващо споделения им Th2-поляризиран имунен път.</p>

    <p>Доминиращите сигнали в повишените ви локуси включват варианти близо до
    IL33 (епителен цитокин-алармин, който инициира Th2 отговори), ORMDL3/GSDMB
    на хромозома 17q21 (най-силният и реплициран локус за астма) и IL1RL1/IL18R1
    (рецепторният комплекс на IL-33).</p>

    <p>Сближаването на сигнала ви за астма с по-широките имунни профили е
    последователно: повишените ви сигнали в множество автоимунни състояния
    предполагат общо реактивна имунна система. Вашата генетика за витамин D е
    пряко релевантна тук: VDR варианти, намаляващи чувствителността на рецептора,
    са свързани с повишена тежест на астмата — витамин D силно потиска Th2
    поляризацията.</p>
    """

def n_caffeine_metabolism_bg(r):
    pgs = r.get("pgs_score", 5.5)
    return f"""
    <p>Генетиката ви за метаболизъм на кофеин показва 3 повишени локуса с PGS
    от {pgs:+.1f}. Основният сигнал е при CYP2A6, ензим, който основно
    метаболизира никотин, но допринася и за клирънса на кофеина като вторичен
    субстрат.</p>

    <p>По-клинично релевантната генетика на кофеина идва от вашите
    фармакогеномни данни: хетерозиготният ви генотип при CYP1A2 ви поставя в
    категорията на междинните метаболизатори на кофеин. CYP1A2 обработва
    приблизително 95% от клирънса на кофеина — основният определящ фактор дали
    сте бърз или бавен метаболизатор.</p>

    <p>Практическата фармакокинетика за вашия профил: сутрешно еспресо в 8 часа
    е до голяма степен изчистено до 14-15 часа. Следобеден кафе в 14 часа все
    още има значително количество кофеин при лягане в 21-22 часа. Това се
    свързва пряко с генетиката ви за сън и профила ви COMT: остатъчният вечерен
    кофеин усилва възбудата по време на прозореца за настъпване на съня.</p>

    <p>Защитните връзки на кофеина с болестта на Паркинсон и когнитивната
    функция са релевантни за неврологичния ви профил. При вашата междинна скорост
    на метаболизъм, две чаши преди обяд улавят тези ползи без нарушаване на съня.</p>
    """

def n_alcohol_consumption_bg(r):
    pgs = r.get("pgs_score", 37.8)
    return f"""
    <p>Генетиката ви за консумация на алкохол показва 10 повишени локуса с PGS
    от {pgs:+.1f}. Заглавната находка — вариант при ADH1B с изключително високо
    съотношение на шансовете — е най-впечатляващото индивидуално съотношение в целия ви
    доклад и изисква внимателно тълкуване.</p>

    <p>ADH1B кодира алкохол дехидрогеназа 1B, основният ензим, превръщащ
    етанола в ацеталдехид в черния дроб. По-бавната активност на ADH1B означава,
    че алкохолът се превръща в ацеталдехид по-бавно, намалявайки аверзивния
    ефект на зачервяване, който възпира пиенето при популации с бърз метаболизъм.
    Високото съотношение на шансовете (OR) отразява популационно ниво на вариация в
    количеството пиене, а не пряк здравен риск.</p>

    <p>Свързвайки това с останалата ви генетика се създава клинично значима картина.
    Вашата генетика за триглицериди означава, че алкохолът има усилен ефект
    върху нивата на триглицеридите ви. Генетичното ви натоварване за IBD и
    болест на Крон означава, че алкохолът директно уврежда чревния епител в
    контекст, където чревната ви бариерна генетика вече е по-малко устойчива.</p>

    <p>Нищо от това не налага въздържание — генетиката описва тенденции и
    чувствителности, не съдби. Но сближаването в множество биологични пътища
    предполага, че за вашия конкретен генетичен профил, съотношението
    риск-полза за редовна консумация на алкохол е по-малко благоприятно,
    отколкото за средния човек. Умерен прием и избягване на алкохол специално
    с високопуринови храни (предвид сигнала ви за подагра) представлява
    информиран от генотипа подход.</p>
    """

def n_lactase_persistence_bg(r):
    return """
    <p>Вашият генотип за лактазна персистентност е хетерозиготен при
    ключовия локус LCT/MCM6 — производният, персистентност-предаващ алел е
    налице в едно копие, което е достатъчно за пълно производство на ензима
    лактаза в зряла възраст. Вие сте толерантни към лактоза.</p>

    <p>Този вариант възниква преди приблизително 7500–10 000 години в
    Понто-Каспийската степ или Северна Европа и се разпространява драматично
    с култури на отглеждане на добитък поради значителното калорийно и
    хранително предимство на смилането на прясно мляко. Това е един от
    най-изследваните примери за скорошна положителна селекция в човешкия геном.</p>

    <p>Вашият хетерозиготен статус е съобразен с профила ви на произход:
    хомозиготна персистентност (от двете родителски линии) е най-честа в
    популации с най-дългата традиция на отглеждане на добитък. Хетерозиготността
    е типична за популации в южния/източния край на градиента на лактазна
    персистентност — точно където се намира профилът на източнобалкански
    произход.</p>

    <p>Функционално, хетерозиготите произвеждат достатъчно лактаза за комфортно
    храносмилане на млечни продукти през целия живот, макар производството на
    ензима да може да бъде донякъде по-ниско, отколкото при хомозиготите.
    Пълномасленото мляко се смила без проблем; много големи количества обезмаслено
    мляко на празен стомах може понякога да произведат леки симптоми при някои
    хетерозиготни лица, но това е изключение, а не правило.</p>
    """

def n_pharmacogenomics_bg(r):
    return """
    <p>Вашите фармакогеномни GWAS данни улавят повишени локуси, включително
    варианти при JAK2, ZNF646 и CPVL. Много високото съотношение на шансовете
    при варианта ZNF646 вероятно отразява популационно-специфичен или рядък
    вариантен ефект, а не широко приложим сигнал за лекарствен отговор.</p>

    <p>Най-клинично приложимите фармакогеномни варианти — CYP2D6, CYP2C19,
    CYP2C9, TPMT, DPYD — не бяха уловени в този GWAS набор данни. Тези са
    вариантите, които пряко засягат метаболизма на често предписвани лекарства,
    включително антидепресанти, антипсихотици, разредители на кръвта и
    химиотерапевтични средства.</p>

    <p>Ако започвате нов медикамент — особено антидепресанти, антитромбоцитни
    лекарства (клопидогрел) или обезболяващи, включващи кодеин или трамадол —
    фармакогеномен панел от клинична генетична служба си заслужава да се обсъди
    с вашия лекар, предписващ лечението. Тези панели могат да предотвратят
    неефективно дозиране или нежелани реакции, които иначе биха се открили
    само чрез проби и грешки.</p>
    """

# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY DICTIONARIES & MAPPINGS
# ─────────────────────────────────────────────────────────────────────────────
BESPOKE = {
    # Appearance
    "eye_color":                n_eye_color,
    "hair_color":               n_hair_color,
    "skin_tone":                n_skin_tone,
    "hair_loss":                n_hair_loss,
    "height":                   n_height,
    "freckles":                 n_freckles,
    "earlobe_type":             n_earlobe_type,
    "bitter_taste":             n_bitter_taste,
    "facial_hair":              n_facial_hair,

    # Cardiometabolic / Lipids
    "cholesterol":              n_cholesterol,
    "cad":                      n_cad,
    "triglycerides":            n_triglycerides,
    "atrial_fibrillation":      n_atrial_fibrillation,
    "stroke":                   n_stroke,
    "heart_failure":            n_heart_failure,
    "blood_pressure":           n_blood_pressure,
    "mthfr":                    n_mthfr,
    "t2d":                      n_t2d,
    "bmi":                      n_bmi,
    "obesity_bmi":              n_obesity_bmi,
    "gout":                     n_gout,
    "chronic_kidney_disease":   n_chronic_kidney_disease,
    "thyroid_function":         n_thyroid_function,
    "vitamin_d":                n_vitamin_d,
    "hdl_cholesterol":          n_hdl_cholesterol,
    "ldl_cholesterol":          n_ldl_cholesterol,
    "metabolic_syndrome":       n_metabolic_syndrome,
    "fasting_glucose":          n_fasting_glucose,
    "insulin_resistance":       n_insulin_resistance,

    # Neurology / Psychiatry / Sleep
    "intelligence":             n_intelligence,
    "alzheimer":                n_alzheimer,
    "depression":               n_depression,
    "adhd":                     n_adhd,
    "autism":                   n_autism,
    "bipolar_disorder":         n_bipolar_disorder,
    "schizophrenia":            n_schizophrenia,
    "parkinson":                n_parkinson,
    "multiple_sclerosis":       n_multiple_sclerosis,
    "sleep_duration":           n_sleep_duration,
    "neuroticism":              n_neuroticism,
    "cognitive_decline":        n_cognitive_decline,
    "anxiety":                  n_anxiety,
    "insomnia":                 n_insomnia,
    "seasonal_affective":       n_seasonal_affective,

    # Cancers
    "melanoma":                 n_melanoma,
    "breast_cancer":            n_breast_cancer,
    "prostate_cancer":          n_prostate_cancer,
    "colorectal_cancer":        n_colorectal_cancer,
    "lung_cancer":              n_lung_cancer,
    "bladder_cancer":           n_bladder_cancer,
    "gastric_cancer":           n_gastric_cancer,
    "pancreatic_cancer":        n_pancreatic_cancer,
    "kidney_cancer":            n_kidney_cancer,
    "thyroid_cancer":           n_thyroid_cancer,
    "leukemia_risk":            n_leukemia_risk,

    # Immune / Autoimmune
    "asthma":                   n_asthma,
    "lupus":                    n_lupus,
    "inflammatory_bowel":       n_inflammatory_bowel,
    "inflammatory_bowel_disease": n_inflammatory_bowel_disease,
    "crohn_disease":            n_crohn_disease,
    "rheumatoid_arthritis":     n_rheumatoid_arthritis,
    "celiac_disease":           n_celiac_disease,
    "eczema":                   n_eczema,
    "psoriasis":                n_psoriasis,
    "type_1_diabetes":          n_type_1_diabetes,
    "hay_fever":                n_hay_fever,
    "ulcerative_colitis":       n_ulcerative_colitis,
    "ankylosing_spondylitis":   n_ankylosing_spondylitis,
    "sarcoidosis":              n_sarcoidosis,
    "allergy_susceptibility":   n_allergy_susceptibility,

    # Lifestyle / Nutrition / Pharmacogenomics
    "alcohol_consumption":      n_alcohol_consumption,
    "caffeine_metabolism":      n_caffeine_metabolism,
    "lactase_persistence":      n_lactase_persistence,
    "longevity":                n_longevity,
    "pharmacogenomics":         n_pharmacogenomics,
    "nicotine_dependence":      n_nicotine_dependence,
    "cannabis_response":        n_cannabis_response,
    "sweet_preference":          n_sweet_preference,
    "salt_taste_sensitivity":    n_salt_taste_sensitivity,
    "circadian_preference":     n_circadian_preference,
}

BG = {
    "eye_color": n_eye_color_bg,
    "hair_color": n_hair_color_bg,
    "skin_tone": n_skin_tone_bg,
    "hair_loss": n_hair_loss_bg,
    "height": n_height_bg,
    "intelligence": lambda r: """
    <p>Когнитивният ви профил съдържа най-високия полигенен резултат в целия
    доклад: PGS +1064 от 8 повишени локуса. Важен методологичен контекст:
    GWAS проучванията за интелигентност често включват образователно постижение
    като приблизителен фенотип, така че резултатът отразява смес от когнитивна
    способност и образователна склонност, а не чиста мярка за интелигентност.</p>

    <p>COMT rs4680 GG е генотипът Val/Val ("Воин") — по-висока ензимна активност
    на COMT означава по-бързо разграждане на допамин в префронталния кортекс.
    Това води до по-добра работна памет и изпълнителна функция при високо
    когнитивно натоварване и стрес.</p>

    <p>BDNF rs6265 CT (хетерозиготен Val66Met) е нюансиращият фактор — алелът
    Met намалява секрецията на BDNF, зависима от активността, което засяга
    синаптичната пластичност. BDNF обаче е силно чувствителен към упражнения:
    редовната аеробна активност съществено компенсира намалената базова секреция.</p>
    """,
    "mthfr": n_mthfr_bg,
    "cholesterol": n_cholesterol_bg,
    "t2d": n_t2d_bg,
    "alzheimer": n_alzheimer_bg,
    "cad": n_cad_bg,
    "bmi": n_bmi_bg,
    "triglycerides": n_triglycerides_bg,
    "depression": n_depression_bg,
    "longevity": n_longevity_bg,
    "heart_failure": n_heart_failure_bg,
    "atrial_fibrillation": n_atrial_fibrillation_bg,
    "stroke": n_stroke_bg,
    "blood_pressure": n_blood_pressure_bg,
    "gout": n_gout_bg,
    "chronic_kidney_disease": n_chronic_kidney_disease_bg,
    "vitamin_d": n_vitamin_d_bg,
    "parkinson": n_parkinson_bg,
    "adhd": n_adhd_bg,
    "autism": n_autism_bg,
    "bipolar_disorder": n_bipolar_disorder_bg,
    "schizophrenia": n_schizophrenia_bg,
    "sleep_duration": n_sleep_duration_bg,
    "melanoma": n_melanoma_bg,
    "breast_cancer": n_breast_cancer_bg,
    "prostate_cancer": n_prostate_cancer_bg,
    "colorectal_cancer": n_colorectal_cancer_bg,
    "lung_cancer": n_lung_cancer_bg,
    "bladder_cancer": n_bladder_cancer_bg,
    "lupus": n_lupus_bg,
    "rheumatoid_arthritis": n_rheumatoid_arthritis_bg,
    "inflammatory_bowel": n_inflammatory_bowel_bg,
    "crohn_disease": n_crohn_disease_bg,
    "multiple_sclerosis": n_multiple_sclerosis_bg,
    "psoriasis": n_psoriasis_bg,
    "asthma": n_asthma_bg,
    "caffeine_metabolism": n_caffeine_metabolism_bg,
    "alcohol_consumption": n_alcohol_consumption_bg,
    "lactase_persistence": n_lactase_persistence_bg,
    "pharmacogenomics": n_pharmacogenomics_bg,
}

IMMUNE_TRAITS = {
    "lupus", "rheumatoid_arthritis", "inflammatory_bowel",
    "crohn_disease", "multiple_sclerosis", "psoriasis", "asthma"
}

CANCER_TRAITS = {
    "breast_cancer", "prostate_cancer", "colorectal_cancer",
    "melanoma", "lung_cancer", "bladder_cancer"
}

LIFESTYLE_TRAITS = {
    "alcohol_consumption", "caffeine_metabolism", "pharmacogenomics"
}

TRAIT_NAMES = {
    "en": {
        "eye_color": "Eye Color", "hair_color": "Hair Color", "skin_tone": "Skin Tone",
        "hair_loss": "Hair Loss", "height": "Height", "intelligence": "Cognitive Profile",
        "mthfr": "MTHFR / B-Vitamin Metabolism", "cholesterol": "Cholesterol / LDL",
        "t2d": "Type 2 Diabetes", "alzheimer": "Alzheimer's Disease", "cad": "Coronary Artery Disease",
        "bmi": "BMI / Obesity Tendency", "triglycerides": "Triglycerides", "depression": "Depression",
        "longevity": "Longevity", "caffeine_metabolism": "Caffeine Metabolism", "alcohol_consumption": "Alcohol Consumption",
        "pharmacogenomics": "Pharmacogenomics", "heart_failure": "Heart Failure", "atrial_fibrillation": "Atrial Fibrillation",
        "stroke": "Stroke", "gout": "Gout", "chronic_kidney_disease": "Chronic Kidney Disease",
        "vitamin_d": "Vitamin D Levels", "parkinson": "Parkinson", "adhd": "ADHD", "autism": "Autism",
        "bipolar_disorder": "Bipolar Disorder", "schizophrenia": "Schizophrenia", "sleep_duration": "Sleep Duration",
        "melanoma": "Melanoma", "breast_cancer": "Breast Cancer", "prostate_cancer": "Prostate Cancer",
        "colorectal_cancer": "Colorectal Cancer", "lung_cancer": "Lung Cancer", "bladder_cancer": "Bladder Cancer",
        "lupus": "Lupus", "rheumatoid_arthritis": "Rheumatoid Arthritis", "inflammatory_bowel": "Inflammatory Bowel",
        "crohn_disease": "Crohn Disease", "multiple_sclerosis": "Multiple Sclerosis", "psoriasis": "Psoriasis", "asthma": "Asthma",
        "freckles": "Freckles", "earlobe_type": "Earlobe Type", "bitter_taste": "Bitter Taste Sensitivity",
        "facial_hair": "Facial Hair Genetics", "hdl_cholesterol": "HDL Cholesterol", "ldl_cholesterol": "LDL Cholesterol",
        "metabolic_syndrome": "Metabolic Syndrome", "fasting_glucose": "Fasting Glucose", "insulin_resistance": "Insulin Resistance",
        "neuroticism": "Neuroticism", "cognitive_decline": "Cognitive Decline Risk", "anxiety": "Anxiety Tendency",
        "insomnia": "Insomnia Susceptibility", "seasonal_affective": "Seasonal Affective Traits", "gastric_cancer": "Gastric Cancer",
        "pancreatic_cancer": "Pancreatic Cancer", "kidney_cancer": "Kidney Cancer", "thyroid_cancer": "Thyroid Cancer",
        "leukemia_risk": "Leukemia Risk", "hay_fever": "Hay Fever / Allergic Rhinitis", "ulcerative_colitis": "Ulcerative Colitis",
        "ankylosing_spondylitis": "Ankylosing Spondylitis", "sarcoidosis": "Sarcoidosis", "allergy_susceptibility": "Allergy Susceptibility",
        "nicotine_dependence": "Nicotine Dependence", "cannabis_response": "Cannabis Response", "sweet_preference": "Sweet Preference",
        "salt_taste_sensitivity": "Salt Taste Sensitivity", "circadian_preference": "Circadian Chronotype"
    },
    "bg": {
        "eye_color": "Цвят на очите", "hair_color": "Цвят на косата", "skin_tone": "Цвят на кожата",
        "hair_loss": "Косопад", "height": "Ръст", "intelligence": "Когнитивен профил",
        "mthfr": "MTHFR / Метаболизъм на B-витамини", "cholesterol": "Холестерол / LDL",
        "t2d": "Диабет тип 2", "alzheimer": "Болест на Алцхаймер", "cad": "Коронарна артериална болест",
        "bmi": "ИТМ / Склонност към затлъстяване", "triglycerides": "Триглицериди", "depression": "Депресия",
        "longevity": "Дълголетие", "caffeine_metabolism": "Метаболизъм на кофеин", "alcohol_consumption": "Консумация на алкохол",
        "pharmacogenomics": "Фармакогеномика", "heart_failure": "Сърдечна недостатъчност", "atrial_fibrillation": "Предсърдно мъждене",
        "stroke": "Инсулт", "gout": "Подагра", "chronic_kidney_disease": "Хронично бъбречно заболяване",
        "vitamin_d": "Ниво на витамин D", "parkinson": "Паркинсон", "adhd": "СДВХ", "autism": "Аутизъм",
        "bipolar_disorder": "Биполярно разстройство", "schizophrenia": "Шизофрения", "sleep_duration": "Продължителност на съня",
        "melanoma": "Меланом", "breast_cancer": "Рак на гърдата", "prostate_cancer": "Рак на простатата",
        "colorectal_cancer": "Колоректален рак", "lung_cancer": "Рак на белия дроб", "bladder_cancer": "Рак на пикочния мехур",
        "lupus": "Лупус", "rheumatoid_arthritis": "Ревматоиден артрит", "inflammatory_bowel": "Възпалително чревно заболяване",
        "crohn_disease": "Болест на Крон", "multiple_sclerosis": "Множествена склероза", "psoriasis": "Псориазис", "asthma": "Астма",
        "freckles": "Лунички", "earlobe_type": "Тип ушна мида", "bitter_taste": "Чувствителност към горчив вкус",
        "facial_hair": "Генетика на окосмяването по лицето", "hdl_cholesterol": "HDL холестерол", "ldl_cholesterol": "LDL холестерол",
        "metabolic_syndrome": "Метаболитен синдром", "fasting_glucose": "Кръвна захар на гладно", "insulin_resistance": "Инсулинова резистентност",
        "neuroticism": "Невротизъм", "cognitive_decline": "Риск от когнитивен спад", "anxiety": "Склонност към тревожност",
        "insomnia": "Предразположеност към безсъние", "seasonal_affective": "Сезонни афективни черти", "gastric_cancer": "Рак на стомаха",
        "pancreatic_cancer": "Рак на панкреаса", "kidney_cancer": "Рак на бъбреците", "thyroid_cancer": "Рак на щитовидната жлеза",
        "leukemia_risk": "Риск от левкемия", "hay_fever": "Сенна хрема / Алергичен ринит", "ulcerative_colitis": "Улцерозен колит",
        "ankylosing_spondylitis": "Анкилозиращ спондилит", "sarcoidosis": "Саркоидоза", "allergy_susceptibility": "Алергична предразположеност",
        "nicotine_dependence": "Nicotine Dependence", "cannabis_response": "Реакция към канабис", "sweet_preference": "Предпочитание към сладко",
        "salt_taste_sensitivity": "Чувствителност към сол", "circadian_preference": "Циркаден хронотип"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# UI STRINGS (localization for report chrome: badges, bars, marker roles)
# ─────────────────────────────────────────────────────────────────────────────
UI = {
    "en": {
        "gwas_summary_label": "GWAS Summary",
        "deep_analysis_label": "Deeper Analysis",
        "pgs_label": "GWAS PGS",
        "elevated_loci": "elevated loci",
        "loci_elevated_of": "of {total} genotyped loci show elevated risk",
        "protective": "Protective",
        "risk": "Risk",
        "no_deep_analysis": "No additional deep analysis available.",
        "roles": {
            "rule_out": "Rule-out check",
            "primary": "Primary driver",
            "secondary": "Secondary modifier",
            "modifier": "Enzymatic modifier",
            "minor": "Minor contributor",
        },
    },
    "bg": {
        "gwas_summary_label": "GWAS Резюме",
        "deep_analysis_label": "По-задълбочен анализ",
        "pgs_label": "GWAS PGS",
        "elevated_loci": "повишени локуси",
        "loci_elevated_of": "от {total} генотипирани локуса показват повишен риск",
        "protective": "Защитен",
        "risk": "Риск",
        "no_deep_analysis": "Няма наличен задълбочен анализ.",
        "roles": {
            "rule_out": "Изключващ маркер",
            "primary": "Първичен драйвер",
            "secondary": "Вторичен модификатор",
            "modifier": "Ензимен модификатор",
            "minor": "Минорен фактор",
        },
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# REPORT COMPONENT HELPERS
# (moved here from generate_report.py — these only depend on data already
# in this module: TRAIT_NAMES, BG, BESPOKE, risk_label_bg, n_gwas_summary, UI)
# ─────────────────────────────────────────────────────────────────────────────
def get_localized_narrative_html(key, r, lang="en"):
    ui = UI.get(lang, UI["en"])
    trait_name = TRAIT_NAMES.get(lang, TRAIT_NAMES["en"]).get(key, r.get("trait", key.replace("_", " ").title()))
    if lang == "bg" and key in BG:
        summary_html = n_gwas_summary_bg(r, trait_name)
    else:
        summary_html = n_gwas_summary(r, trait_name)
    gwas_html = f"""<div class="narrative-unit narrative-unit--gwas"><div class="narrative-kicker">{ui['gwas_summary_label']}</div><div class="narrative-text">{summary_html}</div></div>"""

    bespoke_content = ""
    norm_key = key.strip().lower().replace(" ", "_")
    alt_key = key.strip().lower().replace("_", " ")
    if lang == "bg":
        if norm_key in BG: bespoke_content = BG[norm_key](r)
        elif alt_key in BG: bespoke_content = BG[alt_key](r)
        elif norm_key in BESPOKE: bespoke_content = BESPOKE[norm_key](r)
        else: bespoke_content = f"<p>{r.get('narrative', ui['no_deep_analysis'])}</p>"
    else:
        if norm_key in BESPOKE: bespoke_content = BESPOKE[norm_key](r)
        elif alt_key in BESPOKE: bespoke_content = BESPOKE[alt_key](r)
        else: bespoke_content = f"<p>{r.get('narrative', ui['no_deep_analysis'])}</p>"
    deep_html = f"""<div class="narrative-unit narrative-unit--deep"><div class="narrative-kicker">{ui['deep_analysis_label']}</div><div class="narrative-text">{bespoke_content}</div></div>"""
    return gwas_html, deep_html


def get_marker_votes_html(trait, lang="en"):
    ui = UI.get(lang, UI["en"])
    markers = trait.get("markers")
    if not markers or not isinstance(markers, list):
        return ""
    valid = [m for m in markers if isinstance(m, dict) and m.get("direction")]
    if not valid:
        return ""

    role_rank = {"primary": 0, "secondary": 1, "modifier": 2, "minor": 3, "rule_out": 4, None: 5}
    valid.sort(key=lambda m: role_rank.get(m.get("role"), 5))

    categories = []
    for m in valid:
        d = m["direction"]
        if d not in categories:
            categories.append(d)
    palette = ["var(--cat-a)", "var(--cat-b)", "var(--cat-c)", "var(--cat-d)", "var(--cat-e)"]
    color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}

    dominant_terms = ["strongest", "majority", "primary", "dominant"]
    minor_terms = ["minor contributor", "modest", "secondary"]
    role_labels = {
        "rule_out": ("marker-tag--ruleout", ui["roles"]["rule_out"]),
        "primary": ("marker-tag--primary", ui["roles"]["primary"]),
        "secondary": ("marker-tag--secondary", ui["roles"]["secondary"]),
        "modifier": ("marker-tag--modifier", ui["roles"]["modifier"]),
        "minor": ("marker-tag--minor", ui["roles"]["minor"]),
    }

    def weight_info(marker):
        role = marker.get("role")
        if role in role_labels:
            return role_labels[role]
        note_l = (marker.get("note") or "").lower()
        if any(t in note_l for t in dominant_terms):
            return role_labels["primary"]
        if any(t in note_l for t in minor_terms):
            return role_labels["minor"]
        return "", ""

    tally_html = "".join(
        f'<span class="marker-tally-item"><span class="marker-dot" style="background:{color_map[cat]}"></span>{cat} · {sum(1 for m in valid if m["direction"] == cat)}</span>'
        for cat in categories
    )
    tags = []
    for m in valid:
        css_class, label = weight_info(m)
        note_escaped = (m.get("note") or "").replace('"', "&quot;")
        label_html = f'<span class="marker-tag-weight">{label}</span>' if label else ""
        tags.append(
            f'<div class="marker-tag {css_class}" title="{note_escaped}">'
            f'<span class="marker-tag-dot" style="background:{color_map[m["direction"]]}"></span>'
            f'<div class="marker-tag-main">'
            f'<span class="marker-tag-gene">{m.get("gene","")}</span>'
            f'<span class="marker-tag-rsid">{m.get("rsid","")}</span>'
            f'<span class="marker-tag-geno">{m.get("genotype","")}</span>'
            f'{label_html}'
            f'</div></div>'
        )
    tags_html = "".join(tags)
    return f"""<div class="marker-votes">
        <div class="marker-tally">{tally_html}</div>
        <div class="marker-tag-grid">{tags_html}</div>
    </div>"""


def _find_score(trait, suffix):
    for k, v in trait.items():
        if k.endswith(suffix) and isinstance(v, (int, float)):
            return v
    return None


def get_risk_balance_html(trait, lang="en"):
    ui = UI.get(lang, UI["en"])
    risk = _find_score(trait, "risk_score")
    prot = _find_score(trait, "prot_score")
    if risk is None or prot is None:
        return ""
    total = max(risk, prot, 0.1)
    risk_pct = (risk / total) * 100
    prot_pct = (prot / total) * 100
    return f"""<div class="risk-balance">
        <div class="risk-balance-track">
            <div class="risk-balance-prot" style="width:{prot_pct:.1f}%"></div>
            <div class="risk-balance-risk" style="width:{risk_pct:.1f}%"></div>
        </div>
        <div class="risk-balance-labels">
            <span class="rb-prot">{ui['protective']} {prot:.1f}</span>
            <span class="rb-risk">{ui['risk']} {risk:.1f}</span>
        </div>
    </div>"""


def get_pgs_badge_html(trait, lang="en"):
    ui = UI.get(lang, UI["en"])
    pgs = trait.get("gwas_pgs", trait.get("pgs_score"))
    if pgs is None:
        return ""
    sign = "+" if pgs >= 0 else ""
    extra = ""
    if trait.get("gwas_based") and trait.get("snps_used") is not None and trait.get("total_snps") is not None:
        extra = f" · {trait['snps_used']} {ui['loci_elevated_of'].format(total=trait['total_snps'])}"
    elif trait.get("gwas_elevated") is not None:
        extra = f" · {trait['gwas_elevated']} {ui['elevated_loci']}"
    return f'<div class="pgs-badge">{ui["pgs_label"]} {sign}{pgs:.1f}{extra}</div>'


def get_loci_bar_html(trait, color, lang="en"):
    ui = UI.get(lang, UI["en"])
    used = trait.get("snps_used")
    total = trait.get("total_snps")
    if not trait.get("gwas_based") or not used or not total:
        return ""
    pct = (used / total) * 100
    return f"""<div class="loci-bar">
        <div class="loci-bar-track">
            <div class="loci-bar-fill" style="width:{pct:.1f}%; background:{color}"></div>
        </div>
        <span class="loci-bar-label">{used} {ui['loci_elevated_of'].format(total=total)} ({pct:.1f}%)</span>
    </div>"""