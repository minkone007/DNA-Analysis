#!/usr/bin/env python3
"""
confidence.py
Calculates a standardized confidence score for PRS results.
"""

def calculate_confidence(snps_scored: int, pgs_score: float, total_snps: int = 0) -> dict:
    """
    Returns confidence level and score (0-100) based on multiple factors.
    """
    # Base score from number of SNPs
    if snps_scored >= 4000:
        base = 95
    elif snps_scored >= 2000:
        base = 85
    elif snps_scored >= 800:
        base = 70
    elif snps_scored >= 200:
        base = 50
    elif snps_scored >= 50:
        base = 35
    else:
        base = 20

    # Bonus for replication / data quality (simplified for now)
    replication_bonus = min(15, int(snps_scored / 100))

    # Penalty for very high |PGS| with low SNPs (unreliable extremes)
    reliability_penalty = 0
    if abs(pgs_score) > 80 and snps_scored < 300:
        reliability_penalty = 25

    final_score = max(10, min(100, base + replication_bonus - reliability_penalty))

    # Confidence label
    if final_score >= 85:
        label = "Very High"
    elif final_score >= 70:
        label = "High"
    elif final_score >= 50:
        label = "Medium"
    elif final_score >= 30:
        label = "Low"
    else:
        label = "Very Low"

    return {
        "confidence_score": final_score,
        "confidence_label": label,
        "factors": {
            "snps_scored": snps_scored,
            "replication_bonus": replication_bonus,
            "reliability_penalty": reliability_penalty
        }
    }


# Test
if __name__ == "__main__":
    print(calculate_confidence(3757, 45.2))   # Height example
    print(calculate_confidence(15, 11.4))     # Vitamin D example