import re
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
# BESPOKE NARRATIVES - written for Minko's specific genotypes
# Each function receives the synthesis dict for that trait and returns HTML prose
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
    return """
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

    <p>The GWAS shows 18 longevity-associated loci with PGS +62.4. Combined with
    the APOE ε2 signal and CETP variants, the overall longevity picture is moderately
    favourable at the genetic level. The evidence across all longevity studies
    consistently shows that lifestyle factors - particularly avoiding smoking, regular
    physical activity, Mediterranean-style diet, and maintaining social engagement -
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

def n_systems_synthesis(risk_data):
    """High-level synthesis pulling directly from risk_data."""
    # Look for both High and Moderate risks
    priority_systems = {system: data for system, data in risk_data.items() 
                        if data.get("risk_level") in ["High", "Moderate"]}
    
    priority_list = ""
    if not priority_systems:
        priority_list = "<li>No elevated risk markers detected across biological systems.</li>"
    else:
        for system, data in priority_systems.items():
            level = data.get("risk_level")
            priority_list += f"<li><strong>{system}</strong> - Status: {level}. Review routine wellness protocols.</li>"
    
    return f"""
    <h2>Systems-Level Synthesis</h2>
    <p>Your genetic profile analysis across major biological systems shows the following areas for consideration:</p>
    <ul>
      {priority_list}
    </ul>
    <p>These findings help prioritize lifestyle adjustments. Focus on maintaining consistency in your wellness routines.</p>
    """

def n_gwas_summary(r, trait):
    """GWAS Summary handler with dual paragraphs: statistical overview + detailed variant breakdown."""
    import re
    pgs = r.get('pgs_score', 0)
    elevated = r.get('snps_used', 0)
    pred = r.get('prediction', '')
    support = r.get('supporting', [])
    
    # Extract top gene names for the statistical paragraph
    top_genes = []
    for s in support[:5]:
        m = re.search(r'\(([^)]+)\)', s)
        if m:
            gene_candidate = m.group(1).split('-')[0].strip()
            if gene_candidate and len(gene_candidate) < 10:
                top_genes.append(gene_candidate)
    gene_str = ", ".join(list(dict.fromkeys(top_genes))[:3]) if top_genes else "key regulatory loci"

    # Paragraph 1: Statistical Overview
    para1 = f"{pred} for {trait}. The GWAS polygenic score is {pgs:+.1f} (above population average), with {elevated} loci showing elevated risk allele dosage. Key genes implicated include {gene_str}."

    # Explicit multi-line custom dictionaries for rich biological breakdowns (Paragraph 2)
    FULL_SUMMARIES_P2 = {
        "hair color": f"Medium to dark brown — No MC1R red hair variants detected — red hair is ruled out. SLC45A2 GG ancestral allele is the dominant pigmentation signal — dark hair baseline. TYR CA reduces melanin output modestly, consistent with the overall pigmentation profile. {elevated} SNPs combined.",
        "eye color": f"Based on {elevated} of {elevated} IrisPlex marker SNPs present on your chip, there is moderate agreement toward blue. The single strongest marker, rs12913832 (GG), points blue, and this locus alone drives most of IrisPlex's real-world predictive accuracy. Genotype and direction of effect for each marker is listed below.",
        "parkinson": f"Reflecting both monogenic risk contributions (such as LRRK2 and SNCA) and broader sporadic susceptibility across dopaminergic neuronal maintenance and mitochondrial quality control pathways.",
        "schizophrenia": f"Features a highly polygenic architecture with a strong immunological/MHC component, pointing to synaptic pruning and glutamatergic transmission pathways.",
    }
    
    key_lower = r.get("trait", "").lower()
    para2 = ""
    for k, text in FULL_SUMMARIES_P2.items():
        if k in key_lower:
            para2 = text
            break
            
    # Fallback paragraph 2 if not explicitly mapped
    if not para2 and support:
        sample_support = " ".join(support[:2])
        para2 = f"Observed variant alleles across {elevated} evaluated loci indicate combined polygenic contribution. Supporting markers show localized effects: {sample_support}."
    elif not para2:
        para2 = f"Polygenic architecture derived from {elevated} contributing loci."

    return f"<p>{para1}</p><br><p>{para2}</p>"

def n_pharmacogenomics(r):
    """High-level pharmacogenomics summary."""
    try:
        with open("reports/pharmgkb_matches.json") as f:
            matches = json.load(f)
        
        # Group by drug or phenotype for summary
        from collections import Counter
        drugs = Counter(m.get('drug', 'Unknown') for m in matches)
        top_drugs = drugs.most_common(8)
        
    except:
        return "<p>No pharmacogenomics data available yet.</p>"

    html = """
    <p>Your pharmacogenomics profile (from PharmGKB) shows potential interactions with several medications. Here are the most relevant ones based on your SNPs:</p>
    <ul>
    """
    for drug, count in top_drugs:
        html += f"<li><strong>{drug}</strong> - {count} variant matches</li>"
    html += "</ul>"
    html += "<p><em>Recommendation: Discuss these with your doctor or pharmacist before starting new medications, especially antidepressants, painkillers, or blood thinners.</em></p>"
    return html

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
    "eye_color": n_eye_color,
    "hair_color": n_hair_color,
    "skin_tone": n_skin_tone,
    "hair_loss": n_hair_loss,
    "height": n_height,
    "intelligence": n_intelligence,
    "mthfr": n_mthfr,
    "cholesterol": n_cholesterol,
    "t2d": n_t2d,
    "alzheimer": n_alzheimer,
    "cad": n_cad,
    "bmi": n_bmi,
    "triglycerides": n_triglycerides,
    "depression": n_depression,
    "longevity": n_longevity,
    "vitamin_d": n_vitamin_d,           # ← make sure this is here
    "pharmacogenomics": n_pharmacogenomics
}

IMMUNE_TRAITS = {"lupus","rheumatoid_arthritis","inflammatory_bowel",
                 "crohn_disease","multiple_sclerosis","psoriasis","asthma"}

CANCER_TRAITS = {"breast_cancer","prostate_cancer","colorectal_cancer",
                 "melanoma","lung_cancer","bladder_cancer"}

LIFESTYLE_TRAITS = {"alcohol_consumption","caffeine_metabolism","pharmacogenomics"}

def n_systems_overview(systems_data):
    """High-level synthesis of biological systems."""
    return """
    <h2>Systems-Level Overview</h2>
    <p>Your genetic profile shows the following patterns across major biological systems:</p>
    <ul>
      <li><strong>Cardiometabolic Axis</strong>: Notable loading (10 traits). Focus on blood pressure, lipids, and insulin sensitivity.</li>
      <li><strong>Neuro-Cognitive Axis</strong>: Moderate loading. Cognitive health, mood, and neurodegeneration deserve attention.</li>
      <li><strong>Immune/Inflammatory Axis</strong>: Significant activity. Prioritize anti-inflammatory lifestyle.</li>
      <li><strong>Oncological Axis</strong>: Several elevated signals. Standard screening + lifestyle prevention is wise.</li>
    </ul>
    <p><strong>Top Priority Areas:</strong> Cardiometabolic and Immune systems appear to be your strongest genetic themes.</p>
    """

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
    """Generate both the styled GWAS Summary card and the Deeper Analysis card."""
    trait = r.get("trait", key.replace("_", " ").title())
    
    # 1. Top Card: GWAS Summary
    summary_html = n_gwas_summary(r, trait)
    card_top = f"""
    <div style="background:#f8f9fa; padding:1.2rem; border-left:4px solid #1e3a8a; margin:1.2rem 0; border-radius:4px;">
        <strong>GWAS Summary</strong><br>
        {summary_html}
    </div>
    """
    
    # 2. Bottom Card: Deeper Analysis (Robust Key Matching)
    bespoke_content = ""
    norm_key = key.strip().lower().replace(" ", "_")
    alt_key = key.strip().lower().replace("_", " ")
    if norm_key in (
        "atrial_fibrillation",
        "stroke",
        "heart_failure",
        "gout",
    ):
        print("=" * 70)
        print("key        :", repr(key))
        print("norm_key   :", repr(norm_key))
        print("id(BESPOKE):", id(BESPOKE))
        print("len(BESPOKE):", len(BESPOKE))
        print("Contains atrial_fibrillation?", "atrial_fibrillation" in BESPOKE)
        print("Contains stroke?", "stroke" in BESPOKE)
        print("Contains heart_failure?", "heart_failure" in BESPOKE)
        print("Contains gout?", "gout" in BESPOKE)
        print("Nearby keys:",
          [k for k in BESPOKE.keys()
           if any(x in k for x in ("atrial", "stroke", "heart", "gout"))])
    
    if "atrial" in key:
        print("Closest BESPOKE keys:")
        for k in BESPOKE:
            if "atrial" in k:
                print(repr(k))
    print("=" * 70)
    print("key       :", repr(key))
    print("norm_key  :", repr(norm_key))
    print("alt_key   :", repr(alt_key))

    print("norm in BESPOKE:", norm_key in BESPOKE)
    print("key  in BESPOKE:", key in BESPOKE)
    print("'atrial_fibrillation' in BESPOKE:", "atrial_fibrillation" in BESPOKE)

    if norm_key in BESPOKE:
        print("MATCHED norm_key")
        bespoke_content = BESPOKE[norm_key](r)
    elif alt_key in BESPOKE:
        print("MATCHED alt_key")
        bespoke_content = BESPOKE[alt_key](r)
    elif key in BESPOKE:
        print("MATCHED key")
        bespoke_content = BESPOKE[key](r)
    else:
        print("FALLBACK")
        print("Nearby keys:",
          [k for k in BESPOKE if "atrial" in k or "stroke" in k or "heart" in k])
        bespoke_content = f"<p>{r.get('narrative', 'No additional deep analysis available.')}</p>"
        
    card_bottom = f"""
    <div style="background:#f0f4f8; padding:1.2rem; margin:1.2rem 0; border-radius:4px;">
        <strong>Deeper Analysis</strong><br>
        {bespoke_content}
    </div>
    """
    
    return card_top + card_bottom

# ─────────────────────────────────────────────────────────────────────────────
# NEW BESPOKE NARRATIVES - remaining conditions
# ─────────────────────────────────────────────────────────────────────────────

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
    pgs = r.get("pgs_score", 22.8)
    return f"""
    <p>Your rheumatoid arthritis (RA) genetics display 6 elevated loci with a PGS of
    {pgs:+.1f}. RA heritability is estimated around 60%, with genetic architecture heavily
    tied to immune regulation, antigen presentation, and T-cell activation pathways.</p>

    <p>The key signals in your data include variants associated with the shared epitope
    regions and secondary cytokine response networks. Like your other autoimmune signals,
    RA risk is fundamentally about how your immune cells process self versus non-self
    antigens under chronic environmental or metabolic stress.</p>

    <p>The practical takeaway aligns seamlessly with your overarching immune management
    strategy: controlling systemic inflammation through targeted omega-3 intake,
    maintaining robust vitamin D status (navigating your VDR sensitivities), and
    protecting gut barrier integrity to minimize systemic antigenic load.</p>
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
    pgs = r.get("pgs_score", 21.3)
    return f"""
    <p>Your psoriasis genetics show 7 elevated loci with a PGS of {pgs:+.1f}. Psoriasis
    is a chronic immune-mediated skin condition driven primarily by the IL-23/Th17 axis,
    setting it apart slightly from the Th2-dominant profile of eczema and asthma.</p>

    <p>The elevated loci in your data include variants influencing keratinocyte proliferation
    and immune cell signaling. This ties directly into your broader autoimmune thread:
    your genome carries multiple minor elevations across distinct immunological branches
    (Th1, Th2, and Th17), painting a picture of an overall reactive immune network.</p>

    <p>Managing systemic triggers-such as metabolic inflammation, glycemic variability,
    and vitamin D insufficiency-helps keep these multi-axis immune signals quiet and
    prevents amplification across skin and mucosal tissues.</p>
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

def n_longevity(r):
    pgs = r.get("pgs_score", 19.4)
    return f"""
    <p>Your exceptional longevity and healthspan genetics show a stable polygenic score
    of {pgs:+.1f}. Genetic contributions to lifespan become increasingly powerful at
    extreme old age, while mid-life healthspan is governed largely by the cumulative
    management of modifiable cardiovascular, metabolic, and inflammatory risks.</p>

    <p>The key genetic markers associated with healthy aging include variants near the
    FOXO3A and APOE loci, which regulate cellular stress resistance, DNA repair efficiency,
    and lipid transport.</p>

    <p>The overarching theme of your entire genetic report is that your destiny is not
    determined by a single extreme monogenic flaw, but by a complex web of moderate
    polygenic predispositions. Because your primary risks-cardiovascular loading,
    metabolic efficiency, and immune reactivity-are entirely addressable through
    targeted lifestyle, dietary, and supplemental choices, your actual healthspan
    remains firmly within your control.</p>
    """

# Update BESPOKE dictionary with batch 2 additions
# Explicitly mapped bespoke handlers to bypass generic fallback
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# BESPOKE NARRATIVES - Batch 1 (Cardiovascular, Neurological, Immune)
# ─────────────────────────────────────────────────────────────────────────────

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
    as a direct byproduct via the ATP depletion pathway. Alcohol, particularly
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
    signals clustering around glomerular filtration rate (eGFR) regulation and
    renal tubular transport.</p>

    <p>The most relevant finding in the context of your overall profile is the
    mechanistic overlap between your CKD genetic signal and your other risk factors.
    Your T2D genetic loading (TCF7L2, KCNJ11, CCND2-AS1 elevated hits) and your
    hypertension-relevant signals are the primary known causes of CKD at the
    population level — diabetic nephropathy and hypertensive nephrosclerosis
    account for approximately 60% of all CKD cases. Your genetics are not
    pointing to a rare kidney-specific disease; they are amplifying the upstream
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



# ─────────────────────────────────────────────────────────────────────────────
# CANCER NARRATIVES — specific to Minko's elevated loci
# ─────────────────────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────────────────────
# IMMUNE NARRATIVES — specific bespoke versions
# ─────────────────────────────────────────────────────────────────────────────

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
    your TYK2 GG genotype would make you a particularly strong candidate
    for this mechanism of action over general immunosuppressants.</p>

    <p>The same dietary and lifestyle recommendations apply as for IBD
    generally — with particular emphasis on stress management, since the
    gut-brain axis is especially relevant in Crohn's: psychological stress
    directly activates intestinal mast cells and alters tight junction
    permeability via the same neural pathways that regulate your
    noradrenergic stress response (relevant to your RGS2 CC finding).</p>
    """

