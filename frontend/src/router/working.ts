import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import SimpleApp from '../SimpleApp.vue'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: () => import('../views/auth/SimpleLogin.vue'),
    meta: {
      title: '登录',
      showLayout: false
    }
  },
  {
    path: '/',
    component: SimpleApp,
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    component: SimpleApp,
    children: [
      {
        path: '',
        component: () => import('../views/Dashboard.vue'),
        meta: {
          title: '仪表板'
        }
      }
    ]
  },
  // 学生管理
  {
    path: '/students',
    component: SimpleApp,
    children: [
      {
        path: '',
        component: () => import('../views/StudentManagement.vue'),
        meta: {
          title: '学生管理'
        }
      }
    ]
  },
  // 教师管理
  {
    path: '/teachers',
    component: SimpleApp,
    children: [
      {
        path: '',
        component: () => import('../views/TeacherManagement.vue'),
        meta: {
          title: '教师管理'
        }
      }
    ]
  },
  // 课程管理
  {
    path: '/courses',
    component: SimpleApp,
    children: [
      {
        path: '',
        component: () => import('../views/CourseManagement.vue'),
        meta: {
          title: '课程管理'
        }
      }
    ]
  },
  // 成绩管理
  {
    path: '/grades',
    component: SimpleApp,
    children: [
      {
        path: '',
        component: () => import('../views/GradeManagement.vue'),
        meta: {
          title: '成绩管理'
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 学生信息管理系统`
  }

  if (to.path === '/login') {
    if (token) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    if (token) {
      next()
    } else {
      next('/login')
    }
  }
})

export default router