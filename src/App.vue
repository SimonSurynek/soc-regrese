<script setup>
  import { ref, onMounted, nextTick } from 'vue'
  import { Chart } from 'chart.js/auto'

  const log = ref("");
  const EvoluceProbiha = ref(false);
  const zastavitEvoluci = ref(false);
  const predpisFunkce = ref("");
  

  const vstupniCisla = ref("1,2,3,4,5,6,7,8,9,10");

  const COLS = 10;
  const chromozom = ref([]); 
  const zobrazit = ref(false);
  const VelikostChromozomu = 3;
  const lambda = 10;
  const PocetIteraci = 1000;
  const vybranyDataset = ref('LinearniZavislost.csv');
  const nactenaData = ref([]);
  const chartCanvas = ref(null);
  const logEvo = ref([]);
  let chartInstance = null;
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

  // ----- Generování chromozomu -----
  function GenerovaniChromozomu() {
    const chrom = [];

    for (let i = 0; i < COLS; i++) {  
      const PovoleneVstupy = [];

      if (i === 0) {
        const in1 = 0; // valX
        const in2 = [1005,1006,1007,1008,1009,1010,0][Math.floor(Math.random() * 7)];
        const fn = Math.floor(Math.random() * vybraneFunkce.value.length); 
        chrom.push(in1, in2, fn);
        continue;
      }

      for (let x = 0; x < i; x++) {
        PovoleneVstupy.push(x + 1);
      }

      PovoleneVstupy.push(1005,1006,1007,1008,1009,1010);


      const in1 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
      const in2 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
      const fn = Math.floor(Math.random() * vybraneFunkce.value.length); // přidej .value

      chrom.push(in1, in2, fn);
    }

    chrom.push(COLS - 1); 
    chromozom.value = chrom; 
    console.log("Generovany chromozom", chrom);
    return chrom;
  }

  // ----- Vyhodnocení chromozomu -----
  function chrom_evaluate(chrom, valX) {
  const values = [];
  values[0] = valX;
  values[1005] = 0;
  values[1006] = 0.5;
  values[1007] = 1;
  values[1008] = -2;
  values[1009] = 5;
  values[1010] = -0.5;

  for (let i = 0; i < COLS; i++) {
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
    
    switch(operatory[fn]) {
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
    
    values[i+1] = result;
  }

  const idout = chrom[COLS * VelikostChromozomu]; 
  const finalResult = values[idout];
  
  // Ošetři finální výsledek
  return (isNaN(finalResult) || !isFinite(finalResult)) ? 0 : finalResult;
}

  // ----- Zobrazování chromozomu -----
  function ZobrazHodnotu() {
    zobrazit.value = true;
  }

  const HodnotyY = ref([]);

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
    const index = Math.floor(Math.random() * (chrom.length - 1)); // poslední prvek (output) nemutuje
    if (index === 0) return;

    if (index % VelikostChromozomu === 2) {
      chrom[index] = Math.floor(Math.random() * vybraneFunkce.value.length);
    } else {
      const PovolenaCisla = [];
      for (let x = 1; x <= Math.floor(index / VelikostChromozomu); x++) {
        PovolenaCisla.push(x);
      }
      PovolenaCisla.push(1005, 1006, 1007, 1008, 1009, 1010);
      chrom[index] = PovolenaCisla[Math.floor(Math.random() * PovolenaCisla.length)];
    }
  }

  // ----- Fitness funkce -----
 function VypocitejFitness(chrom) {
  if (nactenaData.value.length === 0) return -Infinity;
  
  let mse = 0;
  let invalidCount = 0;
  
  for (let i = 0; i < nactenaData.value.length; i++) {
    const { x, y: spravneY } = nactenaData.value[i];
    const predikovaneY = chrom_evaluate(chrom, x);
    
    // Počítej neplatné hodnoty
    if (isNaN(predikovaneY) || !isFinite(predikovaneY)) {
      invalidCount++;
      mse += 1000; // Velká penalizace
    } else {
      const chyba = predikovaneY - spravneY;
      mse += Math.pow(chyba, 2);
    }
  }
  
  // Pokud má chromozom příliš mnoho neplatných hodnot, silně penalizuj
  if (invalidCount > nactenaData.value.length * 0.5) {
    return -Infinity;
  }
  
  mse /= nactenaData.value.length;
  
  // Penalizace pro funkce bez variability
  const predY = nactenaData.value.map(item => chrom_evaluate(chrom, item.x));
  const validPredY = predY.filter(y => isFinite(y) && !isNaN(y));
  
  if (validPredY.length < 2) {
    return -Infinity;
  }
  
  const mean = validPredY.reduce((sum, y) => sum + y, 0) / validPredY.length;
  const variance = validPredY.reduce((sum, y) => sum + Math.pow(y - mean, 2), 0) / validPredY.length;
  
  if (variance < 0.0001) {
    return -Infinity;
  }
  
  // Penalizace pro funkce bez použití X
  const pouziteVstupy = chrom.some(v => v === 0);
  if (!pouziteVstupy) {
    return -Infinity;
  }
  
  return -mse;
}

  // ----- Evoluční algoritmus -----
  async function EvolucniAlgoritmus() {
  if (vybraneFunkce.value.length === 0) {
    alert("Vyber alespoň jednu povolenou funkci!");
    return;
  }
  

  EvoluceProbiha.value = true;
  zastavitEvoluci.value = false;
  logEvo.value = [];
  let parent = GenerovaniChromozomu();
  let bestFitness = VypocitejFitness(parent);
  let bestOffspring = [...parent];
  let bestOffspringFitness = bestFitness;

  for (let g = 0; g < PocetIteraci; g++) {
    if (zastavitEvoluci.value) {
      logEvo.value.push(`Evoluce byla zastavena uživatelem na generaci ${g}.`);
      EvoluceProbiha.value = false;
      break;
    }
    for (let i = 0; i < lambda; i++){
      let offspring = [...parent];
      MutaceChromozomu(offspring);
      let offspringFitness = VypocitejFitness(offspring);
      if (offspringFitness > bestOffspringFitness){
        bestOffspring = [...offspring];
        bestOffspringFitness = offspringFitness;
      }
    }

    parent = [...bestOffspring];
    bestFitness = bestOffspringFitness;
    console.log(`Generace ${g}: bestFitness = ${bestFitness}`);

    if (g % 5 === 0) {
      chromozom.value = [...bestOffspring];
      updateChart(true);
      await new Promise(resolve => setTimeout(resolve, 0));
    }

    if(-bestFitness < 0.01) {
      logEvo.value.push(`Dosaženo cílové fitness, Generace ${g}.`);
      break;
    }

    if(g % 10 === 0) {
      logEvo.value.push(`Generace ${g}: bestFitness = ${bestFitness.toFixed(6)}`);
      scrollLogToBottom();
    }
  }
  
  chromozom.value = [...bestOffspring];
  predpisFunkce.value = FunkcniPredpis(chromozom.value[chromozom.value.length - 1]);
  ZobrazHodnotu();
  PocitaniY();
  
  await nextTick();
  updateChart(true);
  EvoluceProbiha.value = false;
}


  // upravené updateChart: parametr showModel - pokud false, vykreslí jen scatter
  function updateChart(showModel = true) {
    if (!chartCanvas.value || nactenaData.value.length === 0) return;
    
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

    // přidat červenou křivku jen když showModel === true a chromozom existuje
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
  function scrollLogToBottom() {
  nextTick(() => {
    const logElement = document.querySelector('.log-content');
    if (logElement) {
      logElement.scrollTop = logElement.scrollHeight;
    }
  });
}
function ZastavitEvoluci() {
  zastavitEvoluci.value = true;
}
// -----Hledání funkčního předpisu podle chromozomu-----
function FunkcniPredpis(index) {
  //Vstup X
  if (index === 0) return "x";
  //Konstanty
  if (index === 1005) return "0";
  if (index === 1006) return "0.5";
  if (index === 1007) return "1";
  if (index === 1008) return "(-2)";
  if (index === 1009) return "5";
  if (index === 1010) return "(-0.5)";

  const in1Index = chromozom.value[(index-1) * VelikostChromozomu + 0];
  const in2Index = chromozom.value[(index-1) * VelikostChromozomu + 1];
  const fnIndex = chromozom.value[(index-1) * VelikostChromozomu + 2];

  const in1 = FunkcniPredpis(in1Index);
  const in2 = FunkcniPredpis(in2Index);
  const operatory = vybraneFunkce.value;
  let VyslednyPredpis = "";
  switch(operatory[fnIndex]) {
    case "plus": VyslednyPredpis = `(${in1} + ${in2})`; break;
    case "krat": VyslednyPredpis = `(${in1} * ${in2})`; break;
    case "minus": VyslednyPredpis = `(${in1} - ${in2})`; break;
    case "deleno": VyslednyPredpis = `(${in1} / ${in2})`; break;
   case "sqrt": VyslednyPredpis = `sqrt(${in1})`; break;
    case "sin": VyslednyPredpis = `sin(${in1})`; break;              
    case "log": VyslednyPredpis = `log(${in1})`; break;
    default: VyslednyPredpis = in1; break;
}
return VyslednyPredpis;
}
  nactiDataset();
  </script>

  <template>
    <div id="container">
      <header id="header">
        <h1>Symbolická regrese s využitím AI</h1>
      </header>

      <aside id="LevaCast">
        <div id="VyberDatasetu">
          <h3>Výběr datasetu:</h3>
          <label>
            <input type="radio" v-model="vybranyDataset" value="LinearniZavislost.csv" @change="nactiDataset">
            Lineární
          </label>
          <label>
            <input type="radio" v-model="vybranyDataset" value="KvadratickaZavislost.csv" @change="nactiDataset">
            Kvadratická
          </label>
          <label>
            <input type="radio" v-model="vybranyDataset" value="SinusovaZavislost.csv" @change="nactiDataset">
            Sinusová
          </label>
          <label>
            <input type="radio" v-model="vybranyDataset" value="LogaritmickaZavislost.csv" @change="nactiDataset">
            Logaritmická
          </label>
          <label>
            <input type="radio" v-model="vybranyDataset" value="KomplexniDataset.csv" @change="nactiDataset">
            Komplexni
          </label>
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
            <button v-if="!EvoluceProbiha" id="EvoluceButton" @click="EvolucniAlgoritmus">Spusť evoluci</button>
            <div v-else class="evolve-spinner">
              <div class="spinner"></div>
              <p>Evoluce běží...</p>
              <button @click="ZastavitEvoluci" class="stop-button">Zastavit</button>
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
            <p>f(x) = {{ predpisFunkce }}</p>
          </div>
          
          <div class="info-box" v-if="zobrazit">
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
                <th>Odchylka</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="hodnota in HodnotyY" :key="hodnota.x">
                <td>{{ hodnota.x.toFixed(3) }}</td> 
                <td>{{ hodnota.ySpravne?.toFixed(3) ?? 'N/A' }}</td>
                <td>{{ hodnota.yVypoctene?.toFixed(3) ?? 'N/A' }}</td>
                <td>{{ hodnota.ySpravne ? ((hodnota.yVypoctene / hodnota.ySpravne - 1) * 100).toFixed(3 ) + '%' : 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  </template>
  <style>
   /*Globální reset - aplikuje se na celou stránku 
  html, body, #app {
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden;
    
  }*/
</style>

  <style scoped>

  /* Reset */
  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root, html, body, #app {
    height: 100%;
    width: 100%;
    overflow: hidden;
  }

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

  #VyberDatasetu, .funkce-panel {
    background: #2a2a2a;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #444;
  }

  #VyberDatasetu h3, .funkce-panel h3 {
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
    overflow: hidden; /* ← PŘIDÁNO */
  }

  #Graf {
    background: #1a1a1a;
    border-radius: 8px;
    padding: 12px;
    border: 1px solid #333;
    min-width: 0; /* ← PŘIDÁNO: zabrání přetékání */
    overflow: hidden; /* ← PŘIDÁNO */
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
    min-height: 0; /* ← PŘIDÁNO */
    overflow: hidden; /* ← PŘIDÁNO */
  }

  #EvoluceButton {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 15px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: transform 0.2s;
    flex-shrink: 0; /* ← PŘIDÁNO: tlačítko se nezmenší */
  }

  #EvoluceButton:hover {
    transform: translateY(-2px);
  }
  /* Evolve spinner */
  .evolve-spinner {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px;
    padding: 15px;
    flex-shrink: 0;
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

  /* Log evoluce - OPRAVENÝ SCROLL */
  #evolog {
    flex: 1;
    background: #1a1a1a;
    border-radius: 8px;
    padding: 12px;
    border: 1px solid #333;
    display: flex;
    flex-direction: column;
    min-height: 0; /* ← DŮLEŽITÉ pro scroll */
    overflow: hidden; /* ← PŘIDÁNO */
  }

  #evolog h3 {
    color: white;
    font-size: 16px;
    margin-bottom: 8px;
    flex-shrink: 0; /* ← PŘIDÁNO: nadpis se nezmenší */
  }

  .log-content {
    flex: 1;
    overflow-y: auto; /* ← SCROLL TADY */
    overflow-x: hidden; /* ← Bez horizontálního scrollu */
    color: #aaa;
    font-size: 13px;
    font-family: 'Courier New', monospace;
    min-height: 0; /* ← DŮLEŽITÉ */
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
    flex-direction: column;
  }

  .info-box h4 {
    color: white;
    font-size: 13px;
    margin-bottom: 4px;
    flex-shrink: 0;
  }

  .info-box p {
    color: #aaa;
    font-size: 12px;
    white-space: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: none; /* ← Firefox */
    -ms-overflow-style: none; /* ← IE/Edge */
  }

  /* Schová scrollbar v Chrome/Safari */
  .info-box p::-webkit-scrollbar {
    display: none;
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