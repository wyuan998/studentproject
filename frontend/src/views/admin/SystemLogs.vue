<template>
  <div class="system-logs">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">系统日志</span>
      </template>
    </el-page-header>

    <!-- 操作栏 -->
    <div class="action-container">
      <el-button @click="handleExport" :loading="exportLoading">
        <el-icon><Download /></el-icon>
        导出日志
      </el-button>
      <el-button @click="handleClear" type="danger">
        <el-icon><Delete /></el-icon>
        清空日志
      </el-button>
      <el-button @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="日志级别">
          <el-select v-model="filterForm.level" placeholder="全部级别" clearable style="width: 120px">
            <el-option label="信息" value="INFO" />
            <el-option label="警告" value="WARNING" />
            <el-option label="错误" value="ERROR" />
            <el-option label="调试" value="DEBUG" />
          </el-select>
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="filterForm.module" placeholder="全部模块" clearable style="width: 150px">
            <el-option label="用户管理" value="user" />
            <el-option label="学生管理" value="student" />
            <el-option label="教师管理" value="teacher" />
            <el-option label="课程管理" value="course" />
            <el-option label="选课管理" value="enrollment" />
            <el-option label="成绩管理" value="grade" />
            <el-option label="系统管理" value="system" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户">
          <el-input
            v-model="filterForm.user"
            placeholder="用户名或IP"
            style="width: 150px"
            clearable
          />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 350px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 日志列表 -->
    <el-card>
      <el-table
        v-loading="loading"
        :data="filteredLogs"
        stripe
        style="width: 100%"
        @expand-change="handleExpandChange"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="log-detail">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="日志ID">{{ row.id }}</el-descriptions-item>
                <el-descriptions-item label="用户ID">{{ row.user_id }}</el-descriptions-item>
                <el-descriptions-item label="用户名">{{ row.username }}</el-descriptions-item>
                <el-descriptions-item label="IP地址">{{ row.ip_address }}</el-descriptions-item>
                <el-descriptions-item label="用户代理" :span="2">{{ row.user_agent }}</el-descriptions-item>
                <el-descriptions-item label="请求路径">{{ row.request_path }}</el-descriptions-item>
                <el-descriptions-item label="请求方法">{{ row.request_method }}</el-descriptions-item>
                <el-descriptions-item label="响应状态">{{ row.response_status }}</el-descriptions-item>
                <el-descriptions-item label="响应时间">{{ row.response_time }}ms</el-descriptions-item>
              </el-descriptions>

              <div v-if="row.request_data" class="request-data">
                <h4>请求数据:</h4>
                <pre>{{ JSON.stringify(row.request_data, null, 2) }}</pre>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="模块" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ getModuleText(row.module) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用户" prop="username" width="120" />
        <el-table-column label="操作" prop="action" min-width="200" show-overflow-tooltip />
        <el-table-column label="IP地址" prop="ip_address" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.response_status)" size="small">
              {{ row.response_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" prop="created_at" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleViewDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="800px"
    >
      <div v-if="currentLog" class="log-detail-dialog">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="日志ID">{{ currentLog.id }}</el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="getLevelType(currentLog.level)">
              {{ currentLog.level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="模块">{{ getModuleText(currentLog.module) }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ currentLog.username }}</el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ currentLog.ip_address }}</el-descriptions-item>
          <el-descriptions-item label="操作">{{ currentLog.action }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatDateTime(currentLog.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentLog.request_data" class="detail-section">
          <h4>请求数据:</h4>
          <el-input
            type="textarea"
            :rows="8"
            :value="JSON.stringify(currentLog.request_data, null, 2)"
            readonly
          />
        </div>

        <div v-if="currentLog.response_data" class="detail-section">
          <h4>响应数据:</h4>
          <el-input
            type="textarea"
            :rows="8"
            :value="JSON.stringify(currentLog.response_data, null, 2)"
            readonly
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Refresh, Search } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const exportLoading = ref(false)
const detailDialogVisible = ref(false)
const currentLog = ref<any>(null)

interface Log {
  id: number
  level: string
  module: string
  user_id: number
  username: string
  ip_address: string
  user_agent: string
  request_path: string
  request_method: string
  request_data?: any
  response_status: number
  response_time: number
  response_data?: any
  action: string
  created_at: string
}

const filterForm = reactive({
  level: '',
  module: '',
  user: '',
  dateRange: null as [Date, Date] | null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const logs = ref<Log[]>([])

const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    const matchLevel = !filterForm.level || log.level === filterForm.level
    const matchModule = !filterForm.module || log.module === filterForm.module
    const matchUser = !filterForm.user ||
      log.username.includes(filterForm.user) ||
      log.ip_address.includes(filterForm.user)

    let matchDate = true
    if (filterForm.dateRange) {
      const logDate = new Date(log.created_at)
      matchDate = logDate >= filterForm.dateRange[0] && logDate <= filterForm.dateRange[1]
    }

    return matchLevel && matchModule && matchUser && matchDate
  })
})

