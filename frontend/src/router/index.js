import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/layouts/AppLayout.vue'
import LandingView from '@/views/LandingView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import CalculatorView from '@/views/CalculatorView.vue'
import OrdersView from '@/views/OrdersView.vue'
import OrderDetailView from '@/views/OrderDetailView.vue'
import ClientsView from '@/views/ClientsView.vue'
import BrokersView from '@/views/BrokersView.vue'
import VehiclesView from '@/views/VehiclesView.vue'

import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/',         name: 'landing',  component: LandingView,  meta: { title: 'FreightFlow' } },
  { path: '/login',    name: 'login',    component: LoginView,    meta: { title: 'Вход', guest: true } },
  { path: '/register', name: 'register', component: RegisterView, meta: { title: 'Регистрация', guest: true } },
  {
    path: '/app',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: { name: 'dashboard' } },
      { path: 'dashboard',   name: 'dashboard',    component: DashboardView,   meta: { title: 'Дашборд' } },
      { path: 'calculator',  name: 'calculator',   component: CalculatorView,  meta: { title: 'Калькулятор' } },
      { path: 'orders',      name: 'orders',       component: OrdersView,      meta: { title: 'Заявки' } },
      { path: 'orders/:id',  name: 'order-detail', component: OrderDetailView, meta: { title: 'Заявка' }, props: true },
      { path: 'clients',   name: 'clients',   component: ClientsView,  meta: { title: 'Клиенты' } },
      { path: 'brokers',   name: 'brokers',   component: BrokersView,  meta: { title: 'Брокеры' } },
      { path: 'vehicles',  name: 'vehicles',  component: VehiclesView, meta: { title: 'Транспорт' } },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()

  // Защищенные роуты — нужен токен
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // Гостевые роуты (login/register) — авторизованных перенаправляем в дашборд
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · FreightFlow` : 'FreightFlow'
})

export default router