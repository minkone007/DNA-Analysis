#!/usr/bin/env python3
"""
systems_mapper.py
Groups traits into biological systems for higher-level insights.
"""
import json
from pathlib import Path

SYSTEMS = {
    "Immune/Inflammatory Axis": ["lupus", "rheumatoid_arthritis", "crohn_disease", "inflammatory_bowel", "psoriasis", "asthma", "celiac_disease", "multiple_sclerosis"],
    "Cardiometabolic Axis": ["bmi", "triglycerides", "diabetes", "t2d", "cholesterol", "coronary_artery_disease", "cad", "heart_failure", "stroke", "blood_pressure", "atrial_fibrillation"],
    "Neuro-Cognitive Axis": ["schizophrenia", "depression", "alzheimer", "autism", "adhd", "bipolar_disorder", "intelligence", "parkinson"],
    "Oncological Axis": ["lung_cancer", "breast_cancer", "prostate_cancer", "colorectal_cancer", "melanoma", "bladder_cancer"],
    "Bone & Mineral Metabolism": ["vitamin_d", "gout", "chronic_kidney_disease"],
    "Longevity & Aging": ["longevity"],
    "Appearance & Physical Traits": ["height", "eye_color", "hair_color", "hair_loss"],
    "Lifestyle & Metabolism": ["caffeine_metabolism", "alcohol_consumption", "lactase_persistence"],
    "Physiology & Fitness": ["vo2_max", "muscle_strength", "sleep_duration"],
    "Dermatology": ["skin_color", "skin_tone"],
    "Pharmacology": ["pharmacogenomics"],
    "Data Metadata": ["gwas-association"]
}

def map_to_systems(summary_path="reports/all_traits_summary.json"):
    with open(summary_path) as f:
        traits = json.load(f)
    
    system_summary = {}
    
    for trait in traits:
        trait_name = trait["trait"].lower().replace(" ", "_").replace("/", "_")
        found = False
        for system_name, keywords in SYSTEMS.items():
            if any(kw in trait_name for kw in keywords):
                if system_name not in system_summary:
                    system_summary[system_name] = []
                system_summary[system_name].append(trait)
                found = True
                break
        
        if not found:
            # This line will now definitely print if a trait isn't categorized
            print(f"DEBUG: Unmapped trait found: {trait['trait']}")
            system_summary.setdefault("Other", []).append(trait)
    
    print("\n=== BIOLOGICAL SYSTEMS MAPPING ===\n")
    for system, items in sorted(system_summary.items(), key=lambda x: len(x[1]), reverse=True):
        high_risk = sum(1 for t in items if t.get("confidence_score", 0) >= 0.7)
        print(f"{system:<30} | {len(items):2d} traits | {high_risk:2d} high-confidence")
    
    return system_summary

def n_systems_overview(system_summary):
    list_items = "".join([f"<li><strong>{s}</strong>: {len(t)} traits identified.</li>\n" 
                          for s, t in sorted(system_summary.items(), key=lambda x: len(x[1]), reverse=True)[:4]])
    return f"<h2>Systems-Level Overview</h2><ul>{list_items}</ul>"

if __name__ == "__main__":
    systems_data = map_to_systems()
    with open("reports/narrative_synthesis.html", "w") as f:
        f.write(n_systems_overview(systems_data))
    print("\n✅ Narrative synthesis saved to reports/narrative_synthesis.html")