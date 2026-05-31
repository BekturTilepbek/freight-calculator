import api from './index'

export const usersApi = {
  list: (params = {}) => api.get('/users', { params }).then(r => r.data),
}