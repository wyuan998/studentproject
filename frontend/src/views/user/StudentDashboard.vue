<template>
  <div class="student-dashboard">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="avatar-section">
          <el-avatar :size="80" :src="profileData.avatar_url">
            {{ getAvatarText() }}
          </el-avatar>
          <div class="welcome-text">
            <h2>欢迎回来，{{ profileData.name || '同学' }}！</h2>
            <p>学号：{{ profileData.student_id }}</p>
            <p>专业：{{ profileData.major }} - {{ profileData.class_name }}</p>
          </div>
        </div>
        <div class="stats-section">
          <div class="stat-item">
            <div class="stat-number">{{ courses.length }}</div>
            <div class="stat-label">已选课程</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ grades.length }}</div>
            <div class="stat-label">成绩记录</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ averageScore }}</div>
            <div class="stat-label">平均成绩</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 我的课程 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <h3>我的课程</h3>
          <el-button type="text" @click="viewAllCourses">查看全部</el-button>
        </div>
      </template>

      <div v-if="loading" class="loading-content">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="courses.length === 0" class="empty-content">
        <el-empty description="暂无选课记录" />
      </div>

      <div v-else class="courses-grid">
        <div v-for="course in courses.slice(0, 4)" :key="course.course_id" class="course-card">
          <div class="course-info">
            <h4>{{ course.course_name }}</h4>
            <p class="course-code">{{ course.course_code }}</p>
            <p class="course-teacher">授课教师：{{ course.teacher_name }}</p>
            <p class="course-schedule">
              <el-icon><Clock /></el-icon>
              {{ course.schedule }}
            </p>
            <p class="course-location">
              <el-icon><Location /></el-icon>
              {{ course.location }}
            </p>
          </div>
          <div class="course-actions">
            <el-tag :type="getStatusType(course.status)" size="small">
              {{ getStatusText(course.status) }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 最近成绩 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <h3>最近成绩</h3>
          <el-button type="text" @click="viewAllGrades">查看全部</el-button>
        </div>
      </template>

      <div v-if="gradesLoading" class="loading-content">
        <el-skeleton :rows="4" animated />
      </div>

      <div v-else-if="grades.length === 0" class="empty-content">
        <el-empty description="暂无成绩记录" />
      </div>

      <div v-else class="grades-table">
        <el-table :data="grades.slice(0, 5)" style="width: 100%">
          <el-table-column prop="course_name" label="课程名称" width="200" />
          <el-table-column prop="exam_type" label="考试类型" width="120">
            <template #default="scope">
              <el-tag :type="getExamTypeTag(scope.row.exam_type)" size="small">
                {{ scope.row.exam_type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="成绩" width="100">
            <template #default="scope">
              <span :style="{ color: getScoreColor(scope.row.score, scope.row.max_score) }">
                {{ scope.row.score }}/{{ scope.row.max_score }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="百分比" width="100">
            <template #default="scope">
              {{ scope.row.percentage }}%
            </template>
          </el-table-column>
          <el-table-column prop="letter_grade" label="等级" width="80">
            <template #default="scope">
              <el-tag :type="getGradeTagType(scope.row.letter_grade)" size="small">
                {{ scope.row.letter_grade }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="comments" label="评语" show-overflow-tooltip />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Clock, Location } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const gradesLoading = ref(false)
const profileData = ref<any>({})
const courses = ref<any[]>([])
const grades = ref<any[]>([])

// 计算属性
const averageScore = computed(() => {
  if (grades.value.length === 0) return '0.0'
  const total = grades.value.reduce((sum, grade) => sum + parseFloat(grade.percentage), 0)
  return (total / grades.value.length).toFixed(1)
})

// 获取用户数据
const fetchUserData = async () => {
  if (!userStore.userInfo?.id) return

  try {
    // 获取个人信息
    const profileResponse = await fetch(`/api/user/profile?user_id=${userStore.userInfo.id}`)
    if (profileResponse.ok) {
      const profileResult = await profileResponse.json()
      if (profileResult.success) {
        profileData.value = profileResult.data
      }
    }

    // 获取课程信息
    loading.value = true
    const coursesResponse = await fetch(`/api/user/courses?user_id=${userStore.userInfo.id}`)
    if (coursesResponse.ok) {
      const coursesResult = await coursesResponse.json()
      if (coursesResult.success) {
        courses.value = coursesResult.data
      }
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    ElMessage.error('获取用户数据失败')
  } finally {
    loading.value = false
  }
}

// 获取成绩数据
const fetchGradesData = async () => {
  if (!userStore.userInfo?.id) return

  try {
    gradesLoading.value = true
    const response = await fetch(`/api/user/grades?user_id=${userStore.userInfo.id}`)
    if (response.ok) {
      const result = await response.json()
      if (result.success) {
        grades.value = result.data
      }
    }
  } catch (error) {
    console.error('获取成绩数据失败:', error)
    ElMessage.error('获取成绩数据失败')
  } finally {
    gradesLoading.value = false
  }
}

// 工具函数
const getAvatarText = () => {
  return (profileData.value.name || 'S').charAt(0).toUpperCase()
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'selected': 'success',
    'completed': 'info',
    'dropped': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'selected': '已选',
    'completed': '已完成',
    'dropped': '已退选'
  }
  return statusMap[status] || status
}

const getExamTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    '期中考试': 'warning',
    '期末考试': 'danger',
    '作业': 'primary',
    '测验': 'info',
    '项目': 'success'
  }
  return typeMap[type] || 'info'
}

const getGradeTagType = (grade: string) => {
  const gradeMap: Record<string, string> = {
    'A+': 'success',
    'A': 'success',
    'A-': 'success',
    'B+': 'primary',
    'B': 'primary',
    'B-': 'primary',
    'C+': 'warning',
    'C': 'warning',
    'C-': 'warning',
    'D': 'danger',
    'F': 'danger'
  }
  return gradeMap[grade] || 'info'
}

const getScoreColor = (score: number, maxScore: number) => {
  const percentage = (score / maxScore) * 100
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

// 事件处理
const viewAllCourses = () => {
  // 跳转到课程页面
  router.push('/student/courses')
}

const viewAllGrades = () => {
  // 跳转到成绩页面
  router.push('/student/grades')
}

onMounted(() => {
  fetchUserData()
  fetchGradesData()
})
</script>

<style scoped>
.student-dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.welcome-card :deep(.el-card__body) {
  padding: 30px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.welcome-text h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.welcome-text p {
  margin: 5px 0;
  opacity: 0.9;
  font-size: 14px;
}

.stats-section {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.section-card {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.loading-content,
.empty-content {
  padding: 40px 0;
  text-align: center;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.course-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.course-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.course-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.course-code {
  color: #909399;
  font-size: 12px;
  margin: 4px 0;
}

.course-teacher,
.course-schedule,
.course-location {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

.course-actions {
  margin-top: 16px;
  text-align: right;
}

.grades-table {
  overflow-x: auto;
}

@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }

  .stats-section {
    gap: 30px;
  }

  .courses-grid {
    grid-template-columns: 1fr;
  }
}
</style>