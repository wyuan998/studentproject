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

              <el-sub-menu index="1">
                <template #title>
                  <el-icon><User /></el-icon>
                  <span>学生管理</span>
                </template>
                <el-menu-item index="/students">学生列表</el-menu-item>
                <el-menu-item index="/students/create">添加学生</el-menu-item>
              </el-sub-menu>

              <el-sub-menu index="2">
                <template #title>
                  <el-icon><Avatar /></el-icon>
                  <span>教师管理</span>
                </template>
                <el-menu-item index="/teachers">教师列表</el-menu-item>
                <el-menu-item index="/teachers/create">添加教师</el-menu-item>
              </el-sub-menu>

              <el-sub-menu index="3">
                <template #title>
                  <el-icon><Reading /></el-icon>
                  <span>课程管理</span>
                </template>
                <el-menu-item index="/courses">课程列表</el-menu-item>
                <el-menu-item index="/courses/create">添加课程</el-menu-item>
              </el-sub-menu>

              <el-sub-menu index="4">
                <template #title>
                  <el-icon><DocumentChecked /></el-icon>
                  <span>成绩管理</span>
                </template>
                <el-menu-item index="/grades">成绩列表</el-menu-item>
                <el-menu-item index="/grades/entry">成绩录入</el-menu-item>
              </el-sub-menu>
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

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  if (index !== route.path) {
    router.push(index)
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