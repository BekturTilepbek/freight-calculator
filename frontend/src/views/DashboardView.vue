<script setup>
import { ref } from 'vue'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const stats = [
  { label: 'Активные рейсы',  value: '12',       icon: 'pi pi-truck',        delta: '+3', color: 'primary' },
  { label: 'Выручка (месяц)', value: '$48,250',  icon: 'pi pi-dollar',       delta: '+12.4%', color: 'green' },
  { label: 'Средняя маржа',   value: '34.2%',    icon: 'pi pi-chart-line',   delta: '+2.1%',  color: 'blue' },
  { label: 'Пробег (мили)',   value: '24,180',   icon: 'pi pi-map-marker',   delta: '+8%',    color: 'orange' },
]

const colorMap = {
  primary: 'bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400',
  green:   'bg-green-50   dark:bg-green-950   text-green-600   dark:text-green-400',
  blue:    'bg-blue-50    dark:bg-blue-950    text-blue-600    dark:text-blue-400',
  orange:  'bg-orange-50  dark:bg-orange-950  text-orange-600  dark:text-orange-400',
}

const recentOrders = ref([
  { id: 'FR-1042', route: 'Chicago, IL → Dallas, TX',    distance: 925,  revenue: 1387.5, status: 'in_transit' },
  { id: 'FR-1041', route: 'Los Angeles, CA → Phoenix, AZ', distance: 372,  revenue: 558,    status: 'delivered' },
  { id: 'FR-1040', route: 'Atlanta, GA → Miami, FL',     distance: 661,  revenue: 991.5,  status: 'delivered' },
  { id: 'FR-1039', route: 'Seattle, WA → Denver, CO',    distance: 1316, revenue: 1974,   status: 'assigned' },
  { id: 'FR-1038', route: 'Houston, TX → New Orleans, LA', distance: 348,  revenue: 522,    status: 'delivered' },
])

const statusMap = {
  in_transit: { label: 'В пути',       severity: 'info' },
  delivered:  { label: 'Доставлено',   severity: 'success' },
  assigned:   { label: 'Назначен',     severity: 'warn' },
  draft:      { label: 'Черновик',     severity: 'secondary' },
}

function fmtMoney(v) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Stats grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="s in stats"
        :key="s.label"
        class="p-5 rounded-2xl bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-800"
      >
        <div class="flex items-start justify-between mb-3">
          <div :class="['w-11 h-11 rounded-xl flex items-center justify-center', colorMap[s.color]]">
            <i :class="[s.icon, 'text-xl']" />
          </div>
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-950 text-green-700 dark:text-green-400">
            {{ s.delta }}
          </span>
        </div>
        <div class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-1">{{ s.value }}</div>
        <div class="text-sm text-surface-500">{{ s.label }}</div>
      </div>
    </div>

    <!-- Recent orders -->
    <Card>
      <template #title>
        <div class="flex items-center justify-between">
          <span class="text-lg font-semibold">Последние заявки</span>
          <span class="text-sm text-surface-500 font-normal">демо-данные</span>
        </div>
      </template>
      <template #content>
        <DataTable
          :value="recentOrders"
          stripedRows
          :pt="{ table: { class: 'text-sm' } }"
        >
          <Column field="id" header="№ заявки">
            <template #body="{ data }">
              <span class="font-mono font-medium text-primary-600 dark:text-primary-400">
                {{ data.id }}
              </span>
            </template>
          </Column>
          <Column field="route" header="Маршрут" />
          <Column field="distance" header="Дистанция (миль)">
            <template #body="{ data }">{{ data.distance.toLocaleString() }}</template>
          </Column>
          <Column field="revenue" header="Выручка">
            <template #body="{ data }">
              <span class="font-semibold">{{ fmtMoney(data.revenue) }}</span>
            </template>
          </Column>
          <Column field="status" header="Статус">
            <template #body="{ data }">
              <Tag
                :value="statusMap[data.status].label"
                :severity="statusMap[data.status].severity"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>