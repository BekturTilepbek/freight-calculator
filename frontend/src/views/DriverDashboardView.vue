<script setup>
import { ref, computed, onMounted } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

import { ordersApi } from '@/api/orders'
import { fmtMoney, fmtNumber, fmtDate, STATUS_MAP } from '@/composables/useFormatters'

const toast = useToast()
const orders = ref([])
const loading = ref(true)
const updatingId = ref(null)

async function load() {
  loading.value = true
  try {
    orders.value = await ordersApi.myAssigned()
  } catch (e) {
    toast.add({
      severity: 'error', summary: 'Ошибка',
      detail: 'Не удалось загрузить рейсы', life: 3000,
    })
  } finally {
    loading.value = false
  }
}

const grouped = computed(() => {
  const result = { active: [], delivered: [] }
  for (const o of orders.value) {
    if (o.status === 'delivered' || o.status === 'cancelled') {
      result.delivered.push(o)
    } else {
      result.active.push(o)
    }
  }
  return result
})

// Следующий разрешенный статус для водителя
function nextStatus(current) {
  if (current === 'assigned') return { label: 'Начать рейс', value: 'in_transit', icon: 'pi pi-play' }
  if (current === 'in_transit') return { label: 'Завершить рейс', value: 'delivered', icon: 'pi pi-check' }
  return null
}

async function changeStatus(order, newStatus) {
  updatingId.value = order.id
  try {
    const updated = await ordersApi.changeStatus(order.id, newStatus)
    Object.assign(order, updated)
    toast.add({
      severity: 'success',
      summary: 'Статус обновлен',
      detail: STATUS_MAP[newStatus]?.label,
      life: 2000,
    })
  } catch (e) {
    toast.add({
      severity: 'error', summary: 'Ошибка',
      detail: e.response?.data?.detail || 'Не удалось сменить статус', life: 3000,
    })
  } finally {
    updatingId.value = null
  }
}
</script>

<template>
  <Toast />

  <div v-if="loading" class="flex justify-center py-20">
    <ProgressSpinner />
  </div>

  <div v-else class="space-y-6">
    <!-- Greeting -->
    <Card>
      <template #content>
        <div class="flex items-center justify-between flex-wrap gap-3">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white text-2xl">
              <i class="pi pi-truck" />
            </div>
            <div>
              <div class="text-sm text-surface-500">Активных рейсов</div>
              <div class="text-2xl font-bold">{{ grouped.active.length }}</div>
            </div>
          </div>
          <div class="text-sm text-surface-500">
            Завершено всего: <span class="font-semibold text-surface-900 dark:text-surface-0">{{ grouped.delivered.length }}</span>
          </div>
        </div>
      </template>
    </Card>

    <!-- Active rides -->
    <div>
      <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
        <i class="pi pi-clock text-primary-500" /> Активные рейсы
      </h3>

      <div v-if="grouped.active.length === 0" class="text-center py-12 text-surface-500">
        <i class="pi pi-check-circle text-4xl text-green-500 mb-2" />
        <p>Нет активных рейсов. Хорошего отдыха!</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="order in grouped.active"
          :key="order.id"
          class="p-5 rounded-2xl bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-800"
        >
          <div class="flex items-start justify-between mb-4 flex-wrap gap-3">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="font-mono font-bold text-primary-600 dark:text-primary-400">{{ order.order_number }}</span>
                <Tag
                  :value="STATUS_MAP[order.status]?.label"
                  :severity="STATUS_MAP[order.status]?.severity"
                  :icon="STATUS_MAP[order.status]?.icon"
                />
              </div>
              <div class="text-sm text-surface-500">
                Забор: {{ fmtDate(order.created_at) }}
              </div>
            </div>
            <div class="text-right">
              <div class="text-xs text-surface-500">Выручка</div>
              <div class="font-bold text-lg">
                {{ fmtMoney(order.distance_miles * order.rate_per_mile) }}
              </div>
            </div>
          </div>

          <!-- Route -->
          <div class="flex items-start gap-3 mb-4">
            <div class="flex flex-col items-center pt-1">
              <div class="w-2.5 h-2.5 rounded-full bg-primary-500" />
              <div class="w-px h-8 bg-surface-300 dark:bg-surface-700 my-1" />
              <div class="w-2.5 h-2.5 rounded-full bg-green-500" />
            </div>
            <div class="flex-1 space-y-3">
              <div>
                <div class="text-xs text-surface-500">Откуда</div>
                <div class="font-medium">{{ order.origin_address }}</div>
              </div>
              <div>
                <div class="text-xs text-surface-500">Куда</div>
                <div class="font-medium">{{ order.destination_address }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="text-xs text-surface-500">Дистанция</div>
              <div class="font-semibold">{{ fmtNumber(order.distance_miles) }} mi</div>
            </div>
          </div>

          <!-- Action -->
          <div v-if="nextStatus(order.status)" class="flex justify-end">
            <Button
              :label="nextStatus(order.status).label"
              :icon="nextStatus(order.status).icon"
              :loading="updatingId === order.id"
              @click="changeStatus(order, nextStatus(order.status).value)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Recent delivered -->
    <div v-if="grouped.delivered.length">
      <h3 class="text-lg font-semibold mb-3 flex items-center gap-2">
        <i class="pi pi-check text-green-500" /> Последние завершенные
      </h3>
      <Card>
        <template #content>
          <div class="space-y-2">
            <div
              v-for="order in grouped.delivered.slice(0, 5)"
              :key="order.id"
              class="flex items-center justify-between p-3 rounded-lg hover:bg-surface-50 dark:hover:bg-surface-800"
            >
              <div class="flex items-center gap-3">
                <Tag
                  :value="STATUS_MAP[order.status]?.label"
                  :severity="STATUS_MAP[order.status]?.severity"
                />
                <div>
                  <span class="font-mono text-sm text-primary-600 dark:text-primary-400">{{ order.order_number }}</span>
                  <div class="text-sm text-surface-500">
                    {{ order.origin_address }} → {{ order.destination_address }}
                  </div>
                </div>
              </div>
              <div class="text-right">
                <div class="font-semibold">{{ fmtMoney(order.distance_miles * order.rate_per_mile) }}</div>
                <div class="text-xs text-surface-500">{{ fmtNumber(order.distance_miles) }} mi</div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>