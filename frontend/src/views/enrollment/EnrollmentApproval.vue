<template>
  <div class="enrollment-approval">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">选课审批</span>
      </template>
    </el-page-header>

    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="学生姓名">
          <el-input
            v-model="filterForm.student_name"
            placeholder="请输入学生姓名"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="课程名称">
          <el-input
            v-model="filterForm.course_name"
            placeholder="请输入课程名称"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
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
        </el-form-item>
      </el-form>
    </div>

    <el-card>
      <el-table
        v-loading="loading"
        :data="enrollments"
        stripe
        style="width: 100%"
      >
        <el-table-column label="申请时间" prop="created_at" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="学生学号" prop="student_no" width="100" />
        <el-table-column label="学生姓名" prop="student_name" width="100" />
        <el-table-column label="课程编号" prop="course_code" width="100" />
        <el-table-column label="课程名称" prop="course_name" width="150" />
        <el-table-column label="学分" prop="credits" width="60" />
        <el-table-column label="教师" prop="teacher_name" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申请原因" prop="reason" min-width="150" show-overflow-tooltip />
        <el-table-column label="审批人" prop="approver_name" width="100" />
        <el-table-column label="审批时间" prop="approved_at" width="120">
          <template #default="{ row }">
            {{ row.approved_at ? formatDate(row.approved_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="success"
              @click="handleApprove(row)"
            >
              批准
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              type="danger"
              @click="handleReject(row)"
            >
              拒绝
            </el-button>
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
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 审批对话框 -->
    <el-dialog
      v-model="approvalDialogVisible"
      :title="approvalType === 'approve' ? '批准选课' : '拒绝选课'"
      width="500px"
    >
      <el-form ref="approvalFormRef" :model="approvalForm" label-width="80px">
        <el-descriptions :column="1" border style="margin-bottom: 20px">
          <el-descriptions-item label="学生">{{ currentEnrollment?.student_name }}</el-descriptions-item>
          <el-descriptions-item label="课程">{{ currentEnrollment?.course_name }}</el-descriptions-item>
          <el-descriptions-item label="申请原因">{{ currentEnrollment?.reason }}</el-descriptions-item>
        </el-descriptions>
        <el-form-item label="审批意见" prop="comment">
          <el-input
            v-model="approvalForm.comment"
            type="textarea"
            :rows="3"
            placeholder="请输入审批意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approvalDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="approvalLoading"
          @click="confirmApproval"
        >
          确认{{ approvalType === 'approve' ? '批准' : '拒绝' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'

const router = useRouter()

interface Enrollment {
  id: number
  student_no: string
  student_name: string
  course_code: string
  course_name: string
  credits: number
  teacher_name: string
  status: 'pending' | 'approved' | 'rejected'
  reason: string
  approver_name?: string
  approved_at?: string
  created_at: string
}

const loading = ref(false)
const approvalLoading = ref(false)
const enrollments = ref<Enrollment[]>([])
const currentEnrollment = ref<Enrollment | null>(null)
const approvalDialogVisible = ref(false)
const approvalType = ref<'approve' | 'reject'>('approve')
const approvalFormRef = ref<FormInstance>()

const filterForm = reactive({
  student_name: '',
  course_name: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const approvalForm = reactive({
  comment: ''
})

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

const loadEnrollments = async () => {
  try {
    loading.value = true
    // Mock API call - 替换为实际的API调用
    const mockData: Enrollment[] = [
      {
        id: 1,
        student_no: 'S2021001',
        student_name: '张三',
        course_code: 'CS101',
        course_name: '计算机科学导论',
        credits: 3,
        teacher_name: '李明',
        status: 'pending',
        reason: '专业必修课，需要完成学分要求',
        created_at: '2024-02-20T10:30:00Z'
      },
      {
        id: 2,
        student_no: 'S2021002',
        student_name: '李四',
        course_code: 'CS102',
        course_name: '数据结构与算法',
        credits: 4,
        teacher_name: '王芳',
        status: 'approved',
        reason: '专业核心课程',
        approver_name: '教务处',
        approved_at: '2024-02-19T14:20:00Z',
        created_at: '2024-02-18T09:15:00Z'
      },
      {
        id: 3,
        student_no: 'S2021003',
        student_name: '王五',
        course_code: 'CS103',
        course_name: '数据库系统',
        credits: 3,
        teacher_name: '张伟',
        status: 'rejected',
        reason: '先修课程未完成',
        approver_name: '教务处',
        approved_at: '2024-02-17T16:45:00Z',
        created_at: '2024-02-16T11:30:00Z'
      }
    ]

    enrollments.value = mockData
    pagination.total = mockData.length
  } catch (error) {
    ElMessage.error('获取选课申请列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadEnrollments()
}

const handleReset = () => {
  filterForm.student_name = ''
  filterForm.course_name = ''
  filterForm.status = ''
  handleSearch()
}

const handleApprove = (enrollment: Enrollment) => {
  currentEnrollment.value = enrollment
  approvalType.value = 'approve'
  approvalForm.comment = ''
  approvalDialogVisible.value = true
}

const handleReject = (enrollment: Enrollment) => {
  currentEnrollment.value = enrollment
  approvalType.value = 'reject'
  approvalForm.comment = ''
  approvalDialogVisible.value = true
}

const confirmApproval = async () => {
  if (!currentEnrollment.value) return

  try {
    approvalLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    const action = approvalType.value === 'approve' ? '批准' : '拒绝'
    ElMessage.success(`选课申请${action}成功`)

    approvalDialogVisible.value = false
    loadEnrollments()
  } catch (error) {
    ElMessage.error(`${approvalType.value === 'approve' ? '批准' : '拒绝'}失败`)
  } finally {
    approvalLoading.value = false
  }
}

const handleViewDetail = (enrollment: Enrollment) => {
  ElMessageBox.alert(`
    学生：${enrollment.student_name} (${enrollment.student_no})<br>
    课程：${enrollment.course_name} (${enrollment.course_code})<br>
    学分：${enrollment.credits}<br>
    教师：${enrollment.teacher_name}<br>
    申请原因：${enrollment.reason}<br>
    申请时间：${formatDate(enrollment.created_at)}<br>
    状态：${getStatusText(enrollment.status)}
  `, '选课申请详情', {
    dangerouslyUseHTMLString: true
  })
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadEnrollments()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadEnrollments()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadEnrollments()
})
</script>

<style lang="scss" scoped>
.enrollment-approval {
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

  .el-card {
    .el-pagination {
      margin-top: 20px;
      justify-content: center;
    }
  }
}
</style>