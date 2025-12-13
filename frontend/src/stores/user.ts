import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { LoginFormData, RegisterFormData, UserInfo, LoginResponse } from '@/types/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string>(localStorage.getItem('token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refreshToken') || '')
  const userInfo = ref<UserInfo | null>(null)
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])
  const loginLoading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => roles.value.includes('admin'))
  const isTeacher = computed(() => roles.value.includes('teacher'))
  const isStudent = computed(() => roles.value.includes('student'))
  const hasPermission = computed(() => (permission: string) => {
    return permissions.value.includes(permission) || isAdmin.value
  })

  // 登录
  const login = async (loginData: LoginFormData) => {
    try {
      loginLoading.value = true
      const response = await authApi.login(loginData)

      if (response.success) {
        const { access_token, refresh_token, user_info: userInfoData } = response.data as LoginResponse

        token.value = access_token
        refreshToken.value = refresh_token
        userInfo.value = userInfoData
        roles.value = userInfoData.roles || []
        permissions.value = userInfoData.permissions || []

        // 保存到本地存储
        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)
        localStorage.setItem('userInfo', JSON.stringify(userInfoData))

        ElMessage.success('登录成功')

        // 根据角色跳转
        const redirect = router.currentRoute.value.query.redirect as string
        if (userInfoData.roles?.includes('admin')) {
          router.replace(redirect || '/admin/dashboard')
        } else if (userInfoData.roles?.includes('teacher')) {
          router.replace(redirect || '/dashboard')
        } else {
          router.replace(redirect || '/dashboard')
        }

        return true
      } else {
        ElMessage.error(response.message || '登录失败')
        return false
      }
    } catch (error: any) {
      console.error('Login error:', error)
      ElMessage.error(error.response?.data?.message || '登录失败，请稍后重试')
      return false
    } finally {
      loginLoading.value = false
    }
  }

  // 注册
  const register = async (registerData: RegisterFormData) => {
    try {
      loginLoading.value = true
      const response = await authApi.register(registerData)

      if (response.success) {
        ElMessage.success('注册成功，请登录')
        router.push('/login')
        return true
      } else {
        ElMessage.error(response.message || '注册失败')
        return false
      }
    } catch (error: any) {
      console.error('Register error:', error)
      ElMessage.error(error.response?.data?.message || '注册失败，请稍后重试')
      return false
    } finally {
      loginLoading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // 清除状态
      token.value = ''
      refreshToken.value = ''
      userInfo.value = null
      permissions.value = []
      roles.value = []

      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userInfo')

      ElMessage.success('已退出登录')
      router.push('/login')
    }
  }

  // 刷新Token
  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token')
      }

      const response = await authApi.refreshToken(refreshToken.value)

      if (response.success) {
        const { access_token, refresh_token: newRefreshToken } = response.data

        token.value = access_token
        refreshToken.value = newRefreshToken || refreshToken.value

        localStorage.setItem('token', access_token)
        if (newRefreshToken) {
          localStorage.setItem('refreshToken', newRefreshToken)
        }

        return true
      } else {
        throw new Error(response.message)
      }
    } catch (error) {
      console.error('Token refresh error:', error)
      await logout()
      return false
    }
  }

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      const response = await authApi.getUserInfo()

      if (response.success) {
        userInfo.value = response.data
        roles.value = response.data.roles || []
        permissions.value = response.data.permissions || []

        localStorage.setItem('userInfo', JSON.stringify(response.data))
        return true
      } else {
        throw new Error(response.message)
      }
    } catch (error) {
      console.error('Get user info error:', error)
      await logout()
      return false
    }
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      const response = await authApi.changePassword({ old_password: oldPassword, new_password: newPassword })

      if (response.success) {
        ElMessage.success('密码修改成功')
        return true
      } else {
        ElMessage.error(response.message || '密码修改失败')
        return false
      }
    } catch (error: any) {
      console.error('Change password error:', error)
      ElMessage.error(error.response?.data?.message || '密码修改失败，请稍后重试')
      return false
    }
  }

  // 更新用户信息
  const updateUserInfo = async (data: Partial<UserInfo>) => {
    try {
      const response = await authApi.updateUserInfo(data)

      if (response.success) {
        userInfo.value = { ...userInfo.value, ...response.data } as UserInfo
        localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
        ElMessage.success('用户信息更新成功')
        return true
      } else {
        ElMessage.error(response.message || '更新失败')
        return false
      }
    } catch (error: any) {
      console.error('Update user info error:', error)
      ElMessage.error(error.response?.data?.message || '更新失败，请稍后重试')
      return false
    }
  }

  // 初始化用户信息（从本地存储恢复）
  const initUserInfo = () => {
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      try {
        userInfo.value = JSON.parse(storedUserInfo)
        roles.value = userInfo.value?.roles || []
        permissions.value = userInfo.value?.permissions || []
      } catch (error) {
        console.error('Parse user info error:', error)
        localStorage.removeItem('userInfo')
      }
    }
  }

  return {
    // 状态
    token,
    refreshToken,
    userInfo,
    permissions,
    roles,
    loginLoading,

    // 计算属性
    isAuthenticated,
    isAdmin,
    isTeacher,
    isStudent,
    hasPermission,

    // 方法
    login,
    register,
    logout,
    refreshAccessToken,
    getUserInfo,
    changePassword,
    updateUserInfo,
    initUserInfo
  }
})