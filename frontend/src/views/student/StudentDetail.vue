<template>
  <div class="student-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>学生详情</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
        <el-popconfirm
          title="确定要删除这个学生吗？"
          @confirm="handleDelete"
        >
          <template #reference>
            <el-button type="danger">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 学生信息 -->
    <div v-else-if="studentInfo" class="student-content">
      <!-- 基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="getStatusTagType(studentInfo.status)">
              {{ getStatusLabel(studentInfo.status) }}
            </el-tag>
          </div>
        </template>

        <div class="student-info">
          <div class="avatar-section">
            <el-avatar :size="120" :src="studentInfo.avatar">
              {{ studentInfo.real_name?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="basic-info">
              <h3>{{ studentInfo.real_name }}</h3>
              <p class="student-id">学号: {{ studentInfo.student_id }}</p>
              <p class="gender">
                <el-tag :type="getGenderTagType(studentInfo.gender)">
                  {{ getGenderLabel(studentInfo.gender) }}
                </el-tag>
              </p>
            </div>
          </div>

          <el-descriptions :column="2" border class="detail-list">
            <el-descriptions-item label="手机号">
              {{ studentInfo.phone || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ studentInfo.email || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="出生日期">
              {{ formatDate(studentInfo.birth_date) || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="入学日期">
              {{ formatDate(studentInfo.enrollment_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="预计毕业日期">
              {{ formatDate(studentInfo.graduation_date) || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="专业">
              {{ studentInfo.major }}
            </el-descriptions-item>
            <el-descriptions-item label="班级">
              {{ studentInfo.class_name }}
            </el-descriptions-item>
            <el-descriptions-item label="年级">
              {{ studentInfo.grade }}
            </el-descriptions-item>
            <el-descriptions-item label="家庭住址">
              {{ studentInfo.address || '未填写' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <!-- 联系人信息 -->
      <el-card class="contact-card">
        <template #header>
          <span>联系人信息</span>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="监护人姓名">
            {{ studentInfo.guardian_name || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="监护人手机">
            {{ studentInfo.guardian_phone || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="监护人邮箱">
            {{ studentInfo.guardian_email || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="紧急联系人">
            {{ studentInfo.emergency_contact || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="紧急联系电话">
            {{ studentInfo.emergency_phone || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(studentInfo.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后更新">
            {{ formatDateTime(studentInfo.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 选课记录 -->
      <el-card class="enrollment-card">
        <template #header>
          <div class="card-header">
            <span>选课记录</span>
            <el-button text type="primary" @click="handleViewAllEnrollments">
              查看全部
            </el-button>
          </div>
        </template>

        <el-table :data="enrollments" stripe border>
          <el-table-column prop="course_name" label="课程名称" />
          <el-table-column prop="teacher_name" label="授课教师" />
          <el-table-column prop="semester" label="学期" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getEnrollmentTagType(row.status)">
                {{ getEnrollmentLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="enrollment_date" label="选课时间" width="150">
            <template #default="{ row }">
              {{ formatDateTime(row.enrollment_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="final_score" label="最终成绩" width="100" />
          <el-table-column prop="credits_earned" label="获得学分" width="100" />
        </el-table>

        <div v-if="enrollments.length === 0" class="empty-state">
          <el-empty description="暂无选课记录" />
        </div>
      </el-card>

      <!-- 成绩记录 -->
      <el-card class="grade-card">
        <template #header>
          <div class="card-header">
            <span>成绩记录</span>
            <el-button text type="primary" @click="handleViewAllGrades">
              查看全部
            </el-button>
          </div>
        </template>

        <el-table :data="grades" stripe border>
          <el-table-column prop="course_name" label="课程名称" />
          <el-table-column prop="assignment_name" label="考核项目" />
          <el-table-column prop="assignment_type" label="类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ getAssignmentTypeLabel(row.assignment_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="得分" width="100" />
          <el-table-column prop="max_score" label="满分" width="100" />
          <el-table-column label="百分比" width="100">
            <template #default="{ row }">
              <el-progress
                :percentage="row.percentage"
                :color="getGradeColor(row.percentage)"
                :show-text="false"
                :stroke-width="8"
              />
              <span class="percentage-text">{{ row.percentage }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="graded_at" label="评分时间" width="150">
            <template #default="{ row }">
              {{ formatDateTime(row.graded_at) }}
            </template>
          </el-table-column>
        </el-table>

        <div v-if="grades.length === 0" class="empty-state">
          <el-empty description="暂无成绩记录" />
        </div>
      </el-card>

      <!-- 备注信息 -->
      <el-card class="notes-card">
        <template #header>
          <span>备注信息</span>
        </template>

        <div class="notes-content">
          {{ studentInfo.notes || '暂无备注' }}
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import { studentApi } from '@/api/user'
import type { Student, Enrollment, Grade } from '@/types/user'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const studentInfo = ref<Student | null>(null)
const enrollments = ref<Enrollment[]>([])
const grades = ref<Grade[]>([])

// 方法
const loadStudentDetail = async () => {
  const studentId = Number(route.params.id)
  if (!studentId) {
    ElMessage.error('无效的学生ID')
    router.go(-1)
    return
  }

  try {
    loading.value = true
    const response = await studentApi.getStudent(studentId)

    if (response.data?.success) {
      studentInfo.value = response.data.data

      // 加载选课记录和成绩记录
      await loadEnrollments(studentId)
      await loadGrades(studentId)
    } else {
      ElMessage.error(response.data?.message || '加载学生详情失败')
      router.go(-1)
    }
  } catch (error: any) {
    console.error('Load student detail error:', error)
    ElMessage.error(error.response?.data?.message || '加载学生详情失败')
    router.go(-1)
  } finally {
    loading.value = false
  }
}

const loadEnrollments = async (studentId: number) => {
  try {
    const response = await studentApi.getStudentEnrollments(studentId, { per_page: 5 })
    if (response.data?.success) {
      enrollments.value = response.data.data.items.map(item => ({
        ...item,
        course_name: item.course?.course_name || '未知课程',
        teacher_name: item.course?.teacher?.real_name || '未知教师'
      }))
    }
  } catch (error) {
    console.error('Load enrollments error:', error)
  }
}

const loadGrades = async (studentId: number) => {
  try {
    const response = await studentApi.getStudentGrades(studentId, { per_page: 5 })
    if (response.data?.success) {
      grades.value = response.data.data.items.map(item => ({
        ...item,
        course_name: item.course?.course_name || '未知课程'
      }))
    }
  } catch (error) {
    console.error('Load grades error:', error)
  }
}

const handleEdit = () => {
  if (studentInfo.value) {
    router.push(`/students/edit/${studentInfo.value.id}`)
  }
}

const handleDelete = async () => {
  if (!studentInfo.value) return

  try {
    const response = await studentApi.deleteStudent(studentInfo.value.id)

    if (response.data?.success) {
      ElMessage.success('删除成功')
      router.push('/students/list')
    } else {
      ElMessage.error(response.data?.message || '删除失败')
    }
  } catch (error: any) {
    console.error('Delete student error:', error)
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

const handleViewAllEnrollments = () => {
  if (studentInfo.value) {
    router.push(`/students/enrollments/${studentInfo.value.id}`)
  }
}

const handleViewAllGrades = () => {
  if (studentInfo.value) {
    router.push(`/students/grades/${studentInfo.value.id}`)
  }
}

// 工具方法
const getGenderTagType = (gender: string) => {
  const typeMap: Record<string, string> = {
    male: 'primary',
    female: 'danger'
  }
  return typeMap[gender] || 'info'
}

const getGenderLabel = (gender: string) => {
  const labelMap: Record<string, string> = {
    male: '男',
    female: '女',
    other: '其他'
  }
  return labelMap[gender] || gender
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

const getEnrollmentTagType = (status: string) => {
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

const getAssignmentTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    exam: '考试',
    quiz: '测验',
    homework: '作业',
    project: '项目',
    participation: '课堂参与',
    final: '期末'
  }
  return labelMap[type] || type
}

const getGradeColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 80) return '#409eff'
  if (percentage >= 70) return '#e6a23c'
  if (percentage >= 60) return '#f56c6c'
  return '#909399'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadStudentDetail()
})
</script>

<style lang="scss" scoped>
.student-detail-container {
  padding: 20px;
  max-width: 1200px;
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

.loading-container {
  padding: 20px;
}

.student-content {
  .info-card,
  .contact-card,
  .enrollment-card,
  .grade-card,
  .notes-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }
  }

  .student-info {
    .avatar-section {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 30px;

      .basic-info {
        h3 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
        }

        .student-id {
          margin: 0 0 4px 0;
          color: var(--el-text-color-secondary);
          font-size: 14px;
        }

        .gender {
          margin: 0;
        }
      }
    }

    .detail-list {
      margin-top: 20px;
    }
  }

  .notes-content {
    color: var(--el-text-color-primary);
    line-height: 1.6;
    min-height: 60px;
  }

  .empty-state {
    padding: 40px 0;
    text-align: center;
  }

  .percentage-text {
    margin-left: 8px;
    font-size: 12px;
    color: var(--el-text-color-regular);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .student-detail-container {
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

  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 12px !important;
  }

  .el-descriptions {
    :deep(.el-descriptions__cell) {
      padding: 8px 12px;
    }
  }

  .el-table {
    font-size: 12px;

    :deep(.el-table__cell) {
      padding: 8px 4px;
    }
  }
}
</style>