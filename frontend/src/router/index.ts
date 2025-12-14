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
        path: '/data-management',
        name: 'DataManagement',
        component: () => import('@/views/admin/DataManagement.vue'),
        meta: {
          title: '数据管理'
        }
      },
      {
        path: '/notifications',
        name: 'MessageCenter',
        component: () => import('@/views/admin/MessageCenter.vue'),
        meta: {
          title: '消息中心'
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