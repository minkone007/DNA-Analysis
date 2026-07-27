# inventory_scanner.py

# 1. Load your personal inventory
my_rsids = {}
with open('full_bio_report.txt', 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 4:
            my_rsids[parts[0]] = parts[3]

# 2. Define a list of known interesting markers
interesting_markers = {
    "rs1801133": "MTHFR (Folate)",
    "rs4988235": "LCT (Lactose)",
    "rs12913832": "HERC2 (Eye Color)",
    "rs762551": "CYP1A2 (Caffeine)",
    "rs4680": "COMT (Dopamine)",
    "rs17822931": "ABCC11 (Earwax/Sweat)"
}

print(f"{'Marker':<15} | {'Your Genotype'}")
print("-" * 35)

for rsid, trait in interesting_markers.items():
    if rsid in my_rsids:
        # Use my_rsids instead of my_genotypes
        print(f"{rsid:<15} | {my_rsids[rsid]} ({trait})")
    else:
        print(f"{rsid:<15} | Not in your data")