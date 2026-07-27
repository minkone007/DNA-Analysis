import math

# Your personal K36 values in a list (in order)
my_values = [0.16, 4.86, 1.33, 7.72, 14.55, 0.18, 8.55, 9.68, 3.22, 8.80, 4.82, 7.23, 1.46, 10.46, 0.17, 1.70, 5.45, 5.12, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.15, 3.39, 0.0, 0.0, 0.0, 0.0]

def calculate_distance(my_vals, pop_vals):
    return math.sqrt(sum((a - b)**2 for a, b in zip(my_vals, pop_vals)))

results = []

with open('references.txt', 'r') as f:
    for line in f:
        parts = line.split()
        pop_name = parts[0]
        pop_vals = [float(x) for x in parts[1:]]
        dist = calculate_distance(my_values, pop_vals)
        results.append((pop_name, dist))

# Sort and print
for pop, dist in sorted(results, key=lambda x: x[1]):
    print(f"{pop}: {dist:.4f}")