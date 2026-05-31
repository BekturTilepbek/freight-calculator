<script setup>
import { ref, reactive, onMounted } from 'vue'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import ProgressSpinner from 'primevue/progressspinner'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

import { brokersApi } from '@/api/brokers'
import { fmtDate } from '@/composables/useFormatters'

const toast = useToast()
const confirm = useConfirm()

const items = ref([])
const loading = ref(true)
const search = ref('')

const dialogVisible = ref(false)
const saving = ref(false)
const editingId = ref(null)
const form = reactive({
  company_name: '', mc_number: '', contact_person: '', email: '', phone: '',
})

async function load() {
  loading.value = true
  try {
    items.value = await brokersApi.list()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, { company_name: '', mc_number: '', contact_person: '', email: '', phone: '' })
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  Object.assign(form, {
    company_name: row.company_name,
    mc_number: row.mc_number || '',
    contact_person: row.contact_person || '',
    email: row.email || '',
    phone: row.phone || '',
  })
  dialogVisible.value = true
}

async function save() {
  if (!form.company_name?.trim()) {
    toast.add({ severity: 'warn', summary: 'Заполните название компании', life: 2000 })
    return
  }
  saving.value = true
  try {
    const payload = {
      company_name: form.company_name,
      mc_number: form.mc_number || null,
      contact_person: form.contact_person || null,
      email: form.email || null,
      phone: form.phone || null,
    }
    if (editingId.value) {
      await brokersApi.update(editingId.value, payload)
      toast.add({ severity: 'success', summary: 'Брокер обновлен', life: 2000 })
    } else {
      await brokersApi.create(payload)
      toast.add({ severity: 'success', summary: 'Брокер создан', life: 2000 })
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
    message: `Удалить брокера «${row.company_name}»?`,
    header: 'Подтверждение',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: { label: 'Отмена', severity: 'secondary', outlined: true },
    acceptProps: { label: 'Удалить', severity: 'danger' },
    accept: async () => {
      try {
        await brokersApi.remove(row.id)
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

const filtered = () => {
  if (!search.value) return items.value
  const q = search.value.toLowerCase()
  return items.value.filter(b =>
    b.company_name?.toLowerCase().includes(q) ||
    b.mc_number?.toLowerCase().includes(q) ||
    b.email?.toLowerCase().includes(q)
  )
}

onMounted(load)
</script>

<template>
  <Toast />
  <ConfirmDialog />

  <div class="space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h2 class="text-sm text-surface-500">
        Всего брокеров: <span class="font-semibold text-surface-900 dark:text-surface-0">{{ items.length }}</span>
      </h2>
      <Button label="Новый брокер" icon="pi pi-plus" @click="openCreate" />
    </div>

    <Card>
      <template #content>
        <div class="relative max-w-md mb-4">
          <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none z-10" />
          <InputText v-model="search" placeholder="Поиск..." class="w-full !pl-10" />
        </div>

        <div v-if="loading" class="flex justify-center py-16">
          <ProgressSpinner />
        </div>

        <DataTable
          v-else
          :value="filtered()"
          paginator :rows="15"
          stripedRows
          :pt="{ table: { class: 'text-sm' } }"
        >
          <Column field="company_name" header="Компания" sortable>
            <template #body="{ data }">
              <div class="font-semibold">{{ data.company_name }}</div>
            </template>
          </Column>
          <Column field="mc_number" header="MC Number">
            <template #body="{ data }">
              <span v-if="data.mc_number" class="font-mono text-sm">{{ data.mc_number }}</span>
              <span v-else class="text-surface-400">—</span>
            </template>
          </Column>
          <Column field="contact_person" header="Контакт">
            <template #body="{ data }">{{ data.contact_person || '—' }}</template>
          </Column>
          <Column field="email" header="Email">
            <template #body="{ data }">
              <a v-if="data.email" :href="`mailto:${data.email}`" class="text-primary-600 dark:text-primary-400 hover:underline">
                {{ data.email }}
              </a>
              <span v-else class="text-surface-400">—</span>
            </template>
          </Column>
          <Column field="phone" header="Телефон">
            <template #body="{ data }">{{ data.phone || '—' }}</template>
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
    :header="editingId ? 'Редактировать брокера' : 'Новый брокер'"
    :style="{ width: '500px' }"
    :closable="!saving"
  >
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1.5">Название компании *</label>
        <InputText v-model="form.company_name" placeholder="TQL Logistics" class="w-full" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">MC Number</label>
        <InputText v-model="form.mc_number" placeholder="MC-123456" class="w-full" />
        <small class="text-surface-500">Motor Carrier Number — реквизит брокера в США</small>
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">Контактное лицо</label>
        <InputText v-model="form.contact_person" placeholder="John Smith" class="w-full" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">Email</label>
        <InputText v-model="form.email" type="email" placeholder="contact@broker.com" class="w-full" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5">Телефон</label>
        <InputText v-model="form.phone" placeholder="+1 555 1234567" class="w-full" />
      </div>
    </div>
    <template #footer>
      <Button label="Отмена" severity="secondary" text :disabled="saving" @click="dialogVisible = false" />
      <Button label="Сохранить" icon="pi pi-check" :loading="saving" @click="save" />
    </template>
  </Dialog>
</template>