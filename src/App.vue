<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Chart } from 'chart.js/auto'

const log = ref("");

const vstupniCisla = ref("1,2,3,4,5,6,7,8,9,10");

const COLS = 10;
const chromozom = ref([]); 
const zobrazit = ref(false);
const VelikostChromozomu = 3;
const PocetFci = 7;
const lambda = 50;
const vybranyDataset = ref('LinearniZavislost.csv');
const nactenaData = ref([]);
const chartCanvas = ref(null);
let chartInstance = null;

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
      const in2 = [1005,1006,1007,1008,1009,1010][Math.floor(Math.random() * 6)];
      const fn = Math.floor(Math.random() * PocetFci);
      chrom.push(in1, in2, fn);
      continue;
    }

    for (let x = 0; x < i; x++) {
      PovoleneVstupy.push(x + 1);
    }

    PovoleneVstupy.push(1005,1006,1007,1008,1009,1010);


    const in1 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
    const in2 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
    const fn = Math.floor(Math.random() * PocetFci);

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
 /* values[1000] = -10;
  values[1001] = -5;
  values[1002] = -2;
  values[1003] = -1;
  values[1004] = -0.5;
  */
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

    switch(fn) {
      case 0: values[i+1] = in1 + in2; break;
      case 1: values[i+1] = in1 * in2; break;
      case 2: values[i+1] = in1 - in2; break;
      case 3: values[i+1] = (in2 !== 0) ? in1 / in2 : 1; break;
      case 4: values[i+1] = in1 >= 0 ? Math.sqrt(in1) : 1; break;
      case 5: values[i+1] = Math.sin(in1); break;              
      case 6: values[i+1] = in1 > 0 ? Math.log(in1) : 0; break;
    }

    if (isNaN(values[i+1])) values[i+1] = 1;
  }

  const idout = chrom[COLS * VelikostChromozomu]; 
  return values[idout];
}

// ----- Zobrazování chromozomu -----
function ZobrazHodnotu() {
  zobrazit.value = true;
}

const HodnotyY = ref([]);

// ----- Výpočet Y podle chromozomu -----
function PocitaniY() {
  if (nactenaData.value.length === 0) return;
  
  HodnotyY.value = nactenaData.value.map(item => ({
    x: item.x,
    ySpravne: item.y,
    yVypoctene: chrom_evaluate(chromozom.value, item.x)
  }));
}

// ----- Mutace chromozomu -----
function MutaceChromozomu(chrom) {
  const index = Math.floor(Math.random() * (chrom.length - 1)); // poslední prvek (output) nemutuje
  if (index === 0) return;

  if (index % VelikostChromozomu === 2) {
    chrom[index] = Math.floor(Math.random() * PocetFci);
  } else {
    const PovolenaCisla = [];
    for (let x = 1; x <= Math.floor(index / VelikostChromozomu); x++) {
      PovolenaCisla.push(x);
    }
    PovolenaCisla.push(1001, 1002, 1003, 1004, 1005);
    chrom[index] = PovolenaCisla[Math.floor(Math.random() * PovolenaCisla.length)];
  }
}

// ----- Fitness funkce -----
function VypocitejFitness(chrom) {
  if (nactenaData.value.length === 0) return 0;
  
  let mse = 0;
  for (let i = 0; i < nactenaData.value.length; i++) {
    const { x, y: spravneY } = nactenaData.value[i];
    const predikovaneY = chrom_evaluate(chrom, x); //Vyzkouset jestli se predY rovnaji jestlinjo tak dat oenalizaci
    const chyba = predikovaneY - spravneY;
    mse += Math.pow(chyba, 2);
  }
  mse /= nactenaData.value.length; 
  //Penalizace cistych konstant
  const pouziteVstupy = chrom.some(v => v === 0);
  if (!pouziteVstupy) mse = Infinity; // 50 % trest
  return -mse;

}

