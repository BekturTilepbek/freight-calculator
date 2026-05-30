<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressSpinner from 'primevue/progressspinner'

const loading = ref(true)
const stats = ref([])
const recentOrders = ref([])

const statusMap = {
  in_transit: { label: 'В пути',     severity: 'info' },
  delivered:  { label: 'Доставлено', severity: 'success' },
  assigned:   { label: 'Назначен',   severity: 'warn' },
  draft:      { label: 'Черновик',   severity: 'secondary' },
  cancelled:  { label: 'Отменен',    severity: 'danger' },
}

const colorMap = {
  primary: 'bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400',
  green:   'bg-green-50   dark:bg-green-950   text-green-600   dark:text-green-400',
  blue:    'bg-blue-50    dark:bg-blue-950    text-blue-600    dark:text-blue-400',
  orange:  'bg-orange-50  dark:bg-orange-950  text-orange-600  dark:text-orange-400',
}

function fmtMoney(v) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency', currency: 'USD', maximumFractionDigits: 0,
  }).format(Number(v))
}

function fmtNumber(v) {
  return new Intl.NumberFormat('en-US').format(Number(v))
}

async function load() {
  loading.value = true
  try {
    const [{ data: s }, { data: orders }] = await Promise.all([
      axios.get('/api/v1/orders/stats'),
      axios.get('/api/v1/orders', { params: { limit: 5 } }),
    ])
    stats.value = [
      { label: 'Активные рейсы',  value: fmtNumber(s.active_orders),       icon: 'pi pi-truck',      color: 'primary' },
      { label: 'Всего заявок',    value: fmtNumber(s.total_orders),        icon: 'pi pi-list',       color: 'blue' },
      { label: 'Общая выручка',   value: fmtMoney(s.total_revenue),        icon: 'pi pi-dollar',     color: 'green' },
      { label: 'Пробег (мили)',   value: fmtNumber(s.total_distance_miles),icon: 'pi pi-map-marker', color: 'orange' },
    ]
    recentOrders.value = orders
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div v-if="loading" class="flex justify-center py-20">
      <ProgressSpinner />
    </div>

    <template v-else>
      <!-- Stats grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="s in stats"
          :key="s.label"
          class="p-5 rounded-2xl bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-800"
        >
          <div :class="['w-11 h-11 rounded-xl flex items-center justify-center mb-3', colorMap[s.color]]">
            <i :class="[s.icon, 'text-xl']" />
          </div>
          <div class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1">{{ s.value }}</div>
          <div class="text-sm text-surface-500">{{ s.label }}</div>
        </div>
      </div>

      <!-- Recent orders -->
      <Card>
        <template #title>
          <span class="text-lg font-semibold">Последние заявки</span>
        </template>
        <template #content>
          <DataTable :value="recentOrders" stripedRows :pt="{ table: { class: 'text-sm' } }">
            <Column field="order_number" header="№ заявки">
              <template #body="{ data }">
                <span class="font-mono font-medium text-primary-600 dark:text-primary-400">
                  {{ data.order_number }}
                </span>
              </template>
            </Column>
            <Column header="Маршрут">
              <template #body="{ data }">
                {{ data.origin_address }} → {{ data.destination_address }}
              </template>
            </Column>
            <Column field="distance_miles" header="Мили">
              <template #body="{ data }">{{ fmtNumber(data.distance_miles) }}</template>
            </Column>
            <Column header="Выручка">
              <template #body="{ data }">
                <span class="font-semibold">
                  {{ fmtMoney(data.distance_miles * data.rate_per_mile) }}
                </span>
              </template>
            </Column>
            <Column field="status" header="Статус">
              <template #body="{ data }">
                <Tag
                  :value="statusMap[data.status]?.label || data.status"
                  :severity="statusMap[data.status]?.severity || 'secondary'"
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </template>
  </div>
</template>