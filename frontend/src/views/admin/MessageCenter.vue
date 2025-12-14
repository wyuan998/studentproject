<template>
  <div class="message-center">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">消息中心</span>
      </template>
    </el-page-header>

    <div class="message-container">
      <!-- 搜索和操作栏 -->
      <el-card class="action-card">
        <el-form :model="searchForm" inline>
          <el-form-item label="消息类型">
            <el-select
              v-model="searchForm.type"
              placeholder="选择消息类型"
              style="width: 120px"
              clearable
            >
              <el-option label="全部" value="" />
              <el-option label="信息" value="info" />
              <el-option label="成功" value="success" />
              <el-option label="警告" value="warning" />
              <el-option label="错误" value="error" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="选择状态"
              style="width: 100px"
              clearable
            >
              <el-option label="全部" value="" />
              <el-option label="未读" value="unread" />
              <el-option label="已读" value="read" />
              <el-option label="已归档" value="archived" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select
              v-model="searchForm.priority"
              placeholder="选择优先级"
              style="width: 100px"
              clearable
            >
              <el-option label="全部" value="" />
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>

        <div class="actions">
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            发送消息
          </el-button>
          <el-button @click="markAllRead" :disabled="!unreadCount">
            <el-icon><Check /></el-icon>
            全部已读
          </el-button>
        </div>
      </el-card>

      <!-- 消息列表 -->
      <el-card class="table-card">
        <div class="batch-actions" v-if="selectedMessages.length > 0">
          <el-alert
            :title="`已选择 ${selectedMessages.length} 条消息`"
            type="info"
            :closable="false"
          >
            <template #default>
              <el-button-group>
                <el-button size="small" @click="batchMarkRead">标记已读</el-button-group>
                <el-button-group>
                  <el-button size="small" @click="batchUnread">标记未读</el-button>
                </el-button-group>
                <el-button-group>
                  <el-button size="small" @click="batchArchive">归档</el-button>
                </el-button-group>
                <el-button-group>
                  <el-button size="small" type="danger" @click="batchDelete">删除</el-button>
                </el-button-group>
              </template>
          </el-alert>
        </div>

        <el-table
          :data="messages"
          v-loading="loading"
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column width="60">
            <template #default="{ row }">
              <el-icon :class="getMessageIconClass(row.type)">
                <component :is="getMessageIcon(row.type)" />
              </el-icon>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <div class="message-title" :class="{ unread: !row.is_read }">
                {{ row.title }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
          <el-table-column prop="type" label="类型" width="80">
            <template #default="{ row }">
              <el-tag :type="getMessageTypeTag(row.type)" size="small">
                {{ getMessageTypeLabel(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="80">
            <template #default="{ row }">
              <el-tag
                :type="getPriorityTag(row.priority)"
                size="small"
                v-if="row.priority !== 'medium'"
              >
                {{ getPriorityLabel(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_read" label="状态" width="80">
            <template #default="{ row }">
              <el-tag
                :type="row.is_read ? 'info' : 'success'"
                size="small"
              >
                {{ row.is_read ? '已读' : '未读' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button
                text
                type="primary"
                size="small"
                @click.stop="viewMessage(row)"
              >
                查看
              </el-button>
              <el-dropdown @command="(command) => handleMessageAction(command, row)">
                <el-button text type="primary" size="small">
                  更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-if="!row.is_read"
                      command="read"
                    >
                      标记已读
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="row.is_read"
                      command="unread"
                    >
                      标记未读
                    </el-dropdown-item>
                    <el-dropdown-item command="archive">归档</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSearch"
            @current-change="handleSearch"
          />
        </div>
      </el-card>
    </div>

    <!-- 创建消息对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="发送消息"
      width="600px"
      @closed="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="消息标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入消息标题" />
        </el-form-item>
        <el-form-item label="消息内容" prop="content">
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入消息内容"
          />
        </el-form-item>
        <el-form-item label="消息类型" prop="type">
          <el-select v-model="createForm.type" style="width: 100%">
            <el-option label="信息" value="info" />
            <el-option label="成功" value="success" />
            <el-option label="警告" value="warning" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="createForm.priority" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="发送对象" prop="target_type">
          <el-select
            v-model="createForm.target_type"
            style="width: 100%"
            @change="handleTargetTypeChange"
          >
            <el-option label="所有用户" value="all" />
            <el-option label="按角色" value="role" />
            <el-option label="指定用户" value="users" />
            <el-option label="所有学生" value="students" />
            <el-option label="所有教师" value="teachers" />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="createForm.target_type === 'role'"
          label="选择角色"
        >
          <el-select
            v-model="createForm.target_ids"
            style="width: 100%"
            multiple
            placeholder="选择角色"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划发送">
          <el-date-picker
            v-model="createForm.scheduled_at"
            type="datetime"
            placeholder="选择发送时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker
            v-model="createForm.expires_at"
            type="datetime"
            placeholder="选择过期时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" :loading="createLoading" @click="handleCreateMessage">
            发送
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="消息详情"
      width="600px"
    >
      <div v-if="selectedMessage" class="message-detail">
        <div class="message-header">
          <div class="message-info">
            <h3>{{ selectedMessage.title }}</h3>
            <div class="message-meta">
              <el-tag :type="getMessageTypeTag(selectedMessage.type)">
                {{ getMessageTypeLabel(selectedMessage.type) }}
              </el-tag>
              <el-tag
                v-if="selectedMessage.priority !== 'medium'"
                :type="getPriorityTag(selectedMessage.priority)"
              >
                {{ getPriorityLabel(selectedMessage.priority) }}
              </el-tag>
            </div>
          </div>
          <div class="message-time">
            {{ formatDateTime(selectedMessage.created_at) }}
          </div>
        </div>
        <div class="message-content">
          {{ selectedMessage.content }}
        </div>
        <div class="message-footer">
          <el-tag :type="selectedMessage.is_read ? 'info' : 'success'">
            {{ selectedMessage.is_read ? '已读' : '未读' }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  Plus,
  Check,
  ArrowDown,
  InfoFilled,
  SuccessFilled,
  WarningFilled,
  CircleCloseFilled
} from '@element-plus/icons-vue'
import { notificationsApi } from '@/api/notifications'
import type { Message, MessageCreate } from '@/api/notifications'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const createLoading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const createFormRef = ref<FormInstance>()
const selectedMessage = ref<Message | null>(null)

const messages = ref<Message[]>([])
const selectedMessages = ref<Message[]>([])
const unreadCount = ref(0)

const searchForm = reactive({
  type: '',
  status: '',
  priority: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const createForm = reactive<MessageCreate>({
  title: '',
  content: '',
  type: 'info',
  priority: 'medium',
  target_type: 'all',
  target_ids: [],
  scheduled_at: '',
  expires_at: ''
})

const createRules: FormRules = {
  title: [
    { required: true, message: '请输入消息标题', trigger: 'blur' },
    { min: 1, max: 100, message: '标题长度为1-100个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入消息内容', trigger: 'blur' },
    { min: 1, max: 1000, message: '内容长度为1-1000个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择消息类型', trigger: 'change' }
  ],
  target_type: [
    { required: true, message: '请选择发送对象', trigger: 'change' }
  ]
}

// 方法
const loadMessages = async () => {
  try {
    loading.value = true

    const response = await notificationsApi.getMessages({
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    })

    if (response.success) {
      messages.value = response.data.messages
      pagination.total = response.data.pagination.total
    }
  } catch (error: any) {
    console.error('加载消息列表失败:', error)
    ElMessage.error(error.response?.data?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const loadUnreadCount = async () => {
  try {
    const response = await notificationsApi.getUnreadCount()
    if (response.success) {
      unreadCount.value = response.data.unread_count
    }
  } catch (error) {
    console.error('加载未读数量失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadMessages()
}

const handleReset = () => {
  Object.assign(searchForm, {
    type: '',
    status: '',
    priority: ''
  })
  handleSearch()
}

const handleSelectionChange = (selection: Message[]) => {
  selectedMessages.value = selection
}

const handleRowClick = (row: Message) => {
  viewMessage(row)
}

const handleTargetTypeChange = () => {
  createForm.target_ids = []
}

const viewMessage = async (message: Message) => {
  selectedMessage.value = message
  showDetailDialog.value = true

  // 如果是未读消息，标记为已读
  if (!message.is_read) {
    try {
      await notificationsApi.updateMessage(message.id, { read: true })
      message.is_read = true
      message.read_at = new Date().toISOString()
      loadUnreadCount()
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }
}

const handleMessageAction = async (command: string, message: Message) => {
  switch (command) {
    case 'read':
      await markAsRead(message.id)
      break
    case 'unread':
      await markAsUnread(message.id)
      break
    case 'archive':
      await archiveMessage(message.id)
      break
    case 'delete':
      await deleteMessage(message.id)
      break
  }
}

const markAsRead = async (messageId: number) => {
  try {
    await notificationsApi.updateMessage(messageId, { read: true })
    const message = messages.value.find(msg => msg.id === messageId)
    if (message) {
      message.is_read = true
      message.read_at = new Date().toISOString()
    }
    loadUnreadCount()
    ElMessage.success('已标记为已读')
  } catch (error: any) {
    console.error('标记已读失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const markAsUnread = async (messageId: number) => {
  try {
    await notificationsApi.updateMessage(messageId, { read: false })
    const message = messages.value.find(msg => msg.id === messageId)
    if (message) {
      message.is_read = false
      message.read_at = undefined
    }
    loadUnreadCount()
    ElMessage.success('已标记为未读')
  } catch (error: any) {
    console.error('标记未读失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const archiveMessage = async (messageId: number) => {
  try {
    await notificationsApi.updateMessage(messageId, { archived: true })
    const index = messages.value.findIndex(msg => msg.id === messageId)
    if (index > -1) {
      messages.value.splice(index, 1)
    }
    ElMessage.success('消息已归档')
  } catch (error: any) {
    console.error('归档消息失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const deleteMessage = async (messageId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await notificationsApi.deleteMessage(messageId)
    const index = messages.value.findIndex(msg => msg.id === messageId)
    if (index > -1) {
      messages.value.splice(index, 1)
    }
    ElMessage.success('消息已删除')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除消息失败:', error)
      ElMessage.error(error.response?.data?.message || '操作失败')
    }
  }
}

const batchMarkRead = async () => {
  try {
    const messageIds = selectedMessages.value.map(msg => msg.id)
    await notificationsApi.batchAction({
      message_ids: messageIds,
      action: 'read'
    })

    selectedMessages.value.forEach(message => {
      message.is_read = true
      message.read_at = new Date().toISOString()
    })

    selectedMessages.value = []
    loadUnreadCount()
    ElMessage.success('已标记为已读')
  } catch (error: any) {
    console.error('批量标记已读失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const batchUnread = async () => {
  try {
    const messageIds = selectedMessages.value.map(msg => msg.id)
    await notificationsApi.batchAction({
      message_ids: messageIds,
      action: 'unread'
    })

    selectedMessages.value.forEach(message => {
      message.is_read = false
      message.read_at = undefined
    })

    selectedMessages.value = []
    loadUnreadCount()
    ElMessage.success('已标记为未读')
  } catch (error: any) {
    console.error('批量标记未读失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const batchArchive = async () => {
  try {
    const messageIds = selectedMessages.value.map(msg => msg.id)
    await notificationsApi.batchAction({
      message_ids: messageIds,
      action: 'archive'
    })

    selectedMessages.value.forEach(message => {
      const index = messages.value.findIndex(msg => msg.id === message.id)
      if (index > -1) {
        messages.value.splice(index, 1)
      }
    })

    selectedMessages.value = []
    ElMessage.success('已归档')
  } catch (error: any) {
    console.error('批量归档失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedMessages.value.length} 条消息吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const messageIds = selectedMessages.value.map(msg => msg.id)
    await notificationsApi.batchAction({
      message_ids: messageIds,
      action: 'delete'
    })

    selectedMessages.value.forEach(message => {
      const index = messages.value.findIndex(msg => msg.id === message.id)
      if (index > -1) {
        messages.value.splice(index, 1)
      }
    })

    selectedMessages.value = []
    ElMessage.success('已删除')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error(error.response?.data?.message || '操作失败')
    }
  }
}

const markAllRead = async () => {
  try {
    await notificationsApi.markAllAsRead()
    messages.value.forEach(message => {
      message.is_read = true
      message.read_at = new Date().toISOString()
    })
    loadUnreadCount()
    ElMessage.success('所有消息已标记为已读')
  } catch (error: any) {
    console.error('标记所有已读失败:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  }
}

const handleCreateMessage = async () => {
  if (!createFormRef.value) return

  try {
    await createFormRef.value.validate()
    createLoading.value = true

    const response = await notificationsApi.createMessage(createForm)
    if (response.success) {
      ElMessage.success('消息发送成功')
      showCreateDialog.value = false
      resetCreateForm()
      loadMessages()
    }
  } catch (error: any) {
    console.error('发送消息失败:', error)
    ElMessage.error(error.response?.data?.message || '发送失败')
  } finally {
    createLoading.value = false
  }
}

const resetCreateForm = () => {
  if (createFormRef.value) {
    createFormRef.value.resetFields()
  }

  Object.assign(createForm, {
    title: '',
    content: '',
    type: 'info',
    priority: 'medium',
    target_type: 'all',
    target_ids: [],
    scheduled_at: '',
    expires_at: ''
  })
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

const getMessageTypeTag = (type: string) => {
  const tagMap = {
    info: 'info',
    success: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return tagMap[type as keyof typeof tagMap] || 'info'
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

const getPriorityTag = (priority: string) => {
  const tagMap = {
    low: 'info',
    medium: '',
    high: 'warning',
    urgent: 'danger'
  }
  return tagMap[priority as keyof typeof tagMap] || ''
}

const getPriorityLabel = (priority: string) => {
  const labelMap = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return labelMap[priority as keyof typeof labelMap] || '中'
}

const formatDateTime = (dateTimeStr: string) => {
  return new Date(dateTimeStr).toLocaleString('zh-CN')
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadMessages()
  loadUnreadCount()
})
</script>

<style lang="scss" scoped>
.message-center {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .message-container {
    margin-top: 20px;

    .action-card {
      .actions {
        margin-top: 16px;
        display: flex;
        gap: 12px;
      }
    }

    .table-card {
      margin-top: 20px;

      .batch-actions {
        margin-bottom: 16px;
      }

      .message-title {
        font-weight: 500;

        &.unread {
          font-weight: 600;
          color: var(--el-color-primary);
        }
      }

      .el-icon {
        font-size: 16px;

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
      }

      .pagination {
        margin-top: 20px;
        display: flex;
        justify-content: flex-end;
      }
    }
  }
}

.message-detail {
  .message-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;

    .message-info {
      flex: 1;

      h3 {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 600;
      }

      .message-meta {
        display: flex;
        gap: 8px;
      }
    }

    .message-time {
      color: var(--el-text-color-secondary);
      font-size: 14px;
    }
  }

  .message-content {
    line-height: 1.6;
    margin-bottom: 20px;
    color: var(--el-text-color-regular);
  }

  .message-footer {
    padding-top: 16px;
    border-top: 1px solid var(--el-border-color-light);
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>