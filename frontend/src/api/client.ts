import axios from 'axios'
import type { AxiosError, AxiosInstance, AxiosResponse } from 'axios'

const client: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// Response interceptor: handle 401
client.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Lazy import to avoid circular dependency:
      // client.ts -> router -> stores/auth -> api/auth -> client.ts
      const { useAuthStore } = await import('@/stores/auth')
      const authStore = useAuthStore()
      authStore.logout()
    } else {
      const data = error.response?.data as Record<string, unknown> | undefined
      console.warn(`API 오류 [${error.response?.status}]:`, data?.detail || error.message)
    }
    return Promise.reject(error)
  }
)

export default client
