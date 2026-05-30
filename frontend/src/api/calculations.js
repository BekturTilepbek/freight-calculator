import api from './index'

export const calculationsApi = {
  estimate: (data) => api.post('/calculations/estimate', data).then(r => r.data),
  saveAsOrder: (data) => api.post('/calculations/save-as-order', data).then(r => r.data),
}