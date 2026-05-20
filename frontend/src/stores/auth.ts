import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userId = ref<string>(localStorage.getItem('userId') || '')
  const userName = ref<string>(localStorage.getItem('userName') || '')
  const role = ref<string>(localStorage.getItem('role') || '')

  const isLoggedIn = computed(() => !!token.value)

  async function login(loginUserId: string, password: string) {
    try {
      const response = await authApi.login(loginUserId, password)
      const data = response.data

      token.value = data.access_token
      userId.value = data.user_id || loginUserId
      userName.value = data.user_name || loginUserId
      role.value = data.role || 'USER'

      localStorage.setItem('token', token.value)
      localStorage.setItem('userId', userId.value)
      localStorage.setItem('userName', userName.value)
      localStorage.setItem('role', role.value)

      router.push('/')
    } catch (error: any) {
      const message = error.response?.data?.detail || '로그인에 실패했습니다.'
      throw new Error(message)
    }
  }

  function logout() {
    token.value = ''
    userId.value = ''
    userName.value = ''
    role.value = ''

    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('userName')
    localStorage.removeItem('role')

    router.push('/login')
  }

  return {
    token,
    userId,
    userName,
    role,
    isLoggedIn,
    login,
    logout
  }
})
