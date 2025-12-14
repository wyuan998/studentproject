import { request } from './request'

export interface Message {
  id: number
  sender_id: number
  recipient_id: number
  title: string
  content: string
  type: 'info' | 'warning' | 'error' | 'success'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  is_read: boolean
  is_archived: boolean
  is_deleted: boolean
  read_at?: string
  archived_at?: string
  created_at: string
  updated_at: string
}

export interface MessageCreate {
  title: string
  content: string
  type: 'info' | 'warning' | 'error' | 'success'
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  target_type: 'all' | 'role' | 'users' | 'students' | 'teachers'
  target_ids?: number[]
  scheduled_at?: string
  expires_at?: string
}

export interface MessageListResponse {
  messages: Message[]
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface MessageTemplate {
  id: number
  name: string
  title_template: string
  content_template: string
  type: string
  description: string
  variables: string[]
}

export interface UnreadCount {
  unread_count: number
}

export interface NotificationUpdate {
  read?: boolean
  archived?: boolean
}

export interface BatchAction {
  message_ids: number[]
  action: 'read' | 'unread' | 'archive' | 'delete'
}

export const notificationsApi = {
  // 获取消息列表
  getMessages: (params?: {
    page?: number
    per_page?: number
    type?: string
    status?: 'read' | 'unread' | 'archived'
    priority?: string
  }) =>
    request.get<MessageListResponse>('/notifications/messages', { params }),

  // 创建消息
  createMessage: (data: MessageCreate) =>
    request.post('/notifications/messages', data),

  // 获取消息详情
  getMessage: (messageId: number) =>
    request.get<Message>(`/notifications/messages/${messageId}`),

  // 更新消息状态
  updateMessage: (messageId: number, data: NotificationUpdate) =>
    request.put(`/notifications/messages/${messageId}`, data),

  // 删除消息
  deleteMessage: (messageId: number) =>
    request.delete(`/notifications/messages/${messageId}`),

  // 获取未读消息数量
  getUnreadCount: () =>
    request.get<UnreadCount>('/notifications/unread-count'),

  // 标记所有消息为已读
  markAllAsRead: () =>
    request.post('/notifications/mark-all-read'),

  // 批量操作消息
  batchAction: (data: BatchAction) =>
    request.post('/notifications/batch-action', data),

  // 获取消息模板列表
  getTemplates: () =>
    request.get<MessageTemplate[]>('/notifications/templates'),

  // 预览消息模板
  previewTemplate: (templateId: number, variables: Record<string, any>) =>
    request.post(`/notifications/templates/${templateId}/preview`, { variables })
}