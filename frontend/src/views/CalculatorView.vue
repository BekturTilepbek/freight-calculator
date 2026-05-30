<script setup>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Divider from 'primevue/divider'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

import { calculationsApi } from '@/api/calculations'
import { fmtMoney } from '@/composables/useFormatters'

const router = useRouter()
const toast = useToast()

const form = reactive({
  distance_miles: 1000,
  rate_per_mile: 1.5,
  fuel_consumption_mpg: 6.5,
  fuel_price_per_gallon: 3.80,
})

const result = ref(null)
const loading = ref(false)
const error = ref(null)

const showSaveDialog = ref(false)
const saving = ref(false)
const saveForm = reactive({
  origin_address: '',
  destination_address: '',
  cargo_type: '',
})

async function calculate() {
  loading.value = true
  error.value = null
  try {
    result.value = await calculationsApi.estimate(form)
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Ошибка запроса'
  } finally {
    loading.value = false
  }
}

function reset() {
  result.value = null
  error.value = null
  Object.assign(form, {
    distance_miles: 1000, rate_per_mile: 1.5,
    fuel_consumption_mpg: 6.5, fuel_price_per_gallon: 3.80,
  })
}

async function saveAsOrder() {
  if (!saveForm.origin_address || !saveForm.destination_address) {
    toast.add({
      severity: 'warn', summary: 'Заполните адреса',
      detail: 'Откуда и куда — обязательные поля', life: 3000,
    })
    return
  }
  saving.value = true
  try {
    const created = await calculationsApi.saveAsOrder({
      calculation: form,
      origin_address: saveForm.origin_address,
      destination_address: saveForm.destination_address,
      cargo_type: saveForm.cargo_type || null,
    })
    toast.add({
      severity: 'success', summary: 'Заявка создана',
      detail: 'Открываем карточку заявки...', life: 2000,
    })
    showSaveDialog.value = false
    setTimeout(() => router.push({
      name: 'order-detail', params: { id: created.order_id },
    }), 500)
  } catch (e) {
    toast.add({
      severity: 'error', summary: 'Ошибка',
      detail: e.response?.data?.detail || 'Не удалось сохранить', life: 3000,
    })
  } finally {
    saving.value = false
  }
}

const marginColor = computed(() => {
  if (!result.value) return ''
  const m = Number(result.value.margin_percent)
  if (m >= 40) return 'text-green-600 dark:text-green-400'
  if (m >= 20) return 'text-orange-500'
  return 'text-red-500'
})
</script>

