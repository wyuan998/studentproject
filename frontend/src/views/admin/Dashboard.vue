<template>
  <div class="admin-dashboard">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">系统控制台</span>
      </template>
    </el-page-header>

    <!-- 系统概览 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon blue">
              <el-icon><User /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ systemStats.totalUsers }}</div>
              <div class="card-label">系统用户</div>
              <div class="card-trend">
                <el-icon><TrendCharts /></el-icon>
                <span>+{{ systemStats.userGrowth }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon green">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ systemStats.systemHealth }}%</div>
              <div class="card-label">系统健康度</div>
              <div class="card-trend">
                <el-icon><TrendCharts /></el-icon>
                <span>正常</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon orange">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ systemStats.todayVisits }}</div>
              <div class="card-label">今日访问</div>
              <div class="card-trend">
                <el-icon><TrendCharts /></el-icon>
                <span>+{{ systemStats.visitGrowth }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon purple">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ systemStats.alerts }}</div>
              <div class="card-label">待处理告警</div>
              <div class="card-trend">
                <el-icon><TrendCharts /></el-icon>
                <span>{{ systemStats.alerts > 0 ? '需要处理' : '正常' }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card class="quick-actions">
      <template #header>
        <span class="card-title">快速操作</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="action-item" @click="navigateToUsers">
            <el-icon class="action-icon"><User /></el-icon>
            <div class="action-text">
              <div class="action-title">用户管理</div>
              <div class="action-desc">管理系统用户和权限</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-item" @click="navigateToSettings">
            <el-icon class="action-icon"><Setting /></el-icon>
            <div class="action-text">
              <div class="action-title">系统设置</div>
              <div class="action-desc">配置系统参数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-item" @click="navigateToLogs">
            <el-icon class="action-icon"><Document /></el-icon>
            <div class="action-text">
              <div class="action-title">系统日志</div>
              <div class="action-desc">查看系统运行日志</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="action-item" @click="navigateToBackup">
            <el-icon class="action-icon"><FolderOpened /></el-icon>
            <div class="action-text">
              <div class="action-title">数据备份</div>
              <div class="action-desc">备份系统数据</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 系统状态监控 -->
    <el-row :gutter="20" class="monitoring-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">系统资源监控</span>
          </template>
          <div ref="resourceChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">访问统计</span>
          </template>
          <div ref="visitChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新活动和系统告警 -->
    <el-row :gutter="20" class="info-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">最新活动</span>
              <el-button type="text" @click="navigateToLogs">查看全部</el-button>
            </div>
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
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">系统告警</span>
              <el-button type="text" @click="navigateToAlerts">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentAlerts" stripe size="small">
            <el-table-column label="级别" width="80">
              <template #default="{ row }">
                <el-tag :type="getAlertType(row.level)" size="small">
                  {{ row.level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="描述" prop="description" />
            <el-table-column label="时间" prop="time" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据统计 -->
    <el-card class="data-stats">
      <template #header>
        <span class="card-title">数据统计</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6" v-for="stat in dataStats" :key="stat.key">
          <div class="stat-item">
            <div class="stat-icon" :class="stat.iconClass">
              <el-icon><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, Monitor, DataAnalysis, Warning, TrendCharts, Setting,
  Document, FolderOpened, Reading, Collection, Message, Box
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

const resourceChart = ref<HTMLElement>()
const visitChart = ref<HTMLElement>()

const systemStats = reactive({
  totalUsers: 1847,
  userGrowth: 8.5,
  systemHealth: 95.8,
  todayVisits: 523,
  visitGrowth: 12.3,
  alerts: 3
})

const recentActivities = ref([
  {
    id: 1,
    description: '管理员张三修改了系统配置',
    timestamp: '2024-02-20 14:30',
    type: 'primary'
  },
  {
    id: 2,
    description: '系统完成数据备份',
    timestamp: '2024-02-20 02:00',
    type: 'success'
  },
  {
    id: 3,
    description: '检测到异常登录尝试',
    timestamp: '2024-02-19 23:45',
    type: 'warning'
  },
  {
    id: 4,
    description: '用户李四创建了新课程',
    timestamp: '2024-02-19 16:20',
    type: 'info'
  }
])

const recentAlerts = ref([
  {
    level: '高危',
    description: '数据库连接池使用率超过80%',
    time: '2024-02-20 14:30'
  },
  {
    level: '中',
    description: '系统磁盘空间不足20%',
    time: '2024-02-20 12:15'
  },
  {
    level: '低',
    description: '部分用户长时间未登录',
    time: '2024-02-20 10:30'
  }
])

const dataStats = reactive([
  {
    key: 'students',
    label: '学生数量',
    value: 1248,
    icon: 'Reading',
    iconClass: 'blue'
  },
  {
    key: 'teachers',
    label: '教师数量',
    value: 156,
    icon: 'User',
    iconClass: 'green'
  },
  {
    key: 'courses',
    label: '课程数量',
    value: 86,
    icon: 'Collection',
    iconClass: 'orange'
  },
  {
    key: 'enrollments',
    label: '选课记录',
    value: 3456,
    icon: 'Box',
    iconClass: 'purple'
  }
])

const getAlertType = (level: string) => {
  const typeMap: Record<string, string> = {
    '高危': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return typeMap[level] || 'info'
}

const initCharts = () => {
  // 系统资源监控
  if (resourceChart.value) {
    const chart = echarts.init(resourceChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['CPU使用率', '内存使用率', '磁盘使用率'] },
      xAxis: {
        type: 'category',
        data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
      },
      yAxis: { type: 'value', max: 100 },
      series: [
        {
          name: 'CPU使用率',
          type: 'line',
          smooth: true,
          data: [30, 25, 45, 65, 75, 55, 35],
          itemStyle: { color: '#5470c6' }
        },
        {
          name: '内存使用率',
          type: 'line',
          smooth: true,
          data: [45, 40, 55, 70, 80, 65, 50],
          itemStyle: { color: '#91cc75' }
        },
        {
          name: '磁盘使用率',
          type: 'line',
          smooth: true,
          data: [20, 18, 22, 28, 35, 30, 25],
          itemStyle: { color: '#fac858' }
        }
      ]
    }
    chart.setOption(option)
  }

  // 访问统计
  if (visitChart.value) {
    const chart = echarts.init(visitChart.value)
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['页面访问', 'API调用'] },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '页面访问',
          type: 'bar',
          data: [280, 320, 350, 380, 420, 180, 120],
          itemStyle: { color: '#91cc75' }
        },
        {
          name: 'API调用',
          type: 'line',
          smooth: true,
          data: [1200, 1400, 1600, 1800, 2000, 800, 600],
          itemStyle: { color: '#5470c6' }
        }
      ]
    }
    chart.setOption(option)
  }
}

const navigateToUsers = () => {
  router.push('/admin/users')
}

const navigateToSettings = () => {
  router.push('/admin/settings')
}

const navigateToLogs = () => {
  router.push('/admin/logs')
}

const navigateToBackup = () => {
  router.push('/admin/backup')
}

const navigateToAlerts = () => {
  router.push('/admin/alerts')
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
.admin-dashboard {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .overview-cards {
    margin-bottom: 20px;

    .overview-card {
      .card-content {
        display: flex;
        align-items: center;
        padding: 10px 0;

        .card-icon {
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

        .card-info {
          flex: 1;

          .card-number {
            font-size: 24px;
            font-weight: 700;
            color: var(--el-text-color-primary);
            line-height: 1;
          }

          .card-label {
            font-size: 14px;
            color: var(--el-text-color-regular);
            margin: 4px 0;
          }

          .card-trend {
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
            color: var(--el-color-success);

            .el-icon {
              font-size: 14px;
            }
          }
        }
      }
    }
  }

  .quick-actions {
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .action-item {
      display: flex;
      align-items: center;
      padding: 16px;
      border: 1px solid var(--el-border-color-light);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        border-color: var(--el-color-primary);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }

      .action-icon {
        width: 48px;
        height: 48px;
        border-radius: 8px;
        background-color: var(--el-color-primary);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;

        .el-icon {
          font-size: 24px;
        }
      }

      .action-text {
        .action-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--el-text-color-primary);
          margin-bottom: 4px;
        }

        .action-desc {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }

  .monitoring-section {
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .chart-container {
      height: 300px;
    }
  }

  .info-section {
    margin-bottom: 20px;

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

  .data-stats {
    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .stat-item {
      display: flex;
      align-items: center;
      padding: 16px;
      background-color: var(--el-fill-color-light);
      border-radius: 8px;

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;

        .el-icon {
          font-size: 24px;
          color: white;
        }

        &.blue { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        &.green { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
        &.orange { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        &.purple { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
      }

      .stat-content {
        .stat-value {
          font-size: 20px;
          font-weight: 700;
          color: var(--el-text-color-primary);
        }

        .stat-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-top: 2px;
        }
      }
    }
  }
}
</style>