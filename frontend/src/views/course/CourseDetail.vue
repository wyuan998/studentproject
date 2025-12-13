<template>
  <div class="course-detail">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">{{ course?.name || '课程详情' }}</span>
      </template>
    </el-page-header>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="course" class="course-content">
      <!-- 基本信息 -->
      <el-card class="info-card">
        <template #header>
          <span class="card-title">课程信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程编号">{{ course.course_code }}</el-descriptions-item>
          <el-descriptions-item label="学分">{{ course.credits }}</el-descriptions-item>
          <el-descriptions-item label="学时">{{ course.hours }}</el-descriptions-item>
          <el-descriptions-item label="教师">{{ course.teacher_name }}</el-descriptions-item>
          <el-descriptions-item label="学期">{{ course.semester }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(course.status)">{{ getStatusText(course.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大人数">{{ course.max_students }}</el-descriptions-item>
          <el-descriptions-item label="已选人数">{{ course.current_students }}</el-descriptions-item>
        </el-descriptions>
        <el-descriptions :column="1" border style="margin-top: 16px;">
          <el-descriptions-item label="课程描述">{{ course.description }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 学生列表 -->
      <el-card class="students-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">选课学生</span>
            <el-button size="small" type="primary" @click="handleViewStudents">
              查看全部
            </el-button>
          </div>
        </template>
        <el-table :data="students" stripe>
          <el-table-column label="学号" prop="student_no" width="120" />
          <el-table-column label="姓名" prop="name" width="120" />
          <el-table-column label="专业" prop="major" />
          <el-table-column label="选课时间" prop="enrollment_date" width="120" />
        </el-table>
      </el-card>
    </div>

    <div v-else class="empty-container">
      <el-empty description="课程不存在" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCourseDetail } from '@/api/course'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const course = ref(null)
const students = ref([])

const courseId = route.params.id as string

const loadCourseDetail = async () => {
  try {
    loading.value = true
    const { data } = await getCourseDetail(Number(courseId))
    course.value = data
    // 这里可以加载选课学生列表
    students.value = [
      { student_no: 'S2021001', name: '张三', major: '计算机科学', enrollment_date: '2024-02-20' },
      { student_no: 'S2021002', name: '李四', major: '计算机科学', enrollment_date: '2024-02-21' },
      { student_no: 'S2021003', name: '王五', major: '软件工程', enrollment_date: '2024-02-22' }
    ]
  } catch (error) {
    ElMessage.error('获取课程详情失败')
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.back()
}

const handleViewStudents = () => {
  router.push(`/courses/${courseId}/students`)
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: 'info',
    published: 'success',
    ongoing: 'warning',
    completed: 'primary',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    published: '已发布',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

onMounted(() => {
  loadCourseDetail()
})
</script>

<style lang="scss" scoped>
.course-detail {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .loading-container {
    padding: 20px;
  }

  .course-content {
    .info-card,
    .students-card {
      margin-bottom: 20px;
    }

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .empty-container {
    padding: 60px 0;
    text-align: center;
  }
}
</style>