def n_rheumatoid_arthritis(r):
    pgs = r.get("pgs_score", 40.4)
    return f"""
    <p>Your rheumatoid arthritis genetics show 10 elevated loci with a PGS of
    {pgs:+.1f}. RA heritability is approximately 60%, with HLA-DRB1 alleles
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

# ─────────────────────────────────────────────────────────────────────────────
# LIFESTYLE NARRATIVES
# ─────────────────────────────────────────────────────────────────────────────

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
    pgs = r.get("pgs_score", 0)
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

# ─────────────────────────────────────────────────────────────────────────────
# FINAL BESPOKE REGISTRY
# Canonical trait keys only (snake_case)
# ─────────────────────────────────────────────────────────────────────────────
BESPOKE.update({

    # Appearance
    "eye_color":                n_eye_color,
    "hair_color":               n_hair_color,
    "skin_tone":                n_skin_tone,
    "hair_loss":                n_hair_loss,
    "height":                   n_height,

    # Cardiometabolic
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

    # Neurology / Psychiatry
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

    # Cancers
    "melanoma":                 n_melanoma,
    "breast_cancer":            n_breast_cancer,
    "prostate_cancer":          n_prostate_cancer,
    "colorectal_cancer":        n_colorectal_cancer,
    "lung_cancer":              n_lung_cancer,
    "bladder_cancer":           n_bladder_cancer,

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

    # Lifestyle
    "alcohol_consumption":      n_alcohol_consumption,
    "caffeine_metabolism":      n_caffeine_metabolism,
    "lactase_persistence":      n_lactase_persistence,
    "longevity":                n_longevity,

    # Pharmacogenomics
    "pharmacogenomics":         n_pharmacogenomics,
})


def risk_label_bg(pred):
    en = risk_label(pred)
    return RISK_LABELS.get(en, en)

def n_eye_color_bg(r):
    return """
    което е точно там, където я поставя вашата генотипна комбинация. Доминиращият
    сигнал е rs12913832 GG - тази единична вариация в гена HERC2 е най-силният
    известен предиктор за цвета на очите при хората. GG е класическият генотип,
    свързан с сини очи, открит при около 97% от синеоките европейци. Сам по себе
    си той би предсказал сини очи.</p>

    <p>Зеленият елемент се въвежда от комбинацията от вторични сигнали, действащи
    в различни посоки. SLC24A4 GT и IRF4 CT са и двете междинни - те нито
    засилват напълно синия сигнал, нито го насочват към кафяво. SLC45A2 GG е
    предковият алел, който не допринася за европейския вариант на изсветляване,
    добавяйки малък противовес. TYR AG (хетерозиготен) намалява умерено синтеза
    на меланин в различни тъкани, включително ириса.</p>

    <p>Крайният резултат: силно намален OCA2-медииран меланинов сигнал от HERC2,
    частично модулиран от междинни алели в поддържащите локуси. Това произвежда
    ирис, по-светъл от кафявия, с конкретен нюанс, намиращ се между синьо и зелено
    в зависимост от условията на осветление и структурата на ириса. Кафявото е
    практически изключено - нямате нито една от класическите алелни комбинации,
    промотиращи кафяво, на ключовите локуси.</p>

    се простира отвъд цвета на очите. Същото намаляване на ензима, което изсветлява
    ириса, намалява и UV-защитния еумеланин в кожата - с реални последици за
    натрупването на увреждания от слънцето, разгледани в раздела за кожата.</p>
    """

def n_hair_color_bg(r):
    return """
    <p>Генетиката на цвета на косата разказва ясна и последователна история:
    средно до тъмнокафява, без червен компонент. Генът MC1R - който функционира
    като основен превключвател между червен/жълт феомеланин и тъмен еумеланин -
    не показва рискови варианти на нито едно от четирите тествани места. Това
    практически изключва червената коса. Наследили сте напълно функционален
    MC1R рецептор, което означава, че меланоцитите ви произвеждат еумеланин
    по подразбиране.</p>

    <p>Доминиращият пигментационен сигнал е SLC45A2 GG - предковият алел,
    разпространен сред непервоевропейски и по-тъмно пигментирани популации,
    който не допринася за европейския вариант на изсветляване на косата.
    Комбиниран с липсата на MC1R варианти, това установява ясна тъмна основа.</p>

    който намалява ефективността на ензима тирозиназа. Това е умерен ефект -
    може да допринесе за известно омекотяване на най-тъмния възможен нюанс,
    поради което прогнозата е средно до тъмно, а не черна.</p>
    """

def n_skin_tone_bg(r):
    return """
    <p>Генетиката на пигментацията на кожата разкрива интересно напрежение между
    два противоположни фактора, което произвежда среден, а не краен резултат.</p>

    алел на единствения най-влиятелен локус за цвета на кожата. Тази вариация се
    е разпространила сред европейските и южноазиатски популации преди около
    8 000 години - вероятно като адаптация към среди с ниско UV лъчение.
    Нейният ефект е достатъчно голям, за да обясни значителна част от разликата
    в пигментацията между европейците и западноафриканците.</p>

    допълнително изсветляване. Комбинацията дава светъл до среден тон, а не
    много бледа кожа. TYR CA (хетерозиготен) намалява меланиновия изход,
    добавяйки склонност към лунички и намалена UV защита.</p>

    по-лесно от средното. SPF50 не е прекалена предпазна мярка за този профил -
    тя е подходящата основна защита, прилагана последователно.</p>
    """

def n_cholesterol_bg(r):
    return """
    <p>Генетиката на холестерола ви представя смесена, но в крайна сметка
    умерена картина. Най-важното откритие е това, което липсва: носите rs7412 CC,
    което е сигналът за APOE ε2 алела - свързан с по-нисък LDL и намален
    сърдечно-съдов риск. Това е наистина благоприятна находка.</p>

    пълното определяне на APOE генотипа - не е бил на вашия чип. Клиничен тест
    за APOE генотип (евтин, наличен при личния лекар) би решил това окончателно
    и си заслужава поради последиците за сърдечно-съдовия и Алцхаймеровия риск.</p>

    <p>Освен APOE: rs629301 TT при SORT1/CELSR2 носи два копия на алела,
    повишаващ LDL. rs11591147 GG при PCSK9 не показва защитен алел за
    намаляване на функцията. LPA rs10455872 AA не е рисков - не носите
    варианта, повишаващ Lp(a), което е значима защитна находка.</p>

    <p>Диета и упражнения са подходящ първи подход. Препоръчват се ежегодни
    липидни панели и изясняване на пълния APOE статус.</p>
    """

def n_t2d_bg(r):
    return """
    обобщеният брой - повишен риск - скрива важен модел в детайлите.</p>

    <p>Вие сте хетерозиготни почти на всеки основен T2D локус: TCF7L2 CT
    (едно рисково копие), KCNJ11 CT, SLC30A8 TC, CDKN2A/B CT, HHEX TC,
    IGF2BP2 GT, FTO CA. Тази последователна хетерозиготност на седем
    независими локуса е определящата характеристика на вашия профил -
    умерено генетично натоварване, разпределено широко, а не тежко натоварване
    на един ген.</p>

    Хетерозиготните носители имат около 1,4 пъти по-висок базов риск.
    Критично: носителите на TCF7L2 риск реагират особено добре на промени
    в начина на живот - умерена загуба на тегло и 150 минути упражнения
    седмично са доказано ефективни.</p>

    с тази генетична предразположеност. Периодичното изследване на кръвната
    захар и HbA1c е подходящо.</p>
    """

def n_alzheimer_bg(r):
    return """
    находка в целия доклад. rs7412 CC съответства на APOE ε2 алела -
    а ε2 е най-силно известният защитен вариант срещу Алцхаймер с късно
    начало. Носителите на ε2 имат около 50% по-нисък риск спрямо общия
    ε3/ε3 генотип и са значително свръхпредставени сред когнитивно
    здравите индивиди на 85 и повече години.</p>

    че rs429358 не е бил на вашия чип. Дори при смесен ε2/ε4 генотип,
    защитният сигнал от ε2 остава реален и значим.</p>

    редовна аеробна активност, когнитивна ангажираност, качествен сън
    (по време на който мозъкът изчиства амилоид) и контрол на кръвното
    налягане. Тези фактори имат пряка неврологична релевантност за
    вашия генотип.</p>
    """

def n_vitamin_d_bg(r):
    return """
    <p>Генетиката ви на витамин D показва нюансирана картина, която надхвърля 
    обобщения "лек" полигенен сигнал. Макар общият GWAS резултат да е само 
    умерено повишен (+11.4), конкретните варианти разкриват неефективност 
    на два ключови етапа: транспорт и клетъчно усвояване.</p>

    <p><strong>Етап на транспорт (GC ген):</strong> Носите rs7041 CA (хетерозиготен) и rs4588 GG. 
    Тази комбинация произвежда смес от протеини, свързващи витамин D, 
    което води до умерено намалена ефективност при доставянето му до тъканите. 
    Не е тежко нарушено, но намалява количеството био-наличен витамин D в сравнение 
    с оптималните GC генотипове.</p>

    <p><strong>Етап на рецептор (VDR ген):</strong> По-значителни са вашите VDR варианти 
    - rs731236 AA (TaqI) и rs7975232 CC (ApaI). Тези добре проучени маркери са 
    свързани с намалена чувствителност на витамин D рецепторите. Това означава, 
    че дори когато витамин D достигне до клетките, рецепторите, които трябва да 
    задействат абсорбцията на калций и минерализацията на костите, реагират по-слабо.</p>

    <p>Комбинираният ефект създава двустепенно "намаляване на силата" на 
    витамин D активността. Не сте неспособни да метаболизирате витамин D, 
    но имате по-висока физиологична нужда, за да постигнете същите нива 
    на абсорбция на калций и минерализация на костите, както човек с по-ефективна генетика. 
    Това обяснява наблюдението ви за намален капацитет за складиране на калций в костите.</p>

    <p><strong>Практически препоръки:</strong> Стремете се към по-високи нива на серумен витамин D 
    (идеално 50-70 ng/mL). Тъй като проблемът е отчасти в чувствителността на рецепторите, 
    оптимизирането на ко-факторите е ключово:</p>
    <ul>
      <li><strong>Магнезий</strong> (300-400 mg/ден) - необходим за активирането на витамин D.</li>
      <li><strong>Витамин K2 (MK-7)</strong> (100-200 mcg/ден) - насочва калция към костите, а не към меките тъкани.</li>
    </ul>
    """

def n_cad_bg(r):
    return """
    <p>Коронарната артериална болест е областта, в която генетичният профил
    показва най-значимото клинично повишение. Локусът '9p21' (CDKN2B-AS1) -
    най-репликираният общ вариант за КАБ - се появява два пъти: rs4977574 AG
    и rs1333049 CG (и двата с едно рисково копие). Тези два варианта са
    адитивни с добре установени ефекти.</p>

    стандартните липидни изследвания не улавят изцяло този риск. Препоръчва
    се внимание към пълния сърдечно-съдов рисков профил: кръвно налягане,
    отказ от тютюнопушене, диабет и LDL. Статини и промени в начина на живот
    са ефективни независимо от генотипа.</p>
    """

def n_bmi_bg(r):
    return """
    <p>Генетиката на ИТМ показва умерено натоварване, като ключовата находка
    е хетерозиготността за FTO. rs9939609 AT означава едно копие на рисковия
    алел на FTO (A) - всеки A алел добавя около 0,4 kg/m^2 към средния ИТМ.</p>

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
    хетерозиготен) - доминиращият триглицериден локус, чийто G алел нарушава
    функцията на APOA5 за активиране на липопротеинова липаза.</p>

    функция, чиято C форма създава хиперактивна липопротеинова липаза,
    която съществено подобрява клирънса на триглицеридите.</p>

    <p>Хранителните последици са преки: вашата APOA5 хетерозиготност означава,
    че приемът на въглехидрати и алкохол има усилен ефект върху нивата на
    триглицеридите. Омега-3 добавки (EPA/DHA) са особено ефективни при
    носители на APOA5 рискови алели - клиничните проучвания показват
    20-30% намаление на триглицеридите.</p>
    """

def n_depression_bg(r):
    return """
    <p>Генетиката на депресията разказва нюансирана история, която изисква
    внимателен контекст. BDNF rs6265 CT означава едно копие на Val66Met -
    Met алелът е свързан с намалена активност-зависима секреция на BDNF.
    BDNF е основният невротрофичен фактор на мозъка, поддържащ невронното
    оцеляване и пластичността.</p>

    <p>COMT rs4680 GG е профилът "Воин" (Val/Val) - по-висок разпад на
    допамин в префронталния кортекс, което типично означава по-добра
    устойчивост на стрес и изпълнителна функция под натиск.</p>

    <p>Нивата на BDNF са силно повлияни от аеробните упражнения - редовната
    физическа активност е един от най-надеждните стимулатори на BDNF и
    съществено компенсира намалената базова секреция на Met алела.</p>
    """

def n_longevity_bg(r):
    return """
    <p>Генетиката на дълголетието показва умерени положителни сигнали,
    като картината с APOE е централна. rs7412 CC съответства на APOE ε2 алела
    - и ε2 е последователно свръхпредставен сред стогодишниците в множество
    независими кохортни проучвания.</p>

    CETP rs3764814 CT и rs5882 AG сочат към по-висок HDL холестерол -
    повишеният HDL е последователно свързан с дълголетие, особено в
    еврейски ашкенази и японски кохорти.</p>

    показват, че факторите на начина на живот - особено избягване на
    тютюнопушенето, редовна физическа активност, средиземноморска диета и
    поддържане на социална ангажираност - обясняват повече от вариацията
    при достигане на изключителна възраст, отколкото генетиката.</p>
    """

def n_mthfr_bg(r):
    return """
    <p>Генетиката на метаболизма на фолат и В-витамини е най-клинично
    приложимата хранителна находка в този доклад и заслужава внимателно
    разглеждане, тъй като липсваше от основния здравен доклад.</p>

    <p>Носите два MTHFR варианта едновременно - сложна хетерозиготност,
    по-значима от всеки вариант поотделно:</p>

    <p><strong>MTHFR C677T (rs1801133) GA - хетерозиготен.</strong> T алелът
    намалява активността на ензима MTHFR с около 35% при хетерозиготите.
    MTHFR е ключовият ензим, превръщащ фолата в активната форма (5-метилТХФ),
    използвана за рециклиране на хомоцистеин обратно до метионин. Намалената
    активност означава по-бавен клирънс на хомоцистеина и потенциално повишен
    плазмен хомоцистеин - рисков фактор за сърдечно-съдови и неврологични
    заболявания.</p>

    <p><strong>MTHFR A1298C (rs1801131) GT - хетерозиготен.</strong> Комбиниран
    с C677T хетерозиготността (сложна хетерозиготност), функционалната
    ензимна активност може да бъде намалена с 50-60%.</p>

    <p>Практическите последици са преки: приемайте <strong>метилфолат
    (5-MTHF)</strong>, а не фолиева киселина, и <strong>метилкобаламин</strong>
    вместо цианокобаламин. Изследвайте нивата на хомоцистеин, фолат и В12 в
    кръвта, за да потвърдите метаболитния статус.</p>

    болест и инсулт - две области, при които GWAS данните вече показват
    повишени сигнали. Адекватното допълване с метилфолат и метилкобаламин
    е доказано ефективно за нормализиране на хомоцистеина при носители на
    MTHFR.</p>
    """

def n_hair_loss_bg(r):
    return """
    AR/EDA2R локус - най-силният сигнал за мъжки тип алопеция, с OR над 2,0
    в публикувани GWAS - показва rs2497938 CC, което е генотипът без риск.
    Този локус се наследява по майчина линия (на X хромозомата).</p>

    <p>GWAS потвърждава: само 1 повишен локус от 15 генотипирани, с PGS от
    +2,8 - най-ниският значим полигенен резултат в целия профил. Мъжкият тип
    алопеция е около 80% наследствена, което прави тази ниска стойност
    наистина информативна.</p>
    """

def n_height_bg(r):
    return """
    <p>Ръстът е едно от най-полигенните черти в човешкия геном - хиляди
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

    <p>COMT rs4680 GG е генотипът Val/Val - "Воинският" профил. По-висока
    ензимна активност на COMT означава по-бърз разпад на допамин в
    префронталния кортекс, произвеждайки по-добра работна памет и
    изпълнителна функция под когнитивно натоварване и стрес.</p>

    <p>BDNF rs6265 CT (Val66Met хетерозиготен) е нюансиращият фактор.
    Хетерозиготността означава, че един функционален Val алел остава -
    това е частично, а не пълно намаление. Редовните аеробни упражнения
    са един от най-надеждните стимулатори на BDNF и съществено компенсират
    намалената базова секреция на Met алела.</p>
    """

def n_immune_bg(r, trait):
    pred     = r.get('prediction','')
    pgs      = r.get('pgs_score', 0)
    elevated = r.get('snps_used', 0)
    return f"""
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
# Place this AFTER SECTIONS, SECTIONS, and BG dict are defined

