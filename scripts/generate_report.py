#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from datetime import date
import re

def get_localized_metadata(lang):
    if lang == "bg":
        name = "Минко Ненов"
        months_bg = [
            "януари", "февруари", "март", "април", "май", "юни",
            "юли", "август", "септември", "октомври", "ноември", "декември"
        ]
        import datetime
        today = datetime.date.today()
        formatted_date = f"{today.day} {months_bg[today.month - 1]} {today.year} г."
        ui = {
            "personal_genomics": "Персонална геномика",
            "elevated_signals": "Повишени",
            "favourable_signals": "Благоприятни",
            "header_subtitle": "Цялостен ДНК анализ и здравни насоки",
            "total_traits": "Общо белези",
            "generated": "Генерирано",
            "disclaimer_sources": "Източници и аналитичен контекст:",
            "disclaimer_sources_text": "GWAS Catalog, ClinVar, dbSNP, фармакогеномична литература, модели за полигенна оценка на риска. Генетичните оценки на риска и прогнозите са статистически приблизителни оценки, базирани на съвременни популационни проучвания и не представляват клинична диагноза.",
            "disclaimer_important": "Важно:",
            "disclaimer_important_text": "Този доклад е само за лични образователни цели, а не медицинска диагноза."
        }
    else:
        name = "Minko Nenov"
        import datetime
        formatted_date = datetime.date.today().strftime("%B %d, %Y")
        ui = {
            "personal_genomics": "Personal Genomics",
            "elevated_signals": "Elevated",
            "favourable_signals": "Favourable",
            "header_subtitle": "Comprehensive DNA Analysis & Health Insights",
            "total_traits": "Total Traits",
            "generated": "Generated",
            "disclaimer_sources": "Sources and analytical context:",
            "disclaimer_sources_text": "GWAS Catalog, ClinVar, dbSNP, pharmacogenomic literature, polygenic risk scoring models. Genetic risk scores and predictions are statistical approximations based on current population studies and do not constitute a clinical diagnosis.",
            "disclaimer_important": "Important:",
            "disclaimer_important_text": "This report is for personal educational purposes only - not a medical diagnosis."
        }
        
    return name, formatted_date, ui

from scripts.narratives import (
    UI, 
    TRAIT_NAMES, 
    BG, 
    BESPOKE, 
    risk_label_bg, 
    n_gwas_summary,
    get_localized_narrative_html, 
    get_marker_votes_html,
    get_risk_balance_html, 
    get_pgs_badge_html, 
    get_loci_bar_html,
    translate_prediction,
)
from scripts.templates import (
    LANG_CONFIG, 
    n_master_synthesis, 
    n_pharmacogenomics,
)

ROOT_DIR = Path(".")
CONFIG = "config.json"

def strip_html_tags(text):
    return re.sub('<[^<]+?>', '', text)

