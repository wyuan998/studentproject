<template>
  <div class="permission-demo-page">
    <h1>权限系统演示页面</h1>

    <!-- 当前角色信息 -->
    <el-card class="role-info">
      <h2>当前用户角色: {{ currentRole }}</h2>
      <div class="role-details">
        <p>权限数量: {{ permissions.length }}</p>
        <div class="permissions-list">
          <el-tag
            v-for="perm in permissions"
            :key="perm"
            size="small"
            style="margin: 2px;"
          >
            {{ perm }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 权限测试区域 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <h3>管理员功能 (仅管理员可见)</h3>
          <div v-permission="'manage_users'" class="permission-content success">
            ✅ 用户管理 - 您可以看到这个内容
          </div>
          <div v-permission="'system_settings'" class="permission-content success">
            ✅ 系统设置 - 您可以看到这个内容
          </div>
          <PermissionGuard permission="delete" show-fallback>
            <div class="permission-content danger">
              ⚠️ 删除功能 - 危险操作权限
            </div>
          </PermissionGuard>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <h3>教学功能 (教师和管理员可见)</h3>
          <div v-permission="'manage_grades'" class="permission-content warning">
            📊 成绩管理 - 您可以管理成绩
          </div>
          <div v-permission="'view_students'" class="permission-content info">
            👥 查看学生 - 您可以查看学生信息
          </div>
          <div v-role="['admin', 'teacher']" class="permission-content primary">
            🎓 教学人员专用区域
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学生功能 -->
    <el-card style="margin-top: 20px;">
      <h3>学生功能 (所有角色可见)</h3>
      <div v-permission="'read'" class="permission-content default">
        📖 基础查看功能
      </div>
      <div v-permission="'view_own_grades'" class="permission-content default">
        📈 查看自己的成绩
      </div>
      <div v-permission="'edit_own_profile'" class="permission-content default">
        ✏️ 编辑个人资料
      </div>
    </el-card>

    <!-- 角色切换演示 -->
    <el-card style="margin-top: 20px;">
      <h3>角色切换演示</h3>
      <p>选择不同角色查看权限差异：</p>
      <el-radio-group v-model="selectedRole" @change="switchRole">
        <el-radio-button label="admin">管理员</el-radio-button>
        <el-radio-button label="teacher">教师</el-radio-button>
        <el-radio-button label="student">学生</el-radio-button>
      </el-radio-group>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import PermissionGuard from '@/components/PermissionGuard.vue'

const userStore = useUserStore()
const selectedRole = ref('admin')

// 模拟角色权限数据
const rolePermissions = {
  admin: [
    'read', 'write', 'delete', 'manage_users', 'manage_courses',
    'manage_grades', 'system_settings', 'view_all_students', 'view_all_teachers',
    'view_all_courses', 'manage_system', 'export_data', 'import_data'
  ],
  teacher: [
    'read', 'write', 'manage_own_courses', 'manage_grades', 'view_students',
    'view_assigned_courses', 'edit_own_profile', 'publish_grades'
  ],
  student: [
    'read', 'view_own_grades', 'view_own_courses', 'edit_own_profile',
    'view_enrolled_courses', 'select_courses', 'drop_courses'
  ]
}

const currentRole = computed(() => {
  const roles = userStore.roles || []
  if (roles.includes('admin')) return '管理员'
  if (roles.includes('teacher')) return '教师'
  if (roles.includes('student')) return '学生'
  return '未知'
})

const permissions = computed(() => {
  const roles = userStore.roles || []
  if (roles.includes('admin')) return rolePermissions.admin
  if (roles.includes('teacher')) return rolePermissions.teacher
  if (roles.includes('student')) return rolePermissions.student
  return []
})

const switchRole = (role: string) => {
  // 模拟切换角色
  userStore.roles = [role]
  userStore.permissions = rolePermissions[role as keyof typeof rolePermissions]

  // 更新用户信息中的角色
  if (userStore.userInfo) {
    userStore.userInfo.role = role
    userStore.userInfo.roles = [role]
    userStore.userInfo.permissions = rolePermissions[role as keyof typeof rolePermissions]
  }
}

onMounted(() => {
  // 初始化为管理员角色（如果没有登录信息）
  if (!userStore.isAuthenticated) {
    switchRole('admin')
  }
})
</script>

<style scoped>
.permission-demo-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.role-info {
  margin-bottom: 20px;
}

.role-details {
  margin-top: 15px;
}

.permissions-list {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.permission-content {
  padding: 15px;
  margin: 10px 0;
  border-radius: 6px;
  border-left: 4px solid;
}

.permission-content.success {
  background: #f0f9ff;
  border-left-color: #67c23a;
  color: #67c23a;
}

.permission-content.warning {
  background: #fdf6ec;
  border-left-color: #e6a23c;
  color: #e6a23c;
}

.permission-content.info {
  background: #f4f4f5;
  border-left-color: #909399;
  color: #909399;
}

.permission-content.primary {
  background: #ecf5ff;
  border-left-color: #409eff;
  color: #409eff;
}

.permission-content.danger {
  background: #fef0f0;
  border-left-color: #f56c6c;
  color: #f56c6c;
}

.permission-content.default {
  background: #f8f9fa;
  border-left-color: #606266;
  color: #606266;
}

h1, h2, h3 {
  color: #303133;
}
</style>