LANG_CONFIG = {
    "en": {
        "html_lang": "en",
        "title_suffix": "- Genetic Health Narrative",
        "eyebrow": "Personal Genomics Report",
        "subtitle": "Genetic Health Narrative",
        "contents": "Contents",
        "traits_label": "Traits analysed",
        "elevated_label": "Elevated signals",
        "favourable_label": "Favourable signals",
        "generated_label": "Generated",
        "sections": SECTIONS,           # ← now defined
        "risk_label_fn": risk_label,
        "disclaimer": """<strong>Important:</strong> This report is for personal educational purposes only - 
not a medical diagnosis. Genetic predisposition does not determine health outcomes. 
Please discuss any findings of concern with a qualified healthcare professional."""
    },
    "bg": {
        "html_lang": "bg",
        "title_suffix": "- Генетичен здравен нарратив",
        "eyebrow": "Персонален геномичен доклад",
        "subtitle": "Генетичен здравен нарратив",
        "contents": "Съдържание",
        "traits_label": "Анализирани черти",
        "elevated_label": "Повишени сигнали",
        "favourable_label": "Благоприятни сигнали",
        "generated_label": "Генериран",
        "sections": SECTIONS,        # ← now defined
        "risk_label_fn": risk_label_bg,
        "disclaimer": """<strong>Важно:</strong> Този доклад е само за образователни цели - 
не е медицинска диагноза. Генетичната предразположеност не определя здравните резултати. 
Моля, обсъдете важни находки с квалифициран лекар."""
    }
}

