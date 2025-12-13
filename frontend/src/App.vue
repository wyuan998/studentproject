<template>
  <div id="app" class="app-container">
    <SimpleApp />
  </div>
</template>

<script setup lang="ts">
import SimpleApp from './SimpleApp.vue'
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