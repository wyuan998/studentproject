<template>
  <el-header class="app-header">
    <div class="header-left">
      <!-- 折叠按钮 -->
      <el-button
        class="collapse-btn"
        text
        @click="appStore.toggleSidebar"
      >
        <el-icon size="20">
          <Fold v-if="!appStore.sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
      </el-button>

      <!-- 面包屑导航 -->
      <AppBreadcrumb />
    </div>

    <div class="header-right">
      <!-- 搜索 -->
      <el-tooltip content="搜索" placement="bottom">
        <el-button text class="header-btn" @click="showSearch = true">
          <el-icon size="18">
            <Search />
          </el-icon>
        </el-button>
      </el-tooltip>

      <!-- 全屏切换 -->
      <el-tooltip content="全屏" placement="bottom">
        <el-button text class="header-btn" @click="toggleFullscreen">
          <el-icon size="18">
            <FullScreen v-if="!isFullscreen" />
            <Aim v-else />
          </el-icon>
        </el-button>
      </el-tooltip>

      <!-- 主题切换 -->
      <el-tooltip :content="appStore.isDarkMode ? '切换到亮色主题' : '切换到暗色主题'" placement="bottom">
        <el-button text class="header-btn" @click="appStore.toggleTheme">
          <el-icon size="18">
            <Sunny v-if="!appStore.isDarkMode" />
            <Moon v-else />
          </el-icon>
        </el-button>
      </el-tooltip>

      <!-- 语言切换 -->
      <el-dropdown trigger="click" @command="handleLanguageChange">
        <el-button text class="header-btn">
          <el-icon size="18">
            <Globe />
          </el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              command="zh-CN"
              :class="{ active: appStore.language === 'zh-CN' }"
            >
              简体中文
            </el-dropdown-item>
            <el-dropdown-item
              command="en-US"
              :class="{ active: appStore.language === 'en-US' }"
            >
              English
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- 通知 -->
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
        <el-button text class="header-btn" @click="showNotifications = true">
          <el-icon size="18">
            <Bell />
          </el-icon>
        </el-button>
      </el-badge>

      <!-- 用户头像和下拉菜单 -->
      <el-dropdown trigger="click" @command="handleUserCommand">
        <div class="user-info">
          <el-avatar
            :size="32"
            :src="userStore.userInfo?.avatar"
            :alt="userStore.userInfo?.real_name || userStore.userInfo?.username"
          >
            {{ (userStore.userInfo?.real_name || userStore.userInfo?.username || 'U').charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="username" v-if="!appStore.isMobile">
            {{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
          </span>
          <el-icon class="arrow">
            <CaretBottom />
          </el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-dropdown-item>
            <el-dropdown-item divided command="password">
              <el-icon><Key /></el-icon>
              修改密码
            </el-dropdown-item>
            <el-dropdown-item command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 全局搜索对话框 -->
    <GlobalSearch v-model:visible="showSearch" />

    <!-- 通知抽屉 -->
    <NotificationDrawer v-model:visible="showNotifications" />

    <!-- 修改密码对话框 -->
    <ChangePasswordDialog v-model:visible="showChangePassword" />
  </el-header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Fold,
  Expand,
  Search,
  FullScreen,
  Aim,
  Sunny,
  Moon,
  Globe,
  Bell,
  CaretBottom,
  User,
  Setting,
  Key,
  SwitchButton
} from '@element-plus/icons-vue'
import AppBreadcrumb from './AppBreadcrumb.vue'
import GlobalSearch from '@/components/common/GlobalSearch.vue'
import NotificationDrawer from '@/components/common/NotificationDrawer.vue'
import ChangePasswordDialog from '@/components/common/ChangePasswordDialog.vue'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

// 响应式数据
const showSearch = ref(false)
const showNotifications = ref(false)
const showChangePassword = ref(false)
const isFullscreen = ref(false)

// 计算属性
const unreadCount = computed(() => {
  // 这里应该从通知store或API获取
  return 0
})

// 方法
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

const handleLanguageChange = (command: 'zh-CN' | 'en-US') => {
  appStore.setLanguage(command)
  ElMessage.success(`已切换到${command === 'zh-CN' ? '简体中文' : 'English'}`)
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      // 跳转到设置页面
      break
    case 'password':
      showChangePassword.value = true
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await userStore.logout()
      } catch (error) {
        // 用户取消
      }
      break
  }
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

// 生命周期
onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style lang="scss" scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: var(--el-index-normal);
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.collapse-btn {
  margin-right: 16px;
  font-size: 18px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 16px;
}

.header-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: var(--el-text-color-regular);
  transition: all 0.3s ease;

  &:hover {
    background-color: var(--el-fill-color-light);
    color: var(--el-color-primary);
  }
}

.notification-badge {
  :deep(.el-badge__content) {
    font-size: 10px;
    height: 16px;
    line-height: 16px;
    min-width: 16px;
    padding: 0 4px;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: var(--el-fill-color-light);
  }

  .username {
    font-size: 14px;
    color: var(--el-text-color-primary);
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .arrow {
    font-size: 12px;
    color: var(--el-text-color-regular);
    transition: transform 0.3s ease;
  }
}

.el-dropdown-menu {
  .active {
    color: var(--el-color-primary);
    font-weight: 600;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header-right {
    gap: 4px;
    padding-right: 8px;
  }

  .header-btn {
    width: 36px;
    height: 36px;
  }

  .username {
    display: none;
  }
}
</style>