# Full trait name translations
TRAIT_NAMES = {
    "en": {
        "eye_color": "Eye Color",
        "hair_color": "Hair Color",
        "skin_tone": "Skin Tone",
        "hair_loss": "Hair Loss",
        "height": "Height",
        "intelligence": "Cognitive Profile",
        "mthfr": "MTHFR / B-Vitamin Metabolism",
        "cholesterol": "Cholesterol / LDL",
        "t2d": "Type 2 Diabetes",
        "alzheimer": "Alzheimer's Disease",
        "cad": "Coronary Artery Disease",
        "bmi": "BMI / Obesity Tendency",
        "triglycerides": "Triglycerides",
        "depression": "Depression",
        "longevity": "Longevity",
        "caffeine_metabolism": "Caffeine Metabolism",
        "alcohol_consumption": "Alcohol Consumption",
        "pharmacogenomics": "Pharmacogenomics",
        "heart_failure": "Heart Failure",
        "atrial_fibrillation": "Atrial Fibrillation",
        "stroke": "Stroke",
        "gout": "Gout",
        "chronic_kidney_disease": "Chronic Kidney Disease",
        "vitamin_d": "Vitamin D Levels",
        "parkinson": "Parkinson",
        "adhd": "ADHD",
        "autism": "Autism",
        "bipolar_disorder": "Bipolar Disorder",
        "schizophrenia": "Schizophrenia",
        "sleep_duration": "Sleep Duration",
        "melanoma": "Melanoma",
        "breast_cancer": "Breast Cancer",
        "prostate_cancer": "Prostate Cancer",
        "colorectal_cancer": "Colorectal Cancer",
        "lung_cancer": "Lung Cancer",
        "bladder_cancer": "Bladder Cancer",
        "lupus": "Lupus",
        "rheumatoid_arthritis": "Rheumatoid Arthritis",
        "inflammatory_bowel": "Inflammatory Bowel",
        "crohn_disease": "Crohn Disease",
        "multiple_sclerosis": "Multiple Sclerosis",
        "psoriasis": "Psoriasis",
        "asthma": "Asthma",
    },
    "bg": {
        "eye_color": "Цвят на очите",
        "hair_color": "Цвят на косата",
        "skin_tone": "Цвят на кожата",
        "hair_loss": "Косопад",
        "height": "Ръст",
        "intelligence": "Когнитивен профил",
        "mthfr": "MTHFR / Метаболизъм на B-витамини",
        "cholesterol": "Холестерол / LDL",
        "t2d": "Диабет тип 2",
        "alzheimer": "Болест на Алцхаймер",
        "cad": "Коронарна артериална болест",
        "bmi": "ИТМ / Склонност към затлъстяване",
        "triglycerides": "Триглицериди",
        "depression": "Депресия",
        "longevity": "Дълголетие",
        "caffeine_metabolism": "Метаболизъм на кофеин",
        "alcohol_consumption": "Консумация на алкохол",
        "pharmacogenomics": "Фармакогеномика",
        "heart_failure": "Сърдечна недостатъчност",
        "atrial_fibrillation": "Предсърдно мъждене",
        "stroke": "Инсулт",
        "gout": "Подагра",
        "chronic_kidney_disease": "Хронично бъбречно заболяване",
        "vitamin_d": "Ниво на витамин D",
        "parkinson": "Паркинсон",
        "adhd": "СДВХ",
        "autism": "Аутизъм",
        "bipolar_disorder": "Биполярно разстройство",
        "schizophrenia": "Шизофрения",
        "sleep_duration": "Продължителност на съня",
        "melanoma": "Меланом",
        "breast_cancer": "Рак на гърдата",
        "prostate_cancer": "Рак на простатата",
        "colorectal_cancer": "Колоректален рак",
        "lung_cancer": "Рак на белия дроб",
        "bladder_cancer": "Рак на пикочния мехур",
        "lupus": "Лупус",
        "rheumatoid_arthritis": "Ревматоиден артрит",
        "inflammatory_bowel": "Възпалително чревно заболяване",
        "crohn_disease": "Болест на Крон",
        "multiple_sclerosis": "Множествена склероза",
        "psoriasis": "Псориазис",
        "asthma": "Астма",
    }
}
# ==================== BUILD SECTIONS ====================
def n_master_synthesis():
    return """
    <h2>Your Genetic Story - The Big Picture</h2>
    <p>After looking at your complete genetic profile, a coherent story emerges. You do not have any dramatic single-gene disorders, but you do have moderate genetic loading across several interconnected systems. The pattern is clear:</p>
    
    <ul>
      <li><strong>Cardiometabolic system</strong> - moderate tendency toward higher lipids, blood pressure sensitivity, and metabolic efficiency challenges.</li>
      <li><strong>Immune & inflammatory regulation</strong> - consistent elevation across multiple autoimmune and inflammatory conditions.</li>
      <li><strong>Brain & cognitive health</strong> - signals in mood regulation, neurodegeneration risk, and cognitive performance under stress.</li>
    </ul>
    
    <p>The common biological theme running through your profile is **inflammation and metabolic resilience**. Your body appears to run a bit "hot" in inflammatory pathways and is less efficient at certain protective and repair processes. This is not uncommon, and importantly, it is highly modifiable through lifestyle.</p>
    
    <p><strong>The highest-leverage areas for you are:</strong></p>
    <ol>
      <li><strong>Consistent physical activity</strong> - especially aerobic + resistance training. This positively influences all three major systems (cardiometabolic, immune, and cognitive).</li>
      <li><strong>Anti-inflammatory nutrition</strong> - Mediterranean-style eating, high omega-3 intake, adequate Vitamin D, and magnesium.</li>
      <li><strong>Sleep and stress management</strong> - critical for immune regulation and cognitive health.</li>
    </ol>
    
    <p>Your genetics also give you clear advantages in other areas (height, intelligence, some protective variants). The overall picture is not one of inevitable disease, but of specific vulnerabilities that respond well to targeted lifestyle intervention.</p>
    
    <p>This is your map. The terrain is known. What you do with it is up to you.</p>
    """

