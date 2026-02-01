
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#----------Konfigurace----------

DATASET = "KvadratickaZavislost"  # Název datasetu
MUTACE = [0.1, 0.2, 0.3, 0.5]  # Všechny mutace hodnoty k porovnání
DATA_PATH = Path(f"C:/Simon_Surynek/SOC_symbolicka_regrese/CSV vysledky/Experiment3_VlivMutace/KvadratickaZavislost/")
OUTPUT_DIR = Path("C:/Simon_Surynek/SOC_symbolicka_regrese/Grafy/Experiment3_box")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Barvy pro jednotlivé mutace hodnoty
COLORS = {
    0.1: 'red',
    0.2: 'blue',
    0.3: 'green',
    0.5: 'purple'
}

#----------Hlavní smyčka - Načítání dat----------

all_data = {pm: [] for pm in MUTACE}  # Slovník: {pm: [fitness_values]}

print(f"\n{'='*60}")
print(f"Načítání dat pro dataset: {DATASET}")
print(f"{'='*60}")

for vysledky_file in DATA_PATH.glob('vysledky_*.csv'):
    try:
        df_params = pd.read_csv(vysledky_file, sep=';')
        
        mutace_row = df_params[df_params['Parametr'] == 'Mutace']
        fitness_row = df_params[df_params['Parametr'] == 'Finalni_fitness']
        
        file_mutace = float(mutace_row['Hodnota'].iloc[0])
        file_fitness = float(fitness_row['Hodnota'].iloc[0])
        
        if file_mutace in MUTACE:
            all_data[file_mutace].append(file_fitness)
            
    except Exception as e:
        continue

# Výpis statistik
print(f"\n{'Pm':<8} {'Počet běhů':<15} {'Průměr':<15} {'Medián':<15}")
print("-" * 60)
for pm in MUTACE:
    if len(all_data[pm]) > 0:
        mean_val = np.mean(all_data[pm])
        median_val = np.median(all_data[pm])
        print(f"{pm:<8} {len(all_data[pm]):<15} {mean_val:<15.2f} {median_val:<15.2f}")

#----------Vykreslení boxplotu----------

print(f"\n{'='*60}")
print("Generování boxplotu")
print(f"{'='*60}\n")

plt.figure(figsize=(10, 6))

# Připrav data pro boxplot
boxplot_data = [all_data[pm] for pm in MUTACE]
positions = list(range(1, len(MUTACE) + 1))

# Vytvoř boxplot
bp = plt.boxplot(boxplot_data, 
                 positions=positions,
                 labels=[f'{pm}' for pm in MUTACE],
                 patch_artist=True,
                 widths=0.6)

# Obarvi boxy
for patch, pm in zip(bp['boxes'], MUTACE):
    patch.set_facecolor(COLORS[pm])
    patch.set_alpha(0.7)

# Popisky
plt.xlabel('Pravděpodobnost mutace', fontsize=13, fontweight='bold')
plt.ylabel('Fitness', fontsize=13, fontweight='bold')
plt.title(f'Vliv pravděpodobnosti mutace na finální fitness - Kvadratický dataset', 
          fontsize=16, fontweight='bold', pad=20)
plt.grid(axis='y', alpha=0.3, linestyle='--')

# Nastavení os
plt.ylim(-150, 0)  
plt.xlim(0.5, len(MUTACE) + 0.5)

# Vylepšení vzhledu
plt.tight_layout()

# Ulož
output_file = OUTPUT_DIR / f"boxplot_mutace_{DATASET}.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Graf uložen: {output_file}")

plt.show()

print(f"\n{'='*60}")
print("Hotovo")
print(f"{'='*60}")