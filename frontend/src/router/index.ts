import { createRouter, createWebHistory } from 'vue-router'

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
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue')
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: {
          title: '个人资料'
        }
      },
      {
        path: '/students',
        name: 'Students',
        component: () => import('@/views/StudentManagement.vue')
      },
      {
        path: '/teachers',
        name: 'Teachers',
        component: () => import('@/views/TeacherManagement.vue')
      },
      {
        path: '/courses',
        name: 'Courses',
        component: () => import('@/views/CourseManagement.vue')
      },
      {
        path: '/grades',
        name: 'GradeManagement',
        component: () => import('@/views/GradeManagement.vue'),
        meta: {
          title: '成绩管理'
        }
      },
      {
        path: '/system-settings',
        name: 'SystemSettings',
        component: () => import('@/views/admin/SystemSettings.vue'),
        meta: {
          title: '系统设置'
        }
      },
      {
        path: '/config-management',
        name: 'ConfigManagement',
        component: () => import('@/views/admin/ConfigManagement.vue'),
        meta: {
          title: '配置管理'
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

export default router