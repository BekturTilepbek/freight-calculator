<script setup>
import { RouterLink } from 'vue-router'
import Button from 'primevue/button'
import { useTheme } from '@/composables/useTheme'

const { isDark, toggle } = useTheme()

const features = [
  {
    icon: 'pi pi-calculator',
    title: 'Автоматический расчет',
    text: 'Стоимость рейса с учетом ставки, топлива и дополнительных расходов — за секунды.',
  },
  {
    icon: 'pi pi-map',
    title: 'Маршруты и дистанции',
    text: 'Интеграция с картографическими сервисами для точного расчета пробега.',
  },
  {
    icon: 'pi pi-chart-line',
    title: 'Аналитика прибыли',
    text: 'Маржа, выручка, расходы — детализация по каждому рейсу и сводно по периоду.',
  },
  {
    icon: 'pi pi-file-pdf',
    title: 'Документы',
    text: 'Генерация Bill of Lading и Rate Confirmation в один клик.',
  },
]
</script>

<template>
  <div class="min-h-screen bg-surface-50 dark:bg-surface-950 text-surface-900 dark:text-surface-0">
    <!-- Nav -->
    <nav class="max-w-7xl mx-auto flex items-center justify-between px-6 py-5">
      <div class="flex items-center gap-2.5">
        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold">
          FF
        </div>
        <span class="font-bold text-xl">
          Freight<span class="text-primary-500">Flow</span>
        </span>
      </div>
      <div class="flex items-center gap-3">
        <Button
          :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
          text rounded severity="secondary"
          @click="toggle"
        />
        <RouterLink to="/login">
          <Button label="Войти в систему" icon="pi pi-arrow-right" iconPos="right" />
        </RouterLink>
      </div>
    </nav>

    <!-- Hero -->
    <section class="max-w-7xl mx-auto px-6 pt-16 pb-24 text-center">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 dark:bg-primary-950/50 border border-primary-200 dark:border-primary-900 text-primary-700 dark:text-primary-300 text-xs font-medium mb-6">
        <span class="w-1.5 h-1.5 rounded-full bg-primary-500 animate-pulse" />
        Дипломный проект · 2026
      </div>
      <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight leading-tight mb-6">
        TMS для логистики,
        <br />
        <span class="bg-gradient-to-r from-primary-500 via-primary-600 to-primary-700 bg-clip-text text-transparent">
          которой удобно пользоваться
        </span>
      </h1>
      <p class="text-lg md:text-xl text-surface-600 dark:text-surface-400 max-w-2xl mx-auto mb-10">
        Расчет стоимости рейсов, ведение заявок, история расчетов, ролевая модель.
        Все, что нужно диспетчеру — в одном приложении.
      </p>
      <div class="flex flex-wrap items-center justify-center gap-3">
        <RouterLink to="/login">
          <Button label="Открыть калькулятор" icon="pi pi-calculator" size="large" />
        </RouterLink>
        <RouterLink to="/login">
          <Button label="Посмотреть дашборд" severity="secondary" outlined size="large" />
        </RouterLink>
      </div>
    </section>

    <!-- Features -->
    <section class="max-w-7xl mx-auto px-6 pb-24">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="f in features"
          :key="f.title"
          class="p-6 rounded-2xl bg-white dark:bg-surface-900 border border-surface-200 dark:border-surface-800 hover:border-primary-300 dark:hover:border-primary-700 transition-colors"
        >
          <div class="w-11 h-11 rounded-xl bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-400 flex items-center justify-center mb-4">
            <i :class="[f.icon, 'text-xl']" />
          </div>
          <h3 class="font-semibold text-lg mb-2">{{ f.title }}</h3>
          <p class="text-sm text-surface-600 dark:text-surface-400 leading-relaxed">{{ f.text }}</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-surface-200 dark:border-surface-800">
      <div class="max-w-7xl mx-auto px-6 py-8 text-sm text-surface-500 flex flex-wrap items-center justify-between gap-3">
        <div>© 2026 FreightFlow · Дипломная работа</div>
        <div>FastAPI · Vue 3 · PostgreSQL · Docker</div>
      </div>
    </footer>
  </div>
</template>