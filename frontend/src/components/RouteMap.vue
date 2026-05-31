<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Фикс известного бага: дефолтные иконки маркеров не находятся при сборке бандлером
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const props = defineProps({
  origin: { type: Object, required: true },       // {lat, lon, display_name}
  destination: { type: Object, required: true },
  geometry: { type: Object, default: null },      // GeoJSON LineString
  height: { type: String, default: '320px' },
})

const mapRef = ref(null)
let map = null
let routeLayer = null

function init() {
  if (map) return
  map = L.map(mapRef.value, { scrollWheelZoom: false })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 18,
  }).addTo(map)
  render()
}

function render() {
  if (!map) return
  if (routeLayer) {
    map.removeLayer(routeLayer)
    routeLayer = null
  }

  const layers = []

  // Маркеры точек отправления и назначения
  const originMarker = L.marker([props.origin.lat, props.origin.lon])
    .bindPopup(`<b>Откуда</b><br>${props.origin.display_name || ''}`)
  const destMarker = L.marker([props.destination.lat, props.destination.lon])
    .bindPopup(`<b>Куда</b><br>${props.destination.display_name || ''}`)
  layers.push(originMarker, destMarker)

  // Линия маршрута, если есть
  if (props.geometry) {
    const routeLine = L.geoJSON(props.geometry, {
      style: { color: '#3B82F6', weight: 4, opacity: 0.85 },
    })
    layers.push(routeLine)
  }

  routeLayer = L.featureGroup(layers).addTo(map)
  map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] })
}

onMounted(init)
watch(() => [props.origin, props.destination, props.geometry], render, { deep: true })

onUnmounted(() => {
  if (map) { map.remove(); map = null }
})
</script>

<template>
  <div
    ref="mapRef"
    :style="{ height, width: '100%' }"
    class="rounded-xl overflow-hidden border border-surface-200 dark:border-surface-800 z-0"
  />
</template>

<style>
/* Leaflet вешает свои стили на body — корректируем z-index, чтобы не вылезали поверх dropdown-ов PrimeVue */
.leaflet-container { z-index: 0; }
.leaflet-popup { z-index: 1; }
</style>