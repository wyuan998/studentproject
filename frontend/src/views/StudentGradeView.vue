<template>
  <div class="student-grade-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h2>我的成绩</h2>
        <p class="page-description">查看您在各门课程中的学习成绩和详细情况</p>
      </div>
    </div>

    <!-- 成绩统计卡片 -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="overview-card average">
            <div class="card-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ averageScore }}</div>
              <div class="card-label">总体平均分</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-card courses">
            <div class="card-icon">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ uniqueCourses.length }}</div>
              <div class="card-label">已选课程</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-card excellent">
            <div class="card-icon">
              <el-icon><Star /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ excellentCount }}</div>
              <div class="card-label">优秀成绩</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="overview-card total">
            <div class="card-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ grades.length }}</div>
              <div class="card-label">成绩记录</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <div class="filter-section">
        <div class="filter-left">
          <el-select
            v-model="selectedSemester"
            placeholder="选择学期"
            clearable
            @change="handleFilterChange"
            style="width: 150px"
          >
            <el-option label="全部学期" value="" />
            <el-option label="2024-2025学年第一学期" value="2024-1" />
            <el-option label="2023-2024学年第二学期" value="2023-2" />
            <el-option label="2023-2024学年第一学期" value="2023-1" />
          </el-select>

          <el-select
            v-model="selectedCourse"
            placeholder="选择课程"
            clearable
            @change="handleFilterChange"
            style="width: 200px"
          >
            <el-option label="全部课程" value="" />
            <el-option
              v-for="course in uniqueCourses"
              :key="course.course_name"
              :label="course.course_name"
              :value="course.course_name"
            />
          </el-select>

          <el-select
            v-model="selectedExamType"
            placeholder="考试类型"
            clearable
            @change="handleFilterChange"
            style="width: 150px"
          >
            <el-option label="全部类型" value="" />
            <el-option label="期末考试" value="期末考试" />
            <el-option label="期中考试" value="期中考试" />
            <el-option label="作业" value="作业" />
            <el-option label="测验" value="测验" />
            <el-option label="项目" value="项目" />
          </el-select>
        </div>

        <div class="filter-right">
          <el-input
            v-model="searchQuery"
            placeholder="搜索课程名称..."
            @input="handleSearch"
            clearable
            style="width: 250px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
    </el-card>

    <!-- 成绩列表 -->
    <el-card class="grades-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="filteredGrades.length === 0" class="empty-container">
        <el-empty description="暂无成绩记录" />
      </div>

      <div v-else>
        <!-- 课程分组展示 -->
        <div v-for="course in groupedGrades" :key="course.courseName" class="course-group">
          <div class="course-header">
            <div class="course-info">
              <h3 class="course-name">{{ course.courseName }}</h3>
              <span class="course-code">{{ course.courseCode }}</span>
              <span class="course-teacher">授课教师：{{ course.teacher }}</span>
            </div>
            <div class="course-summary">
              <span class="course-average">课程平均分：{{ course.average }}分</span>
            </div>
          </div>

          <el-table :data="course.grades" style="width: 100%" class="grade-table">
            <el-table-column prop="exam_type" label="考试类型" width="120">
              <template #default="scope">
                <el-tag :type="getExamTypeTag(scope.row.exam_type)" size="small">
                  {{ scope.row.exam_type }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="score" label="成绩" width="120">
              <template #default="scope">
                <div class="score-display">
                  <span class="score-text" :style="{ color: getScoreColor(scope.row.score, scope.row.max_score) }">
                    {{ scope.row.score }}
                  </span>
                  <span class="score-total">/ {{ scope.row.max_score }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="percentage" label="百分比" width="100">
              <template #default="scope">
                <div class="percentage-bar">
                  <div
                    class="percentage-fill"
                    :style="{
                      width: `${scope.row.percentage}%`,
                      backgroundColor: getScoreColor(scope.row.score, scope.row.max_score)
                    }"
                  ></div>
                  <span class="percentage-text">{{ scope.row.percentage }}%</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="letter_grade" label="等级" width="80">
              <template #default="scope">
                <el-tag :type="getGradeTagType(scope.row.letter_grade)" size="small">
                  {{ scope.row.letter_grade }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="gpa" label="绩点" width="80">
              <template #default="scope">
                <span class="gpa-text">{{ scope.row.gpa }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="exam_date" label="考试日期" width="120">
              <template #default="scope">
                {{ formatDate(scope.row.exam_date) }}
              </template>
            </el-table-column>

            <el-table-column prop="comments" label="评语" show-overflow-tooltip />

            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" link @click="viewGradeDetail(scope.row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>

    <!-- 成绩详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="成绩详情" width="600px">
      <div v-if="selectedGrade" class="grade-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程名称">
            {{ selectedGrade.course_name }}
          </el-descriptions-item>
          <el-descriptions-item label="课程代码">
            {{ selectedGrade.course_code }}
          </el-descriptions-item>
          <el-descriptions-item label="考试类型">
            <el-tag :type="getExamTypeTag(selectedGrade.exam_type)">
              {{ selectedGrade.exam_type }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="考试日期">
            {{ formatDate(selectedGrade.exam_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="成绩">
            <span class="detail-score" :style="{ color: getScoreColor(selectedGrade.score, selectedGrade.max_score) }">
              {{ selectedGrade.score }} / {{ selectedGrade.max_score }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="百分比">
            {{ selectedGrade.percentage }}%
          </el-descriptions-item>
          <el-descriptions-item label="等级">
            <el-tag :type="getGradeTagType(selectedGrade.letter_grade)">
              {{ selectedGrade.letter_grade }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="绩点">
            {{ selectedGrade.gpa }}
          </el-descriptions-item>
          <el-descriptions-item label="班级排名" v-if="selectedGrade.class_rank">
            第 {{ selectedGrade.class_rank }} 名 (共 {{ selectedGrade.class_total }} 人)
          </el-descriptions-item>
          <el-descriptions-item label="年级排名" v-if="selectedGrade.grade_rank">
            第 {{ selectedGrade.grade_rank }} 名 (共 {{ selectedGrade.grade_total }} 人)
          </el-descriptions-item>
          <el-descriptions-item label="评语" :span="2">
            {{ selectedGrade.comments || '暂无评语' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts, Reading, Star, Document, Search
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const grades = ref<any[]>([])
const searchQuery = ref('')
const selectedSemester = ref('')
const selectedCourse = ref('')
const selectedExamType = ref('')
const detailDialogVisible = ref(false)
const selectedGrade = ref<any>(null)

// 计算属性
const filteredGrades = computed(() => {
  let result = grades.value

  // 学期筛选
  if (selectedSemester.value) {
    result = result.filter(grade => grade.semester === selectedSemester.value)
  }

  // 课程筛选
  if (selectedCourse.value) {
    result = result.filter(grade => grade.course_name === selectedCourse.value)
  }

  // 考试类型筛选
  if (selectedExamType.value) {
    result = result.filter(grade => grade.exam_type === selectedExamType.value)
  }

  // 搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(grade =>
      grade.course_name.toLowerCase().includes(query) ||
      grade.course_code.toLowerCase().includes(query) ||
      grade.exam_type.toLowerCase().includes(query)
    )
  }

  return result
})

const groupedGrades = computed(() => {
  const groups = new Map()

  filteredGrades.value.forEach(grade => {
    if (!groups.has(grade.course_name)) {
      groups.set(grade.course_name, {
        courseName: grade.course_name,
        courseCode: grade.course_code,
        teacher: grade.teacher_name,
        average: 0,
        grades: []
      })
    }

    const group = groups.get(grade.course_name)
    group.grades.push(grade)
  })

  // 计算每门课的平均分
  groups.forEach(group => {
    const total = group.grades.reduce((sum: number, grade: any) => sum + parseFloat(grade.percentage), 0)
    group.average = (total / group.grades.length).toFixed(1)
  })

  return Array.from(groups.values())
})

const uniqueCourses = computed(() => {
  const courses = new Map()
  grades.value.forEach(grade => {
    if (!courses.has(grade.course_name)) {
      courses.set(grade.course_name, {
        course_name: grade.course_name,
        course_code: grade.course_code
      })
    }
  })
  return Array.from(courses.values())
})

const averageScore = computed(() => {
  if (grades.value.length === 0) return '0.0'
  const total = grades.value.reduce((sum, grade) => sum + parseFloat(grade.percentage), 0)
  return (total / grades.value.length).toFixed(1)
})

const excellentCount = computed(() => {
  return grades.value.filter(grade => {
    const percentage = parseFloat(grade.percentage)
    return percentage >= 90
  }).length
})

// 方法
const loadGrades = async () => {
  if (!userStore.userInfo?.id) return

  try {
    loading.value = true

    // 模拟数据，实际应该调用API
    const mockData = [
      {
        id: 1,
        student_id: userStore.userInfo.id,
        course_name: '计算机科学导论',
        course_code: 'CS101',
        teacher_name: '李教授',
        exam_type: '期中考试',
        score: 85,
        max_score: 100,
        percentage: 85.0,
        letter_grade: 'B+',
        gpa: 3.3,
        exam_date: '2024-11-15',
        semester: '2024-1',
        comments: '基础知识掌握扎实，实践能力良好',
        class_rank: 15,
        class_total: 60,
        grade_rank: 125,
        grade_total: 280
      },
      {
        id: 2,
        student_id: userStore.userInfo.id,
        course_name: '计算机科学导论',
        course_code: 'CS101',
        teacher_name: '李教授',
        exam_type: '期末考试',
        score: 88,
        max_score: 100,
        percentage: 88.0,
        letter_grade: 'A-',
        gpa: 3.7,
        exam_date: '2025-01-20',
        semester: '2024-1',
        comments: '期末表现优秀，综合能力强'
      },
      {
        id: 3,
        student_id: userStore.userInfo.id,
        course_name: '软件工程',
        course_code: 'SE201',
        teacher_name: '王教授',
        exam_type: '作业',
        score: 92,
        max_score: 100,
        percentage: 92.0,
        letter_grade: 'A-',
        gpa: 3.7,
        exam_date: '2024-10-28',
        semester: '2024-1',
        comments: '作业完成质量很高，代码规范'
      },
      {
        id: 4,
        student_id: userStore.userInfo.id,
        course_name: '软件工程',
        course_code: 'SE201',
        teacher_name: '王教授',
        exam_type: '项目',
        score: 95,
        max_score: 100,
        percentage: 95.0,
        letter_grade: 'A',
        gpa: 4.0,
        exam_date: '2024-12-10',
        semester: '2024-1',
        comments: '项目设计优秀，团队协作能力突出'
      },
      {
        id: 5,
        student_id: userStore.userInfo.id,
        course_name: '数据结构与算法',
        course_code: 'DS301',
        teacher_name: '张教授',
        exam_type: '测验',
        score: 78,
        max_score: 100,
        percentage: 78.0,
        letter_grade: 'B-',
        gpa: 2.7,
        exam_date: '2024-11-05',
        semester: '2024-1',
        comments: '算法思维需要进一步加强'
      },
      {
        id: 6,
        student_id: userStore.userInfo.id,
        course_name: '数据结构与算法',
        course_code: 'DS301',
        teacher_name: '张教授',
        exam_type: '期末考试',
        score: 82,
        max_score: 100,
        percentage: 82.0,
        letter_grade: 'B',
        gpa: 3.0,
        exam_date: '2025-01-18',
        semester: '2024-1',
        comments: '期末成绩有明显提升'
      }
    ]

    grades.value = mockData
  } catch (error) {
    console.error('获取成绩数据失败:', error)
    ElMessage.error('获取成绩数据失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  // 筛选变化时自动更新
}

const handleSearch = () => {
  // 搜索时自动更新
}

const viewGradeDetail = (grade: any) => {
  selectedGrade.value = grade
  detailDialogVisible.value = true
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

const formatDate = (dateString: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadGrades()
})
</script>

<style scoped>
.student-grade-view {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
  padding: 24px 0;
  border-bottom: 1px solid #e4e7ed;
}

.header-content h2 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.stats-overview {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  height: 100px;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.overview-card.average .card-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.overview-card.courses .card-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.overview-card.excellent .card-icon {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #ff6b6b;
}

.overview-card.total .card-icon {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #666;
}

.card-content {
  flex: 1;
}

.card-number {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.card-label {
  font-size: 14px;
  color: #909399;
}

.filter-card {
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.filter-left {
  display: flex;
  gap: 16px;
  align-items: center;
}

.grades-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-container,
.empty-container {
  padding: 60px 0;
  text-align: center;
}

.course-group {
  margin-bottom: 32px;
}

.course-group:last-child {
  margin-bottom: 0;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f2f5;
}

.course-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.course-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.course-code {
  background: #f0f2f5;
  color: #666;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.course-teacher {
  color: #909399;
  font-size: 14px;
}

.course-average {
  font-size: 16px;
  font-weight: 600;
  color: #409EFF;
}

.grade-table {
  margin-top: 16px;
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score-text {
  font-size: 18px;
  font-weight: 600;
}

.score-total {
  font-size: 14px;
  color: #909399;
}

.percentage-bar {
  display: flex;
  align-items: center;
  width: 100%;
  height: 20px;
  background: #f0f2f5;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.percentage-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.percentage-text {
  position: absolute;
  width: 100%;
  text-align: center;
  line-height: 20px;
  font-size: 12px;
  font-weight: 500;
  color: #303133;
}

.gpa-text {
  font-weight: 600;
  color: #409EFF;
}

.grade-detail {
  padding: 20px 0;
}

.detail-score {
  font-size: 18px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left {
    flex-wrap: wrap;
  }

  .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .course-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>