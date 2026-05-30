import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

const TOKEN_KEY = 'freight-token'
const USER_KEY = 'freight-user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || null)
  const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isDispatcher = computed(() => user.value?.role === 'dispatcher')
  const isDriver = computed(() => user.value?.role === 'driver')

  function setSession(data) {
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
  }

  function clearSession() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  async function login(email, password) {
    const data = await authApi.login({ email, password })
    setSession(data)
    return data
  }

  async function register(payload) {
    const data = await authApi.register(payload)
    setSession(data)
    return data
  }

  async function fetchMe() {
    try {
      const me = await authApi.me()
      user.value = me
      localStorage.setItem(USER_KEY, JSON.stringify(me))
      return me
    } catch {
      clearSession()
      return null
    }
  }

  function logout() {
    clearSession()
  }

  return {
    token, user,
    isAuthenticated, isAdmin, isDispatcher, isDriver,
    login, register, logout, fetchMe,
  }
})