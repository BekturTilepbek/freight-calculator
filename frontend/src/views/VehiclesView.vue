<script setup>
import { ref, reactive, onMounted } from 'vue'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import ProgressSpinner from 'primevue/progressspinner'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

import { vehiclesApi } from '@/api/vehicles'
import { usersApi } from '@/api/users'

const toast = useToast()
const confirm = useConfirm()

const items = ref([])
const drivers = ref([])
const loading = ref(true)

const dialogVisible = ref(false)
const saving = ref(false)
const editingId = ref(null)
const form = reactive({
  plate_number: '', make: '', model: '',
  fuel_consumption_mpg: 6.5, driver_id: null, is_active: true,
})

async function load() {
  loading.value = true
  try {
    const [v, d] = await Promise.all([
      vehiclesApi.list(),
      usersApi.list({ role: 'driver' }),
    ])
    items.value = v
    drivers.value = d
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, {
    plate_number: '', make: '', model: '',
    fuel_consumption_mpg: 6.5, driver_id: null, is_active: true,
  })
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    plate_number: row.plate_number,
    make: row.make || '',
    model: row.model || '',
    fuel_consumption_mpg: Number(row.fuel_consumption_mpg),
    driver_id: row.driver_id,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

async function save() {
  if (!form.plate_number?.trim()) {
    toast.add({ severity: 'warn', summary: 'Заполните гос. номер', life: 2000 })
    return
  }
  saving.value = true
  try {
    const payload = {
      plate_number: form.plate_number,
      make: form.make || null,
      model: form.model || null,
      fuel_consumption_mpg: form.fuel_consumption_mpg,
      driver_id: form.driver_id || null,
      is_active: form.is_active,
    }
    if (editingId.value) {
      await vehiclesApi.update(editingId.value, payload)
      toast.add({ severity: 'success', summary: 'ТС обновлено', life: 2000 })
    } else {
      await vehiclesApi.create(payload)
      toast.add({ severity: 'success', summary: 'ТС добавлено', life: 2000 })
    }
    dialogVisible.value = false
    await load()
  } catch (e) {
    toast.add({
      severity: 'error', summary: 'Ошибка',
      detail: e.response?.data?.detail || 'Не удалось сохранить', life: 3000,
    })
  } finally {
    saving.value = false
  }
}

function confirmDelete(row) {
  confirm.require({
    message: `Удалить ТС «${row.plate_number}»?`,
    header: 'Подтверждение',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Отмена', severity: 'secondary', outlined: true },
    acceptProps: { label: 'Удалить', severity: 'danger' },
    accept: async () => {
      try {
        await vehiclesApi.remove(row.id)
        toast.add({ severity: 'success', summary: 'Удалено', life: 2000 })
        await load()
      } catch (e) {
        toast.add({
          severity: 'error', summary: 'Ошибка',
          detail: e.response?.data?.detail || 'Нет прав на удаление',
          life: 3000,
        })
      }
    },
  })
}

onMounted(load)
</script>

<template>
  <Toast />
  <ConfirmDialog />

  <div class="space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h2 class="text-sm text-surface-500">
        Всего ТС: <span class="font-semibold text-surface-900 dark:text-surface-0">{{ items.length }}</span>
      </h2>
      <Button label="Добавить ТС" icon="pi pi-plus" @click="openCreate" />
    </div>

    <Card>
      <template #content>
        <div v-if="loading" class="flex justify-center py-16">
          <ProgressSpinner />
        </div>

        <div v-else-if="items.length === 0" class="text-center py-16">
          <i class="pi pi-truck text-5xl text-surface-300 dark:text-surface-700 mb-3" />
          <p class="text-surface-500">Пока нет добавленных ТС</p>
        </div>

        <DataTable
          v-else
          :value="items"
          paginator :rows="15"
          stripedRows
          :pt="{ table: { class: 'text-sm' } }"
        >
          <Column field="plate_number" header="Гос. номер" sortable>
            <template #body="{ data }">
              <span class="font-mono font-semibold">{{ data.plate_number }}</span>
            </template>
          </Column>
          <Column header="Марка / Модель">
            <template #body="{ data }">
              <span v-if="data.make || data.model">
                {{ data.make }} {{ data.model }}
              </span>
              <span v-else class="text-surface-400">—</span>
            </template>
          </Column>
          <Column field="fuel_consumption_mpg" header="Расход (MPG)" sortable>
            <template #body="{ data }">
              {{ Number(data.fuel_consumption_mpg).toFixed(1) }}
            </template>
          </Column>
          <Column header="Водитель">
            <template #body="{ data }">
              <span v-if="data.driver">{{ data.driver.full_name }}</span>
              <span v-else class="text-surface-400">Не назначен</span>
            </template>
          </Column>
          <Column field="is_active" header="Статус">
            <template #body="{ data }">
              <Tag
                :value="data.is_active ? 'Активно' : 'Неактивно'"
                :severity="data.is_active ? 'success' : 'secondary'"
              />
            </template>
          </Column>
          <Column header="" style="width: 100px">
            <template #body="{ data }">
              <div class="flex gap-1 justify-end">
                <Button icon="pi pi-pencil" text rounded severity="secondary" @click="openEdit(data)" />
                <Button icon="pi pi-trash" text rounded severity="danger" @click="confirmDelete(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>

  <Dialog
    v-model:visible="dialogVisible"
    modal
    :header="editingId ? 'Редактировать ТС' : 'Новое ТС'"
    :style="{ width: '500px' }"
    :closable="!saving"
  >
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1.5">Гос. номер *</label>
        <InputText v-model="form.plate_number" placeholder="ABC-1234" class="w-full" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm font-medium mb-1.5">Марка</label>
          <InputText v-model="form.make" placeholder="Freightliner" class="w-full" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1.5">Модель</label>
          <InputText v-model="form.model" placeholder="Cascadia" class="w-full" />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">Расход топлива (MPG)</label>
        <InputNumber
          v-model="form.fuel_consumption_mpg"
          :min="0.1" :max="50"
          :minFractionDigits="1" :maxFractionDigits="2"
          class="w-full"
        />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">Водитель</label>
        <Select
          v-model="form.driver_id"
          :options="drivers"
          optionLabel="full_name"
          optionValue="id"
          placeholder="Не назначен"
          class="w-full"
          showClear
        />
      </div>
      <div class="flex items-center gap-3">
        <ToggleSwitch v-model="form.is_active" inputId="is_active" />
        <label for="is_active" class="text-sm font-medium cursor-pointer">
          ТС активно
        </label>
      </div>
    </div>
    <template #footer>
      <Button label="Отмена" severity="secondary" text :disabled="saving" @click="dialogVisible = false" />
      <Button label="Сохранить" icon="pi pi-check" :loading="saving" @click="save" />
    </template>
  </Dialog>
</template>