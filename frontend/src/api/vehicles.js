import api from './index'

export const vehiclesApi = {
  list: () => api.get('/vehicles').then(r => r.data),
  get: (id) => api.get(`/vehicles/${id}`).then(r => r.data),
  create: (data) => api.post('/vehicles', data).then(r => r.data),
  update: (id, data) => api.patch(`/vehicles/${id}`, data).then(r => r.data),
  remove: (id) => api.delete(`/vehicles/${id}`),
}