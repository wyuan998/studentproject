// 导出所有类型定义
export * from './auth'
export * from './user'

// 通用类型定义
export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
  code?: number
  errors?: Record<string, string[]>
}

export interface PaginationParams {
  page?: number
  per_page?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface PaginatedData<T = any> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
  has_next: boolean
  has_prev: boolean
  next_page?: number
  prev_page?: number
}

export interface FileUploadResponse {
  url: string
  filename: string
  size: number
  type: string
}

export interface SelectOption {
  label: string
  value: any
  disabled?: boolean
  children?: SelectOption[]
}

export interface TableColumn {
  prop: string
  label: string
  width?: string | number
  minWidth?: string | number
  fixed?: boolean | 'left' | 'right'
  sortable?: boolean | 'custom'
  align?: 'left' | 'center' | 'right'
  resizable?: boolean
  formatter?: (row: any, column: any, cellValue: any) => string
  className?: string
  labelClassName?: string
}

export interface FormRule {
  required?: boolean
  message?: string
  trigger?: 'blur' | 'change' | ['blur', 'change']
  min?: number
  max?: number
  len?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
  type?: 'string' | 'number' | 'boolean' | 'method' | 'regexp' | 'integer' | 'float' | 'array' | 'object' | 'enum' | 'date' | 'url' | 'hex' | 'email'
}

export interface FormRules {
  [key: string]: FormRule | FormRule[]
}

// 状态类型
export type Status = 'active' | 'inactive' | 'pending' | 'completed' | 'cancelled' | 'locked' | 'suspended' | 'withdrawn' | 'graduated' | 'retired'
export type Gender = 'male' | 'female' | 'other'

// 操作类型
export type Action = 'create' | 'read' | 'update' | 'delete' | 'list' | 'export' | 'import'

// 文件类型
export type FileType = 'image' | 'document' | 'video' | 'audio' | 'archive' | 'other'

// 排序类型
export type SortOrder = 'asc' | 'desc'

// 设备类型
export type DeviceType = 'desktop' | 'mobile' | 'tablet'

// 主题类型
export type Theme = 'light' | 'dark'

// 语言类型
export type Language = 'zh-CN' | 'en-US'

// 日志级别
export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'fatal'

// 消息类型
export type MessageType = 'info' | 'success' | 'warning' | 'error'

// 按钮类型
export type ButtonType = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text' | 'default'

// 输入框类型
export type InputType = 'text' | 'password' | 'email' | 'tel' | 'url' | 'number' | 'textarea'

// 日期类型
export type DateType = 'date' | 'datetime' | 'time' | 'week' | 'month' | 'year' | 'dates' | 'daterange' | 'monthrange' | 'datetimerange'

// 颜色类型
export type ColorType = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'

// 尺寸类型
export type Size = 'large' | 'default' | 'small' | 'mini'

// 位置类型
export type Position = 'top' | 'top-start' | 'top-end' | 'bottom' | 'bottom-start' | 'bottom-end' | 'left' | 'left-start' | 'left-end' | 'right' | 'right-start' | 'right-end'