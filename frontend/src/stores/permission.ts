import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userApi } from '@/api/user'
import type { Permission, Role } from '@/types/user'
import { ElMessage } from 'element-plus'

export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const permissions = ref<Permission[]>([])
  const roles = ref<Role[]>([])
  const userPermissions = ref<string[]>([])
  const userRoles = ref<string[]>([])
  const loading = ref(false)

  // 计算属性
  const hasPermission = computed(() => (permission: string) => {
    return userPermissions.value.includes(permission) || isSuperAdmin.value
  })

  const hasRole = computed(() => (role: string) => {
    return userRoles.value.includes(role)
  })

  const hasAnyRole = computed(() => (rolesList: string[]) => {
    return rolesList.some(role => userRoles.value.includes(role))
  })

  const hasAllRoles = computed(() => (rolesList: string[]) => {
    return rolesList.every(role => userRoles.value.includes(role))
  })

  const isSuperAdmin = computed(() => {
    return userRoles.value.includes('admin') || userRoles.value.includes('super_admin')
  })

  const isTeacher = computed(() => {
    return userRoles.value.includes('teacher')
  })

  const isStudent = computed(() => {
    return userRoles.value.includes('student')
  })

  // 获取权限列表
  const getPermissions = async () => {
    try {
      loading.value = true
      const response = await userApi.getPermissions()

      if (response.success) {
        permissions.value = response.data.permissions || []
        roles.value = response.data.roles || []
        return true
      } else {
        ElMessage.error(response.message || '获取权限列表失败')
        return false
      }
    } catch (error: any) {
      console.error('Get permissions error:', error)
      ElMessage.error(error.response?.data?.message || '获取权限列表失败，请稍后重试')
      return false
    } finally {
      loading.value = false
    }
  }

  // 获取用户权限
  const getUserPermissions = async (userId?: number) => {
    try {
      loading.value = true
      const response = await userApi.getUserPermissions(userId)

      if (response.success) {
        userPermissions.value = response.data.permissions || []
        userRoles.value = response.data.roles || []
        return true
      } else {
        ElMessage.error(response.message || '获取用户权限失败')
        return false
      }
    } catch (error: any) {
      console.error('Get user permissions error:', error)
      ElMessage.error(error.response?.data?.message || '获取用户权限失败，请稍后重试')
      return false
    } finally {
      loading.value = false
    }
  }

  // 设置用户权限和角色
  const setUserPermissions = (permissionsList: string[], rolesList: string[]) => {
    userPermissions.value = permissionsList
    userRoles.value = rolesList
  }

  // 清除用户权限和角色
  const clearUserPermissions = () => {
    userPermissions.value = []
    userRoles.value = []
  }

  // 检查路由权限
  const hasRoutePermission = (route: any) => {
    // 如果路由没有设置权限要求，则允许访问
    if (!route.meta?.roles && !route.meta?.permissions) {
      return true
    }

    // 检查角色权限
    if (route.meta?.roles) {
      const requiredRoles = Array.isArray(route.meta.roles) ? route.meta.roles : [route.meta.roles]
      if (!hasAnyRole.value(requiredRoles)) {
        return false
      }
    }

    // 检查具体权限
    if (route.meta?.permissions) {
      const requiredPermissions = Array.isArray(route.meta.permissions)
        ? route.meta.permissions
        : [route.meta.permissions]

      for (const permission of requiredPermissions) {
        if (!hasPermission.value(permission)) {
          return false
        }
      }
    }

    return true
  }

  // 获取可访问的菜单
  const getAccessibleMenus = (menus: any[]) => {
    return menus.filter(menu => {
      if (menu.meta?.hidden) {
        return false
      }

      if (menu.children) {
        menu.children = getAccessibleMenus(menu.children)
        return menu.children.length > 0
      }

      return hasRoutePermission(menu)
    })
  }

  // 权限过滤器（用于v-permission指令）
  const filterPermissions = (permissionsList: string[]) => {
    return permissionsList.filter(permission => hasPermission.value(permission))
  }

  // 角色过滤器（用于v-role指令）
  const filterRoles = (rolesList: string[]) => {
    return rolesList.filter(role => hasRole.value(role))
  }

  // 初始化权限
  const initializePermissions = async () => {
    // 从本地存储恢复用户权限
    const storedUserPermissions = localStorage.getItem('userPermissions')
    const storedUserRoles = localStorage.getItem('userRoles')

    if (storedUserPermissions) {
      try {
        userPermissions.value = JSON.parse(storedUserPermissions)
      } catch (error) {
        console.error('Parse user permissions error:', error)
        localStorage.removeItem('userPermissions')
      }
    }

    if (storedUserRoles) {
      try {
        userRoles.value = JSON.parse(storedUserRoles)
      } catch (error) {
        console.error('Parse user roles error:', error)
        localStorage.removeItem('userRoles')
      }
    }

    // 加载系统权限列表
    await getPermissions()
  }

  // 权限验证中间件
  const requirePermission = (permission: string) => {
    if (!hasPermission.value(permission)) {
      ElMessage.error('权限不足')
      return false
    }
    return true
  }

  // 角色验证中间件
  const requireRole = (role: string) => {
    if (!hasRole.value(role)) {
      ElMessage.error('角色权限不足')
      return false
    }
    return true
  }

  // 多角色验证中间件
  const requireAnyRole = (rolesList: string[]) => {
    if (!hasAnyRole.value(rolesList)) {
      ElMessage.error('角色权限不足')
      return false
    }
    return true
  }

  return {
    // 状态
    permissions,
    roles,
    userPermissions,
    userRoles,
    loading,

    // 计算属性
    hasPermission,
    hasRole,
    hasAnyRole,
    hasAllRoles,
    isSuperAdmin,
    isTeacher,
    isStudent,

    // 方法
    getPermissions,
    getUserPermissions,
    setUserPermissions,
    clearUserPermissions,
    hasRoutePermission,
    getAccessibleMenus,
    filterPermissions,
    filterRoles,
    initializePermissions,
    requirePermission,
    requireRole,
    requireAnyRole
  }
})