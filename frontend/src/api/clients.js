import api from './index'

export const clientsApi = {
  list: (params = {}) => api.get('/clients', { params }).then(r => r.data),
  get: (id) => api.get(`/clients/${id}`).then(r => r.data),
}