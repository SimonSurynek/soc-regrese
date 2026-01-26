<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { Chart } from 'chart.js/auto'

const log = ref("");

//Pro v-for k zobrazení funkčního předpisu datasetu
const datasety = [
  { 
    value: 'LinearniZavislost.csv', 
    label: 'Lineární',
    formula: 'f(x) = 2x + 3'
  },
  { 
    value: 'KvadratickaZavislost.csv', 
    label: 'Kvadratická',
    formula: 'f(x) = (x + 2)² + 3'
  },
  { 
    value: 'SinusovaZavislost.csv', 
    label: 'Sinusová',
    formula: 'f(x) = 6·sin(2x+1)'
  },
  { 
    value: 'LogaritmickaZavislost.csv', 
    label: 'Logaritmická',
    formula: 'f(x) = 5·log(x + 1) + 0.5'
  },
  { 
    value: 'KomplexniDataset.csv', 
    label: 'Komplexní',
    formula: 'f(x) = x² + 2·sin(2x) - 0.3x'
  },
  { 
    value: 'SikmyVrh.csv', 
    label: 'Šikmý Vrh',
    formula: 'y(x) = x − 0.0245·x²'
  }
];

// Stavy evoluce  pro tlacitko
const EvoluceProbiha = ref(false);
const zastavitEvoluci = ref(false);

const predpisFunkce = ref("");

//pro vybirani typu a poctu konstant
const typKonstant = ref('evolvable');
const pocetFixnichKonstant = ref(10);
const pocetEvolKonstant = ref(3);

// Zpusoby inicializace chromozomu
const typInicializace = ref('random');
const PocetKandidatu = ref(100);

// Parametry evolučního algoritmu
const COLS = ref(10); // počet funkčních bloků v chromozomu
const chromozom = ref([]);
const VelikostChromozomu = 3;  // počet genů na jeden funkční blok (fixní hodnota 3)
const lambda = ref(20);
const PocetIteraci = ref(5000);
const PravdepodobnostMutace = ref(0.2);
const dostupneFunkce = [
  { name: "plus", label: "+" },
  { name: "minus", label: "-" },
  { name: "krat", label: "*" },
  { name: "deleno", label: "/" },
  { name: "log", label: "log" },
  { name: "sqrt", label: "sqrt" },
  { name: "sin", label: "sin" },
];
const vybraneFunkce = ref(["plus", "minus", "krat", "deleno", "log", "sqrt", "sin"]);

// Data a datasety
const vybranyDataset = ref('LinearniZavislost.csv');
const nactenaData = ref([]);

// Vlastní data// Vlastní data
const vlastniDataNahrana = ref(false);
const vlastniDatasetNazev = ref('');

// Graf, logy, tabulka
const chartCanvas = ref(null);
const logEvo = ref([]);
const zobrazit = ref(false);
let chartInstance = null;
const HodnotyY = ref([]);
const fitnessHistory = ref([]);

// ---------Nahrání datsetu uživatelem----------
function NahratVlastniData(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Kontrola přípony
  if (!file.name.endsWith('.csv') && !file.name.endsWith('.txt')) {
    alert('Podporované formáty: .csv, .txt');
    event.target.value = '';
    return;
  }
  
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const text = e.target.result;
      
      // Normalizace konců řádků
      const normalizedText = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      const lines = normalizedText.trim().split('\n');
      
      // Kontrola minimálního počtu řádků
      if (lines.length < 2) {
        throw new Error('Soubor musí obsahovat hlavičku a alespoň jeden řádek dat');
      }
      
      // Parsování dat (přeskočit hlavičku)
      const parsedData = lines.slice(1).map((line, index) => {
        const parts = line.split(';');
        
        // Kontrola počtu sloupců
        if (parts.length !== 2) {
          throw new Error(`Řádek ${index + 2}: Očekávány 2 sloupce (x;y), nalezeno ${parts.length}`);
        }
        
        const x = Number(parts[0]);
        const y = Number(parts[1]);
        
        // Kontrola číselných hodnot
        if (isNaN(x) || isNaN(y)) {
          throw new Error(`Řádek ${index + 2}: Neplatná číselná hodnota (x="${parts[0]}", y="${parts[1]}")`);
        }
        
        return { x, y };
      });
      
      // Kontrola, že máme aspoň jeden bod
      if (parsedData.length === 0) {
        throw new Error('Soubor neobsahuje žádná platná data');
      }
      
      // Úspěch - nahraď data
      nactenaData.value = parsedData;
      vlastniDataNahrana.value = true;
      vlastniDatasetNazev.value = file.name;
      vybranyDataset.value = 'vlastni'; // označení vlastního datasetu
      
      // Aktualizuj graf
      nextTick(() => updateChart(false));
      
      console.log(`✅ Úspěšně nahráno ${parsedData.length} bodů z ${file.name}`);
      
    } catch (error) {
      alert('❌ Chyba při čtení souboru:\n\n' + error.message + '\n\nOčekávaný formát:\nx;y\n1;2\n3;4');
      event.target.value = ''; // Reset file input
      vlastniDataNahrana.value = false;
    }
  };
  
  reader.onerror = () => {
    alert('❌ Chyba při čtení souboru');
    event.target.value = '';
  };
  
  reader.readAsText(file);
}

