import api from './index'

export const brokersApi = {
  list: () => api.get('/brokers').then(r => r.data),
  get: (id) => api.get(`/brokers/${id}`).then(r => r.data),
  create: (data) => api.post('/brokers', data).then(r => r.data),
  update: (id, data) => api.patch(`/brokers/${id}`, data).then(r => r.data),
  remove: (id) => api.delete(`/brokers/${id}`),
}