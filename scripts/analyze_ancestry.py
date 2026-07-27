import math

# File paths
COORDS_FILE = 'My_G25_Coordinates.txt'
REFERENCE_FILE = 'Global25_PCA_Ancient_scaled.txt'

def parse_line(line):
    # Splits by comma and converts all PC values to floats
    parts = line.strip().split(',')
    # We take parts[1:] because parts[0] is the population name
    return parts[0], [float(x) for x in parts[1:]]

# Load your coordinates
with open(COORDS_FILE, 'r') as f:
    line = f.readline()
    my_name, my_coords = parse_line(line)

# Calculate Euclidean distance
def get_distance(target, reference):
    return math.sqrt(sum((t - r) ** 2 for t, r in zip(target, reference)))

results = []
# Load reference data
with open(REFERENCE_FILE, 'r') as f:
    # Skip the header line (PC1, PC2...)
    next(f)
    for line in f:
        if not line.strip(): continue
        name, ref_coords = parse_line(line)
        dist = get_distance(my_coords, ref_coords)
        results.append((name, dist))

# Sort by distance (closest first)
results.sort(key=lambda x: x[1])

print(f"--- Top 10 Closest Ancient Populations ---")
for name, dist in results[:10]:
    print(f"{name}: {dist:.4f}")