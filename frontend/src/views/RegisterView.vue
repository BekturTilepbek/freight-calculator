<script setup>
import { ref, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const router = useRouter()
const auth = useAuthStore()
const { isDark, toggle } = useTheme()

const form = reactive({ full_name: '', email: '', password: '' })
const loading = ref(false)
const error = ref(null)

async function handleRegister() {
  loading.value = true
  error.value = null
  try {
    await auth.register(form)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-950 p-6 relative">
    <Button
      :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
      text rounded severity="secondary"
      class="!absolute top-4 right-4"
      @click="toggle"
    />

    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <RouterLink to="/" class="inline-flex items-center gap-2.5">
          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold">FF</div>
          <span class="font-bold text-xl text-surface-900 dark:text-surface-0">FreightFlow</span>
        </RouterLink>
      </div>

      <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-0 mb-2 text-center">Регистрация</h1>
      <p class="text-surface-500 mb-8 text-center">Создайте аккаунт диспетчера</p>

      <Message v-if="error" severity="error" :closable="false" class="!mb-4">
        {{ error }}
      </Message>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1.5">ФИО</label>
          <InputText
            v-model="form.full_name"
            placeholder="Иван Иванов"
            class="w-full"
            required
            minlength="2"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5">Email</label>
          <InputText
            v-model="form.email"
            type="email"
            placeholder="you@company.com"
            class="w-full"
            autocomplete="email"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5">Пароль</label>
          <Password
            v-model="form.password"
            toggleMask
            placeholder="Минимум 6 символов"
            inputClass="w-full"
            :pt="{ root: { class: 'w-full' } }"
            autocomplete="new-password"
            required
            minlength="6"
          />
        </div>

        <Button
          type="submit"
          label="Создать аккаунт"
          icon="pi pi-user-plus"
          class="w-full"
          size="large"
          :loading="loading"
        />
      </form>

      <div class="mt-6 text-center text-sm text-surface-600 dark:text-surface-400">
        Уже есть аккаунт?
        <RouterLink to="/login" class="text-primary-600 dark:text-primary-400 font-medium hover:underline">
          Войти
        </RouterLink>
      </div>
    </div>
  </div>
</template>