// ----- Evoluční algoritmus -----
function EvolucniAlgoritmus() {
  let parent = GenerovaniChromozomu();
  let bestFitness = VypocitejFitness(parent);
  let bestOffspring = [...parent];
  let bestOffspringFitness = bestFitness;

  for (let g = 0; g < 1000; g++) {
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
  }

  chromozom.value = [...bestOffspring];
  ZobrazHodnotu();
  PocitaniY();
  
}

function updateChart() {
  if (!chartCanvas.value || nactenaData.value.length === 0) return;
  
  // Zničit starý graf, pokud existuje
  if (chartInstance) {
    chartInstance.destroy();
  }
  
  // Data z excelu (modré body)
  const scatterData = nactenaData.value.map(item => ({
    x: item.x,
    y: item.y
  }));
  
  // Vypočtená data z naučené funkce (červená křivka)
  const lineData = nactenaData.value.map(item => ({
    x: item.x,
    y: chrom_evaluate(chromozom.value, item.x)
  }));
  
  // Vytvoř nový graf
  chartInstance = new Chart(chartCanvas.value, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'Správná data (CSV)',
          data: scatterData,
          backgroundColor: 'rgba(54, 162, 235, 0.8)',
          borderColor: 'rgba(54, 162, 235, 1)',
          pointRadius: 6,
          type: 'scatter'
        },
        {
          label: 'Naučená funkce',
          data: lineData,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 2,
          pointRadius: 0,
          type: 'line',
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Symbolická regrese - Porovnání',
          font: { size: 18 }
        },
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'x'
          }
        },
        y: {
          title: {
            display: true,
            text: 'y'
          }
        }
      }
    }
  });
}

nactiDataset();
</script>

<template>

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
</div>

    <div style="width: 80%; max-width: 800px; height: 500px; margin: 40px auto;">
      <canvas ref="chartCanvas"></canvas>
    </div>
  

    <label for="cisla">Zadej čísla oddělená čárkou bez mezer:</label><br />
    <input id="cisla" type="text" v-model="vstupniCisla" /><br />
    <div>f(x) = 2*√x + 2*x</div>

    <button @click="GenerovaniChromozomu">Generuj náhodný chromozom</button>
    <button @click="PocitaniY">Spočítej y pro vybraná čísla</button>
    <button @click="ZobrazHodnotu">Zobraz Chromozom</button>
    <button @click="MutaceChromozomu(chromozom.value); PocitaniY();">Mutuj Chromozom</button>
    <button @click="EvolucniAlgoritmus">Spusť evoluci</button>

    <p v-if="zobrazit"> Chromozom: {{ chromozom }}</p>

    <table border="1" cellspacing="0" cellpadding="5">
      <thead>
        <tr>
          <th>x</th>
          <th>Očekávaná hodnota y podle f(x)</th>
          <th>Vypočítaná hodnota y</th>
          <th>Odchylka v procentech</th>
        </tr>
      </thead>
     <tbody>
        <tr v-for="hodnota in HodnotyY" :key="hodnota.x">
          <td>{{ hodnota.x }}</td> 
          <td>{{ hodnota.ySpravne?.toFixed(2) ?? 'N/A' }}</td>
          <td>{{ hodnota.yVypoctene?.toFixed(2) ?? 'N/A' }}</td>
          <td>{{ hodnota.ySpravne ? ((hodnota.yVypoctene / hodnota.ySpravne - 1) * 100).toFixed(2) + '%' : 'N/A' }}</td>
        </tr>
      </tbody>
    </table>
  
</template>

<style scoped>
#cisla { width: 100%; height: 30px; }
button { text-align: center; margin: 10px; }
table { margin:auto; }

#VyberDatasetu {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(50, 50, 50, 0.9);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(255,255,255,0.1);
}

#VyberDatasetu h3 {
  margin-bottom: 15px;
  font-size: 18px;
  color: white;
}

#VyberDatasetu label {
  display: block;
  margin-bottom: 10px;
  cursor: pointer;
  font-size: 16px;
  color: white;
}

#VyberDatasetu input[type="radio"] {
  margin-right: 8px;
  cursor: pointer;
}
</style>