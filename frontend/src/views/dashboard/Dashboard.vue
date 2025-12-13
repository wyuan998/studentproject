<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>欢迎回来，{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</h2>
          <p class="welcome-desc">
            <el-icon><Calendar /></el-icon>
            {{ formatDate(new Date()) }}
            <span class="weather">今天天气晴朗，适合学习工作！</span>
          </p>
        </div>
        <div class="welcome-actions">
          <el-button type="primary" @click="router.push('/courses/list')">
            <el-icon><ShoppingCart /></el-icon>
            在线选课
          </el-button>
          <el-button @click="router.push('/grades/list')">
            <el-icon><Document /></el-icon>
            查看成绩
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon primary">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.studentCount || 0 }}</div>
              <div class="stat-label">学生总数</div>
            </div>
          </div>
          <div class="stat-trend">
            <el-icon class="trend-up"><ArrowUp /></el-icon>
            <span>较上月增长 5.2%</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.courseCount || 0 }}</div>
              <div class="stat-label">课程总数</div>
            </div>
          </div>
          <div class="stat-trend">
            <el-icon class="trend-up"><ArrowUp /></el-icon>
            <span>较上月增长 3.8%</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.enrollmentCount || 0 }}</div>
              <div class="stat-label">选课人数</div>
            </div>
          </div>
          <div class="stat-trend">
            <el-icon class="trend-down"><ArrowDown /></el-icon>
            <span>较上月下降 1.2%</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon danger">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.messageCount || 0 }}</div>
              <div class="stat-label">未读消息</div>
            </div>
          </div>
          <div class="stat-trend">
            <el-icon class="trend-up"><ArrowUp /></el-icon>
            <span>较上月增长 12.5%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="content-row">
      <!-- 日程安排 -->
      <el-col :xs="24" :lg="8">
        <el-card class="schedule-card">
          <template #header>
            <div class="card-header">
              <span>今日日程</span>
              <el-button text size="small" @click="viewCalendar">
                查看日历
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>

          <div class="schedule-list">
            <div v-if="todaySchedules.length === 0" class="empty-schedule">
              <el-empty description="暂无日程安排" :image-size="60" />
            </div>
            <div v-else>
              <div v-for="schedule in todaySchedules" :key="schedule.id" class="schedule-item">
                <div class="schedule-time">{{ schedule.time }}</div>
                <div class="schedule-info">
                  <div class="schedule-title">{{ schedule.title }}</div>
                  <div class="schedule-location">
                    <el-icon><Location /></el-icon>
                    {{ schedule.location }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 快捷操作 -->
        <el-card class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>

          <div class="quick-actions">
            <el-button
              v-for="action in quickActions"
              :key="action.name"
              class="quick-action-btn"
              @click="router.push(action.path)"
            >
              <el-icon size="20">
                <component :is="action.icon" />
              </el-icon>
              <span>{{ action.name }}</span>
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 最近成绩 -->
      <el-col :xs="24" :lg="8">
        <el-card class="grades-card">
          <template #header>
            <div class="card-header">
              <span>最近成绩</span>
              <el-button text size="small" @click="router.push('/grades/list')">
                查看全部
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>

          <div class="grades-list">
            <div v-if="recentGrades.length === 0" class="empty-grades">
              <el-empty description="暂无成绩记录" :image-size="60" />
            </div>
            <div v-else>
              <div v-for="grade in recentGrades" :key="grade.id" class="grade-item">
                <div class="grade-info">
                  <div class="grade-course">{{ grade.course_name }}</div>
                  <div class="grade-type">{{ grade.type }}</div>
                </div>
                <div class="grade-score" :class="getGradeClass(grade.score)">
                  {{ grade.score }}
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 系统公告 -->
        <el-card class="notice-card">
          <template #header>
            <div class="card-header">
              <span>系统公告</span>
              <el-button text size="small">更多</el-button>
            </div>
          </template>

          <div class="notice-list">
            <div v-for="notice in notices" :key="notice.id" class="notice-item">
              <div class="notice-dot" :class="{ urgent: notice.urgent }"></div>
              <div class="notice-content">
                <div class="notice-title">{{ notice.title }}</div>
                <div class="notice-time">{{ formatTime(notice.time) }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 学习进度 -->
      <el-col :xs="24" :lg="8">
        <el-card class="progress-card">
          <template #header>
            <div class="card-header">
              <span>学习进度</span>
              <el-button text size="small">查看详情</el-button>
            </div>
          </template>

          <div class="progress-list">
            <div v-for="course in courseProgress" :key="course.id" class="progress-item">
              <div class="progress-info">
                <div class="progress-title">{{ course.name }}</div>
                <div class="progress-percent">{{ course.progress }}%</div>
              </div>
              <el-progress
                :percentage="course.progress"
                :color="getProgressColor(course.progress)"
                :show-text="false"
                :stroke-width="8"
                class="progress-bar"
              />
              <div class="progress-status">{{ course.status }}</div>
            </div>
          </div>
        </el-card>

        <!-- 每日一言 -->
        <el-card class="quote-card">
          <div class="quote-content">
            <div class="quote-text">"学习就像攀登高山，每一步都让你看得更远。"</div>
            <div class="quote-author">—— 拉尔夫·沃尔多·爱默生</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import {
  User,
  Reading,
  Box,
  Bell,
  Calendar,
  ShoppingCart,
  Document,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  Location,
  School,
  Postcard,
  ChatDotSquare,
  DataBoard,
  Setting,
  Trophy
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const stats = reactive({
  studentCount: 0,
  courseCount: 0,
  enrollmentCount: 0,
  messageCount: 0
})

const todaySchedules = ref([
  { id: 1, time: '08:00-09:40', title: '高等数学', location: '教学楼A-201' },
  { id: 2, time: '10:00-11:40', title: '数据结构', location: '教学楼B-305' },
  { id: 3, time: '14:00-15:40', title: '大学英语', location: '外语楼-102' }
])

const recentGrades = ref([
  { id: 1, course_name: '数据结构', type: '期中考试', score: 92 },
  { id: 2, course_name: '高等数学', type: '作业', score: 85 },
  { id: 3, course_name: '大学英语', type: '测验', score: 88 }
])

const notices = ref([
  { id: 1, title: '关于期末考试安排的通知', time: new Date(Date.now() - 1000 * 60 * 60 * 2), urgent: false },
  { id: 2, title: '系统维护通知', time: new Date(Date.now() - 1000 * 60 * 60 * 24), urgent: true },
  { id: 3, title: '选课系统开放通知', time: new Date(Date.now() - 1000 * 60 * 60 * 48), urgent: false }
])

const courseProgress = ref([
  { id: 1, name: '数据结构', progress: 75, status: '学习中' },
  { id: 2, name: '高等数学', progress: 60, status: '学习中' },
  { id: 3, name: '大学英语', progress: 90, status: '即将完成' }
])

const quickActions = [
  { name: '查看课表', icon: 'Calendar', path: '/schedule' },
  { name: '在线选课', icon: 'ShoppingCart', path: '/courses/list' },
  { name: '查看成绩', icon: 'Document', path: '/grades/list' },
  { name: '申请休学', icon: 'Postcard', path: '/students/leave' },
  { name: '成绩统计', icon: 'DataBoard', path: '/reports/grades' },
  { name: '个人设置', icon: 'Setting', path: '/settings' }
]

// 方法
const loadStats = async () => {
  try {
    // 这里应该调用实际的API
    // const response = await dashboardApi.getStats()
    // Object.assign(stats, response.data)

    // 模拟数据
    Object.assign(stats, {
      studentCount: 2847,
      courseCount: 156,
      enrollmentCount: 8234,
      messageCount: 3
    })
  } catch (error) {
    console.error('Load stats error:', error)
    ElMessage.error('加载统计数据失败')
  }
}

const viewCalendar = () => {
  router.push('/schedule')
}

const getGradeClass = (score: number) => {
  if (score >= 90) return 'grade-excellent'
  if (score >= 80) return 'grade-good'
  if (score >= 70) return 'grade-normal'
  return 'grade-poor'
}

const getProgressColor = (progress: number) => {
  if (progress >= 90) return '#67c23a'
  if (progress >= 70) return '#409eff'
  if (progress >= 50) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (date: Date) => {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  }
  return date.toLocaleDateString('zh-CN', options)
}

const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 1000 * 60) {
    return '刚刚'
  } else if (diff < 1000 * 60 * 60) {
    return `${Math.floor(diff / (1000 * 60))}分钟前`
  } else if (diff < 1000 * 60 * 60 * 24) {
    return `${Math.floor(diff / (1000 * 60 * 60))}小时前`
  } else if (diff < 1000 * 60 * 60 * 24 * 7) {
    return `${Math.floor(diff / (1000 * 60 * 60 * 24))}天前`
  } else {
    return date.toLocaleDateString()
  }
}

// 生命周期
onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;

  .welcome-card {
    margin-bottom: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;

    :deep(.el-card__body) {
      padding: 30px;
    }

    .welcome-content {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .welcome-text {
        h2 {
          margin: 0 0 10px 0;
          font-size: 28px;
          font-weight: 600;
        }

        .welcome-desc {
          display: flex;
          align-items: center;
          gap: 8px;
          opacity: 0.9;
          font-size: 16px;

          .weather {
            margin-left: auto;
          }
        }
      }

      .welcome-actions {
        display: flex;
        gap: 12px;
      }
    }
  }

  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      height: 120px;

      :deep(.el-card__body) {
        padding: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }

      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: white;

          &.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          &.success {
            background: linear-gradient(135deg, #56d3b1 0%, #2ecc71 100%);
          }

          &.warning {
            background: linear-gradient(135deg, #f9ca24 0%, #f0932b 100%);
          }

          &.danger {
            background: linear-gradient(135deg, #f5576c 0%, #ee5a24 100%);
          }
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 24px;
            font-weight: 600;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }

          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-regular);
          }
        }
      }

      .stat-trend {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        display: flex;
        align-items: center;
        gap: 4px;

        .trend-up {
          color: #67c23a;
        }

        .trend-down {
          color: #f56c6c;
        }
      }
    }
  }

  .content-row {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }

    .schedule-card,
    .grades-card,
    .progress-card {
      margin-bottom: 20px;
    }

    .schedule-list {
      .empty-schedule {
        padding: 20px 0;
      }

      .schedule-item {
        display: flex;
        padding: 12px 0;
        border-bottom: 1px solid var(--el-border-color-lighter);

        &:last-child {
          border-bottom: none;
        }

        .schedule-time {
          font-size: 12px;
          color: var(--el-color-primary);
          font-weight: 600;
          padding: 2px 8px;
          background: var(--el-color-primary-light-9);
          border-radius: 4px;
          margin-right: 12px;
          white-space: nowrap;
        }

        .schedule-info {
          flex: 1;

          .schedule-title {
            font-weight: 600;
            margin-bottom: 4px;
            color: var(--el-text-color-primary);
          }

          .schedule-location {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }

    .quick-actions {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .quick-action-btn {
        height: 60px;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
        background: var(--el-fill-color-light);
        border: 1px solid var(--el-border-color-lighter);

        &:hover {
          background: var(--el-color-primary-light-9);
          border-color: var(--el-color-primary);
          color: var(--el-color-primary);
        }

        span {
          font-size: 12px;
        }
      }
    }

    .grades-list {
      .empty-grades {
        padding: 20px 0;
      }

      .grade-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid var(--el-border-color-lighter);

        &:last-child {
          border-bottom: none;
        }

        .grade-info {
          .grade-course {
            font-weight: 600;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }

          .grade-type {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }

        .grade-score {
          font-size: 18px;
          font-weight: 600;
          padding: 4px 8px;
          border-radius: 4px;

          &.grade-excellent {
            color: #67c23a;
            background: #f0f9ff;
          }

          &.grade-good {
            color: #409eff;
            background: #f0f9ff;
          }

          &.grade-normal {
            color: #e6a23c;
            background: #fdf6ec;
          }

          &.grade-poor {
            color: #f56c6c;
            background: #fef0f0;
          }
        }
      }
    }

    .notice-list {
      .notice-item {
        display: flex;
        padding: 12px 0;
        border-bottom: 1px solid var(--el-border-color-lighter);

        &:last-child {
          border-bottom: none;
        }

        .notice-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--el-color-info);
          margin-top: 6px;
          margin-right: 8px;

          &.urgent {
            background: var(--el-color-danger);
          }
        }

        .notice-content {
          flex: 1;

          .notice-title {
            font-weight: 500;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }

          .notice-time {
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
      }
    }

    .progress-list {
      .progress-item {
        padding: 16px 0;
        border-bottom: 1px solid var(--el-border-color-lighter);

        &:last-child {
          border-bottom: none;
        }

        .progress-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .progress-title {
            font-weight: 600;
            color: var(--el-text-color-primary);
          }

          .progress-percent {
            font-weight: 600;
            color: var(--el-color-primary);
          }
        }

        .progress-bar {
          margin-bottom: 8px;
        }

        .progress-status {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }

    .quote-card {
      .quote-content {
        text-align: center;
        padding: 20px 0;

        .quote-text {
          font-size: 16px;
          color: var(--el-text-color-primary);
          font-style: italic;
          margin-bottom: 8px;
          line-height: 1.6;
        }

        .quote-author {
          font-size: 14px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;

    .welcome-card {
      :deep(.el-card__body) {
        padding: 20px;
      }

      .welcome-content {
        flex-direction: column;
        text-align: center;
        gap: 20px;

        .welcome-desc {
          flex-direction: column;
          gap: 4px;

          .weather {
            margin-left: 0;
          }
        }
      }
    }

    .stats-row {
      .el-col {
        margin-bottom: 20px;
      }
    }

    .quick-actions {
      grid-template-columns: 1fr !important;
    }
  }
}
</style>