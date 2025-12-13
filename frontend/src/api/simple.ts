import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  },
  transformRequest: [
    function (data) {
      // 确保JSON数据正确编码
      return JSON.stringify(data)
    }
  ]
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 统一处理响应格式
    if (response.data && typeof response.data === 'object') {
      return response.data
    }
    return {
      success: true,
      data: response.data
    }
  },
  (error) => {
    console.error('API Error:', error)

    let message = '请求失败'
    if (error.response) {
      switch (error.response.status) {
        case 401:
          message = '未授权，请重新登录'
          // 清除 token 并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
          break
        case 403:
          message = '权限不足'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data?.message || '请求失败'
      }
    } else if (error.request) {
      message = '网络连接失败'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request

// 简单的 API 函数
export const api = {
  // 认证相关
  login: (data: { username: string; password: string }) => {
    return request.post('/api/auth/login', data)
  },

  logout: () => {
    return request.post('/api/auth/logout')
  },

  getUserInfo: () => {
    return request.get('/api/auth/user')
  },

  // 学生管理
  getStudents: (params?: any) => {
    return request.get('/api/students', { params })
  },

  createStudent: (data: any) => {
    return request.post('/api/students', data)
  },

  updateStudent: (id: number, data: any) => {
    return request.put(`/api/students/${id}`, data)
  },

  deleteStudent: (id: number) => {
    return request.delete(`/api/students/${id}`)
  },

  // 教师管理
  getTeachers: (params?: any) => {
    return request.get('/api/teachers', { params })
  },

  createTeacher: (data: any) => {
    return request.post('/api/teachers', data)
  },

  updateTeacher: (id: number, data: any) => {
    return request.put(`/api/teachers/${id}`, data)
  },

  deleteTeacher: (id: number) => {
    return request.delete(`/api/teachers/${id}`)
  },

  // 课程管理
  getCourses: (params?: any) => {
    return request.get('/api/courses', { params })
  },

  createCourse: (data: any) => {
    return request.post('/api/courses', data)
  },

  updateCourse: (id: number, data: any) => {
    return request.put(`/api/courses/${id}`, data)
  },

  deleteCourse: (id: number) => {
    return request.delete(`/api/courses/${id}`)
  }
}