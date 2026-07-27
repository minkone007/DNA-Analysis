#!/usr/bin/env python3
"""
validation_correlator.py
Bridges genetic predictions with real-world validation and recommended tests.
"""

from risk_aggregator import aggregate_system_risk
import json

def generate_validation_plan():
    # Get latest risk aggregation
    risk_data = aggregate_system_risk()
    
    print("\n=== VALIDATION & CORRELATION PLAN ===\n")
    print("Recommended measurements to validate your genetic profile:\n")
    
    for system, data in risk_data.items():
        level = data.get("risk_level", "Low")
        if level in ["High", "Moderate"]:
            print(f"→ {system} ({level})")
            
            if "Cardiometabolic" in system:
                print("   Tests: Full lipid panel, HbA1c, fasting insulin, hs-CRP, blood pressure log")
            elif "Immune" in system:
                print("   Tests: hs-CRP, Vitamin D (25(OH)D), CBC with differential, stool test for gut health")
            elif "Neuro" in system:
                print("   Tests: Consider cognitive baseline (if symptoms), sleep tracking, mood/symptom journal")
            elif "Oncological" in system:
                print("   Tests: Follow standard screening (PSA, mammogram, colonoscopy per age guidelines)")
            else:
                print("   Tests: General bloodwork + symptom tracking")
            print("")
    
    print("Actionable Next Step:")
    print("1. Get baseline bloodwork for top 2 systems")
    print("2. Track lifestyle variables for 4–6 weeks")
    print("3. Re-run pipeline and compare before/after")
    
    return risk_data


if __name__ == "__main__":
    generate_validation_plan()