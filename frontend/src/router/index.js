import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/layouts/AppLayout.vue'
import LandingView from '@/views/LandingView.vue'
import DashboardView from '@/views/DashboardView.vue'
import CalculatorView from '@/views/CalculatorView.vue'
import OrdersView from '@/views/OrdersView.vue'
import OrderDetailView from '@/views/OrderDetailView.vue'

const routes = [
  { path: '/', name: 'landing', component: LandingView, meta: { title: 'Freight Calculator' } },
  {
    path: '/app',
    component: AppLayout,
    children: [
      { path: '', redirect: { name: 'dashboard' } },
      { path: 'dashboard',   name: 'dashboard',    component: DashboardView,   meta: { title: 'Дашборд' } },
      { path: 'calculator',  name: 'calculator',   component: CalculatorView,  meta: { title: 'Калькулятор' } },
      { path: 'orders',      name: 'orders',       component: OrdersView,      meta: { title: 'Заявки' } },
      { path: 'orders/:id',  name: 'order-detail', component: OrderDetailView, meta: { title: 'Заявка' }, props: true },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · Freight Calculator` : 'Freight Calculator'
})

export default router