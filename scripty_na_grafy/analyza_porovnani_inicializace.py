import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#----------Konfigurace----------

DATASET = "KomplexniDataset"  # Název datasetu
INICIALIZACE = ["random", "best_of_n", "maximal"]  # Všechny hodnoty inicializace
DATA_PATH = Path("C:/Simon_Surynek/SOC_symbolicka_regrese/CSV vysledky/Experiment5_Vlivinicializace/KomplexniDataset/")
OUTPUT_DIR = Path("C:/Simon_Surynek/SOC_symbolicka_regrese/Grafy/Experiment5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Barvy pro jednotlivé inicializace
COLORS = {
    'random': 'blue',
    'maximal': 'green',
    'best_of_n': 'red'
}

#----------Hlavní smyčka - Načítání dat pro každou hodnotu inicializace----------

all_data = {}  # Slovník: {inicializace: matrix_dat}

for inicializace in INICIALIZACE:
    print(f"\n{'='*60}")
    print(f"Načítám data pro Inicializaci={inicializace}")
    print(f"{'='*60}")
    
    all_runs = []
    file_list = list(DATA_PATH.glob("fitness_history_*.csv"))

    
    # Načtení dat pro danou inicializaci
    for file_fitness in file_list:
        fitness_name = file_fitness.stem
        vysledky_name = fitness_name.replace("fitness_history", "vysledky")
        file_vysledky = DATA_PATH / f"{vysledky_name}.csv"

        
        try:
            df_params = pd.read_csv(file_vysledky, sep=';')
            inicializace_row = df_params[df_params['Parametr'] == 'Inicializace']
            file_inicializace = str(inicializace_row['Hodnota'].iloc[0])

            if file_inicializace == inicializace:
                df_fitness = pd.read_csv(file_fitness, sep=';')
                all_runs.append(df_fitness)
                
                if len(all_runs) >= 10:
                    break
                    
        except Exception as e:
            continue
    
    print(f"Načteno {len(all_runs)} běhů")
    
    if len(all_runs) == 0:
        print(f"Žádná data pro Inicializaci={inicializace}")
        continue
    
    # Zpracování dat
    max_length = max(len(run) for run in all_runs)
    
    matrix = []
    for run in all_runs:
        fitness_values = run['Fitness'].values
        
        if len(fitness_values) < max_length:
            last_value = fitness_values[-1]
            fitness_values = np.pad(fitness_values, 
                                    (0, max_length - len(fitness_values)), 
                                    mode='constant', 
                                    constant_values=last_value)
        
        matrix.append(fitness_values)
    
    matrix = np.array(matrix)

    # Ulož data pro tuto inicializaci
    all_data[inicializace] = {
        'mean': np.mean(matrix, axis=0),
        'median': np.median(matrix, axis=0),
        'std': np.std(matrix, axis=0),
        'q75': np.percentile(matrix, 75, axis=0),
        'q25': np.percentile(matrix, 25, axis=0),
        'generations': np.arange(max_length),
        'n_runs': len(all_runs)
    }
    
    print(f"Finální fitness: {all_data[inicializace]['mean'][-1]:.6f}")

#----------Vykreslení grafu se všemi inicializacemi----------

plt.figure(figsize=(10, 5.75)) # Širší formát pro lepší čitelnost -pohrát

# Vykreslení pro každou inicializaci
for inicializace in INICIALIZACE:
    if inicializace not in all_data:
        continue

    data = all_data[inicializace]
    color = COLORS[inicializace]
    
    # Průměr (plná čára)
    plt.plot(data['generations'], data['mean'], 
             color=color, linewidth=2.5, 
             label=f'Inicializace={inicializace} (n={data["n_runs"]})')
    
    # Interval spolehlivosti (mezikvartilové rozpětí) - světlejší
    plt.fill_between(data['generations'], 
                     data["q25"], data["q75"],
                     color=color, alpha=0.15)

# Popisky
plt.xlabel('Generace', fontsize=13, fontweight='bold')
plt.ylabel('Fitness', fontsize=13, fontweight='bold')
plt.title(f'Vliv inicializace na konvergenci - Komplexní dataset', 
          fontsize=16, fontweight='bold', pad=20)
plt.legend(loc='lower right', fontsize=11, framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle='--')

# Nastavení os
plt.ylim(-130, 0)
plt.xlim(0, 1000)  # Pro detailní pohled na první generace

# Vylepšení vzhledu
plt.tight_layout()

# Ulož
output_file = OUTPUT_DIR / f"konvergence_{DATASET}_POROVNANI.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Graf uložen: {output_file}")

plt.show()

#----------Shrnutí výsledků----------

print(f"\n{'='*60}")
print("Shrnutí výsledků pro jednotlivé inicializace:")
print(f"{'='*60}\n")

print(f"{'inicializace':<6} {'Finální fitness':<18} {'Počet běhů':<12}")
print("-" * 40)
for inicializace in INICIALIZACE:
    if inicializace in all_data:
        mean_final = all_data[inicializace]['mean'][-1]
        n_runs = all_data[inicializace]['n_runs']
        print(f"{inicializace:<8} {mean_final:<18.6f} {n_runs:<12}")
print(f"\n{'='*60}")
print("Hotovo")
