<template>
  <el-breadcrumb class="app-breadcrumb" separator="/">
    <el-breadcrumb-item
      v-for="item in breadcrumbs"
      :key="item.path"
      :to="item.path"
    >
      {{ item.title }}
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const breadcrumbs = computed(() => appStore.breadcrumbs)
</script>

<style lang="scss" scoped>
.app-breadcrumb {
  display: inline-block;
  font-size: 14px;
  line-height: 50px;
  margin-left: 8px;

  :deep(.el-breadcrumb__item) {
    .el-breadcrumb__inner {
      color: var(--el-text-color-regular);
      font-weight: normal;

      &:hover {
        color: var(--el-color-primary);
      }
    }

    &:last-child {
      .el-breadcrumb__inner {
        color: var(--el-text-color-primary);
        font-weight: 600;
        cursor: text;

        &:hover {
          color: var(--el-text-color-primary);
        }
      }
    }
  }

  :deep(.el-breadcrumb__separator) {
    color: var(--el-text-color-placeholder);
    margin: 0 8px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .app-breadcrumb {
    display: none;
  }
}
</style>