#!/usr/bin/env python3
"""
prs_engine.py
Main PRS engine with confidence scoring.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from confidence import calculate_confidence   # ← new import

def compute_prs_from_json(gwas_json_path: Path) -> Dict[str, Any]:
    """Process one gwas_*.json file with confidence scoring."""
    with open(gwas_json_path) as f:
        data = json.load(f)
    
    trait = data.get("trait", gwas_json_path.stem.replace("gwas_", "").replace("_", " ").title())
    pgs_score = data.get("pgs_score", 0)
    snps_used = data.get("pgs_snps_used", 0)
    total_snps = data.get("total_gwas_snps", 0)
    
    # Get confidence
    confidence_data = calculate_confidence(snps_used, pgs_score, total_snps)
    
    # Prediction logic
    if pgs_score > 50:
        prediction = "Elevated"
    elif pgs_score > 20:
        prediction = "Moderately Elevated"
    elif pgs_score < -20:
        prediction = "Reduced"
    else:
        prediction = "Average"
    
    result = {
        "trait": trait,
        "prediction": prediction,
        "raw_score": round(pgs_score, 4),
        "percentile": max(1, min(99, int(50 + pgs_score * 8))),
        "confidence_score": confidence_data["confidence_score"],
        "confidence_label": confidence_data["confidence_label"],
        "snps_scored": snps_used,
        "snps_available": total_snps,
        "evidence": "GWAS Catalog",
        "notes": f"PGS = {pgs_score:.1f} based on {snps_used} SNPs."
    }
    
    return result


def run_full_analysis() -> List[Dict]:
    """Process ALL gwas_*.json files."""
    results = []
    # Point explicitly to your verified GWAS data directory
    gwas_dir = Path("/Users/Minkone1/Documents/Minkone/Documents/DNA Virtual Lab/scripts/results/Minko/")
    
    for json_file in gwas_dir.glob("gwas_*.json"):
        result = compute_prs_from_json(json_file)
        results.append(result)
        print(f"✓ {json_file.name:<45} → {result['trait']:<25} | {result['confidence_label']}")
    
    # Save summary to your reports directory (use absolute path for safety)
    report_path = Path("/Users/Minkone1/Documents/Minkone/Documents/DNA Virtual Lab/reports/all_traits_summary.json")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Full analysis complete: {len(results)} traits processed.")
    return results


if __name__ == "__main__":
    run_full_analysis()