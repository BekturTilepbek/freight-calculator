<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const { isDark, toggle } = useTheme()

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref(null)

async function handleLogin() {
  loading.value = true
  error.value = null
  try {
    await auth.login(form.email, form.password)
    const redirect = route.query.redirect || { name: 'dashboard' }
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}

function quickLogin(email, password) {
  form.email = email
  form.password = password
  handleLogin()
}
</script>

<template>
  <div class="min-h-screen flex bg-surface-50 dark:bg-surface-950">
    <!-- Левая часть — брендинг -->
    <div class="hidden lg:flex lg:flex-1 relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900">
      <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 80%, white 1px, transparent 1px); background-size: 50px 50px;"></div>
      <div class="relative z-10 flex flex-col justify-between p-12 text-white w-full">
        <RouterLink to="/" class="flex items-center gap-2.5 text-white">
          <div class="w-10 h-10 rounded-lg bg-white/20 backdrop-blur flex items-center justify-center font-bold">FF</div>
          <span class="font-bold text-xl">FreightFlow</span>
        </RouterLink>

        <div>
          <h2 class="text-4xl font-extrabold mb-4 leading-tight">
            Автоматизируйте свою<br />логистику
          </h2>
          <p class="text-white/80 text-lg mb-8 max-w-md">
            FreightFlow — TMS для диспетчеров: расчет стоимости, маржа, история заявок.
          </p>
          <div class="flex flex-wrap gap-3">
            <div class="px-3 py-1.5 rounded-full bg-white/10 backdrop-blur text-sm font-medium">FastAPI</div>
            <div class="px-3 py-1.5 rounded-full bg-white/10 backdrop-blur text-sm font-medium">Vue 3</div>
            <div class="px-3 py-1.5 rounded-full bg-white/10 backdrop-blur text-sm font-medium">PostgreSQL</div>
            <div class="px-3 py-1.5 rounded-full bg-white/10 backdrop-blur text-sm font-medium">Docker</div>
          </div>
        </div>

        <div class="text-sm text-white/60">© 2026 · Дипломная работа</div>
      </div>
    </div>

    <!-- Правая часть — форма -->
    <div class="flex-1 flex items-center justify-center p-6 relative">
      <Button
        :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
        text rounded severity="secondary"
        class="!absolute top-4 right-4"
        @click="toggle"
      />

      <div class="w-full max-w-md">
        <div class="lg:hidden mb-8 text-center">
          <RouterLink to="/" class="inline-flex items-center gap-2.5">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold">FF</div>
            <span class="font-bold text-xl text-surface-900 dark:text-surface-0">FreightFlow</span>
          </RouterLink>
        </div>

        <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-0 mb-2">Вход в систему</h1>
        <p class="text-surface-500 mb-8">Введите email и пароль для продолжения</p>

        <Message v-if="error" severity="error" :closable="false" class="!mb-4">
          {{ error }}
        </Message>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1.5 text-surface-700 dark:text-surface-300">Email</label>
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
            <label class="block text-sm font-medium mb-1.5 text-surface-700 dark:text-surface-300">Пароль</label>
            <Password
              v-model="form.password"
              :feedback="false"
              toggleMask
              placeholder="••••••••"
              inputClass="w-full"
              class="w-full"
              :pt="{ root: { class: 'w-full' } }"
              autocomplete="current-password"
              required
            />
          </div>

          <Button
            type="submit"
            label="Войти"
            icon="pi pi-sign-in"
            class="w-full"
            size="large"
            :loading="loading"
          />
        </form>

        <div class="mt-6 text-center text-sm text-surface-600 dark:text-surface-400">
          Нет аккаунта?
          <RouterLink to="/register" class="text-primary-600 dark:text-primary-400 font-medium hover:underline">
            Зарегистрироваться
          </RouterLink>
        </div>

        <!-- Demo accounts -->
        <div class="mt-8 pt-6 border-t border-surface-200 dark:border-surface-800">
          <p class="text-xs uppercase tracking-wide text-surface-500 mb-3 text-center">
            Демо-доступ для проверки
          </p>
          <div class="space-y-2">
            <button
              type="button"
              class="w-full text-left p-3 rounded-lg border border-surface-200 dark:border-surface-800 hover:border-primary-300 dark:hover:border-primary-700 transition-colors"
              @click="quickLogin('admin@freight.app', 'admin123')"
            >
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-sm">Администратор</div>
                  <div class="text-xs text-surface-500 font-mono">admin@freight.app</div>
                </div>
                <i class="pi pi-arrow-right text-surface-400" />
              </div>
            </button>
            <button
              type="button"
              class="w-full text-left p-3 rounded-lg border border-surface-200 dark:border-surface-800 hover:border-primary-300 dark:hover:border-primary-700 transition-colors"
              @click="quickLogin('dispatcher@freight.app', 'dispatcher123')"
            >
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-sm">Диспетчер</div>
                  <div class="text-xs text-surface-500 font-mono">dispatcher@freight.app</div>
                </div>
                <i class="pi pi-arrow-right text-surface-400" />
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>