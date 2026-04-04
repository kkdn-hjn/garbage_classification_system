import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const permissionCodes = ref([])
  const isAuthenticated = ref(!!token.value)

  async function login(username, password) {
    try {
      const response = await api.post('/auth/login', { username, password })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      isAuthenticated.value = true
      await fetchUser()
      return { success: true }
    } catch (error) {
      const detail = error.response?.data?.detail
      const message = Array.isArray(detail) ? detail[0]?.msg || '登录失败' : (detail || '登录失败')
      return { success: false, message }
    }
  }

  async function register(userData) {
    try {
      await api.post('/auth/register', userData)
      return { success: true }
    } catch (error) {
      const detail = error.response?.data?.detail
      const message = Array.isArray(detail) ? detail[0]?.msg || '注册失败' : (detail || '注册失败')
      return { success: false, message }
    }
  }

  async function fetchUser() {
    try {
      const [userRes, permRes] = await Promise.all([
        api.get('/auth/me'),
        api.get('/auth/permissions')
      ])
      user.value = userRes.data
      permissionCodes.value = permRes.data?.permission_codes || []
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    permissionCodes.value = []
    localStorage.removeItem('token')
    isAuthenticated.value = false
  }

  function hasPermission(code) {
    return permissionCodes.value.includes(code)
  }

  return { token, user, permissionCodes, isAuthenticated, login, register, fetchUser, logout, hasPermission }
})
