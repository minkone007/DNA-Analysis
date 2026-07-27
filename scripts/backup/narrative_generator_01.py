#!/usr/bin/env python3
"""
narrative_generator.py
Generates bespoke genetics narrative in English or Bulgarian.
"""

import json, argparse, sys
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
CONFIG   = ROOT_DIR / "people.json"

# ─────────────────────────────────────────────────────────────────────────────
# BESPOKE NARRATIVES — written for Minko's specific genotypes
# Each function receives the synthesis dict for that trait and returns HTML prose
# ─────────────────────────────────────────────────────────────────────────────

def n_eye_color(r):
    return """
    <p>Your eye colour prediction sits at the blue-green boundary, which is exactly
    where your genotype combination places you. The dominant signal is rs12913832 GG —
    this single variant in the HERC2 gene is the strongest known predictor of eye colour
    in humans, and GG is the classic blue-associated genotype found in roughly 97% of
    blue-eyed Europeans. On its own, this would predict blue.</p>

    <p>What introduces the green element is the combination of secondary signals pulling
    in different directions. SLC24A4 GT and IRF4 CT are both intermediate — they neither
    fully reinforce the blue signal nor push toward brown. SLC45A2 GG is the ancestral
    allele, which doesn't contribute the European lightening variant, adding a small
    counterweight. TYR AG (heterozygous) reduces melanin synthesis modestly across all
    tissues including the iris.</p>

    <p>The net result: a strongly reduced OCA2-driven melanin signal from HERC2, partially
    modulated by intermediate alleles at supporting loci. This produces a lighter-than-brown
    iris with the specific hue sitting somewhere between blue and green depending on
    lighting conditions and iris structure. Blue-green or green-blue are both plausible
    phenotypic outcomes. Brown is effectively ruled out — you carry none of the
    classic brown-promoting allele combinations at the key loci.</p>

    <p>One practical note: TYR CA's melanin-reducing effect extends beyond eye colour.
    The same enzyme reduction that lightens the iris also reduces UV-protective eumelanin
    in skin. This is not merely a cosmetic footnote — it has genuine implications for
    sun damage accumulation over a lifetime, addressed further in the skin section.</p>
    """

def n_hair_color(r):
    return """
    <p>Your hair colour genetics tell a clean, consistent story: medium to dark brown,
    with no red component. The MC1R gene — which functions as the primary switch between
    red/yellow pheomelanin and dark eumelanin — shows no risk variants across all four
    tested positions (Arg151Cys, Arg160Trp, Arg163Gln, Cys289Arg). This effectively
    rules out red hair entirely. You inherited a fully functional MC1R receptor, which
    means your melanocytes default to eumelanin production.</p>

    <p>The dominant pigmentation signal is SLC45A2 GG. This is the ancestral allele —
    common in non-European and darker-pigmented populations — which does not contribute
    the European hair-lightening variant. Combined with the absence of MC1R variants,
    this firmly establishes a dark baseline.</p>

    <p>The only modest lightening signal comes from TYR AC (heterozygous at rs1042602),
    which reduces tyrosinase enzyme efficiency. This is a moderate effect — it may
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

    <p>Counterbalancing this is SLC45A2 GG — the ancestral allele at a second major
    pigmentation gene. Unlike the CC European variant at SLC45A2, GG does not contribute
    additional lightening. This creates a genuine partial offset: SLC24A5 pushes
    strongly toward lighter skin; SLC45A2 holds back from adding further lightening,
    producing a light-to-medium rather than very fair result.</p>

    <p>TYR CA (heterozygous) adds a third layer: reduced tyrosinase activity means
    less eumelanin output across all skin cells. This contributes to freckling tendency
    and, critically, to reduced UV protection. The skin's tanning response depends on
    tyrosinase upregulation in response to UV — with one reduced-function TYR allele,
    this response is blunted. The practical consequence: your skin burns more readily
    than it tans, and UV damage accumulates faster than in someone with full tyrosinase
    activity. SPF50 is not overcautious for this profile — it is the appropriate
    baseline, used consistently rather than occasionally.</p>

    <p>The Fitzpatrick Type III prediction (medium skin, tans after initial burn) fits
    this genotype combination accurately.</p>
    """

def n_cholesterol(r):
    return """
    <p>Your cholesterol genetics present a mixed but ultimately moderate picture.
    The most important finding is what is absent: you carry rs7412 CC, which is the
    APOE ε2 signal — associated with lower LDL and reduced cardiovascular risk compared
    to the common ε3/ε3 genotype. This is a genuinely favourable finding at the most
    clinically significant cholesterol locus.</p>

    <p>The note of caution is that rs429358 — the second SNP needed to fully call
    APOE genotype — was not on your chip. This means we cannot rule out a mixed
    ε2/ε4 genotype, which would partially offset the ε2 protection. A clinical APOE
    genotype test (inexpensive, available through your GP) would resolve this definitively
    and is worth doing given its implications for both cardiovascular and Alzheimer risk.</p>

    <p>Beyond APOE, the LDL-relevant variants show: rs629301 TT at SORT1/CELSR2 carries
    two copies of the LDL-raising allele — this locus modestly elevates LDL through
    effects on hepatic SORT1 expression and LDL receptor trafficking. rs11591147 GG at
    PCSK9 shows no protective loss-of-function allele, meaning you don't have the natural
    PCSK9 inhibition that some individuals carry (which can lower LDL by 30% without
    medication). LPA rs10455872 AA is non-risk — you do not carry the Lp(a)-elevating
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
    headline number — elevated risk — obscures an important pattern in the detail.</p>

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
    intervention — the Diabetes Prevention Program trial showed that carriers who
    underwent lifestyle modification had the same T2D incidence reduction as non-carriers,
    meaning the genetic effect is not fixed.</p>

    <p>The practical message: your genetic profile warrants attention to modifiable
    risk factors — weight, physical activity, dietary glycaemic load — but the
    predominantly heterozygous pattern means lifestyle intervention is genuinely
    effective at this level of loading. Fasting glucose and HbA1c monitoring every
    few years is appropriate regardless of symptoms.</p>
    """

def n_alzheimer(r):
    return """
    <p>Your Alzheimer's risk profile contains arguably the most reassuring finding in
    this entire report. rs7412 CC corresponds to the APOE ε2 allele — and APOE ε2
    is the strongest known protective variant against late-onset Alzheimer's disease.
    ε2 carriers have approximately 50% lower Alzheimer's risk compared to the common
    ε3/ε3 genotype, and are significantly overrepresented among cognitively healthy
    individuals aged 85 and older.</p>

    <p>The caveat, as noted in the cholesterol section, is that rs429358 was not on
    your chip — so we cannot fully exclude an ε2/ε4 mixed genotype. However, even
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
    The most evidence-based protective behaviours — cardiovascular health maintenance,
    regular aerobic exercise, quality sleep (critical for amyloid clearance via the
    glymphatic system), and cognitive engagement — remain worthwhile regardless of
    genotype, and are especially effective in ε2 carriers who already have a protective
    biological baseline.</p>
    """

