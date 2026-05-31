import api from './index'

export const geoApi = {
  route: (origin, destination) =>
    api.post('/geo/route', { origin, destination }).then(r => r.data),
}