def build_sections(synthesis, lang="en"):
    config = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    html_output = ""

    # Master Synthesis at the top
    try:
        systems_content = n_master_synthesis()
        html_output += f"""
        <section class="report-section" id="s_synthesis">
            <h2 class="section-heading">Your Genetic Story - The Big Picture</h2>
            <div class="narrative-body">{systems_content}</div>
        </section>"""
    except:
        pass

        # Regular trait sections
    for sid, stitle, keys in config["sections"]:
        section_traits = {k: v for k, v in synthesis.items() if k in keys}
        if not section_traits:
            continue

        html_output += f'<section class="report-section" id="s_{sid}">'
        html_output += f'<h2 class="section-heading">{stitle}</h2>'

        for key, trait in section_traits.items():
            prediction = trait.get("prediction", "N/A")
            color = "#f87171" if "elevated" in prediction.lower() else "#86efac" if "low" in prediction.lower() or "favourable" in prediction.lower() else "#fbbf24"
            narrative = get_narrative_html(key, trait, lang)

            html_output += f"""
            <div class="trait-block" id="n_{key}">
                <div class="trait-header">
                    <span class="trait-name">{trait.get("trait", key.replace("_"," ").title())}</span>
                    <span class="risk-pill" style="background:{color};">{prediction}</span>
                </div>
                <div class="narrative-body">
                    {narrative}
                </div>
            </div>"""

        html_output += '</section>'

    return html_output

