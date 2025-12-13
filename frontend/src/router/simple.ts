import { createRouter, createWebHistory } from 'vue-router'
import SimpleApp from '../SimpleApp.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: () => import('../views/auth/SimpleLogin.vue'),
    meta: {
      showLayout: false
    }
  },
  {
    path: '/dashboard',
    component: SimpleApp
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 简单的路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

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