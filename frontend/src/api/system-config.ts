import { request } from './request'

export interface SystemConfigItem {
  id: string
  key: string
  name: string
  description?: string
  category: string
  config_type: string
  value_type: string
  value: any
  display_value: string
  display_type: string
  is_active: boolean
  is_required: boolean
  is_public: boolean
  is_editable: boolean
  requires_restart: boolean
  sort_order: number
  version: string
  last_modified_by?: string
  last_modified_at?: string
  created_at: string
  updated_at: string
}

export interface SystemConfigCreateData {
  key: string
  name: string
  description?: string
  category: string
  config_type: string
  value_type: string
  value: any
  min_value?: number
  max_value?: number
  allowed_values?: any[]
  validation_pattern?: string
  is_active?: boolean
  is_required?: boolean
  is_public?: boolean
  is_editable?: boolean
  requires_restart?: boolean
  version?: string
  change_log?: string
  cache_ttl?: number
  is_cached?: boolean
  sort_order?: number
}

export interface SystemConfigUpdateData {
  name?: string
  description?: string
  category?: string
  value?: any
  min_value?: number
  max_value?: number
  allowed_values?: any[]
  validation_pattern?: string
  is_active?: boolean
  is_required?: boolean
  is_public?: boolean
  is_editable?: boolean
  requires_restart?: boolean
  version?: string
  change_log?: string
  cache_ttl?: number
  is_cached?: boolean
  sort_order?: number
}

export interface SystemConfigSearchParams {
  keyword?: string
  config_type?: string
  category?: string
  is_active?: boolean
  is_public?: boolean
  is_editable?: boolean
  page?: number
  per_page?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface SystemConfigListResponse {
  configs: SystemConfigItem[]
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface SystemConfigCategory {
  category: string
  config_count: number
}

export interface BatchUpdateData {
  configs: Record<string, any>[]
  category?: string
}

export const systemConfigApi = {
  // 获取系统配置列表
  getConfigList: (params?: SystemConfigSearchParams) =>
    request.get<SystemConfigListResponse>('/system-config', { params }),

  // 创建系统配置
  createConfig: (data: SystemConfigCreateData) =>
    request.post<SystemConfigItem>('/system-config', data),

  // 批量更新系统配置
  batchUpdateConfigs: (data: BatchUpdateData) =>
    request.put('/system-config/batch', data),

  // 获取配置分类列表
  getConfigCategories: () =>
    request.get<SystemConfigCategory[]>('/system-config/categories'),

  // 获取公开配置（无需认证）
  getPublicConfigs: () =>
    request.get<Record<string, any>>('/system-config/public'),

  // 导出系统配置
  exportConfigs: (params?: { category?: string; format?: string }) =>
    request.get('/system-config/export', { params }),

  // 获取指定配置详情
  getConfigDetail: (key: string) =>
    request.get<SystemConfigItem>(`/system-config/${key}`),

  // 更新系统配置
  updateConfig: (key: string, data: SystemConfigUpdateData) =>
    request.put<SystemConfigItem>(`/system-config/${key}`, data),

  // 删除系统配置
  deleteConfig: (key: string) =>
    request.delete(`/system-config/${key}`),

  // 清除配置缓存
  clearConfigCache: () =>
    request.post('/system-config/cache/clear')
}