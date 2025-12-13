<template>
  <div class="reports-dashboard">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">报表中心</span>
      </template>
    </el-page-header>

    <!-- 快速统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card" @click="navigateToStudents">
          <div class="stat-content">
            <div class="stat-icon blue">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalStudents }}</div>
              <div class="stat-label">在校学生</div>
              <div class="stat-change positive">
                <el-icon><TrendCharts /></el-icon>
                +{{ stats.studentGrowth }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" @click="navigateToCourses">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalCourses }}</div>
              <div class="stat-label">开设课程</div>
              <div class="stat-change positive">
                <el-icon><TrendCharts /></el-icon>
                +{{ stats.courseGrowth }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" @click="navigateToEnrollments">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalEnrollments }}</div>
              <div class="stat-label">选课记录</div>
              <div class="stat-change positive">
                <el-icon><TrendCharts /></el-icon>
                +{{ stats.enrollmentGrowth }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" @click="navigateToGrades">
          <div class="stat-content">
            <div class="stat-icon purple">
              <el-icon><Medal /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.averageGrade }}%</div>
              <div class="stat-label">平均成绩</div>
              <div class="stat-change positive">
                <el-icon><TrendCharts /></el-icon>
                +{{ stats.gradeImprovement }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">学生选课趋势</span>
              <el-select v-model="chartFilter.semester" size="small" style="width: 120px">
                <el-option label="本学期" value="current" />
                <el-option label="上学期" value="last" />
                <el-option label="全年" value="year" />
              </el-select>
            </div>
          </template>
          <div ref="enrollmentTrendChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">成绩分布统计</span>
              <el-select v-model="chartFilter.courseType" size="small" style="width: 120px">
                <el-option label="全部课程" value="all" />
                <el-option label="必修课" value="required" />
                <el-option label="选修课" value="elective" />
              </el-select>
            </div>
          </template>
          <div ref="gradeDistributionChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">专业分布</span>
          </template>
          <div ref="majorDistributionChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">教师工作量</span>
          </template>
          <div ref="teacherWorkloadChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作和最近活动 -->
    <el-row :gutter="20" class="bottom-section">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span class="card-title">快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" icon="Document" @click="generateStudentReport">
              生成学生报表
            </el-button>
            <el-button type="success" icon="DataAnalysis" @click="generateGradeReport">
              成绩分析报表
            </el-button>
            <el-button type="warning" icon="TrendCharts" @click="generateEnrollmentReport">
              选课统计报表
            </el-button>
            <el-button type="info" icon="User" @click="generateTeacherReport">
              教师工作量报表
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card>
          <template #header>
            <span class="card-title">最近活动</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="activity.timestamp"
              :type="activity.type"
            >
              {{ activity.description }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, Reading, Document, Medal, TrendCharts, DataAnalysis
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

const enrollmentTrendChart = ref<HTMLElement>()
const gradeDistributionChart = ref<HTMLElement>()
const majorDistributionChart = ref<HTMLElement>()
const teacherWorkloadChart = ref<HTMLElement>()

const chartFilter = reactive({
  semester: 'current',
  courseType: 'all'
})

const stats = reactive({
  totalStudents: 1248,
  studentGrowth: 8.5,
  totalCourses: 86,
  courseGrowth: 12.3,
  totalEnrollments: 3456,
  enrollmentGrowth: 15.7,
  averageGrade: 78.5,
  gradeImprovement: 2.3
})

const recentActivities = ref([
  {
    id: 1,
    description: '系统管理员导出了《2024年春季学期学生成绩报表》',
    timestamp: '2024-02-20 14:30',
    type: 'primary'
  },
  {
    id: 2,
    description: '新选课批次开始，共有234名学生参与选课',
    timestamp: '2024-02-20 10:15',
    type: 'success'
  },
  {
    id: 3,
    description: '成绩录入截止，剩余5门课程未完成录入',
    timestamp: '2024-02-19 16:45',
    type: 'warning'
  },
  {
    id: 4,
    description: '系统自动备份完成，数据已安全存储',
    timestamp: '2024-02-19 02:00',
    type: 'info'
  },
  {
    id: 5,
    description: '新增3名教师信息录入系统',
    timestamp: '2024-02-18 14:20',
    type: 'success'
  }
])

const initCharts = () => {
  // 学生选课趋势图
  if (enrollmentTrendChart.value) {
    const chart = echarts.init(enrollmentTrendChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['选课人数', '完成选课'] },
      xAxis: {
        type: 'category',
        data: ['第1周', '第2周', '第3周', '第4周', '第5周', '第6周']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '选课人数',
          type: 'line',
          smooth: true,
          data: [120, 180, 350, 480, 520, 580],
          itemStyle: { color: '#5470c6' }
        },
        {
          name: '完成选课',
          type: 'line',
          smooth: true,
          data: [80, 150, 280, 380, 420, 480],
          itemStyle: { color: '#91cc75' }
        }
      ]
    }
    chart.setOption(option)
  }

  // 成绩分布统计
  if (gradeDistributionChart.value) {
    const chart = echarts.init(gradeDistributionChart.value)
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
          { value: 328, name: '优秀(90-100分)', itemStyle: { color: '#5470c6' } },
          { value: 456, name: '良好(80-89分)', itemStyle: { color: '#91cc75' } },
          { value: 289, name: '中等(70-79分)', itemStyle: { color: '#fac858' } },
          { value: 167, name: '及格(60-69分)', itemStyle: { color: '#ee6666' } },
          { value: 78, name: '不及格(0-59分)', itemStyle: { color: '#73c0de' } }
        ]
      }]
    }
    chart.setOption(option)
  }

  // 专业分布
  if (majorDistributionChart.value) {
    const chart = echarts.init(majorDistributionChart.value)
    const option = {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 420, name: '计算机科学与技术' },
          { value: 380, name: '软件工程' },
          { value: 289, name: '数据科学' },
          { value: 156, name: '人工智能' }
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

  // 教师工作量
  if (teacherWorkloadChart.value) {
    const chart = echarts.init(teacherWorkloadChart.value)
    const option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: {
        type: 'category',
        data: ['李明', '王芳', '张伟', '刘洋', '陈静', '赵强']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [120, 98, 86, 75, 65, 58],
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
}

const navigateToStudents = () => {
  router.push('/students')
}

const navigateToCourses = () => {
  router.push('/courses')
}

const navigateToEnrollments = () => {
  router.push('/enrollments')
}

const navigateToGrades = () => {
  router.push('/grades')
}

const generateStudentReport = () => {
  ElMessage.success('学生报表生成任务已提交，请稍后查看下载')
}

const generateGradeReport = () => {
  router.push('/reports/grade')
}

const generateEnrollmentReport = () => {
  router.push('/reports/enrollment')
}

const generateTeacherReport = () => {
  router.push('/reports/teacher')
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  nextTick(() => {
    initCharts()
  })
})
</script>

<style lang="scss" scoped>
.reports-dashboard {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .stats-cards {
    margin: 20px 0;

    .stat-card {
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
      }

      .stat-content {
        display: flex;
        align-items: center;

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
          .stat-number {
            font-size: 28px;
            font-weight: 700;
            color: var(--el-text-color-primary);
            line-height: 1;
          }

          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-regular);
            margin: 4px 0;
          }

          .stat-change {
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;

            .el-icon {
              font-size: 14px;
            }

            &.positive { color: var(--el-color-success); }
            &.negative { color: var(--el-color-danger); }
          }
        }
      }
    }
  }

  .chart-section {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .card-title {
        font-size: 16px;
        font-weight: 600;
      }
    }

    .chart-container {
      height: 300px;
    }
  }

  .bottom-section {
    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .quick-actions {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .el-button {
        justify-content: flex-start;
      }
    }
  }
}
</style>