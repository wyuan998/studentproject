<template>
  <div class="grade-reports">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">成绩报表</span>
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
        <el-form-item label="课程类型">
          <el-select v-model="filterForm.course_type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="必修课" value="required" />
            <el-option label="选修课" value="elective" />
          </el-select>
        </el-form-item>
        <el-form-item label="专业">
          <el-select v-model="filterForm.major" placeholder="全部专业" clearable style="width: 150px">
            <el-option label="计算机科学" value="计算机科学" />
            <el-option label="软件工程" value="软件工程" />
            <el-option label="数据科学" value="数据科学" />
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
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.totalRecords }}</div>
              <div class="stat-label">成绩记录总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.averageGrade }}%</div>
              <div class="stat-label">整体平均分</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.passRate }}%</div>
              <div class="stat-label">整体及格率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon purple">
              <el-icon><Medal /></el-icon>
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
            <span class="card-title">成绩分布统计</span>
          </template>
          <div ref="distributionChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">各专业平均分对比</span>
          </template>
          <div ref="majorChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span class="card-title">课程成绩分析</span>
          </template>
          <div ref="courseChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 成绩详细数据表格 -->
    <el-card class="detail-table">
      <template #header>
        <div class="card-header">
          <span class="card-title">课程成绩详细数据</span>
          <div class="table-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索课程名称/编号"
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
        :data="filteredGradeData"
        stripe
        style="width: 100%"
      >
        <el-table-column label="课程编号" prop="course_code" width="120" />
        <el-table-column label="课程名称" prop="course_name" min-width="200" />
        <el-table-column label="授课教师" prop="teacher_name" width="100" />
        <el-table-column label="学生人数" prop="student_count" width="100" />
        <el-table-column label="最高分" prop="max_score" width="100" />
        <el-table-column label="最低分" prop="min_score" width="100" />
        <el-table-column label="平均分" width="100">
          <template #default="{ row }">
            <span :class="getGradeClass(row.average_score)">
              {{ row.average_score.toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="及格率" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.pass_rate"
              :color="getProgressColor(row.pass_rate)"
              :show-text="false"
              style="width: 60px;"
            />
            <span style="margin-left: 8px;">{{ row.pass_rate.toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="优秀率" width="100">
          <template #default="{ row }">
            <span class="text-success">{{ row.excellent_rate.toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleViewDetail(row)"
            >
              详细分析
            </el-button>
            <el-button
              size="small"
              type="success"
              @click="handleGenerateCourseReport(row)"
            >
              课程报表
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

    <!-- 课程详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentCourse?.course_name + ' - 成绩分析'"
      width="900px"
    >
      <div v-if="currentCourse" class="course-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-descriptions title="基本信息" :column="1" border>
              <el-descriptions-item label="课程编号">{{ currentCourse.course_code }}</el-descriptions-item>
              <el-descriptions-item label="课程名称">{{ currentCourse.course_name }}</el-descriptions-item>
              <el-descriptions-item label="授课教师">{{ currentCourse.teacher_name }}</el-descriptions-item>
              <el-descriptions-item label="学生人数">{{ currentCourse.student_count }}</el-descriptions-item>
              <el-descriptions-item label="学分">{{ currentCourse.credits }}</el-descriptions-item>
              <el-descriptions-item label="学时">{{ currentCourse.hours }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <el-descriptions title="成绩统计" :column="1" border>
              <el-descriptions-item label="平均分">{{ currentCourse.average_score.toFixed(1) }}</el-descriptions-item>
              <el-descriptions-item label="最高分">{{ currentCourse.max_score }}</el-descriptions-item>
              <el-descriptions-item label="最低分">{{ currentCourse.min_score }}</el-descriptions-item>
              <el-descriptions-item label="及格率">{{ currentCourse.pass_rate.toFixed(1) }}%</el-descriptions-item>
              <el-descriptions-item label="优秀率">{{ currentCourse.excellent_rate.toFixed(1) }}%</el-descriptions-item>
              <el-descriptions-item label="标准差">{{ currentCourse.std_deviation.toFixed(2) }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>

        <div class="grade-distribution" style="margin-top: 20px;">
          <h4>成绩分布详情</h4>
          <el-row :gutter="20">
            <el-col :span="6" v-for="(item, index) in gradeDistribution" :key="index">
              <div class="grade-item">
                <div class="grade-label">{{ item.label }}</div>
                <div class="grade-count">{{ item.count }}人</div>
                <div class="grade-percent">{{ ((item.count / currentCourse.student_count) * 100).toFixed(1) }}%</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleGenerateCourseReport(currentCourse!)">
          生成课程报表
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Download, Document, TrendCharts, Trophy, Medal } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

interface GradeData {
  id: number
  course_code: string
  course_name: string
  teacher_name: string
  student_count: number
  max_score: number
  min_score: number
  average_score: number
  pass_rate: number
  excellent_rate: number
  credits: number
  hours: number
  std_deviation: number
}

const distributionChart = ref<HTMLElement>()
const majorChart = ref<HTMLElement>()
const courseChart = ref<HTMLElement>()

const tableLoading = ref(false)
const exportLoading = ref(false)
const detailDialogVisible = ref(false)
const currentCourse = ref<GradeData | null>(null)
const searchKeyword = ref('')

const filterForm = reactive({
  semester: '2024-春',
  course_type: '',
  major: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const reportStats = reactive({
  totalRecords: 3456,
  averageGrade: 78.5,
  passRate: 85.3,
  excellentRate: 25.7
})

const gradeData = ref<GradeData[]>([])

const filteredGradeData = computed(() => {
  if (!searchKeyword.value) return gradeData.value

  return gradeData.value.filter(data =>
    data.course_code.includes(searchKeyword.value) ||
    data.course_name.includes(searchKeyword.value)
  )
})

const gradeDistribution = computed(() => {
  if (!currentCourse.value) return []

  return [
    { label: '优秀(90-100)', count: Math.floor(currentCourse.value.student_count * 0.25) },
    { label: '良好(80-89)', count: Math.floor(currentCourse.value.student_count * 0.35) },
    { label: '中等(70-79)', count: Math.floor(currentCourse.value.student_count * 0.25) },
    { label: '及格(60-69)', count: Math.floor(currentCourse.value.student_count * 0.10) },
    { label: '不及格(0-59)', count: Math.floor(currentCourse.value.student_count * 0.05) }
  ]
})

const loadGradeData = async () => {
  try {
    tableLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockGradeData: GradeData[] = [
      {
        id: 1,
        course_code: 'CS101',
        course_name: '计算机科学导论',
        teacher_name: '李明',
        student_count: 45,
        max_score: 98,
        min_score: 42,
        average_score: 76.8,
        pass_rate: 88.9,
        excellent_rate: 28.9,
        credits: 3,
        hours: 48,
        std_deviation: 12.5
      },
      {
        id: 2,
        course_code: 'CS102',
        course_name: '数据结构与算法',
        teacher_name: '王芳',
        student_count: 38,
        max_score: 95,
        min_score: 38,
        average_score: 72.3,
        pass_rate: 81.6,
        excellent_rate: 23.7,
        credits: 4,
        hours: 64,
        std_deviation: 15.2
      },
      {
        id: 3,
        course_code: 'CS103',
        course_name: '数据库系统',
        teacher_name: '张伟',
        student_count: 42,
        max_score: 99,
        min_score: 45,
        average_score: 82.1,
        pass_rate: 90.5,
        excellent_rate: 35.7,
        credits: 3,
        hours: 48,
        std_deviation: 10.8
      }
    ]

    gradeData.value = mockGradeData
    pagination.total = mockGradeData.length
  } catch (error) {
    ElMessage.error('获取成绩数据失败')
  } finally {
    tableLoading.value = false
  }
}

const initCharts = () => {
  // 成绩分布统计
  if (distributionChart.value) {
    const chart = echarts.init(distributionChart.value)
    const option = {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold'
          }
        },
        labelLine: { show: false },
        data: [
          { value: 868, name: '优秀(90-100分)', itemStyle: { color: '#5470c6' } },
          { value: 1209, name: '良好(80-89分)', itemStyle: { color: '#91cc75' } },
          { value: 864, name: '中等(70-79分)', itemStyle: { color: '#fac858' } },
          { value: 346, name: '及格(60-69分)', itemStyle: { color: '#ee6666' } },
          { value: 169, name: '不及格(0-59分)', itemStyle: { color: '#73c0de' } }
        ]
      }]
    }
    chart.setOption(option)
  }

  // 各专业平均分对比
  if (majorChart.value) {
    const chart = echarts.init(majorChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['计算机科学', '软件工程', '数据科学', '人工智能']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [78.5, 76.2, 82.3, 74.8],
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

  // 课程成绩分析
  if (courseChart.value) {
    const chart = echarts.init(courseChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['平均分', '最高分', '最低分', '及格率'] },
      xAxis: {
        type: 'category',
        data: gradeData.value.map(item => item.course_code + ' ' + item.course_name)
      },
      yAxis: [
        { type: 'value', name: '分数', min: 0, max: 100 },
        { type: 'value', name: '及格率(%)', min: 0, max: 100 }
      ],
      series: [
        {
          name: '平均分',
          type: 'line',
          yAxisIndex: 0,
          data: gradeData.value.map(item => item.average_score),
          itemStyle: { color: '#5470c6' }
        },
        {
          name: '最高分',
          type: 'line',
          yAxisIndex: 0,
          data: gradeData.value.map(item => item.max_score),
          itemStyle: { color: '#91cc75' }
        },
        {
          name: '最低分',
          type: 'line',
          yAxisIndex: 0,
          data: gradeData.value.map(item => item.min_score),
          itemStyle: { color: '#fac858' }
        },
        {
          name: '及格率',
          type: 'bar',
          yAxisIndex: 1,
          data: gradeData.value.map(item => item.pass_rate),
          itemStyle: { color: '#ee6666' }
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

const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 80) return '#409eff'
  if (percentage >= 70) return '#e6a23c'
  if (percentage >= 60) return '#f56c6c'
  return '#f56c6c'
}

const handleSearch = () => {
  loadGradeData()
}

const handleReset = () => {
  filterForm.course_type = ''
  filterForm.major = ''
  searchKeyword.value = ''
  loadGradeData()
}

const handleRefresh = () => {
  loadGradeData()
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('成绩报表导出成功')
  } catch (error) {
    ElMessage.error('报表导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleViewDetail = (course: GradeData) => {
  currentCourse.value = course
  detailDialogVisible.value = true
}

const handleGenerateCourseReport = async (course: GradeData) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success(`${course.course_name} 的成绩报表生成成功`)
  } catch (error) {
    ElMessage.error('课程报表生成失败')
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadGradeData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadGradeData()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadGradeData()
  nextTick(() => {
    initCharts()
  })
})
</script>

<style lang="scss" scoped>
.grade-reports {
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

  .course-detail {
    .grade-distribution {
      h4 {
        margin-bottom: 16px;
        color: var(--el-text-color-primary);
      }

      .grade-item {
        text-align: center;
        padding: 16px;
        background-color: var(--el-fill-color-light);
        border-radius: 8px;

        .grade-label {
          font-size: 14px;
          color: var(--el-text-color-regular);
          margin-bottom: 8px;
        }

        .grade-count {
          font-size: 24px;
          font-weight: 700;
          color: var(--el-color-primary);
          margin-bottom: 4px;
        }

        .grade-percent {
          font-size: 14px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }
}
</style>