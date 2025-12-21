import { useUserStore } from '@/stores/user'
import type { App, Directive, DirectiveBinding } from 'vue'

/**
 * 权限指令 v-permission
 * 用法：
 * v-permission="'manage_users'"          - 需要特定权限
 * v-permission="['manage_users', 'read']" - 需要任意一个权限
 * :v-permission="{permissions: ['manage_users'], mode: 'all'}" - 需要所有权限
 */
export const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding)
  },
  updated(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding)
  }
}

function checkPermission(el: HTMLElement, binding: DirectiveBinding) {
  const userStore = useUserStore()

  // 获取指令参数
  const value = binding.value

  if (!value) {
    // 没有指定权限要求，默认显示
    return
  }

  let hasPermission = false

  if (typeof value === 'string') {
    // 单个权限检查
    hasPermission = userStore.hasPermission(value)
  } else if (Array.isArray(value)) {
    // 权限数组检查（任意一个）
    hasPermission = userStore.hasAnyPermission(value)
  } else if (typeof value === 'object') {
    const { permissions, mode = 'any' } = value
    if (!permissions || !Array.isArray(permissions)) {
      return
    }

    if (mode === 'all') {
      // 需要所有权限
      hasPermission = userStore.hasAllPermissions(permissions)
    } else {
      // 需要任意一个权限（默认）
      hasPermission = userStore.hasAnyPermission(permissions)
    }
  }

  // 根据权限检查结果显示或隐藏元素
  if (!hasPermission) {
    // 移除元素
    el.style.display = 'none'
    // 或者完全移除DOM元素
    // el.parentNode?.removeChild(el)
  } else {
    el.style.display = ''
  }
}

/**
 * 角色指令 v-role
 * 用法：
 * v-role="'admin'"                    - 需要特定角色
 * v-role="['admin', 'teacher']"       - 需要任意一个角色
 * :v-role="{roles: ['admin'], mode: 'all'}" - 需要所有角色
 */
export const roleDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    checkRole(el, binding)
  },
  updated(el: HTMLElement, binding: DirectiveBinding) {
    checkRole(el, binding)
  }
}

function checkRole(el: HTMLElement, binding: DirectiveBinding) {
  const userStore = useUserStore()
  const userRoles = userStore.roles || []

  // 获取指令参数
  const value = binding.value

  if (!value) {
    // 没有指定角色要求，默认显示
    return
  }

  let hasRole = false

  if (typeof value === 'string') {
    // 单个角色检查
    hasRole = userRoles.includes(value)
  } else if (Array.isArray(value)) {
    // 角色数组检查（任意一个）
    hasRole = userRoles.some(role => value.includes(role))
  } else if (typeof value === 'object') {
    const { roles, mode = 'any' } = value
    if (!roles || !Array.isArray(roles)) {
      return
    }

    if (mode === 'all') {
      // 需要所有角色
      hasRole = roles.every(role => userRoles.includes(role))
    } else {
      // 需要任意一个角色（默认）
      hasRole = userRoles.some(role => roles.includes(role))
    }
  }

  // 根据角色检查结果显示或隐藏元素
  if (!hasRole) {
    // 移除元素
    el.style.display = 'none'
    // 或者完全移除DOM元素
    // el.parentNode?.removeChild(el)
  } else {
    el.style.display = ''
  }
}

/**
 * 注册权限指令
 */
export function setupPermissionDirective(app: App) {
  app.directive('permission', permissionDirective)
  app.directive('role', roleDirective)
}

// 权限检查工具函数
export const permissionUtils = {
  // 检查是否有权限
  hasPermission: (permission: string) => {
    const userStore = useUserStore()
    return userStore.hasPermission(permission)
  },

  // 检查是否有任意权限
  hasAnyPermission: (permissions: string[]) => {
    const userStore = useUserStore()
    return userStore.hasAnyPermission(permissions)
  },

  // 检查是否有所有权限
  hasAllPermissions: (permissions: string[]) => {
    const userStore = useUserStore()
    return userStore.hasAllPermissions(permissions)
  },

  // 检查是否有角色
  hasRole: (role: string) => {
    const userStore = useUserStore()
    return userStore.roles?.includes(role) || false
  },

  // 检查是否有任意角色
  hasAnyRole: (roles: string[]) => {
    const userStore = useUserStore()
    return userStore.roles?.some(role => roles.includes(role)) || false
  },

  // 检查是否为管理员
  isAdmin: () => {
    const userStore = useUserStore()
    return userStore.isAdmin
  },

  // 检查是否为教师
  isTeacher: () => {
    const userStore = useUserStore()
    return userStore.isTeacher
  },

  // 检查是否为学生
  isStudent: () => {
    const userStore = useUserStore()
    return userStore.isStudent
  }
}