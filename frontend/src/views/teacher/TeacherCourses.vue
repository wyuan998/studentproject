<template>
  <div class="teacher-courses-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ teacherInfo?.real_name }}的课程</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateCourse">
          <el-icon><Plus /></el-icon>
          创建课程
        </el-button>
      </div>
    </div>

    <!-- 教师信息卡片 -->
    <el-card class="teacher-info-card" v-if="teacherInfo">
      <div class="info-content">
        <el-avatar :size="80" :src="teacherInfo.avatar">
          {{ teacherInfo.real_name?.charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="info-text">
          <h3>{{ teacherInfo.real_name }}</h3>
          <p class="teacher-id">工号: {{ teacherInfo.teacher_id }}</p>
          <p class="department-title">院系: {{ teacherInfo.department }} | 职称: {{ getTitleLabel(teacherInfo.title) }}</p>
          <p class="status">状态:
            <el-tag :type="getStatusTagType(teacherInfo.status)">
              {{ getStatusLabel(teacherInfo.status) }}
            </el-tag>
          </p>
        </div>
        <div class="info-stats">
          <div class="stat-item">
            <div class="stat-value">{{ courses.length }}</div>
            <div class="stat-label">总课程数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ currentSemesterCount }}</div>
            <div class="stat-label">本学期课程</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalStudents }}</div>
            <div class="stat-label">总学生数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ avgStudentsPerCourse.toFixed(1) }}</div>
            <div class="stat-label">平均班额</div>
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
        <el-form-item label="课程状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已归档" value="archived" />
            <el-option label="已取消" value="cancelled" />
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

    <!-- 课程列表 -->
    <el-card class="course-card">
      <div class="course-grid">
        <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="course-item"
        >
          <div class="course-header">
            <h4>{{ course.course_name }}</h4>
            <div class="course-badges">
              <el-tag :type="getCourseStatusTagType(course.status)" size="small">
                {{ getCourseStatusLabel(course.status) }}
              </el-tag>
              <el-tag :type="getCourseTypeTagType(course.course_type)" size="small">
                {{ getCourseTypeLabel(course.course_type) }}
              </el-tag>
            </div>
          </div>
          <div class="course-info">
            <p><strong>课程代码:</strong> {{ course.course_code }}</p>
            <p><strong>学分:</strong> {{ course.credits }}</p>
            <p><strong>学时:</strong> {{ course.hours || '待定' }}</p>
            <p><strong>学期:</strong> {{ course.semester }}</p>
            <p><strong>上课时间:</strong> {{ course.schedule || '待定' }}</p>
            <p><strong>上课地点:</strong> {{ course.classroom || '待定' }}</p>
            <p><strong>选课人数:</strong> {{ course.enrolled_count || 0 }} / {{ course.max_students || '不限' }}</p>
          </div>
          <div class="course-actions">
            <el-button type="primary" size="small" @click="handleViewCourse(course)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="handleEditCourse(course)">
              编辑
            </el-button>
            <el-button type="info" size="small" @click="handleManageStudents(course)">
              学生管理
            </el-button>
          </div>
        </div>
      </div>

      <div v-if="filteredCourses.length === 0" class="empty-state">
        <el-empty description="暂无课程" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Plus,
  Search,
  Refresh
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

const filterForm = reactive({
  semester: '',
  course_type: '',
  status: ''
})

// 计算属性
const filteredCourses = computed(() => {
  return courses.value.filter(course => {
    if (filterForm.semester && course.semester !== filterForm.semester) return false
    if (filterForm.course_type && course.course_type !== filterForm.course_type) return false
    if (filterForm.status && course.status !== filterForm.status) return false
    return true
  })
})

const currentSemesterCount = computed(() => {
  return courses.value.filter(c => c.semester === '2024-2').length
})

const totalStudents = computed(() => {
  return courses.value.reduce((sum, c) => sum + (c.enrolled_count || 0), 0)
})

const avgStudentsPerCourse = computed(() => {
  if (courses.value.length === 0) return 0
  return totalStudents.value / courses.value.length
})

// 方法
const loadTeacherInfo = async () => {
  const teacherId = Number(route.params.id)
  if (!teacherId) {
    ElMessage.error('无效的教师ID')
    router.go(-1)
    return
  }

  try {
    const response = await teacherApi.getTeacher(teacherId)
    if (response.data?.success) {
      teacherInfo.value = response.data.data
    } else {
      ElMessage.error(response.data?.message || '加载教师信息失败')
    }
  } catch (error) {
    console.error('Load teacher info error:', error)
    ElMessage.error('加载教师信息失败')
  }
}

const loadCourses = async () => {
  const teacherId = Number(route.params.id)
  if (!teacherId) return

  try {
    const response = await courseApi.getCourses({
      teacher_id: teacherId,
      per_page: 100
    })

    if (response.data?.success) {
      courses.value = response.data.data.items
    } else {
      ElMessage.error(response.data?.message || '加载课程列表失败')
    }
  } catch (error) {
    console.error('Load courses error:', error)
    ElMessage.error('加载课程列表失败')
  }
}

const handleSearch = () => {
  // 筛选逻辑已在computed中实现
}

const handleReset = () => {
  Object.assign(filterForm, {
    semester: '',
    course_type: '',
    status: ''
  })
}

const handleCreateCourse = () => {
  router.push('/courses/create')
}

const handleViewCourse = (course: Course) => {
  router.push(`/courses/detail/${course.id}`)
}

const handleEditCourse = (course: Course) => {
  router.push(`/courses/edit/${course.id}`)
}

const handleManageStudents = (course: Course) => {
  router.push(`/courses/students/${course.id}`)
}

// 工具方法
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

const getCourseTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    required: 'danger',
    elective: 'primary',
    general: 'success'
  }
  return typeMap[type] || 'info'
}

const getCourseTypeLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    required: '必修课',
    elective: '选修课',
    general: '通识课'
  }
  return labelMap[type] || type
}

// 生命周期
onMounted(() => {
  loadTeacherInfo()
  loadCourses()
})
</script>

<style lang="scss" scoped>
.teacher-courses-container {
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

.teacher-info-card {
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

      .teacher-id {
        margin: 0 0 4px 0;
        color: var(--el-text-color-secondary);
        font-size: 14px;
      }

      .department-title {
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

.course-card {
  .course-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin-top: 16px;

    .course-item {
      border: 1px solid var(--el-border-color-light);
      border-radius: 8px;
      padding: 20px;
      background: var(--el-bg-color);
      transition: all 0.3s ease;

      &:hover {
        border-color: var(--el-color-primary);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }

      .course-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;

        h4 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          flex: 1;
          margin-right: 8px;
        }

        .course-badges {
          display: flex;
          gap: 4px;
          flex-direction: column;
          align-items: flex-end;
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
        gap: 8px;
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
  .teacher-courses-container {
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

  .teacher-info-card {
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

  .course-grid {
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