// --------Načítání datasetu, zpracování---------
async function nactiDataset() {
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}Datasets/${vybranyDataset.value}`);
    const text = await response.text();

    console.log('Raw text:', text);
    console.log('Text length:', text.length);

    // Normalizuj konce řádků - nahraď všechny \r\n a \r za \n
    const normalizedText = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const lines = normalizedText.trim().split('\n');
    console.log('Lines:', lines);
    console.log('Lines count:', lines.length);

    // Odstranění hlavičky a parsování dat
    nactenaData.value = lines.slice(1).map(line => {
      const [x, y] = line.split(';').map(Number);
      console.log('Parsed:', { x, y });
      return { x, y };
    });

    console.log('Načtená data:', nactenaData.value);

    // vykresli pouze scatter po změně datasetu (bez červené křivky)
    nextTick(() => {
      updateChart(false);
    });

  } catch (error) {
    console.error('Chyba:', error);
  }
}

// Načtení výchozího datasetu při spuštění aplikace
nactiDataset();

// ---------Funkce pro generování fixních konstant---------
function VygenerujFixniKonstanty() {
  const konstanty = [];
  const pocet = pocetFixnichKonstant.value;
  
  if (pocet === 5) {
    return [-2, -1, 0, 1, 2];
  } else if (pocet === 10) {
    return [-3, -2, -1, -0.5, -0.1, 0, 0.1, 0.5, 1, 2];
  } else if (pocet === 15) {
    return [-5, -3, -2, -1, -0.5, -0.3, -0.1, 0, 0.1, 0.3, 0.5, 1, 2, 3, 5];
  } else if (pocet === 20) {
    // Pro 20 konstant vytvoř rovnoměrně rozložené hodnoty od -10 do 10
    const rozsah = 10;
    const krok = (2 * rozsah) / (pocet - 1);
    for (let i = 0; i < pocet; i++) {
      konstanty.push(Number((-rozsah + i * krok).toFixed(2)));
    }
    return konstanty;
  }
  return [0]; // fallback
}

// ------Funkce pro generování Gaussova normálového rozdělení--------
function gaussianRandom(mean = 0, stdev = 1) {
  const u = 1 - Math.random();
  const v = Math.random();
  const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  return z * stdev + mean;
}

// --------Generování náhodného chromozomu--------
function GenerovaniNahodnehoChromozomu() {
  const chrom = [];

  // Priprava indexu konstant
  let indexyKonstant = [];
  if (typKonstant.value === 'fixed') {
    // Fixní konstanty mají indexy 1001, 1002, 1003, ...
    const pocet = pocetFixnichKonstant.value;
    for (let i = 0; i < pocet; i++) {
      indexyKonstant.push(1001 + i);
    }
  } else {
    // Evolvovatelné konstanty mají indexy 2000, 2001, 2002, ...
    for (let i = 0; i < pocetEvolKonstant.value; i++) {
      indexyKonstant.push(2000 + i);
    }
  }

  for (let i = 0; i < COLS.value; i++) {
    const PovoleneVstupy = [];

    if (i === 0) {
      const in1 = 0; // valX
      // muze vybrat jak valX tak prvek z množiny kopie konstant
      const moznosti = [0, ...indexyKonstant];
      const in2 = moznosti[Math.floor(Math.random() * moznosti.length)];
      const fn = Math.floor(Math.random() * vybraneFunkce.value.length);
      chrom.push(in1, in2, fn);
      continue;
    }

    // Přidej všechny předchozí uzly jako možné vstupy
    for (let x = 0; x < i; x++) {
      PovoleneVstupy.push(x + 1);
    }

    // Zbytek chromozomu pravidla pro tvoření vstupů
    PovoleneVstupy.push(...indexyKonstant);

    const in1 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
    const in2 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
    const fn = Math.floor(Math.random() * vybraneFunkce.value.length);

    chrom.push(in1, in2, fn);
  }
  // Pridani outputu
  chrom.push(COLS.value);

  // Pro evolvovatelné konstanty
  if (typKonstant.value === 'evolvable') {
    for (let i = 0; i < pocetEvolKonstant.value; i++) {
      // Inicializuj konstanty s Gaussovým rozložením (střed 0, rozptyl 2)
      const konstanta = gaussianRandom(0, 2);
      chrom.push(konstanta);
    }
  }
  

  chromozom.value = chrom;
  console.log("Nahodne generovany chromozom", chrom);
  return chrom;
}

// -------Generování chromozomu s maximální délkou-------
function GenerovaniMaximalnihoChromozomu() {
  const chrom = [];
  
  // Indexy konstant 
  let indexyKonstant = [];
  if (typKonstant.value === 'fixed') {
    const pocet = pocetFixnichKonstant.value;
    for (let i = 0; i < pocet; i++) {
      indexyKonstant.push(1001 + i);
    }
  } else {
    for (let i = 0; i < pocetEvolKonstant.value; i++) {
      indexyKonstant.push(2000 + i);
    }
  }

  // Generování uzlů
  for (let i = 0; i < COLS.value; i++) {
    if (i === 0) {
      const in1 = 0; // valX
      const moznosti = [0, ...indexyKonstant];
      const in2 = moznosti[Math.floor(Math.random() * moznosti.length)];
      const fn = Math.floor(Math.random() * vybraneFunkce.value.length);
      chrom.push(in1, in2, fn);
      continue;
    }

    // in1 = předchozí uzel (zaručuje propojení)
    const in1 = i;
    
    // in2 = libovolný předchozí uzel nebo konstanta
    const PovoleneVstupy = [];
    for (let j = 0; j < i; j++) {
      PovoleneVstupy.push(j);
    }
    PovoleneVstupy.push(...indexyKonstant);
    
    const in2 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
    const fn = Math.floor(Math.random() * vybraneFunkce.value.length);

    chrom.push(in1, in2, fn);
  }

  // Output = poslední uzel (maximální délka)
  chrom.push(COLS.value);

  // Evolvovatelné konstanty
  if (typKonstant.value === 'evolvable') {
    for (let i = 0; i < pocetEvolKonstant.value; i++) {
      const konstanta = gaussianRandom(0, 2);
      chrom.push(konstanta);
    }
  }

  chromozom.value = chrom;
  console.log("Generovany MAXIMALNI chromozom", chrom);
  return chrom;
}

// ------Generování chromozomu jako nejlepšího z N kandidátů------
function GenerovaniNejlepsihoChromozomu() {
  let bestChrom = null;
  let bestFitness = -Infinity;

  // Vygeneruj N kandidátů
  for (let i = 0; i < PocetKandidatu.value; i++) {
    const kandidat = GenerovaniNahodnehoChromozomu();
    const fitness = VypocitejFitness(kandidat);
    
    if (fitness > bestFitness) {
      bestChrom = [...kandidat];
      bestFitness = fitness;
    }
  }

  chromozom.value = bestChrom;
  console.log(`Best of ${PocetKandidatu.value}: fitness = ${bestFitness}`);
  return bestChrom;
}

// -----Switch pro různé typy inicilizace------
function GenerovaniChromozomu() {
  switch (typInicializace.value) {
    case 'random':
      return GenerovaniNahodnehoChromozomu();
    case 'maximal':
      return GenerovaniMaximalnihoChromozomu();
    case 'best_of_n':
      return GenerovaniNejlepsihoChromozomu();
    default:
      return GenerovaniNahodnehoChromozomu();
  }
}

// ----- Vyhodnocení chromozomu -----
function chrom_evaluate(chrom, valX) {
  const values = [];
  values[0] = valX; // Vstupní hodnota X
  
  // Načtení hodnot, co které číslo reprezentuje
  if (typKonstant.value === 'fixed') {
    // Fixní konstanty - načti z chromozomu
    const fixniKonstanty = VygenerujFixniKonstanty();
    for (let i = 0; i < fixniKonstanty.length; i++) {
      values[1001 + i] = fixniKonstanty[i];
    }
  } else {
    // Evolvovatelné konstanty - načti Z CHROMOZOMU
    const evolveKonstanty = COLS.value * VelikostChromozomu + 1;
    for (let i = 0; i < pocetEvolKonstant.value; i++) {
      values[2000 + i] = chrom[evolveKonstanty + i];
    }
  }

  //Vytváření chromozomu
  for (let i = 0; i < COLS.value; i++) {
    let in1 = chrom[i * VelikostChromozomu + 0];
    let in2 = chrom[i * VelikostChromozomu + 1];
    let fn = chrom[i * VelikostChromozomu + 2];

    in1 = values[in1];
    in2 = values[in2];

    // Ošetři NaN vstupy
    if (isNaN(in1) || !isFinite(in1)) in1 = 0;
    if (isNaN(in2) || !isFinite(in2)) in2 = 0;

    let operatory = vybraneFunkce.value;
    let result = 0;

    // Provádění operací podle fce
    switch (operatory[fn]) {
      case "plus":
        result = in1 + in2;
        break;
      case "krat":
        result = in1 * in2;
        break;
      case "minus":
        result = in1 - in2;
        break;
      case "deleno":
        result = (in2 !== 0 && Math.abs(in2) > 1e-10) ? in1 / in2 : 0;
        break;
      case "sqrt":
        result = in1 >= 0 ? Math.sqrt(in1) : 0;
        break;
      case "sin":
        result = Math.sin(in1);
        break;
      case "log":
        result = in1 > 1e-10 ? Math.log(in1) : 0;
        break;
      default:
        result = 0;
        break;
    }

    // Finální kontrola výsledku
    if (isNaN(result) || !isFinite(result)) {
      result = 0;
    }

    values[i + 1] = result;
  }

  const idout = chrom[COLS.value * VelikostChromozomu];
  const finalResult = values[idout];

  // Ošetři finální výsledek
  return (isNaN(finalResult) || !isFinite(finalResult)) ? 0 : finalResult;
}

// ----- Výpočet Y podle chromozomu -----
function PocitaniY() {
  if (nactenaData.value.length === 0) return;

  HodnotyY.value = nactenaData.value.map(item => {
    const vypoctene = chrom_evaluate(chromozom.value, item.x);
    return {
      x: item.x,
      ySpravne: item.y,
      yVypoctene: (isNaN(vypoctene) || !isFinite(vypoctene)) ? 0 : vypoctene
    };
  });
}

// ----- Mutace chromozomu -----
function MutaceChromozomu(chrom) {
  //Zjisteni kde konci funkční bloky a začínají konstanty
  const delkaFunkcniCasti = COLS.value * VelikostChromozomu + 1;
  // Počet  mutaci
  const pocetMutaci = Math.max(1, Math.floor(delkaFunkcniCasti * PravdepodobnostMutace.value));

  for (let m = 0; m < pocetMutaci; m++) {
    // Nahodny index z CELEHO CHROMOZOMU
    const index = Math.floor(Math.random() * (chrom.length));

    //Pokud je to evolvovatelná konstanta
    if (typKonstant.value === 'evolvable' && index >= delkaFunkcniCasti) {
      chrom[index] += gaussianRandom(0, 0.5);
      // Omezeni, aby moc nevystřelilo
      chrom[index] = Math.max(-100, Math.min(100, chrom[index]));
      continue; 
    }

    // Prvni gen zachovat valX
    if (index === 0) continue;

    // Mutace podle pozice v chromozomu
    if (index === delkaFunkcniCasti - 1) {
      chrom[index] = Math.floor(Math.random() * COLS.value); // Mutace outputu
      continue;
    }

    // Mutace funkce (každý 3. gen)
    if (index % VelikostChromozomu === 2) {
      chrom[index] = Math.floor(Math.random() * vybraneFunkce.value.length);
      continue;
    }

    // Mutace vstupu (každý 1. a 2. gen v trojici)
    const PovolenaCisla = [];
    for (let x = 0; x <= Math.floor(index / VelikostChromozomu); x++) { 
      PovolenaCisla.push(x); // Pouze předchozi uzly
    }

    // Pridani konstant do moznosti mutace
    if (typKonstant.value === 'fixed') {
      for (let i = 0; i < pocetFixnichKonstant.value; i++) {
        PovolenaCisla.push(1001 + i);
      }
    } else {
      for (let i = 0; i < pocetEvolKonstant.value; i++) {
        PovolenaCisla.push(2000 + i);
      }
    }

    chrom[index] = PovolenaCisla[Math.floor(Math.random() * PovolenaCisla.length)]; //Samotná mutace
  }
}

// ----- Fitness funkce -----
function VypocitejFitness(chrom) {
  if (nactenaData.value.length === 0) return -Infinity; // Kontrola načtení dat

  let mse = 0;
  let invalidCount = 0;

  // Cyklus projíždějící všemi daty a počítající MSE
  for (let i = 0; i < nactenaData.value.length; i++) {
    const { x, y: spravneY } = nactenaData.value[i];
    const predikovaneY = chrom_evaluate(chrom, x);

    // Další kontrola platnosti predikovaných hodnot
    if (isNaN(predikovaneY) || !isFinite(predikovaneY)) {
      invalidCount++;
      mse += 1000; // Velká penalizace
    } else {
      const chyba = predikovaneY - spravneY; //Samotný výpočet chyby
      mse += Math.pow(chyba, 2);
    }
  }

  // Pokud má chromozom příliš mnoho neplatných hodnot, penalizuj nekonečnem
  if (invalidCount > nactenaData.value.length * 0.5) {
    return -Infinity;
  }
 
  // Průměrné MSE
  mse /= nactenaData.value.length;
 
  //-- Další penalizace pro speciální případy ----
  // 1)Penalizace pro funkce bez variability
  // Penalizace nízké variability
  const predY = nactenaData.value.map(item => chrom_evaluate(chrom, item.x));
  const validPredY = predY.filter(y => isFinite(y) && !isNaN(y));

  if (validPredY.length < 2) {
    return -Infinity;
  }

  const mean = validPredY.reduce((sum, y) => sum + y, 0) / validPredY.length;
  const variance = validPredY.reduce((sum, y) => sum + Math.pow(y - mean, 2), 0) / validPredY.length;

  // Kontroluj varianci pouze pokud dataset není konstantní
  const targetMean = nactenaData.value.reduce((sum, item) => sum + item.y, 0) / nactenaData.value.length;
  const targetVariance = nactenaData.value.reduce((sum, item) => {
    const diff = item.y - targetMean;
    return sum + diff * diff;
  } , 0) / nactenaData.value.length;

  // Pokud má dataset variaci, ale predikce ne, penalizuj
  if (targetVariance > 0.01 && variance < 0.0001) {
    return -Infinity;
  }

  // 2)Penalizace za složitost, dá se experimentovat s hodnotou
  const aktivniUzly = SpocitejAktivniUzly(chrom);
  const komplexitaPenalizace = aktivniUzly * 0.002; // váha penalizace za složitost

  return -(mse + komplexitaPenalizace);
}

// -------Pomocná funkce pro spočítání aktivních uzlů-------
function SpocitejAktivniUzly(chrom) {
  const aktivni = new Set();
  const output = chrom[chrom.length - 1];

  function WatchChromozom(index) {
    // Základní podmínky pro rekurzi
    if (index <= 0 || index >= 1001 || aktivni.has(index)) return;
    aktivni.add(index);

    // Rekurzivní volání pro vstupy
    const in1 = chrom[(index - 1) * VelikostChromozomu + 0];
    const in2 = chrom[(index - 1) * VelikostChromozomu + 1];
    WatchChromozom(in1);
    WatchChromozom(in2);
  }

  WatchChromozom(output);
  return aktivni.size;
}

// ----- Evoluční algoritmus -----
async function EvolucniAlgoritmus() {

  // Kontrola výběru funkcí
  if (vybraneFunkce.value.length === 0) {
    alert("Vyber alespoň jednu povolenou funkci!");
    return;
  }

  // Inicializace evoluce
  EvoluceProbiha.value = true;
  zastavitEvoluci.value = false;
  logEvo.value = [];
  fitnessHistory.value = [];
  let parent = GenerovaniChromozomu();
  let bestFitness = VypocitejFitness(parent);
  let bestOffspring = [...parent];
  let bestOffspringFitness = bestFitness;

  // Hlavní evoluční smyčka
  for (let g = 0; g < PocetIteraci.value; g++) {

    // Kontrola zastavení uživatelem
    if (zastavitEvoluci.value) {
      logEvo.value.push(`Evoluce byla zastavena uživatelem na generaci ${g}.`);
      EvoluceProbiha.value = false;
      break;
    }

    // Generování potomků a výběr nejlepšího
    for (let i = 0; i < lambda.value; i++) {
      let offspring = [...parent];
      MutaceChromozomu(offspring);
      let offspringFitness = VypocitejFitness(offspring);
      if (offspringFitness >= bestOffspringFitness) {
        bestOffspring = [...offspring];
        bestOffspringFitness = offspringFitness;
      }
    }

    parent = [...bestOffspring];
    bestFitness = bestOffspringFitness;
    console.log(`Generace ${g}: bestFitness = ${bestFitness}`);

    // Uložení historie fitness
    fitnessHistory.value.push({
      generace: g,
      fitness: bestFitness
    });

    // Aktualizace grafu každých 5 generací
    if (g % 5 === 0) {
      chromozom.value = [...bestOffspring];
      updateChart(true);
      await new Promise(resolve => setTimeout(resolve, 0));
    }

    // Kontrola dosažení cílové fitness
    if (-bestFitness < 0.01) {
      logEvo.value.push(`Dosaženo cílové fitness, Generace ${g}.`);
      break;
    }

    // Logování každých 10 generací
    if (g % 10 === 0) {
      logEvo.value.push(`Generace ${g}: bestFitness = ${bestFitness.toFixed(6)}`);
      scrollLogToBottom();
    }
  }

  chromozom.value = [...bestOffspring];

  // Output index je vždy na pozici: COLS * 3
  const outputIndex = chromozom.value[COLS.value * VelikostChromozomu];
  predpisFunkce.value = FunkcniPredpis(outputIndex);

  // Zobraz výsledky
  PocitaniY();

  // Finalní aktualizace grafu a zastavení animace, že evoluce probíhá
  await nextTick();
  updateChart(true);
  EvoluceProbiha.value = false;
}


// ------ Aktualizace grafu -----
function updateChart(showModel = true) {
  // Kontrola platnosti dat
  if (!chartCanvas.value || nactenaData.value.length === 0) return;

  // Zničení předchozí instance grafu
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  // Data z excelu (modré body)
  const scatterData = nactenaData.value.map(item => ({
    x: item.x,
    y: item.y
  }));

  const datasets = [
    {
      label: 'Správná data (CSV)',
      data: scatterData,
      backgroundColor: 'rgba(54, 162, 235, 0.8)',
      borderColor: 'rgba(54, 162, 235, 1)',
      pointRadius: 6,
      type: 'scatter',
      showLine: false,
      parsing: false
    }
  ];

  // Přidání červené křivky, podmínka showModel === true a chromozom existuje
  if (showModel && chromozom.value && chromozom.value.length) {
    const lineData = nactenaData.value
      .map(item => ({ x: item.x, y: chrom_evaluate(chromozom.value, item.x) }))
      .sort((a, b) => a.x - b.x);

    datasets.push({
      label: 'Naučená funkce',
      data: lineData,
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgba(255, 99, 132, 1)',
      borderWidth: 2,
      pointRadius: 0,
      type: 'line',
      tension: 0.4,
      parsing: false,
      showLine: true
    });
  }

  // Vytvoření nové instance grafu
  chartInstance = new Chart(chartCanvas.value, {
    type: 'scatter',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: { display: true, text: 'Symbolická regrese - Porovnání' },
        legend: { display: true, position: 'top' }
      },
      scales: {
        x: { title: { display: true, text: 'x' } },
        y: { title: { display: true, text: 'y' } }
      }
    }
  });
}

// ----- Automatické scrollování logu -----
function scrollLogToBottom() {
  nextTick(() => {
    const logElement = document.querySelector('.log-content');
    if (logElement) {
      logElement.scrollTop = logElement.scrollHeight;
    }
  });
}

// ----- Zastavení evoluce -----
function ZastavitEvoluci() {
  zastavitEvoluci.value = true;
}

// -----Hledání funkčního předpisu podle chromozomu-----
function FunkcniPredpis(index) {
  //Vstup X
  if (index === 0) return "x";

  // Konstanty
  // Fixní konstanty
  if (typKonstant.value === 'fixed' && index >= 1001 && index < 1001 + pocetFixnichKonstant.value) {
    const fixniKonstanty = VygenerujFixniKonstanty();
    const hodnota = fixniKonstanty[index - 1001];
    return hodnota >= 0 ? hodnota.toString() : `(${hodnota})`;
  }

  // Evolvovatelné konstanty
  if (typKonstant.value === 'evolvable' && index >= 2000 && index < 2000 + pocetEvolKonstant.value) {
    const offsetKonstant = COLS.value * VelikostChromozomu + 1;
    const hodnota = chromozom.value[offsetKonstant + (index - 2000)];
    return hodnota >= 0 ? hodnota.toFixed(3) : `(${hodnota.toFixed(3)})`;
  }

  const in1Index = chromozom.value[(index - 1) * VelikostChromozomu + 0];
  const in2Index = chromozom.value[(index - 1) * VelikostChromozomu + 1];
  const fnIndex = chromozom.value[(index - 1) * VelikostChromozomu + 2];

  const in1 = FunkcniPredpis(in1Index);
  const in2 = FunkcniPredpis(in2Index);
  const operatory = vybraneFunkce.value;
  let VyslednyPredpis = "";

  // Pomocná funkce pro určení, zda je potřeba závorky
  const needsParens = (expr) => {
    return expr.includes('+') || expr.includes('-') || expr.includes('\\cdot') || expr.includes('\\div');
  };

  // Sestavení výrazu podle operátoru
  switch (operatory[fnIndex]) {
    case "plus":
      VyslednyPredpis = `${in1} + ${in2}`;
      break;
    case "krat":
      const left = needsParens(in1) ? `(${in1})` : in1;
      const right = needsParens(in2) ? `(${in2})` : in2;
      VyslednyPredpis = `${left} \\cdot ${right}`;
      break;
    case "minus":
      VyslednyPredpis = `${in1} - ${in2}`;
      break;
    case "deleno":
      VyslednyPredpis = `\\frac{${in1}}{${in2}}`;
      break;
    case "sqrt":
      VyslednyPredpis = `\\sqrt{${in1}}`;
      break;
    case "sin":
      VyslednyPredpis = `\\sin(${in1})`;
      break;
    case "log":
      VyslednyPredpis = `\\log(${in1})`;
      break;
  }
  return VyslednyPredpis;
}

onMounted(() => {
  if (!window.MathJax) {
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']]
      },
      startup: {
        ready: () => {
          window.MathJax.startup.defaultReady();
          window.MathJax.startup.promise.then(() => {
            console.log('MathJax loaded');
          });
        }
      }
    };

    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js';
    script.async = true;
    document.head.appendChild(script);
  }
  
  // Automatický režim pro výsledky
  const params = new URLSearchParams(window.location.search);
  
  if (params.get('auto') === 'true') {
    console.log('Automatický režim');
    
    // Nastav parametry
    if (params.get('dataset')) {
      vybranyDataset.value = params.get('dataset');
      nactiDataset(); 
    }
    if (params.get('lambda')) {
      lambda.value = parseInt(params.get('lambda'));
    }
    if (params.get('inicializace')) {
    typInicializace.value = params.get('inicializace');
  }
    if (params.get('cols')) {
      COLS.value = parseInt(params.get('cols'));
    }
    if (params.get('mutace')) {
      PravdepodobnostMutace.value = parseFloat(params.get('mutace'));
    }
    if (params.has('generace')) {
      PocetIteraci.value = parseInt(params.get('generace'));
    }
    if (params.get('typ_konstant')) {
      typKonstant.value = params.get('typ_konstant');
    }

    if (params.get('pocet_konstant')) {
      const pocet = parseInt(params.get('pocet_konstant'));
      if (typKonstant.value === 'fixed') {
      pocetFixnichKonstant.value = pocet;
      } else if (typKonstant.value === 'evolvable') {
      pocetEvolKonstant.value = pocet;
      }
    }
    
    // Spusť po 3 sekundách
    setTimeout(async () => {
      console.log('Spouštím...');
      await EvolucniAlgoritmus();
      await nextTick();
      ExportVysledkuDoCSV();
      document.title = 'HOTOVO';
      console.log('Hotovo!');
    }, 3000);
  }
});

// Watch pro re-render MathJax když se změní předpis
watch(predpisFunkce, () => {
  nextTick(() => {
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise().catch((err) => console.log(err));
    }
  });
});

// ----- Export výsledků do CSV -----
function ExportVysledkuDoCSV() {
  if (!chromozom.value || chromozom.value.length === 0) {
    alert('Spusťte nejprve evoluci.');
    return;
  }
  
  const finalFitness = VypocitejFitness(chromozom.value);
  const aktivniUzly = SpocitejAktivniUzly(chromozom.value);
  const finalMSE = -finalFitness - (aktivniUzly * 0.002); // Odečtení penalizace za složitost
  
  // Definice timestampu
  const timestamp = Date.now();

  
  let csv = "Parametr;Hodnota\n";
  csv += `Dataset;${vybranyDataset.value}\n`;
  if (vybranyDataset.value === 'vlastni' && vlastniDatasetNazev.value) {
    csv += `Vlastni_soubor;${vlastniDatasetNazev.value}\n`;
  }
  csv += `Inicializace;${typInicializace.value}\n`;
  csv += `Typ_konstant;${typKonstant.value}\n`;
  csv += `Pocet_konstant;${typKonstant.value === 'fixed' ? pocetFixnichKonstant.value : pocetEvolKonstant.value}\n`;
  csv += `Lambda;${lambda.value}\n`;
  csv += `Generace_max;${PocetIteraci.value}\n`;
  csv += `COLS;${COLS.value}\n`;
  csv += `Mutace;${PravdepodobnostMutace.value}\n`;
  csv += `Finalni_fitness;${finalFitness.toFixed(6)}\n`;
  csv += `Finalni_MSE;${finalMSE.toFixed(6)}\n`;
  csv += `Aktivni_uzly;${aktivniUzly}\n`;
  csv += `Vysledny_vzorec;"${predpisFunkce.value}"\n`;
  csv += `Timestamp;${new Date().toISOString()}\n`;
  
  // Export parametrů a výsledků
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `vysledky_${vybranyDataset.value.replace('.csv', '')}_${timestamp}.csv`;
  a.click();
  URL.revokeObjectURL(url);

  // Export fitness history
  let csvHistory = "Generace;Fitness\n";
  fitnessHistory.value.forEach(row => {
    csvHistory += `${row.generace};${row.fitness}\n`;
  });
  
  const blobHistory = new Blob([csvHistory], { type: 'text/csv;charset=utf-8;' });
  const urlHistory = URL.createObjectURL(blobHistory);
  const aHistory = document.createElement('a');
  aHistory.href = urlHistory;
  aHistory.download = `fitness_history_${vybranyDataset.value.replace('.csv', '')}_${timestamp}.csv`;
  aHistory.click();
  URL.revokeObjectURL(urlHistory);
}
</script>

<template>
  <div id="container">
    <header id="header">
      <h1>Symbolická regrese s využitím AI</h1>
    </header>

    <aside id="LevaCast">
      <div id="VyberDatasetu">
        <h3>Výběr datasetu:</h3>
        <label v-for="dataset in datasety" :key="dataset.value">
          <input type="radio" v-model="vybranyDataset" :value="dataset.value" @change="nactiDataset">
          {{ dataset.label }}
          <span v-if="dataset.formula" class="info-icon" :title="dataset.formula">ⓘ</span>
        </label>
        <label>
          <input type="radio" v-model="vybranyDataset" value="vlastni" @change="nactiDataset">
          Vlastní data
        </label>
        <!-- File input - zobrazí se jen když je vybrán "Vlastní data" -->
        <div v-if="vybranyDataset === 'vlastni'" class="vlastni-data-upload">
          <input type="file" accept=".csv,.txt" @change="NahratVlastniData" class="file-input" ref="fileInputRef">
          <p class="upload-hint">Formát: x;y (s hlavičkou)</p>
          <!-- Úspěšné nahrání -->
          <div v-if="vlastniDataNahrana" class="upload-success">✅ Nahráno: <strong>{{ vlastniDatasetNazev }}</strong><br>({{ nactenaData.length }} bodů)</div>
        </div>
      </div>

      <div class="funkce-panel">
        <h3>Povolené funkce:</h3>
        <div class="funkce-grid">
          <label v-for="f in dostupneFunkce" :key="f.name" class="funkce-item">
            <input type="checkbox" :value="f.name" v-model="vybraneFunkce">
            {{ f.label }}
          </label>
        </div>
      </div>

      <div class="nastaveni-panel">
      <h3>Zpusob inicializace:</h3>
        <label class="param-label">
        <select v-model="typInicializace" class="param-input">
          <option value="random">Náhodná inicializace</option>
          <option value="maximal">Output poslední uzel</option>
          <option value="best_of_n">Nejlepší ze 100</option>
        </select>
      </label>
      </div>
      <div class="nastaveni-panel">
      <h3>Typ konstant:</h3>
  
      <label class="param-label">
        <span>Režim:</span>
        <select v-model="typKonstant" class="param-input">
          <option value="fixed">Fixní konstanty</option>
          <option value="evolvable">Evolvovatelné konstanty</option>
        </select>
      </label>

      <label v-if="typKonstant === 'fixed'" class="param-label">
      <span>Počet fixních konstant:</span>
        <select v-model.number="pocetFixnichKonstant" class="param-input">
          <option :value="5">5 konstant</option>
          <option :value="10">10 konstant</option>
          <option :value="15">15 konstant</option>
          <option :value="20">20 konstant</option>
        </select>
      </label>

      <label v-if="typKonstant === 'evolvable'" class="param-label">
        <span>Počet evolvovatelných konstant:</span>
        <input 
        type="number" 
        v-model.number="pocetEvolKonstant" 
        min="1" 
        max="5" 
        class="param-input"
        >
      </label>
      </div>
      <div class="nastaveni-panel">
        <h3>Nastavení evoluce:</h3>

        <label class="param-label">
          <span>Lambda (λ):</span>
          <input type="number" v-model.number="lambda" min="1" max="100" class="param-input">
        </label>

        <label class="param-label">
          <span>Počet generací:</span>
          <input type="number" v-model.number="PocetIteraci" min="10" max="10000" step="10" class="param-input">
        </label>

        <label class="param-label">
          <span>Max počet uzlů:</span>
          <input type="number" v-model.number="COLS" min="3" max="20" class="param-input">
        </label>
        <label class="param-label">
          <span>Pravděpodobnost mutace:</span>
          <input type="number" v-model.number="PravdepodobnostMutace" min="0" max="0.5" step="0.01" class="param-input">
        </label>
      </div>
    </aside>

    <main id="PravaCast">
      <!-- Horní řádek: Graf + Tlačítko/Log -->
      <div id="TabulkaLogButton">
        <!-- Graf -->
        <div id="Graf">
          <canvas ref="chartCanvas"></canvas>
        </div>

        <!-- Pravá část: Tlačítko + Log -->
        <div class="right-panel">
          <div class="button-row" :class="{ 'single-button': HodnotyY.length === 0 || EvoluceProbiha }">
            <button v-if="!EvoluceProbiha" id="EvoluceButton" @click="EvolucniAlgoritmus">Spusť evoluci</button>
            <div v-else class="evolve-spinner">
              <div class="spinner"></div>
              <p>Evoluce běží...</p>
              <button @click="ZastavitEvoluci" class="stop-button">Zastavit</button>
            </div>
            <button v-if="HodnotyY.length > 0 && !EvoluceProbiha" id="export-button" @click="ExportVysledkuDoCSV">📊 Export Výsledků</button>
          </div>
          <div id="evolog">
            <h3>Log evoluce:</h3>
            <div class="log-content">
              <div v-for="line in logEvo" :key="line">{{ line }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Střední řádek: Předpis + Chromozom (fixed výška, bez scrollu) -->
      <div id="FunkcniCast">
        <div class="info-box">
          <h4>Funkční předpis:</h4>
          <div class="math-formula">
            $f(x) = {{ predpisFunkce }}$
          </div>
        </div>

         <div class="info-box">
          <h4>Chromozom:</h4>
          <p>{{ chromozom }}</p>
        </div>
      </div>

      <!-- Dolní řádek: Tabulka (scrollovatelná) -->
      <div id="TabulkovaCast">
        <table id="HodnotyTabulka">
          <thead>
            <tr>
              <th>x</th>
              <th>Očekávaná y</th>
              <th>Vypočítaná y</th>
              <th>Absolutní odchylka</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hodnota in HodnotyY" :key="hodnota.x">
              <td>{{ hodnota.x.toFixed(3) }}</td>
              <td>{{ hodnota.ySpravne?.toFixed(3) ?? 'N/A' }}</td>
              <td>{{ hodnota.yVypoctene?.toFixed(3) ?? 'N/A' }}</td>
              <td>{{ hodnota.ySpravne !== undefined ? Math.abs(hodnota.yVypoctene - hodnota.ySpravne).toFixed(3) : 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>


<style scoped>
/* Grid container */
#container {
  display: grid;
  grid-template-rows: 60px 1fr;
  grid-template-columns: 250px 1fr;
  height: 100vh;
  width: 100vw;
  gap: 0;
  margin: 0;
  padding: 0;
}

/* Header */
#header {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 2px solid #555;
}

#header h1 {
  font-size: 24px;
  margin: 0;
}

/* Levý sidebar */
#LevaCast {
  grid-column: 1;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #1a1a1a;
  border-right: 2px solid #333;
  overflow-y: auto;
}

#VyberDatasetu,
.funkce-panel {
  background: #2a2a2a;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #444;
}

#VyberDatasetu h3,
.funkce-panel h3 {
  color: white;
  font-size: 16px;
  margin-bottom: 12px;
}

#VyberDatasetu label {
  display: block;
  color: white;
  margin-bottom: 8px;
  cursor: pointer;
  font-size: 14px;
}

.info-icon {
  margin-left: 5px;
  font-size: 16px;
  color: #aaaaaa; 
  transition: all 0.2s;
  user-select: none;
}

.info-icon:hover {
  color: #ffffff; 
  transform: scale(1.15);
}
/* Vlastní data upload */
.vlastni-data-upload {
  margin-top: 12px;
  padding: 12px;
  background: #1a1a1a;
  border-radius: 6px;
  border: 1px dashed #667eea;
}

.file-input {
  display: block;
  width: 100%;
  padding: 8px;
  margin-bottom: 8px;
  background: #2a2a2a;
  color: white;
  border: 1px solid #444;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}

.file-input::-webkit-file-upload-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 8px;
}

.file-input::-webkit-file-upload-button:hover {
  opacity: 0.9;
}

.upload-hint {
  color: #888;
  font-size: 12px;
  margin: 8px 0;
  line-height: 1.5;
}

.upload-hint code {
  background: #0d0d0d;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #4CAF50;
}

.upload-success {
  margin-top: 8px;
  padding: 8px;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid #4CAF50;
  border-radius: 4px;
  color: #4CAF50;
  font-size: 12px;
  line-height: 1.6;
}

.upload-success strong {
  color: white;
}

/* Funkce grid - 2 sloupce */
.funkce-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.funkce-item {
  display: flex;
  align-items: center;
  color: white;
  cursor: pointer;
  font-size: 14px;
}

.funkce-item input[type="checkbox"] {
  margin-right: 6px;
}

.nastaveni-panel {
  background: #2a2a2a;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #444;
}

.nastaveni-panel h3 {
  color: white;
  font-size: 16px;
  margin-bottom: 12px;
}

.param-label {
  display: flex;
  flex-direction: column;
  color: white;
  margin-bottom: 12px;
  font-size: 14px;
}

.param-label span {
  margin-bottom: 4px;
}

.param-input {
  background: #1a1a1a;
  border: 1px solid #444;
  border-radius: 4px;
  color: white;
  padding: 6px 8px;
  font-size: 14px;
  width: 100%;
}

.param-input:focus {
  outline: none;
  border-color: #667eea;
}

.param-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Pravá část */
#PravaCast {
  grid-column: 2;
  grid-row: 2;
  display: grid;
  grid-template-rows: 1fr 60px 200px;
  gap: 12px;
  padding: 12px;
  background: #0d0d0d;
  overflow: hidden;
  min-width: 0;
}

/* Horní řádek: Graf + Tlačítko/Log - PŮVODNÍ */
#TabulkaLogButton {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 12px;
  min-height: 0;
  overflow: hidden;
  /* ← PŘIDÁNO */
}

#Graf {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #333;
  min-width: 0;
  /* ← PŘIDÁNO: zabrání přetékání */
  overflow: hidden;
  /* ← PŘIDÁNO */
}

canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  /* ← PŘIDÁNO */
  overflow: hidden;
  /* ← PŘIDÁNO */
}

.button-row {
  display: grid;
  grid-template-columns: 1fr 1fr; /* Výchozí: 2 sloupce */
  gap: 12px;
  transition: grid-template-columns 0.3s ease; /* Hladký přechod */
  align-items: stretch;
}

/* Když je jen jedno tlačítko */
.button-row.single-button {
  grid-template-columns: 1fr; /* Jen 1 sloupec */
}

/* Tlačítko evoluce */
#EvoluceButton,
#export-button {
  padding: 15px 20px; 
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  line-height: 1.2;
  text-align: center;
  transition: all 0.2s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px; /* Mezera mezi emoji a textem */
}

#EvoluceButton {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

#export-button {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
}

#EvoluceButton:hover,
#export-button:hover {
  transform: translateY(-2px);
}

#export-button:hover {
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

#EvoluceButton:active,
#export-button:active {
  transform: translateY(0);
}

/* Spinner */
.evolve-spinner {
  grid-column: 1 / -1; /* Vždy přes všechny sloupce */
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 15px;
  gap: 12px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.evolve-spinner p {
  color: white;
  font-weight: 600;
  font-size: 14px;
  margin: 0;
}

.stop-button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
  padding: 8px 16px;
  font-size: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.stop-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Export tlačítko */
#export-button {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  padding: 15px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

#export-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

#export-button:active {
  transform: translateY(0);
}

/* Log evoluce - OPRAVENÝ SCROLL */
#evolog {
  flex: 1;
  background: #1a1a1a;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #333;
  display: flex;
  flex-direction: column;
  min-height: 0;
  /* ← DŮLEŽITÉ pro scroll */
  overflow: hidden;
  /* ← PŘIDÁNO */
}

#evolog h3 {
  color: white;
  font-size: 16px;
  margin-bottom: 8px;
  flex-shrink: 0;
  /* ← PŘIDÁNO: nadpis se nezmenší */
}

.log-content {
  flex: 1;
  overflow-y: auto;
  /* ← SCROLL TADY */
  overflow-x: hidden;
  /* ← Bez horizontálního scrollu */
  color: #aaa;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  min-height: 0;
  /* ← DŮLEŽITÉ */
}

/* Střední řádek: Předpis + Chromozom */
#FunkcniCast {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  height: 60px;
  min-height: 60px;
  max-height: 60px;
}

.info-box {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 10px;
  border: 1px solid #333;
  overflow: hidden;
  display: flex;
  flex-direction: row; 
  align-items: center;
  gap: 8px;
}

.info-box h4 {
  color: white;
  font-size: 13px;
  margin-bottom: 0px;
  flex-shrink: 0;
}

.info-box p {
  color: #aaa;
  font-size: 14px;
  white-space: nowrap;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;  
  padding: 4px 0;
  flex: 1; 
}

.math-formula {
  color: #aaa;
  font-size: 16px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 0;
  scrollbar-width: thin;
  flex: 1;
}

.math-formula::-webkit-scrollbar {
  height: 4px;
}

.math-formula::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 2px;
}

/* Styling scrollbaru pro Chrome/Safari/Edge */
.info-box p::-webkit-scrollbar {
  height: 6px;
}

.info-box p::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 3px;
}

.info-box p::-webkit-scrollbar-thumb {
  background: #444;  /*Šedý jako u math-formula */
  border-radius: 3px;
}

.info-box p::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Dolní řádek: Tabulka */
#TabulkovaCast {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 10px;
  border: 1px solid #333;
  overflow: auto;
  min-height: 0;
  max-height: 200px;
}

#HodnotyTabulka {
  width: 100%;
  border-collapse: collapse;
  color: white;
}

#HodnotyTabulka th {
  background: #2a2a2a;
  padding: 10px;
  text-align: center;
  font-size: 14px;
  position: sticky;
  top: 0;
  z-index: 1;
}

#HodnotyTabulka td {
  padding: 8px;
  text-align: center;
  font-size: 13px;
  border-top: 1px solid #333;
}

#HodnotyTabulka tbody tr:hover {
  background: #252525;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1a1a;
}

::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>