def build_sections(synthesis, lang="en"):
    config = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    ui = UI.get(lang, UI["en"])
    
    html_output = f"""<section class="report-section" id="s_synthesis"><h2 class="section-heading">{ui['overview_title']}</h2><div class="narrative-body">{n_master_synthesis(lang)}</div></section>"""
    for sid, stitle, keys in config["sections"]:
        section_traits = {k: v for k, v in synthesis.items() if k in keys}
        if not section_traits:
            continue
        html_output += f'<section class="report-section" id="s_{sid}"><h2 class="section-heading">{stitle}</h2>'
        for key, trait in section_traits.items():
            prediction = trait.get("prediction", "N/A")
            prediction = translate_prediction(prediction, lang)
            
            pred_lower = prediction.lower()
            if "elevated" in pred_lower or "повишен" in pred_lower:
                color = "var(--risk-elevated)"
                spine_label = "Elevated" if lang == "en" else "Повишен"
            elif "low" in pred_lower or "favourable" in pred_lower or "нисък" in pred_lower or "благоприятен" in pred_lower:
                color = "var(--risk-favourable)"
                spine_label = "Favourable" if lang == "en" else "Благоприятен"
            else:
                color = "var(--risk-moderate)"
                spine_label = "Moderate" if lang == "en" else "Умерен"
                
            trait_title = TRAIT_NAMES.get(
                lang,
                TRAIT_NAMES["en"]
            ).get(
                key,
                trait.get("trait", key.replace("_", " ").title())
            )

            try:
                gwas_html, deep_html = get_localized_narrative_html(key, trait, lang)
            except Exception as e:
                print(f"ERROR in {key} ({lang}): {e}")
                gwas_html = ""
                deep_html = f"<p style='color:red'>ERROR: {e}</p>"
            
            # Generate pgs_badge first so it's defined
            pgs_badge = get_pgs_badge_html(trait, lang)
            pgs_badge_plain = strip_html_tags(pgs_badge)
            prediction_full = f"{prediction} ({pgs_badge_plain})" if pgs_badge_plain else prediction
            
            risk_balance = get_risk_balance_html(trait, lang)
            loci_bar = get_loci_bar_html(trait, color, lang)
            marker_votes = get_marker_votes_html(trait, lang)
            
            html_output += f"""<div class="trait-row" id="n_{key}">
    <div class="trait-spine" style="color:{color}">
        <span class="spine-dot"></span>
        <span class="spine-line"></span>
        <span class="spine-risk">{spine_label}</span>

    </div>
    <div class="trait-content">
        <h3 class="trait-title">{trait_title}</h3>
        <div class="trait-narrative">
            {gwas_html}
            {pgs_badge}
            {risk_balance}
            {loci_bar}
            {marker_votes}
            {deep_html}
        </div>
    </div>
</div>"""
        html_output += '</section>'
    return html_output

