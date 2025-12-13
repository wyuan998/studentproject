<template>
  <div class="data-backup">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">数据备份</span>
      </template>
    </el-page-header>

    <!-- 操作栏 -->
    <div class="action-container">
      <el-button type="primary" @click="handleCreateBackup" :loading="createLoading">
        <el-icon><Plus /></el-icon>
        创建备份
      </el-button>
      <el-button @click="handleRestore" :loading="restoreLoading">
        <el-icon><RefreshRight /></el-icon>
        恢复数据
      </el-button>
      <el-button @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 备份统计 -->
    <el-row :gutter="20" class="stats-container">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon blue">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ backupStats.total }}</div>
              <div class="stat-label">总备份数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ backupStats.successful }}</div>
              <div class="stat-label">成功备份</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ formatFileSize(backupStats.totalSize) }}</div>
              <div class="stat-label">总大小</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon purple">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ backupStats.lastBackup }}</div>
              <div class="stat-label">最近备份</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选条件 -->
    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="备份类型">
          <el-select v-model="filterForm.type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="完整备份" value="full" />
            <el-option label="增量备份" value="incremental" />
            <el-option label="差异备份" value="differential" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 100px">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="进行中" value="in_progress" />
          </el-select>
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

    <!-- 备份列表 -->
    <el-card>
      <el-table
        v-loading="loading"
        :data="filteredBackups"
        stripe
        style="width: 100%"
      >
        <el-table-column label="备份名称" prop="name" min-width="200" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="包含内容" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="item in row.content"
              :key="item"
              size="small"
              style="margin-right: 4px; margin-bottom: 4px;"
            >
              {{ getContentText(item) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="created_at" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration }}s
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'success'"
              size="small"
              type="success"
              @click="handleRestoreBackup(row)"
            >
              恢复
            </el-button>
            <el-button
              v-if="row.status === 'success'"
              size="small"
              type="primary"
              @click="handleDownload(row)"
            >
              下载
            </el-button>
            <el-button
              size="small"
              type="info"
              @click="handleViewDetail(row)"
            >
              详情
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
    </el-card>

    <!-- 创建备份对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建备份"
      width="600px"
    >
      <el-form :model="createForm" label-width="120px">
        <el-form-item label="备份名称">
          <el-input v-model="createForm.name" placeholder="自动生成备份名称" readonly />
        </el-form-item>
        <el-form-item label="备份类型">
          <el-radio-group v-model="createForm.type">
            <el-radio label="full">完整备份</el-radio>
            <el-radio label="incremental">增量备份</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备份内容">
          <el-checkbox-group v-model="createForm.content">
            <el-checkbox label="database">数据库</el-checkbox>
            <el-checkbox label="uploads">上传文件</el-checkbox>
            <el-checkbox label="config">配置文件</el-checkbox>
            <el-checkbox label="logs">日志文件</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="压缩选项">
          <el-switch v-model="createForm.compression" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="备份说明（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreate" :loading="createLoading">
          开始备份
        </el-button>
      </template>
    </el-dialog>

    <!-- 恢复数据对话框 -->
    <el-dialog
      v-model="restoreDialogVisible"
      title="恢复数据"
      width="600px"
    >
      <el-form :model="restoreForm" label-width="120px">
        <el-form-item label="备份文件">
          <el-upload
            class="upload-demo"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="restoreForm.files"
            accept=".sql,.zip,.tar.gz"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 .sql, .zip, .tar.gz 格式的备份文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="恢复选项">
          <el-checkbox-group v-model="restoreForm.options">
            <el-checkbox label="database">恢复数据库</el-checkbox>
            <el-checkbox label="files">恢复文件</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="恢复前备份">
          <el-switch v-model="restoreForm.preBackup" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="restoreDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmRestore" :loading="restoreLoading">
          开始恢复
        </el-button>
      </template>
    </el-dialog>

    <!-- 备份详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="备份详情"
      width="800px"
    >
      <div v-if="currentBackup" class="backup-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="备份名称">{{ currentBackup.name }}</el-descriptions-item>
          <el-descriptions-item label="备份类型">
            <el-tag :type="getTypeColor(currentBackup.type)">
              {{ getTypeText(currentBackup.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(currentBackup.status)">
              {{ getStatusText(currentBackup.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="大小">{{ formatFileSize(currentBackup.size) }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentBackup.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ currentBackup.duration }}秒</el-descriptions-item>
          <el-descriptions-item label="创建人">{{ currentBackup.creator }}</el-descriptions-item>
          <el-descriptions-item label="文件路径">{{ currentBackup.file_path }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentBackup.description" class="detail-section">
          <h4>备份描述:</h4>
          <p>{{ currentBackup.description }}</p>
        </div>

        <div class="detail-section">
          <h4>包含内容:</h4>
          <el-tag
            v-for="item in currentBackup.content"
            :key="item"
            style="margin-right: 8px; margin-bottom: 8px;"
          >
            {{ getContentText(item) }}
          </el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, RefreshRight, Refresh, Document, Check, FolderOpened, Clock, Search
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const createLoading = ref(false)
const restoreLoading = ref(false)
const createDialogVisible = ref(false)
const restoreDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentBackup = ref<any>(null)

interface Backup {
  id: number
  name: string
  type: string
  status: string
  size: number
  content: string[]
  created_at: string
  duration: number
  creator: string
  file_path: string
  description?: string
}

const backupStats = reactive({
  total: 12,
  successful: 11,
  totalSize: 1024 * 1024 * 512, // 512MB
  lastBackup: '今天'
})

const filterForm = reactive({
  type: '',
  status: '',
  dateRange: null as [Date, Date] | null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const createForm = reactive({
  name: '',
  type: 'full',
  content: ['database', 'uploads'],
  compression: true,
  description: ''
})

const restoreForm = reactive({
  files: [],
  options: ['database'],
  preBackup: true
})

const backups = ref<Backup[]>([])

const filteredBackups = computed(() => {
  return backups.value.filter(backup => {
    const matchType = !filterForm.type || backup.type === filterForm.type
    const matchStatus = !filterForm.status || backup.status === filterForm.status

    let matchDate = true
    if (filterForm.dateRange) {
      const backupDate = new Date(backup.created_at)
      matchDate = backupDate >= filterForm.dateRange[0] && backupDate <= filterForm.dateRange[1]
    }

    return matchType && matchStatus && matchDate
  })
})

const loadBackups = async () => {
  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    const mockBackups: Backup[] = [
      {
        id: 1,
        name: 'backup_20240220_143000_full',
        type: 'full',
        status: 'success',
        size: 1024 * 1024 * 128, // 128MB
        content: ['database', 'uploads', 'config'],
        created_at: '2024-02-20T14:30:00Z',
        duration: 245,
        creator: 'admin',
        file_path: '/backups/backup_20240220_143000_full.zip',
        description: '完整备份'
      },
      {
        id: 2,
        name: 'backup_20240219_020000_incremental',
        type: 'incremental',
        status: 'success',
        size: 1024 * 1024 * 32, // 32MB
        content: ['database'],
        created_at: '2024-02-19T02:00:00Z',
        duration: 89,
        creator: 'system',
        file_path: '/backups/backup_20240219_020000_incremental.zip'
      },
      {
        id: 3,
        name: 'backup_20240218_143000_full',
        type: 'full',
        status: 'failed',
        size: 0,
        content: ['database', 'uploads'],
        created_at: '2024-02-18T14:30:00Z',
        duration: 120,
        creator: 'admin',
        file_path: '',
        description: '备份失败'
      }
    ]

    backups.value = mockBackups
    pagination.total = mockBackups.length
  } catch (error) {
    ElMessage.error('获取备份列表失败')
  } finally {
    loading.value = false
  }
}

const getTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'full': 'primary',
    'incremental': 'success',
    'differential': 'warning'
  }
  return colorMap[type] || 'info'
}

const getTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    'full': '完整',
    'incremental': '增量',
    'differential': '差异'
  }
  return textMap[type] || type
}

const getStatusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    'success': 'success',
    'failed': 'danger',
    'in_progress': 'warning'
  }
  return colorMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    'success': '成功',
    'failed': '失败',
    'in_progress': '进行中'
  }
  return textMap[status] || status
}

