<template>
  <div class="enrollment-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">选课列表</h2>
        <p class="page-description">管理学生选课申请</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          学生选课
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-container">
      <el-form :model="queryParams" inline class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="搜索学生姓名、课程名称"
            clearable
            @keyup.enter="handleSearch"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="queryParams.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="待审核" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已取消" value="dropped" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select
            v-model="queryParams.semester"
            placeholder="选择学期"
            clearable
            style="width: 160px"
          >
            <el-option label="2024-春" value="2024-春" />
            <el-option label="2023-秋" value="2023-秋" />
            <el-option label="2023-春" value="2023-春" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="enrollmentList"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="学生姓名" prop="student_name" width="120" />
        <el-table-column label="学号" prop="student_no" width="120" />
        <el-table-column label="课程名称" prop="course_name" width="200" show-overflow-tooltip />
        <el-table-column label="课程编号" prop="course_code" width="120" />
        <el-table-column label="教师" prop="teacher_name" width="120" />
        <el-table-column label="学期" prop="semester" width="100" />
        <el-table-column label="选课时间" prop="enrollment_date" width="120" />
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              link
              @click="handleApprove(row)"
            >
              批准
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="warning"
              size="small"
              link
              @click="handleReject(row)"
            >
              拒绝
            </el-button>
            <el-button
              v-if="row.status === 'approved'"
              type="danger"
              size="small"
              link
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              @click="handleView(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedIds.length > 0">
        <el-button type="success" @click="batchApprove">
          批量批准 ({{ selectedIds.length }})
        </el-button>
        <el-button type="warning" @click="batchReject">
          批量拒绝 ({{ selectedIds.length }})
        </el-button>
      </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getEnrollmentList, approveEnrollment, rejectEnrollment, cancelEnrollment, batchApproveEnrollments } from '@/api/enrollment'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const enrollmentList = ref([])
const total = ref(0)
const selectedIds = ref([])

// 查询参数
const queryParams = reactive({
  page: 1,
  size: 20,
  keyword: '',
  status: '',
  semester: ''
})

// 获取选课列表
const getList = async () => {
  try {
    loading.value = true
    const { data } = await getEnrollmentList(queryParams)
    enrollmentList.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error('获取选课列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  queryParams.page = 1
  getList()
}

// 重置查询
const resetQuery = () => {
  Object.assign(queryParams, {
    page: 1,
    size: 20,
    keyword: '',
    status: '',
    semester: ''
  })
  getList()
}

// 分页处理
const handleSizeChange = (val: number) => {
  queryParams.size = val
  getList()
}

const handleCurrentChange = (val: number) => {
  queryParams.page = val
  getList()
}

// 表格选择
const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map(item => item.id)
}

// 操作处理
const handleCreate = () => {
  router.push('/enrollments/create')
}

const handleView = (row: any) => {
  router.push(`/enrollments/detail/${row.id}`)
}

const handleApprove = async (row: any) => {
  try {
    await approveEnrollment(row.id)
    ElMessage.success('批准成功')
    getList()
  } catch (error) {
    ElMessage.error('批准失败')
  }
}

const handleReject = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要拒绝这个选课申请吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await rejectEnrollment(row.id)
    ElMessage.success('拒绝成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('拒绝失败')
    }
  }
}

const handleCancel = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要取消这个选课吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await cancelEnrollment(row.id)
    ElMessage.success('取消成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

// 批量操作
const batchApprove = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要批准这 ${selectedIds.value.length} 个选课申请吗？`,
      '批量批准',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await batchApproveEnrollments(selectedIds.value, true)
    ElMessage.success('批量批准成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量批准失败')
    }
  }
}

const batchReject = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要拒绝这 ${selectedIds.value.length} 个选课申请吗？`,
      '批量拒绝',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await batchApproveEnrollments(selectedIds.value, false)
    ElMessage.success('批量拒绝成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量拒绝失败')
    }
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    dropped: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待审核',
    approved: '已批准',
    rejected: '已拒绝',
    dropped: '已取消'
  }
  return statusMap[status] || status
}

// 初始化
onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.enrollment-list {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      .page-title {
        margin: 0 0 4px;
        font-size: 20px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .page-description {
        margin: 0;
        font-size: 14px;
        color: var(--el-text-color-regular);
      }
    }
  }

  .filter-container {
    background-color: var(--el-bg-color);
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;

    .filter-form {
      margin: 0;
    }
  }

  .table-container {
    background-color: var(--el-bg-color);
    padding: 20px;
    border-radius: 4px;

    .batch-actions {
      margin: 16px 0;
      display: flex;
      gap: 12px;
    }

    .pagination-container {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>