def render(person, synthesis, results_dir, lang="en"):
    config = LANG_CONFIG.get(lang, LANG_CONFIG["en"])
    
    # 1. Define nav_ui first
    ui_nav = {
        "en": {"overview": "Overview", "pgx": "Pharmacogenomics"},
        "bg": {"overview": "Преглед", "pgx": "Фармакогеномика"}
    }
    nav_ui = ui_nav.get(lang, ui_nav["en"])
    
    # 2. Initialize nav using nav_ui immediately after
    nav = f'<a href="#s_synthesis" class="nav-link">{nav_ui["overview"]}</a>'
    for sid, stitle, keys in config["sections"]:
        if any(k in synthesis for k in keys):
            nav += f'<a href="#s_{sid}" class="nav-link">{stitle}</a>'
    nav += f'<a href="#s_pharmacogenomics" class="nav-link">{nav_ui["pgx"]}</a>'
    en_file = "narrative_Minko Nenov.html"
    bg_file = "narrative_Минко Ненов_bg.html"

    lang_switch = f'''
    <a href="{en_file}" class="lang-btn">EN</a>
    <a href="{bg_file}" class="lang-btn">БГ</a>
    '''

    css_styles = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
        --paper: #fdfcfa; --paper-2: #f4f1eb; --ink: #1a1612; --ink-2: #4a4238; --ink-3: #8a7f72;
        --rule: #ddd8cf; --blue: #1a4b7a; --nav-w: 210px;
        --risk-elevated: #c0392b; --risk-moderate: #c97b2a; --risk-favourable: #2d7a4f;
        --blue-tint: rgba(26, 75, 122, 0.05);
        --cat-a: #5a7290; --cat-b: #8a6a4a; --cat-c: #a89464; --cat-d: #8a7f72; --cat-e: #6b8a7a;
    }
    body { background: var(--paper); color: var(--ink); font-family: 'EB Garamond', Georgia, serif; font-size: 17px; line-height: 1.85; }
    .narrative-body em, .narrative-body i, .narrative-text em, .narrative-text i { font-style: normal; }

    .nav-sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: var(--nav-w); background: #fff; border-right: 1px solid var(--rule); overflow-y: auto; z-index: 200; display: flex; flex-direction: column; }
    .nav-head { padding: 1.4rem 1rem 1rem; border-bottom: 1px solid var(--rule); }
    .nav-brand { font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .8rem; font-weight: 600; letter-spacing: .04em; color: var(--ink-3); margin-bottom: .2rem; }
    .nav-person { font-family: 'EB Garamond', serif; font-size: 1.1rem; color: var(--ink); }
    .nav-links { flex: 1; overflow-y: auto; padding: .8rem .7rem; }
    .nav-link { display: flex; align-items: center; gap: .45rem; font-family: 'EB Garamond', serif; font-size: .92rem; color: var(--ink-3); text-decoration: none; padding: .25rem .4rem; border-radius: 3px; line-height: 1.4; margin-bottom: .1rem; }
    .nav-link:hover { background: var(--paper-2); color: var(--blue); }
    .nav-score { padding: .8rem 1rem; border-top: 1px solid var(--rule); display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .3rem; }
    .ns { display: flex; flex-direction: column; align-items: center; }
    .ns-val { font-family: 'EB Garamond', serif; font-size: 1.15rem; font-weight: 700; }
    .ns-lbl { font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .72rem; font-weight: 600; color: var(--ink-3); }
    .lang-bar { padding: .5rem 1rem; border-top: 1px solid var(--rule); display: flex; gap: .4rem; }
    .lang-btn { font-family: 'EB Garamond', serif; font-weight: 700; font-size: .8rem; padding: .2rem .5rem; border-radius: 3px; border: 1px solid var(--rule); color: var(--ink-3); text-decoration: none; }
    .lang-btn:hover { background: var(--blue); color: #fff; border-color: var(--blue); }

    .mobile-bar { display: none; }

    .cover { margin-left: var(--nav-w); background: var(--ink); color: #f0ebe3; padding: 5rem 3.5rem 4rem; position: relative; }
    .cover-eyebrow { font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .88rem; font-weight: 600; letter-spacing: .04em; color: #7fa8c4; margin-bottom: 1.2rem; }
    .cover h1 { font-family: 'EB Garamond', serif; font-size: 3.2rem; font-weight: 400; color: #f0ebe3; margin-bottom: .2rem; }
    .cover-sub { font-size: 1.05rem; font-style: italic; color: #7fa8c4; margin-bottom: 3.5rem; }
    .cover-stats { display: flex; gap: 3rem; flex-wrap: wrap; border-top: 1px solid #2d3f52; padding-top: 1.5rem; }
    .cs { display: flex; flex-direction: column; }
    .cs-val { font-family: 'EB Garamond', serif; font-size: 1.85rem; font-weight: 700; color: #f0ebe3; }
    .cs-lbl { font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .78rem; font-weight: 500; color: #5a7a94; }

    .main { margin-left: var(--nav-w); width: calc(100vw - var(--nav-w)); padding: 0 3.5rem 6rem; }
    .main-inner { max-width: 920px; margin-left: auto; margin-right: auto; }
    .disclaimer { font-family: 'EB Garamond', serif; font-size: .92rem; line-height: 1.6; background: #fffbeb; border-left: 3px solid #d97706; padding: .8rem 1.2rem; color: #78450a; margin: 2.5rem 0 0; }
    .report-section { margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--rule); }
    .section-heading { font-family: 'EB Garamond', serif; font-size: 1.8rem; font-weight: 600; margin-bottom: .5rem; color: var(--ink); }

    .narrative-body p { margin-bottom: .9rem; font-size: .98rem; line-height: 1.9; color: var(--ink-2); }

    .trait-row { display: grid; grid-template-columns: 78px 1fr; column-gap: 1.8rem; padding: 2.6rem 0; border-bottom: 1px solid var(--rule); }
    .trait-row:last-child { border-bottom: none; padding-bottom: 0; }
    .trait-spine { position: relative; display: flex; flex-direction: column; align-items: center; padding-top: .4rem; }
    .spine-dot { width: 13px; height: 13px; border-radius: 50%; background: currentColor; border: 2px solid var(--paper); box-shadow: 0 0 0 2px currentColor; flex-shrink: 0; z-index: 1; }
    .spine-line { position: absolute; top: 15px; bottom: -2.6rem; left: 50%; width: 1px; background: var(--rule); transform: translateX(-50%); }
    .spine-risk { margin-top: .6rem; font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .74rem; font-weight: 600; text-align: center; line-height: 1.3; }
    .trait-title { font-family: 'EB Garamond', serif; font-size: 1.55rem; font-weight: 600; color: var(--ink); margin-bottom: 1.4rem; letter-spacing: -.01em; }

    .trait-narrative { display: flex; flex-direction: column; gap: 2rem; }
    .narrative-unit { display: grid; grid-template-columns: 118px 1fr; gap: 1.4rem; }
    .narrative-kicker { font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .9rem; line-height: 1.3rem; font-weight: 600; color: var(--ink-3); padding-top: .1rem; }
    .narrative-text p { font-size: 1rem; line-height: 1.9; color: var(--ink-2); margin-bottom: .9rem; }
    .narrative-text p:last-child { margin-bottom: 0; }
    .narrative-unit--gwas .narrative-kicker { position: relative; color: var(--blue); padding-left: 1.5rem; }
    .narrative-unit--gwas .narrative-kicker::before { content: ""; position: absolute; left: 0; top: .35rem; width: 9px; height: 9px; border-radius: 50%; background: var(--blue); border: 2px solid var(--paper); box-shadow: 0 0 0 2px var(--blue); z-index: 1; }
    .narrative-unit--gwas .narrative-kicker::after { content: ""; position: absolute; left: 4px; top: 1.15rem; bottom: 0; width: 1px; background: var(--rule); }
    .narrative-unit--gwas .narrative-text { padding-left: 1.6rem; }
    .narrative-unit--gwas .narrative-text strong { color: var(--blue); font-weight: 700; }
    .risk-pill { display: inline-block; font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .8rem; font-weight: 700; padding: .25rem .75rem; border-radius: 4px; color: #fff; white-space: nowrap; }
    .narrative-unit--deep { display: block; }
    .narrative-unit--deep .narrative-kicker { margin-bottom: .6rem; }

    .pgs-badge { display: inline-block; font-family: 'Inter', monospace; font-size: .78rem; font-weight: 600; color: var(--blue); background: var(--blue-tint); padding: .3rem .7rem; border-radius: 4px; margin-bottom: 0; }
    .risk-balance { margin: 0 0 1.4rem; }
    .risk-balance-track { display: flex; height: 6px; border-radius: 3px; overflow: hidden; background: var(--paper-2); }
    .risk-balance-prot { background: var(--risk-favourable); }
    .risk-balance-risk { background: var(--risk-elevated); }
    .risk-balance-labels { display: flex; justify-content: space-between; margin-top: .4rem; font-family: 'EB Garamond', serif; font-size: .8rem; color: var(--ink-3); }
    .rb-risk { color: var(--risk-elevated); font-weight: 600; }
    .rb-prot { color: var(--risk-favourable); font-weight: 600; }
    .loci-bar { margin: 0 0 1.4rem; }
    .loci-bar-track { height: 6px; border-radius: 3px; overflow: hidden; background: var(--paper-2); }
    .loci-bar-fill { height: 100%; }
    .loci-bar-label { display: block; margin-top: .4rem; font-family: 'EB Garamond', serif; font-size: .8rem; color: var(--ink-3); }

    .drug-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.2rem; margin-top: 1rem; }
    .drug-card { background: #fff; border: 1px solid var(--rule); border-radius: 6px; overflow: hidden; }
    .drug-card-head { padding: .8rem 1rem; border-bottom: 1px solid var(--rule); }
    .drug-card-top { display: flex; align-items: center; gap: .5rem; margin-bottom: .3rem; }
    .drug-enzyme { font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .88rem; font-weight: 700; color: var(--ink-3); }
    .drug-genotype { font-family: 'Inter', monospace; font-size: .8rem; font-weight: 600; color: var(--blue); margin-bottom: .2rem; }
    .drug-affected { font-family: 'EB Garamond', serif; font-size: .85rem; color: var(--ink-3); }
    .drug-card-body { padding: 1rem; }
    .drug-narrative { font-family: 'EB Garamond', serif; font-size: .93rem; color: var(--ink-2); line-height: 1.75; margin-bottom: .8rem; }
    .drug-action { padding: .6rem .8rem; background: var(--paper-2); border-radius: 4px; font-family: 'EB Garamond', serif; font-size: .88rem; color: var(--ink-3); line-height: 1.55; }

    .marker-votes { margin: 0 0 1.4rem; }
    .marker-tally { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: .8rem; }
    .marker-tally-item { display: flex; align-items: center; gap: .4rem; font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .85rem; color: var(--ink-3); }
    .marker-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .marker-tag-grid { display: flex; flex-wrap: wrap; gap: .5rem; }
    .marker-tag-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
    .marker-tag-gene { font-family: 'EB Garamond', serif; font-weight: 600; font-size: .8rem; color: var(--ink-2); }
    .marker-tag-rsid { font-family: 'Inter', monospace; font-size: .72rem; color: var(--ink-3); }
    .marker-tag-geno { font-family: 'Inter', monospace; font-weight: 700; font-size: .78rem; color: var(--blue); }
    .marker-tag { display: flex; align-items: flex-start; gap: .4rem; background: var(--paper-2); border-radius: 4px; padding: .3rem .6rem; cursor: default; }
    .marker-tag-main { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem; }
    .marker-tag--primary { border: 1.5px solid var(--blue); background: var(--blue-tint); }
    .marker-tag--primary .marker-tag-gene { font-weight: 700; }
    .marker-tag--minor { opacity: .62; }
    .marker-tag-weight { font-family: 'EB Garamond', serif; font-style: italic; font-variant-caps: small-caps; font-size: .68rem; font-weight: 600; color: var(--blue); }
    .marker-tag--minor .marker-tag-weight { color: var(--ink-3); }
    .marker-tag--primary .marker-tag-gene { font-weight: 700; }
    .marker-tag--ruleout { opacity: .75; }
    .marker-tag--secondary { border: 1px solid var(--rule); }
    .marker-tag--modifier { border: 1px dashed var(--rule); }

    @media(max-width: 768px) {
        .nav-sidebar { display: none; }
        .cover, .main { margin-left: 0; }
        .cover { padding: 3rem 1.2rem 2.5rem; }
        .cover h1 { font-size: 2.1rem; }
        .cover-sub { font-size: .95rem; margin-bottom: 2rem; }
        .cover-stats { gap: 1.5rem 2rem; }
        .cs-val { font-size: 1.4rem; }
        .main { padding: 0 1.2rem 4rem; width: 100vw; }
        body { font-size: 16px; }

        .mobile-bar {
            display: flex; align-items: center; justify-content: space-between; gap: .8rem;
            position: sticky; top: 0; z-index: 150;
            background: #fff; border-bottom: 1px solid var(--rule);
            padding: .7rem 1.2rem;
        }
        .mobile-person { font-family: 'EB Garamond', serif; font-weight: 600; font-size: .95rem; }
        .mobile-nav-select {
            font-family: 'EB Garamond', serif; font-size: .85rem; color: var(--ink-2);
            border: 1px solid var(--rule); border-radius: 4px; padding: .3rem .5rem; background: #fff;
        }

        .trait-row { grid-template-columns: 44px 1fr; column-gap: 1rem; }
        .spine-risk { display: none; }
        .narrative-unit { grid-template-columns: 1fr; gap: .5rem; }
        .narrative-unit--gwas .narrative-kicker::after { display: none; }
        .narrative-unit--gwas .narrative-text { padding-left: 0; }

        .drug-grid { grid-template-columns: 1fr; }
    }
    """
    name_display, formatted_date, ui = get_localized_metadata(lang)
    name_display, formatted_date, ui = get_localized_metadata(lang)
    file_name_person = name_display
    
    total = len(synthesis)
    elevated = sum(1 for r in synthesis.values() if "elevated" in (r.get("prediction", "")).lower())
    favourable = sum(1 for r in synthesis.values() if any(w in (r.get("prediction", "")).lower() for w in ["favourable", "below average", "low risk"]))
    moderate = total - elevated - favourable
    
    sections_html = build_sections(synthesis, lang) + n_pharmacogenomics(synthesis, lang)
    
    today = formatted_date
    
    html = f"""<!DOCTYPE html>
<html lang="{config['html_lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{person} {config['title_suffix']}</title>
    <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>{css_styles}</style>
</head>
<body>
<!-- add right after <body>, before .nav-sidebar -->
<div class="mobile-bar">
    <span class="mobile-person">{person}</span>
    <select class="mobile-nav-select" onchange="if(this.value) location.hash=this.value;">
        <option value="">Jump to…</option>
        <!-- reuse the same section list as .nav-links, just as <option>s -->
    </select>
</div>
    <aside class="nav-sidebar">
        <div class="nav-head">
            <div class="nav-brand">{ui['personal_genomics']}</div>
            <div class="nav-person">{person}</div>
        </div>
        <nav class="nav-links">{nav}</nav>
        <div class="nav-score">
            <div class="ns"><span class="ns-val" style="color:#c0392b">{elevated}</span><span class="ns-lbl">{ui['elevated_signals']}</span></div>
            <div class="ns"><span class="ns-val" style="color:#c97b2a">{moderate}</span><span class="ns-lbl">Moderate</span></div>
            <div class="ns"><span class="ns-val" style="color:#2d7a4f">{favourable}</span><span class="ns-lbl">{ui['favourable_signals']}</span></div>
        </div>
        <div class="lang-bar">{lang_switch}</div>
    </aside>
    <div class="cover">
        <p class="cover-eyebrow">{config['eyebrow']}</p>
        <h1>{person}</h1>
        <p class="cover-sub">{ui['header_subtitle']}</p>
        <div class="cover-stats">
            <div class="cs"><span class="cs-val">{total}</span><span class="cs-lbl">{ui['total_traits']}</span></div>
            <div class="cs"><span class="cs-val" style="color:#f87171">{elevated}</span><span class="cs-lbl">{ui['elevated_signals']}</span></div>
            <div class="cs"><span class="cs-val" style="color:#86efac">{favourable}</span><span class="cs-lbl">{ui['favourable_signals']}</span></div>
            <div class="cs"><span class="cs-val">{today}</span><span class="cs-lbl">{ui['generated']}</span></div>
        </div>
    </div>
   <div class="main">
        <div class="main-inner">
            <div class="disclaimer">
                <strong>{ui['disclaimer_sources']}</strong> {ui['disclaimer_sources_text']}<br><br>
                <strong>{ui['disclaimer_important']}</strong> {ui['disclaimer_important_text']}
            </div>
            {sections_html}
        </div>
    </div>
</body>
</html>"""
    
    suffix = "_bg" if lang == "bg" else ""
    out = results_dir / f"narrative_{file_name_person}{suffix}.html"
    out.write_text(html, encoding="utf-8")
    return out

# Change these lines at the top of scripts/generate_report.py
ROOT_DIR = Path(".")

def generate(pcfg, lang="en"):
    name = pcfg["name"]
    base_results_dir = Path(pcfg.get("results_dir", "scripts/results"))
    
    # If results_dir doesn't contain the person's name, append it
    if name.lower() not in str(base_results_dir).lower():
        results_dir = base_results_dir / name.split()[0]
    else:
        results_dir = base_results_dir
        
    results_dir.mkdir(parents=True, exist_ok=True)
    
    synth_path = results_dir / "synthesis.json"
    if not synth_path.exists():
        # Fallback: check current directory or scripts/results/Minko directly
        synth_path = Path("scripts/results/Minko/synthesis.json")
        results_dir = Path("scripts/results/Minko")
        if not synth_path.exists():
            print(f"[-] Synthesis JSON not found at {synth_path}")
            return
        
    synthesis = json.load(open(synth_path, encoding="utf-8"))
    
    display_name = "Минко Ненов" if lang == "bg" else name
    
    out = render(display_name, synthesis, results_dir, lang)
    print(f"[+] Generated {lang.upper()} report: {out}")

def main():
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--person")
    grp.add_argument("--all", action="store_true")
    parser.add_argument("--lang", choices=["en", "bg"], default="en")
    args = parser.parse_args()
    if Path(CONFIG).exists():
        cfg = json.load(open(CONFIG, encoding="utf-8"))
        people = cfg["people"]
    else:
        people = [{"name": "Minko Nenov", "results_dir": "."}]
    targets = people if args.all else [p for p in people if p["name"].lower() == args.person.lower()]
    for pcfg in targets:
        generate(pcfg, lang=args.lang)

if __name__ == "__main__":
    main()