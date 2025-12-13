<template>
  <div class="message-list">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">消息通知</span>
      </template>
    </el-page-header>

    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="消息类型">
          <el-select v-model="filterForm.type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="系统通知" value="system" />
            <el-option label="选课通知" value="enrollment" />
            <el-option label="成绩通知" value="grade" />
            <el-option label="活动通知" value="activity" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 100px">
            <el-option label="未读" value="unread" />
            <el-option label="已读" value="read" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="handleMarkAllRead" :loading="loading">
            全部标记已读
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-card>
      <el-table
        v-loading="loading"
        :data="messages"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag v-if="!row.read" type="danger" size="small">未读</el-tag>
            <el-tag v-else type="info" size="small">已读</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)" size="small">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="标题" min-width="200">
          <template #default="{ row }">
            <span
              :class="{ 'message-title': true, 'unread': !row.read }"
              @click="handleViewDetail(row)"
            >
              {{ row.title }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="发送人" width="120" prop="sender_name" />

        <el-table-column label="接收人" width="120" prop="receiver_name" />

        <el-table-column label="发送时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleViewDetail(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="!row.read"
              size="small"
              type="success"
              @click="handleMarkRead(row)"
            >
              标记已读
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />

      <div class="batch-actions" v-if="selectedMessages.length > 0">
        <span>已选择 {{ selectedMessages.length }} 条消息</span>
        <el-button type="success" @click="handleBatchMarkRead">批量标记已读</el-button>
        <el-button type="danger" @click="handleBatchDelete">批量删除</el-button>
      </div>
    </el-card>

    <!-- 消息详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentMessage?.title"
      width="600px"
    >
      <div v-if="currentMessage" class="message-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="类型">
            <el-tag :type="getTypeColor(currentMessage.type)">
              {{ getTypeText(currentMessage.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentMessage.read ? 'info' : 'danger'">
              {{ currentMessage.read ? '已读' : '未读' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发送人">{{ currentMessage.sender_name }}</el-descriptions-item>
          <el-descriptions-item label="发送时间">{{ formatDateTime(currentMessage.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="message-content">
          <h4>消息内容</h4>
          <div class="content-text">{{ currentMessage.content }}</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentMessage && !currentMessage.read"
          type="primary"
          @click="handleMarkRead(currentMessage)"
        >
          标记已读
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'

const router = useRouter()

interface Message {
  id: number
  type: 'system' | 'enrollment' | 'grade' | 'activity'
  title: string
  content: string
  sender_name: string
  receiver_name: string
  read: boolean
  created_at: string
}

const loading = ref(false)
const messages = ref<Message[]>([])
const selectedMessages = ref<Message[]>([])
const currentMessage = ref<Message | null>(null)
const detailDialogVisible = ref(false)

const filterForm = reactive({
  type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const getTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    system: 'primary',
    enrollment: 'success',
    grade: 'warning',
    activity: 'info'
  }
  return colorMap[type] || 'info'
}

const getTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    system: '系统通知',
    enrollment: '选课通知',
    grade: '成绩通知',
    activity: '活动通知'
  }
  return textMap[type] || type
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

const loadMessages = async () => {
  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    const mockMessages: Message[] = [
      {
        id: 1,
        type: 'system',
        title: '系统维护通知',
        content: '系统将于今晚22:00-24:00进行维护升级，期间将无法正常访问，请提前做好准备。',
        sender_name: '系统管理员',
        receiver_name: '全体用户',
        read: false,
        created_at: '2024-02-20T10:30:00Z'
      },
      {
        id: 2,
        type: 'enrollment',
        title: '选课开始通知',
        content: '2024年春季学期选课将于明天上午9:00正式开始，请同学们提前查看选课手册，合理安排选课计划。',
        sender_name: '教务处',
        receiver_name: '全体学生',
        read: true,
        created_at: '2024-02-19T14:20:00Z'
      },
      {
        id: 3,
        type: 'grade',
        title: '成绩发布通知',
        content: '您的《数据结构与算法》课程成绩已发布，请及时查看。如有疑问，请联系任课教师。',
        sender_name: '王芳',
        receiver_name: '张三',
        read: false,
        created_at: '2024-02-18T16:45:00Z'
      },
      {
        id: 4,
        type: 'activity',
        title: '学术讲座通知',
        content: '本周五下午2:00将在图书馆报告厅举办人工智能前沿技术讲座，欢迎各位师生参加。',
        sender_name: '学术部',
        receiver_name: '全体师生',
        read: true,
        created_at: '2024-02-17T09:15:00Z'
      }
    ]

    messages.value = mockMessages
    pagination.total = mockMessages.length
  } catch (error) {
    ElMessage.error('获取消息列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadMessages()
}

const handleReset = () => {
  filterForm.type = ''
  filterForm.status = ''
  handleSearch()
}

const handleSelectionChange = (selection: Message[]) => {
  selectedMessages.value = selection
}

const handleViewDetail = (message: Message) => {
  currentMessage.value = message
  detailDialogVisible.value = true

  // 自动标记为已读
  if (!message.read) {
    handleMarkRead(message)
  }
}

const handleMarkRead = async (message?: Message) => {
  try {
    const targetMessage = message || currentMessage.value
    if (!targetMessage) return

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    targetMessage.read = true
    ElMessage.success('消息已标记为已读')
  } catch (error) {
    ElMessage.error('标记失败')
  }
}

const handleMarkAllRead = async () => {
  const unreadMessages = messages.value.filter(msg => !msg.read)
  if (unreadMessages.length === 0) {
    ElMessage.info('没有未读消息')
    return
  }

  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    unreadMessages.forEach(msg => {
      msg.read = true
    })

    ElMessage.success(`已标记 ${unreadMessages.length} 条消息为已读`)
  } catch (error) {
    ElMessage.error('批量标记失败')
  } finally {
    loading.value = false
  }
}

const handleBatchMarkRead = async () => {
  const unreadSelected = selectedMessages.value.filter(msg => !msg.read)
  if (unreadSelected.length === 0) {
    ElMessage.info('选中的消息都已读')
    return
  }

  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 800))

    unreadSelected.forEach(msg => {
      msg.read = true
    })

    ElMessage.success(`已批量标记 ${unreadSelected.length} 条消息为已读`)
  } catch (error) {
    ElMessage.error('批量标记失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (message: Message) => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    const index = messages.value.findIndex(msg => msg.id === message.id)
    if (index > -1) {
      messages.value.splice(index, 1)
      pagination.total--
    }

    ElMessage.success('消息删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedMessages.value.length} 条消息吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    loading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    selectedMessages.value.forEach(selectedMsg => {
      const index = messages.value.findIndex(msg => msg.id === selectedMsg.id)
      if (index > -1) {
        messages.value.splice(index, 1)
      }
    })

    pagination.total -= selectedMessages.value.length
    selectedMessages.value = []

    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadMessages()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadMessages()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadMessages()
})
</script>

<style lang="scss" scoped>
.message-list {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .filter-container {
    margin: 20px 0;
    padding: 20px;
    background-color: var(--el-bg-color-page);
    border-radius: 8px;
  }

  .message-title {
    cursor: pointer;
    color: var(--el-text-color-primary);

    &.unread {
      font-weight: 600;
      color: var(--el-color-primary);
    }

    &:hover {
      color: var(--el-color-primary);
    }
  }

  .batch-actions {
    margin-top: 20px;
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .message-detail {
    .message-content {
      margin-top: 20px;

      h4 {
        margin-bottom: 10px;
        color: var(--el-text-color-primary);
      }

      .content-text {
        padding: 16px;
        background-color: var(--el-fill-color-light);
        border-radius: 8px;
        line-height: 1.6;
        color: var(--el-text-color-regular);
      }
    }
  }
}
</style>