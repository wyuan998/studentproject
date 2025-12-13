<template>
  <div id="app" class="app-container">
    <!-- 路由视图 -->
    <router-view v-slot="{ Component, route }">
      <keep-alive :include="cachedViews">
        <component :is="Component" :key="route.path" />
      </keep-alive>
    </router-view>

    <!-- 全局加载遮罩 -->
    <el-loading
      v-if="loading"
      fullscreen
      :lock="true"
      text="正在加载..."
      background-color="rgba(0, 0, 0, 0.7)"
    />

    <!-- 全局消息提示 -->
    <el-container v-if="$route.meta.showLayout !== false">
      <!-- 头部导航 -->
      <AppHeader />

      <!-- 侧边栏 -->
      <AppSidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />

      <!-- 主内容区域 -->
      <el-container class="main-container">
        <!-- 面包屑导航 -->
        <AppBreadcrumb />

        <!-- 路由内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppBreadcrumb from '@/components/layout/AppBreadcrumb.vue'

const route = useRoute()
const appStore = useAppStore()

// 响应式数据
const loading = ref(false)
const sidebarCollapsed = ref(false)

// 计算属性
const cachedViews = computed(() => {
  return ['Dashboard', 'StudentList', 'CourseList', 'EnrollmentList', 'GradeList']
})

// 侧边栏切换
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 初始化
onMounted(async () => {
  try {
    loading.value = true

    // 加载用户信息
    await appStore.loadUserInfo()

    // 加载菜单
    await appStore.loadMenus()

    // 设置主题
    appStore.initTheme()

  } catch (error) {
    console.error('App initialization error:', error)
    ElMessage.error('应用初始化失败')
  } finally {
    await nextTick()
    loading.value = false
  }
})
</script>

<style lang="scss">
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--el-bg-color);
}

.main-container {
  height: calc(100vh - 60px); // 减去头部高度
  transition: margin-left 0.3s ease;

  .main-content {
    padding: 16px;
    background-color: var(--el-bg-color-page);
    min-height: calc(100vh - 60px - 60px); // 减去头部和面包屑高度
    overflow-y: auto;
  }
}

// 当侧边栏折叠时调整主容器边距
.main-container.sidebar-collapsed {
  margin-left: 64px;
}

// 响应式设计
@media (max-width: 768px) {
  .main-container {
    margin-left: 0;
  }
}
</style>