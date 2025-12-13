<template>
  <div class="grade-statistics">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">成绩统计分析</span>
      </template>
    </el-page-header>

    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="学期">
          <el-select v-model="filterForm.semester" placeholder="选择学期" style="width: 150px">
            <el-option label="2024-春" value="2024-春" />
            <el-option label="2024-夏" value="2024-夏" />
            <el-option label="2024-秋" value="2024-秋" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程">
          <el-select v-model="filterForm.course_id" placeholder="全部课程" clearable style="width: 200px">
            <el-option
              v-for="course in courses"
              :key="course.value"
              :label="course.label"
              :value="course.value"
            />
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
            查询统计
          </el-button>
          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-overview">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon primary">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.totalStudents }}</div>
              <div class="stat-label">参与学生</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.averageScore.toFixed(1) }}</div>
              <div class="stat-label">平均分</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.passRate.toFixed(1) }}%</div>
              <div class="stat-label">及格率</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon danger">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.excellentRate.toFixed(1) }}%</div>
              <div class="stat-label">优秀率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">成绩分布图</span>
          </template>
          <div ref="distributionChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">班级成绩对比</span>
          </template>
          <div ref="classChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">课程成绩趋势</span>
          </template>
          <div ref="trendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">等级分布</span>
          </template>
          <div ref="levelChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细统计表格 -->
    <el-card class="detail-table">
      <template #header>
        <span class="card-title">详细统计数据</span>
      </template>
      <el-table :data="detailStats" stripe>
        <el-table-column label="课程编号" prop="course_code" width="120" />
        <el-table-column label="课程名称" prop="course_name" />
        <el-table-column label="参与人数" prop="student_count" width="100" />
        <el-table-column label="最高分" prop="max_score" width="100" />
        <el-table-column label="最低分" prop="min_score" width="100" />
        <el-table-column label="平均分" prop="average_score" width="100">
          <template #default="{ row }">
            <span :class="getScoreClass(row.average_score)">
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
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Download, User, TrendCharts, DataAnalysis, Trophy } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

interface Course {
  value: number
  label: string
  course_code: string
}

interface Class {
  value: number
  label: string
}

interface DetailStats {
  course_code: string
  course_name: string
  student_count: number
  max_score: number
  min_score: number
  average_score: number
  pass_rate: number
  excellent_rate: number
}

const distributionChart = ref<HTMLElement>()
const classChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()
const levelChart = ref<HTMLElement>()

const filterForm = reactive({
  semester: '2024-春',
  course_id: '',
  class_id: ''
})

const courses = ref<Course[]>([])
const classes = ref<Class[]>([])
const detailStats = ref<DetailStats[]>([])

const statistics = reactive({
  totalStudents: 0,
  averageScore: 0,
  passRate: 0,
  excellentRate: 0
})

const loadCourses = async () => {
  try {
    const mockCourses: Course[] = [
      { value: 1, label: '计算机科学导论', course_code: 'CS101' },
      { value: 2, label: '数据结构与算法', course_code: 'CS102' },
      { value: 3, label: '数据库系统', course_code: 'CS103' },
      { value: 4, label: '操作系统', course_code: 'CS104' }
    ]
    courses.value = mockCourses
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  }
}

const loadClasses = async () => {
  try {
    const mockClasses: Class[] = [
      { value: 1, label: '计算机科学1班' },
      { value: 2, label: '计算机科学2班' },
      { value: 3, label: '软件工程1班' },
      { value: 4, label: '软件工程2班' }
    ]
    classes.value = mockClasses
  } catch (error) {
    ElMessage.error('获取班级列表失败')
  }
}

const loadStatistics = async () => {
  try {
    // Mock API call - 替换为实际的API调用
    statistics.totalStudents = 156
    statistics.averageScore = 78.5
    statistics.passRate = 85.3
    statistics.excellentRate = 32.1

    const mockDetailStats: DetailStats[] = [
      {
        course_code: 'CS101',
        course_name: '计算机科学导论',
        student_count: 45,
        max_score: 98,
        min_score: 42,
        average_score: 76.8,
        pass_rate: 88.9,
        excellent_rate: 28.9
      },
      {
        course_code: 'CS102',
        course_name: '数据结构与算法',
        student_count: 38,
        max_score: 95,
        min_score: 38,
        average_score: 72.3,
        pass_rate: 81.6,
        excellent_rate: 23.7
      },
      {
        course_code: 'CS103',
        course_name: '数据库系统',
        student_count: 42,
        max_score: 99,
        min_score: 45,
        average_score: 82.1,
        pass_rate: 90.5,
        excellent_rate: 35.7
      },
      {
        course_code: 'CS104',
        course_name: '操作系统',
        student_count: 31,
        max_score: 97,
        min_score: 40,
        average_score: 79.6,
        pass_rate: 87.1,
        excellent_rate: 29.0
      }
    ]
    detailStats.value = mockDetailStats

    await nextTick()
    initCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

const initCharts = () => {
  // 成绩分布图
  if (distributionChart.value) {
    const chart = echarts.init(distributionChart.value)
    const option = {
      title: { text: '成绩分布', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['0-59', '60-69', '70-79', '80-89', '90-100']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [8, 15, 25, 18, 12],
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
  if (classChart.value) {
    const chart = echarts.init(classChart.value)
    const option = {
      title: { text: '班级平均分对比', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['计算机1班', '计算机2班', '软件1班', '软件2班']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [82.5, 76.8, 79.3, 74.2],
        type: 'bar',
        itemStyle: { color: '#5470c6' }
      }]
    }
    chart.setOption(option)
  }

  // 课程成绩趋势
  if (trendChart.value) {
    const chart = echarts.init(trendChart.value)
    const option = {
      title: { text: '学期成绩趋势', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['第1次', '第2次', '第3次', '期中', '第5次', '期末']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [75, 78, 76, 72, 80, 82],
        type: 'line',
        smooth: true,
        itemStyle: { color: '#91cc75' }
      }]
    }
    chart.setOption(option)
  }

  // 等级分布
  if (levelChart.value) {
    const chart = echarts.init(levelChart.value)
    const option = {
      title: { text: '成绩等级分布', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 12, name: '优秀(90-100)' },
          { value: 28, name: '良好(80-89)' },
          { value: 35, name: '中等(70-79)' },
          { value: 18, name: '及格(60-69)' },
          { value: 7, name: '不及格(0-59)' }
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
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'text-success font-bold'
  if (score >= 80) return 'text-primary'
  if (score >= 70) return 'text-warning'
  if (score >= 60) return 'text-info'
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
  loadStatistics()
}

const handleExport = () => {
  ElMessage.success('统计报告导出成功')
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadCourses()
  loadClasses()
  loadStatistics()
})
</script>

<style lang="scss" scoped>
.grade-statistics {
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

          &.primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
          &.success { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
          &.warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
          &.danger { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
        }

        .stat-info {
          .stat-value {
            font-size: 28px;
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

  .chart-row {
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .chart-container {
      height: 300px;
    }
  }

  .detail-table {
    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .text-success { color: var(--el-color-success); }
    .text-primary { color: var(--el-color-primary); }
    .text-warning { color: var(--el-color-warning); }
    .text-info { color: var(--el-color-info); }
    .text-danger { color: var(--el-color-danger); }
    .font-bold { font-weight: 600; }
  }
}
</style>