def n_cad(r):
    return """
    <p>Coronary artery disease is where your genetic profile shows its most clinically
    significant elevation. The 9p21 locus (CDKN2B-AS1) — the single most replicated
    common CAD variant in the literature — appears twice in your data: rs4977574 AG
    (one risk copy) and rs1333049 CG (one risk copy at the secondary variant).
    These two variants are additive and their effects are well-established across
    multiple large cohort studies.</p>

    <p>What makes the 9p21 locus particularly important is that it acts independently
    of LDL cholesterol. Its mechanism involves regulation of cell proliferation in
    vascular smooth muscle and inflammatory pathways — meaning standard lipid testing
    will not capture this risk. Someone with normal cholesterol and 9p21 risk alleles
    still has meaningfully elevated CAD risk compared to population baseline.</p>

    <p>Additional signals: rs646776 TT at CELSR2/SORT1 (the same locus relevant to
    LDL) carries two copies of the risk allele and contributes via the LDL pathway.
    rs1122608 GG at LDLR is the LDL receptor region variant. The LPL rs264 GG is
    the protective allele — a gain-of-function variant that raises lipoprotein lipase
    activity and improves triglyceride clearance. This partial offset from LPL is
    a genuine counterbalancing factor.</p>

    <p>The GWAS shows 25 elevated loci and a PGS of +111, confirming meaningful
    polygenic loading across multiple CAD pathways. Given this profile, attention
    to the full cardiovascular risk picture is warranted: blood pressure monitoring,
    regular lipid panels (with awareness that 9p21 risk is not captured by LDL alone),
    smoking avoidance, and physical activity. High-sensitivity CRP (hsCRP) testing
    is worth discussing with your GP as an inflammatory risk marker relevant to
    the 9p21 pathway.</p>
    """

def n_bmi(r):
    return """
    <p>Your BMI genetics show moderate loading, with the key finding being FTO
    heterozygosity. rs9939609 AT means you carry one copy of the FTO risk allele
    (A) — each A allele adds approximately 0.4 kg/m² to average BMI, putting you
    at modest rather than strong genetic BMI elevation. The secondary FTO variant
    rs17817449 GT adds a small additional signal.</p>

    <p>A critically important counterbalance: rs2815752 AG at NEGR1 carries the
    protective allele (A) in heterozygous form. NEGR1 is involved in neuronal growth
    and appetite regulation — the protective variant is associated with lower BMI,
    and its presence here partially offsets the FTO signal.</p>

    <p>The most important thing to know about your FTO genotype is what the research
    shows about modifiability. The Kilpeläinen et al. 2011 meta-analysis (PLOS Medicine,
    218,000 participants) demonstrated that FTO risk allele carriers who were physically
    active had BMI values essentially identical to non-carriers. The genetic effect of
    FTO on BMI was almost completely abolished by regular physical activity. This is one
    of the clearest gene-environment interaction findings in all of genomics — and it is
    directly actionable. The genetic tendency exists; whether it expresses depends
    substantially on activity level.</p>
    """

def n_triglycerides(r):
    return """
    <p>Your triglyceride genetics show a pattern of moderate elevation with one
    important protective counterweight. The primary risk signal is APOA5 AG
    (rs662799 heterozygous) — APOA5 is the dominant triglyceride locus, and the G
    allele impairs APOA5's role in activating lipoprotein lipase, leading to slower
    triglyceride clearance. Heterozygous carriers typically show mild-to-moderate
    triglyceride elevation, with the effect amplified substantially by carbohydrate
    intake and alcohol.</p>

    <p>APOC3 AG (rs2266788) adds a secondary signal — APOC3 normally inhibits LPL,
    and the promoter variant increases APOC3 expression, further reducing triglyceride
    clearance. MTNR1B CG (heterozygous) affects fasting triglycerides via melatonin
    receptor signalling — a more modest contribution.</p>

    <p>The key protective finding is LPL rs328 CC — the S447X gain-of-function
    variant. This is genuinely protective: the C allele creates a truncated but
    hyperactive form of lipoprotein lipase that substantially improves triglyceride
    clearance. This is one of the few cases in lipid genetics where a variant provides
    real biological protection, and its presence meaningfully counterbalances the APOA5
    and APOC3 risk signals.</p>

    <p>Dietary implications are direct: your APOA5 heterozygosity means carbohydrate
    and alcohol intake have an amplified effect on your triglyceride levels compared
    to someone without this variant. Omega-3 supplementation (EPA/DHA, 2-4g daily)
    is particularly effective in APOA5 risk carriers — clinical trials show 20-30%
    triglyceride reduction. Low-carbohydrate diets are more effective for you than
    for the average person. The LPL protective allele means you have better baseline
    clearance capacity than your risk alleles alone would suggest.</p>
    """

def n_depression(r):
    return """
    <p>Your depression genetics tell a nuanced story that requires careful context
    to interpret correctly. The headline — elevated genetic signal with 32 GWAS loci
    and PGS +71.8 — reflects genuine polygenic loading. But depression genetics have
    important interpretive limitations that are as important as the numbers themselves.</p>

    <p>The most personally relevant findings are in the curated SNPs. BDNF rs6265 CT
    means you carry one copy of the Val66Met variant — the T (Met) allele is associated
    with reduced activity-dependent BDNF secretion. BDNF is the brain's primary
    neurotrophic factor, supporting neuronal survival, plasticity, and stress recovery.
    The Met allele has been associated with reduced hippocampal volume, increased
    anxiety response, and greater vulnerability to stress-induced mood changes.
    Importantly, BDNF levels are highly responsive to aerobic exercise — physical
    activity is one of the most robust BDNF upregulators known, and this is one
    mechanism by which exercise reduces depression risk.</p>

    <p>COMT rs4680 GG is the Warrior profile (Val/Val) — higher dopamine breakdown
    in the prefrontal cortex, which typically means better stress resilience and
    executive function under pressure, at the cost of slightly lower baseline
    dopamine tone. For depression, this is generally neutral-to-protective rather
    than a risk factor.</p>

    <p>NEGR1 AG (rs1545843) and TMEM161B TT (rs10514299) are the first wave of
    genome-wide significant depression hits, but their individual effect sizes are
    very small — important at the population level, less meaningful individually.</p>

    <p>The overarching message: the BDNF Val66Met heterozygosity is the most
    interpretively meaningful finding here. It suggests somewhat higher biological
    sensitivity to stress and environmental adversity — not a predetermined outcome,
    but a profile that responds particularly well to protective factors: regular
    aerobic exercise (the most evidence-based BDNF upregulator), quality sleep,
    and strong social connection. These are not generic lifestyle advice — for
    your specific genotype, they have direct neurobiological relevance.</p>
    """

def n_longevity(r):
    return """
    <p>Your longevity genetics show moderate positive signals, with the APOE picture
    being the centrepiece. As noted in the Alzheimer section, rs7412 CC corresponds
    to the APOE ε2 allele — and ε2 is consistently overrepresented among centenarians
    in multiple independent cohort studies. The mechanism is multifactorial: lower LDL,
    reduced neuroinflammation, more efficient lipid metabolism, and lower Alzheimer risk
    all contribute to the survival advantage.</p>

    <p>The CETP variants add genuine additional longevity signal. CETP rs3764814 CT
    (one protective C allele) and CETP rs5882 AG (one protective allele) both point
    toward higher HDL cholesterol — and elevated HDL has been consistently associated
    with longevity in centenarian studies, particularly in Ashkenazi Jewish and
    Japanese cohorts. The CETP variants work by reducing cholesterol ester transfer
    activity, allowing HDL particles to remain larger and more functional for longer.</p>

    <p>FOXO3 was not on your chip — this is the single most replicated longevity
    locus outside APOE, active across five independent national cohorts. It is worth
    checking via a clinical or research genetic test if longevity genetics are of
    particular interest to you.</p>

    <p>The GWAS shows 18 longevity-associated loci with PGS +62.4. Combined with
    the APOE ε2 signal and CETP variants, the overall longevity picture is moderately
    favourable at the genetic level. The evidence across all longevity studies
    consistently shows that lifestyle factors — particularly avoiding smoking, regular
    physical activity, Mediterranean-style diet, and maintaining social engagement —
    explain more variance in reaching exceptional age than genetics does. Your genetics
    provide a reasonable starting position; what you do with it matters more.</p>
    """

