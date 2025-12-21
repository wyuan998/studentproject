<template>
  <div class="teacher-dashboard">
    <!-- 调试信息 -->
    <div style="background: #f0f0f0; padding: 10px; margin: 10px; border: 1px solid #ccc;">
      <h3>教师仪表板调试信息</h3>
      <p>当前用户: {{ userInfo?.real_name || '未知' }}</p>
      <p>用户角色: {{ userStore.userInfo?.role }}</p>
      <p>用户权限: {{ userStore.roles }}</p>
    </div>
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="avatar-section">
          <el-avatar :size="80" :src="profileData.avatar_url">
            {{ getAvatarText() }}
          </el-avatar>
          <div class="welcome-text">
            <h2>欢迎回来，{{ profileData.name || '老师' }}！</h2>
            <p>工号：{{ profileData.teacher_id }}</p>
            <p>{{ profileData.department }} - {{ profileData.title }}</p>
          </div>
        </div>
        <div class="stats-section">
          <div class="stat-item">
            <div class="stat-number">{{ courses.length }}</div>
            <div class="stat-label">授课课程</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ totalStudents }}</div>
            <div class="stat-label">学生总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ grades.length }}</div>
            <div class="stat-label">成绩录入</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 我的课程 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <h3>授课课程</h3>
          <el-button type="text" @click="viewAllCourses">管理课程</el-button>
        </div>
      </template>

      <div v-if="loading" class="loading-content">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="courses.length === 0" class="empty-content">
        <el-empty description="暂无授课安排" />
      </div>

      <div v-else class="courses-grid">
        <div v-for="course in courses" :key="course.course_id" class="course-card">
          <div class="course-info">
            <h4>{{ course.course_name }}</h4>
            <p class="course-code">{{ course.course_code }}</p>
            <p class="course-details">
              <span class="detail-item">
                <el-icon><User /></el-icon>
                {{ course.current_students }}/{{ course.max_students }}人
              </span>
              <span class="detail-item">
                <el-icon><Clock /></el-icon>
                {{ course.hours }}学时
              </span>
            </p>
            <p class="course-schedule">
              <el-icon><Calendar /></el-icon>
              {{ course.schedule }}
            </p>
            <p class="course-location">
              <el-icon><Location /></el-icon>
              {{ course.location }}
            </p>
          </div>
          <div class="course-actions">
            <el-tag :type="getTypeTag(course.course_type)" size="small">
              {{ getTypeText(course.course_type) }}
            </el-tag>
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="manageCourse(course)">
                课程管理
              </el-button>
              <el-button size="small" @click="enterGrades(course)">
                成绩录入
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 学生成绩概览 -->
    <el-card class="section-card">
      <template #header>
        <div class="section-header">
          <h3>成绩概览</h3>
          <el-button type="text" @click="viewAllGrades">查看全部成绩</el-button>
        </div>
      </template>

      <div v-if="gradesLoading" class="loading-content">
        <el-skeleton :rows="4" animated />
      </div>

      <div v-else-if="grades.length === 0" class="empty-content">
        <el-empty description="暂无成绩记录" />
      </div>

      <div v-else class="grades-content">
        <!-- 成绩统计 -->
        <div class="grades-stats">
          <div class="stat-card">
            <div class="stat-icon average">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ classAverage }}</div>
              <div class="stat-label">班级平均分</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon highest">
              <el-icon><Top /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ highestScore }}</div>
              <div class="stat-label">最高分</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon lowest">
              <el-icon><Bottom /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ lowestScore }}</div>
              <div class="stat-label">最低分</div>
            </div>
          </div>
        </div>

        <!-- 成绩表格 -->
        <div class="grades-table">
          <el-table :data="grades.slice(0, 8)" style="width: 100%">
            <el-table-column prop="student_name" label="学生姓名" width="120" />
            <el-table-column prop="student_id" label="学号" width="120" />
            <el-table-column prop="course_name" label="课程名称" width="180" />
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
            <el-table-column prop="is_published" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.is_published ? 'success' : 'warning'" size="small">
                  {{ scope.row.is_published ? '已发布' : '未发布' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button type="text" size="small" @click="editGrade(scope.row)">
                  编辑
                </el-button>
                <el-button
                  :type="scope.row.is_published ? 'text' : 'success'"
                  size="small"
                  @click="togglePublish(scope.row)"
                >
                  {{ scope.row.is_published ? '取消发布' : '发布' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  Clock,
  Location,
  User,
  Calendar,
  TrendCharts,
  Top,
  Bottom
} from '@element-plus/icons-vue'
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
const totalStudents = computed(() => {
  return courses.value.reduce((total, course) => total + course.current_students, 0)
})

const classAverage = computed(() => {
  if (grades.value.length === 0) return '0.0'
  const total = grades.value.reduce((sum, grade) => sum + parseFloat(grade.percentage), 0)
  return (total / grades.value.length).toFixed(1)
})

const highestScore = computed(() => {
  if (grades.value.length === 0) return '0'
  const scores = grades.value.map(g => g.score)
  return Math.max(...scores).toString()
})

const lowestScore = computed(() => {
  if (grades.value.length === 0) return '0'
  const scores = grades.value.map(g => g.score)
  return Math.min(...scores).toString()
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
  return (profileData.value.name || 'T').charAt(0).toUpperCase()
}

const getTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    'required': 'danger',
    'elective': 'primary',
    'optional': 'info'
  }
  return typeMap[type] || 'info'
}

const getTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    'required': '必修',
    'elective': '选修',
    'optional': '任选'
  }
  return typeMap[type] || type
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
  router.push('/teacher/courses')
}

const viewAllGrades = () => {
  router.push('/teacher/grades')
}

const manageCourse = (course: any) => {
  // 跳转到课程管理页面
  router.push(`/teacher/course/${course.course_id}`)
}

const enterGrades = (course: any) => {
  // 跳转到成绩录入页面
  router.push(`/teacher/grades/${course.course_id}`)
}

const editGrade = (grade: any) => {
  // 编辑成绩
  ElMessage.info('编辑成绩功能开发中')
}

const togglePublish = async (grade: any) => {
  try {
    const action = grade.is_published ? '取消发布' : '发布'
    await ElMessageBox.confirm(`确定要${action}这条成绩吗？`, '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 模拟切换状态
    grade.is_published = !grade.is_published
    ElMessage.success(`成绩${action}成功`)
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  console.log('=== TeacherDashboard onMounted ===')
  console.log('用户状态:', {
    userInfo: userStore.userInfo,
    roles: userStore.roles,
    token: userStore.token
  })

  fetchUserData()
  fetchGradesData()
})
</script>

<style scoped>
.teacher-dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-card {
  background: linear-gradient(135deg, #5e72e4 0%, #825ee4 100%);
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
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
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

.course-details {
  display: flex;
  gap: 16px;
  margin: 12px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.grades-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.grades-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #e4e7ed;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.stat-icon.average {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.highest {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: #666;
}

.stat-icon.lowest {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: #666;
}

.stat-info {
  flex: 1;
}

.stat-card .stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-card .stat-label {
  font-size: 14px;
  color: #909399;
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

  .course-actions {
    flex-direction: column;
    gap: 12px;
    align-items: flex-end;
  }

  .grades-stats {
    grid-template-columns: 1fr;
  }
}
</style>