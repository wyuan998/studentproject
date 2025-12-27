<template>
  <div class="permission-demo">
    <el-card class="demo-card">
      <template #header>
        <div class="card-header">
          <h3>权限系统演示</h3>
          <el-select v-model="selectedRole" placeholder="选择角色模拟" @change="changeRole">
            <el-option label="管理员 (Admin)" value="admin" />
            <el-option label="教师 (Teacher)" value="teacher" />
            <el-option label="学生 (Student)" value="student" />
          </el-select>
        </div>
      </template>

      <div class="permission-info">
        <el-descriptions title="当前角色信息" :column="2" border>
          <el-descriptions-item label="角色">
            <el-tag :type="getRoleTagType(currentRole)">{{ currentRole.toUpperCase() }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="权限等级">
            {{ hierarchyLevel }}
          </el-descriptions-item>
          <el-descriptions-item label="权限数量">
            {{ permissions.length }}
          </el-descriptions-item>
          <el-descriptions-item label="主要权限">
            <el-tag v-for="perm in mainPermissions" :key="perm" size="small" style="margin: 2px;">
              {{ perm }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider />

      <div class="permission-tests">
        <h4>权限测试</h4>

        <el-row :gutter="20">
          <el-col :span="12">
            <h5>指令测试</h5>

            <div class="test-section">
              <h6>管理权限 (只有管理员可见)</h6>
              <div v-permission="'manage_users'" class="permission-box success">
                <el-icon><User /></el-icon>
                <span>用户管理功能 (v-permission="'manage_users'")</span>
              </div>
              <div v-permission="'system_settings'" class="permission-box success">
                <el-icon><Tools /></el-icon>
                <span>系统设置功能 (v-permission="'system_settings'")</span>
              </div>
            </div>

            <div class="test-section">
              <h6>教学权限 (教师和管理员可见)</h6>
              <div v-permission="'manage_grades'" class="permission-box warning">
                <el-icon><DocumentChecked /></el-icon>
                <span>成绩管理功能 (v-permission="'manage_grades'")</span>
              </div>
            </div>

            <div class="test-section">
              <h6>学生权限 (所有角色可见)</h6>
              <div v-permission="'read'" class="permission-box info">
                <el-icon><View /></el-icon>
                <span>查看功能 (v-permission="'read'")</span>
              </div>
            </div>
          </el-col>

          <el-col :span="12">
            <h5>组件测试</h5>

            <div class="test-section">
              <h6>权限组件测试</h6>
              <PermissionGuard permission="manage_users" show-fallback>
                <template #default>
                  <el-alert type="success" :closable="false">
                    <template #title>
                      ✅ 你有权限管理用户
                    </template>
                  </el-alert>
                </template>
                <template #fallback>
                  <el-alert type="error" :closable="false">
                    <template #title>
                      ❌ 你没有权限管理用户
                    </template>
                  </el-alert>
                </template>
              </PermissionGuard>
            </div>

            <div class="test-section">
              <h6>角色测试</h6>
              <div v-role="'admin'" class="permission-box success">
                <el-icon><Avatar /></el-icon>
                <span>管理员专用区域 (v-role="'admin'")</span>
              </div>
              <div v-role="['admin', 'teacher']" class="permission-box warning">
                <el-icon><Reading /></el-icon>
                <span>教学人员区域 (v-role="['admin', 'teacher']")</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <el-divider />

      <div class="all-permissions">
        <h4>完整权限列表</h4>
        <div class="permissions-grid">
          <div
            v-for="perm in permissions"
            :key="perm"
            :class="['permission-item', getPermissionClass(perm)]"
          >
            <el-icon><Check /></el-icon>
            <span>{{ perm }}</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  User, Tools, DocumentChecked, View, Avatar, Reading, Check
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const selectedRole = ref<string>('admin')

// 模拟角色数据
const roleData = {
  admin: {
    permissions: [
      'read', 'write', 'delete', 'manage_users', 'manage_courses',
      'manage_grades', 'system_settings', 'view_all_students', 'view_all_teachers',
      'view_all_courses', 'manage_system', 'export_data', 'import_data'
    ],
    hierarchyLevel: 100
  },
  teacher: {
    permissions: [
      'read', 'write', 'manage_own_courses', 'manage_grades', 'view_students',
      'view_assigned_courses', 'edit_own_profile', 'publish_grades'
    ],
    hierarchyLevel: 50
  },
  student: {
    permissions: [
      'read', 'view_own_grades', 'view_own_courses', 'edit_own_profile',
      'view_enrolled_courses', 'select_courses', 'drop_courses'
    ],
    hierarchyLevel: 10
  }
}

// 计算属性
const currentRole = computed(() => selectedRole.value)
const permissions = computed(() => roleData[selectedRole.value as keyof typeof roleData].permissions)
const hierarchyLevel = computed(() => roleData[selectedRole.value as keyof typeof roleData].hierarchyLevel)

// 主要权限显示
const mainPermissions = computed(() => {
  const perms = permissions.value
  if (perms.includes('manage_users')) {
    return ['用户管理', '系统管理', '数据管理']
  } else if (perms.includes('manage_grades')) {
    return ['成绩管理', '课程管理', '学生查看']
  } else {
    return ['查看成绩', '课程选择', '个人信息']
  }
})

// 方法
const changeRole = (role: string) => {
  // 模拟切换角色，更新用户store
  userStore.roles = [role]
  userStore.permissions = roleData[role as keyof typeof roleData].permissions
}

const getRoleTagType = (role: string) => {
  const types: Record<string, string> = {
    admin: 'danger',
    teacher: 'warning',
    student: 'primary'
  }
  return types[role] || 'info'
}

const getPermissionClass = (permission: string) => {
  if (permission.includes('manage') || permission.includes('delete')) {
    return 'high-permission'
  } else if (permission.includes('view') || permission.includes('read')) {
    return 'low-permission'
  } else {
    return 'medium-permission'
  }
}

onMounted(() => {
  // 初始化为管理员角色
  changeRole('admin')
})
</script>

<style scoped>
.permission-demo {
  padding: 20px;
}

.demo-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}

.permission-info {
  margin: 20px 0;
}

.permission-tests h4 {
  color: #303133;
  margin-bottom: 15px;
}

.permission-tests h5 {
  color: #606266;
  margin-bottom: 10px;
}

.permission-tests h6 {
  color: #909399;
  margin-bottom: 8px;
  font-size: 14px;
}

.test-section {
  margin-bottom: 20px;
}

.permission-box {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  margin: 8px 0;
  border-radius: 6px;
  border-left: 4px solid;
}

.permission-box.success {
  background: #f0f9ff;
  border-left-color: #67c23a;
  color: #67c23a;
}

.permission-box.warning {
  background: #fdf6ec;
  border-left-color: #e6a23c;
  color: #e6a23c;
}

.permission-box.info {
  background: #f4f4f5;
  border-left-color: #909399;
  color: #909399;
}

.permission-box .el-icon {
  margin-right: 8px;
}

.all-permissions h4 {
  color: #303133;
  margin-bottom: 15px;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.permission-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  background: #f8f9fa;
}

.permission-item.high-permission {
  background: #fef0f0;
  color: #f56c6c;
}

.permission-item.medium-permission {
  background: #fdf6ec;
  color: #e6a23c;
}

.permission-item.low-permission {
  background: #f0f9ff;
  color: #409eff;
}

.permission-item .el-icon {
  margin-right: 6px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .permissions-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
}
</style>