import { request } from './request'

export interface ImportPreviewData {
  total_rows: number
  valid_rows: number
  error_count: number
  errors: string[]
  preview_data: any[]
  schema: {
    fields: string[]
    required: string[]
  }
}

export interface ImportResult {
  total_rows: number
  success_count: number
  error_count: number
  errors: string[]
}

export interface ExportConfig {
  type: string
  format: 'xlsx' | 'csv' | 'json'
  filters?: Record<string, any>
  fields?: string[]
}

export interface ImportTemplate {
  schema: {
    fields: string[]
    required: string[]
  }
  example: Record<string, any>
  description: string
}

export interface ImportData {
  type: string
  data: Record<string, any>[]
}

export const dataImportExportApi = {
  // 预览导入数据
  previewImport: (data: ImportData) =>
    request.post<ImportPreviewData>('/data-import-export/import/preview', data),

  // 执行数据导入
  executeImport: (data: ImportData) =>
    request.post<ImportResult>('/data-import-export/import/execute', data),

  // 导出数据
  exportData: (config: ExportConfig) => {
    return request.post('/data-import-export/export', config, {
      responseType: 'blob'
    })
  },

  // 获取导入模板
  getTemplates: () =>
    request.get<Record<string, ImportTemplate>>('/data-import-export/templates')
}