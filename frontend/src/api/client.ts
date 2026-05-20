import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'

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
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('userId')
      localStorage.removeItem('userName')
      localStorage.removeItem('role')
      window.location.href = '/login'
    } else {
      console.warn(`API 오류 [${error.response?.status}]:`, error.response?.data?.detail || error.message)
    }
    return Promise.reject(error)
  }
)

export default client
