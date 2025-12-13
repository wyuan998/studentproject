<template>
  <div class="teacher-reports">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">教师报表</span>
      </template>
    </el-page-header>

    <!-- 筛选条件 -->
    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="学期">
          <el-select v-model="filterForm.semester" placeholder="选择学期" style="width: 150px">
            <el-option label="2024-春" value="2024-春" />
            <el-option label="2024-夏" value="2024-夏" />
            <el-option label="2024-秋" value="2024-秋" />
          </el-select>
        </el-form-item>
        <el-form-item label="学院">
          <el-select v-model="filterForm.college" placeholder="全部学院" clearable style="width: 150px">
            <el-option label="计算机学院" value="计算机学院" />
            <el-option label="软件学院" value="软件学院" />
            <el-option label="数据科学学院" value="数据科学学院" />
          </el-select>
        </el-form-item>
        <el-form-item label="职称">
          <el-select v-model="filterForm.title" placeholder="全部职称" clearable style="width: 150px">
            <el-option label="教授" value="教授" />
            <el-option label="副教授" value="副教授" />
            <el-option label="讲师" value="讲师" />
            <el-option label="助教" value="助教" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="handleExport" :loading="exportLoading">
            <el-icon><Download /></el-icon>
            导出报表
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-overview">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon blue">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.totalTeachers }}</div>
              <div class="stat-label">教师总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.avgCourses }}</div>
              <div class="stat-label">平均授课数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon><Users /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.totalStudents }}</div>
              <div class="stat-label">指导学生总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon purple">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.avgRating }}</div>
              <div class="stat-label">平均教学评分</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">职称分布</span>
          </template>
          <div ref="titleChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">学院分布</span>
          </template>
          <div ref="collegeChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span class="card-title">教师工作量统计</span>
          </template>
          <div ref="workloadChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span class="card-title">教学评分排行</span>
          </template>
          <div ref="ratingChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 教师详细数据表格 -->
    <el-card class="detail-table">
      <template #header>
        <div class="card-header">
          <span class="card-title">教师详细数据</span>
          <div class="table-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索工号/姓名"
              style="width: 200px; margin-right: 10px"
              clearable
              @input="handleSearch"
            />
            <el-button type="primary" @click="handleRefresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="tableLoading"
        :data="filteredTeachers"
        stripe
        style="width: 100%"
      >
        <el-table-column label="工号" prop="teacher_id" width="120" />
        <el-table-column label="姓名" prop="name" width="100" />
        <el-table-column label="性别" prop="gender" width="80" />
        <el-table-column label="职称" prop="title" width="100" />
        <el-table-column label="学院" prop="college" />
        <el-table-column label="授课数量" prop="course_count" width="100" />
        <el-table-column label="指导学生" prop="student_count" width="100" />
        <el-table-column label="总学时" prop="total_hours" width="100" />
        <el-table-column label="教学评分" width="100">
          <template #default="{ row }">
            <el-rate
              v-model="row.rating"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}"
            />
          </template>
        </el-table-column>
        <el-table-column label="科研积分" prop="research_points" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleViewDetail(row)"
            >
              详情
            </el-button>
            <el-button
              size="small"
              type="success"
              @click="handleGenerateIndividualReport(row)"
            >
              个人报表
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
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 教师详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentTeacher?.name + ' - 详细信息'"
      width="900px"
    >
      <div v-if="currentTeacher" class="teacher-detail">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="工号">{{ currentTeacher.teacher_id }}</el-descriptions-item>
              <el-descriptions-item label="姓名">{{ currentTeacher.name }}</el-descriptions-item>
              <el-descriptions-item label="性别">{{ currentTeacher.gender }}</el-descriptions-item>
              <el-descriptions-item label="出生日期">{{ currentTeacher.birth_date }}</el-descriptions-item>
              <el-descriptions-item label="职称">{{ currentTeacher.title }}</el-descriptions-item>
              <el-descriptions-item label="学历">{{ currentTeacher.education }}</el-descriptions-item>
              <el-descriptions-item label="学院">{{ currentTeacher.college }}</el-descriptions-item>
              <el-descriptions-item label="专业">{{ currentTeacher.major }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{ currentTeacher.phone }}</el-descriptions-item>
              <el-descriptions-item label="邮箱">{{ currentTeacher.email }}</el-descriptions-item>
              <el-descriptions-item label="入职日期">{{ currentTeacher.hire_date }}</el-descriptions-item>
              <el-descriptions-item label="工作年限">{{ currentTeacher.work_years }}年</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="教学情况" name="teaching">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="授课数量">{{ currentTeacher.course_count }}</el-descriptions-item>
              <el-descriptions-item label="总学时">{{ currentTeacher.total_hours }}</el-descriptions-item>
              <el-descriptions-item label="指导学生">{{ currentTeacher.student_count }}</el-descriptions-item>
              <el-descriptions-item label="教学评分">{{ currentTeacher.rating }}/5.0</el-descriptions-item>
              <el-descriptions-item label="优秀课程">{{ currentTeacher.excellent_courses }}</el-descriptions-item>
              <el-descriptions-item label="教学奖项">{{ currentTeacher.teaching_awards }}</el-descriptions-item>
            </el-descriptions>

            <div style="margin-top: 20px;">
              <h4>本学期授课课程</h4>
              <el-table :data="currentTeacher.courses" size="small">
                <el-table-column label="课程编号" prop="course_code" width="120" />
                <el-table-column label="课程名称" prop="course_name" />
                <el-table-column label="学时" prop="hours" width="80" />
                <el-table-column label="学生人数" prop="student_count" width="100" />
                <el-table-column label="评分" prop="rating" width="100">
                  <template #default="{ row }">
                    <el-tag type="success">{{ row.rating }}/5.0</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="科研情况" name="research">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="科研积分">{{ currentTeacher.research_points }}</el-descriptions-item>
              <el-descriptions-item label="发表论文">{{ currentTeacher.papers }}</el-descriptions-item>
              <el-descriptions-item label="主持项目">{{ currentTeacher.projects }}</el-descriptions-item>
              <el-descriptions-item label="科研经费">{{ currentTeacher.funding }}万元</el-descriptions-item>
              <el-descriptions-item label="专利申请">{{ currentTeacher.patents }}</el-descriptions-item>
              <el-descriptions-item label="学术兼职">{{ currentTeacher.academic_positions }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleGenerateIndividualReport(currentTeacher!)">
          生成个人报表
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Download, User, Reading, Users, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

interface Teacher {
  id: number
  teacher_id: string
  name: string
  gender: string
  birth_date: string
  title: string
  education: string
  college: string
  major: string
  phone: string
  email: string
  hire_date: string
  work_years: number
  course_count: number
  student_count: number
  total_hours: number
  rating: number
  research_points: number
  papers: number
  projects: number
  funding: number
  patents: number
  academic_positions: number
  excellent_courses: number
  teaching_awards: number
  courses: Array<{
    course_code: string
    course_name: string
    hours: number
    student_count: number
    rating: number
  }>
}

const titleChart = ref<HTMLElement>()
const collegeChart = ref<HTMLElement>()
const workloadChart = ref<HTMLElement>()
const ratingChart = ref<HTMLElement>()

const tableLoading = ref(false)
const exportLoading = ref(false)
const detailDialogVisible = ref(false)
const currentTeacher = ref<Teacher | null>(null)
const activeTab = ref('basic')
const searchKeyword = ref('')

const filterForm = reactive({
  semester: '2024-春',
  college: '',
  title: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const reportStats = reactive({
  totalTeachers: 156,
  avgCourses: 2.8,
  totalStudents: 1248,
  avgRating: 4.3
})

const teachers = ref<Teacher[]>([])

const filteredTeachers = computed(() => {
  if (!searchKeyword.value) return teachers.value

  return teachers.value.filter(teacher =>
    teacher.teacher_id.includes(searchKeyword.value) ||
    teacher.name.includes(searchKeyword.value)
  )
})

const loadTeachers = async () => {
  try {
    tableLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockTeachers: Teacher[] = [
      {
        id: 1,
        teacher_id: 'T001',
        name: '李明',
        gender: '男',
        birth_date: '1980-05-15',
        title: '教授',
        education: '博士',
        college: '计算机学院',
        major: '计算机科学',
        phone: '13800138001',
        email: 'liming@university.edu.cn',
        hire_date: '2005-09-01',
        work_years: 18,
        course_count: 3,
        student_count: 86,
        total_hours: 144,
        rating: 4.7,
        research_points: 156,
        papers: 23,
        projects: 5,
        funding: 128.5,
        patents: 3,
        academic_positions: 2,
        excellent_courses: 8,
        teaching_awards: 5,
        courses: [
          { course_code: 'CS101', course_name: '计算机科学导论', hours: 48, student_count: 45, rating: 4.6 },
          { course_code: 'CS102', course_name: '数据结构与算法', hours: 64, student_count: 38, rating: 4.8 },
          { course_code: 'CS201', course_name: '高级算法设计', hours: 32, student_count: 25, rating: 4.7 }
        ]
      },
      {
        id: 2,
        teacher_id: 'T002',
        name: '王芳',
        gender: '女',
        birth_date: '1985-08-20',
        title: '副教授',
        education: '博士',
        college: '软件学院',
        major: '软件工程',
        phone: '13800138002',
        email: 'wangfang@university.edu.cn',
        hire_date: '2010-03-01',
        work_years: 13,
        course_count: 2,
        student_count: 64,
        total_hours: 96,
        rating: 4.5,
        research_points: 98,
        papers: 15,
        projects: 3,
        funding: 86.2,
        patents: 2,
        academic_positions: 1,
        excellent_courses: 5,
        teaching_awards: 3,
        courses: [
          { course_code: 'SE101', course_name: '软件工程导论', hours: 48, student_count: 42, rating: 4.4 },
          { course_code: 'SE201', course_name: '软件测试', hours: 48, student_count: 35, rating: 4.6 }
        ]
      },
      {
        id: 3,
        teacher_id: 'T003',
        name: '张伟',
        gender: '男',
        birth_date: '1988-03-10',
        title: '讲师',
        education: '博士',
        college: '数据科学学院',
        major: '数据科学',
        phone: '13800138003',
        email: 'zhangwei@university.edu.cn',
        hire_date: '2015-09-01',
        work_years: 8,
        course_count: 4,
        student_count: 128,
        total_hours: 192,
        rating: 4.2,
        research_points: 67,
        papers: 8,
        projects: 2,
        funding: 45.8,
        patents: 1,
        academic_positions: 0,
        excellent_courses: 3,
        teaching_awards: 1,
        courses: [
          { course_code: 'DS101', course_name: '数据科学基础', hours: 48, student_count: 45, rating: 4.1 },
          { course_code: 'DS102', course_name: '机器学习', hours: 64, student_count: 38, rating: 4.3 },
          { course_code: 'DS201', course_name: '深度学习', hours: 48, student_count: 28, rating: 4.2 },
          { course_code: 'DS202', course_name: '自然语言处理', hours: 32, student_count: 17, rating: 4.0 }
        ]
      }
    ]

    teachers.value = mockTeachers
    pagination.total = mockTeachers.length
  } catch (error) {
    ElMessage.error('获取教师数据失败')
  } finally {
    tableLoading.value = false
  }
}

const initCharts = () => {
  // 职称分布图
  if (titleChart.value) {
    const chart = echarts.init(titleChart.value)
    const option = {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 25, name: '教授' },
          { value: 38, name: '副教授' },
          { value: 65, name: '讲师' },
          { value: 28, name: '助教' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
    chart.setOption(option)
  }

  // 学院分布图
  if (collegeChart.value) {
    const chart = echarts.init(collegeChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['计算机学院', '软件学院', '数据科学学院', '人工智能学院']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [45, 38, 42, 31],
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }]
    }
    chart.setOption(option)
  }

  // 教师工作量统计
  if (workloadChart.value) {
    const chart = echarts.init(workloadChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['授课数量', '总学时', '指导学生'] },
      xAxis: {
        type: 'category',
        data: ['李明', '王芳', '张伟', '刘洋', '陈静', '赵强']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '授课数量',
          type: 'bar',
          data: [3, 2, 4, 2, 3, 1],
          itemStyle: { color: '#5470c6' }
        },
        {
          name: '总学时',
          type: 'bar',
          data: [144, 96, 192, 80, 128, 48],
          itemStyle: { color: '#91cc75' }
        },
        {
          name: '指导学生',
          type: 'bar',
          data: [86, 64, 128, 45, 72, 25],
          itemStyle: { color: '#fac858' }
        }
      ]
    }
    chart.setOption(option)
  }

  // 教学评分排行
  if (ratingChart.value) {
    const chart = echarts.init(ratingChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'value',
        min: 4,
        max: 5,
        interval: 0.1
      },
      yAxis: {
        type: 'category',
        data: ['李明', '王芳', '张伟', '刘洋', '陈静', '赵强']
      },
      series: [{
        type: 'bar',
        data: [4.7, 4.5, 4.2, 4.6, 4.3, 4.1],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#ff9a76' },
            { offset: 1, color: '#ff6b6b' }
          ])
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}'
        }
      }]
    }
    chart.setOption(option)
  }
}

