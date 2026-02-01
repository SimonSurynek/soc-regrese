import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#----------Konfigurace----------

DATASET = "SinusovaZavislost"  # Název datasetu
KONSTANTY_KONFIGURACE = [
    {"typ": "fixed", "pocet": 5},
    {"typ": "fixed", "pocet": 15},
    {"typ": "fixed", "pocet": 20},
    {"typ": "evolvable", "pocet": 2},
    {"typ": "evolvable", "pocet": 3},
    {"typ": "evolvable", "pocet": 5},
]
DATA_PATH = Path("C:/Simon_Surynek/SOC_symbolicka_regrese/CSV vysledky/Experiment4_Vlivkonstant/SinusovaZavislost/")
OUTPUT_DIR = Path("C:/Simon_Surynek/SOC_symbolicka_regrese/Grafy/Experiment4")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Barvy pro jednotlivé konstanty
COLORS = {
    ('fixed', 5): '#1B4965',     # Tmavě modrá
    ('fixed', 15): '#2E86AB',    # Středně modrá
    ('fixed', 20): '#62B6CB',    # Světle modrá
    ('evolvable', 2): '#E63946', # Tmavě červená
    ('evolvable', 3): '#FF6B6B', # Červená
    ('evolvable', 5): '#FFA07A', # Světle oranžová
}

#----------Hlavní smyčka - Načítání dat pro každou konfiguraci konstant----------

all_data = {}  # Slovník: {(typ, pocet): matrix_dat}

for config in KONSTANTY_KONFIGURACE:  
    typ = config['typ']        
    pocet = config['pocet']    
    key = (typ, pocet)  
    
    print(f"\n{'='*60}")
    print(f"Načítám data pro {typ} {pocet} konstant")  
    print(f"{'='*60}")
    
    all_runs = []
    file_list = list(DATA_PATH.glob("fitness_history_*.csv"))
    
    # Načtení dat pro danou konfiguraci
    for file_fitness in file_list:
        fitness_name = file_fitness.stem
        vysledky_name = fitness_name.replace("fitness_history", "vysledky")
        file_vysledky = DATA_PATH / f"{vysledky_name}.csv"
        
        try:
            df_params = pd.read_csv(file_vysledky, sep=';')
            
            # Načti typ konstant
            typ_row = df_params[df_params['Parametr'] == 'Typ_konstant']
            file_typ = str(typ_row['Hodnota'].iloc[0])
            
            # Načti počet konstant
            pocet_row = df_params[df_params['Parametr'] == 'Pocet_konstant']
            file_pocet = int(pocet_row['Hodnota'].iloc[0])
            
            if file_typ == typ and file_pocet == pocet:
                df_fitness = pd.read_csv(file_fitness, sep=';')
                all_runs.append(df_fitness)
                
                if len(all_runs) >= 10:
                    break
                    
        except Exception as e:
            continue
    
    print(f"Načteno {len(all_runs)} běhů")
    
    if len(all_runs) == 0:
        print(f"Žádná data pro {typ} {pocet}")
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
    
    # Ulož data pro tuto konfiguraci
    all_data[key] = {
        'mean': np.mean(matrix, axis=0),
        'median': np.median(matrix, axis=0),
        'std': np.std(matrix, axis=0),
        'q75': np.percentile(matrix, 75, axis=0),
        'q25': np.percentile(matrix, 25, axis=0),
        'generations': np.arange(max_length),
        'n_runs': len(all_runs)
    }
    
    print(f"Finální fitness: {all_data[key]['mean'][-1]:.6f}")

#----------Vykreslení grafu se všemi konfiguracemi----------

plt.figure(figsize=(10, 5.75))

# Vykreslení pro každou konfiguraci
for config in KONSTANTY_KONFIGURACE:
    typ = config['typ']
    pocet = config['pocet']
    key = (typ, pocet)
    
    if key not in all_data:
        continue
    
    data = all_data[key]
    color = COLORS[key]
    
    # Label s jednotným formátem
    if typ == 'fixed':
        label = f"Fixní {pocet} (n={data['n_runs']})"
    else:
        label = f"Evolvovatelné {pocet} (n={data['n_runs']})"
    
    # Průměr (plná čára)
    plt.plot(data['generations'], data['mean'], 
             color=color, linewidth=2.5, 
             label=label)
    
    # Interval spolehlivosti (mezikvartilové rozpětí)
    plt.fill_between(data['generations'], 
                     data["q25"], data["q75"],
                     color=color, alpha=0.15)

# Popisky
plt.xlabel('Generace', fontsize=13, fontweight='bold')
plt.ylabel('Fitness', fontsize=13, fontweight='bold')
plt.title(f'Vliv typu konstant na konvergenci - Sinusový dataset', 
          fontsize=16, fontweight='bold', pad=20)
plt.legend(loc='lower right', fontsize=10, framealpha=0.9, ncol=2)
plt.grid(True, alpha=0.3, linestyle='--')

# Nastavení os
plt.ylim(-40, 0)
plt.xlim(0, 1000)

# Vylepšení vzhledu
plt.tight_layout()

# Ulož
output_file = OUTPUT_DIR / f"konvergence_{DATASET}_POROVNANI.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Graf uložen: {output_file}")

plt.show()

#----------Shrnutí výsledků----------

print(f"\n{'='*60}")
print("Shrnutí výsledků pro jednotlivé konfigurace konstant:")
print(f"{'='*60}\n")

print(f"{'Typ':<12} {'Počet':<8} {'Finální fitness':<18} {'Počet běhů':<12}")
print("-" * 60)

# Nejdřív fixní
print("Fixní:")
for config in KONSTANTY_KONFIGURACE:
    if config['typ'] == 'fixed':
        typ = config['typ']
        pocet = config['pocet']
        key = (typ, pocet)
        
        if key in all_data:
            mean_final = all_data[key]['mean'][-1]
            n_runs = all_data[key]['n_runs']
            print(f"  {pocet:<8} {mean_final:<18.6f} {n_runs:<12}")

# Pak evolvable
print("\nEvolvovatelné:")
for config in KONSTANTY_KONFIGURACE:
    if config['typ'] == 'evolvable':
        typ = config['typ']
        pocet = config['pocet']
        key = (typ, pocet)
        
        if key in all_data:
            mean_final = all_data[key]['mean'][-1]
            n_runs = all_data[key]['n_runs']
            print(f"  {pocet:<8} {mean_final:<18.6f} {n_runs:<12}")

print(f"\n{'='*60}")
print("Hotovo")