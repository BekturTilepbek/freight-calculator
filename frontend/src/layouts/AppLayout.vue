<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter, RouterLink, RouterView } from 'vue-router'
import Button from 'primevue/button'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { isDark, toggle } = useTheme()

const sidebarOpen = ref(true)
const userMenuOpen = ref(false)
const userMenuRef = ref(null)

const pageTitle = computed(() => route.meta.title || '')

const userInitials = computed(() => {
  if (!auth.user?.full_name) return '?'
  return auth.user.full_name
    .split(' ').slice(0, 2).map(s => s[0]).join('').toUpperCase()
})

const ROLE_LABELS = {
  admin: 'Администратор',
  dispatcher: 'Диспетчер',
  driver: 'Водитель',
}
const roleLabel = computed(() => ROLE_LABELS[auth.user?.role] || '')

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}

function onClickOutside(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    userMenuOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))

const menu = [
  { label: 'Дашборд',     icon: 'pi pi-th-large',   to: '/app/dashboard' },
  { label: 'Калькулятор', icon: 'pi pi-calculator', to: '/app/calculator' },
  { label: 'Заявки',      icon: 'pi pi-truck',      to: '/app/orders' },
  { label: 'Клиенты',     icon: 'pi pi-building',   to: '/app/clients',  disabled: true },
  { label: 'Водители',    icon: 'pi pi-users',      to: '/app/drivers',  disabled: true },
  { label: 'Отчеты',      icon: 'pi pi-chart-bar',  to: '/app/reports',  disabled: true },
]
</script>

<template>
  <div class="min-h-screen flex bg-surface-50 dark:bg-surface-950">
    <!-- Sidebar -->
    <aside
      :class="[
        'transition-all duration-200 border-r border-surface-200 dark:border-surface-800',
        'bg-white dark:bg-surface-900',
        sidebarOpen ? 'w-64' : 'w-20',
      ]"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center px-4 border-b border-surface-200 dark:border-surface-800">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold flex-shrink-0">
          FF
        </div>
        <span v-if="sidebarOpen" class="ml-3 font-bold text-lg text-surface-900 dark:text-surface-0">
          Freight<span class="text-primary-500">Flow</span>
        </span>
      </div>

      <!-- Nav -->
      <nav class="p-3 space-y-1">
        <RouterLink
          v-for="item in menu"
          :key="item.to"
          :to="item.disabled ? '' : item.to"
          :class="[
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
            item.disabled
              ? 'text-surface-400 dark:text-surface-600 cursor-not-allowed'
              : 'text-surface-700 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-surface-800',
          ]"
          active-class="!bg-primary-50 dark:!bg-primary-950 !text-primary-700 dark:!text-primary-300"
          :event="item.disabled ? '' : 'click'"
        >
          <i :class="[item.icon, 'text-lg flex-shrink-0']" />
          <span v-if="sidebarOpen" class="flex-1">{{ item.label }}</span>
          <span
            v-if="sidebarOpen && item.disabled"
            class="text-xs px-1.5 py-0.5 rounded bg-surface-200 dark:bg-surface-800 text-surface-500"
          >
            скоро
          </span>
        </RouterLink>
      </nav>
    </aside>

    <!-- Main column -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Topbar -->
      <header class="h-16 flex items-center justify-between px-6 bg-white dark:bg-surface-900 border-b border-surface-200 dark:border-surface-800">
        <div class="flex items-center gap-3">
          <Button
            icon="pi pi-bars"
            text
            rounded
            severity="secondary"
            @click="sidebarOpen = !sidebarOpen"
          />
          <h1 class="text-lg font-semibold text-surface-900 dark:text-surface-0">
            {{ pageTitle }}
          </h1>
        </div>

        <div class="flex items-center gap-2">
          <Button
            :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
            text rounded severity="secondary"
            @click="toggle"
          />
          <Button icon="pi pi-bell" text rounded severity="secondary" />

          <!-- Меню пользователя -->
          <div class="relative" ref="userMenuRef">
            <button
              class="flex items-center gap-2 pl-2 ml-2 border-l border-surface-200 dark:border-surface-800 hover:opacity-80 transition-opacity"
              @click="userMenuOpen = !userMenuOpen"
            >
              <div class="w-9 h-9 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center text-white text-sm font-semibold">
                {{ userInitials }}
              </div>
              <div class="hidden md:block leading-tight text-left">
                <div class="text-sm font-medium text-surface-900 dark:text-surface-0">{{ auth.user?.full_name }}</div>
                <div class="text-xs text-surface-500">{{ roleLabel }}</div>
              </div>
              <i class="pi pi-chevron-down text-xs text-surface-400 hidden md:block" />
            </button>

            <div
              v-if="userMenuOpen"
              class="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-800 rounded-lg shadow-xl py-1.5 z-50"
            >
              <div class="px-3 py-2 border-b border-surface-200 dark:border-surface-800 md:hidden">
                <div class="font-medium text-sm">{{ auth.user?.full_name }}</div>
                <div class="text-xs text-surface-500">{{ auth.user?.email }}</div>
              </div>
              <button
                class="w-full px-3 py-2 text-left text-sm hover:bg-surface-100 dark:hover:bg-surface-800 flex items-center gap-2 text-red-600 dark:text-red-400"
                @click="handleLogout"
              >
                <i class="pi pi-sign-out" />
                Выйти
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="flex-1 p-6 overflow-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>