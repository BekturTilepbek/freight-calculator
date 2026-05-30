import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Подставляем токен в каждый запрос, если он сохранен
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('freight-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Если бэк ответил 401 — токен невалидный, выкидываем на логин
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('freight-token')
      localStorage.removeItem('freight-user')
      // Редирект делаем через window.location, чтобы не зависеть от router
      // в этом месте (избегаем циклической зависимости)
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api