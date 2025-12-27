<template>
  <div class="simple-profile-container">
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
          <el-avatar :size="120" src="">
            {{ userInfo?.username?.charAt(0).toUpperCase() || 'U' }}
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
              {{ userInfo?.username }}
            </el-descriptions-item>
            <el-descriptions-item label="姓名">
              {{ profileData?.first_name }} {{ profileData?.last_name }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ profileData?.email }}
            </el-descriptions-item>
            <el-descriptions-item label="手机号">
              {{ profileData?.phone || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="性别">
              {{ profileData?.gender || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="生日">
              {{ profileData?.birthday || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="部门">
              {{ profileData?.department || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="专业">
              {{ profileData?.major || '未设置' }}
            </el-descriptions-item>
            <el-descriptions-item label="地址" :span="2">
              {{ profileData?.address || '未设置' }}
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

    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="600px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editForm.address" placeholder="请输入地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateProfile">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 头像上传对话框 -->
    <el-dialog v-model="showAvatarDialog" title="更换头像" width="400px">
      <div class="avatar-upload-content">
        <div class="avatar-preview">
          <el-avatar :size="150" src="" />
        </div>
        <div class="avatar-upload-actions">
          <el-button>选择图片</el-button>
          <el-button type="primary">确认上传</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showChangePassword" title="修改密码" width="450px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showChangePassword = false">取消</el-button>
          <el-button type="primary">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const showEditDialog = ref(false)
const showChangePassword = ref(false)
const showAvatarDialog = ref(false)

const userInfo = ref<any>({
  username: 'admin',
  real_name: '系统管理员'
})

const profileData = ref<any>({
  first_name: '系统',
  last_name: '管理员',
  email: 'admin@example.com',
  phone: '13800138000',
  gender: '男',
  birthday: '2000-01-01',
  address: '北京市海淀区中关村大街1号',
  city: '北京市',
  province: '北京',
  postal_code: '100000',
  department: '计算机学院',
  major: '计算机科学与技术',
  degree: '本科'
})

const editForm = reactive({
  name: '系统管理员',
  email: 'admin@example.com',
  phone: '13800138000',
  address: '北京市海淀区中关村大街1号'
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 方法
const handleAvatarUpload = () => {
  showAvatarDialog.value = true
}

const handleUpdateProfile = () => {
  ElMessage.success('个人信息更新成功')
  showEditDialog.value = false
}

onMounted(() => {
  // 从localStorage获取用户信息
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      userInfo.value = JSON.parse(userStr)
    } catch (error) {
      console.error('解析用户信息失败:', error)
    }
  }
})
</script>

<style lang="scss" scoped>
.simple-profile-container {
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

// 响应式设计
@media (max-width: 768px) {
  .simple-profile-container {
    padding: 12px;
  }

  .profile-content {
    flex-direction: column;
    gap: 20px;
  }
}
</style>