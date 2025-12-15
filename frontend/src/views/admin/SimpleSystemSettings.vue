<template>
  <div class="simple-system-settings">
    <el-card>
      <template #header>
        <h2>系统设置</h2>
      </template>

      <el-tabs v-model="activeTab" type="card">
        <!-- 基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <el-form :model="basicSettings" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" />
            </el-form-item>
            <el-form-item label="系统版本">
              <el-input v-model="basicSettings.version" disabled />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input type="textarea" v-model="basicSettings.description" :rows="3" />
            </el-form-item>
            <el-form-item label="维护模式">
              <el-switch v-model="basicSettings.maintenanceMode" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <el-form :model="securitySettings" label-width="120px">
            <el-form-item label="密码最小长度">
              <el-input-number v-model="securitySettings.minPasswordLength" :min="6" :max="20" />
            </el-form-item>
            <el-form-item label="登录失败锁定">
              <el-switch v-model="securitySettings.loginLockout" />
            </el-form-item>
            <el-form-item label="最大登录尝试">
              <el-input-number v-model="securitySettings.maxLoginAttempts" :min="3" :max="10" />
            </el-form-item>
            <el-form-item label="会话超时(分钟)">
              <el-input-number v-model="securitySettings.sessionTimeout" :min="30" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 邮件设置 -->
        <el-tab-pane label="邮件设置" name="email">
          <el-form :model="emailSettings" label-width="120px">
            <el-form-item label="SMTP服务器">
              <el-input v-model="emailSettings.smtpHost" placeholder="smtp.example.com" />
            </el-form-item>
            <el-form-item label="SMTP端口">
              <el-input-number v-model="emailSettings.smtpPort" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item label="发送邮箱">
              <el-input v-model="emailSettings.fromEmail" placeholder="noreply@example.com" />
            </el-form-item>
            <el-form-item label="邮箱密码">
              <el-input v-model="emailSettings.password" type="password" show-password />
            </el-form-item>
            <el-form-item label="启用TLS">
              <el-switch v-model="emailSettings.enableTLS" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveEmailSettings">保存设置</el-button>
              <el-button @click="testEmailSettings">测试邮件</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 存储设置 -->
        <el-tab-pane label="存储设置" name="storage">
          <el-form :model="storageSettings" label-width="120px">
            <el-form-item label="上传路径">
              <el-input v-model="storageSettings.uploadPath" placeholder="/uploads" />
            </el-form-item>
            <el-form-item label="最大文件大小(MB)">
              <el-input-number v-model="storageSettings.maxFileSize" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="允许的文件类型">
              <el-input v-model="storageSettings.allowedTypes" placeholder="jpg,png,pdf,doc" />
            </el-form-item>
            <el-form-item label="自动压缩图片">
              <el-switch v-model="storageSettings.autoCompressImages" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveStorageSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 备份设置 -->
        <el-tab-pane label="备份设置" name="backup">
          <el-form :model="backupSettings" label-width="120px">
            <el-form-item label="自动备份">
              <el-switch v-model="backupSettings.autoBackup" />
            </el-form-item>
            <el-form-item label="备份频率">
              <el-select v-model="backupSettings.frequency">
                <el-option label="每日" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
            </el-form-item>
            <el-form-item label="保留备份数">
              <el-input-number v-model="backupSettings.retentionCount" :min="1" :max="30" />
            </el-form-item>
            <el-form-item label="备份路径">
              <el-input v-model="backupSettings.backupPath" placeholder="/backups" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBackupSettings">保存设置</el-button>
              <el-button @click="createBackup">立即备份</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notification">
          <el-form :model="notificationSettings" label-width="120px">
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationSettings.emailNotification" />
            </el-form-item>
            <el-form-item label="系统通知">
              <el-switch v-model="notificationSettings.systemNotification" />
            </el-form-item>
            <el-form-item label="通知邮箱">
              <el-input v-model="notificationSettings.notificationEmail" placeholder="admin@example.com" />
            </el-form-item>
            <el-form-item label="通知级别">
              <el-select v-model="notificationSettings.notificationLevel">
                <el-option label="全部" value="all" />
                <el-option label="重要" value="important" />
                <el-option label="紧急" value="urgent" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

// 基本设置
const basicSettings = ref({
  systemName: '学生信息管理系统',
  version: '1.0.0',
  description: '基于Vue3 + Flask的现代化学生信息管理系统',
  maintenanceMode: false
})

// 安全设置
const securitySettings = ref({
  minPasswordLength: 8,
  loginLockout: true,
  maxLoginAttempts: 5,
  sessionTimeout: 120
})

// 邮件设置
const emailSettings = ref({
  smtpHost: '',
  smtpPort: 587,
  fromEmail: '',
  password: '',
  enableTLS: true
})

// 存储设置
const storageSettings = ref({
  uploadPath: '/uploads',
  maxFileSize: 10,
  allowedTypes: 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx',
  autoCompressImages: true
})

// 备份设置
const backupSettings = ref({
  autoBackup: true,
  frequency: 'daily',
  retentionCount: 7,
  backupPath: '/backups'
})

// 通知设置
const notificationSettings = ref({
  emailNotification: true,
  systemNotification: true,
  notificationEmail: 'admin@example.com',
  notificationLevel: 'important'
})

// 保存设置的方法
const saveBasicSettings = () => {
  ElMessage.success('基本设置保存成功')
}

const saveSecuritySettings = () => {
  ElMessage.success('安全设置保存成功')
}

const saveEmailSettings = () => {
  ElMessage.success('邮件设置保存成功')
}

const testEmailSettings = () => {
  ElMessage.info('测试邮件已发送')
}

const saveStorageSettings = () => {
  ElMessage.success('存储设置保存成功')
}

const saveBackupSettings = () => {
  ElMessage.success('备份设置保存成功')
}

const createBackup = () => {
  ElMessage.success('备份创建成功')
}

const saveNotificationSettings = () => {
  ElMessage.success('通知设置保存成功')
}
</script>

<style lang="scss" scoped>
.simple-system-settings {
  padding: 20px;

  .el-form {
    max-width: 600px;
  }
}
</style>