const getContentText = (content: string) => {
  const textMap: Record<string, string> = {
    'database': '数据库',
    'uploads': '上传文件',
    'config': '配置',
    'logs': '日志'
  }
  return textMap[content] || content
}

const formatFileSize = (bytes: number) => {
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

const handleSearch = () => {
  pagination.page = 1
}

const handleReset = () => {
  filterForm.type = ''
  filterForm.status = ''
  filterForm.dateRange = null
  pagination.page = 1
}

const handleRefresh = () => {
  loadBackups()
}

const handleCreateBackup = () => {
  const now = new Date()
  const timestamp = now.toISOString().replace(/[:.]/g, '').slice(0, -5)
  createForm.name = `backup_${timestamp}_${createForm.type}`
  createDialogVisible.value = true
}

const handleConfirmCreate = async () => {
  try {
    createLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 3000))

    ElMessage.success('备份创建成功')
    createDialogVisible.value = false
    loadBackups()
  } catch (error) {
    ElMessage.error('备份创建失败')
  } finally {
    createLoading.value = false
  }
}

const handleRestore = () => {
  restoreForm.files = []
  restoreForm.options = ['database']
  restoreForm.preBackup = true
  restoreDialogVisible.value = true
}

const handleFileChange = (file: any, fileList: any[]) => {
  restoreForm.files = fileList
}

