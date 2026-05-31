<script setup>
import { ref, computed, onMounted } from 'vue'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Chart from 'primevue/chart'
import ProgressSpinner from 'primevue/progressspinner'

import { ordersApi } from '@/api/orders'
import { fmtMoney, fmtMoneyShort, fmtNumber, STATUS_MAP } from '@/composables/useFormatters'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()

const loading = ref(true)
const stats = ref([])
const recentOrders = ref([])
const analytics = ref(null)

const colorMap = {
  primary: 'bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400',
  green:   'bg-green-50   dark:bg-green-950   text-green-600   dark:text-green-400',
  blue:    'bg-blue-50    dark:bg-blue-950    text-blue-600    dark:text-blue-400',
  orange:  'bg-orange-50  dark:bg-orange-950  text-orange-600  dark:text-orange-400',
}

async function load() {
  loading.value = true
  try {
    const [s, orders, a] = await Promise.all([
      ordersApi.stats(),
      ordersApi.list({ limit: 5 }),
      ordersApi.analytics(),
    ])
    stats.value = [
      { label: 'Активные рейсы',  value: fmtNumber(s.active_orders),        icon: 'pi pi-truck',      color: 'primary' },
      { label: 'Всего заявок',    value: fmtNumber(s.total_orders),         icon: 'pi pi-list',       color: 'blue' },
      { label: 'Общая выручка',   value: fmtMoneyShort(s.total_revenue),    icon: 'pi pi-dollar',     color: 'green' },
      { label: 'Пробег (мили)',   value: fmtNumber(s.total_distance_miles), icon: 'pi pi-map-marker', color: 'orange' },
    ]
    recentOrders.value = orders
    analytics.value = a
  } finally {
    loading.value = false
  }
}

// === ГРАФИК 1: выручка по месяцам ===
const revenueChartData = computed(() => {
  if (!analytics.value?.monthly) return null
  const months = analytics.value.monthly
  const labels = months.map(m => {
    const [year, month] = m.month.split('-')
    const monthNames = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
                        'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    return `${monthNames[parseInt(month) - 1]} ${year.slice(2)}`
  })
  return {
    labels,
    datasets: [
      {
        label: 'Выручка',
        data: months.map(m => Math.round(m.revenue)),
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#3B82F6',
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  }
})

const revenueChartOptions = computed(() => {
  const textColor = isDark.value ? '#cbd5e1' : '#475569'
  const gridColor = isDark.value ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'
  return {
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => `Выручка: $${ctx.parsed.y.toLocaleString()}`,
        },
      },
    },
    scales: {
      x: { ticks: { color: textColor }, grid: { color: gridColor } },
      y: {
        ticks: {
          color: textColor,
          callback: (v) => '$' + (v / 1000).toFixed(0) + 'k',
        },
        grid: { color: gridColor },
        beginAtZero: true,
      },
    },
  }
})

// === ГРАФИК 2: статусы заявок (donut) ===
const statusChartData = computed(() => {
  if (!analytics.value?.status_counts) return null
  const counts = analytics.value.status_counts
  const order = ['delivered', 'in_transit', 'assigned', 'draft', 'cancelled']
  const colors = {
    delivered:  '#10B981',
    in_transit: '#3B82F6',
    assigned:   '#F59E0B',
    draft:      '#94A3B8',
    cancelled:  '#EF4444',
  }
  const present = order.filter(s => counts[s])
  return {
    labels: present.map(s => STATUS_MAP[s]?.label || s),
    datasets: [{
      data: present.map(s => counts[s]),
      backgroundColor: present.map(s => colors[s]),
      borderWidth: 0,
    }],
  }
})

const statusChartOptions = computed(() => {
  const textColor = isDark.value ? '#cbd5e1' : '#475569'
  return {
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'right',
        labels: { color: textColor, padding: 12, font: { size: 12 } },
      },
    },
  }
})

// === ГРАФИК 3: топ маршрутов (горизонтальный bar) ===
const topRoutesChartData = computed(() => {
  if (!analytics.value?.top_routes) return null
  const routes = analytics.value.top_routes
  return {
    labels: routes.map(r => r.route),
    datasets: [{
      label: 'Кол-во рейсов',
      data: routes.map(r => r.count),
      backgroundColor: 'rgba(59, 130, 246, 0.7)',
      borderRadius: 6,
    }],
  }
})

const topRoutesChartOptions = computed(() => {
  const textColor = isDark.value ? '#cbd5e1' : '#475569'
  const gridColor = isDark.value ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'
  return {
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: { legend: { display: false } },
    scales: {
      x: {
        ticks: { color: textColor, stepSize: 1 },
        grid: { color: gridColor },
        beginAtZero: true,
      },
      y: {
        ticks: { color: textColor, font: { size: 11 } },
        grid: { display: false },
      },
    },
  }
})

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

      <!-- Charts row: revenue + status -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Revenue chart -->
        <Card class="lg:col-span-2">
          <template #title>
            <div class="flex items-center justify-between">
              <span class="text-lg font-semibold">Выручка по месяцам</span>
              <span class="text-xs px-2 py-1 rounded-full bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400">
                {{ analytics?.monthly?.length || 0 }} месяцев
              </span>
            </div>
          </template>
          <template #content>
            <div v-if="revenueChartData" style="height: 280px">
              <Chart type="line" :data="revenueChartData" :options="revenueChartOptions" />
            </div>
            <div v-else class="h-[280px] flex items-center justify-center text-surface-500">
              Нет данных
            </div>
          </template>
        </Card>

        <!-- Status distribution -->
        <Card>
          <template #title>
            <span class="text-lg font-semibold">Статусы заявок</span>
          </template>
          <template #content>
            <div v-if="statusChartData" style="height: 280px">
              <Chart type="doughnut" :data="statusChartData" :options="statusChartOptions" />
            </div>
            <div v-else class="h-[280px] flex items-center justify-center text-surface-500">
              Нет данных
            </div>
          </template>
        </Card>
      </div>

      <!-- Top routes -->
      <Card>
        <template #title>
          <span class="text-lg font-semibold">Топ-5 маршрутов</span>
        </template>
        <template #content>
          <div v-if="topRoutesChartData && analytics.top_routes.length" style="height: 280px">
            <Chart type="bar" :data="topRoutesChartData" :options="topRoutesChartOptions" />
          </div>
          <div v-else class="h-[280px] flex items-center justify-center text-surface-500">
            Нет данных
          </div>
        </template>
      </Card>

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
                <span class="font-semibold">{{ fmtMoney(data.distance_miles * data.rate_per_mile) }}</span>
              </template>
            </Column>
            <Column field="status" header="Статус">
              <template #body="{ data }">
                <Tag
                  :value="STATUS_MAP[data.status]?.label || data.status"
                  :severity="STATUS_MAP[data.status]?.severity || 'secondary'"
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </template>
  </div>
</template>