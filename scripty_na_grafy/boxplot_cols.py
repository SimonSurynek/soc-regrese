
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#----------Konfigurace----------

DATASET = "KvadratickaZavislost"  # Název datasetu
COLS = [5, 10, 15, 25]  # Všechny COLS hodnoty k porovnání
DATA_PATH = Path(f"C:/Simon_Surynek/SOC_symbolicka_regrese/CSV vysledky/Experiment2_Vlivcols/KvadratickaZavislost/")
OUTPUT_DIR = Path("C:/Simon_Surynek/SOC_symbolicka_regrese/Grafy/Experiment2_box")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Barvy pro jednotlivé COLS hodnoty
COLORS = {
    5: 'red',
    10: 'blue',
    15: 'green',
    25: 'purple'
}

#----------Hlavní smyčka - Načítání dat----------

all_data = {cols: [] for cols in COLS}  # Slovník: {cols: [fitness_values]}

print(f"\n{'='*60}")
print(f"Načítání dat pro dataset: {DATASET}")
print(f"{'='*60}")

for vysledky_file in DATA_PATH.glob('vysledky_*.csv'):
    try:
        df_params = pd.read_csv(vysledky_file, sep=';')
        
        cols_row = df_params[df_params['Parametr'] == 'COLS']
        fitness_row = df_params[df_params['Parametr'] == 'Finalni_fitness']
        
        file_cols = int(cols_row['Hodnota'].iloc[0])
        file_fitness = float(fitness_row['Hodnota'].iloc[0])
        
        if file_cols in COLS:
            all_data[file_cols].append(file_fitness)
            
    except Exception as e:
        continue

# Výpis statistik
print(f"\n{'COLS':<8} {'Počet běhů':<15} {'Průměr':<15} {'Medián':<15}")
print("-" * 60)
for cols in COLS:
    if len(all_data[cols]) > 0:
        mean_val = np.mean(all_data[cols])
        median_val = np.median(all_data[cols])
        print(f"{cols:<8} {len(all_data[cols]):<15} {mean_val:<15.2f} {median_val:<15.2f}")

#----------Vykreslení boxplotu----------

print(f"\n{'='*60}")
print("Generování boxplotu")
print(f"{'='*60}\n")

plt.figure(figsize=(10, 6))

# Připrav data pro boxplot
boxplot_data = [all_data[cols] for cols in COLS]
positions = list(range(1, len(COLS) + 1))

# Vytvoř boxplot
bp = plt.boxplot(boxplot_data, 
                 positions=positions,
                 labels=[str(c) for c in COLS],
                 patch_artist=True,
                 widths=0.6)

# Obarvi boxy
for patch, cols in zip(bp['boxes'], COLS):
    patch.set_facecolor(COLORS[cols])
    patch.set_alpha(0.7)

# Popisky
plt.xlabel('COLS', fontsize=13, fontweight='bold')
plt.ylabel('Fitness', fontsize=13, fontweight='bold')
plt.title(f'Vliv parametru COLS na finální fitness - Kvadratická závislost', 
          fontsize=16, fontweight='bold', pad=20)
plt.grid(axis='y', alpha=0.3, linestyle='--')

# Nastavení os
plt.ylim(-100,0)  
plt.xlim(0.5, len(COLS) + 0.5)

# Vylepšení vzhledu
plt.tight_layout()

# Ulož
output_file = OUTPUT_DIR / f"boxplot_cols_{DATASET}.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Graf uložen: {output_file}")

plt.show()

print(f"\n{'='*60}")
print("Hotovo")
print(f"{'='*60}")