<template>
  <div class="enrollment-reports">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">选课报表</span>
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
        <el-form-item label="选课状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
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
              <div class="stat-value">{{ reportStats.totalEnrollments }}</div>
              <div class="stat-label">选课申请总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon green">
              <el-icon><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.approvedCount }}</div>
              <div class="stat-label">已批准数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orange">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reportStats.pendingCount }}</div>
              <div class="stat-label">待审批数量</div>
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
              <div class="stat-value">{{ reportStats.approvalRate }}%</div>
              <div class="stat-label">批准率</div>
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
            <span class="card-title">选课状态分布</span>
          </template>
          <div ref="statusChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">各专业选课统计</span>
          </template>
          <div ref="majorChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span class="card-title">选课趋势分析</span>
          </template>
          <div ref="trendChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-section">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span class="card-title">热门课程排行</span>
          </template>
          <div ref="popularCoursesChart" class="chart-container-large"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 选课详细数据表格 -->
    <el-card class="detail-table">
      <template #header>
        <div class="card-header">
          <span class="card-title">选课记录详细数据</span>
          <div class="table-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索学号/姓名/课程"
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
        :data="filteredEnrollments"
        stripe
        style="width: 100%"
      >
        <el-table-column label="申请时间" prop="created_at" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="学号" prop="student_no" width="100" />
        <el-table-column label="学生姓名" prop="student_name" width="100" />
        <el-table-column label="专业" prop="student_major" />
        <el-table-column label="课程编号" prop="course_code" width="100" />
        <el-table-column label="课程名称" prop="course_name" min-width="150" />
        <el-table-column label="授课教师" prop="teacher_name" width="100" />
        <el-table-column label="学分" prop="credits" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="审批时间" prop="approved_at" width="160">
          <template #default="{ row }">
            {{ row.approved_at ? formatDateTime(row.approved_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="审批人" prop="approver_name" width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleViewDetail(row)"
            >
              详情
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

    <!-- 选课详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="'选课申请详情'"
      width="700px"
    >
      <div v-if="currentEnrollment" class="enrollment-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="申请时间">{{ formatDateTime(currentEnrollment.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentEnrollment.status)">
              {{ getStatusText(currentEnrollment.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="学生学号">{{ currentEnrollment.student_no }}</el-descriptions-item>
          <el-descriptions-item label="学生姓名">{{ currentEnrollment.student_name }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ currentEnrollment.student_major }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ currentEnrollment.student_class }}</el-descriptions-item>
          <el-descriptions-item label="课程编号">{{ currentEnrollment.course_code }}</el-descriptions-item>
          <el-descriptions-item label="课程名称">{{ currentEnrollment.course_name }}</el-descriptions-item>
          <el-descriptions-item label="授课教师">{{ currentEnrollment.teacher_name }}</el-descriptions-item>
          <el-descriptions-item label="学分">{{ currentEnrollment.credits }}</el-descriptions-item>
          <el-descriptions-item label="学时">{{ currentEnrollment.hours }}</el-descriptions-item>
          <el-descriptions-item label="学期">{{ currentEnrollment.semester }}</el-descriptions-item>
          <el-descriptions-item label="审批时间">{{ currentEnrollment.approved_at ? formatDateTime(currentEnrollment.approved_at) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="审批人">{{ currentEnrollment.approver_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="申请原因" span="2">{{ currentEnrollment.reason || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" span="2">{{ currentEnrollment.notes || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Download, Document, Check, Clock, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

interface Enrollment {
  id: number
  created_at: string
  student_no: string
  student_name: string
  student_major: string
  student_class: string
  course_code: string
  course_name: string
  teacher_name: string
  credits: number
  hours: number
  semester: string
  status: 'pending' | 'approved' | 'rejected'
  approved_at?: string
  approver_name?: string
  reason?: string
  notes?: string
}

const statusChart = ref<HTMLElement>()
const majorChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()
const popularCoursesChart = ref<HTMLElement>()

const tableLoading = ref(false)
const exportLoading = ref(false)
const detailDialogVisible = ref(false)
const currentEnrollment = ref<Enrollment | null>(null)
const searchKeyword = ref('')

const filterForm = reactive({
  semester: '2024-春',
  status: '',
  major: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const reportStats = reactive({
  totalEnrollments: 2456,
  approvedCount: 1892,
  pendingCount: 156,
  approvalRate: 77.0
})

const enrollments = ref<Enrollment[]>([])

const filteredEnrollments = computed(() => {
  if (!searchKeyword.value) return enrollments.value

  return enrollments.value.filter(enrollment =>
    enrollment.student_no.includes(searchKeyword.value) ||
    enrollment.student_name.includes(searchKeyword.value) ||
    enrollment.course_name.includes(searchKeyword.value)
  )
})

const loadEnrollments = async () => {
  try {
    tableLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockEnrollments: Enrollment[] = [
      {
        id: 1,
        created_at: '2024-02-20T10:30:00Z',
        student_no: 'S2021001',
        student_name: '张三',
        student_major: '计算机科学',
        student_class: '计算机科学1班',
        course_code: 'CS101',
        course_name: '计算机科学导论',
        teacher_name: '李明',
        credits: 3,
        hours: 48,
        semester: '2024-春',
        status: 'approved',
        approved_at: '2024-02-21T14:20:00Z',
        approver_name: '教务处',
        reason: '专业必修课，需要完成学分要求'
      },
      {
        id: 2,
        created_at: '2024-02-20T09:15:00Z',
        student_no: 'S2021002',
        student_name: '李四',
        student_major: '软件工程',
        student_class: '软件工程1班',
        course_code: 'CS102',
        course_name: '数据结构与算法',
        teacher_name: '王芳',
        credits: 4,
        hours: 64,
        semester: '2024-春',
        status: 'pending',
        reason: '专业核心课程'
      },
      {
        id: 3,
        created_at: '2024-02-19T16:45:00Z',
        student_no: 'S2021003',
        student_name: '王五',
        student_major: '数据科学',
        student_class: '数据科学1班',
        course_code: 'CS103',
        course_name: '数据库系统',
        teacher_name: '张伟',
        credits: 3,
        hours: 48,
        semester: '2024-春',
        status: 'rejected',
        approved_at: '2024-02-20T11:30:00Z',
        approver_name: '教务处',
        reason: '先修课程未完成'
      }
    ]

    enrollments.value = mockEnrollments
    pagination.total = mockEnrollments.length
  } catch (error) {
    ElMessage.error('获取选课数据失败')
  } finally {
    tableLoading.value = false
  }
}

const initCharts = () => {
  // 选课状态分布
  if (statusChart.value) {
    const chart = echarts.init(statusChart.value)
    const option = {
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '60%',
        data: [
          { value: 1892, name: '已批准', itemStyle: { color: '#67c23a' } },
          { value: 156, name: '待审批', itemStyle: { color: '#e6a23c' } },
          { value: 408, name: '已拒绝', itemStyle: { color: '#f56c6c' } }
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

  // 各专业选课统计
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
        data: [856, 698, 542, 360],
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

  // 选课趋势分析
  if (trendChart.value) {
    const chart = echarts.init(trendChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: '选课申请数' },
      xAxis: {
        type: 'category',
        data: ['第1天', '第2天', '第3天', '第4天', '第5天', '第6天', '第7天']
      },
      yAxis: { type: 'value' },
      series: [{
        name: '选课申请数',
        type: 'line',
        smooth: true,
        data: [120, 280, 350, 420, 380, 290, 180],
        itemStyle: { color: '#5470c6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.05)' }
          ])
        }
      }]
    }
    chart.setOption(option)
  }

  // 热门课程排行
  if (popularCoursesChart.value) {
    const chart = echarts.init(popularCoursesChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'category',
        data: ['计算机科学导论', '数据结构与算法', '数据库系统', '操作系统', '计算机网络', '软件工程']
      },
      series: [{
        type: 'bar',
        data: [156, 142, 128, 115, 98, 87],
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

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return textMap[status] || status
}

const handleSearch = () => {
  loadEnrollments()
}

const handleReset = () => {
  filterForm.status = ''
  filterForm.major = ''
  searchKeyword.value = ''
  loadEnrollments()
}

const handleRefresh = () => {
  loadEnrollments()
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('选课报表导出成功')
  } catch (error) {
    ElMessage.error('报表导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleViewDetail = (enrollment: Enrollment) => {
  currentEnrollment.value = enrollment
  detailDialogVisible.value = true
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadEnrollments()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadEnrollments()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadEnrollments()
  nextTick(() => {
    initCharts()
  })
})
</script>

<style lang="scss" scoped>
.enrollment-reports {
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

  .enrollment-detail {
    // 详细信息样式
  }
}
</style>