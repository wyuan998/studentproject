<template>
  <el-drawer
    v-model="visible"
    title="消息通知"
    size="400px"
    direction="rtl"
    class="notification-drawer"
  >
    <template #header>
      <div class="drawer-header">
        <h3>消息通知</h3>
        <el-button
          v-if="notifications.length > 0"
          text
          size="small"
          @click="markAllAsRead"
        >
          全部标记为已读
        </el-button>
      </div>
    </template>

    <div class="notification-content">
      <el-tabs v-model="activeTab" class="notification-tabs">
        <el-tab-pane label="全部" name="all">
          <div v-if="notifications.length === 0" class="empty-state">
            <el-empty description="暂无消息" :image-size="80" />
          </div>
          <div v-else class="notification-list">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
              :class="{ unread: !notification.is_read }"
              @click="handleNotificationClick(notification)"
            >
              <div class="notification-icon">
                <el-icon :color="getNotificationColor(notification.type)">
                  <component :is="getNotificationIcon(notification.type)" />
                </el-icon>
              </div>
              <div class="notification-body">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-content-text">{{ notification.content }}</div>
                <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
              </div>
              <div class="notification-actions">
                <el-dropdown trigger="click" @command="(command) => handleCommand(command, notification)">
                  <el-button text size="small">
                    <el-icon>
                      <MoreFilled />
                    </el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                        v-if="!notification.is_read"
                        command="markAsRead"
                      >
                        标记为已读
                      </el-dropdown-item>
                      <el-dropdown-item
                        v-if="notification.is_read"
                        command="markAsUnread"
                      >
                        标记为未读
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="未读" name="unread">
          <div v-if="unreadNotifications.length === 0" class="empty-state">
            <el-empty description="暂无未读消息" :image-size="80" />
          </div>
          <div v-else class="notification-list">
            <div
              v-for="notification in unreadNotifications"
              :key="notification.id"
              class="notification-item unread"
              @click="handleNotificationClick(notification)"
            >
              <div class="notification-icon">
                <el-icon :color="getNotificationColor(notification.type)">
                  <component :is="getNotificationIcon(notification.type)" />
                </el-icon>
              </div>
              <div class="notification-body">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-content-text">{{ notification.content }}</div>
                <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
              </div>
              <div class="notification-actions">
                <el-dropdown trigger="click" @command="(command) => handleCommand(command, notification)">
                  <el-button text size="small">
                    <el-icon>
                      <MoreFilled />
                    </el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="markAsRead">
                        标记为已读
                      </el-dropdown-item>
                      <el-dropdown-item command="delete" divided>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button size="small" @click="loadMore" v-if="hasMore">
          加载更多
        </el-button>
        <el-button size="small" @click="clearAll">
          清空所有
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Bell,
  InfoFilled,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled,
  MoreFilled
} from '@element-plus/icons-vue'

interface Notification {
  id: number
  title: string
  content: string
  type: 'info' | 'success' | 'warning' | 'error'
  is_read: boolean
  created_at: string
  related_id?: number
  related_type?: string
}

interface Props {
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const router = useRouter()

// 响应式数据
const activeTab = ref('all')
const notifications = ref<Notification[]>([])
const loading = ref(false)
const hasMore = ref(false)
const page = ref(1)
const pageSize = 20

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const unreadNotifications = computed(() => {
  return notifications.value.filter(n => !n.is_read)
})

// 方法
const loadNotifications = async (reset = false) => {
  if (loading.value) return

  loading.value = true

  try {
    // 这里应该调用实际的API
    // const response = await messageApi.getNotifications({
    //   page: reset ? 1 : page.value,
    //   per_page: pageSize,
    //   is_read: activeTab.value === 'unread' ? false : undefined
    // })

    // 模拟数据
    const mockNotifications: Notification[] = [
      {
        id: 1,
        title: '选课审核通知',
        content: '您提交的《高等数学》选课申请已通过审核',
        type: 'success',
        is_read: false,
        created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString()
      },
      {
        id: 2,
        title: '成绩发布提醒',
        content: '《数据结构》课程成绩已发布，请及时查看',
        type: 'info',
        is_read: true,
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
      },
      {
        id: 3,
        title: '系统维护通知',
        content: '系统将于今晚22:00-23:00进行维护，期间可能影响正常使用',
        type: 'warning',
        is_read: false,
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString()
      }
    ]

    if (reset) {
      notifications.value = mockNotifications
      page.value = 1
    } else {
      notifications.value.push(...mockNotifications)
    }

    hasMore.value = mockNotifications.length === pageSize
  } catch (error) {
    console.error('Load notifications error:', error)
    ElMessage.error('加载消息失败')
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  page.value++
  await loadNotifications()
}

const markAllAsRead = async () => {
  try {
    // const response = await messageApi.markAllAsRead()
    notifications.value.forEach(n => {
      n.is_read = true
    })
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    console.error('Mark all as read error:', error)
    ElMessage.error('操作失败')
  }
}

const markAsRead = async (notification: Notification) => {
  try {
    // const response = await messageApi.markAsRead(notification.id)
    notification.is_read = true
    ElMessage.success('已标记为已读')
  } catch (error) {
    console.error('Mark as read error:', error)
    ElMessage.error('操作失败')
  }
}

const markAsUnread = async (notification: Notification) => {
  try {
    // const response = await messageApi.markAsUnread(notification.id)
    notification.is_read = false
    ElMessage.success('已标记为未读')
  } catch (error) {
    console.error('Mark as unread error:', error)
    ElMessage.error('操作失败')
  }
}

const deleteNotification = async (notification: Notification) => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // const response = await messageApi.deleteNotification(notification.id)
    const index = notifications.value.findIndex(n => n.id === notification.id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete notification error:', error)
      ElMessage.error('删除失败')
    }
  }
}

const clearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // const response = await messageApi.clearAllNotifications()
    notifications.value = []
    ElMessage.success('已清空所有消息')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Clear all error:', error)
      ElMessage.error('操作失败')
    }
  }
}

const handleNotificationClick = (notification: Notification) => {
  if (!notification.is_read) {
    markAsRead(notification)
  }

  // 根据消息类型跳转到相关页面
  if (notification.related_type && notification.related_id) {
    const routeMap: Record<string, string> = {
      'course': `/courses/detail/${notification.related_id}`,
      'enrollment': `/enrollments/list`,
      'grade': `/grades/list`,
      'message': `/messages/detail/${notification.related_id}`
    }

    const route = routeMap[notification.related_type]
    if (route) {
      router.push(route)
      visible.value = false
    }
  }
}

const handleCommand = (command: string, notification: Notification) => {
  switch (command) {
    case 'markAsRead':
      markAsRead(notification)
      break
    case 'markAsUnread':
      markAsUnread(notification)
      break
    case 'delete':
      deleteNotification(notification)
      break
  }
}

const getNotificationIcon = (type: string) => {
  const iconMap = {
    info: InfoFilled,
    success: SuccessFilled,
    warning: WarningFilled,
    error: CircleCloseFilled
  }
  return iconMap[type as keyof typeof iconMap] || Bell
}

const getNotificationColor = (type: string) => {
  const colorMap = {
    info: '#409eff',
    success: '#67c23a',
    warning: '#e6a23c',
    error: '#f56c6c'
  }
  return colorMap[type as keyof typeof colorMap] || '#909399'
}

const formatTime = (timeStr: string) => {
  const time = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - time.getTime()

  if (diff < 1000 * 60) {
    return '刚刚'
  } else if (diff < 1000 * 60 * 60) {
    return `${Math.floor(diff / (1000 * 60))}分钟前`
  } else if (diff < 1000 * 60 * 60 * 24) {
    return `${Math.floor(diff / (1000 * 60 * 60))}小时前`
  } else if (diff < 1000 * 60 * 60 * 24 * 7) {
    return `${Math.floor(diff / (1000 * 60 * 60 * 24))}天前`
  } else {
    return time.toLocaleDateString()
  }
}

// 监听可见性变化
watch(() => props.visible, (newValue) => {
  if (newValue) {
    loadNotifications(true)
  }
})

onMounted(() => {
  if (props.visible) {
    loadNotifications(true)
  }
})
</script>

<style lang="scss" scoped>
.notification-drawer {
  :deep(.el-drawer__header) {
    padding: 0;
    margin-bottom: 0;
  }

  :deep(.el-drawer__body) {
    padding: 0;
    display: flex;
    flex-direction: column;
  }
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-light);

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
}

.notification-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.notification-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;

  :deep(.el-tabs__content) {
    flex: 1;
    overflow: hidden;
  }

  :deep(.el-tab-pane) {
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 16px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: var(--el-fill-color-light);
    margin: 0 -20px;
    padding: 16px 20px;
  }

  &.unread {
    .notification-title {
      font-weight: 600;
    }

    &::before {
      content: '';
      position: absolute;
      left: 8px;
      top: 20px;
      width: 6px;
      height: 6px;
      background-color: var(--el-color-primary);
      border-radius: 50%;
    }
  }

  position: relative;

  .notification-icon {
    margin-right: 12px;
    margin-top: 2px;
  }

  .notification-body {
    flex: 1;
    min-width: 0;

    .notification-title {
      font-size: 14px;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
      line-height: 1.4;
    }

    .notification-content-text {
      font-size: 13px;
      color: var(--el-text-color-regular);
      margin-bottom: 6px;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
    }

    .notification-time {
      font-size: 12px;
      color: var(--el-text-color-placeholder);
    }
  }

  .notification-actions {
    margin-left: 8px;
  }
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.drawer-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>