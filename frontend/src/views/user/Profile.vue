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
          <el-avatar :size="120" :src="profileData?.avatar">
            {{ getAvatarText() }}
          </el-avatar>
          <div class="avatar-actions">
            <el-button text type="primary" @click="handleAvatarUpload">
              更换头像
            </el-button>
            <el-button text type="danger" @click="handleDeleteAvatar" v-if="profileData?.avatar">
              删除头像
            </el-button>
          </div>
        </div>

        <div class="info-section">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户名">
              {{ userStore.userInfo?.username }}
            </el-descriptions-item>
            <el-descriptions-item label="姓名">
              {{ profileData?.first_name }} {{ profileData?.last_name }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userStore.userInfo?.email }}
            </el-descriptions-item>
            <el-descriptions-item label="手机号">
              {{ profileData?.phone || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="性别">
              {{ getGenderLabel(profileData?.gender) }}
            </el-descriptions-item>
            <el-descriptions-item label="生日">
              {{ formatDate(profileData?.birthday) }}
            </el-descriptions-item>
            <el-descriptions-item label="部门">
              {{ profileData?.department || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="专业">
              {{ profileData?.major || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="学位">
              {{ profileData?.degree || '未设置' }}
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
            <el-descriptions-item label="地址" :span="2">
              {{ formatAddress(profileData) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>

    <!-- 安全设置 -->
    <el-card class="security-card">
      <template #header>
        <div class="card-header">
          <span>安全设置</span>
        </div>
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

    <!-- 数据管理 -->
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>数据管理</span>
        </div>
      </template>

      <div class="data-list">
        <div class="data-item">
          <div class="data-info">
            <div class="data-title">导出个人信息</div>
            <div class="data-desc">导出您的个人资料数据</div>
          </div>
          <div class="data-actions">
            <el-dropdown @command="handleExportProfile">
              <el-button text type="primary">
                导出数据 <el-icon><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="json">JSON格式</el-dropdown-item>
                  <el-dropdown-item command="pdf" disabled>PDF格式（开发中）</el-dropdown-item>
                  <el-dropdown-item command="csv" disabled>CSV格式（开发中）</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div class="data-item">
          <div class="data-info">
            <div class="data-title">变更历史</div>
            <div class="data-desc">查看个人信息的变更记录</div>
          </div>
          <el-button text type="primary" @click="showHistoryDialog = true">
            查看历史
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="600px"
      @closed="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓" prop="first_name">
              <el-input v-model="editForm.first_name" placeholder="请输入姓" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名" prop="last_name">
              <el-input v-model="editForm.last_name" placeholder="请输入名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="editForm.gender" placeholder="请选择性别">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生日">
              <el-date-picker
                v-model="editForm.birthday"
                type="date"
                placeholder="选择生日"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="部门">
          <el-input v-model="editForm.department" placeholder="请输入部门" />
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="editForm.major" placeholder="请输入专业" />
        </el-form-item>
        <el-form-item label="学位">
          <el-input v-model="editForm.degree" placeholder="请输入学位" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editForm.address" placeholder="请输入详细地址" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="省份">
              <el-input v-model="editForm.province" placeholder="请输入省份" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="城市">
              <el-input v-model="editForm.city" placeholder="请输入城市" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="邮编">
              <el-input v-model="editForm.postal_code" placeholder="请输入邮编" />
            </el-form-item>
          </el-col>
        </el-row>
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

    <!-- 头像上传对话框 -->
    <el-dialog v-model="showAvatarDialog" title="更换头像" width="400px">
      <input
        ref="avatarInput"
        type="file"
        accept="image/*"
        style="display: none"
        @change="handleFileChange"
      />
      <div class="avatar-upload-content">
        <div v-if="avatarPreview" class="avatar-preview">
          <el-avatar :size="150" :src="avatarPreview" />
        </div>
        <div class="avatar-upload-actions">
          <el-button @click="triggerFileInput">选择图片</el-button>
          <el-button type="primary" :loading="avatarLoading" @click="handleUploadAvatar">
            确认上传
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <ChangePasswordDialog v-model="showChangePassword" />

    <!-- 变更历史对话框 -->
    <el-dialog
      v-model="showHistoryDialog"
      title="个人信息变更历史"
      width="800px"
    >
      <div class="history-content">
        <el-timeline v-if="historyList.length > 0">
          <el-timeline-item
            v-for="(item, index) in historyList"
            :key="item.id"
            :timestamp="formatDate(item.timestamp)"
            :type="index === 0 ? 'primary' : 'info'"
          >
            <div class="history-item">
              <div class="history-info">
                <div class="history-time">{{ formatDate(item.timestamp) }}</div>
                <div class="history-ip">IP: {{ item.ip_address }}</div>
              </div>
              <div class="history-changes">
                <el-tag
                  v-for="change in item.changes"
                  :key="change.field"
                  size="small"
                  type="info"
                  class="change-tag"
                >
                  {{ getFieldName(change.field) }}:
                  {{ change.old_value || '空' }} → {{ change.new_value || '空' }}
                </el-tag>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>

        <el-empty v-else description="暂无变更记录" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import ChangePasswordDialog from '@/components/common/ChangePasswordDialog.vue'
import type { UserProfileData } from '@/types/auth'

const userStore = useUserStore()

// 响应式数据
const showEditDialog = ref(false)
const showChangePassword = ref(false)
const showAvatarDialog = ref(false)
const showHistoryDialog = ref(false)
const updateLoading = ref(false)
const avatarLoading = ref(false)
const editFormRef = ref<FormInstance>()
const avatarInput = ref<HTMLInputElement>()
const avatarPreview = ref('')
const avatarFile = ref<File | null>(null)

const profileData = ref<any>(null)
const historyList = ref<any[]>([])

const editForm = reactive<UserProfileData>({
  first_name: '',
  last_name: '',
  phone: '',
  gender: undefined,
  birthday: '',
  address: '',
  city: '',
  province: '',
  postal_code: '',
  department: '',
  major: '',
  degree: '',
  email: ''
})

// 表单验证规则
const editRules: FormRules = {
  first_name: [
    { required: true, message: '请输入姓', trigger: 'blur' },
    { min: 1, max: 50, message: '长度为1-50位', trigger: 'blur' }
  ],
  last_name: [
    { required: true, message: '请输入名', trigger: 'blur' },
    { min: 1, max: 50, message: '长度为1-50位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ]
}

// 生命周期
onMounted(() => {
  loadProfileData()
})

// 方法
const loadProfileData = async () => {
  try {
    const response = await authApi.getProfile()
    if (response.success) {
      profileData.value = response.data
    }
  } catch (error) {
    console.error('Load profile error:', error)
    // 设置默认数据避免页面空白
    profileData.value = {
      first_name: '系统',
      last_name: '管理员',
      email: 'admin@example.com',
      phone: '13800138000',
      gender: 'male',
      birthday: '2000-01-01',
      address: '北京市海淀区中关村大街1号',
      city: '北京市',
      province: '北京',
      postal_code: '100000',
      department: '计算机学院',
      major: '计算机科学与技术',
      degree: '本科'
    }
  }
}

const handleAvatarUpload = () => {
  showAvatarDialog.value = true
  avatarPreview.value = ''
  avatarFile.value = null
}

const triggerFileInput = () => {
  avatarInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    // 检查文件大小（2MB）
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过2MB')
      return
    }

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      return
    }

    avatarFile.value = file

    // 生成预览
    const reader = new FileReader()
    reader.onload = (e) => {
      avatarPreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const handleUploadAvatar = async () => {
  if (!avatarFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }

  try {
    avatarLoading.value = true

    // 转换为Base64
    const base64 = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(avatarFile.value!)
    })

    const response = await authApi.uploadAvatar(base64)

    if (response.success) {
      ElMessage.success('头像上传成功')
      showAvatarDialog.value = false
      // 更新用户信息
      await userStore.getUserInfo()
      await loadProfileData()
    }
  } catch (error: any) {
    console.error('Upload avatar error:', error)
    ElMessage.error(error.response?.data?.message || '头像上传失败')
  } finally {
    avatarLoading.value = false
  }
}

const handleDeleteAvatar = async () => {
  try {
    await ElMessageBox.confirm('确定要删除头像吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await authApi.deleteAvatar()

    if (response.success) {
      ElMessage.success('头像删除成功')
      // 更新用户信息
      await userStore.getUserInfo()
      await loadProfileData()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Delete avatar error:', error)
      ElMessage.error(error.response?.data?.message || '头像删除失败')
    }
  }
}

const handleUpdateProfile = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()

    updateLoading.value = true

    const response = await authApi.updateProfile(editForm)

    if (response.success) {
      ElMessage.success('个人信息更新成功')
      showEditDialog.value = false

      // 更新用户信息
      await userStore.getUserInfo()
      await loadProfileData()
    }
  } catch (error: any) {
    console.error('Update profile error:', error)
    ElMessage.error(error.response?.data?.message || '更新失败')
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
    first_name: profileData.value?.first_name || '',
    last_name: profileData.value?.last_name || '',
    email: userStore.userInfo?.email || '',
    phone: profileData.value?.phone || '',
    gender: profileData.value?.gender || undefined,
    birthday: profileData.value?.birthday || '',
    address: profileData.value?.address || '',
    city: profileData.value?.city || '',
    province: profileData.value?.province || '',
    postal_code: profileData.value?.postal_code || '',
    department: profileData.value?.department || '',
    major: profileData.value?.major || '',
    degree: profileData.value?.degree || ''
  })
}

const getAvatarText = () => {
  if (profileData.value?.first_name && profileData.value?.last_name) {
    return (profileData.value.first_name + profileData.value.last_name).charAt(0).toUpperCase()
  }
  return (userStore.userInfo?.username || 'U').charAt(0).toUpperCase()
}

const getGenderLabel = (gender?: string) => {
  const labelMap: Record<string, string> = {
    male: '男',
    female: '女',
    other: '其他'
  }
  return labelMap[gender || ''] || '未设置'
}

const formatAddress = (profile?: any) => {
  if (!profile) return '未设置'

  const parts = [
    profile.address,
    profile.city,
    profile.province,
    profile.postal_code
  ].filter(Boolean)

  return parts.length > 0 ? parts.join(', ') : '未设置'
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

const handleExportProfile = async (format: string) => {
  try {
    const response = await authApi.exportProfile(format)

    if (response.success) {
      if (format === 'json') {
        // 创建下载链接
        const blob = new Blob([JSON.stringify(response.data, null, 2)], {
          type: 'application/json'
        })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `个人资料_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)

        ElMessage.success('个人资料导出成功')
      }
    }
  } catch (error: any) {
    console.error('Export profile error:', error)
    ElMessage.error(error.response?.data?.message || '导出失败')
  }
}

const loadHistoryData = async () => {
  try {
    const response = await authApi.getProfileHistory()
    if (response.success) {
      historyList.value = response.data
    }
  } catch (error) {
    console.error('Load history error:', error)
  }
}

const getFieldName = (field: string) => {
  const nameMap: Record<string, string> = {
    first_name: '姓',
    last_name: '名',
    email: '邮箱',
    phone: '手机号',
    gender: '性别',
    birthday: '生日',
    address: '地址',
    city: '城市',
    province: '省份',
    postal_code: '邮编',
    department: '部门',
    major: '专业',
    degree: '学位',
    password: '密码',
    avatar_url: '头像'
  }
  return nameMap[field] || field
}

// 监听历史对话框打开
watch(showHistoryDialog, (show: boolean) => {
  if (show) {
    loadHistoryData()
  }
})

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
.security-card,
.data-card {
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

.avatar-upload-content {
  text-align: center;

  .avatar-preview {
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
  }

  .avatar-upload-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
  }
}

.data-list {
  .data-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);

    &:last-child {
      border-bottom: none;
    }

    .data-info {
      .data-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin-bottom: 4px;
      }

      .data-desc {
        font-size: 14px;
        color: var(--el-text-color-regular);
      }
    }

    .data-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}

.history-content {
  max-height: 500px;
  overflow-y: auto;

  .history-item {
    margin-bottom: 12px;

    .history-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;

      .history-time {
        font-size: 14px;
        color: var(--el-text-color-primary);
        font-weight: 600;
      }

      .history-ip {
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }

    .history-changes {
      .change-tag {
        margin-right: 8px;
        margin-bottom: 4px;
      }
    }
  }
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