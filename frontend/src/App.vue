<template>
  <div id="app" class="app-container">
    <!-- 全局加载遮罩 -->
    <el-loading
      v-if="loading"
      fullscreen
      :lock="true"
      text="正在加载..."
      background-color="rgba(0, 0, 0, 0.7)"
    />

    <!-- 登录页面直接显示 -->
    <template v-if="$route.meta.showLayout === false">
      <router-view />
    </template>

    <!-- 主应用布局 -->
    <template v-else>
      <el-container class="layout-container">
        <!-- 侧边栏 -->
        <AppSidebar :collapsed="appStore.sidebarCollapsed" @toggle="appStore.toggleSidebar" />

        <!-- 主体内容 -->
        <el-container>
          <!-- 头部 -->
          <AppHeader />

          <!-- 内容区域 -->
          <el-main class="main-content">
            <div class="content-wrapper">
              <!-- 面包屑 -->
              <div class="breadcrumb-wrapper">
                <AppBreadcrumb />
              </div>

              <!-- 页面内容 -->
              <div class="page-content">
                <router-view v-slot="{ Component, route }">
                  <transition name="fade-transform" mode="out-in">
                    <keep-alive :include="keepAliveIncludes">
                      <component :is="Component" :key="route.path" />
                    </keep-alive>
                  </transition>
                </router-view>
              </div>
            </div>
          </el-main>
        </el-container>
      </el-container>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppBreadcrumb from '@/components/layout/AppBreadcrumb.vue'

const appStore = useAppStore()

// 需要缓存的路由组件
const keepAliveIncludes = computed(() => {
  // 这里可以根据实际需要配置需要缓存的组件名称
  return ['Dashboard', 'StudentList', 'TeacherList', 'CourseList']
})
</script>

<style lang="scss">
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: var(--el-bg-color);
}

.layout-container {
  height: 100vh;
  overflow: hidden;
}

.el-container {
  height: 100%;
}

.main-content {
  padding: 0;
  overflow: hidden;
  background-color: var(--el-bg-color-page);
}

.content-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
}

.breadcrumb-wrapper {
  margin-bottom: 16px;
}

.page-content {
  flex: 1;
  min-height: 0;
}

// 页面切换动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

// 响应式设计
@media (max-width: 768px) {
  .content-wrapper {
    padding: 12px;
  }

  .breadcrumb-wrapper {
    margin-bottom: 12px;
  }
}
</style>