<template>
  <Toast />

  <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
    <!-- Форма -->
    <div class="lg:col-span-2">
      <Card>
        <template #title>
          <div class="flex items-center gap-2">
            <i class="pi pi-calculator text-primary-500" />
            <span>Параметры рейса</span>
          </div>
        </template>
        <template #content>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                Дистанция, миль
              </label>
              <InputNumber
                v-model="form.distance_miles"
                :min="1" :max="10000" :step="50"
                class="w-full"
                showButtons buttonLayout="horizontal"
              >
                <template #incrementbuttonicon><i class="pi pi-plus" /></template>
                <template #decrementbuttonicon><i class="pi pi-minus" /></template>
              </InputNumber>
            </div>

            <div>
              <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                Ставка, $/милю
              </label>
              <InputNumber
                v-model="form.rate_per_mile"
                mode="currency" currency="USD" locale="en-US"
                :min="0" :max="100"
                :minFractionDigits="2" :maxFractionDigits="2"
                class="w-full"
              />
            </div>

            <Divider align="left" type="dashed">
              <span class="text-xs text-surface-500">Параметры топлива</span>
            </Divider>

            <div>
              <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                Расход, MPG
              </label>
              <InputNumber
                v-model="form.fuel_consumption_mpg"
                :min="0.1" :max="50"
                :minFractionDigits="1" :maxFractionDigits="2"
                class="w-full"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1.5">
                Цена топлива, $/галлон
              </label>
              <InputNumber
                v-model="form.fuel_price_per_gallon"
                mode="currency" currency="USD" locale="en-US"
                :min="0" :max="20"
                :minFractionDigits="2" :maxFractionDigits="3"
                class="w-full"
              />
            </div>

            <div class="flex gap-2 pt-2">
              <Button
                label="Рассчитать" icon="pi pi-bolt"
                class="flex-1" :loading="loading"
                @click="calculate"
              />
              <Button icon="pi pi-refresh" severity="secondary" outlined @click="reset" />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Результат -->
    <div class="lg:col-span-3">
      <Card class="h-full">
        <template #title>
          <div class="flex items-center justify-between">
            <span>Результат расчета</span>
            <Button
              v-if="result"
              icon="pi pi-save" label="Сохранить как заявку"
              size="small"
              @click="showSaveDialog = true"
            />
          </div>
        </template>
        <template #content>
          <div v-if="!result && !loading && !error" class="flex flex-col items-center justify-center py-16 text-center">
            <div class="w-16 h-16 rounded-2xl bg-primary-50 dark:bg-primary-950 text-primary-500 flex items-center justify-center mb-4">
              <i class="pi pi-arrow-left text-2xl" />
            </div>
            <p class="text-surface-500 max-w-sm">
              Заполните параметры рейса слева и нажмите «Рассчитать».
            </p>
          </div>

          <div v-if="loading" class="flex justify-center py-16">
            <ProgressSpinner />
          </div>

          <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

          <div v-if="result && !loading" class="space-y-5">
            <div class="grid grid-cols-3 gap-3">
              <div class="p-4 rounded-xl bg-surface-50 dark:bg-surface-800">
                <div class="text-xs text-surface-500 mb-1">Выручка</div>
                <div class="text-xl font-bold">{{ fmtMoney(result.gross_revenue) }}</div>
              </div>
              <div class="p-4 rounded-xl bg-surface-50 dark:bg-surface-800">
                <div class="text-xs text-surface-500 mb-1">Расходы</div>
                <div class="text-xl font-bold text-red-500">{{ fmtMoney(result.total_expenses) }}</div>
              </div>
              <div class="p-4 rounded-xl bg-surface-50 dark:bg-surface-800">
                <div class="text-xs text-surface-500 mb-1">Прибыль</div>
                <div class="text-xl font-bold text-green-600 dark:text-green-400">
                  {{ fmtMoney(result.net_profit) }}
                </div>
              </div>
            </div>

            <div class="p-5 rounded-xl bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900 border border-primary-200 dark:border-primary-800">
              <div class="flex items-baseline justify-between">
                <div>
                  <div class="text-sm text-primary-700 dark:text-primary-300 mb-1">Маржа рейса</div>
                  <div :class="['text-4xl font-extrabold', marginColor]">
                    {{ Number(result.margin_percent).toFixed(1) }}%
                  </div>
                </div>
                <i class="pi pi-chart-line text-5xl text-primary-300 dark:text-primary-700" />
              </div>
            </div>

            <div>
              <h3 class="font-semibold text-sm uppercase tracking-wide text-surface-500 mb-3">Детализация</h3>
              <div class="space-y-2">
                <div
                  v-for="(item, i) in result.breakdown"
                  :key="i"
                  class="flex items-center justify-between p-3 rounded-lg bg-surface-50 dark:bg-surface-800"
                >
                  <div>
                    <div class="font-medium">{{ item.name }}</div>
                    <div v-if="item.description" class="text-xs text-surface-500 mt-0.5">
                      {{ item.description }}
                    </div>
                  </div>
                  <div class="font-semibold tabular-nums">{{ fmtMoney(item.amount) }}</div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>

  <!-- Диалог сохранения -->
  <Dialog
    v-model:visible="showSaveDialog"
    modal header="Сохранить как заявку"
    :style="{ width: '500px' }"
    :closable="!saving"
  >
    <div class="space-y-4">
      <p class="text-sm text-surface-600 dark:text-surface-400">
        Заявка будет создана со статусом «Черновик». Текущий расчет будет привязан к ней.
      </p>
      <div>
        <label class="block text-sm font-medium mb-1.5">Откуда *</label>
        <InputText
          v-model="saveForm.origin_address"
          placeholder="Chicago, IL"
          class="w-full"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">Куда *</label>
        <InputText
          v-model="saveForm.destination_address"
          placeholder="Dallas, TX"
          class="w-full"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">Тип груза</label>
        <InputText
          v-model="saveForm.cargo_type"
          placeholder="Electronics, Food, ..."
          class="w-full"
        />
      </div>
    </div>
    <template #footer>
      <Button
        label="Отмена" severity="secondary" text
        :disabled="saving"
        @click="showSaveDialog = false"
      />
      <Button
        label="Создать заявку" icon="pi pi-check"
        :loading="saving"
        @click="saveAsOrder"
      />
    </template>
  </Dialog>
</template>