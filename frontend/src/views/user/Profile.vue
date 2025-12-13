<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
          <el-button type="primary" @click="showEditDialog = true">
            编辑资料
          </el-button>
        </div>
      </template>

      <div class="profile-content">
        <div class="avatar-section">
          <el-avatar :size="120" :src="userStore.userInfo?.avatar">
            {{ (userStore.userInfo?.real_name || userStore.userInfo?.username || 'U').charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="avatar-actions">
            <el-button text type="primary" @click="handleAvatarUpload">
              更换头像
            </el-button>
          </div>
        </div>

        <div class="info-section">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户名">
              {{ userStore.userInfo?.username }}
            </el-descriptions-item>
            <el-descriptions-item label="真实姓名">
              {{ userStore.userInfo?.real_name || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userStore.userInfo?.email }}
            </el-descriptions-item>
            <el-descriptions-item label="手机号">
              {{ userStore.userInfo?.phone || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag
                v-for="role in userStore.roles"
                :key="role"
                :type="getRoleType(role)"
                class="role-tag"
              >
                {{ getRoleLabel(role) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(userStore.userInfo?.status)">
                {{ getStatusLabel(userStore.userInfo?.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">
              {{ formatDate(userStore.userInfo?.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后登录">
              {{ formatDate(userStore.userInfo?.last_login_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>

    <!-- 安全设置 -->
    <el-card class="security-card">
      <template #header>
        <span>安全设置</span>
      </template>

      <div class="security-list">
        <div class="security-item">
          <div class="security-info">
            <div class="security-title">登录密码</div>
            <div class="security-desc">保护账户安全的重要方式</div>
          </div>
          <el-button text type="primary" @click="showChangePassword = true">
            修改密码
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="500px"
      @closed="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="editForm.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" :loading="updateLoading" @click="handleUpdateProfile">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <ChangePasswordDialog v-model="showChangePassword" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import ChangePasswordDialog from '@/components/common/ChangePasswordDialog.vue'

const userStore = useUserStore()

// 响应式数据
const showEditDialog = ref(false)
const showChangePassword = ref(false)
const updateLoading = ref(false)
const editFormRef = ref<FormInstance>()

const editForm = reactive({
  real_name: '',
  email: '',
  phone: ''
})

// 表单验证规则
const editRules: FormRules = {
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度为2-10位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ]
}

// 方法
const handleAvatarUpload = () => {
  ElMessage.info('头像上传功能开发中...')
}

const handleUpdateProfile = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()

    updateLoading.value = true

    const success = await userStore.updateUserInfo(editForm)

    if (success) {
      showEditDialog.value = false
    }
  } catch (error) {
    console.error('Update profile error:', error)
  } finally {
    updateLoading.value = false
  }
}

const resetEditForm = () => {
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }

  // 重置表单数据
  Object.assign(editForm, {
    real_name: userStore.userInfo?.real_name || '',
    email: userStore.userInfo?.email || '',
    phone: userStore.userInfo?.phone || ''
  })
}

const getRoleType = (role: string) => {
  const typeMap: Record<string, string> = {
    admin: 'danger',
    teacher: 'warning',
    student: 'primary'
  }
  return typeMap[role] || 'info'
}

const getRoleLabel = (role: string) => {
  const labelMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return labelMap[role] || role
}

const getStatusType = (status?: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    locked: 'danger'
  }
  return typeMap[status || ''] || 'info'
}

const getStatusLabel = (status?: string) => {
  const labelMap: Record<string, string> = {
    active: '正常',
    inactive: '未激活',
    locked: '已锁定'
  }
  return labelMap[status || ''] || '未知'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '暂无数据'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 初始化表单数据
resetEditForm()
</script>

<style lang="scss" scoped>
.profile-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-card,
.security-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.profile-content {
  display: flex;
  gap: 40px;

  .avatar-section {
    text-align: center;

    .avatar-actions {
      margin-top: 16px;
    }
  }

  .info-section {
    flex: 1;

    .role-tag {
      margin-right: 8px;
    }
  }
}

.security-list {
  .security-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);

    &:last-child {
      border-bottom: none;
    }

    .security-info {
      .security-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin-bottom: 4px;
      }

      .security-desc {
        font-size: 14px;
        color: var(--el-text-color-regular);
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .profile-container {
    padding: 12px;
  }

  .profile-content {
    flex-direction: column;
    gap: 20px;
  }
}
</style>