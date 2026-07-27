import csv

# 1. Load your genotypes from full_bio_report.txt
my_genotypes = {}
with open('full_bio_report.txt', 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 4:
            my_genotypes[parts[0]] = parts[3]

# 2. Load the traits you want to check from your new CSV
print(f"{'Trait':<30} | {'Your Genotype'}")
print("-" * 45)

with open('my_genes.csv', mode='r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rsid = row['rsID']
        trait = row['TraitName']
        
        # 3. Match and Print
        genotype = my_genotypes.get(rsid, "Not found")
        print(f"{trait:<30} | {genotype}")