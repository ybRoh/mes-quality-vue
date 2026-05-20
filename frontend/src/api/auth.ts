import client from './client'

export const authApi = {
  login(userId: string, password: string) {
    return client.post('/auth/login', { user_id: userId, password })
  },

  logout() {
    return client.post('/auth/logout')
  },

  getMe() {
    return client.get('/auth/me')
  }
}
