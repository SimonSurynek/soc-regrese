# 🧬 Interaktivní symbolická regrese s využitím AI

[![Live Demo](https://img.shields.io/badge/demo-online-brightgreen)](https://simonsurynek.github.io/soc-regrese/)

> **Webová aplikace pro objevování matematických vztahů z dat pomocí kartézského genetického programování**

Tato aplikace umožňuje interaktivně experimentovat s parametry evolučního algoritmu a sledovat průběh hledání matematických funkcí v reálném čase. Projekt byl vytvořen jako práce do soutěže Středoškolská odborná činnost 2026.

## [**→ Vyzkoušet aplikaci online**](https://simonsurynek.github.io/soc-regrese/)

---

## O projektu

### Co je symbolická regrese?

Symbolická regrese automaticky objevuje matematické vztahy z dat **bez předem dané struktury funkce**. Na rozdíl od klasické regrese (kde musíte předem specifikovat zda se jedná o lineární/kvadratickou/... funkci) algoritmus sám hledá optimální matematický výraz.

### Jak to funguje?

Aplikace využívá **kartézské genetické programování (CGP)** – evoluční algoritmus inspirovaný přírodní evolucí:

1. Vytvoří náhodné kandidátní řešení
2. Pomocí mutace vytvoří několik potomků
3. Ohodnotí jejich kvalitu (fitness)
4. Vybere nejlepšího a opakuje proces, dokud nenajde optimální funkci

---

## Hlavní funkce

- **Interaktivní vizualizace** – Sledujte evoluci v reálném čase
- **Experimentování s parametry** – Lambda, mutace, počet uzlů, inicializace, konstanty
- **6 předpřipravených datasetů** – Lineární, kvadratický, sinusový, logaritmický, komplexní, fyzikální (šikmý vrh)
- **Nahrání vlastních dat** – Podporuje nahrání vlastních CSV/TXT souborů
- **Export výsledků** – Stažení parametrů, historie fitness hodnot a nalezeného vzorce
- **LaTeX výstup** – Profesionální zobrazení matematických vzorců

---

## Výsledky experimentů

Algoritmus byl úspěšně testován na:

| Dataset | Cílová funkce | MSE | Přesnost |
|---------|---------------|-----|----------|
| Lineární | `y = 2x + 3` | 0.0026 | ✅ 99.9% |
| Kvadratický | `y = (x+2)² + 3` | 0.0081 | ✅ 99.2% |
| Sinusový | `y = 6·sin(2x+1)` | 0.0058 | ✅ 99.4% |
| **Šikmý vrh** | `y = x − 0.0245x²` | 0.0048 | ✅ **98.5%** |

> **Rekonstrukce reálného fyzikálního problému** – Algoritmus dokázal z dat se šumem zrekonstruovat trajektorii šikmého vrhu s přesností přes 98%!

---

## Rychlý start

### Online verze (doporučeno)

Nejjednodušší způsob – otevřete přímo v prohlížeči:

 **https://simonsurynek.github.io/soc-regrese/**

### Lokální spuštění
```bash
# 1. Naklonujte repozitář
git clone https://github.com/SimonSurynek/soc-regrese.git
cd soc-regrese

# 2. Nainstalujte závislosti
npm install

# 3. Spusťte vývojový server
npm run dev

# 4. Otevřete v prohlížeči
# http://localhost:5173
```

---

## Technologie

- **Frontend:** Vue.js 3 (reaktivní rozhraní)
- **Vizualizace:** Chart.js (grafy), MathJax 3 (matematické vzorce)
- **Build:** Vite (rychlý dev server + optimalizovaný build)
- **Deployment:** GitHub Pages (automatické publikování přes GitHub Actions)

---

## Struktura projektu
```
soc-regrese/
├── public/
│   └── Datasets/           # Předpřipravené CSV datasety
├── src/
│   ├── components/
│   │   └── App.vue        # Hlavní komponenta (algoritmus + GUI)
│   ├── main.js            # Vstupní bod aplikace
│   └── style.css          # Globální styly
├── scripty_na_grafy/      # Python skripty pro analýzu výsledků
└── automatickeBehy.py     # Automatizované experimenty
```

---

## Akademické informace

**Autor:** Šimon Surýnek  
**Škola:** Gymnázium Brno-Řečkovice  
**Soutěž:** Středoškolská odborná činnost 2026  
**Obor:** 18 – Informatika  
**Konzultant:** Ing. Vojtěch Mrázek, Ph.D. (FIT VUT)

### Dokumentace

Kompletní teoretický základ, implementace a experimentální vyhodnocení jsou popsány v [**SOČ práci**](./18_Surynek_Simon.pdf).

**Klíčová zjištění:**
- Evolvovatelné konstanty výrazně překonávají fixní
- Inicializace s maximálním propojením dosahuje nejlepších výsledků
- Penalizace složitosti účinně brání bloatu
- Optimální nastavení: λ=20, COLS=10-15, Pm=0.2

---

## Návod k použití

### 1. Vyberte dataset

### 2. Nastavte parametry
- Lambda (počet potomků): 5–50
- Počet generací: 10–10000
- Pravděpodobnost mutace: 0.1–0.5
- Typ konstant: fixní / evolvovatelné

### 3. Spusťte evoluci
- Sledujte konvergenci v reálném čase
- Graf automaticky aktualizuje nalezenou funkci
- Log zobrazuje fitness každých 10 generací

### 4. Exportujte výsledky
- CSV s parametry a finální fitness
- Historie konvergence
- LaTeX zápis nalezené funkce

---

## Poděkování

- **Ing. Vojtěch Mrázek, Ph.D.** – Odborné konzultace z FIT VUT
- **Prof. Ing. Lukáš Sekanina, Ph.D.** – Inspirace v oblasti evolučních algoritmů
- **Mgr. Martina Blahová** – Korektura práce
- **Jihomoravský kraj** – Finanční podpora

---



## Kontakt

**GitHub:** [@SimonSurynek](https://github.com/SimonSurynek)  
**Email:** [simon.surynek@gmail.com]

---

## Užitečné odkazy

-  [Live demo](https://simonsurynek.github.io/soc-regrese/)
-  [Středoškolská odborná činnost](https://soc.cz/)
-  [FIT VUT - Kartézské genetické programování](https://www.fit.vut.cz/)

---

