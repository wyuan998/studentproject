import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/SimpleLogin.vue')
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