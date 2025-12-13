import request from './request'

// 消息接口类型定义
export interface Message {
  id: number
  sender_id: number
  sender_name: string
  recipient_id?: number
  recipient_name?: string
  recipient_type: 'user' | 'role' | 'all'
  recipient_role?: string
  title: string
  content: string
  type: 'system' | 'notice' | 'announcement' | 'reminder' | 'private'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  status: 'draft' | 'sent' | 'read' | 'archived'
  send_at?: string
  read_at?: string
  archived_at?: string
  attachments?: MessageAttachment[]
  created_at: string
  updated_at: string
}

export interface MessageAttachment {
  id: number
  filename: string
  original_name: string
  file_path: string
  file_size: number
  mime_type: string
}

export interface MessageListParams {
  page?: number
  size?: number
  keyword?: string
  type?: string
  priority?: string
  status?: string
  sender_id?: number
  recipient_type?: string
  start_date?: string
  end_date?: string
}

export interface MessageListResponse {
  items: Message[]
  total: number
  page: number
  size: number
  pages: number
  unread_count: number
}

export interface MessageCreateParams {
  recipient_type: 'user' | 'role' | 'all'
  recipient_id?: number
  recipient_role?: string
  title: string
  content: string
  type: 'system' | 'notice' | 'announcement' | 'reminder' | 'private'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  send_at?: string
  attachments?: File[]
}

export interface MessageTemplate {
  id: number
  name: string
  title: string
  content: string
  type: 'system' | 'notice' | 'announcement' | 'reminder' | 'private'
  variables: string[]
  created_at: string
  updated_at: string
}

// API 方法
/**
 * 获取消息列表
 */
export function getMessageList(params: MessageListParams) {
  return request<MessageListResponse>({
    url: '/messages',
    method: 'get',
    params
  })
}

/**
 * 获取消息详情
 */
export function getMessageDetail(id: number) {
  return request<Message>({
    url: `/messages/${id}`,
    method: 'get'
  })
}

/**
 * 发送消息
 */
export function createMessage(data: MessageCreateParams) {
  const formData = new FormData()

  Object.keys(data).forEach(key => {
    if (key === 'attachments') {
      data.attachments?.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file)
      })
    } else if (data[key as keyof MessageCreateParams] !== undefined) {
      formData.append(key, String(data[key as keyof MessageCreateParams]))
    }
  })

  return request<Message>({
    url: '/messages',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 标记消息为已读
 */
export function markMessageAsRead(id: number) {
  return request({
    url: `/messages/${id}/read`,
    method: 'post'
  })
}

/**
 * 批量标记消息为已读
 */
export function batchMarkMessagesAsRead(ids: number[]) {
  return request({
    url: '/messages/batch-read',
    method: 'post',
    data: { ids }
  })
}

/**
 * 归档消息
 */
export function archiveMessage(id: number) {
  return request({
    url: `/messages/${id}/archive`,
    method: 'post'
  })
}

/**
 * 批量归档消息
 */
export function batchArchiveMessages(ids: number[]) {
  return request({
    url: '/messages/batch-archive',
    method: 'post',
    data: { ids }
  })
}

/**
 * 删除消息
 */
export function deleteMessage(id: number) {
  return request({
    url: `/messages/${id}`,
    method: 'delete'
  })
}

/**
 * 获取未读消息数量
 */
export function getUnreadMessageCount() {
  return request({
    url: '/messages/unread-count',
    method: 'get'
  })
}

/**
 * 获取消息模板列表
 */
export function getMessageTemplates(params?: { type?: string }) {
  return request<MessageTemplate[]>({
    url: '/message-templates',
    method: 'get',
    params
  })
}

/**
 * 创建消息模板
 */
export function createMessageTemplate(data: {
  name: string
  title: string
  content: string
  type: 'system' | 'notice' | 'announcement' | 'reminder' | 'private'
  variables: string[]
}) {
  return request<MessageTemplate>({
    url: '/message-templates',
    method: 'post',
    data
  })
}

/**
 * 更新消息模板
 */
export function updateMessageTemplate(id: number, data: Partial<MessageTemplate>) {
  return request<MessageTemplate>({
    url: `/message-templates/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除消息模板
 */
export function deleteMessageTemplate(id: number) {
  return request({
    url: `/message-templates/${id}`,
    method: 'delete'
  })
}

/**
 * 使用消息模板
 */
export function useMessageTemplate(templateId: number, variables: Record<string, string>) {
  return request({
    url: `/message-templates/${templateId}/use`,
    method: 'post',
    data: { variables }
  })
}

/**
 * 下载消息附件
 */
export function downloadMessageAttachment(attachmentId: number) {
  return request({
    url: `/message-attachments/${attachmentId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 发送系统公告
 */
export function sendSystemAnnouncement(data: {
  title: string
  content: string
  priority: 'low' | 'normal' | 'high' | 'urgent'
  send_at?: string
  attachments?: File[]
}) {
  return createMessage({
    ...data,
    recipient_type: 'all',
    type: 'announcement'
  })
}

/**
 * 发送角色消息
 */
export function sendRoleMessage(role: string, data: {
  title: string
  content: string
  type: 'system' | 'notice' | 'reminder'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  send_at?: string
  attachments?: File[]
}) {
  return createMessage({
    ...data,
    recipient_type: 'role',
    recipient_role: role
  })
}