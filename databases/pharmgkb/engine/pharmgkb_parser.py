import pandas as pd
import os
import json

# Setup paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, '..', 'var_drug_ann.tsv')
RAW_DNA = os.path.join(SCRIPT_DIR, '..', '..', '..', 'data', 'Minko', 'MyHeritage_raw_dna_data.csv')

def load_raw_genotypes(raw_path):
    genotypes = {}
    with open(raw_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.startswith('"rs'):
                continue
            parts = line.strip().split(',')
            if len(parts) >= 4:
                rsid = parts[0].strip('"')
                genotype = parts[3].strip('"')
                genotypes[rsid] = genotype
    return genotypes

def match_pharmgkb(raw_path=RAW_DNA, pharmgkb_file=DB_PATH):
    genotypes = load_raw_genotypes(raw_path)
    df = pd.read_csv(pharmgkb_file, sep='\t', low_memory=False)
    
    matches = []
    # Efficient matching using dictionary lookup
    for _, row in df.iterrows():
        variant_info = str(row.get('Variant/Haplotypes', '')).strip()
        if variant_info in genotypes:
            matches.append({
                "rsid": variant_info,
                "your_genotype": genotypes[variant_info],
                "gene": row.get('Gene', ''),
                "drug": row.get('Drug(s)', ''),
                "phenotype": row.get('Phenotype Category', ''),
                "significance": row.get('Significance', 'Unknown'),
                "notes": str(row.get('Notes', ''))[:200]
            })
    
    print(f"Found {len(matches)} pharmacogenomic matches")
    
    # Ensure reports directory exists
    os.makedirs(os.path.join(SCRIPT_DIR, '..', '..', '..', 'reports'), exist_ok=True)
    report_path = os.path.join(SCRIPT_DIR, '..', '..', '..', 'reports', 'pharmgkb_matches.json')
    
    with open(report_path, "w") as f:
        json.dump(matches, f, indent=2)
    
    return matches

if __name__ == "__main__":
    matches = match_pharmgkb()
    for m in matches[:10]:
        print(f"{m['rsid']} ({m['your_genotype']}) → {m['drug']}")