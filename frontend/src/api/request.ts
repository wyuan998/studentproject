import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 请求配置接口
export interface RequestConfig extends AxiosRequestConfig {
  loading?: boolean
  skipErrorHandler?: boolean
  skipAuth?: boolean
}

// 响应数据接口
export interface ResponseData<T = any> {
  success: boolean
  message: string
  data?: T
  code?: number
  errors?: Record<string, string[]>
}

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// loading实例
let loadingInstance: any = null
let loadingCount = 0

// 显示loading
const showLoading = () => {
  if (loadingCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.7)',
      fullscreen: true
    })
  }
  loadingCount++
}

// 隐藏loading
const hideLoading = () => {
  loadingCount--
  if (loadingCount <= 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
    loadingCount = 0
  }
}

// 请求拦截器
service.interceptors.request.use(
  (config: RequestConfig) => {
    // 显示loading
    if (config.loading !== false) {
      showLoading()
    }

    // 添加认证token
    if (!config.skipAuth) {
      const userStore = useUserStore()
      if (userStore.token) {
        config.headers = config.headers || {}
        config.headers['Authorization'] = `Bearer ${userStore.token}`
      }
    }

    // 添加时间戳防止缓存
    if (config.method?.toLowerCase() === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }

    return config
  },
  (error: AxiosError) => {
    hideLoading()
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<ResponseData>) => {
    // 隐藏loading
    const config = response.config as RequestConfig
    if (config.loading !== false) {
      hideLoading()
    }

    const { data } = response

    // 如果响应数据格式不正确，直接返回
    if (!data || typeof data !== 'object') {
      return response
    }

    // 如果是文件下载等特殊响应，直接返回
    if (response.headers['content-type']?.includes('application/octet-stream') ||
        response.headers['content-type']?.includes('application/vnd.openxmlformats-officedocument') ||
        response.headers['content-type']?.includes('application/pdf')) {
      return response
    }

    // 检查业务状态码
    if (data.success === false) {
      const error = new Error(data.message || '请求失败')
      ;(error as any).code = data.code
      ;(error as any).response = response
      ;(error as any).data = data

      if (!config.skipErrorHandler) {
        ElMessage.error(data.message || '请求失败')
      }

      return Promise.reject(error)
    }

    return response
  },
  async (error: AxiosError) => {
    // 隐藏loading
    const config = error.config as RequestConfig
    if (config?.loading !== false) {
      hideLoading()
    }

    const { response, code } = error
    let errorMessage = '网络错误，请稍后重试'

    if (response) {
      const { status, data } = response

      switch (status) {
        case 400:
          errorMessage = (data as ResponseData)?.message || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权，请重新登录'

          // 如果是token过期，尝试刷新token
          const userStore = useUserStore()
          if (userStore.refreshToken && !config?.url?.includes('/refresh')) {
            try {
              await userStore.refreshAccessToken()
              // 重新发送请求
              if (config) {
                return service(config)
              }
            } catch (refreshError) {
              // 刷新失败，跳转到登录页
              userStore.logout()
              router.push('/login')
            }
          } else {
            userStore.logout()
            router.push('/login')
          }
          break
        case 403:
          errorMessage = '权限不足，拒绝访问'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 408:
          errorMessage = '请求超时'
          break
        case 422:
          errorMessage = '数据验证失败'
          // 处理表单验证错误
          if ((data as ResponseData)?.errors) {
            const errors = (data as ResponseData).errors!
            const errorMessages = Object.values(errors).flat()
            errorMessage = errorMessages.join(', ')
          }
          break
        case 429:
          errorMessage = '请求过于频繁，请稍后重试'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        case 502:
          errorMessage = '网关错误'
          break
        case 503:
          errorMessage = '服务不可用'
          break
        case 504:
          errorMessage = '网关超时'
          break
        default:
          errorMessage = (data as ResponseData)?.message || `请求失败 (${status})`
      }
    } else if (code) {
      switch (code) {
        case 'ECONNABORTED':
          errorMessage = '请求超时'
          break
        case 'ERR_NETWORK':
          errorMessage = '网络连接失败'
          break
        case 'ERR_CANCELED':
          errorMessage = '请求已取消'
          break
        default:
          errorMessage = `请求失败: ${code}`
      }
    }

    // 显示错误消息
    if (!config?.skipErrorHandler) {
      ElMessage.error(errorMessage)
    }

    // 增强错误对象
    const enhancedError = new Error(errorMessage)
    Object.assign(enhancedError, {
      config,
      code: response?.status,
      response,
      data: response?.data
    })

    return Promise.reject(enhancedError)
  }
)

// 封装请求方法
export const request = {
  // GET请求
  get<T = any>(url: string, config?: RequestConfig): Promise<AxiosResponse<ResponseData<T>>> {
    return service.get(url, config)
  },

  // POST请求
  post<T = any>(url: string, data?: any, config?: RequestConfig): Promise<AxiosResponse<ResponseData<T>>> {
    return service.post(url, data, config)
  },

  // PUT请求
  put<T = any>(url: string, data?: any, config?: RequestConfig): Promise<AxiosResponse<ResponseData<T>>> {
    return service.put(url, data, config)
  },

  // DELETE请求
  delete<T = any>(url: string, config?: RequestConfig): Promise<AxiosResponse<ResponseData<T>>> {
    return service.delete(url, config)
  },

  // PATCH请求
  patch<T = any>(url: string, data?: any, config?: RequestConfig): Promise<AxiosResponse<ResponseData<T>>> {
    return service.patch(url, data, config)
  },

  // 文件上传
  upload<T = any>(url: string, formData: FormData, config?: RequestConfig): Promise<AxiosResponse<ResponseData<T>>> {
    return service.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers
      }
    })
  },

  // 文件下载
  download(url: string, config?: RequestConfig): Promise<AxiosResponse> {
    return service.get(url, {
      ...config,
      responseType: 'blob'
    })
  }
}

export default service