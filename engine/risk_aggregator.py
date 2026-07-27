import json
from systems_mapper import SYSTEMS
from pathlib import Path

def aggregate_system_risk(summary_path="reports/all_traits_summary.json"):
    print(f"DEBUG: Reading from {summary_path}")
    with open(summary_path, "r") as f:
        traits = json.load(f)
    
    system_risk = {}
    
    for trait in traits:
        trait_lower = trait["trait"].lower().replace(" ", "_").replace("/", "_")
        score = trait.get("confidence_score", 0)
        pgs = trait.get("raw_score", 0)
        
        found = False
        for system_name, keywords in SYSTEMS.items():
            if any(kw in trait_lower for kw in keywords):
                if system_name not in system_risk:
                    system_risk[system_name] = {
                        "trait_count": 0, "high_confidence_count": 0,
                        "total_pgs": 0, "traits": []
                    }
                system_risk[system_name]["trait_count"] += 1
                if score >= 70:
                    system_risk[system_name]["high_confidence_count"] += 1
                system_risk[system_name]["total_pgs"] += pgs
                system_risk[system_name]["traits"].append(trait["trait"])
                found = True
                break
    
    for system in system_risk:
        data = system_risk[system]
        data["avg_pgs"] = data["total_pgs"] / data["trait_count"] if data["trait_count"] > 0 else 0
        data["risk_level"] = "High" if data["high_confidence_count"] >= 3 else "Moderate" if data["high_confidence_count"] >= 2 else "Low"
    
    print("\n=== RISK AGGREGATION COMPLETE ===")
    for system_name, data in system_risk.items():
        print(f"{system_name:<30} | {data['risk_level']:8} | {data['high_confidence_count']:2d} high-confidence traits")
    
    with open("reports/system_risk_aggregation.json", "w") as f:
        json.dump(system_risk, f, indent=2)
    return system_risk

if __name__ == "__main__":
    aggregate_system_risk()
