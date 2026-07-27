import csv
import os

# --- PATH CONFIGURATION ---
# We use 'input' so you can specify who you are scanning today
user_name = input("Enter the folder name (Minko/Julian/Stayko): ")
# This path navigates out of 'code/' and into your data structure
raw_data_file = f"../MyHeritage Raw DNA Data/{user_name}/MyHeritage_raw_dna_data.csv"

# --- ERROR CHECKING ---
if not os.path.exists(raw_data_file):
    print(f"Error: File not found at {raw_data_file}")
    exit()

# 2. Build a fast lookup dictionary (Index)
print(f"Indexing DNA for {user_name} (this happens only once)...")
dna_index = {}
with open(raw_data_file, mode='r') as f:
    # MyHeritage files usually use a header row; skip it if necessary
    reader = csv.reader(f)
    for row in reader:
        # Assuming format: rsid, chromosome, position, genotype
        # Adjust indices if your CSV has a different column order
        if len(row) >= 4 and row[0].startswith('rs'):
            dna_index[row[0]] = row[3]
print(f"Index complete! Loaded {len(dna_index)} markers.")

# 3. Search function
def get_genotype(rsid):
    return dna_index.get(rsid, "Not found in your data")

# 4. Your consolidated list of traits
targets = {
    # --- METABOLIC & ENERGY ---
    "rs1801282": "PPARGC1A (Metabolic Efficiency)",
    "rs1042713": "ADRB2 (Fat Mobilization)",
    "rs9939609": "FTO (Obesity/Hunger)",
    "rs1801260": "CLOCK (Circadian Rhythm)",
    "rs662799":  "APOA5 (High-Fat Diet Response)",
    "rs4994":    "ADRB3 (Resting Metabolic Rate)",
    
    # --- COGNITIVE & NEUROTRANSMITTER ---
    "rs4680":    "COMT (Dopamine Breakdown Speed)",
    "rs6265":    "BDNF (Brain Plasticity/Memory)",
    "rs1799971": "OPRM1 (Dopamine/Reward/Alcohol Cravings)",
    "rs53576":   "OXTR (Social/Empathy Processing)",
    "rs1800497": "DRD2 (Pleasure/Reward Sensitivity)",
    
    # --- IMMUNE & INFLAMMATION ---
    "rs1800795": "IL6 (Baseline Inflammation)",
    "rs2243250": "IL4 (Immune Regulation)",
    "rs1143627": "IL1B (Inflammatory Response)",
    "rs3021094": "VEGFA (Blood Vessel Growth)",
    
    # --- ATHLETIC & PHYSICAL ---
    "rs1815739": "ACTN3 (Muscle Power)",
    "rs4762":    "NOS3 (Nitric Oxide/Blood Flow)",
    "rs1799983": "ACE (Endurance)",
    
    # --- VITAMINS, DETOX & LONGEVITY ---
    "rs1801133": "MTHFR (Folate Cycle)",
    "rs1801131": "MTHFR (Additional Methylation marker)",
    "rs762551":  "CYP1A2 (Caffeine Metabolism)",
    "rs2228570": "VDR (Vitamin D Receptor)",
    "rs1045642": "ABCB1 (Drug/Toxin Transport)",
    "rs4880":    "SOD2 (Superoxide Dismutase)",
    "rs1229984": "ADH1B (Alcohol metabolism)",
    
    # --- PHYSICAL TRAITS & NUTRITION ---
    "rs6152":    "AR (Male Pattern Baldness)",
    "rs1805007": "MC1R (Red Hair/Anesthesia Sensitivity)",
    "rs17822931": "ABCC11 (Earwax/Sweat/Body Odor)",
    "rs7495174": "HERC2 (Position 28344238)",
    "rs12913832": "HERC2 (Position 28365618)",
    "rs1393350": "SLC24A4 (Pigmentation Modulator)",
    "rs1042602": "TYR (Tyrosinase - Melanin Production)",
    "rs16891982": "SLC45A2 (Melanin Pathway Modifier)",
    "rs4988235": "LCT (Lactose Intolerance)",
    
    # --- DISEASE & PROTECTION ---
    "rs7412":    "APOE (Alzheimer's Risk)",
    "rs429358":  "APOE (Alzheimer's Risk)",
    "rs333":     "CCR5 (HIV Resistance)",
    "rs1333049": "CDKN2B (Coronary Heart Disease)",
    "rs1051730": "CHRNA3 (Nicotine Dependence)",
    "rs3750344": "CHRNA5 (Nicotine Dependence)",
    "rs7903146": "TCF7L2 (Type-2 Diabetes Risk)",
    "rs12255372": "TCF7L2 (Diabetes/Breast Cancer Link)",
    "rs1800566": "HFE (Iron metabolism/Hemochromatosis)",
    "rs2267735": "CRHR1 (Cortisol/Stress response)",

    # --- SOCIAL & COGNITIVE ---
    "rs53576":   "OXTR (Social Behavior/Empathy)",
    "rs4680":    "COMT (Cognitive Effects)",
    "rs1800497": "DRD2 (Pleasure/Reward Sensitivity)",
    "rs1799971": "OPRM1 (Alcohol Cravings)",
    
    # --- PHYSICAL TRAITS & PIGMENTATION ---
    "rs6152":    "AR (Male Pattern Baldness)",
    "rs1805007": "MC1R (Red Hair/Anesthesia Sensitivity)",
    "rs17822931": "ABCC11 (Earwax/Sweat/Body Odor)",
    "rs7495174": "HERC2 (Position 28344238 - OCA2 Regulator)",
    "rs12913832": "HERC2 (Position 28365618 - Melanin Modulator)",
    "rs1393350":  "SLC24A4 (Pigmentation Modulator)",
    "rs1042602":  "TYR (Tyrosinase - Melanin Production)",
    "rs16891982": "SLC45A2 (Melanin Pathway Modifier)",
    
    # --- METABOLIC & HEALTH RISKS ---
    "rs9939609":  "FTO (Obesity/Type-2 Diabetes Risk)",
    "rs7903146":  "TCF7L2 (Type-2 Diabetes Risk)",
    "rs12255372": "TCF7L2 (Diabetes/Breast Cancer Link)",
    "rs662799":   "APOA5 (High-Fat Diet Response)",
    "rs4988235":  "LCT (Lactose Intolerance)",
    "rs762551":   "CYP1A2 (Caffeine Metabolism Speed)",
    "rs1801133":  "MTHFR (Folate Processing)",
    "rs2228570":  "VDR (Vitamin D Receptor Efficiency)",
    "rs1800566":  "HFE (Iron Metabolism/Hemochromatosis)",
    
    # --- DISEASE & PROTECTION ---
    "rs7412":    "APOE (Alzheimer's Risk)",
    "rs429358":  "APOE (Alzheimer's Risk)",
    "rs333":     "CCR5 (HIV Resistance)",
    "rs1333049": "CDKN2B (Coronary Heart Disease)",
    "rs1051730": "CHRNA3 (Nicotine Dependence)",
    "rs3750344": "CHRNA5 (Nicotine Dependence)",
    "rs1800795": "IL6 (Baseline Inflammation)",
    
    # --- PHYSICAL PERFORMANCE ---
    "rs1815739": "ACTN3 (Muscle Performance)",
    "rs4762":    "NOS3 (Nitric Oxide/Blood Flow)",
    "rs1799983": "ACE (Endurance Capacity)",
    "rs4880":    "SOD2 (Antioxidant Enzyme Capacity)"
}

print("\n--- Full Genomic Trait Report ---")
for rsid, trait in targets.items():
    print(f"{trait:<25} | {get_genotype(rsid)}")