const handleSearch = () => {
  loadTeachers()
}

const handleReset = () => {
  filterForm.college = ''
  filterForm.title = ''
  searchKeyword.value = ''
  loadTeachers()
}

const handleRefresh = () => {
  loadTeachers()
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('教师报表导出成功')
  } catch (error) {
    ElMessage.error('报表导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleViewDetail = (teacher: Teacher) => {
  currentTeacher.value = teacher
  detailDialogVisible.value = true
  activeTab.value = 'basic'
}

const handleGenerateIndividualReport = async (teacher: Teacher) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success(`${teacher.name} 的个人报表生成成功`)
  } catch (error) {
    ElMessage.error('个人报表生成失败')
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadTeachers()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadTeachers()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadTeachers()
  nextTick(() => {
    initCharts()
  })
})
</script>

<style lang="scss" scoped>
.teacher-reports {
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

  .stats-overview {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        padding: 10px 0;

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;

          .el-icon {
            font-size: 28px;
            color: white;
          }

          &.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
          &.green { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
          &.orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
          &.purple { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
        }

        .stat-info {
          .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--el-text-color-primary);
            line-height: 1;
          }

          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-regular);
            margin-top: 4px;
          }
        }
      }
    }
  }

  .chart-section {
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .chart-container {
      height: 300px;
    }

    .chart-container-large {
      height: 400px;
    }
  }

  .detail-table {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 16px;
        font-weight: 600;
      }

      .table-actions {
        display: flex;
        align-items: center;
      }
    }
  }

  .teacher-detail {
    h4 {
      margin-bottom: 16px;
      color: var(--el-text-color-primary);
    }
  }
}
</style>