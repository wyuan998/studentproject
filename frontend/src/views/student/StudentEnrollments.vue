<template>
  <div class="student-enrollments-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>选课记录</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleEnroll">
          <el-icon><Plus /></el-icon>
          在线选课
        </el-button>
      </div>
    </div>

    <!-- 学生信息卡片 -->
    <el-card class="student-info-card" v-if="studentInfo">
      <div class="info-content">
        <el-avatar :size="80" :src="studentInfo.avatar">
          {{ studentInfo.real_name?.charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="info-text">
          <h3>{{ studentInfo.real_name }}</h3>
          <p class="student-id">学号: {{ studentInfo.student_id }}</p>
          <p class="major-major">专业: {{ studentInfo.major }} | 班级: {{ studentInfo.grade }}</p>
          <p class="status">状态:
            <el-tag :type="getStatusTagType(studentInfo.status)">
              {{ getStatusLabel(studentInfo.status) }}
            </el-tag>
          </p>
        </div>
        <div class="info-stats">
          <div class="stat-item">
            <div class="stat-value">{{ enrollments.length }}</div>
            <div class="stat-label">总选课数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ approvedCount }}</div>
            <div class="stat-label">已通过</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalCredits }}</div>
            <div class="stat-label">总学分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ avgGPA.toFixed(2) }}</div>
            <div class="stat-label">平均GPA</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form
        ref="filterFormRef"
        :model="filterForm"
        :inline="true"
        class="filter-form"
      >
        <el-form-item label="学期">
          <el-select
            v-model="filterForm.semester"
            placeholder="请选择学期"
            clearable
            style="width: 180px"
          >
            <el-option label="2024春季" value="2024-1" />
            <el-option label="2024秋季" value="2024-2" />
            <el-option label="2023春季" value="2023-1" />
            <el-option label="2023秋季" value="2023-2" />
            <el-option label="2022春季" value="2022-1" />
            <el-option label="2022秋季" value="2022-2" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已退选" value="withdrawn" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程类型">
          <el-select
            v-model="filterForm.course_type"
            placeholder="请选择课程类型"
            clearable
            style="width: 150px"
          >
            <el-option label="必修课" value="required" />
            <el-option label="选修课" value="elective" />
            <el-option label="通识课" value="general" />
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
    </el-card>

    <!-- 选课记录表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="course_name" label="课程名称" min-width="150" />
        <el-table-column prop="course_code" label="课程代码" width="120" />
        <el-table-column prop="teacher_name" label="授课教师" width="120" />
        <el-table-column prop="semester" label="学期" width="100" />
        <el-table-column prop="credits" label="学分" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getEnrollmentLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enrollment_date" label="选课时间" width="150">
          <template #default="{ row }">
            {{ formatDateTime(row.enrollment_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="approved_by" label="审核人" width="100">
          <template #default="{ row }">
            {{ row.approver?.real_name || '系统' }}
          </template>
        </el-table-column>
        <el-table-column prop="final_score" label="最终成绩" width="100" />
        <el-table-column prop="credits_earned" label="获得学分" width="100" />
        <el-table-column prop="attendance_rate" label="出勤率" width="100">
          <template #default="{ row }">
            <span v-if="row.attendance_rate">
              {{ row.attendance_rate }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button
              text
              type="info"
              size="small"
              @click="handleViewCourse(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              text
              type="warning"
              size="small"
              @click="handleCancel(row)"
            >
              退选
            </el-button>
            <el-button
              v-if="row.status === 'rejected'"
              text
              type="primary"
              size="small"
              @click="handleReEnroll(row)"
            >
              重选
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 可选课程 -->
    <el-card class="available-courses-card">
      <template #header>
        <div class="card-header">
          <span>可选课程</span>
          <el-button type="primary" @click="loadAvailableCourses">
            刷新课程
          </el-button>
        </div>
      </template>

      <div class="courses-grid">
        <div
          v-for="course in availableCourses"
          :key="course.id"
          class="course-item"
          @click="handleEnrollCourse(course)"
        >
          <div class="course-header">
            <h4>{{ course.course_name }}</h4>
            <el-tag size="small">{{ course.credits }}学分</el-tag>
          </div>
          <div class="course-info">
            <p><strong>课程代码:</strong> {{ course.course_code }}</p>
            <p><strong>授课教师:</strong> {{ course.teacher?.real_name }}</p>
            <p><strong>上课时间:</strong> {{ course.schedule || '待定' }}</p>
            <p><strong>上课地点:</strong> {{ course.classroom || '待定' }}</p>
          </div>
          <div class="course-actions">
            <el-button type="primary" size="small" :disabled="isEnrolling">
              {{ isEnrolling ? '正在选课...' : '立即选课' }}
            </el-button>
          </div>
        </div>
      </div>

      <div v-if="availableCourses.length === 0" class="empty-state">
        <el-empty description="暂无可选课程" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Plus,
  Search,
  Refresh
} from '@element-plus/icons-vue'
import { studentApi } from '@/api/user'
import { enrollmentApi } from '@/api/enrollment'
import { courseApi } from '@/api/course'
import type { Student, Enrollment, Course } from '@/types/user'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const isEnrolling = ref(false)
const studentInfo = ref<Student | null>(null)
const tableData = ref<Enrollment[]>([])
const selectedRows = ref<Enrollment[]>([])
const availableCourses = ref<Course[]>([])

const filterForm = reactive({
  semester: '',
  status: '',
  course_type: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 计算属性
const approvedCount = computed(() => {
  return tableData.value.filter(item => item.status === 'approved').length
})

const totalCredits = computed(() => {
  return tableData.value
    .filter(item => item.status === 'completed')
    .reduce((sum, item) => sum + (item.credits_earned || 0), 0)
})

const avgGPA = computed(() => {
  const completedCourses = tableData.value.filter(item => item.status === 'completed')
  if (completedCourses.length === 0) return 0
  const totalGPA = completedCourses.reduce((sum, item) => sum + (item.gpa_points || 0), 0)
  return totalGPA / completedCourses.length
})

// 方法
const loadStudentInfo = async () => {
  const studentId = Number(route.params.id)
  if (!studentId) {
    ElMessage.error('无效的学生ID')
    router.go(-1)
    return
  }

  try {
    const response = await studentApi.getStudent(studentId)
    if (response.data?.success) {
      studentInfo.value = response.data.data
    } else {
      ElMessage.error(response.data?.message || '加载学生信息失败')
    }
  } catch (error) {
    console.error('Load student info error:', error)
    ElMessage.error('加载学生信息失败')
  }
}

const loadEnrollments = async () => {
  const studentId = Number(route.params.id)
  if (!studentId) return

  try {
    loading.value = true
    const response = await studentApi.getStudentEnrollments(studentId, {
      page: pagination.page,
      per_page: pagination.per_page,
      semester: filterForm.semester || undefined,
      status: filterForm.status as any || undefined
    })

    if (response.data?.success) {
      tableData.value = response.data.data.items.map(item => ({
        ...item,
        course_name: item.course?.course_name || '未知课程',
        course_code: item.course?.course_code || '',
        teacher_name: item.course?.teacher?.real_name || '未知教师',
        credits: item.course?.credits || 0
      }))
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data?.message || '加载选课记录失败')
    }
  } catch (error) {
    console.error('Load enrollments error:', error)
    ElMessage.error('加载选课记录失败')
  } finally {
    loading.value = false
  }
}

const loadAvailableCourses = async () => {
  try {
    const response = await courseApi.getCourses({
      page: 1,
      per_page: 20,
      status: 'published'
    })

    if (response.data?.success) {
      availableCourses.value = response.data.data.items.map(course => ({
        ...course,
        teacher_name: course.teacher?.real_name || '未知教师'
      }))
    }
  } catch (error) {
    console.error('Load available courses error:', error)
    ElMessage.error('加载可选课程失败')
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadEnrollments()
}

const handleReset = () => {
  Object.assign(filterForm, {
    semester: '',
    status: '',
    course_type: ''
  })
  pagination.page = 1
  loadEnrollments()
}

const handleEnroll = () => {
  router.push('/courses/list')
}

const handleViewCourse = (row: Enrollment) => {
  router.push(`/courses/detail/${row.course_id}`)
}

const handleCancel = async (row: Enrollment) => {
  try {
    await ElMessageBox.confirm(
      '确定要退选这门课程吗？',
      '确认退选',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await enrollmentApi.withdrawEnrollment(row.id)

    if (response.data?.success) {
      ElMessage.success('退选成功')
      loadEnrollments()
      loadAvailableCourses()
    } else {
      ElMessage.error(response.data?.message || '退选失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退选失败')
    }
  }
}

const handleReEnroll = async (row: Enrollment) => {
  try {
    const response = await enrollmentApi.createEnrollment({
      student_id: row.student_id,
      course_id: row.course_id
    })

    if (response.data?.success) {
      ElMessage.success('重新选课成功')
      loadEnrollments()
    } else {
      ElMessage.error(response.data?.message || '选课失败')
    }
  } catch (error) {
    ElMessage.error('选课失败')
  }
}

const handleEnrollCourse = async (course: Course) => {
  if (!studentInfo.value) return

  try {
    isEnrolling.value = true
    const response = await enrollmentApi.createEnrollment({
      student_id: studentInfo.value.id,
      course_id: course.id
    })

    if (response.data?.success) {
      ElMessage.success('选课成功')
      loadEnrollments()
      loadAvailableCourses()
    } else {
      ElMessage.error(response.data?.message || '选课失败')
    }
  } catch (error) {
    console.error('Enroll course error:', error)
    ElMessage.error('选课失败')
  } finally {
    isEnrolling.value = false
  }
}

const handleSelectionChange = (rows: Enrollment[]) => {
  selectedRows.value = rows
}

const handleSizeChange = (size: number) => {
  pagination.per_page = size
  loadEnrollments()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadEnrollments()
}

// 工具方法
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    withdrawn: 'info',
    completed: 'success'
  }
  return typeMap[status] || 'info'
}

const getEnrollmentLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    withdrawn: '已退选',
    completed: '已完成'
  }
  return labelMap[status] || status
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    graduated: 'info',
    suspended: 'warning',
    withdrawn: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    active: '在读',
    graduated: '已毕业',
    suspended: '休学',
    withdrawn: '退学'
  }
  return labelMap[status] || status
}

const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadStudentInfo()
  loadEnrollments()
  loadAvailableCourses()
})
</script>