const loadLogs = async () => {
  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    const mockLogs: Log[] = [
      {
        id: 1,
        level: 'INFO',
        module: 'user',
        user_id: 1,
        username: 'admin',
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        request_path: '/api/admin/users',
        request_method: 'GET',
        request_data: { page: 1, pageSize: 20 },
        response_status: 200,
        response_time: 120,
        action: '查看用户列表',
        created_at: '2024-02-20T14:30:00Z'
      },
      {
        id: 2,
        level: 'WARNING',
        module: 'student',
        user_id: 2,
        username: 'teacher1',
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        request_path: '/api/students/123',
        request_method: 'PUT',
        request_data: { name: '张三', email: 'zhangsan@example.com' },
        response_status: 400,
        response_time: 85,
        action: '更新学生信息失败',
        created_at: '2024-02-20T14:25:00Z'
      },
      {
        id: 3,
        level: 'ERROR',
        module: 'system',
        user_id: null,
        username: 'system',
        ip_address: '127.0.0.1',
        user_agent: 'System/1.0',
        request_path: '/api/backup',
        request_method: 'POST',
        response_status: 500,
        response_time: 3000,
        action: '数据备份失败',
        created_at: '2024-02-20T14:20:00Z'
      }
    ]

    logs.value = mockLogs
    pagination.total = mockLogs.length
  } catch (error) {
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

const getLevelType = (level: string) => {
  const typeMap: Record<string, string> = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'danger',
    'DEBUG': 'success'
  }
  return typeMap[level] || 'info'
}

const getModuleText = (module: string) => {
  const textMap: Record<string, string> = {
    'user': '用户管理',
    'student': '学生管理',
    'teacher': '教师管理',
    'course': '课程管理',
    'enrollment': '选课管理',
    'grade': '成绩管理',
    'system': '系统管理'
  }
  return textMap[module] || module
}

const getStatusType = (status: number) => {
  if (status >= 200 && status < 300) return 'success'
  if (status >= 300 && status < 400) return 'info'
  if (status >= 400 && status < 500) return 'warning'
  if (status >= 500) return 'danger'
  return 'info'
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

const handleSearch = () => {
  pagination.page = 1
}

const handleReset = () => {
  filterForm.level = ''
  filterForm.module = ''
  filterForm.user = ''
  filterForm.dateRange = null
  pagination.page = 1
}

const handleRefresh = () => {
  loadLogs()
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('日志导出成功')
  } catch (error) {
    ElMessage.error('日志导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleClear = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复！',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    logs.value = []
    pagination.total = 0
    ElMessage.success('日志清空成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('日志清空失败')
    }
  }
}

const handleViewDetail = (log: Log) => {
  currentLog.value = log
  detailDialogVisible.value = true
}

const handleExpandChange = (row: Log, expanded: boolean) => {
  if (expanded) {
    // 展开时可以加载更多详细信息
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadLogs()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadLogs()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadLogs()
})
</script>

<style lang="scss" scoped>
.system-logs {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .action-container {
    margin: 20px 0;
    display: flex;
    gap: 12px;
  }

  .filter-container {
    margin: 20px 0;
    padding: 20px;
    background-color: var(--el-bg-color-page);
    border-radius: 8px;
  }

  .log-detail {
    padding: 20px;
    background-color: var(--el-bg-color-page);

    .request-data {
      margin-top: 16px;

      h4 {
        margin-bottom: 8px;
        color: var(--el-text-color-primary);
      }

      pre {
        background-color: var(--el-fill-color-light);
        padding: 12px;
        border-radius: 4px;
        font-size: 12px;
        overflow-x: auto;
      }
    }
  }

  .log-detail-dialog {
    .detail-section {
      margin-top: 20px;

      h4 {
        margin-bottom: 12px;
        color: var(--el-text-color-primary);
      }
    }
  }
}
</style>