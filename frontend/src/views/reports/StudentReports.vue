<template>
  <div class="student-reports">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">学生报表</span>
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
        <el-form-item label="专业">
          <el-select v-model="filterForm.major" placeholder="全部专业" clearable style="width: 150px">
            <el-option label="计算机科学" value="计算机科学" />
            <el-option label="软件工程" value="软件工程" />
            <el-option label="数据科学" value="数据科学" />
            <el-option label="人工智能" value="人工智能" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="filterForm.class_id" placeholder="全部班级" clearable style="width: 150px">
            <el-option
              v-for="cls in classes"
              :key="cls.value"
              :label="cls.label"
              :value="cls.value"
            />
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
              <div class="stat-value">{{ reportStats.totalStudents }}</div>
              <div class="stat-label">学生总数</div>
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
              <div class="stat-value">{{ reportStats.avgCredits }}</div>
              <div class="stat-label">平均学分</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.avgGrade }}%</div>
              <div class="stat-label">平均成绩</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon purple">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.excellentRate }}%</div>
              <div class="stat-label">优秀率</div>
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
            <span class="card-title">专业分布</span>
          </template>
          <div ref="majorChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">年级分布</span>
          </template>
          <div ref="gradeChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span class="card-title">班级成绩对比</span>
          </template>
          <div ref="classPerformanceChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学生详细数据表格 -->
    <el-card class="detail-table">
      <template #header>
        <div class="card-header">
          <span class="card-title">学生详细数据</span>
          <div class="table-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索学号/姓名"
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
        :data="filteredStudents"
        stripe
        style="width: 100%"
      >
        <el-table-column label="学号" prop="student_no" width="120" />
        <el-table-column label="姓名" prop="name" width="100" />
        <el-table-column label="性别" prop="gender" width="80" />
        <el-table-column label="专业" prop="major" />
        <el-table-column label="班级" prop="class_name" width="120" />
        <el-table-column label="已修学分" prop="credits" width="100" />
        <el-table-column label="平均成绩" width="100">
          <template #default="{ row }">
            <span :class="getGradeClass(row.average_grade)">
              {{ row.average_grade }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="选课数量" prop="course_count" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
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

    <!-- 学生详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentStudent?.name + ' - 详细信息'"
      width="800px"
    >
      <div v-if="currentStudent" class="student-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学号">{{ currentStudent.student_no }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ currentStudent.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ currentStudent.gender }}</el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ currentStudent.birth_date }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ currentStudent.major }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ currentStudent.class_name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentStudent.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentStudent.email }}</el-descriptions-item>
          <el-descriptions-item label="入学日期">{{ currentStudent.enrollment_date }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentStudent.status)">
              {{ getStatusText(currentStudent.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="academic-info" style="margin-top: 20px;">
          <h4>学业信息</h4>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="已修学分">{{ currentStudent.credits }}</el-descriptions-item>
            <el-descriptions-item label="选课数量">{{ currentStudent.course_count }}</el-descriptions-item>
            <el-descriptions-item label="平均成绩">{{ currentStudent.average_grade }}%</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleGenerateIndividualReport(currentStudent!)">
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
import { Search, Download, User, Reading, TrendCharts, Trophy } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

interface Class {
  value: number
  label: string
}

interface Student {
  id: number
  student_no: string
  name: string
  gender: string
  birth_date: string
  major: string
  class_name: string
  phone: string
  email: string
  enrollment_date: string
  status: string
  credits: number
  course_count: number
  average_grade: number
}

const majorChart = ref<HTMLElement>()
const gradeChart = ref<HTMLElement>()
const classPerformanceChart = ref<HTMLElement>()

const tableLoading = ref(false)
const exportLoading = ref(false)
const detailDialogVisible = ref(false)
const currentStudent = ref<Student | null>(null)
const searchKeyword = ref('')

const filterForm = reactive({
  semester: '2024-春',
  major: '',
  class_id: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const reportStats = reactive({
  totalStudents: 1248,
  avgCredits: 68.5,
  avgGrade: 78.3,
  excellentRate: 25.7
})

const classes = ref<Class[]>([])
const students = ref<Student[]>([])

const filteredStudents = computed(() => {
  if (!searchKeyword.value) return students.value

  return students.value.filter(student =>
    student.student_no.includes(searchKeyword.value) ||
    student.name.includes(searchKeyword.value)
  )
})

const loadClasses = async () => {
  try {
    const mockClasses: Class[] = [
      { value: 1, label: '计算机科学1班' },
      { value: 2, label: '计算机科学2班' },
      { value: 3, label: '软件工程1班' },
      { value: 4, label: '软件工程2班' },
      { value: 5, label: '数据科学1班' },
      { value: 6, label: '人工智能1班' }
    ]
    classes.value = mockClasses
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  }
}

const loadStudents = async () => {
  try {
    tableLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockStudents: Student[] = [
      {
        id: 1,
        student_no: 'S2021001',
        name: '张三',
        gender: '男',
        birth_date: '2002-05-15',
        major: '计算机科学',
        class_name: '计算机科学1班',
        phone: '13800138001',
        email: 'zhangsan@example.com',
        enrollment_date: '2021-09-01',
        status: 'active',
        credits: 72,
        course_count: 18,
        average_grade: 85.6
      },
      {
        id: 2,
        student_no: 'S2021002',
        name: '李四',
        gender: '女',
        birth_date: '2002-08-20',
        major: '软件工程',
        class_name: '软件工程1班',
        phone: '13800138002',
        email: 'lisi@example.com',
        enrollment_date: '2021-09-01',
        status: 'active',
        credits: 68,
        course_count: 17,
        average_grade: 92.3
      },
      {
        id: 3,
        student_no: 'S2021003',
        name: '王五',
        gender: '男',
        birth_date: '2002-03-10',
        major: '数据科学',
        class_name: '数据科学1班',
        phone: '13800138003',
        email: 'wangwu@example.com',
        enrollment_date: '2021-09-01',
        status: 'active',
        credits: 65,
        course_count: 16,
        average_grade: 78.9
      }
    ]

    students.value = mockStudents
    pagination.total = mockStudents.length
  } catch (error) {
    ElMessage.error('获取学生数据失败')
  } finally {
    tableLoading.value = false
  }
}

const initCharts = () => {
  // 专业分布图
  if (majorChart.value) {
    const chart = echarts.init(majorChart.value)
    const option = {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 420, name: '计算机科学与技术' },
          { value: 380, name: '软件工程' },
          { value: 289, name: '数据科学' },
          { value: 159, name: '人工智能' }
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

  // 年级分布图
  if (gradeChart.value) {
    const chart = echarts.init(gradeChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['2021级', '2022级', '2023级', '2024级']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [320, 289, 256, 383],
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

  // 班级成绩对比
  if (classPerformanceChart.value) {
    const chart = echarts.init(classPerformanceChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['平均成绩', '最高成绩', '最低成绩'] },
      xAxis: {
        type: 'category',
        data: ['计算机1班', '计算机2班', '软件1班', '软件2班', '数据1班', '人工智能1班']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '平均成绩',
          type: 'line',
          smooth: true,
          data: [85.6, 82.3, 88.7, 79.4, 83.2, 86.5],
          itemStyle: { color: '#5470c6' }
        },
        {
          name: '最高成绩',
          type: 'line',
          smooth: true,
          data: [98, 96, 99, 95, 97, 98],
          itemStyle: { color: '#91cc75' }
        },
        {
          name: '最低成绩',
          type: 'line',
          smooth: true,
          data: [65, 62, 70, 58, 68, 66],
          itemStyle: { color: '#fac858' }
        }
      ]
    }
    chart.setOption(option)
  }
}

const getGradeClass = (grade: number) => {
  if (grade >= 90) return 'text-success font-bold'
  if (grade >= 80) return 'text-primary'
  if (grade >= 70) return 'text-warning'
  if (grade >= 60) return 'text-info'
  return 'text-danger'
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    graduated: 'primary',
    suspended: 'warning',
    dropped: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    active: '在读',
    graduated: '已毕业',
    suspended: '休学',
    dropped: '退学'
  }
  return textMap[status] || status
}

const handleSearch = () => {
  loadStudents()
}

const handleReset = () => {
  filterForm.major = ''
  filterForm.class_id = ''
  searchKeyword.value = ''
  loadStudents()
}

const handleRefresh = () => {
  loadStudents()
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('学生报表导出成功')
  } catch (error) {
    ElMessage.error('报表导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleViewDetail = (student: Student) => {
  currentStudent.value = student
  detailDialogVisible.value = true
}

const handleGenerateIndividualReport = async (student: Student) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success(`${student.name} 的个人报表生成成功`)
  } catch (error) {
    ElMessage.error('个人报表生成失败')
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadStudents()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadStudents()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadClasses()
  loadStudents()
  nextTick(() => {
    initCharts()
  })
})
</script>

<style lang="scss" scoped>
.student-reports {
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

    .text-success { color: var(--el-color-success); }
    .text-primary { color: var(--el-color-primary); }
    .text-warning { color: var(--el-color-warning); }
    .text-info { color: var(--el-color-info); }
    .text-danger { color: var(--el-color-danger); }
    .font-bold { font-weight: 600; }
  }

  .student-detail {
    .academic-info {
      h4 {
        margin-bottom: 16px;
        color: var(--el-text-color-primary);
      }
    }
  }
}
</style>