#!/usr/bin/env python3
from .narratives import SECTIONS, risk_label, risk_label_bg

LANG_CONFIG = {
    "en": {
        "html_lang": "en",
        "title_suffix": "- Personal Genomics",
        "eyebrow": "Genetic Analysis & Polygenic Profile",
        "subtitle": "Comprehensive Multi-System Genetic & Pharmacogenomic Report",
        "traits_label": "Total Traits",
        "elevated_label": "Elevated",
        "moderate_label": "Moderate",
        "favourable_label": "Favourable",
        "generated_label": "Generated on",
        "sections": [
            ("appearance", "Traits & Physical Characteristics", [
                "eye_color",
                "hair_color",
                "skin_tone",
                "hair_loss",
                "height"
            ]),

            ("cardiovascular", "Cardiovascular Health", [
                "cholesterol",
                "triglycerides",
                "cad",
                "atrial_fibrillation",
                "stroke",
                "heart_failure"
            ]),

            ("metabolic", "Metabolic Health", [
                "t2d",
                "bmi",
                "gout",
                "chronic_kidney_disease",
                "mthfr",
                "vitamin_d"
            ]),

            ("brain", "Brain & Neurology", [
                "intelligence",
                "alzheimer",
                "depression",
                "adhd",
                "autism",
                "bipolar_disorder",
                "schizophrenia",
                "parkinson",
                "sleep_duration"
            ]),

            ("cancer", "Cancer Risk", [
                "breast_cancer",
                "prostate_cancer",
                "colorectal_cancer",
                "melanoma",
                "lung_cancer",
                "bladder_cancer"
            ]),

            ("immune", "Immune & Autoimmune", [
                "asthma",
                "lupus",
                "rheumatoid_arthritis",
                "inflammatory_bowel",
                "crohn_disease",
                "psoriasis",
                "multiple_sclerosis"
            ]),

            ("lifestyle", "Lifestyle & Longevity", [
                "longevity",
                "caffeine_metabolism",
                "alcohol_consumption"
            ]),

            ("pharmacogenomics", "Pharmacogenomics", [
                "pharmacogenomics"
            ])
        ]
    },
    "bg": {
        "html_lang": "bg",
        "title_suffix": "- Персонализирана геномика",
        "eyebrow": "Генетичен анализ и полигенен профил",
        "subtitle": "Цялостен мултисистемен генетичен и фармакогеномен доклад",
        "traits_label": "Общо белези",
        "elevated_label": "Повишени",
        "moderate_label": "Умерени",
        "favourable_label": "Благоприятни",
        "generated_label": "Дата на генериране",
        "sections": [
            ("appearance", "Физически характеристики", [
                "eye_color",
                "hair_color",
                "skin_tone",
                "hair_loss",
                "height"
            ]),

            ("cardiovascular", "Сърдечно-съдово здраве", [
                "cholesterol",
                "triglycerides",
                "cad",
                "atrial_fibrillation",
                "stroke",
                "heart_failure"
            ]),

            ("metabolic", "Метаболитно здраве", [
                "t2d",
                "bmi",
                "gout",
                "chronic_kidney_disease",
                "mthfr",
                "vitamin_d"
            ]),

            ("brain", "Мозък и неврология", [
                "intelligence",
                "alzheimer",
                "depression",
                "adhd",
                "autism",
                "bipolar_disorder",
                "schizophrenia",
                "parkinson",
                "sleep_duration"
            ]),

            ("cancer", "Онкологичен риск", [
                "breast_cancer",
                "prostate_cancer",
                "colorectal_cancer",
                "melanoma",
                "lung_cancer",
                "bladder_cancer"
            ]),

            ("immune", "Имунна система и автоимунни заболявания", [
                "asthma",
                "lupus",
                "rheumatoid_arthritis",
                "inflammatory_bowel",
                "crohn_disease",
                "psoriasis",
                "multiple_sclerosis"
            ]),

            ("lifestyle", "Начин на живот и дълголетие", [
                "longevity",
                "caffeine_metabolism",
                "alcohol_consumption"
            ]),

            ("pharmacogenomics", "Фармакогеномика", [
                "pharmacogenomics"
            ])
        ]
    }
}

def n_master_synthesis(lang="en"):
    if lang == "bg":
        return """
        <h3>Вашата генетична история - голямата картина</h3>
        <p>След анализ на вашия пълен мултисистемен генетичен профил се очертава сложна, силно кохерентна картина. Вие не носите моногенни заболявания с висока пенетрантност, но проявявате умерено полигенно натоварване, разпределено в няколко основни биологични мрежи:</p>
        <ul>
            <li><strong>Кардиометаболитна система</strong> – умерени полигенни тенденции по отношение на липидния обмін, съдовия тонус и гликемичната ефективност.</li>
            <li><strong>Имунни и възпалителни пътища</strong> – последователни полигенни повишения в редица автоимунни и слузести възпалителни клъстери.</li>
            <li><strong>Мозъчна и когнитивна архитектура</strong> – надеждни маркери в регулацията на невротрансмитерите, невропротекцията и устойчивостта на стрес.</li>
        </ul>
        <p>Обединяващата биологична тема в целия ви генетичен профил е <strong>системното възпалително натоварване и управлението на метаболитната ефективност</strong>. Вашият молекулярен профил се ползва със значителни ползи от структурирани интервенции в начина на живот, целева поддръжка с микронутриенти и проактивен клиничен мониторинг.</p>
        """
    else:
        return """
        <h3>Your Genetic Story - The Big Picture</h3>
        <p>After analyzing your complete multi-system genetic profile, an intricate, highly coherent story emerges. You do not carry high-penetrance single-gene Mendelian disorders, but you display moderate, polygenic loading distributed across several core biological networks:</p>
        <ul>
            <li><strong>Cardiometabolic system</strong> - moderate polygenic tendencies concerning lipid handling, vascular tone, and glycemic efficiency.</li>
            <li><strong>Immune & inflammatory pathways</strong> - consistent polygenic elevations across several autoimmune and mucosal inflammatory clusters.</li>
            <li><strong>Brain & cognitive architecture</strong> - robust markers in neurotransmitter regulation, neuroprotection, and stress resilience.</li>
        </ul>
        <p>The unifying biological theme throughout your genetic topography is <strong>systemic inflammatory load and metabolic efficiency management</strong>. Your molecular profile benefits significantly from structured lifestyle interventions, targeted micronutrient support, and proactive clinical monitoring.</p>
        """
        
# In your scripts/templates.py file, make sure the string variables for the Pharmacogenomics section 
# are correctly localized or mapped if they are still appearing in English.

# Look for where the Pharmacogenomics headers/UI strings are defined in templates.py (around line 112+):
def n_pharmacogenomics(synthesis, lang="en"):
    # Ensure you have Bulgarian translations mapped here:
    pgx_ui = {
        "en": {
            "title": "Pharmacogenomics & Drug Metabolism",
            "desc": "Pharmacogenomics examines how your inherited genetic variants alter your body's enzymatic capacity to process, clear, and respond to various pharmaceutical compounds.",
            "affects": "Affects:",
            "takeaway": "Clinical Takeaway:"
        },
        "bg": {
            "title": "Фармакогеномика и лекарствен метаболизъм",
            "desc": "Фармакогеномиката изследва как вашите наследствени генетични варианти променят ензимния капацитет на тялото ви да обработва, изчиства и реагира на различни фармацевтични съединения.",
            "affects": "Засяга:",
            "takeaway": "Клиничен извод:"
        }
    }
    ui = pgx_ui.get(lang, pgx_ui["en"])
    html_output = f"""..."""
    return html_output