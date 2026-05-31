<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Select from 'primevue/select'
import ProgressSpinner from 'primevue/progressspinner'
import Divider from 'primevue/divider'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

import { ordersApi } from '@/api/orders'
import { vehiclesApi } from '@/api/vehicles'
import {
  fmtMoney, fmtNumber, fmtDate, fmtDateTime, STATUS_MAP,
} from '@/composables/useFormatters'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()
const toast = useToast()

const order = ref(null)
const calculations = ref([])
const vehicles = ref([])
const loading = ref(true)
const updatingStatus = ref(false)
const updatingVehicle = ref(false)

const statusOptions = Object.entries(STATUS_MAP).map(([k, v]) => ({
  label: v.label, value: k,
}))

const revenue = computed(() => {
  if (!order.value) return 0
  return Number(order.value.distance_miles) * Number(order.value.rate_per_mile)
})

const latestCalc = computed(() => calculations.value[0] || null)

const assignedVehicle = computed(() => {
  if (!order.value?.vehicle_id) return null
  return vehicles.value.find(v => v.id === order.value.vehicle_id) || null
})

async function load() {
  loading.value = true
  try {
    const [o, c, v] = await Promise.all([
      ordersApi.get(props.id),
      ordersApi.calculations(props.id),
      vehiclesApi.list(),
    ])
    order.value = o
    calculations.value = c
    vehicles.value = v
  } catch (e) {
    toast.add({
      severity: 'error', summary: 'Ошибка',
      detail: 'Не удалось загрузить заявку', life: 3000,
    })
  } finally {
    loading.value = false
  }
}

async function changeStatus(newStatus) {
  if (newStatus === order.value.status) return
  updatingStatus.value = true
  try {
    order.value = await ordersApi.update(props.id, { status: newStatus })
    toast.add({
      severity: 'success', summary: 'Статус обновлен',
      detail: STATUS_MAP[newStatus]?.label, life: 2000,
    })
  } catch {
    toast.add({
      severity: 'error', summary: 'Ошибка',
      detail: 'Не удалось обновить', life: 3000,
    })
  } finally {
    updatingStatus.value = false
  }
}

async function assignVehicle(vehicleId) {
  if (vehicleId === order.value.vehicle_id) return
  updatingVehicle.value = true
  try {
    const updates = { vehicle_id: vehicleId }
    // Auto-transition draft → assigned when vehicle is picked
    if (vehicleId && order.value.status === 'draft') {
      updates.status = 'assigned'
    }
    order.value = await ordersApi.update(props.id, updates)
    toast.add({
      severity: 'success',
      summary: vehicleId ? 'ТС назначено' : 'ТС снято с заявки',
      life: 2000,
    })
  } catch (e) {
    toast.add({
      severity: 'error', summary: 'Ошибка',
      detail: e.response?.data?.detail || 'Не удалось назначить', life: 3000,
    })
  } finally {
    updatingVehicle.value = false
  }
}

onMounted(load)
</script>

