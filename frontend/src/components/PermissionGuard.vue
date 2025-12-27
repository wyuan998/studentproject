<template>
  <div v-if="hasAccess">
    <slot />
  </div>
  <div v-else-if="showFallback" class="permission-fallback">
    <slot name="fallback">
      <el-empty
        :image-size="120"
        description="权限不足"
      >
        <template #image>
          <el-icon size="120" color="#c0c4cc">
            <Lock />
          </el-icon>
        </template>
        <el-button type="primary" @click="$router.back()">
          返回
        </el-button>
      </el-empty>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed, type PropType } from 'vue'
import { useUserStore } from '@/stores/user'
import { Lock } from '@element-plus/icons-vue'

const props = defineProps({
  // 权限要求
  permission: {
    type: [String, Array] as PropType<string | string[]>,
    default: null
  },
  // 角色要求
  role: {
    type: [String, Array] as PropType<string | string[]>,
    default: null
  },
  // 权限检查模式：'any'（任意一个）或 'all'（所有）
  mode: {
    type: String as PropType<'any' | 'all'>,
    default: 'any'
  },
  // 是否显示无权限时的替代内容
  showFallback: {
    type: Boolean,
    default: true
  }
})

const userStore = useUserStore()

// 检查是否有访问权限
const hasAccess = computed(() => {
  // 如果同时指定了权限和角色，需要同时满足
  let hasPermissionAccess = true
  let hasRoleAccess = true

  // 检查权限
  if (props.permission) {
    if (typeof props.permission === 'string') {
      hasPermissionAccess = userStore.hasPermission(props.permission)
    } else if (Array.isArray(props.permission)) {
      hasPermissionAccess = props.mode === 'all'
        ? userStore.hasAllPermissions(props.permission)
        : userStore.hasAnyPermission(props.permission)
    }
  }

  // 检查角色
  if (props.role) {
    if (typeof props.role === 'string') {
      hasRoleAccess = userStore.roles?.includes(props.role) || false
    } else if (Array.isArray(props.role)) {
      hasRoleAccess = props.mode === 'all'
        ? props.role.every(role => userStore.roles?.includes(role))
        : props.role.some(role => userStore.roles?.includes(role))
    }
  }

  return hasPermissionAccess && hasRoleAccess
})
</script>

<style scoped>
.permission-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 20px;
}
</style>