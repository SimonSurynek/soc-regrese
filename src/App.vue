<script setup>
import { ref } from 'vue'

const log = ref("");

const vstupniCisla = ref("1,2,3,4,5,6,7,8,9,10");

const COLS = 10;
const chromozom = ref([]); 
const zobrazit = ref(false);
const VelikostChromozomu = 3;
const PocetFci = 7;
const lambda = 50;

// ----- Generování chromozomu -----
function GenerovaniChromozomu() {
  const chrom = [];

  for (let i = 0; i < COLS; i++) {  
    const PovoleneVstupy = [];

    if (i === 0) {
      const in1 = 0; // valX
      const in2 = [1000, 1001, 1002, 1003, 1004, 1005][Math.floor(Math.random() * 6)];
      const fn = Math.floor(Math.random() * PocetFci);
      chrom.push(in1, in2, fn);
      continue;
    }

    for (let x = 0; x < i; x++) {
      PovoleneVstupy.push(x + 1);
    }

    PovoleneVstupy.push(1000, 1001, 1002, 1003, 1004, 1005);

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
  values[0] = valX;
  values[1000] = 0;
  values[1001] = 1;
  values[1002] = 0.5;
  values[1003] = 2;
  values[1004] = 5;
  values[1005] = 10;

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
  const cisla = vstupniCisla.value.split(',').map(Number);

  HodnotyY.value = cisla.map(x => ({
    x,
    y: chrom_evaluate(chromozom.value, x)
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
  const cisla = vstupniCisla.value.split(',').map(Number);
  let mse = 0;
  for (let x=0; x<cisla.length; x++){
    const predikovaneY = chrom_evaluate(chrom, cisla[x]);
    const spravneY = 2 * Math.sqrt(cisla[x]) + 2 * cisla[x];
    const chyba = predikovaneY - spravneY;
    mse += Math.pow(chyba, 2);
  }
  mse /= cisla.length;
  return 1 / (1 + mse);
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

</script>

<template>
  <div>
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
          <td>{{ (2 * Math.sqrt(hodnota.x) + 2 * hodnota.x).toFixed(2) }}</td>
          <td>{{ hodnota.y.toFixed(2) }}</td>
          <td>{{ (100 / (2 * Math.sqrt(hodnota.x) + 2 * hodnota.x) * hodnota.y - 100).toFixed(2)  + "%" }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
#cisla { width: 100%; height: 30px; }
button { text-align: center; margin: 10px; }
table { margin:auto; }
</style>
