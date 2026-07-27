import csv
import json

def match_genotypes_simple(csv_path, json_path):
    # Load your clinical/trait risks
    with open(json_path, 'r') as f:
        trait_data = json.load(f)

    matches = {}
    print("Cross-referencing your DNA with GWAS height data...")
    
    with open(csv_path, 'r') as f:
        # Use tab delimiter for .tsv files
        reader = csv.DictReader(f, delimiter='\t') 
        
        for row in reader:
            # Update these keys to match your GWAS file headers
            # (e.g., 'SNP_ID_CURRENT', 'STRONGEST_SNP_RISK_ALLELE')
            rsid = row.get('SNPS') 
            risk_allele = row.get('STRONGEST_SNP_RISK_ALLELE')
            
            if rsid in trait_data:
                # Logic to flag if your DNA matches the risk/trait allele
                matches[rsid] = {"trait": "height", "allele": risk_allele}

    # Save results
    with open('height_matches.json', 'w') as f:
        json.dump(matches, f, indent=4)
    print(f"Done! Found {len(matches)} matches.")