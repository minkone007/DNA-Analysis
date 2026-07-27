#!/usr/bin/env python3
import numpy as np
from scipy.optimize import minimize

# Your master 72K high-resolution scaled coordinates
TARGET_NAME = "Minko_72K_Master"
TARGET_COORDS = np.array([
    0.1241, 0.1228, 0.0359, 0.0063, 0.0263, 0.0022, 0.0032, 0.0036, 0.0027, 
    0.0034, -0.0009, 0.0005, -0.0051, 0.0121, -0.0084, -0.0035, -0.0039, 
    0.0043, 0.0077, -0.0067, -0.0012, 0.0017, 0.0032, 0.0013, -0.0005
])

# Official G25 coordinates for archaic hominids vs modern reference frames
SOURCES = {
    "Neanderthal_Vindija": [-0.025041, -0.528076, -0.023381, 0.052003, 0.109867, -0.033746, -0.116562, 0.093457, -0.027406, -0.031527, 0.065443, -0.025328, 0.046828, -0.005367, -0.088625, -0.027048, 0.076927, -0.019383, -0.031299, 0.088042, -0.051409, 0.01422, -0.011832, -0.094593, 0.019759],
    "Neanderthal_Altai":   [-0.045529, -0.548437, -0.032809, 0.051034, 0.125255, -0.045738, -0.134190, 0.114688, -0.037837, -0.042643, 0.079246, -0.035517, 0.062437, -0.016377, -0.111834, -0.039644, 0.091350, -0.018243, -0.031676, 0.110290, -0.057524, 0.025102, -0.013434, -0.127006, 0.021076],
    "Denisovan_Archaic":   [-0.072847, -0.420428, -0.144066, 0.148581, 0.109252, -0.054384, -0.178371, 0.155762, -0.075470, -0.066881, 0.108476, -0.049457, 0.091728, -0.022708, -0.134498, -0.052506, 0.114221, -0.025591, -0.042108, 0.143944, -0.076241, 0.034375, -0.020336, -0.155806, 0.031015],
    "Modern_Eurasian_Core":[0.123000, 0.139000, 0.032000, -0.015000, 0.025000, -0.008000, 0.002000, 0.001000, 0.003000, 0.012000, -0.001000, 0.002000, -0.006000, 0.003000, -0.005000, -0.002000, 0.003000, 0.001000, 0.004000, -0.004000, -0.002000, 0.001000, 0.002000, 0.002000, -0.001000]
}

source_names = list(SOURCES.keys())
matrix = np.array([SOURCES[name] for name in source_names]).T

def objective(weights):
    predicted = np.dot(matrix, weights)
    return np.linalg.norm(TARGET_COORDS - predicted)

constraints = ({'type': 'eq', 'fun': lambda w: 1.0 - np.sum(w)})
bounds = [(0, 1) for _ in range(len(source_names))]
init_guess = [1.0 / len(source_names)] * len(source_names)

res = minimize(objective, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)

print("\n" + "="*50)
print(f" TERMINAL ARCHAIC ADMIXTURE FOR: {TARGET_NAME}")
print("="*50)
print(f"Mathematical Fit Distance: {res.fun * 100:.4f}%")
print("-"*50)

results = sorted(zip(source_names, res.x), key=lambda x: x[1], reverse=True)
for name, weight in results:
    if weight > 0.0001:  # Lower threshold to catch tiny archaic traces
        print(f" -> {name:<21} : {weight * 100:6.3f}%")
print("="*50 + "\n")