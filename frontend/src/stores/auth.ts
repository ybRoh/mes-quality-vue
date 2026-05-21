import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const userId = ref<string>(localStorage.getItem('userId') || '')
  const userName = ref<string>(localStorage.getItem('userName') || '')
  const role = ref<string>(localStorage.getItem('role') || '')
  const sessionChecked = ref(false)

  const isLoggedIn = computed(() => !!userId.value)

  async function login(loginUserId: string, password: string) {
    try {
      const response = await authApi.login(loginUserId, password)
      const data = response.data

      userId.value = data.user_id || loginUserId
      userName.value = data.user_name || loginUserId
      role.value = data.role || 'USER'

      localStorage.setItem('userId', userId.value)
      localStorage.setItem('userName', userName.value)
      localStorage.setItem('role', role.value)

      router.push('/')
    } catch (error: any) {
      const message = error.response?.data?.detail || '로그인에 실패했습니다.'
      throw new Error(message)
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // 쿠키 만료 등으로 실패해도 클라이언트 정리 진행
    }

    userId.value = ''
    userName.value = ''
    role.value = ''
    sessionChecked.value = false

    localStorage.removeItem('userId')
    localStorage.removeItem('userName')
    localStorage.removeItem('role')

    router.push('/login')
  }

  async function checkSession(): Promise<boolean> {
    try {
      const res = await authApi.getMe()
      userId.value = res.data.user_id
      userName.value = res.data.user_name
      role.value = res.data.role || 'USER'
      localStorage.setItem('userId', userId.value)
      localStorage.setItem('userName', userName.value)
      localStorage.setItem('role', role.value)
      sessionChecked.value = true
      return true
    } catch {
      userId.value = ''
      userName.value = ''
      role.value = ''
      localStorage.removeItem('userId')
      localStorage.removeItem('userName')
      localStorage.removeItem('role')
      return false
    }
  }

  return {
    userId,
    userName,
    role,
    sessionChecked,
    isLoggedIn,
    login,
    logout,
    checkSession
  }
})
