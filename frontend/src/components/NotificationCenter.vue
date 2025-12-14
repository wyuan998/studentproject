<template>
  <div class="notification-center">
    <!-- 通知按钮 -->
    <el-popover
      placement="bottom-end"
      :width="400"
      trigger="click"
      popper-class="notification-popover"
      @show="loadNotifications"
    >
      <template #reference>
        <el-badge :value="unreadCount" :hidden="unreadCount === 0">
          <el-button
            class="notification-btn"
            :class="{ active: popoverVisible }"
            circle
            @click="popoverVisible = !popoverVisible"
          >
            <el-icon size="18">
              <Bell />
            </el-icon>
          </el-button>
        </el-badge>
      </template>

      <div class="notification-content">
        <!-- 头部 -->
        <div class="notification-header">
          <h3>消息通知</h3>
          <div class="header-actions">
            <el-button
              text
              type="primary"
              @click="markAllAsRead"
              :disabled="!unreadCount"
            >
              全部已读
            </el-button>
            <el-button
              text
              @click="showAllNotifications"
            >
              查看全部
            </el-button>
          </div>
        </div>

        <!-- 标签页 -->
        <el-tabs v-model="activeTab" class="notification-tabs">
          <!-- 未读消息 -->
          <el-tab-pane name="unread" :label="`未读 (${unreadCount})`">
            <div class="notification-list">
              <div
                v-if="unreadMessages.length === 0"
                class="empty-state"
              >
                <el-empty description="暂无未读消息" />
              </div>
              <template v-else>
                <div
                  v-for="message in unreadMessages"
                  :key="message.id"
                  class="notification-item unread"
                  @click="handleMessageClick(message)"
                >
                  <div class="notification-icon">
                    <el-icon :class="getMessageIconClass(message.type)">
                      <component :is="getMessageIcon(message.type)" />
                    </el-icon>
                  </div>
                  <div class="notification-content">
                    <div class="notification-title">
                      {{ message.title }}
                    </div>
                    <div class="notification-text">
                      {{ message.content }}
                    </div>
                    <div class="notification-time">
                      {{ formatTime(message.created_at) }}
                    </div>
                  </div>
                  <div class="notification-actions">
                    <el-button
                      text
                      type="primary"
                      size="small"
                      @click.stop="markAsRead(message.id)"
                    >
                      标记已读
                    </el-button>
                  </div>
                </div>
              </template>
            </div>
          </el-tab-pane>

          <!-- 已读消息 -->
          <el-tab-pane name="read" label="已读">
            <div class="notification-list">
              <div
                v-if="readMessages.length === 0"
                class="empty-state"
              >
                <el-empty description="暂无已读消息" />
              </div>
              <template v-else>
                <div
                  v-for="message in readMessages.slice(0, 5)"
                  :key="message.id"
                  class="notification-item"
                  @click="handleMessageClick(message)"
                >
                  <div class="notification-icon read">
                    <el-icon :class="getMessageIconClass(message.type)">
                      <component :is="getMessageIcon(message.type)" />
                    </el-icon>
                  </div>
                  <div class="notification-content">
                    <div class="notification-title">
                      {{ message.title }}
                    </div>
                    <div class="notification-text">
                      {{ message.content }}
                    </div>
                    <div class="notification-time">
                      {{ formatTime(message.created_at) }}
                    </div>
                  </div>
                </div>
                <div v-if="readMessages.length > 5" class="load-more">
                  <el-button text type="primary" @click="showAllNotifications">
                    查看更多
                  </el-button>
                </div>
              </template>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-popover>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="showMessageDetail"
      title="消息详情"
      width="500px"
      @closed="selectedMessage = null"
    >
      <div v-if="selectedMessage" class="message-detail">
        <div class="message-header">
          <div class="message-type">
            <el-icon :class="getMessageIconClass(selectedMessage.type)">
              <component :is="getMessageIcon(selectedMessage.type)" />
            </el-icon>
            <span class="type-label">{{ getMessageTypeLabel(selectedMessage.type) }}</span>
          </div>
          <div class="message-time">
            {{ formatTime(selectedMessage.created_at) }}
          </div>
        </div>

        <div class="message-body">
          <h4>{{ selectedMessage.title }}</h4>
          <p>{{ selectedMessage.content }}</p>
        </div>

        <div class="message-footer">
          <el-button
            v-if="!selectedMessage.is_read"
            type="primary"
            @click="markAsRead(selectedMessage.id)"
          >
            标记已读
          </el-button>
          <el-button
            @click="archiveMessage(selectedMessage.id)"
          >
            归档
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Bell,
  InfoFilled,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'