<style lang="scss" scoped>
.student-enrollments-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }

  .header-right {
    display: flex;
    gap: 12px;
  }
}

.student-info-card {
  margin-bottom: 20px;

  .info-content {
    display: flex;
    align-items: center;
    gap: 20px;

    .info-text {
      h3 {
        margin: 0 0 8px 0;
        font-size: 20px;
        font-weight: 600;
      }

      .student-id {
        margin: 0 0 4px 0;
        color: var(--el-text-color-secondary);
        font-size: 14px;
      }

      .major-major {
        margin: 0 0 4px 0;
        color: var(--el-text-color-secondary);
        font-size: 14px;
      }

      .status {
        margin: 0;

        .el-tag {
          margin-left: 8px;
        }
      }
    }

    .info-stats {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-left: auto;

      .stat-item {
        text-align: center;

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--el-color-primary);
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-form {
    .el-form-item {
      margin-bottom: 0;
      margin-right: 16px;
    }
  }
}

.table-card {
  margin-bottom: 20px;

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.available-courses-card {
  .courses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 16px;

    .course-item {
      border: 1px solid var(--el-border-color-light);
      border-radius: 8px;
      padding: 20px;
      cursor: pointer;
      transition: all 0.3s ease;
      background: var(--el-bg-color);

      &:hover {
        border-color: var(--el-color-primary);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }

      .course-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        h4 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
      }

      .course-info {
        margin-bottom: 16px;

        p {
          margin: 4px 0;
          font-size: 13px;
          color: var(--el-text-color-regular);

          strong {
            color: var(--el-text-color-primary);
          }
        }
      }

      .course-actions {
        display: flex;
        justify-content: flex-end;
      }
    }
  }

  .empty-state {
    padding: 40px 0;
    text-align: center;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .student-enrollments-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .header-right {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .student-info-card {
    .info-content {
      flex-direction: column;
      gap: 16px;
      text-align: center;

      .info-stats {
        grid-template-columns: repeat(2, 1fr);
        margin-left: 0;
      }
    }
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }

  .filter-form {
    .el-form-item {
      width: 100%;
      margin-right: 0;
      margin-bottom: 12px;
    }
  }
}
</style>