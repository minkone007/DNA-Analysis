#!/usr/bin/env python3
import json
from collections import defaultdict

def summarize_pharmgkb():
    with open("reports/pharmgkb_matches.json") as f:
        matches = json.load(f)
    
    by_drug = defaultdict(list)
    by_gene = defaultdict(list)
    
    for m in matches:
        drug = m.get("drug", "Unknown")
        gene = m.get("gene", "Unknown")
        phenotype = m.get("phenotype", "")
        significance = m.get("significance", "")
        
        by_drug[drug].append(m)
        by_gene[gene].append(m)
    
    print("=== PHARMACOGENOMICS SUMMARY ===\n")
    print("Top Drugs with Potential Interactions:\n")
    for drug, items in sorted(by_drug.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
        print(f"• {drug} ({len(items)} variants)")
    
    print("\nTop Genes Involved:\n")
    for gene, items in sorted(by_gene.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"• {gene} ({len(items)} variants)")
    
    print("\nRecommendation: Discuss the top 5–10 drugs above with your doctor or pharmacist, especially if you are taking or planning to take antidepressants, antidiabetics, or pain medications.")

if __name__ == "__main__":
    summarize_pharmgkb()