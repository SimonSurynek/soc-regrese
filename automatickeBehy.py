import webbrowser
import time
import pyautogui

#Konfigurace pro test
datasety = ["KvadratickaZavislost.csv", "LinearniZavislost.csv", "LogaritmickaZavislost.csv", "SinusovaZavislost.csv", "KomplexniDataset.csv"]

# Konstanty konfigurace - širší pokrytí
KONSTANTY_KONFIGURACE = [
    {"typ": "fixed", "pocet": 5},       # Minimum fixních
    {"typ": "fixed", "pocet": 15},      # Baseline (výchozí)
    {"typ": "fixed", "pocet": 20},      # Maximum fixních
    {"typ": "evolvable", "pocet": 2},   # Minimum evolvable
    {"typ": "evolvable", "pocet": 3},   # Základní evolvable
    {"typ": "evolvable", "pocet": 5},   # Maximum evolvable
]
pocet_behu = 10

LAMBDA = 20
GENERACE = 1000
COLS = 10
MUTACE = 0.2

#----------Info o testu----------

celkem = len(datasety) * len(KONSTANTY_KONFIGURACE) * pocet_behu
cas_na_experiment = 0.8  # minuty na jeden experiment
celkovy_cas = celkem * cas_na_experiment

print(f"Parametry testu:")
print(f"Datasety: {len(datasety)} (KvadratickaZavislost, LinearniZavislost, LogaritmickaZavislost, SinusovaZavislost, KomplexniDataset)")
print(f"Typy konstant: {len(KONSTANTY_KONFIGURACE)}")
print(f"Fixní:")
for config in KONSTANTY_KONFIGURACE:
    if config['typ'] == 'fixed':
        print(f"      {config['pocet']:2d} konstant")
print(f"Evolvovatelné:")
for config in KONSTANTY_KONFIGURACE:
    if config['typ'] == 'evolvable':
        print(f"      {config['pocet']:2d} konstanty")
print(f"Běhů na kombinaci: {pocet_behu}")
print()
print(f"Počet experimentů: {celkem}")
print(f"Odhadovaný čas: {celkovy_cas:.0f} minut ({celkovy_cas/60:.1f} hodin)")

input("ENTER pro start testu...")


#----------Hlavni smycka----------

cislo = 1
start_time = time.time()

for dataset in datasety:
    nazev_datasetu = dataset.replace(".csv", "")
    
    for config in KONSTANTY_KONFIGURACE:
        typ_konstant = config['typ']
        pocet_konstant = config['pocet']
        
        for beh in range(pocet_behu):
            # Vytvoř URL
            url = (
                f"http://localhost:5173/?auto=true"
                f"&dataset={dataset}"
                f"&lambda={LAMBDA}"
                f"&generace={GENERACE}"
                f"&cols={COLS}"
                f"&mutace={MUTACE}"
                f"&typ_konstant={typ_konstant}"
                f"&pocet_konstant={pocet_konstant}"
            )
            
            # Vypis info
            print(f"[{cislo}/{celkem}] 📊 {nazev_datasetu:25s} {typ_konstant:12s} {pocet_konstant:2d} konstant | běh {beh+1}/{pocet_behu}")
            
            # před otevřením nového tabu - zavři předchozí (kromě prvního běhu)
            if cislo > 1:
                time.sleep(1)  # Počkej sekundu
                pyautogui.hotkey('ctrl', 'w')  # Zavře tab
                time.sleep(1)  # Počkej sekundu
            
            # Otevři nový tab
            webbrowser.open(url)
            
            print(f"Čekám {cas_na_experiment} minuty na dokončení...")
            
            # Čekej
            time.sleep(cas_na_experiment * 60)
            
            print(f"Dokončeno")
            print()
            
            cislo += 1

# Zavři poslední tab
time.sleep(1)
pyautogui.hotkey('ctrl', 'w')

#------------Vysledek------------

total_time = (time.time() - start_time) / 60

print(f"\n{'='*60}")
print(f"Celkový čas: {total_time:.1f} minut ({total_time/60:.1f} hodin)")
print(f"Provedeno experimentů: {celkem}")
print(f"{'='*60}")