<template>
  <Toast />

  <div v-if="loading" class="flex justify-center py-20">
    <ProgressSpinner />
  </div>

  <div v-else-if="order" class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div class="flex items-center gap-3">
        <Button
          icon="pi pi-arrow-left"
          severity="secondary"
          text rounded
          @click="router.push({ name: 'orders' })"
        />
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 font-mono">
              {{ order.order_number }}
            </h1>
            <Tag
              :value="STATUS_MAP[order.status]?.label"
              :severity="STATUS_MAP[order.status]?.severity"
              :icon="STATUS_MAP[order.status]?.icon"
            />
          </div>
          <div class="text-sm text-surface-500 mt-1">
            Создана {{ fmtDateTime(order.created_at) }}
          </div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Select
          :modelValue="order.status"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Изменить статус"
          :loading="updatingStatus"
          @update:modelValue="changeStatus"
        />
        <Button icon="pi pi-file-pdf" label="PDF" severity="secondary" outlined disabled />
      </div>
    </div>

    <!-- Main grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Маршрут -->
      <Card class="lg:col-span-2">
        <template #title>Маршрут</template>
        <template #content>
          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <div class="flex flex-col items-center pt-1">
                <div class="w-3 h-3 rounded-full bg-primary-500 ring-4 ring-primary-100 dark:ring-primary-950" />
                <div class="w-px h-12 bg-surface-300 dark:bg-surface-700 my-1" />
                <div class="w-3 h-3 rounded-full bg-green-500 ring-4 ring-green-100 dark:ring-green-950" />
              </div>
              <div class="flex-1 space-y-4">
                <div>
                  <div class="text-xs uppercase tracking-wide text-surface-500 mb-1">Откуда</div>
                  <div class="font-medium">{{ order.origin_address }}</div>
                  <div v-if="order.pickup_date" class="text-sm text-surface-500 mt-1">
                    Забор: {{ fmtDate(order.pickup_date) }}
                  </div>
                </div>
                <div>
                  <div class="text-xs uppercase tracking-wide text-surface-500 mb-1">Куда</div>
                  <div class="font-medium">{{ order.destination_address }}</div>
                  <div v-if="order.delivery_date" class="text-sm text-surface-500 mt-1">
                    Доставка: {{ fmtDate(order.delivery_date) }}
                  </div>
                </div>
              </div>
            </div>

            <Divider />

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <div class="text-xs text-surface-500 mb-1">Дистанция</div>
                <div class="font-semibold">{{ fmtNumber(order.distance_miles) }} mi</div>
              </div>
              <div>
                <div class="text-xs text-surface-500 mb-1">Ставка</div>
                <div class="font-semibold">${{ Number(order.rate_per_mile).toFixed(2) }}/mi</div>
              </div>
              <div>
                <div class="text-xs text-surface-500 mb-1">Груз</div>
                <div class="font-semibold">{{ order.cargo_type || '—' }}</div>
              </div>
              <div>
                <div class="text-xs text-surface-500 mb-1">Вес</div>
                <div class="font-semibold">{{ order.weight_lbs ? `${fmtNumber(order.weight_lbs)} lbs` : '—' }}</div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Правая колонка: Исполнитель + Финансы -->
      <div class="space-y-4">
        <!-- Исполнитель -->
        <Card>
          <template #title>
            <span class="text-sm font-semibold uppercase tracking-wide text-surface-500">
              Исполнитель
            </span>
          </template>
          <template #content>
            <div class="space-y-3">
              <div>
                <label class="block text-xs font-medium text-surface-500 mb-1.5">
                  Транспортное средство
                </label>
                <Select
                  :modelValue="order.vehicle_id"
                  :options="vehicles"
                  optionLabel="plate_number"
                  optionValue="id"
                  placeholder="Не назначено"
                  class="w-full"
                  showClear
                  :loading="updatingVehicle"
                  @update:modelValue="assignVehicle"
                >
                  <template #option="{ option }">
                    <div>
                      <div class="font-mono font-semibold">{{ option.plate_number }}</div>
                      <div class="text-xs text-surface-500">
                        {{ option.make }} {{ option.model }}
                        <span v-if="option.driver">· {{ option.driver.full_name }}</span>
                        <span v-else class="text-orange-500">· без водителя</span>
                      </div>
                    </div>
                  </template>
                </Select>
              </div>

              <div v-if="assignedVehicle?.driver" class="p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white font-semibold">
                    {{ assignedVehicle.driver.full_name?.split(' ').slice(0, 2).map(s => s[0]).join('').toUpperCase() }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="font-medium text-sm truncate">{{ assignedVehicle.driver.full_name }}</div>
                    <div class="text-xs text-surface-500 truncate">{{ assignedVehicle.driver.email }}</div>
                  </div>
                </div>
              </div>

              <div v-else-if="assignedVehicle" class="p-3 rounded-lg bg-orange-50 dark:bg-orange-950 text-orange-700 dark:text-orange-400 text-sm flex items-center gap-2">
                <i class="pi pi-exclamation-triangle" />
                У этого ТС не назначен водитель
              </div>

              <div v-else class="text-sm text-surface-500 italic">
                Назначьте ТС — водитель увидит заявку у себя.
              </div>
            </div>
          </template>
        </Card>

        <!-- Финансы -->
        <Card>
          <template #title>Финансы</template>
          <template #content>
            <div class="space-y-3">
              <div class="p-4 rounded-xl bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900">
                <div class="text-sm text-primary-700 dark:text-primary-300 mb-1">Выручка</div>
                <div class="text-3xl font-extrabold text-primary-700 dark:text-primary-200">
                  {{ fmtMoney(revenue) }}
                </div>
              </div>

              <template v-if="latestCalc">
                <div class="flex items-center justify-between py-2">
                  <span class="text-sm text-surface-600 dark:text-surface-400">Топливо</span>
                  <span class="font-semibold text-red-500">−{{ fmtMoney(latestCalc.fuel_cost) }}</span>
                </div>
                <div v-if="Number(latestCalc.extra_costs_total) > 0" class="flex items-center justify-between py-2">
                  <span class="text-sm text-surface-600 dark:text-surface-400">Доп. расходы</span>
                  <span class="font-semibold text-red-500">−{{ fmtMoney(latestCalc.extra_costs_total) }}</span>
                </div>
                <Divider class="!my-2" />
                <div class="flex items-center justify-between py-1">
                  <span class="font-semibold">Прибыль</span>
                  <span class="text-lg font-bold text-green-600 dark:text-green-400">
                    {{ fmtMoney(latestCalc.net_profit) }}
                  </span>
                </div>
                <div class="flex items-center justify-between">
                  <span class="text-sm text-surface-600 dark:text-surface-400">Маржа</span>
                  <span class="font-semibold">{{ Number(latestCalc.margin_percent).toFixed(1) }}%</span>
                </div>
              </template>
              <div v-else class="text-sm text-surface-500 italic">
                Расчет не сохранен.
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- История расчетов -->
    <Card v-if="calculations.length">
      <template #title>
        История расчетов
        <span class="text-sm text-surface-500 font-normal ml-2">({{ calculations.length }})</span>
      </template>
      <template #content>
        <div class="space-y-2">
          <div
            v-for="(c, i) in calculations"
            :key="c.id"
            class="p-4 rounded-lg border border-surface-200 dark:border-surface-800"
            :class="i === 0 ? 'bg-surface-50 dark:bg-surface-800' : ''"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="text-sm text-surface-500">{{ fmtDateTime(c.created_at) }}</span>
                <Tag v-if="i === 0" value="Актуальный" severity="success" />
              </div>
              <div class="font-semibold">{{ fmtMoney(c.net_profit) }} · {{ Number(c.margin_percent).toFixed(1) }}%</div>
            </div>
            <div class="text-xs text-surface-500">
              Топливо: {{ c.fuel_consumption_mpg }} MPG · ${{ Number(c.fuel_price_per_gallon).toFixed(2) }}/gal · Топливо: {{ fmtMoney(c.fuel_cost) }}
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>

  <div v-else class="text-center py-20 text-surface-500">
    Заявка не найдена
  </div>
</template>