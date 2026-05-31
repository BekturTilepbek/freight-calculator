<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import DashboardView from '@/views/DashboardView.vue'
import DriverDashboardView from '@/views/DriverDashboardView.vue'

const auth = useAuthStore()
const isDriver = computed(() => auth.user?.role === 'driver')
</script>

<template>
  <DriverDashboardView v-if="isDriver" />
  <DashboardView v-else />
</template>