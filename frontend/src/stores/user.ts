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

  // 登录
  const login = async (loginData: LoginFormData) => {
    try {
      loginLoading.value = true
      const response = await authApi.login(loginData)

      if (response.data.success) {
        const { access_token, refresh_token, user_info: userInfoData } = response.data.data as LoginResponse

        token.value = access_token
        refreshToken.value = refresh_token
        userInfo.value = userInfoData
        roles.value = userInfoData.roles || []
        permissions.value = userInfoData.permissions || []

        console.log('登录成功，用户数据:', {
          userInfoData,
          roles: roles.value,
          token: access_token
        })

        // 保存到本地存储 - 统一使用'user'作为key
        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)
        localStorage.setItem('user', JSON.stringify(userInfoData))
        // 为了兼容性，同时保存到userInfo
        localStorage.setItem('userInfo', JSON.stringify(userInfoData))

        ElMessage.success('登录成功')

        // 根据角色跳转
        const redirect = router.currentRoute.value.query.redirect as string
        if (userInfoData.roles?.includes('admin')) {
          router.replace(redirect || '/dashboard')
        } else if (userInfoData.roles?.includes('teacher')) {
          router.replace(redirect || '/teacher/dashboard')
        } else {
          router.replace(redirect || '/student/dashboard')
        }

        return true
      } else {
        ElMessage.error(response.data.message || '登录失败')
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

      // 检查响应格式
      if (response.data?.success) {
        ElMessage.success(response.data?.message || '注册成功，请登录')
        return true
      } else {
        ElMessage.error(response.data?.message || '注册失败')
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

      // 清除本地存储 - 清除所有可能的key
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
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

      if (response.data.success) {
        userInfo.value = response.data.data
        roles.value = response.data.data.roles || []
        permissions.value = response.data.data.permissions || []

        localStorage.setItem('userInfo', JSON.stringify(response.data.data))
        return true
      } else {
        throw new Error(response.data.message)
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

  // 权限检查方法
  const checkUserPermission = (permission: string) => {
    return permissions.value.includes(permission) || isAdmin.value
  }

  const hasAnyPermission = (permissionList: string[]) => {
    return permissionList.some(permission => permissions.value.includes(permission) || isAdmin.value)
  }

  const hasAllPermissions = (permissionList: string[]) => {
    return permissionList.every(permission => permissions.value.includes(permission) || isAdmin.value)
  }

  // 为了向后兼容，提供hasPermission别名
  const hasPermission = checkUserPermission

  const checkPermission = async (permission: string) => {
    try {
      const response = await fetch('/api/auth/check-permission', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token.value}`
        },
        body: JSON.stringify({ permission })
      })

      if (response.ok) {
        const result = await response.json()
        return result.success ? result.data.has_permission : false
      }
      return false
    } catch (error) {
      console.error('权限检查错误:', error)
      return false
    }
  }

  const refreshPermissions = async () => {
    try {
      const response = await fetch('/api/auth/permissions', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })

      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          permissions.value = result.data.permissions
          return true
        }
      }
      return false
    } catch (error) {
      console.error('刷新权限错误:', error)
      return false
    }
  }

  // 初始化用户信息（从本地存储恢复）
  const initUserInfo = () => {
    console.log('=== 开始初始化用户信息 ===')

    // 检查当前状态
    console.log('当前userStore状态:', {
      hasToken: !!token.value,
      hasUserInfo: !!userInfo.value,
      currentRoles: roles.value
    })

    const storedToken = localStorage.getItem('token')
    // 修复：localStorage中保存的key是'user'，不是'userInfo'
    const storedUserInfo = localStorage.getItem('userInfo') || localStorage.getItem('user')

    // 调试：打印localStorage中的所有内容
    console.log('localStorage完整内容:')
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key) {
        console.log(`  ${key}: ${localStorage.getItem(key)}`)
      }
    }

    console.log('初始化用户信息 - token:', storedToken, 'userInfo:', storedUserInfo)

    // 如果已经有用户信息，就不重新初始化
    if (userInfo.value && token.value) {
      console.log('用户信息已存在，跳过初始化')
      return
    }

    if (storedToken) {
      token.value = storedToken
    }

    if (storedUserInfo) {
      try {
        userInfo.value = JSON.parse(storedUserInfo)
        // 修复：如果localStorage中有role但没有roles，则创建roles数组
        if (userInfo.value?.role && !userInfo.value?.roles) {
          userInfo.value.roles = [userInfo.value.role]
        }
        roles.value = userInfo.value?.roles || []
        permissions.value = userInfo.value?.permissions || []
        console.log('用户信息恢复成功:', {
          userInfo: userInfo.value,
          roles: roles.value,
          role: userInfo.value?.role,
          userInfoType: typeof userInfo.value,
          rolesType: typeof roles.value
        })
      } catch (error) {
        console.error('Parse user info error:', error)
        console.error('Original userInfo string:', storedUserInfo)
        localStorage.removeItem('user')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('token')
      }
    } else {
      console.log('没有找到用户信息，可能是首次访问')
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

    // 权限检查方法
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    checkPermission,
    refreshPermissions,

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