# pathogenic_scanner.py

# 1. Load your personal data into a dictionary for fast lookup
my_data = {}
with open('full_bio_report.txt', 'r') as f:
    for line in f:
        # Skip empty lines or headers if they exist
        if not line.strip() or line.startswith('rsid'): continue
        
        # .split() without arguments splits by any whitespace (tabs/spaces)
        parts = line.split()
        
        # Based on your file: parts[0] is rsID, parts[3] is the genotype
        if len(parts) >= 4:
            rsid = parts[0]
            genotype = parts[3]
            my_data[rsid] = genotype
        else:
            print(f"Skipping malformed line: {line.strip()}")

print(f"Loaded {len(my_data)} variants. Scanning for Pathogenic variants...")

# 2. Scan the massive ClinVar file
print("Scanning for Pathogenic variants...")
with open('variant_summary.txt', 'r') as f:
    for line in f:
        # We check every line to see if it contains one of your rsIDs
        for rsid, genotype in my_data.items():
            if rsid in line:
                parts = line.split('\t')
                significance = parts[5]
                # Check if 'Pathogenic' is in the classification string
                if 'Pathogenic' in significance:
                    print(f"MATCH FOUND: {rsid} (Your Genotype: {genotype})")
                    print(f"Clinical Significance: {significance}")
                    print("-" * 30)