import { notificationsApi } from '@/api/notifications'
import type { Message } from '@/api/notifications'

const router = useRouter()

// 响应式数据
const popoverVisible = ref(false)
const activeTab = ref('unread')
const showMessageDetail = ref(false)
const selectedMessage = ref<Message | null>(null)

const messages = ref<Message[]>([])
const unreadCount = ref(0)
const loading = ref(false)

// 计算属性
const unreadMessages = computed(() =>
  messages.value.filter(msg => !msg.is_read && !msg.is_archived)
)

const readMessages = computed(() =>
  messages.value.filter(msg => msg.is_read && !msg.is_archived)
)

// 方法
const loadNotifications = async () => {
  if (loading.value) return

  try {
    loading.value = true

    // 加载未读消息
    const [messagesResponse, countResponse] = await Promise.all([
      notificationsApi.getMessages({ per_page: 20 }),
      notificationsApi.getUnreadCount()
    ])

    if (messagesResponse.success) {
      messages.value = messagesResponse.data.messages
    }

    if (countResponse.success) {
      unreadCount.value = countResponse.data.unread_count
    }

  } catch (error) {
    console.error('加载通知失败:', error)
  } finally {
    loading.value = false
  }
}

const refreshUnreadCount = async () => {
  try {
    const response = await notificationsApi.getUnreadCount()
    if (response.success) {
      unreadCount.value = response.data.unread_count
    }
  } catch (error) {
    console.error('刷新未读数量失败:', error)
  }
}

const handleMessageClick = (message: Message) => {
  selectedMessage.value = message
  showMessageDetail.value = true
  popoverVisible.value = false

  // 自动标记为已读
  if (!message.is_read) {
    markAsRead(message.id)
  }
}

const markAsRead = async (messageId: number) => {
  try {
    await notificationsApi.updateMessage(messageId, { read: true })

    // 更新本地状态
    const message = messages.value.find(msg => msg.id === messageId)
    if (message) {
      message.is_read = true
      message.read_at = new Date().toISOString()
    }

    // 更新未读数量
    refreshUnreadCount()

    ElMessage.success('已标记为已读')
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const markAllAsRead = async () => {
  try {
    await notificationsApi.markAllAsRead()

    // 更新本地状态
    messages.value.forEach(message => {
      message.is_read = true
      message.read_at = new Date().toISOString()
    })

    unreadCount.value = 0
    ElMessage.success('所有消息已标记为已读')
  } catch (error) {
    console.error('标记所有已读失败:', error)
  }
}

const archiveMessage = async (messageId: number) => {
  try {
    await notificationsApi.updateMessage(messageId, { archived: true })

    // 从列表中移除
    const index = messages.value.findIndex(msg => msg.id === messageId)
    if (index > -1) {
      messages.value.splice(index, 1)
    }

    showMessageDetail.value = false
    ElMessage.success('消息已归档')
  } catch (error) {
    console.error('归档消息失败:', error)
  }
}

const showAllNotifications = () => {
  popoverVisible.value = false
  router.push('/notifications')
}

const getMessageIcon = (type: string) => {
  const iconMap = {
    info: InfoFilled,
    success: SuccessFilled,
    warning: WarningFilled,
    error: CircleCloseFilled
  }
  return iconMap[type as keyof typeof iconMap] || InfoFilled
}

const getMessageIconClass = (type: string) => {
  const classMap = {
    info: 'info-icon',
    success: 'success-icon',
    warning: 'warning-icon',
    error: 'error-icon'
  }
  return classMap[type as keyof typeof classMap] || 'info-icon'
}

const getMessageTypeLabel = (type: string) => {
  const labelMap = {
    info: '信息',
    success: '成功',
    warning: '警告',
    error: '错误'
  }
  return labelMap[type as keyof typeof labelMap] || '信息'
}

const formatTime = (timeStr: string) => {
  const time = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - time.getTime()

  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }

  // 小于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  }

  // 小于24小时
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }

  // 超过24小时显示具体日期
  return time.toLocaleDateString('zh-CN')
}

