<template>
  <div class="dashboard-view">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon student">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalStudents }}</h3>
              <p>学生总数</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon teacher">
              <el-icon><Avatar /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalTeachers }}</h3>
              <p>教师总数</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon course">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalCourses }}</h3>
              <p>课程总数</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon grade">
              <el-icon><DocumentChecked /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalGrades }}</h3>
              <p>成绩记录</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 快捷操作 -->
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <h3>快捷操作</h3>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/students/create')">
              <el-icon><Plus /></el-icon>
              添加学生
            </el-button>
            <el-button type="success" @click="$router.push('/teachers/create')">
              <el-icon><Plus /></el-icon>
              添加教师
            </el-button>
            <el-button type="warning" @click="$router.push('/courses/create')">
              <el-icon><Plus /></el-icon>
              添加课程
            </el-button>
            <el-button type="info" @click="$router.push('/grades/entry')">
              <el-icon><EditPen /></el-icon>
              录入成绩
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 最近活动 -->
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <h3>最近活动</h3>
          </template>
          <div class="recent-activities">
            <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="activity.type">
                <el-icon><component :is="activity.icon" /></el-icon>
              </div>
              <div class="activity-content">
                <p>{{ activity.description }}</p>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px;">
      <!-- 系统信息 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <h3>系统信息</h3>
          </template>
          <div class="system-info">
            <el-descriptions :column="4" border>
              <el-descriptions-item label="系统版本">
                <el-tag type="primary">v1.0.0</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="运行环境">
                <el-tag>Development</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据库状态">
                <el-tag type="success">正常</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="最后更新">
                {{ new Date().toLocaleString() }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 统计数据
const stats = ref({
  totalStudents: 1250,
  totalTeachers: 85,
  totalCourses: 42,
  totalGrades: 3890
})

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    type: 'student',
    icon: 'User',
    description: '新增学生张三',
    time: '5分钟前'
  },
  {
    id: 2,
    type: 'course',
    icon: 'Reading',
    description: '创建新课程《高等数学》',
    time: '15分钟前'
  },
  {
    id: 3,
    type: 'grade',
    icon: 'DocumentChecked',
    description: '录入了30条成绩记录',
    time: '1小时前'
  },
  {
    id: 4,
    type: 'teacher',
    icon: 'Avatar',
    description: '教师李四更新了个人信息',
    time: '2小时前'
  }
])

onMounted(() => {
  ElMessage.success('欢迎来到学生信息管理系统')
})
</script>

<style scoped>
.dashboard-view {
  max-width: 1400px;
  margin: 0 auto;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin-right: 16px;
}

.stat-icon.student {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.teacher {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.course {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.grade {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info h3 {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #303133;
}

.stat-info p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.quick-actions .el-button {
  height: 48px;
  justify-content: flex-start;
}

.recent-activities {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: white;
  font-size: 16px;
}

.activity-icon.student {
  background: #409eff;
}

.activity-icon.teacher {
  background: #67c23a;
}

.activity-icon.course {
  background: #e6a23c;
}

.activity-icon.grade {
  background: #f56c6c;
}

.activity-content {
  flex: 1;
}

.activity-content p {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 14px;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

.system-info {
  padding: 16px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>