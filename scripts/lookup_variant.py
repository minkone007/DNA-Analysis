targets = ["1801133", "4680", "762551"] 

# Use the full database, not the filtered MTHFR file
with open('variant_summary.txt', 'r') as f:
    lines = f.readlines() # Read all lines once to speed up the loop

for target in targets:
    print(f"\n--- Searching for variant: {target} ---")
    found = False
    for line in lines:
        if target in line:
            parts = line.split('\t')
            # Column 3=Name, 6=ClinicalSignificance, 7=ReviewStatus
            print(f"Variant: {parts[2]}")
            print(f"Significance: {parts[5]}")
            print(f"Review: {parts[6]}")
            found = True
    if not found:
        print("Not found in database.")