const handleConfirmRestore = async () => {
  try {
    restoreLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 5000))

    ElMessage.success('数据恢复成功')
    restoreDialogVisible.value = false
    loadBackups()
  } catch (error) {
    ElMessage.error('数据恢复失败')
  } finally {
    restoreLoading.value = false
  }
}

const handleRestoreBackup = async (backup: Backup) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复备份 "${backup.name}" 吗？此操作将覆盖当前数据！`,
      '确认恢复',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 4000))

    ElMessage.success('数据恢复成功')
    loadBackups()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('数据恢复失败')
    }
  }
}

const handleDownload = async (backup: Backup) => {
  try {
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('备份下载开始')
  } catch (error) {
    ElMessage.error('备份下载失败')
  }
}

const handleViewDetail = (backup: Backup) => {
  currentBackup.value = backup
  detailDialogVisible.value = true
}

const handleDelete = async (backup: Backup) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除备份 "${backup.name}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    const index = backups.value.findIndex(b => b.id === backup.id)
    if (index > -1) {
      backups.value.splice(index, 1)
      pagination.total--
    }

    ElMessage.success('备份删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('备份删除失败')
    }
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadBackups()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadBackups()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadBackups()
})
</script>

<style lang="scss" scoped>
.data-backup {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .action-container {
    margin: 20px 0;
    display: flex;
    gap: 12px;
  }

  .stats-container {
    margin: 20px 0;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;

          .el-icon {
            font-size: 28px;
            color: white;
          }

          &.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
          &.green { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
          &.orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
          &.purple { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
        }

        .stat-info {
          .stat-number {
            font-size: 24px;
            font-weight: 700;
            color: var(--el-text-color-primary);
            line-height: 1;
          }

          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-regular);
            margin-top: 4px;
          }
        }
      }
    }
  }

  .filter-container {
    margin: 20px 0;
    padding: 20px;
    background-color: var(--el-bg-color-page);
    border-radius: 8px;
  }

  .backup-detail {
    .detail-section {
      margin-top: 20px;

      h4 {
        margin-bottom: 8px;
        color: var(--el-text-color-primary);
      }

      p {
        color: var(--el-text-color-regular);
      }
    }
  }
}
</style>