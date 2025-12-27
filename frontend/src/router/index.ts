import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/SimpleLogin.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue')
  },
  {
    path: '/',
    component: () => import('@/SimpleApp.vue'),
    children: [
      // 管理员路由
      {
        path: '/dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          roles: ['admin']
        }
      },
      {
        path: '/profile',
        name: 'AdminProfile',
        component: () => import('@/views/user/TestProfile.vue'),
        meta: {
          title: '个人资料',
          roles: ['admin']
        }
      },
      {
        path: '/students',
        name: 'Students',
        component: () => import('@/views/StudentManagement.vue'),
        meta: {
          roles: ['admin']
        }
      },
      {
        path: '/teachers',
        name: 'Teachers',
        component: () => import('@/views/TeacherManagement.vue'),
        meta: {
          roles: ['admin']
        }
      },
      {
        path: '/courses',
        name: 'Courses',
        component: () => import('@/views/CourseManagement.vue'),
        meta: {
          roles: ['admin']
        }
      },
      {
        path: '/grades',
        name: 'GradeManagement',
        component: () => import('@/views/GradeManagement.vue'),
        meta: {
          title: '成绩管理',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: '/system-settings',
        name: 'SystemSettings',
        component: () => import('@/views/admin/SimpleSystemSettings.vue'),
        meta: {
          title: '系统设置',
          roles: ['admin']
        }
      },

      // 教师路由
      {
        path: '/teacher/dashboard',
        name: 'TeacherDashboard',
        component: () => import('@/views/user/TeacherDashboard.vue'),
        meta: {
          roles: ['teacher']
        }
      },
      {
        path: '/teacher/profile',
        name: 'TeacherProfile',
        component: () => import('@/views/user/Profile.vue'),
        meta: {
          title: '个人资料',
          roles: ['teacher']
        }
      },
      {
        path: '/teacher/courses',
        name: 'TeacherCourses',
        component: () => import('@/views/CourseManagement.vue'),
        meta: {
          title: '课程管理',
          roles: ['teacher']
        }
      },
      {
        path: '/teacher/grades',
        name: 'TeacherGrades',
        component: () => import('@/views/GradeManagement.vue'),
        meta: {
          title: '成绩管理',
          roles: ['teacher']
        }
      },

      // 学生路由
      {
        path: '/student/dashboard',
        name: 'StudentDashboard',
        component: () => import('@/views/user/StudentDashboard.vue'),
        meta: {
          roles: ['student']
        }
      },
      {
        path: '/student/profile',
        name: 'StudentProfile',
        component: () => import('@/views/user/Profile.vue'),
        meta: {
          title: '个人资料',
          roles: ['student']
        }
      },
      {
        path: '/student/courses',
        name: 'StudentCourses',
        component: () => import('@/views/CourseManagement.vue'),
        meta: {
          title: '我的课程',
          roles: ['student']
        }
      },
      {
        path: '/student/grades',
        name: 'StudentGrades',
        component: () => import('@/views/StudentGradeView.vue'),
        meta: {
          title: '我的成绩',
          roles: ['student']
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 权限控制
router.beforeEach((to, from, next) => {
  console.log('路由守卫开始:', to.path)

  // 如果是登录或注册页面，直接放行
  if (to.path === '/login' || to.path === '/register') {
    next()
    return
  }

  // 获取用户信息
  const userStore = useUserStore()
  userStore.initUserInfo()

  const isAuthenticated = userStore.isAuthenticated
  const userRoles = userStore.roles || []

  console.log('路由守卫检查:', {
    path: to.path,
    isAuthenticated,
    userRoles,
    token: !!userStore.token
  })

  // 如果未登录，重定向到登录页
  if (!isAuthenticated) {
    next('/login')
    return
  }

  // 检查角色权限
  const requiredRoles = to.meta?.roles as string[]
  if (requiredRoles && requiredRoles.length > 0) {
    const hasPermission = requiredRoles.some(role => userRoles.includes(role))
    if (!hasPermission) {
      console.log('无权限，用户角色:', userRoles, '需要角色:', requiredRoles)
      // 重定向到对应的仪表板
      if (userRoles.includes('admin')) {
        next('/dashboard')
      } else if (userRoles.includes('teacher')) {
        next('/teacher/dashboard')
      } else if (userRoles.includes('student')) {
        next('/student/dashboard')
      } else {
        next('/login')
      }
      return
    }
  }

  next()
})

// 根据角色获取对应的仪表板路径
function getDashboardPath(roles: string[]): string {
  if (roles.includes('admin')) {
    return '/dashboard'
  } else if (roles.includes('teacher')) {
    return '/teacher/dashboard'
  } else if (roles.includes('student')) {
    return '/student/dashboard'
  } else {
    return '/dashboard' // 默认
  }
}

export default router