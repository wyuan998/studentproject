import { createRouter, createWebHistory } from 'vue-router'
import SimpleApp from '@/SimpleApp.vue'
import WorkingGrades from '@/views/WorkingGrades.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/SimpleLogin.vue')
  },
  {
    path: '/',
    component: SimpleApp,
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue')
      },
      {
        path: '/grades/list',
        name: 'GradeList',
        component: WorkingGrades
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