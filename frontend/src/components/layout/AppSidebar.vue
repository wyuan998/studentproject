<template>
  <el-aside
    class="app-sidebar"
    :class="{ collapsed: collapsed }"
    :width="collapsed ? '64px' : '220px'"
  >
    <!-- Logo区域 -->
    <div class="logo-container">
      <router-link to="/dashboard" class="logo-link">
        <img v-if="!collapsed" src="/logo.png" alt="Logo" class="logo-img" />
        <img v-else src="/logo-mini.png" alt="Logo" class="logo-img-mini" />
        <h1 v-if="!collapsed" class="logo-title">学生管理系统</h1>
      </router-link>
    </div>

    <!-- 菜单 -->
    <el-scrollbar class="sidebar-scrollbar">
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :unique-opened="true"
        :router="true"
        background-color="var(--el-bg-color)"
        text-color="var(--el-text-color-primary)"
        active-text-color="var(--el-color-primary)"
        class="sidebar-menu"
      >
        <template v-for="route in menuRoutes" :key="route.path">
          <!-- 有子菜单的情况 -->
          <el-sub-menu v-if="route.children && route.children.length > 0" :index="route.path">
            <template #title>
              <el-icon v-if="route.meta?.icon">
                <component :is="route.meta.icon" />
              </el-icon>
              <span>{{ route.meta?.title }}</span>
            </template>

            <el-menu-item
              v-for="child in route.children"
              :key="child.path"
              :index="child.path"
              v-show="!child.meta?.hidden"
            >
              <el-icon v-if="child.meta?.icon">
                <component :is="child.meta.icon" />
              </el-icon>
              <span>{{ child.meta?.title }}</span>
            </el-menu-item>
          </el-sub-menu>

          <!-- 无子菜单的情况 -->
          <el-menu-item v-else :index="route.path" v-show="!route.meta?.hidden">
            <el-icon v-if="route.meta?.icon">
              <component :is="route.meta.icon" />
            </el-icon>
            <span>{{ route.meta?.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-scrollbar>

    <!-- 折叠按钮 -->
    <div class="collapse-trigger" @click="$emit('toggle')">
      <el-icon size="16">
        <Expand v-if="collapsed" />
        <Fold v-else />
      </el-icon>
    </div>
  </el-aside>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { Fold, Expand } from '@element-plus/icons-vue'

interface Props {
  collapsed: boolean
}

const props = defineProps<Props>()
defineEmits<{
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

// 获取所有路由配置
const allRoutes = router.options.routes.find(r => r.path === '/')?.children || []

// 过滤有权限的菜单路由
const menuRoutes = computed(() => {
  return permissionStore.getAccessibleMenus(allRoutes)
})

// 当前激活的菜单
const activeMenu = computed(() => {
  const { path } = route
  // 处理详情页等路由，匹配到列表页
  if (path.includes('/detail/') || path.includes('/edit/')) {
    const pathSegments = path.split('/')
    if (pathSegments.length >= 3) {
      return `/${pathSegments[1]}/list`
    }
  }
  return path
})

// 监听路由变化，更新面包屑
watch(
  () => route.path,
  (newPath) => {
    updateBreadcrumbs(newPath)
  },
  { immediate: true }
)

// 更新面包屑
const updateBreadcrumbs = (path: string) => {
  const breadcrumbs: Array<{ title: string; path?: string }> = []
  const pathSegments = path.split('/').filter(Boolean)

  // 查找匹配的路由
  let currentRoute = router.resolve(path)
  let matchedRoutes = currentRoute.matched

  if (matchedRoutes.length === 0) {
    // 尝试匹配父路由
    const parentPath = '/' + pathSegments.slice(0, -1).join('/')
    currentRoute = router.resolve(parentPath)
    matchedRoutes = currentRoute.matched
  }

  matchedRoutes.forEach((matchedRoute, index) => {
    if (matchedRoute.meta?.title && matchedRoute.path !== '/') {
      breadcrumbs.push({
        title: matchedRoute.meta.title,
        path: index === matchedRoutes.length - 1 ? undefined : matchedRoute.path
      })
    }
  })

  // 如果路由中有自定义面包屑，使用自定义的
  if (route.meta?.breadcrumbs) {
    breadcrumbs.splice(0, breadcrumbs.length, ...route.meta.breadcrumbs)
  }

  // 更新到store
  const appStore = useAppStore()
  appStore.setBreadcrumbs(breadcrumbs)
}
</script>

<style lang="scss" scoped>
.app-sidebar {
  position: relative;
  height: 100vh;
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  &.collapsed {
    :deep(.el-sub-menu__title) {
      padding: 0 20px !important;
    }

    :deep(.el-menu-item) {
      padding: 0 20px !important;
    }

    :deep(.el-sub-menu__icon-arrow) {
      display: none;
    }

    .logo-title {
      display: none;
    }

    .collapse-trigger {
      width: 64px;
    }
  }
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  flex-shrink: 0;

  .logo-link {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: var(--el-text-color-primary);
    transition: all 0.3s ease;

    &:hover {
      color: var(--el-color-primary);
    }
  }

  .logo-img {
    width: 32px;
    height: 32px;
    margin-right: 12px;
  }

  .logo-img-mini {
    width: 32px;
    height: 32px;
  }

  .logo-title {
    font-size: 18px;
    font-weight: 600;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.sidebar-scrollbar {
  flex: 1;
  overflow: hidden;

  :deep(.el-scrollbar__view) {
    height: 100%;
  }
}

.sidebar-menu {
  border: none;
  height: 100%;

  :deep(.el-menu-item) {
    height: 50px;
    line-height: 50px;
    margin: 0 8px;
    border-radius: 6px;
    transition: all 0.3s ease;

    &:hover {
      background-color: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
    }

    &.is-active {
      background-color: var(--el-color-primary-light-8);
      color: var(--el-color-primary);
      font-weight: 600;
    }

    .el-icon {
      font-size: 18px;
      margin-right: 8px;
    }
  }

  :deep(.el-sub-menu) {
    .el-sub-menu__title {
      height: 50px;
      line-height: 50px;
      margin: 0 8px;
      border-radius: 6px;
      transition: all 0.3s ease;

      &:hover {
        background-color: var(--el-color-primary-light-9);
        color: var(--el-color-primary);
      }

      .el-icon {
        font-size: 18px;
        margin-right: 8px;
      }
    }

    .el-menu-item {
      padding-left: 48px !important;

      &::before {
        content: '';
        position: absolute;
        left: 28px;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 4px;
        background-color: var(--el-text-color-placeholder);
        border-radius: 50%;
      }

      &:hover::before {
        background-color: var(--el-color-primary);
      }

      &.is-active::before {
        background-color: var(--el-color-primary);
      }
    }
  }

  :deep(.el-menu--collapse) {
    .el-sub-menu {
      & > .el-sub-menu__title {
        padding: 0 20px !important;
      }

      .el-menu-item {
        padding-left: 20px !important;

        &::before {
          left: 20px;
        }
      }
    }
  }
}

.collapse-trigger {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid var(--el-border-color-light);
  cursor: pointer;
  color: var(--el-text-color-regular);
  transition: all 0.3s ease;
  width: 220px;

  &:hover {
    color: var(--el-color-primary);
    background-color: var(--el-fill-color-light);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: var(--el-index-top);
    transform: translateX(-100%);
    transition: transform 0.3s ease;

    &.mobile-open {
      transform: translateX(0);
    }
  }
}
</style>