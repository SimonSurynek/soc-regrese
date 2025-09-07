<script setup>
import { ref, computed } from 'vue'

const log = ref("");

const vstupniCisla = ref("");

const COLS = 100;
const chromozom = ref([]); 
const zobrazit = ref(false);


function GenerovaniChromozomu() {
  const chrom = [];

  for (let i = 0; i < COLS; i++) {  
    const PovoleneVstupy = [0];

    for (let x = 0; x < i; x++) {
      PovoleneVstupy.push(x + 1);
    }

    PovoleneVstupy.push(1000);
    PovoleneVstupy.push(1001);

    const in1 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
    const in2 = PovoleneVstupy[Math.floor(Math.random() * PovoleneVstupy.length)];
    const fn = Math.floor(Math.random() * 5);

    chrom.push(in1, in2, fn);
  }

  
  chrom.push(COLS - 1); 

  chromozom.value = chrom; 
  console.log("Generovany chromozom", chrom);
  return chrom;
}


function chrom_evaluate(chrom, valX) {
  var values = [];
  values[0] = valX;
  values[1000] = 0;
  values[1001] = 1;
  console.log("chrom", chrom);

  for (let i = 0; i < COLS; i++) {
    var in1 = chrom[i * 3 + 0];
    var in2 = chrom[i * 3 + 1];
    var fn = chrom[i * 3 + 2];

    in1 = values[in1];
    in2 = values[in2];

    if (fn == 0) {
      values[i + 1] = in1 + in2;
    } else if (fn == 1) {
      values[i + 1] = in1 * in2;  
    } else if (fn == 2) {
      values[i + 1] = in1 - in2;
    } else if (fn == 3) {
      values[i + 1] = (in2 !== 0) ? in1 / in2 : 0; 
    } else if (fn == 4) {
      values[i + 1] = in1 >= 0 ? Math.sqrt(in1) : 0;
    }
    if (isNaN(values[i + 1])) {
      values[i + 1] = 1;
    }

    console.log("Krok", i, "PrvniCislo", in1, "DruheCislo", in2, "FunkceCislo", fn, "Vysledek", values[i + 1]);
  }

  var idout = chrom[COLS * 3]; 
  console.log("values", values, "output", values[idout], "idout", idout);
  return values[idout];
}

const HodnotyY = ref([]);

function PocitaniY() {
  const cisla = vstupniCisla.value
    .split(',')
    .map(Number);

  const Vysledky = cisla.map(x => ({
    x,
    y: chrom_evaluate(chromozom.value, x)
  }));

  HodnotyY.value = Vysledky;
}

const text = ref("ahoj");
const cislo = ref(0);

const mensiCisla = computed(() => {
  const n = cislo.value;
  const vysledek = [50, 45];

  for (let i = 0; i < n; i++) {
    vysledek.push(i);
  }
  return vysledek;
});
function ZobrazHodnotu() {
  zobrazit.value = true;
}

function MutaceChromozomu(chrom) {
  const index = Math.floor(Math.random() * chrom.length);
  const newValue = Math.floor(Math.random() * 100); 
  chrom[index] = newValue;
  console.log(`Mutace na indexu ${index}, nová hodnota: ${newValue}`);
}
</script>

<template>
  <pre>{{ log }}</pre> 

  <div>
    <input type="number" v-model.number="cislo" placeholder="Zadej číslo" />
    <p>Zadané číslo: {{ cislo }} {{  text }}</p>
    <ul>
      <li v-for="n in mensiCisla" :key="n" :class="{ even: n % 2 === 0, odd: n % 2 !== 0 }">cislo {{ n }}</li>
    </ul>
  </div>

  <div>
    <label for="cisla">Zadej čísla oddělená čárkou bez mezer:</label><br />
    <input id="cisla" type="text" v-model="vstupniCisla" /><br />
    <div>f(x) = 2*√x + 2*x</div>
    <button @click="GenerovaniChromozomu">Generuj náhodný chromozom</button>
    <button @click="PocitaniY">Spočítej y pro vybraná čísla</button>
    <button @click="ZobrazHodnotu">Zobraz Chromozom</button>
    <button @click="MutaceChromozomu(chromozom)">Mutuj Chromozom</button>
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
          <td>{{ (hodnota.y).toFixed(2) }}</td>
          <td>{{ (100 / (2 * Math.sqrt(hodnota.x) + 2 * hodnota.x) * hodnota.y).toFixed(2) + "%" }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
#cisla {
  width: 100%;
  height: 30px;
}
button {
  text-align: center;
  margin: 10px;
}
.even {
  background-color: #f0f0f0;
}
.odd {
  background-color: #ae3131;
  color: #fff;
  font-weight: bold;
}
table {
  margin:auto;
}
</style>