// 定时刷新
let refreshTimer: number

onMounted(() => {
  // 初始加载未读数量
  refreshUnreadCount()

  // 每30秒刷新一次未读数量
  refreshTimer = window.setInterval(() => {
    refreshUnreadCount()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style lang="scss" scoped>
.notification-center {
  .notification-btn {
    background-color: transparent;
    border: none;
    color: var(--el-text-color-primary);
    transition: all 0.3s;

    &:hover,
    &.active {
      color: var(--el-color-primary);
      background-color: var(--el-color-primary-light-9);
    }
  }
}

:deep(.notification-popover) {
  padding: 0;

  .notification-content {
    min-height: 400px;

    .notification-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 16px 8px;
      border-bottom: 1px solid var(--el-border-color-light);

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      .header-actions {
        display: flex;
        gap: 8px;
      }
    }

    .notification-tabs {
      .notification-list {
        max-height: 350px;
        overflow-y: auto;

        .empty-state {
          padding: 40px 20px;
          text-align: center;
        }

        .notification-item {
          display: flex;
          align-items: flex-start;
          padding: 12px 16px;
          cursor: pointer;
          transition: background-color 0.2s;

          &:hover {
            background-color: var(--el-fill-color-light);
          }

          &.unread {
            background-color: var(--el-color-primary-light-9);
            border-left: 3px solid var(--el-color-primary);
          }

          .notification-icon {
            flex-shrink: 0;
            margin-right: 12px;
            margin-top: 2px;

            .el-icon {
              font-size: 18px;

              &.info-icon {
                color: var(--el-color-info);
              }

              &.success-icon {
                color: var(--el-color-success);
              }

              &.warning-icon {
                color: var(--el-color-warning);
              }

              &.error-icon {
                color: var(--el-color-danger);
              }

              &.read {
                color: var(--el-text-color-placeholder);
              }
            }
          }

          .notification-content {
            flex: 1;
            min-width: 0;

            .notification-title {
              font-weight: 600;
              margin-bottom: 4px;
              font-size: 14px;
              color: var(--el-text-color-primary);
            }

            .notification-text {
              color: var(--el-text-color-regular);
              font-size: 13px;
              line-height: 1.4;
              margin-bottom: 4px;
              display: -webkit-box;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
              overflow: hidden;
            }

            .notification-time {
              color: var(--el-text-color-secondary);
              font-size: 12px;
            }
          }

          .notification-actions {
            flex-shrink: 0;
            margin-left: 8px;
          }
        }

        .load-more {
          padding: 12px;
          text-align: center;
        }
      }
    }
  }
}

.message-detail {
  .message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .message-type {
      display: flex;
      align-items: center;
      gap: 8px;

      .type-label {
        font-weight: 600;
      }
    }

    .message-time {
      color: var(--el-text-color-secondary);
      font-size: 14px;
    }
  }

  .message-body {
    margin-bottom: 20px;

    h4 {
      margin-bottom: 12px;
      color: var(--el-text-color-primary);
    }

    p {
      line-height: 1.6;
      color: var(--el-text-color-regular);
    }
  }

  .message-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>