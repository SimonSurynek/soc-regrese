import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#----------Konfigurace----------

DATASET = "KvadratickaZavislost"  # Název datasetu

# Lambda konfigurace (generace × lambda = 60,000 evaluací)
LAMBDA_KONFIGURACE = [
    {"lambda": 5, "generace": 6000},
    {"lambda": 10, "generace": 3000},
    {"lambda": 20, "generace": 2000},
    {"lambda": 50, "generace": 1200},
    
]

DATA_PATH = "C:/Simon_Surynek/SOC_symbolicka_regrese/CSV vysledky/Experiment1_Vlivlambdy/KvadratickaZavislost/"
OUTPUT_DIR = Path("C:/Simon_Surynek/SOC_symbolicka_regrese/Grafy/Experiment1")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Barvy pro jednotlivé lambdy
COLORS = { 
    10: 'blue',
    20: 'green',
    50: 'purple',
    5: 'red'
}

#----------Hlavní smyčka - Načítání dat pro každou lambdu----------

all_data = {}  # Slovník: {lambda: matrix_dat}

for config in LAMBDA_KONFIGURACE:
    LAMBDA = config['lambda']
    
    print(f"\n{'='*60}")
    print(f"Načítám data pro lambda={LAMBDA}")
    print(f"{'='*60}")
    
    all_runs = []
    file_list = list(Path(DATA_PATH).glob("fitness_history_*.csv"))
    
    # Načtení dat pro danou lambdu
    for file_fitness in file_list:
        fitness_name = file_fitness.stem
        vysledky_name = fitness_name.replace("fitness_history", "vysledky")
        file_vysledky = f"{DATA_PATH}{vysledky_name}.csv"
        
        try:
            df_params = pd.read_csv(file_vysledky, sep=';')
            lambda_row = df_params[df_params['Parametr'] == 'Lambda']
            file_lambda = int(lambda_row['Hodnota'].iloc[0])
            
            if file_lambda == LAMBDA:
                df_fitness = pd.read_csv(file_fitness, sep=';')
                all_runs.append(df_fitness)
                
                if len(all_runs) >= 10:
                    break
                    
        except Exception as e:
            continue
    
    print(f"Načteno {len(all_runs)} běhů")
    
    if len(all_runs) == 0:
        print(f"Žádná data pro λ={LAMBDA}")
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
    
    #Vytvoř pole evaluací (generace × lambda)
    generace = np.arange(max_length)
    evaluace = generace * LAMBDA
    
    # Ulož data pro tuto lambdu
    all_data[LAMBDA] = {
        'mean': np.mean(matrix, axis=0),
        'median': np.median(matrix, axis=0),
        'std': np.std(matrix, axis=0),
        'q75': np.percentile(matrix, 75, axis=0),
        'q25': np.percentile(matrix, 25, axis=0),
        'generations': generace,
        'evaluace': evaluace,
        'n_runs': len(all_runs)
    }
    
    print(f"Finální fitness: {all_data[LAMBDA]['mean'][-1]:.6f}")

#----------Vykreslení grafu se všemi lambdami----------

plt.figure(figsize=(10, 5.75))

# Vykreslení pro každou lambdu
for config in LAMBDA_KONFIGURACE:
    LAMBDA = config['lambda']
    
    if LAMBDA not in all_data:
        continue
    
    data = all_data[LAMBDA]
    color = COLORS[LAMBDA]
    
    # Průměr (plná čára) - osa X = evaluace
    plt.plot(data['evaluace'], data['mean'], 
             color=color, linewidth=2.5, 
             label=f'λ={LAMBDA} (n={data["n_runs"]})')
    
    # Interval spolehlivosti (mezikvartilové rozpětí) - světlejší
    plt.fill_between(data['evaluace'], 
                     data["q25"], data["q75"],
                     #data['mean'] + data['std'],
                     color=color, alpha=0.15)

# popisek osy X
plt.xlabel('Počet evaluací (generace × λ)', fontsize=13, fontweight='bold')
plt.ylabel('Fitness', fontsize=13, fontweight='bold')
plt.title(f'Vliv λ na konvergenci - Kvadratický dataset', 
          fontsize=16, fontweight='bold', pad=20)
plt.legend(loc='lower right', fontsize=11, framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle='--')

# Nastavení os
plt.ylim(-300, 0)
plt.xlim(0, 60000)

# Vylepšení vzhledu
plt.tight_layout()

# Ulož
output_file = OUTPUT_DIR / f"konvergence_{DATASET}_POROVNANI.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Graf uložen: {output_file}")

plt.show()

#----------Shrnutí----------

print(f"\n{'='*60}")
print("Shrnutí výsledků pro jednotlivé λ:")
print(f"{'='*60}\n")

print(f"{'Lambda':<8} {'Finální fitness':<18} {'Počet běhů':<12}")
print("-" * 40)
for config in LAMBDA_KONFIGURACE:
    LAMBDA = config['lambda']
    if LAMBDA in all_data:
        mean_final = all_data[LAMBDA]['mean'][-1]
        n_runs = all_data[LAMBDA]['n_runs']
        print(f"{LAMBDA:<8} {mean_final:<18.6f} {n_runs:<12}")

print(f"\n{'='*60}")
print("Hotovo")