def n_schizophrenia(r):
    return """
    <p>The schizophrenia GWAS signal deserves careful contextualisation before anything
    else is said. Your PGS of +125.2 and 29 elevated loci sound alarming, but this
    requires two important corrections before interpretation.</p>

    <p>First, schizophrenia polygenic risk scores have very poor individual predictive
    value. Even in the highest PGS decile of the general population, lifetime
    schizophrenia incidence remains around 3-4% — compared to ~1% population baseline.
    The score distinguishes statistical groups, not individuals. The vast majority of
    people with high schizophrenia PGS never develop the condition.</p>

    <p>Second, the specific variants driving your elevated score include several with
    very high ORs from small studies (rs117673608 at PRKN with OR 26.32, rs7116879
    at DKK3 with OR 14.70). Large ORs in GWAS almost always reflect either
    population-specific effects, small study sizes with inflated estimates, or rare
    variants with limited generalisability. The schizophrenia GWAS literature has
    known issues with winner's curse and population stratification in some datasets.</p>

    <p>The most meaningful biological signal here is the HLA/MHC component — many
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
    genetic architecture — particularly in the HLA region and cytokine signalling
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
    with your GP — autoimmune conditions are frequently underdiagnosed, and
    having a clear picture of your genetic predispositions can inform appropriate
    monitoring thresholds.</p>
    """

