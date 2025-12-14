<template>
  <div class="simple-app">
    <!-- 如果是登录页面，只显示路由视图 -->
    <template v-if="$route.path === '/login'">
      <router-view />
    </template>

    <!-- 否则显示完整的主界面 -->
    <template v-else>
      <div class="dashboard">
        <!-- 顶部导航栏 -->
        <div class="header">
          <div class="header-left">
            <h1>学生信息管理系统</h1>
          </div>
          <div class="header-right">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRouteMeta?.title">
                {{ currentRouteMeta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
            <div class="user-info">
              <el-dropdown @command="handleUserCommand">
                <span class="user-name">
                  <el-icon><User /></el-icon>
                  {{ userInfo?.real_name || '用户' }}
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                    <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>

        <div class="main-layout">
          <!-- 侧边栏菜单 -->
          <div class="sidebar">
            <el-menu
              :default-active="$route.path"
              class="sidebar-menu"
              @select="handleMenuSelect"
            >
              <el-menu-item index="/dashboard">
                <el-icon><Monitor /></el-icon>
                <span>仪表板</span>
              </el-menu-item>

              <el-menu-item index="/students">
                <el-icon><User /></el-icon>
                <span>学生管理</span>
              </el-menu-item>

              <el-menu-item index="/teachers">
                <el-icon><Avatar /></el-icon>
                <span>教师管理</span>
              </el-menu-item>

              <el-menu-item index="/courses">
                <el-icon><Reading /></el-icon>
                <span>课程管理</span>
              </el-menu-item>

              <el-menu-item index="/grades">
                <el-icon><DocumentChecked /></el-icon>
                <span>成绩管理</span>
              </el-menu-item>
            </el-menu>
          </div>

          <!-- 主内容区域 -->
          <div class="content-area">
            <router-view />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userInfo = ref<any>(null)

// 当前路由的元信息
const currentRouteMeta = computed(() => route.meta)

// 成绩数据
const gradesData = ref([
  {
    id: 1,
    student_name: '张三',
    student_no: 'S2021001',
    course_name: '计算机科学导论',
    exam_type: '期中考试',
    score: 85,
    max_score: 100,
    is_published: true
  },
  {
    id: 2,
    student_name: '张三',
    student_no: 'S2021001',
    course_name: '计算机科学导论',
    exam_type: '期末考试',
    score: 88,
    max_score: 100,
    is_published: true
  },
  {
    id: 3,
    student_name: '李四',
    student_no: 'S2021002',
    course_name: '计算机科学导论',
    exam_type: '期中考试',
    score: 92,
    max_score: 100,
    is_published: true
  },
  {
    id: 4,
    student_name: '李四',
    student_no: 'S2021002',
    course_name: '软件工程',
    exam_type: '作业',
    score: 95,
    max_score: 100,
    is_published: true
  },
  {
    id: 5,
    student_name: '王五',
    student_no: 'S2021003',
    course_name: '软件工程',
    exam_type: '测验',
    score: 76,
    max_score: 100,
    is_published: false
  },
  {
    id: 6,
    student_name: '王五',
    student_no: 'S2021003',
    course_name: '数据结构与算法',
    exam_type: '项目',
    score: 82,
    max_score: 100,
    is_published: true
  }
])

// 响应式数据
const gradeSearchQuery = ref('')
const selectedGrades = ref([])

// 计算属性
const showGradesList = computed(() => route.path === '/grades/list')

const filteredGrades = computed(() => {
  if (!gradeSearchQuery.value) return gradesData.value
  const query = gradeSearchQuery.value.toLowerCase()
  return gradesData.value.filter(grade =>
    grade.student_name.toLowerCase().includes(query) ||
    grade.student_no.toLowerCase().includes(query) ||
    grade.course_name.toLowerCase().includes(query) ||
    grade.exam_type.toLowerCase().includes(query)
  )
})

const publishedCount = computed(() => gradesData.value.filter(g => g.is_published).length)
const unpublishedCount = computed(() => gradesData.value.filter(g => !g.is_published).length)
const averageScore = computed(() => {
  const total = gradesData.value.reduce((sum, g) => sum + g.score, 0)
  return (total / gradesData.value.length).toFixed(1)
})

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  console.log('菜单点击:', index)
  console.log('当前路径:', route.path)

  
  if (index !== route.path) {
    console.log('跳转到:', index)
    router.push(index)
  } else {
    console.log('路径相同，不跳转')
  }
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        logout()
      } catch {
        // 用户取消
      }
      break
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}

const goToDashboard = () => {
  router.push('/dashboard')
}

// 成绩管理相关方法
const handleGradeSearch = () => {
  console.log('搜索成绩:', gradeSearchQuery.value)
}

const handleAddGrade = () => {
  ElMessage.info('录入成绩功能开发中')
}

const handleImportGrades = () => {
  ElMessage.info('批量导入功能开发中')
}

const handleExportGrades = () => {
  ElMessage.info('导出数据功能开发中')
}

const handleBatchDelete = () => {
  ElMessage.info('批量删除功能开发中')
}

const handleGradeSelectionChange = (selection) => {
  selectedGrades.value = selection
}

const handleViewGrade = (row) => {
  ElMessage.info('查看成绩详情功能开发中')
}

const handleEditGrade = (row) => {
  ElMessage.info('编辑成绩功能开发中')
}

const handlePublishGrade = (row) => {
  row.is_published = true
  ElMessage.success('成绩已发布')
}

const handleDeleteGrade = (row) => {
  ElMessage.info('删除成绩功能开发中')
}

// 工具函数
const getExamTypeTag = (type) => {
  const typeMap = {
    '期中考试': 'warning',
    '期末考试': 'danger',
    '作业': 'primary',
    '测验': 'info',
    '项目': 'success'
  }
  return typeMap[type] || 'info'
}

const getExamTypeText = (type) => {
  return type
}

const getScoreColor = (score, maxScore) => {
  const percentage = (score / maxScore) * 100
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

const getPercentage = (score, maxScore) => {
  return ((score / maxScore) * 100).toFixed(1)
}

onMounted(() => {
  // 获取用户信息
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      userInfo.value = JSON.parse(userStr)
    } catch (error) {
      console.error('解析用户信息失败:', error)
    }
  }
})
</script>

<style scoped>
.simple-app {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left h1 {
  color: #409eff;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-name:hover {
  background-color: #f5f7fa;
}

.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.sidebar-menu {
  border: none;
  height: 100%;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
  padding: 0 20px !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #f5f7fa;
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f5f5f5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }

  .header {
    padding: 0 16px;
  }

  .header-left h1 {
    font-size: 18px;
  }

  .content-area {
    padding: 16px;
  }
}

@media (max-width: 640px) {
  .header {
    padding: 0 12px;
  }

  .header-right {
    gap: 12px;
  }

  .sidebar {
    width: 180px;
  }

  .content-area {
    padding: 12px;
  }
}
</style>

<style scoped>
/* 成绩管理样式 */
.grade-management {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
  padding: 20px 0;
  border-bottom: 1px solid #e4e7ed;
}

.header-content h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.table-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-cards {
  margin-top: 20px;
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.published {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.unpublished {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-icon.average {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #666;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>