# ==================== RENDER ====================
def render(person, synthesis, results_dir, lang="en"):
    config = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    today = date.today().strftime("%d %B %Y" if lang == "bg" else "%B %d, %Y")

    sections_html = build_sections(synthesis, lang)
    sections_html += n_pharmacogenomics(synthesis)

    total = len(synthesis)
    elevated = sum(
        1 for r in synthesis.values()
        if "elevated" in (r.get("prediction", "")).lower()
    )

    favourable = sum(
        1 for r in synthesis.values()
        if any(
            w in (r.get("prediction", "")).lower()
            for w in ["favourable", "below average", "low risk"]
        )
    )

    moderate = total - elevated - favourable

    nav = ""
    nav += '<a href="#s_synthesis" class="nav-link">Overview</a>'

    for sid, stitle, keys in config["sections"]:
        if any(k in synthesis for k in keys):
            nav += f'<a href="#s_{sid}" class="nav-link">{stitle}</a>'

    nav += '<a href="#s_pharmacogenomics" class="nav-link">Pharmacogenomics</a>'

    lang_switch = (
        f'<a href="narrative_{person}.html" class="lang-btn">EN</a>'
        f'<a href="narrative_{person}_bg.html" class="lang-btn">БГ</a>'
    )

    html = f"""<!DOCTYPE html>
<html lang="{config['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{person} {config['title_suffix']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
/* ── Reset ── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --paper:#fdfcfa;
  --paper-2:#f4f1eb;
  --paper-3:#ede8df;
  --ink:#1a1612;
  --ink-2:#4a4238;
  --ink-3:#8a7f72;
  --rule:#ddd8cf;
  --blue:#1a4b7a;
  --red:#c0392b;
  --orange:#c97b2a;
  --green:#2d7a4f;
  --purple:#6b3fa0;
  --grey:#5a5a5a;
  --nav-w:210px;
}}
body{{
  background:var(--paper);
  color:var(--ink);
  font-family:'EB Garamond',Georgia,serif;
  font-size:17px;
  line-height:1.85;
}}
/* ── Sidebar ── */
.nav-sidebar{{
  position:fixed;left:0;top:0;bottom:0;
  width:var(--nav-w);
  background:#fff;
  border-right:1px solid var(--rule);
  overflow-y:auto;
  z-index:200;
  display:flex;flex-direction:column;
}}
.nav-head{{
  padding:1.4rem 1rem 1rem;
  border-bottom:1px solid var(--rule);
  flex-shrink:0;
}}
.nav-brand{{
  font-family:'Inter',sans-serif;
  font-size:.58rem;font-weight:700;
  letter-spacing:.18em;text-transform:uppercase;
  color:var(--ink-3);margin-bottom:.2rem;
}}
.nav-person{{
  font-family:'EB Garamond',serif;
  font-size:1.1rem;color:var(--ink);
}}
.nav-links{{flex:1;overflow-y:auto;padding:.8rem .7rem}}
.nav-section-label{{
  font-family:'Inter',sans-serif;
  font-size:.55rem;font-weight:700;
  letter-spacing:.16em;text-transform:uppercase;
  color:var(--ink-3);margin:.8rem 0 .3rem .3rem;display:block;
}}
.nav-link{{
  display:flex;align-items:center;gap:.45rem;
  font-family:'Inter',sans-serif;
  font-size:.74rem;color:var(--ink-3);
  text-decoration:none;padding:.25rem .4rem;
  border-radius:3px;line-height:1.4;
  transition:background .12s,color .12s;
}}
.nav-link:hover{{background:var(--paper-2);color:var(--blue)}}
.nav-score{{
  padding:.8rem 1rem;
  border-top:1px solid var(--rule);
  display:grid;grid-template-columns:1fr 1fr 1fr;
  gap:.3rem;flex-shrink:0;
}}
.ns{{display:flex;flex-direction:column;align-items:center}}
.ns-val{{
  font-family:'Inter',sans-serif;
  font-size:1.05rem;font-weight:700;
}}
.ns-lbl{{
  font-family:'Inter',sans-serif;
  font-size:.5rem;font-weight:600;
  letter-spacing:.07em;text-transform:uppercase;
  color:var(--ink-3);text-align:center;
}}
.lang-bar{{
  padding:.5rem 1rem;
  border-top:1px solid var(--rule);
  display:flex;gap:.4rem;flex-shrink:0;
}}
.lang-btn{{
  font-family:'Inter',sans-serif;
  font-size:.65rem;font-weight:700;
  letter-spacing:.1em;
  padding:.2rem .5rem;border-radius:3px;
  border:1px solid var(--rule);
  color:var(--ink-3);text-decoration:none;
  transition:all .12s;
}}
.lang-btn:hover{{background:var(--blue);color:#fff;border-color:var(--blue)}}
/* ── Cover ── */
.cover{{
  margin-left:var(--nav-w);
  background:var(--ink);
  color:#f0ebe3;
  padding:5rem 3.5rem 4rem;
  position:relative;overflow:hidden;
}}
.cover::after{{
  content:'';
  position:absolute;
  bottom:0;left:0;right:0;height:4px;
  background:linear-gradient(90deg,var(--red),var(--orange),var(--green),var(--purple));
}}
.cover-eyebrow{{
  font-family:'Inter',sans-serif;
  font-size:.62rem;font-weight:600;
  letter-spacing:.2em;text-transform:uppercase;
  color:#7fa8c4;margin-bottom:1.2rem;
}}
.cover h1{{
  font-family:'EB Garamond',serif;
  font-size:3.2rem;font-weight:400;
  letter-spacing:-.02em;
  color:#f0ebe3;margin-bottom:.2rem;line-height:1.1;
}}
.cover-sub{{
  font-size:1.05rem;font-style:italic;
  color:#7fa8c4;margin-bottom:3.5rem;
}}
.cover-stats{{
  display:flex;gap:3rem;flex-wrap:wrap;
  border-top:1px solid #2d3f52;padding-top:1.5rem;
}}
.cs{{display:flex;flex-direction:column}}
.cs-val{{
  font-family:'Inter',sans-serif;
  font-size:1.7rem;font-weight:700;color:#f0ebe3;
}}
.cs-lbl{{
  font-family:'Inter',sans-serif;
  font-size:.58rem;font-weight:500;
  letter-spacing:.12em;text-transform:uppercase;color:#5a7a94;
}}
/* ── Main ── */
.main{{
  margin-left:var(--nav-w);
  max-width:920px;
  padding:0 3.5rem 6rem;
}}
.disclaimer{{
  font-family:'Inter',sans-serif;
  font-size:.76rem;line-height:1.6;
  background:#fffbeb;
  border-left:3px solid #d97706;
  padding:.8rem 1.2rem;color:#78450a;
  margin:2.5rem 0 0;
}}
/* ── Era blocks - ancestry layout ── */
.era-block{{
  display:grid;
  grid-template-columns:120px 1fr;
  gap:0 2rem;
  padding:3rem 0;
  border-bottom:1px solid var(--rule);
  position:relative;
}}
.era-block:last-child{{border-bottom:none}}
.era-marker{{
  position:relative;
  display:flex;flex-direction:column;
  align-items:center;gap:.5rem;
  padding-top:.25rem;
}}
.era-marker::before{{
  content:'';
  position:absolute;left:50%;
  top:0;bottom:-3rem;
  width:1px;background:var(--rule);
  transform:translateX(-50%);z-index:0;
}}
.era-dot{{
  width:10px;height:10px;border-radius:50%;
  background:var(--ink-3);
  border:2px solid var(--paper);
  box-shadow:0 0 0 3px var(--ink-3);
  z-index:1;flex-shrink:0;
}}
.era-label{{
  font-family:'Inter',sans-serif;
  font-size:.6rem;font-weight:500;
  letter-spacing:.07em;text-transform:uppercase;
  color:var(--ink-3);text-align:center;
  line-height:1.4;z-index:1;
}}
.era-content{{min-width:0}}
.era-heading{{
  font-family:'EB Garamond',serif;
  font-size:1.55rem;font-weight:600;
  color:var(--ink);margin-bottom:1.5rem;
  letter-spacing:-.01em;line-height:1.2;
}}
/* ── Trait blocks ── */
.trait-block{{
  margin-bottom:2.5rem;
  padding-bottom:2.5rem;
  border-bottom:1px dashed var(--rule);
}}
.trait-block:last-child{{border-bottom:none;margin-bottom:0;padding-bottom:0}}
.trait-header{{
  display:flex;align-items:flex-start;gap:.8rem;margin-bottom:.8rem;
}}
.trait-sev-bar{{
  width:3px;min-height:3rem;align-self:stretch;
  border-radius:2px;flex-shrink:0;margin-top:.1rem;
}}
.trait-header-inner{{flex:1;min-width:0}}
.trait-icon-row{{
  display:flex;align-items:center;
  gap:.5rem;margin-bottom:.4rem;flex-wrap:wrap;
}}
.trait-icon{{font-size:1.1rem}}
.trait-name{{
  font-family:'Inter',sans-serif;
  font-size:.9rem;font-weight:600;
  color:var(--ink);letter-spacing:-.01em;
}}
.risk-pill{{
  display:inline-block;
  font-family:'Inter',sans-serif;
  font-size:.55rem;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;
  padding:.18rem .55rem;border-radius:999px;color:#fff;
}}
/* ── GWAS chips ── */
.gwas-strip{{
  display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:.7rem;
}}
.gwas-chip{{
  font-family:'Inter',sans-serif;
  font-size:.62rem;font-weight:500;
  padding:.12rem .45rem;border-radius:4px;
  background:var(--paper-2);color:var(--ink-3);
  border:1px solid var(--rule);
}}
.gwas-chip.pgs-up{{background:#e8f0f8;color:var(--blue);border-color:var(--blue)}}
.gwas-chip.pgs-down{{background:#fdf0ee;color:var(--red);border-color:var(--red)}}
.gwas-chip.elev{{background:#fdf4e7;color:var(--orange);border-color:var(--orange)}}
/* ── Narrative ── */
.narrative-body p{{
  margin-bottom:.9rem;
  font-size:.98rem;line-height:1.9;color:var(--ink-2);
}}
.narrative-body p:last-child{{margin-bottom:0}}
.narrative-body strong{{color:var(--ink);font-weight:600}}
.narrative-body ul,.narrative-body ol{{margin:.4rem 0 .9rem 1.2rem}}
.narrative-body li{{font-size:.95rem;color:var(--ink-2);margin-bottom:.25rem;line-height:1.7}}
/* ── Master synthesis ── */
.synthesis-block{{
  background:var(--ink);color:#f0ebe3;
  padding:2.2rem;border-radius:6px;margin-bottom:2rem;
}}
.synthesis-block h2{{
  font-family:'EB Garamond',serif;
  font-size:1.3rem;color:#f0ebe3;margin-bottom:.9rem;
}}
.synthesis-block p,.synthesis-block li{{
  font-size:.9rem;color:#c8bfb0;line-height:1.85;margin-bottom:.6rem;
}}
.synthesis-block strong{{color:#f0ebe3}}
.synthesis-block ul,.synthesis-block ol{{margin:.4rem 0 .7rem 1.2rem}}
/* ── Drug cards ── */
.pharma-intro{{
  font-size:.97rem;color:var(--ink-2);
  line-height:1.85;margin-bottom:2rem;
}}
.drug-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(360px,1fr));
  gap:1.2rem;
}}
.drug-card{{
  background:#fff;border:1px solid var(--rule);
  border-radius:6px;overflow:hidden;
}}
.drug-card-head{{
  padding:.8rem 1rem;
  border-bottom:1px solid var(--rule);
}}
.drug-card-top{{
  display:flex;align-items:center;gap:.5rem;
  margin-bottom:.3rem;
}}
.drug-enzyme{{
  font-family:'Inter',sans-serif;
  font-size:.7rem;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);
}}
.drug-genotype{{
  font-family:'Inter',monospace;
  font-size:.8rem;font-weight:600;color:var(--blue);
  margin-bottom:.2rem;
}}
.drug-affected{{
  font-family:'Inter',sans-serif;
  font-size:.72rem;color:var(--ink-3);
}}
.drug-card-body{{padding:1rem}}
.drug-narrative{{
  font-family:'EB Garamond',serif;
  font-size:.93rem;color:var(--ink-2);
  line-height:1.75;margin-bottom:.8rem;
}}
.drug-action{{
  padding:.6rem .8rem;
  background:var(--paper-2);border-radius:4px;
  font-family:'Inter',sans-serif;
  font-size:.72rem;color:var(--ink-3);line-height:1.55;
}}
.drug-action strong{{color:var(--ink);font-weight:600}}
/* ── Print / responsive ── */
@media print{{
  .nav-sidebar{{display:none}}
  .cover,.main{{margin-left:0}}
  .era-marker::before{{display:none}}
  .drug-card{{break-inside:avoid}}
}}
@media(max-width:900px){{
  .nav-sidebar{{display:none}}
  .cover,.main{{margin-left:0;padding-left:1.5rem;padding-right:1.5rem}}
  .era-block{{grid-template-columns:1fr}}
  .era-marker{{display:none}}
  .drug-grid{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>
<aside class="nav-sidebar">
  <div class="nav-head">
    <div class="nav-brand">Personal Genomics</div>
    <div class="nav-person">{person}</div>
  </div>
  <nav class="nav-links">
    {nav}
  </nav>
  <div class="nav-score">
    <div class="ns"><span class="ns-val" style="color:var(--red)">{elevated}</span><span class="ns-lbl">Elevated</span></div>
    <div class="ns"><span class="ns-val" style="color:var(--orange)">{moderate}</span><span class="ns-lbl">Moderate</span></div>
    <div class="ns"><span class="ns-val" style="color:var(--green)">{favourable}</span><span class="ns-lbl">Favourable</span></div>
  </div>
  <div class="lang-bar">{lang_switch}</div>
</aside>
<div class="cover">
  <p class="cover-eyebrow">{config['eyebrow']}</p>
  <h1>{person}</h1>
  <p class="cover-sub">{config['subtitle']}</p>
  <div class="cover-stats">
    <div class="cs"><span class="cs-val">{total}</span><span class="cs-lbl">{config['traits_label']}</span></div>
    <div class="cs"><span class="cs-val" style="color:#f87171">{elevated}</span><span class="cs-lbl">{config['elevated_label']}</span></div>
    <div class="cs"><span class="cs-val" style="color:#86efac">{favourable}</span><span class="cs-lbl">{config['favourable_label']}</span></div>
    <div class="cs"><span class="cs-val">{today}</span><span class="cs-lbl">{config['generated_label']}</span></div>
  </div>
</div>
<div class="main">
  <div class="disclaimer">{config['disclaimer']}</div>
  {sections_html}
</div>
</body>
</html>"""

    suffix = "_bg" if lang == "bg" else ""
    out = results_dir / f"narrative_{person}{suffix}.html"
    out.write_text(html, encoding="utf-8")
    return out


# ==================== ENTRY POINTS ====================

def generate(person_cfg, lang="en", verbose=True):
    name = person_cfg["name"]
    results_dir = ROOT_DIR / person_cfg["results_dir"]
    synth_path = results_dir / "synthesis.json"

    if not synth_path.exists():
        print(f"  WARN: synthesis.json not found for {name}")
        return None

    with open(synth_path, "r", encoding="utf-8") as f:
        synthesis = json.load(f)

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
