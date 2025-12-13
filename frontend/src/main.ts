import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router/working'
import '@/styles/index.scss'

// 创建应用实例
const app = createApp(App)

// 全局注册ElementPlus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 创建Pinia状态管理
const pinia = createPinia()

// 注册插件
app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  size: 'default'
})

// 挂载路由
app.mount('#app')

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Global Error:', err)
  console.error('Error Info:', info)
}

// 全局警告处理
app.config.warnHandler = (msg, vm, info) => {
  console.warn('Global Warning:', msg)
}

// 简单的应用初始化
const initApp = async () => {
  try {
    console.log('测试应用初始化成功')
  } catch (error) {
    console.error('App initialization error:', error)
  }
}

// 应用启动后初始化
setTimeout(initApp, 100)

export { app, pinia }