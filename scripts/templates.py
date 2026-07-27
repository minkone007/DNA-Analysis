#!/usr/bin/env python3
from narratives import SECTIONS, risk_label, risk_label_bg

LANG_CONFIG = {
    "en": {
        "html_lang": "en", "title_suffix": "- Genetic Health Narrative", "eyebrow": "Personal Genomics Report",
        "subtitle": "Comprehensive Genetic Health Narrative", "contents": "Contents", "traits_label": "Traits analysed",
        "elevated_label": "Elevated signals", "favourable_label": "Favourable signals", "generated_label": "Generated",
        "sections": SECTIONS, "risk_label_fn": risk_label,
        "disclaimer": "<strong>Important:</strong> This report is for personal educational purposes only - not a medical diagnosis."
    },
    "bg": {
        "html_lang": "bg", "title_suffix": "- Генетичен здравен нарратив", "eyebrow": "Персонален геномичен доклад",
        "subtitle": "Изчерпателен генетичен здравен нарратив", "contents": "Съдържание", "traits_label": "Анализирани черти",
        "elevated_label": "Повишени сигнали", "favourable_label": "Благоприятни сигнали", "generated_label": "Генериран",
        "sections": SECTIONS, "risk_label_fn": risk_label_bg,
        "disclaimer": "<strong>Важно:</strong> Този доклад е само за образователни цели - не е медицинска диагноза."
    }
}

def n_master_synthesis():
    return """<h2>Your Genetic Story - The Big Picture</h2><p>After analyzing your complete multi-system genetic profile, an intricate, highly coherent story emerges. You do not carry high-penetrance single-gene Mendelian disorders, but you display moderate, polygenic loading distributed across several core biological networks:</p><ul><li><strong>Cardiometabolic system</strong> - moderate polygenic tendencies concerning lipid handling, vascular tone, and glycemic efficiency.</li><li><strong>Immune & inflammatory pathways</strong> - consistent polygenic elevations across several autoimmune and mucosal inflammatory clusters.</li><li><strong>Brain & cognitive architecture</strong> - robust markers in neurotransmitter regulation, neuroprotection, and stress resilience.</li></ul><p>The unifying biological theme throughout your genetic topography is <strong>systemic inflammatory load and metabolic efficiency management</strong>. Your molecular profile benefits significantly from structured lifestyle interventions, targeted micronutrient support, and proactive clinical monitoring.</p>"""

def n_pharmacogenomics(synthesis):
    return """<section class="report-section" id="s_pharmacogenomics"><h2 class="section-heading">Pharmacogenomics & Drug Metabolism</h2><p class="pharma-intro">Pharmacogenomics examines how your inherited genetic variants alter your body's enzymatic capacity to process, clear, and respond to various pharmaceutical compounds.</p><div class="drug-grid"><div class="drug-card"><div class="drug-card-head"><div class="drug-card-top"><span class="drug-enzyme">CYP1A2</span><span class="risk-pill" style="background:#c97b2a;">Intermediate</span></div><div class="drug-genotype">rs762551 (CA)</div><div class="drug-affected">Affects: Caffeine, Melatonin, Theophylline</div></div><div class="drug-card-body"><p class="drug-narrative">You carry the CA heterozygous genotype, classifying you as an <strong>intermediate metaboliser</strong> for caffeine clearance pathways.</p><div class="drug-action"><strong>Clinical Takeaway:</strong> Afternoon and evening caffeine consumption will significantly affect nocturnal sleep architecture.</div></div></div><div class="drug-card"><div class="drug-card-head"><div class="drug-card-top"><span class="drug-enzyme">CYP2C19</span><span class="risk-pill" style="background:#2d7a4f;">Normal / Extensive</span></div><div class="drug-genotype">Standard Function</div><div class="drug-affected">Affects: Proton Pump Inhibitors, SSRIs, Antiplatelets (Plavix)</div></div><div class="drug-card-body"><p class="drug-narrative">Your genetic profile indicates normal metabolic function for the CYP2C19 enzyme family.</p><div class="drug-action"><strong>Clinical Takeaway:</strong> Standard prescribing guidelines apply without unexpected rapid clearance or toxicity risks.</div></div></div><div class="drug-card"><div class="drug-card-head"><div class="drug-card-top"><span class="drug-enzyme">CYP2D6</span><span class="risk-pill" style="background:#2d7a4f;">Extensive Metaboliser</span></div><div class="drug-genotype">Standard Function</div><div class="drug-affected">Affects: Beta-blockers, Antidepressants, Opioids, Antipsychotics</div></div><div class="drug-card-body"><p class="drug-narrative">CYP2D6 handles roughly 25% of all clinical medications. Your genetic profile aligns with high extensive activity.</p><div class="drug-action"><strong>Clinical Takeaway:</strong> Standard therapeutic dosages are appropriate under clinical supervision.</div></div></div></div></section>"""