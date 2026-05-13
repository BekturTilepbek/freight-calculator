import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/layouts/AppLayout.vue'
import LandingView from '@/views/LandingView.vue'
import DashboardView from '@/views/DashboardView.vue'
import CalculatorView from '@/views/CalculatorView.vue'

const routes = [
  {
    path: '/',
    name: 'landing',
    component: LandingView,
    meta: { title: 'Freight Calculator' },
  },
  {
    path: '/app',
    component: AppLayout,
    children: [
      {
        path: '',
        redirect: { name: 'dashboard' },
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: DashboardView,
        meta: { title: 'Дашборд' },
      },
      {
        path: 'calculator',
        name: 'calculator',
        component: CalculatorView,
        meta: { title: 'Калькулятор' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = to.meta.title
    ? `${to.meta.title} · Freight Calculator`
    : 'Freight Calculator'
})

export default router