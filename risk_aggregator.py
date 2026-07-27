#!/usr/bin/env python3
"""
risk_aggregator.py
Tuned risk aggregation for better signal.
"""

import json
from pathlib import Path

def aggregate_system_risk(summary_path="reports/all_traits_summary.json"):
    with open(summary_path) as f:
        traits = json.load(f)
    
    system_risk = {}
    
    for trait in traits:
        trait_lower = trait["trait"].lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        confidence = trait.get("confidence_score", 0)
        pgs = trait.get("raw_score", 0)
        
        for system_name, keywords in SYSTEMS.items():
            if any(kw in trait_lower for kw in keywords):
                if system_name not in system_risk:
                    system_risk[system_name] = {
                        "trait_count": 0,
                        "high_conf": 0,
                        "total_pgs": 0.0,
                        "traits": []
                    }
                
                system_risk[system_name]["trait_count"] += 1
                if confidence >= 50:                     # Lowered threshold
                    system_risk[system_name]["high_conf"] += 1
                system_risk[system_name]["total_pgs"] += pgs
                system_risk[system_name]["traits"].append(trait["trait"])
                break
    
    # Calculate risk score
    for name, data in system_risk.items():
        data["avg_pgs"] = data["total_pgs"] / data["trait_count"] if data["trait_count"] > 0 else 0
        data["risk_score"] = (data["high_conf"] * 10) + (data["avg_pgs"] * 0.6) + (data["trait_count"] * 0.5)        
        if data["risk_score"] > 35:
            data["risk_level"] = "High"
        elif data["risk_score"] > 18:
            data["risk_level"] = "Moderate"
        else:
            data["risk_level"] = "Low"
    
    # Sort by risk
    sorted_systems = sorted(system_risk.items(), key=lambda x: x[1]["risk_score"], reverse=True)
    
    print("\n=== RISK AGGREGATION ===\n")
    for system_name, data in sorted_systems:
        print(f"{system_name:<30} | {data['risk_level']:8} | {data['high_conf']:2d} high-conf traits | Avg PGS: {data['avg_pgs']:.1f}")
    
    return system_risk


if __name__ == "__main__":
    aggregate_system_risk()