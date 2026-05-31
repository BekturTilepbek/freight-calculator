import api from './index'

export const ordersApi = {
  list: (params = {}) => api.get('/orders', { params }).then(r => r.data),
  get: (id) => api.get(`/orders/${id}`).then(r => r.data),
  create: (data) => api.post('/orders', data).then(r => r.data),
  update: (id, data) => api.patch(`/orders/${id}`, data).then(r => r.data),
  remove: (id) => api.delete(`/orders/${id}`),
  stats: () => api.get('/orders/stats').then(r => r.data),
  calculations: (id) => api.get(`/orders/${id}/calculations`).then(r => r.data),
  analytics: () => api.get('/orders/analytics/summary').then(r => r.data),
  // Driver-specific
  myAssigned: () => api.get('/orders/my/assigned').then(r => r.data),
  changeStatus: (id, newStatus) =>
    api.patch(`/orders/${id}/status`, null, { params: { new_status: newStatus } })
      .then(r => r.data),
}