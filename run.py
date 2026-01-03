import webbrowser
import time
import pyautogui

#Konfigurace pro test
datasety = ["LinearniZavislost.csv", "KvadratickaZavislost.csv", "SinusovaZavislost.csv", "LogaritmickaZavislost.csv", "KomplexniDataset.csv"]
lambdy = [5, 10, 20, 50]
pocet_behu = 10

COLS = 10
MUTACE = 0.2
POCET_KONSTANT = 15

#----------Info o testu----------

celkem = len(datasety) * len(lambdy) * pocet_behu
cas_na_experiment = 0.6  # minuty
celkovy_cas = celkem * cas_na_experiment

print(f"Parametry testu:")
print(f"   • Datasety: {len(datasety)} (LinearniZavislost, KvadratickaZavislost, SinusovaZavislost, LogaritmickaZavislost, KomplexníZavislost)")
print(f"   • Lambda hodnoty: {len(lambdy)} ({lambdy})")
print(f"   • Běhů na kombinaci: {pocet_behu}")
print()
print(f"Pocet experimentů: {celkem}")
print(f"Odhadovaný čas: {celkovy_cas} minut")

input("ENTER pro start testu...")


#----------Hlavni smycka----------

cislo = 1
start_time = time.time()

for dataset in datasety:
    nazev_datasetu = dataset.replace(".csv", "")
    
    for lam in lambdy:
        for beh in range(pocet_behu):
            # Vytvoř URL
            url = (
                f"http://localhost:5173/?auto=true"
                f"&dataset={dataset}"
                f"&lambda={lam}"
                f"&cols={COLS}"
                f"&mutace={MUTACE}"
                f"&konstanty={POCET_KONSTANT}" 
            )
            
            # Vypis info
            print(f"[{cislo}/{celkem}] 📊 {nazev_datasetu:25s} | λ={lam:3d} | běh {beh+1}/{pocet_behu}")
            
            # PŘED otevřením nového tabu - zavři předchozí (kromě prvního běhu)
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

print(f"Celkový čas: {total_time:.1f} minut")
print(f"Provedeno experimentů: {celkem}")