<script setup>
import { ref, computed } from 'vue'

const log = ref("");

const vstupniCisla = ref("");

const COLS = 5;

function chrom_evaluate(chrom, valX) {
  var values = [];
  values[0] = valX;
  values[100] = 1;
  values[101] = 0;
  console.log("chrom", chrom);

  /* todo prepsat na cyklus pres N prvku a podle defunice funkci 0: +, 1: *, 2: -, ...
  values[1] = Math.sqrt(values[0]);
  values[2] = values[0] * values[1];
  values[3] = values[0] * values[1];
  values[4] = values[2] + values[100];
  values[5] = Math.sqrt(values[0]);
  */

  for (let i = 0; i < COLS; i++) {
    var in1 = chrom[i * 3 + 0];
    var in2 = chrom[i * 3 + 1];
    var fn = chrom[i * 3 + 2];

  if (in1 == 0) {
      in1 = valX;
    } else if (in1 == 100) {
      in1 = 1;
    } else if (in1 == 101) {
      in1 = 0;
    } else {
      in1 = values[in1];
    }

    if (in2 == 0) {
      in2 = valX;
    } else if (in2 == 100) {
      in2 = 1;
    } else if (in2 == 101) {
      in2 = 0;
    } else {
      in2 = values[in2];
    }

    if (fn == 0) {
      values[i + 1] = in1 + in2;
    } else if (fn == 1) {
      values[i + 1] = in1 * in2;
    } else if (fn == 2) {
      values[i + 1] = in1 - in2;
    } else if (fn == 3) {
      values[i + 1] = (in2 !== 0) ? in1 / in2 : 0; 
    } else if (fn == 4) {
      values[i + 1] = Math.sqrt(in1); 
    }

    console.log("Krok", i, "PrvniCislo", in1, "DuheCislo", in2, "FunkceCislo", fn, "Vysledek", values[i + 1]);
  }

  var idout = chrom[COLS * 3]; 
  console.log("values", values, "output", values[idout], "idout", idout);
  return values[idout];
}


const HodnotyY = ref([]);

function PocitaniY() {
  const cisla = vstupniCisla.value
  .split(',')
  .map(Number)
  const Vysledky = cisla.map(x => ({
    x,
    y: chrom_evaluate([0, 0, 4, 0, 1, 1, 0, 1, 1, 2, 100, 0, 0, 3, 4, 4], x)
  }));

  HodnotyY.value = Vysledky;
}


const text = ref("ahoj");
//const log = ref("");
const cislo = ref(0);

const mensiCisla = computed(() => {
  const n = cislo.value;
  const vysledek = [50, 45];

  for (let i = 0; i < n; i++) {
    vysledek.push(i);
  }
  return vysledek;
});
</script>

<template>
  <!-- <div>{{ text }}</div>
  <input type="text">
  <button @click="funkce">OK</button> -->
  <pre>
    {{ log }}
    </pre> 
  <div>
    <input type="number" v-model.number="cislo" placeholder="Zadej číslo" />
    <p>Zadané číslo: {{ cislo }} {{  text }}</p>
    <ul>
      <li v-for="n in mensiCisla" :key="n" :class="{ even: n % 2 === 0, odd: n % 2 !== 0 }">cislo {{ n }}</li>
    </ul>

   
  </div>
  <div>
  <label for="cisla">Zadej čísla oddělená čárkou bez mezer:</label><br />
  <input
    id="cisla"
    type="text"
    v-model="vstupniCisla"
    
  />
  <br>
  <div>f(x) = 2*√x+2*x</div>
  <button @click="PocitaniY">Spočítej y pro vybraná čísla</button>

  <table border="1" cellspacing="0" cellpadding="5">
    <thead>
      <tr>
        <th>x</th>
        <th>Oekavana hodnota y podle f(x)</th>
        <th>Vypocitana hodnota y</th>
        <th>Odchylka v procentech</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="hodnota in HodnotyY" :key="hodnota.x">
        <td>{{ hodnota.x }}</td> 
        <td>{{(2 * Math.sqrt(hodnota.x) + 2 * hodnota.x).toFixed(2) }}</td>
        <td>{{(hodnota.y).toFixed(2) }}</td>
        <td>{{(100 / (2 * Math.sqrt(hodnota.x) + 2 * hodnota.x) * hodnota.y).toFixed(2) + "%" }}</td>
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
#VypocitaneHodnoty {
  text-align: left;
  padding: 0;
}

.odd {
  background-color: #ae3131;
  color: #fff;
  font-weight: bold;
}
</style>