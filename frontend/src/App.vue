<script setup>
import { ref } from 'vue'
import axios from 'axios'

const form = ref({
  distance_miles: 1000,
  rate_per_mile: 1.5,
  fuel_consumption_mpg: 6.5,
  fuel_price_per_gallon: 3.80,
})

const result = ref(null)
const loading = ref(false)
const error = ref(null)

async function calculate() {
  loading.value = true
  error.value = null
  try {
    const { data } = await axios.post('/api/v1/calculations/estimate', form.value)
    result.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width: 600px; margin: 40px auto; font-family: sans-serif;">
    <h1>Freight Calculator — sanity check</h1>

    <div style="display: grid; gap: 8px;">
      <label>Distance (miles): <input v-model.number="form.distance_miles" type="number" /></label>
      <label>Rate per mile ($): <input v-model.number="form.rate_per_mile" type="number" step="0.01" /></label>
      <label>Fuel MPG: <input v-model.number="form.fuel_consumption_mpg" type="number" step="0.1" /></label>
      <label>Fuel price ($/gal): <input v-model.number="form.fuel_price_per_gallon" type="number" step="0.01" /></label>
      <button @click="calculate" :disabled="loading">
        {{ loading ? 'Calculating…' : 'Calculate' }}
      </button>
    </div>

    <pre v-if="result" style="background: #f4f4f4; padding: 12px; margin-top: 20px;">{{ result }}</pre>
    <p v-if="error" style="color: red;">{{ error }}</p>
  </div>
</template>