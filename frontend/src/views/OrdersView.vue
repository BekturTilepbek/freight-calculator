<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import ProgressSpinner from 'primevue/progressspinner'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'

import { ordersApi } from '@/api/orders'
import { fmtMoney, fmtNumber, fmtDate, STATUS_MAP } from '@/composables/useFormatters'

const router = useRouter()

const orders = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref(null)

const statusOptions = [
  { label: 'Все статусы', value: null },
  ...Object.entries(STATUS_MAP).map(([k, v]) => ({ label: v.label, value: k })),
]

async function load() {
  loading.value = true
  try {
    orders.value = await ordersApi.list({ limit: 500 })
  } finally {
    loading.value = false
  }
}

const filteredOrders = computed(() => {
  let list = orders.value
  if (statusFilter.value) {
    list = list.filter(o => o.status === statusFilter.value)
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(o =>
      o.order_number.toLowerCase().includes(q) ||
      o.origin_address.toLowerCase().includes(q) ||
      o.destination_address.toLowerCase().includes(q)
    )
  }
  return list
})

function openOrder(order) {
  router.push({ name: 'order-detail', params: { id: order.id } })
}

function newOrder() {
  router.push({ name: 'calculator' })
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <!-- Header with actions -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h2 class="text-sm text-surface-500">
          Всего: <span class="font-semibold text-surface-900 dark:text-surface-0">{{ orders.length }}</span>
          <span v-if="search || statusFilter" class="ml-2">
            · Найдено: <span class="font-semibold text-surface-900 dark:text-surface-0">{{ filteredOrders.length }}</span>
          </span>
        </h2>
      </div>
      <div class="flex items-center gap-2">
        <Button
          label="Обновить"
          icon="pi pi-refresh"
          severity="secondary"
          outlined
          @click="load"
          :loading="loading"
        />
        <Button
          label="Новая заявка"
          icon="pi pi-plus"
          @click="newOrder"
        />
      </div>
    </div>

    <!-- Filters -->
    <Card>
      <template #content>
        <div class="flex flex-wrap gap-3">
          <IconField class="flex-1 min-w-[260px]">
            <InputIcon class="pi pi-search" />
            <InputText
              v-model="search"
              placeholder="Поиск по номеру или маршруту..."
              class="w-full"
            />
          </IconField>
          <Select
            v-model="statusFilter"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Статус"
            class="min-w-[200px]"
            showClear
          />
        </div>
      </template>
    </Card>

    <!-- Table -->
    <Card>
      <template #content>
        <div v-if="loading" class="flex justify-center py-16">
          <ProgressSpinner />
        </div>

        <div v-else-if="filteredOrders.length === 0" class="text-center py-16">
          <i class="pi pi-inbox text-5xl text-surface-300 dark:text-surface-700 mb-3" />
          <p class="text-surface-500">Заявки не найдены</p>
        </div>

        <DataTable
          v-else
          :value="filteredOrders"
          paginator
          :rows="15"
          :rowsPerPageOptions="[10, 15, 25, 50]"
          stripedRows
          :rowHover="true"
          @rowClick="openOrder($event.data)"
          :pt="{ table: { class: 'text-sm' }, bodyRow: { class: 'cursor-pointer' } }"
        >
          <Column field="order_number" header="№" sortable>
            <template #body="{ data }">
              <span class="font-mono font-medium text-primary-600 dark:text-primary-400">
                {{ data.order_number }}
              </span>
            </template>
          </Column>
          <Column header="Маршрут">
            <template #body="{ data }">
              <div class="flex items-center gap-2">
                <i class="pi pi-map-marker text-surface-400 text-xs" />
                <span>{{ data.origin_address }}</span>
                <i class="pi pi-arrow-right text-surface-400 text-xs" />
                <span>{{ data.destination_address }}</span>
              </div>
            </template>
          </Column>
          <Column field="distance_miles" header="Мили" sortable>
            <template #body="{ data }">{{ fmtNumber(data.distance_miles) }}</template>
          </Column>
          <Column header="Ставка">
            <template #body="{ data }">${{ Number(data.rate_per_mile).toFixed(2) }}</template>
          </Column>
          <Column header="Выручка" sortable :sortField="(d) => d.distance_miles * d.rate_per_mile">
            <template #body="{ data }">
              <span class="font-semibold">{{ fmtMoney(data.distance_miles * data.rate_per_mile) }}</span>
            </template>
          </Column>
          <Column field="status" header="Статус" sortable>
            <template #body="{ data }">
              <Tag
                :value="STATUS_MAP[data.status]?.label || data.status"
                :severity="STATUS_MAP[data.status]?.severity || 'secondary'"
                :icon="STATUS_MAP[data.status]?.icon"
              />
            </template>
          </Column>
          <Column field="created_at" header="Создан" sortable>
            <template #body="{ data }">
              <span class="text-surface-500">{{ fmtDate(data.created_at) }}</span>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>