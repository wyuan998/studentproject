import request from './request'

// 系统配置接口类型定义
export interface SystemConfig {
  id: number
  key: string
  value: string
  description: string
  type: 'string' | 'number' | 'boolean' | 'json'
  category: string
  editable: boolean
  created_at: string
  updated_at: string
}

export interface SystemLog {
  id: number
  user_id: number
  user_name: string
  action: string
  resource: string
  resource_id?: number
  details?: Record<string, any>
  ip_address: string
  user_agent: string
  created_at: string
}

export interface BackupRecord {
  id: number
  filename: string
  file_path: string
  file_size: number
  type: 'full' | 'incremental'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  description?: string
  created_at: string
  completed_at?: string
}

export interface SystemStatistics {
  users: {
    total: number
    active: number
    students: number
    teachers: number
    admins: number
  }
  courses: {
    total: number
    active: number
    completed: number
  }
  enrollments: {
    total: number
    pending: number
    approved: number
  }
  grades: {
    total: number
    published: number
    draft: number
  }
  system: {
    version: string
    uptime: number
    memory_usage: number
    disk_usage: number
  }
}

// API 方法
/**
 * 获取系统配置
 */
export function getSystemConfig(category?: string) {
  return request<SystemConfig[]>({
    url: '/system-config',
    method: 'get',
    params: { category }
  })
}

/**
 * 更新系统配置
 */
export function updateSystemConfig(data: { key: string; value: string }[]) {
  return request({
    url: '/system-config',
    method: 'put',
    data
  })
}

/**
 * 重置系统配置
 */
export function resetSystemConfig(key: string) {
  return request({
    url: `/system-config/${key}/reset`,
    method: 'post'
  })
}

/**
 * 获取系统日志
 */
export function getSystemLogs(params: {
  page?: number
  size?: number
  user_id?: number
  action?: string
  resource?: string
  start_date?: string
  end_date?: string
}) {
  return request({
    url: '/system-logs',
    method: 'get',
    params
  })
}

/**
 * 清理系统日志
 */
export function cleanSystemLogs(beforeDate: string) {
  return request({
    url: '/system-logs/clean',
    method: 'delete',
    data: { before_date: beforeDate }
  })
}

/**
 * 获取系统统计
 */
export function getSystemStatistics() {
  return request<SystemStatistics>({
    url: '/system-statistics',
    method: 'get'
  })
}

/**
 * 获取备份记录
 */
export function getBackupRecords(params?: { page?: number; size?: number; type?: string }) {
  return request({
    url: '/backups',
    method: 'get',
    params
  })
}

/**
 * 创建系统备份
 */
export function createBackup(data: {
  type: 'full' | 'incremental'
  description?: string
}) {
  return request<BackupRecord>({
    url: '/backups',
    method: 'post',
    data
  })
}

/**
 * 恢复系统备份
 */
export function restoreBackup(backupId: number) {
  return request({
    url: `/backups/${backupId}/restore`,
    method: 'post'
  })
}

/**
 * 下载备份文件
 */
export function downloadBackup(backupId: number) {
  return request({
    url: `/backups/${backupId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 删除备份记录
 */
export function deleteBackup(backupId: number) {
  return request({
    url: `/backups/${backupId}`,
    method: 'delete'
  })
}

/**
 * 健康检查
 */
export function healthCheck() {
  return request({
    url: '/health',
    method: 'get'
  })
}

/**
 * 获取系统信息
 */
export function getSystemInfo() {
  return request({
    url: '/system-info',
    method: 'get'
  })
}

/**
 * 清理缓存
 */
export function clearCache(type?: 'all' | 'config' | 'session' | 'template') {
  return request({
    url: '/cache/clear',
    method: 'post',
    data: { type }
  })
}

/**
 * 发送测试邮件
 */
export function sendTestEmail(email: string) {
  return request({
    url: '/system/test-email',
    method: 'post',
    data: { email }
  })
}

/**
 * 数据库维护
 */
export function databaseMaintenance(action: 'optimize' | 'repair' | 'analyze') {
  return request({
    url: '/database/maintenance',
    method: 'post',
    data: { action }
  })
}

/**
 * 获取在线用户
 */
export function getOnlineUsers() {
  return request({
    url: '/system/online-users',
    method: 'get'
  })
}

/**
 * 强制用户下线
 */
export function forceUserOffline(userId: number) {
  return request({
    url: `/system/users/${userId}/offline`,
    method: 'post'
  })
}