def n_cancer(r, trait):
    specifics = {
        "Breast Cancer": (
            "rs637644 GG (OR 32.50) and rs3844412 AA (OR 5.22) are the headline hits, "
            "but these ORs likely reflect population-specific or rare variant effects "
            "rather than common risk applicable to all ancestries. rs78378222 TT at TP53 "
            "is more universally relevant — TP53 is the genome's master tumour suppressor, "
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
            "variant for prostate cancer — however, CC at rs138213197 is the common "
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
            "pigmentation allele — but here it appears in the melanoma data because "
            "some studies find this allele pattern in melanoma cohorts reflecting "
            "ancestry confounding. More relevant is IRF4 CT (rs12203592, OR 1.76) — "
            "IRF4 genuinely affects melanocyte biology and melanoma risk. TP53 TT "
            "(rs78378222) is a cross-cancer signal. Combined with your TYR CA "
            "melanin-reducing variant from the pigmentation analysis, the UV sensitivity "
            "picture is clear and actionable: consistent SPF50, annual skin checks, "
            "and shade-seeking behaviour are genuinely warranted for your specific "
            "genetic profile. Melanoma caught at Stage I has >95% five-year survival."
        ),
        "Lung Cancer": (
            "rs17879961 AA at CHEK2 is the dominant signal, appearing multiple times "
            "with ORs of 1.54-2.63. CHEK2 is a DNA damage checkpoint gene — carriers "
            "of loss-of-function variants have elevated risk across multiple cancer types "
            "including lung, breast, and colorectal. However, rs17879961 is an intronic "
            "variant, not the classic CHEK2 I157T coding change, so its functional "
            "significance is less certain. rs11571818 TT at BRCA2 is also notable — "
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
    The CC genotype at rs1229984 is associated with slower ADH1B activity — meaning
    acetaldehyde accumulates more slowly, which in some populations is associated
    with higher alcohol consumption because the aversive flushing effect is reduced.
    However, an OR of 24.56 for alcohol consumption quantity (not a disease outcome)
    reflects the enormous population-level variation in drinking behaviour, not a
    personal risk for any specific harm.</p>

    <p>rs13107325 CC at SLC39A8 (OR 11.45) and rs1260326 CC at GCKR (OR 7.39-8.22)
    are additional metabolic variants associated with alcohol-related traits. GCKR
    is a glucokinase regulatory protein that affects both alcohol and glucose
    metabolism — its CC genotype is the risk allele here.</p>

    <p>The practical interpretation: these variants may reflect differences in
    alcohol metabolism efficiency and reward pathway response. They do not predict
    alcohol use disorder — that is a complex behavioural outcome with distinct
    genetics. What they do suggest is awareness of individual metabolic response
    to alcohol, particularly given the triglyceride picture (APOA5 AG means alcohol
    has a disproportionate effect on your triglyceride levels).</p>
    """,
        "Caffeine Metabolism": """
    <p>rs56113850 TC at CYP2A6 drives your caffeine signal, appearing three times
    with ORs of 4.59-9.59. CYP2A6 is primarily known for nicotine metabolism but
    also contributes to caffeine breakdown. The heterozygous TC genotype suggests
    intermediate metabolic activity at this locus.</p>

    <p>The primary caffeine metabolism gene — CYP1A2 — was not directly captured
    in your GWAS data, which limits the interpretation. CYP1A2 is the enzyme that
    handles roughly 95% of caffeine clearance, and its variants (particularly
    rs762551) are the strongest determinants of whether you are a fast or slow
    caffeine metaboliser. A direct CYP1A2 genotype test would give a clearer
    picture of your optimal caffeine timing.</p>

    <p>The practical takeaway from CYP2A6 TC: likely intermediate caffeine
    metabolism. If you notice caffeine affecting sleep quality even when consumed
    in the early afternoon, this is consistent with a slower-than-average
    clearance profile — cutting off caffeine by noon rather than 2-3pm would be
    a worthwhile experiment.</p>
    """,
        "Pharmacogenomics": """
    <p>Your pharmacogenomics GWAS data captured three elevated loci: rs77375493
    GG at JAK2 (OR 1.94), rs749671 GA at ZNF646 (OR 20.40), and rs245880 AG
    at CPVL (OR 4.69). The very high OR for rs749671 likely reflects a
    population-specific or rare variant effect rather than a broadly applicable
    drug response signal.</p>

    <p>The most clinically actionable pharmacogenomics variants — CYP2D6, CYP2C19,
    CYP2C9, TPMT, DPYD — were not captured in this GWAS dataset. These are the
    variants that directly affect metabolism of commonly prescribed drugs including
    antidepressants, antipsychotics, blood thinners, and chemotherapy agents.</p>

    <p>If you are starting any new medication — particularly antidepressants,
    antiplatelet drugs (clopidogrel), or pain medications involving codeine or
    tramadol — a pharmacogenomics panel from a clinical genetics service is worth
    discussing with your prescriber. These panels cost £100-300 and can prevent
    ineffective dosing or adverse reactions that would otherwise only be discovered
    through trial and error.</p>
    """,
    }
    return specifics.get(trait, f"<p>{r.get('narrative','')}</p>")

def n_hair_loss(r):
    return """
    <p>Your hair loss genetics tell a reassuring story. The X-linked AR/EDA2R locus
    — the single strongest signal for male pattern baldness, with ORs above 2.0
    in published GWAS — shows rs2497938 CC, which is the non-risk genotype.
    This locus is inherited maternally (on the X chromosome), meaning the signal
    you carry from your mother's side does not confer the classic androgenetic
    alopecia predisposition at this dominant position.</p>

    <p>The GWAS confirms this: only 1 elevated locus out of 15 genotyped, with a
    PGS of +2.8 — the lowest meaningful polygenic score in your entire profile.
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
    <p>Height is one of the most polygenic traits in the human genome — thousands
    of variants each contributing fractions of a millimetre. Your polygenic score
    of +401 from 29 elevated loci is the second-highest quantitative score in
    your profile (after intelligence), and it consistently points above the
    population mean.</p>

    <p>HMGA2 rs1042725 TT is the one well-characterised curated locus on your chip.
    HMGA2 (High Mobility Group AT-hook 2) is a transcription factor that regulates
    growth and development — TT at this position is the taller-associated genotype,
    contributing approximately 0.4 cm per allele in large-scale studies.</p>

    <p>The GWAS elevated loci include hits across pathways governing bone growth,
    IGF-1 signalling, and skeletal development. A PGS of +401 in the height GWAS
    (which uses beta coefficients in cm units) translates to a meaningful cumulative
    signal toward above-average stature. Height is approximately 80% heritable in
    well-nourished populations, and your genetic signal is consistent with
    above-average genetic potential for height — though actual realised height
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
    neurological resilience signals — not a pure intelligence measure.</p>

    <p>The curated SNPs provide the most interpretable layer. COMT rs4680 GG is
    the Val/Val (Warrior) genotype — higher COMT enzymatic activity means faster
    dopamine breakdown in the prefrontal cortex. This produces better working
    memory performance and executive function under high cognitive load and stress,
    at the cost of slightly lower baseline dopamine tone and potentially reduced
    exploratory behaviour. Critically, Val/Val carriers show superior cognitive
    performance specifically under pressure and in complex task-switching — the
    profile associated with performance in demanding professional environments.</p>

    <p>BDNF rs6265 CT (Val66Met heterozygous) is the one nuancing factor. The
    Met allele reduces activity-dependent BDNF secretion, which affects synaptic
    plasticity and learning consolidation. However, heterozygosity means one
    functional Val allele remains — this is a partial rather than full reduction.
    In practice, Val66Met heterozygotes show modestly reduced episodic memory
    performance in some studies but maintain normal working memory.</p>

    <p>The combination — COMT Warrior profile with heterozygous BDNF — suggests
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

    <p>You carry two MTHFR variants simultaneously — compound heterozygosity
    that is more significant than either variant alone:</p>

    <p><strong>MTHFR C677T (rs1801133) GA — heterozygous.</strong> The T allele
    reduces MTHFR enzyme activity by approximately 35% in heterozygotes. MTHFR
    (methylenetetrahydrofolate reductase) is the key enzyme that converts folate
    into the active form (5-methylTHF) used to recycle homocysteine back to
    methionine. Reduced activity means slower homocysteine clearance and
    potentially elevated plasma homocysteine — a cardiovascular and neurological
    risk factor.</p>

    <p><strong>MTHFR A1298C (rs1801131) GT — heterozygous.</strong> The C allele
    at this position reduces MTHFR activity through a different mechanism,
    affecting the regulatory domain of the enzyme. Alone, A1298C heterozygosity
    has modest effects. Combined with C677T heterozygosity (compound
    heterozygosity), the functional enzyme activity can be reduced by 50-60% —
    approaching the level seen in C677T homozygotes.</p>

    <p><strong>MTR A2756G (rs1805087) AA</strong> — this is the wild-type at the
    methionine synthase gene, meaning no additional impairment of the B12-dependent
    remethylation pathway from this locus.</p>

    <p><strong>MTRR A66G (rs1801394) GG</strong> — this is the AA wild-type at
    methionine synthase reductase (the enzyme that recycles the B12 cofactor for
    MTR). GG here means no MTRR-related impairment.</p>

    <p><strong>MTHFD1 (rs2236225) AG</strong> — heterozygous at the
    methylenetetrahydrofolate dehydrogenase gene, which feeds into the folate cycle.
    This adds a modest additional strain on the overall one-carbon metabolism pathway.</p>

    <p>The practical implications of compound MTHFR heterozygosity are direct and
    well-supported by clinical evidence:</p>

    <p>First, standard folic acid (the synthetic form in most supplements) requires
    conversion to active 5-methylTHF by MTHFR itself — a step that is inefficient
    in your case. The solution is to supplement with <strong>methylfolate
    (5-MTHF)</strong> directly, bypassing the impaired conversion step entirely.
    400-800 mcg of methylfolate daily is the standard recommendation for MTHFR
    compound heterozygotes.</p>

    <p>Second, B12 status matters more for you than for the average person.
    The homocysteine-to-methionine conversion requires both active folate and
    B12 as cofactors. Methylcobalamin (the active form of B12) rather than
    cyanocobalamin is preferable for the same bypass reasoning. Testing
    homocysteine, folate, and B12 blood levels is worth doing to establish
    your actual metabolic status — genetics tell you the predisposition,
    blood tests tell you whether it is expressing.</p>

    <p>Third, the cardiovascular relevance: elevated homocysteine is an
    independent risk factor for coronary artery disease and stroke — two areas
    where your GWAS data already shows elevated signals. This is not coincidental;
    the MTHFR-homocysteine-cardiovascular connection is well-established and
    represents a direct intervention opportunity. Adequate methylfolate and
    methylcobalamin supplementation has been shown to normalise homocysteine
    in MTHFR carriers.</p>

    <p>This is one area where a relatively simple nutritional intervention
    (switching supplement forms) has genuine mechanistic rationale specific
    to your genotype.</p>
    """

def n_gwas_summary(r, trait):
    """Generic bespoke paragraph for GWAS-only traits."""
    pred    = r.get('prediction','')
    pgs     = r.get('pgs_score', 0)
    elevated= r.get('snps_used', 0)
    support = r.get('supporting', [])

    top_genes = []
    for s in support[:4]:
        import re
        m = re.search(r'\(([^)]+)\)', s)
        if m:
            top_genes.append(m.group(1).split('-')[0].strip())

    gene_str = ", ".join(set(top_genes[:3])) if top_genes else "multiple loci"

    return f"""
    <p>{pred} for {trait}. The GWAS polygenic score is {pgs:+.1f} (above population
    average), with {elevated} loci showing elevated risk allele dosage. Key genes
    implicated include {gene_str}.</p>
    <p>{r.get('narrative', '')}</p>
    """

# ─────────────────────────────────────────────────────────────────────────────
# Section builder
# ─────────────────────────────────────────────────────────────────────────────
SECTIONS = [
    ("appearance",     "Physical Appearance & Traits",
     ["eye_color","hair_color","skin_tone","hair_loss","height"]),
    ("cardiovascular", "Cardiovascular Health",
     ["cholesterol","triglycerides","cad","heart_failure",
      "atrial_fibrillation","stroke","blood_pressure"]),
    ("metabolic",      "Metabolic Health",
     ["t2d","bmi","gout","chronic_kidney_disease","vitamin_d","mthfr"]),
    ("neurological",   "Brain, Cognition & Neurological Health",
     ["intelligence","alzheimer","parkinson","depression","adhd","autism",
      "bipolar_disorder","schizophrenia","sleep_duration"]),
    ("cancer",         "Cancer Risk",
     ["melanoma","breast_cancer","prostate_cancer",
      "colorectal_cancer","lung_cancer","bladder_cancer"]),
    ("immune",         "Immune & Inflammatory Conditions",
     ["lupus","rheumatoid_arthritis","inflammatory_bowel",
      "crohn_disease","multiple_sclerosis","psoriasis","asthma"]),
    ("longevity",      "Longevity & Ageing",
     ["longevity"]),
    ("lifestyle",      "Lifestyle, Nutrition & Drug Metabolism",
     ["caffeine_metabolism","alcohol_consumption",
      "lactase_persistence","pharmacogenomics"]),
]

BESPOKE = {
    "eye_color":      n_eye_color,
    "hair_color":     n_hair_color,
    "skin_tone":      n_skin_tone,
    "hair_loss":      n_hair_loss,
    "height":         n_height,
    "intelligence":   n_intelligence,
    "mthfr":          n_mthfr,
    "cholesterol":    n_cholesterol,
    "t2d":            n_t2d,
    "alzheimer":      n_alzheimer,
    "cad":            n_cad,
    "bmi":            n_bmi,
    "triglycerides":  n_triglycerides,
    "depression":     n_depression,
    "longevity":      n_longevity,
}

IMMUNE_TRAITS = {"lupus","rheumatoid_arthritis","inflammatory_bowel",
                 "crohn_disease","multiple_sclerosis","psoriasis","asthma"}

CANCER_TRAITS = {"breast_cancer","prostate_cancer","colorectal_cancer",
                 "melanoma","lung_cancer","bladder_cancer"}

LIFESTYLE_TRAITS = {"alcohol_consumption","caffeine_metabolism","pharmacogenomics"}

def risk_color(pred):
    p = (pred or "").lower()
    if any(w in p for w in ["elevated","high risk"]): return "#ef5350"
    if any(w in p for w in ["moderate","moderately"]): return "#ffa726"
    if any(w in p for w in ["favourable","below average","low risk"]): return "#66bb6a"
    if any(w in p for w in ["mild","average","low genetic"]): return "#78909c"
    return "#42a5f5"

def risk_label(pred):
    p = (pred or "").lower()
    if "elevated" in p:         return "ELEVATED"
    if "moderately" in p:       return "MODERATE"
    if "moderate genetic" in p: return "MODERATE"
    if "favourable" in p:       return "FAVOURABLE"
    if "below average" in p:    return "LOW RISK"
    if "mild" in p:             return "MILD"
    if "average" in p:          return "AVERAGE"
    return ""

def get_narrative_html(key, r, lang="en"):
    trait = r.get("trait", key.replace("_"," ").title())
    if lang == "bg":
        if key in BG:
            return BG[key](r)
        if key in IMMUNE_TRAITS:
            return n_immune_bg(r, trait)
        if key in CANCER_TRAITS:
            return n_cancer_bg(r, trait)
        if key in LIFESTYLE_TRAITS:
            return n_lifestyle_bg(r, trait)
        return n_gwas_summary_bg(r, trait)
    # English
    if key in BESPOKE:
        return BESPOKE[key](r)
    if key in IMMUNE_TRAITS:
        return n_immune(r, trait)
    if key in CANCER_TRAITS:
        return n_cancer(r, trait)
    if key in LIFESTYLE_TRAITS:
        return n_lifestyle(r, trait)
    return n_gwas_summary(r, trait)


# ─────────────────────────────────────────────────────────────────────────────
# BULGARIAN TRANSLATIONS
# Medical review recommended before sharing with patients.
# ─────────────────────────────────────────────────────────────────────────────

SECTIONS_BG = [
    ("appearance",     "Физически характеристики",
     ["eye_color","hair_color","skin_tone","hair_loss","height"]),
    ("cardiovascular", "Сърдечно-съдово здраве",
     ["cholesterol","triglycerides","cad","heart_failure",
      "atrial_fibrillation","stroke","blood_pressure"]),
    ("metabolic",      "Метаболитно здраве",
     ["t2d","bmi","gout","chronic_kidney_disease","vitamin_d","mthfr"]),
    ("neurological",   "Мозък, познание и неврологично здраве",
     ["intelligence","alzheimer","parkinson","depression","adhd","autism",
      "bipolar_disorder","schizophrenia","sleep_duration"]),
    ("cancer",         "Онкологичен риск",
     ["melanoma","breast_cancer","prostate_cancer",
      "colorectal_cancer","lung_cancer","bladder_cancer"]),
    ("immune",         "Имунни и възпалителни заболявания",
     ["lupus","rheumatoid_arthritis","inflammatory_bowel",
      "crohn_disease","multiple_sclerosis","psoriasis","asthma"]),
    ("longevity",      "Дълголетие и стареене",
     ["longevity"]),
    ("lifestyle",      "Начин на живот, хранене и метаболизъм на лекарства",
     ["caffeine_metabolism","alcohol_consumption",
      "lactase_persistence","pharmacogenomics"]),
]

RISK_LABELS_BG = {
    "ELEVATED":   "ПОВИШЕН",
    "MODERATE":   "УМЕРЕН",
    "FAVOURABLE": "БЛАГОПРИЯТЕН",
    "LOW RISK":   "НИСъК РИСК",
    "MILD":       "ЛЕК",
    "AVERAGE":    "СРЕДЕН",
}

def risk_label_bg(pred):
    en = risk_label(pred)
    return RISK_LABELS_BG.get(en, en)

def n_eye_color_bg(r):
    return """
    <p>Прогнозата за цвета на очите попада на границата между синьо и зелено,
    което е точно там, където я поставя вашата генотипна комбинация. Доминиращият
    сигнал е rs12913832 GG — тази единична вариация в гена HERC2 е най-силният
    известен предиктор за цвета на очите при хората. GG е класическият генотип,
    свързан с сини очи, открит при около 97% от синеоките европейци. Сам по себе
    си той би предсказал сини очи.</p>

    <p>Зеленият елемент се въвежда от комбинацията от вторични сигнали, действащи
    в различни посоки. SLC24A4 GT и IRF4 CT са и двете междинни — те нито
    засилват напълно синия сигнал, нито го насочват към кафяво. SLC45A2 GG е
    предковият алел, който не допринася за европейския вариант на изсветляване,
    добавяйки малък противовес. TYR AG (хетерозиготен) намалява умерено синтеза
    на меланин в различни тъкани, включително ириса.</p>

    <p>Крайният резултат: силно намален OCA2-медииран меланинов сигнал от HERC2,
    частично модулиран от междинни алели в поддържащите локуси. Това произвежда
    ирис, по-светъл от кафявия, с конкретен нюанс, намиращ се между синьо и зелено
    в зависимост от условията на осветление и структурата на ириса. Кафявото е
    практически изключено — нямате нито една от класическите алелни комбинации,
    промотиращи кафяво, на ключовите локуси.</p>

    <p>Една практическа бележка: ефектът на TYR CA за намаляване на меланина
    се простира отвъд цвета на очите. Същото намаляване на ензима, което изсветлява
    ириса, намалява и UV-защитния еумеланин в кожата — с реални последици за
    натрупването на увреждания от слънцето, разгледани в раздела за кожата.</p>
    """

def n_hair_color_bg(r):
    return """
    <p>Генетиката на цвета на косата разказва ясна и последователна история:
    средно до тъмнокафява, без червен компонент. Генът MC1R — който функционира
    като основен превключвател между червен/жълт феомеланин и тъмен еумеланин —
    не показва рискови варианти на нито едно от четирите тествани места. Това
    практически изключва червената коса. Наследили сте напълно функционален
    MC1R рецептор, което означава, че меланоцитите ви произвеждат еумеланин
    по подразбиране.</p>

    <p>Доминиращият пигментационен сигнал е SLC45A2 GG — предковият алел,
    разпространен сред непервоевропейски и по-тъмно пигментирани популации,
    който не допринася за европейския вариант на изсветляване на косата.
    Комбиниран с липсата на MC1R варианти, това установява ясна тъмна основа.</p>

    <p>Единственият умерен сигнал за изсветляване идва от TYR AC (хетерозиготен),
    който намалява ефективността на ензима тирозиназа. Това е умерен ефект —
    може да допринесе за известно омекотяване на най-тъмния възможен нюанс,
    поради което прогнозата е средно до тъмно, а не черна.</p>
    """

def n_skin_tone_bg(r):
    return """
    <p>Генетиката на пигментацията на кожата разкрива интересно напрежение между
    два противоположни фактора, което произвежда среден, а не краен резултат.</p>

    <p>Сигналът за изсветляване е съществен: SLC24A5 AA е производният европейски
    алел на единствения най-влиятелен локус за цвета на кожата. Тази вариация се
    е разпространила сред европейските и южноазиатски популации преди около
    8 000 години — вероятно като адаптация към среди с ниско UV лъчение.
    Нейният ефект е достатъчно голям, за да обясни значителна част от разликата
    в пигментацията между европейците и западноафриканците.</p>

    <p>Противовесът е SLC45A2 GG — предковият алел, който не допринася за
    допълнително изсветляване. Комбинацията дава светъл до среден тон, а не
    много бледа кожа. TYR CA (хетерозиготен) намалява меланиновия изход,
    добавяйки склонност към лунички и намалена UV защита.</p>

    <p>Практическото следствие: кожата ви се загаря умерено, но изгаря
    по-лесно от средното. SPF50 не е прекалена предпазна мярка за този профил —
    тя е подходящата основна защита, прилагана последователно.</p>
    """

def n_cholesterol_bg(r):
    return """
    <p>Генетиката на холестерола ви представя смесена, но в крайна сметка
    умерена картина. Най-важното откритие е това, което липсва: носите rs7412 CC,
    което е сигналът за APOE ε2 алела — свързан с по-нисък LDL и намален
    сърдечно-съдов риск. Това е наистина благоприятна находка.</p>

    <p>Бележката на предпазливост е, че rs429358 — вторият SNP, необходим за
    пълното определяне на APOE генотипа — не е бил на вашия чип. Клиничен тест
    за APOE генотип (евтин, наличен при личния лекар) би решил това окончателно
    и си заслужава поради последиците за сърдечно-съдовия и Алцхаймеровия риск.</p>

    <p>Освен APOE: rs629301 TT при SORT1/CELSR2 носи два копия на алела,
    повишаващ LDL. rs11591147 GG при PCSK9 не показва защитен алел за
    намаляване на функцията. LPA rs10455872 AA не е рисков — не носите
    варианта, повишаващ Lp(a), което е значима защитна находка.</p>

    <p>Диета и упражнения са подходящ първи подход. Препоръчват се ежегодни
    липидни панели и изясняване на пълния APOE статус.</p>
    """

def n_t2d_bg(r):
    return """
    <p>Генетичният профил за диабет тип 2 изисква внимателен прочит, защото
    обобщеният брой — повишен риск — скрива важен модел в детайлите.</p>

    <p>Вие сте хетерозиготни почти на всеки основен T2D локус: TCF7L2 CT
    (едно рисково копие), KCNJ11 CT, SLC30A8 TC, CDKN2A/B CT, HHEX TC,
    IGF2BP2 GT, FTO CA. Тази последователна хетерозиготност на седем
    независими локуса е определящата характеристика на вашия профил —
    умерено генетично натоварване, разпределено широко, а не тежко натоварване
    на един ген.</p>

    <p>TCF7L2 е най-важната находка — най-силно репликираният общ вариант за T2D.
    Хетерозиготните носители имат около 1,4 пъти по-висок базов риск.
    Критично: носителите на TCF7L2 риск реагират особено добре на промени
    в начина на живот — умерена загуба на тегло и 150 минути упражнения
    седмично са доказано ефективни.</p>

    <p>Генетичният риск не е съдба — начинът на живот взаимодейства силно
    с тази генетична предразположеност. Периодичното изследване на кръвната
    захар и HbA1c е подходящо.</p>
    """

def n_alzheimer_bg(r):
    return """
    <p>Генетичният профил за Алцхаймер съдържа може би най-обнадеждаващата
    находка в целия доклад. rs7412 CC съответства на APOE ε2 алела —
    а ε2 е най-силно известният защитен вариант срещу Алцхаймер с късно
    начало. Носителите на ε2 имат около 50% по-нисък риск спрямо общия
    ε3/ε3 генотип и са значително свръхпредставени сред когнитивно
    здравите индивиди на 85 и повече години.</p>

    <p>Предупреждението, както е отбелязано в раздела за холестерола, е,
    че rs429358 не е бил на вашия чип. Дори при смесен ε2/ε4 генотип,
    защитният сигнал от ε2 остава реален и значим.</p>

    <p>Най-добре доказаните защитни фактори: сърдечно-съдово здраве,
    редовна аеробна активност, когнитивна ангажираност, качествен сън
    (по време на който мозъкът изчиства амилоид) и контрол на кръвното
    налягане. Тези фактори имат пряка неврологична релевантност за
    вашия генотип.</p>
    """

def n_cad_bg(r):
    return """
    <p>Коронарната артериална болест е областта, в която генетичният профил
    показва най-значимото клинично повишение. Локусът 9p21 (CDKN2B-AS1) —
    най-репликираният общ вариант за КАБ — се появява два пъти: rs4977574 AG
    и rs1333049 CG (и двата с едно рисково копие). Тези два варианта са
    адитивни с добре установени ефекти.</p>

    <p>Важното за локуса 9p21 е, че той действа независимо от LDL холестерола —
    стандартните липидни изследвания не улавят изцяло този риск. Препоръчва
    се внимание към пълния сърдечно-съдов рисков профил: кръвно налягане,
    отказ от тютюнопушене, диабет и LDL. Статини и промени в начина на живот
    са ефективни независимо от генотипа.</p>
    """

def n_bmi_bg(r):
    return """
    <p>Генетиката на ИТМ показва умерено натоварване, като ключовата находка
    е хетерозиготността за FTO. rs9939609 AT означава едно копие на рисковия
    алел на FTO (A) — всеки A алел добавя около 0,4 kg/m² към средния ИТМ.</p>

    <p>Най-важното за вашия FTO генотип: мета-анализ от 2011 г. (Kilpeläinen
    и сътр., PLOS Medicine, 218 000 участника) демонстрира, че носителите на
    рисковия алел за FTO, които са физически активни, имат стойности на ИТМ,
    практически идентични с тези на не-носителите. Генетичната предразположеност
    съществува; дали ще се изяви, зависи съществено от нивото на физическа
    активност.</p>
    """

def n_triglycerides_bg(r):
    return """
    <p>Генетиката на триглицеридите показва умерено повишение с един важен
    защитен противовес. Основният рисков сигнал е APOA5 AG (rs662799
    хетерозиготен) — доминиращият триглицериден локус, чийто G алел нарушава
    функцията на APOA5 за активиране на липопротеинова липаза.</p>

    <p>Ключовата защитна находка е LPL rs328 CC — алелът S447X с придобита
    функция, чиято C форма създава хиперактивна липопротеинова липаза,
    която съществено подобрява клирънса на триглицеридите.</p>

    <p>Хранителните последици са преки: вашата APOA5 хетерозиготност означава,
    че приемът на въглехидрати и алкохол има усилен ефект върху нивата на
    триглицеридите. Омега-3 добавки (EPA/DHA) са особено ефективни при
    носители на APOA5 рискови алели — клиничните проучвания показват
    20-30% намаление на триглицеридите.</p>
    """

def n_depression_bg(r):
    return """
    <p>Генетиката на депресията разказва нюансирана история, която изисква
    внимателен контекст. BDNF rs6265 CT означава едно копие на Val66Met —
    Met алелът е свързан с намалена активност-зависима секреция на BDNF.
    BDNF е основният невротрофичен фактор на мозъка, поддържащ невронното
    оцеляване и пластичността.</p>

    <p>COMT rs4680 GG е профилът „Воин" (Val/Val) — по-висок разпад на
    допамин в префронталния кортекс, което типично означава по-добра
    устойчивост на стрес и изпълнителна функция под натиск.</p>

    <p>Нивата на BDNF са силно повлияни от аеробните упражнения — редовната
    физическа активност е един от най-надеждните стимулатори на BDNF и
    съществено компенсира намалената базова секреция на Met алела.</p>
    """

def n_longevity_bg(r):
    return """
    <p>Генетиката на дълголетието показва умерени положителни сигнали,
    като картината с APOE е централна. rs7412 CC съответства на APOE ε2 алела
    — и ε2 е последователно свръхпредставен сред стогодишниците в множество
    независими кохортни проучвания.</p>

    <p>Вариантите на CETP добавят реален допълнителен сигнал за дълголетие.
    CETP rs3764814 CT и rs5882 AG сочат към по-висок HDL холестерол —
    повишеният HDL е последователно свързан с дълголетие, особено в
    еврейски ашкенази и японски кохорти.</p>

    <p>Доказателствата от всички проучвания за дълголетие последователно
    показват, че факторите на начина на живот — особено избягване на
    тютюнопушенето, редовна физическа активност, средиземноморска диета и
    поддържане на социална ангажираност — обясняват повече от вариацията
    при достигане на изключителна възраст, отколкото генетиката.</p>
    """

def n_mthfr_bg(r):
    return """
    <p>Генетиката на метаболизма на фолат и В-витамини е най-клинично
    приложимата хранителна находка в този доклад и заслужава внимателно
    разглеждане, тъй като липсваше от основния здравен доклад.</p>

    <p>Носите два MTHFR варианта едновременно — сложна хетерозиготност,
    по-значима от всеки вариант поотделно:</p>

    <p><strong>MTHFR C677T (rs1801133) GA — хетерозиготен.</strong> T алелът
    намалява активността на ензима MTHFR с около 35% при хетерозиготите.
    MTHFR е ключовият ензим, превръщащ фолата в активната форма (5-метилТХФ),
    използвана за рециклиране на хомоцистеин обратно до метионин. Намалената
    активност означава по-бавен клирънс на хомоцистеина и потенциално повишен
    плазмен хомоцистеин — рисков фактор за сърдечно-съдови и неврологични
    заболявания.</p>

    <p><strong>MTHFR A1298C (rs1801131) GT — хетерозиготен.</strong> Комбиниран
    с C677T хетерозиготността (сложна хетерозиготност), функционалната
    ензимна активност може да бъде намалена с 50-60%.</p>

    <p>Практическите последици са преки: приемайте <strong>метилфолат
    (5-MTHF)</strong>, а не фолиева киселина, и <strong>метилкобаламин</strong>
    вместо цианокобаламин. Изследвайте нивата на хомоцистеин, фолат и В12 в
    кръвта, за да потвърдите метаболитния статус.</p>

    <p>Повишеният хомоцистеин е независим рисков фактор за коронарна артериална
    болест и инсулт — две области, при които GWAS данните вече показват
    повишени сигнали. Адекватното допълване с метилфолат и метилкобаламин
    е доказано ефективно за нормализиране на хомоцистеина при носители на
    MTHFR.</p>
    """

def n_hair_loss_bg(r):
    return """
    <p>Генетиката на косопада разказва обнадеждаваща история. X-свързаният
    AR/EDA2R локус — най-силният сигнал за мъжки тип алопеция, с OR над 2,0
    в публикувани GWAS — показва rs2497938 CC, което е генотипът без риск.
    Този локус се наследява по майчина линия (на X хромозомата).</p>

    <p>GWAS потвърждава: само 1 повишен локус от 15 генотипирани, с PGS от
    +2,8 — най-ниският значим полигенен резултат в целия профил. Мъжкият тип
    алопеция е около 80% наследствена, което прави тази ниска стойност
    наистина информативна.</p>
    """

def n_height_bg(r):
    return """
    <p>Ръстът е едно от най-полигенните черти в човешкия геном — хиляди
    варианти, всеки допринасящ с части от милиметъра. Вашият полигенен резултат
    от +401 от 29 повишени локуса е вторият по величина количествен резултат
    в профила и последователно сочи над популационната средна.</p>

    <p>HMGA2 rs1042725 TT е добре охарактеризираният куриран локус на вашия
    чип. TT на тази позиция е генотипът, свързан с по-висок ръст, допринасящ
    с приблизително 0,4 cm на алел в мащабни проучвания.</p>

    <p>Ръстът е около 80% наследствен при добре хранените популации. Реализираният
    ръст зависи съществено от детското хранене, съня и здравето.</p>
    """

def n_intelligence_bg(r):
    return """
    <p>Когнитивната генетика съдържа най-високия полигенен резултат в целия
    доклад: PGS +1064 от 8 повишени локуса. Важен методологичен контекст:
    GWAS проучванията за интелигентност включват образователните постижения
    като прокси фенотип, поради което резултатът отразява смес от когнитивни
    способности, образователна предразположеност и неврологична устойчивост.</p>

    <p>COMT rs4680 GG е генотипът Val/Val — „Воинският" профил. По-висока
    ензимна активност на COMT означава по-бърз разпад на допамин в
    префронталния кортекс, произвеждайки по-добра работна памет и
    изпълнителна функция под когнитивно натоварване и стрес.</p>

    <p>BDNF rs6265 CT (Val66Met хетерозиготен) е нюансиращият фактор.
    Хетерозиготността означава, че един функционален Val алел остава —
    това е частично, а не пълно намаление. Редовните аеробни упражнения
    са един от най-надеждните стимулатори на BDNF и съществено компенсират
    намалената базова секреция на Met алела.</p>
    """

def n_immune_bg(r, trait):
    pred     = r.get('prediction','')
    pgs      = r.get('pgs_score', 0)
    elevated = r.get('snps_used', 0)
    return f"""
    <p>{pred} за {trait}. Полигенният резултат от GWAS е {pgs:+.1f}
    (над средното за популацията); {elevated} локуса показват повишена
    дозировка на рисковия алел.</p>

    <p>Важен модел в имунния профил: повишени сигнали се появяват последователно
    при лупус, ревматоиден артрит, възпалително чревно заболяване, болест на Крон
    и псориазис. Тези заболявания споделят генетична архитектура, особено в HLA
    региона и сигналните пътища на цитокините. Това предполага реална основна
    тема на имунна чувствителност.</p>

    <p>Същите фактори на начина на живот, намаляващи единия, са склонни да намаляват
    другите: противовъзпалителна диета, управление на стреса, достатъчен сън и
    поддържане на разнообразна чревна микробиота.</p>
    """

def n_cancer_bg(r, trait):
    pred     = r.get('prediction','')
    pgs      = r.get('pgs_score', 0)
    elevated = r.get('snps_used', 0)
    narr     = r.get('narrative','')
    return f"""
    <p>{pred} за {trait}. Полигенният резултат от GWAS е {pgs:+.1f},
    с {elevated} локуса, показващи повишена дозировка на рисковия алел.</p>
    <p>{narr}</p>
    """

def n_lifestyle_bg(r, trait):
    pred = r.get('prediction','')
    narr = r.get('narrative','')
    return f"<p><strong>{pred}</strong></p><p>{narr}</p>"

def n_gwas_summary_bg(r, trait):
    pred     = r.get('prediction','')
    pgs      = r.get('pgs_score', 0)
    elevated = r.get('snps_used', 0)
    return f"""
    <p>{pred} за {trait}. Полигенният резултат от GWAS е {pgs:+.1f}
    (над средното за популацията), с {elevated} локуса, показващи повишена
    дозировка на рисковия алел.</p>
    <p>{r.get('narrative','')}</p>
    """

BG = {
    "eye_color":     n_eye_color_bg,
    "hair_color":    n_hair_color_bg,
    "skin_tone":     n_skin_tone_bg,
    "hair_loss":     n_hair_loss_bg,
    "height":        n_height_bg,
    "intelligence":  n_intelligence_bg,
    "mthfr":         n_mthfr_bg,
    "cholesterol":   n_cholesterol_bg,
    "t2d":           n_t2d_bg,
    "alzheimer":     n_alzheimer_bg,
    "cad":           n_cad_bg,
    "bmi":           n_bmi_bg,
    "triglycerides": n_triglycerides_bg,
    "depression":    n_depression_bg,
    "longevity":     n_longevity_bg,
}

# ====================== LANGUAGE CONFIG ======================
# Place this AFTER SECTIONS, SECTIONS_BG, and BG dict are defined

LANG_CONFIG = {
    "en": {
        "html_lang": "en",
        "title_suffix": "— Genetic Health Narrative",
        "eyebrow": "Personal Genomics Report",
        "subtitle": "Genetic Health Narrative",
        "contents": "Contents",
        "traits_label": "Traits analysed",
        "elevated_label": "Elevated signals",
        "favourable_label": "Favourable signals",
        "generated_label": "Generated",
        "sections": SECTIONS,           # ← now defined
        "risk_label_fn": risk_label,
        "disclaimer": """<strong>Important:</strong> This report is for personal educational purposes only — 
not a medical diagnosis. Genetic predisposition does not determine health outcomes. 
Please discuss any findings of concern with a qualified healthcare professional."""
    },
    "bg": {
        "html_lang": "bg",
        "title_suffix": "— Генетичен здравен нарратив",
        "eyebrow": "Персонален геномичен доклад",
        "subtitle": "Генетичен здравен нарратив",
        "contents": "Съдържание",
        "traits_label": "Анализирани черти",
        "elevated_label": "Повишени сигнали",
        "favourable_label": "Благоприятни сигнали",
        "generated_label": "Генериран",
        "sections": SECTIONS_BG,        # ← now defined
        "risk_label_fn": risk_label_bg,
        "disclaimer": """<strong>Важно:</strong> Този доклад е само за образователни цели — 
не е медицинска диагноза. Генетичната предразположеност не определя здравните резултати. 
Моля, обсъдете важни находки с квалифициран лекар."""
    }
}


# ==================== BUILD SECTIONS ====================
def build_sections(synthesis, lang="en"):
    config = LANG_CONFIG[lang]
    out = ""
    for sid, stitle, keys in config["sections"]:
        traits = [(k, synthesis[k]) for k in keys if k in synthesis]
        if not traits:
            continue
        content = ""
        for key, r in traits:
            trait = r.get("trait", key.replace("_"," ").title())
            pred  = r.get("prediction","")
            color = risk_color(pred)
            label = config["risk_label_fn"](pred)
            icon  = r.get("icon","⬡")
            narr  = get_narrative_html(key, r, lang)

            content += f"""
            <div class="trait-block" id="n_{key}">
              <div class="trait-header">
                <span class="trait-icon">{icon}</span>
                <h3 class="trait-name">{trait}</h3>
                {"<span class='risk-pill' style='background:" + color + ";'>" + label + "</span>" if label else ""}
              </div>
              <div class="finding-bar" style="border-left-color:{color};">
                <strong class="finding-headline">{pred}</strong>
              </div>
              <div class="narrative-body">{narr}</div>
            </div>"""
        out += f"""
        <section class="report-section" id="s_{sid}">
          <h2 class="section-heading">{stitle}</h2>
          {content}
        </section>"""
    return out

# ==================== RENDER ====================
def render(person, synthesis, results_dir, lang="en"):
    config = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    today = date.today().strftime("%d %B %Y" if lang == "bg" else "%B %d, %Y")

    sections_html = build_sections(synthesis, lang)

    total = len(synthesis)
    elevated = sum(1 for r in synthesis.values() if "elevated" in (r.get("prediction","")).lower())
    favourable = sum(1 for r in synthesis.values() if any(w in (r.get("prediction","")).lower() for w in ["favourable","below average","low risk"]))

    nav = "".join(f'<a href="#s_{sid}" class="nav-link">{stitle}</a>' for sid, stitle, keys in config["sections"] if any(k in synthesis for k in keys))

    # Your original HTML template with config variables
    html = f"""<!DOCTYPE html>
<html lang="{config['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{person} {config['title_suffix']}</title>
<style>
/* Paste your full original CSS block here */
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#faf9f7;--surface:#ffffff;--border:#e5e0d8;--text:#1c1917;--muted:#6b6560;--accent:#1d4e7a;--light:#f0ece4;--radius:8px;font-family:Georgia,"Times New Roman",serif;}}
body{{background:var(--bg);color:var(--text);font-size:17px;line-height:1.85}}
/* ... your full CSS ... */
</style>
</head>
<body>
<nav class="nav-sidebar">
  <h4>{config['contents']}</h4>
  {nav}
</nav>
<div class="cover">
  <p class="cover-eyebrow">{config['eyebrow']}</p>
  <h1>{person}</h1>
  <p class="cover-sub">{config['subtitle']}</p>
  <div class="cover-stats">
    <div class="cs"><span class="cs-val">{total}</span><span class="cs-label">{config['traits_label']}</span></div>
    <div class="cs"><span class="cs-val" style="color:#f87171">{elevated}</span><span class="cs-label">{config['elevated_label']}</span></div>
    <div class="cs"><span class="cs-val" style="color:#86efac">{favourable}</span><span class="cs-label">{config['favourable_label']}</span></div>
    <div class="cs"><span class="cs-val">{today}</span><span class="cs-label">{config['generated_label']}</span></div>
  </div>
</div>
<div class="main">
  <div class="disclaimer">
    {config['disclaimer']}
  </div>
  {sections_html}
</div>
</body>
</html>"""

    suffix = "_bg" if lang == "bg" else ""
    out = results_dir / f"narrative_{person}{suffix}.html"
    out.write_text(html, encoding="utf-8")
    print(f"✅ Saved: {out.name}")
    return out

# ==================== ENTRY POINTS ====================
def generate(person_cfg, lang="en", verbose=True):
    name = person_cfg["name"]
    results_dir = ROOT_DIR / person_cfg["results_dir"]
    synth_path = results_dir / "synthesis.json"

    if not synth_path.exists():
        print(f"  WARN: synthesis.json not found for {name}")
        return None

    synthesis = json.load(open(synth_path))
    out = render(name, synthesis, results_dir, lang)
    if verbose:
        print(f"  OK   Narrative ({lang}) → {out.name}")
    return out

def main():
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--person")
    grp.add_argument("--all", action="store_true")
    parser.add_argument("--lang", choices=["en", "bg"], default="en")
    args = parser.parse_args()

    cfg = json.load(open(CONFIG))
    people = cfg["people"]
    targets = people if args.all else [p for p in people if p["name"].lower() == args.person.lower()]

    if not targets:
        print("ERROR: person not found")
        sys.exit(1)

    for pcfg in targets:
        print(f"\n--- Generating {args.lang.upper()} narrative for {pcfg['name']} ---")
        generate(pcfg, lang=args.lang)

if __name__ == "__main__":
    main()