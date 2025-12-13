<template>
  <div class="teacher-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>教师详情</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
        <el-popconfirm
          title="确定要删除这个教师吗？"
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

    <!-- 教师信息 -->
    <div v-else-if="teacherInfo" class="teacher-content">
      <!-- 基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="getStatusTagType(teacherInfo.status)">
              {{ getStatusLabel(teacherInfo.status) }}
            </el-tag>
          </div>
        </template>

        <div class="teacher-info">
          <div class="avatar-section">
            <el-avatar :size="120" :src="teacherInfo.avatar">
              {{ teacherInfo.real_name?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="basic-info">
              <h3>{{ teacherInfo.real_name }}</h3>
              <p class="teacher-id">工号: {{ teacherInfo.teacher_id }}</p>
              <p class="gender">
                <el-tag :type="getGenderTagType(teacherInfo.gender)">
                  {{ getGenderLabel(teacherInfo.gender) }}
                </el-tag>
              </p>
              <p class="title">
                <el-tag :type="getTitleTagType(teacherInfo.title)">
                  {{ getTitleLabel(teacherInfo.title) }}
                </el-tag>
              </p>
            </div>
          </div>

          <el-descriptions :column="2" border class="detail-list">
            <el-descriptions-item label="手机号">
              {{ teacherInfo.phone || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ teacherInfo.email || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="出生日期">
              {{ formatDate(teacherInfo.birth_date) || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="入职日期">
              {{ formatDate(teacherInfo.hire_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="院系">
              {{ teacherInfo.department || '未分配' }}
            </el-descriptions-item>
            <el-descriptions-item label="办公地点">
              {{ teacherInfo.office_location || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="最高学历">
              {{ teacherInfo.education || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="毕业院校">
              {{ teacherInfo.graduated_from || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="研究方向">
              {{ teacherInfo.research_area || '未填写' }}
            </el-descriptions-item>
            <el-descriptions-item label="家庭住址">
              {{ teacherInfo.address || '未填写' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <!-- 课程信息 -->
      <el-card class="course-card">
        <template #header>
          <div class="card-header">
            <span>授课信息</span>
            <el-button text type="primary" @click="handleViewAllCourses">
              查看全部
            </el-button>
          </div>
        </template>

        <el-table :data="courses" stripe border>
          <el-table-column prop="course_name" label="课程名称" />
          <el-table-column prop="course_code" label="课程代码" />
          <el-table-column prop="semester" label="学期" />
          <el-table-column prop="credits" label="学分" width="80" />
          <el-table-column prop="enrolled_count" label="选课人数" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getCourseStatusTagType(row.status)">
                {{ getCourseStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button
                text
                type="primary"
                size="small"
                @click="handleViewCourse(row)"
              >
                查看
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="courses.length === 0" class="empty-state">
          <el-empty description="暂无授课信息" />
        </div>
      </el-card>

      <!-- 统计信息 -->
      <el-card class="stats-card">
        <template #header>
          <span>教学统计</span>
        </template>

        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalCourses }}</div>
            <div class="stat-label">总课程数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.currentSemesterCourses }}</div>
            <div class="stat-label">本学期课程</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.totalStudents }}</div>
            <div class="stat-label">总学生数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.avgStudentsPerCourse.toFixed(1) }}</div>
            <div class="stat-label">平均班额</div>
          </div>
        </div>
      </el-card>

      <!-- 备注信息 -->
      <el-card class="notes-card">
        <template #header>
          <span>备注信息</span>
        </template>

        <div class="notes-content">
          {{ teacherInfo.notes || '暂无备注' }}
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import { teacherApi } from '@/api/user'
import { courseApi } from '@/api/course'
import type { Teacher, Course } from '@/types/user'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const teacherInfo = ref<Teacher | null>(null)
const courses = ref<Course[]>([])

// 计算属性 - 统计信息
const stats = computed(() => {
  return {
    totalCourses: courses.value.length,
    currentSemesterCourses: courses.value.filter(c => c.semester === '2024-2').length,
    totalStudents: courses.value.reduce((sum, c) => sum + (c.enrolled_count || 0), 0),
    avgStudentsPerCourse: courses.value.length > 0
      ? courses.value.reduce((sum, c) => sum + (c.enrolled_count || 0), 0) / courses.value.length
      : 0
  }
})

// 方法
const loadTeacherDetail = async () => {
  const teacherId = Number(route.params.id)
  if (!teacherId) {
    ElMessage.error('无效的教师ID')
    router.go(-1)
    return
  }

  try {
    loading.value = true
    const response = await teacherApi.getTeacher(teacherId)

    if (response.data?.success) {
      teacherInfo.value = response.data.data

      // 加载课程信息
      await loadCourses(teacherId)
    } else {
      ElMessage.error(response.data?.message || '加载教师详情失败')
      router.go(-1)
    }
  } catch (error: any) {
    console.error('Load teacher detail error:', error)
    ElMessage.error(error.response?.data?.message || '加载教师详情失败')
    router.go(-1)
  } finally {
    loading.value = false
  }
}

const loadCourses = async (teacherId: number) => {
  try {
    const response = await courseApi.getCourses({
      teacher_id: teacherId,
      per_page: 5
    })
    if (response.data?.success) {
      courses.value = response.data.data.items
    }
  } catch (error) {
    console.error('Load courses error:', error)
  }
}

const handleEdit = () => {
  if (teacherInfo.value) {
    router.push(`/teachers/edit/${teacherInfo.value.id}`)
  }
}

const handleDelete = async () => {
  if (!teacherInfo.value) return

  try {
    const response = await teacherApi.deleteTeacher(teacherInfo.value.id)

    if (response.data?.success) {
      ElMessage.success('删除成功')
      router.push('/teachers/list')
    } else {
      ElMessage.error(response.data?.message || '删除失败')
    }
  } catch (error: any) {
    console.error('Delete teacher error:', error)
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

const handleViewAllCourses = () => {
  if (teacherInfo.value) {
    router.push(`/teachers/courses/${teacherInfo.value.id}`)
  }
}

const handleViewCourse = (row: Course) => {
  router.push(`/courses/detail/${row.id}`)
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

const getTitleTagType = (title: string) => {
  const typeMap: Record<string, string> = {
    professor: 'danger',
    associate_professor: 'warning',
    lecturer: 'primary',
    assistant: 'info'
  }
  return typeMap[title] || 'info'
}

const getTitleLabel = (title: string) => {
  const labelMap: Record<string, string> = {
    professor: '教授',
    associate_professor: '副教授',
    lecturer: '讲师',
    assistant: '助教'
  }
  return labelMap[title] || title
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    inactive: 'danger',
    on_leave: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    active: '在职',
    inactive: '离职',
    on_leave: '休假'
  }
  return labelMap[status] || status
}

const getCourseStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    draft: 'info',
    published: 'success',
    archived: 'warning',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const getCourseStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    draft: '草稿',
    published: '已发布',
    archived: '已归档',
    cancelled: '已取消'
  }
  return labelMap[status] || status
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadTeacherDetail()
})
</script>

<style lang="scss" scoped>
.teacher-detail-container {
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

.teacher-content {
  .info-card,
  .course-card,
  .stats-card,
  .notes-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }
  }

  .teacher-info {
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

        .teacher-id {
          margin: 0 0 4px 0;
          color: var(--el-text-color-secondary);
          font-size: 14px;
        }

        .gender, .title {
          margin: 0 0 4px 0;

          &:not(:last-child) {
            margin-right: 8px;
          }
        }
      }
    }

    .detail-list {
      margin-top: 20px;
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;

    .stat-item {
      text-align: center;
      padding: 20px;
      border: 1px solid var(--el-border-color-light);
      border-radius: 8px;
      background: var(--el-bg-color-overlay);

      .stat-value {
        font-size: 32px;
        font-weight: 600;
        color: var(--el-color-primary);
        margin-bottom: 8px;
      }

      .stat-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
      }
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
}

// 响应式设计
@media (max-width: 768px) {
  .teacher-detail-container {
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

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;

    .stat-item {
      padding: 16px 12px;

      .stat-value {
        font-size: 24px;
      }

      .stat-label {
        font-size: 12px;
      }
    }
  }
}
</style>