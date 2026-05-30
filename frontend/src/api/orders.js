import api from './index'

export const ordersApi = {
  list: (params = {}) => api.get('/orders', { params }).then(r => r.data),
  get: (id) => api.get(`/orders/${id}`).then(r => r.data),
  create: (data) => api.post('/orders', data).then(r => r.data),
  update: (id, data) => api.patch(`/orders/${id}`, data).then(r => r.data),
  remove: (id) => api.delete(`/orders/${id}`),
  stats: () => api.get('/orders/stats').then(r => r.data),
  calculations: (id) => api.get(`/orders/${id}/calculations`).then(r => r.data),
}