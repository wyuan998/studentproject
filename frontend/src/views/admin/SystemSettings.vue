<template>
  <div class="system-settings">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">系统设置</span>
      </template>
    </el-page-header>

    <div class="settings-container">
      <el-row :gutter="20">
        <!-- 左侧菜单 -->
        <el-col :span="6">
          <el-card class="settings-menu">
            <el-menu
              v-model:default-active="activeMenu"
              mode="vertical"
              @select="handleMenuSelect"
            >
              <el-menu-item index="basic">
                <el-icon><Setting /></el-icon>
                <span>基本设置</span>
              </el-menu-item>
              <el-menu-item index="security">
                <el-icon><Lock /></el-icon>
                <span>安全设置</span>
              </el-menu-item>
              <el-menu-item index="email">
                <el-icon><Message /></el-icon>
                <span>邮件设置</span>
              </el-menu-item>
              <el-menu-item index="storage">
                <el-icon><FolderOpened /></el-icon>
                <span>存储设置</span>
              </el-menu-item>
              <el-menu-item index="backup">
                <el-icon><Download /></el-icon>
                <span>备份设置</span>
              </el-menu-item>
              <el-menu-item index="notification">
                <el-icon><Bell /></el-icon>
                <span>通知设置</span>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>

        <!-- 右侧内容 -->
        <el-col :span="18">
          <el-card class="settings-content">
            <!-- 基本设置 -->
            <div v-if="activeMenu === 'basic'" class="settings-section">
              <h3>基本设置</h3>
              <el-form :model="basicForm" label-width="150px" size="default">
                <el-form-item label="系统名称">
                  <el-input v-model="basicForm.systemName" placeholder="学生信息管理系统" />
                </el-form-item>
                <el-form-item label="系统描述">
                  <el-input
                    v-model="basicForm.systemDescription"
                    type="textarea"
                    :rows="3"
                    placeholder="系统功能描述"
                  />
                </el-form-item>
                <el-form-item label="系统版本">
                  <el-input v-model="basicForm.systemVersion" readonly />
                </el-form-item>
                <el-form-item label="维护模式">
                  <el-switch v-model="basicForm.maintenanceMode" />
                  <div class="form-tip">开启后普通用户无法访问系统</div>
                </el-form-item>
                <el-form-item label="维护通知">
                  <el-input
                    v-model="basicForm.maintenanceMessage"
                    type="textarea"
                    :rows="2"
                    placeholder="系统维护期间显示的通知信息"
                  />
                </el-form-item>
                <el-form-item label="时区设置">
                  <el-select v-model="basicForm.timezone" style="width: 100%">
                    <el-option label="UTC+8 北京时间" value="Asia/Shanghai" />
                    <el-option label="UTC+0 格林威治时间" value="UTC" />
                    <el-option label="UTC-5 纽约时间" value="America/New_York" />
                  </el-select>
                </el-form-item>
                <el-form-item label="语言设置">
                  <el-select v-model="basicForm.language" style="width: 100%">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSaveBasic">保存设置</el-button>
                  <el-button @click="handleResetBasic">重置</el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 安全设置 -->
            <div v-if="activeMenu === 'security'" class="settings-section">
              <h3>安全设置</h3>
              <el-form :model="securityForm" label-width="150px" size="default">
                <el-form-item label="密码策略">
                  <el-checkbox-group v-model="securityForm.passwordPolicy">
                    <el-checkbox label="length">最少8位字符</el-checkbox>
                    <el-checkbox label="uppercase">包含大写字母</el-checkbox>
                    <el-checkbox label="lowercase">包含小写字母</el-checkbox>
                    <el-checkbox label="number">包含数字</el-checkbox>
                    <el-checkbox label="special">包含特殊字符</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item label="密码过期天数">
                  <el-input-number v-model="securityForm.passwordExpiry" :min="0" :max="365" />
                  <div class="form-tip">0表示永不过期</div>
                </el-form-item>
                <el-form-item label="登录失败锁定">
                  <el-switch v-model="securityForm.loginLockout" />
                </el-form-item>
                <el-form-item v-if="securityForm.loginLockout" label="锁定阈值">
                  <el-input-number v-model="securityForm.lockoutThreshold" :min="3" :max="10" />
                  <div class="form-tip">连续失败次数达到此值将锁定账户</div>
                </el-form-item>
                <el-form-item v-if="securityForm.loginLockout" label="锁定时间">
                  <el-input-number v-model="securityForm.lockoutDuration" :min="5" :max="1440" />
                  <div class="form-tip">账户锁定时长（分钟）</div>
                </el-form-item>
                <el-form-item label="会话超时">
                  <el-input-number v-model="securityForm.sessionTimeout" :min="30" :max="1440" />
                  <div class="form-tip">用户无操作自动退出时间（分钟）</div>
                </el-form-item>
                <el-form-item label="强制HTTPS">
                  <el-switch v-model="securityForm.forceHttps" />
                </el-form-item>
                <el-form-item label="IP白名单">
                  <el-input
                    v-model="securityForm.ipWhitelist"
                    type="textarea"
                    :rows="3"
                    placeholder="每行一个IP地址或IP段，如：192.168.1.0/24"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSaveSecurity">保存设置</el-button>
                  <el-button @click="handleResetSecurity">重置</el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 邮件设置 -->
            <div v-if="activeMenu === 'email'" class="settings-section">
              <h3>邮件设置</h3>
              <el-form :model="emailForm" label-width="150px" size="default">
                <el-form-item label="SMTP服务器">
                  <el-input v-model="emailForm.smtpHost" placeholder="smtp.example.com" />
                </el-form-item>
                <el-form-item label="SMTP端口">
                  <el-input-number v-model="emailForm.smtpPort" :min="1" :max="65535" />
                </el-form-item>
                <el-form-item label="加密方式">
                  <el-select v-model="emailForm.encryption" style="width: 100%">
                    <el-option label="无" value="none" />
                    <el-option label="SSL" value="ssl" />
                    <el-option label="TLS" value="tls" />
                  </el-select>
                </el-form-item>
                <el-form-item label="发件人邮箱">
                  <el-input v-model="emailForm.fromEmail" placeholder="noreply@example.com" />
                </el-form-item>
                <el-form-item label="发件人名称">
                  <el-input v-model="emailForm.fromName" placeholder="系统通知" />
                </el-form-item>
                <el-form-item label="用户名">
                  <el-input v-model="emailForm.username" placeholder="邮箱地址" />
                </el-form-item>
                <el-form-item label="密码">
                  <el-input v-model="emailForm.password" type="password" placeholder="邮箱密码或授权码" show-password />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSaveEmail">保存设置</el-button>
                  <el-button @click="handleTestEmail" :loading="testEmailLoading">测试邮件</el-button>
                  <el-button @click="handleResetEmail">重置</el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 存储设置 -->
            <div v-if="activeMenu === 'storage'" class="settings-section">
              <h3>存储设置</h3>
              <el-form :model="storageForm" label-width="150px" size="default">
                <el-form-item label="存储方式">
                  <el-select v-model="storageForm.storageType" style="width: 100%">
                    <el-option label="本地存储" value="local" />
                    <el-option label="阿里云OSS" value="aliyun-oss" />
                    <el-option label="腾讯云COS" value="tencent-cos" />
                    <el-option label="AWS S3" value="aws-s3" />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="storageForm.storageType !== 'local'" label="存储桶名称">
                  <el-input v-model="storageForm.bucketName" />
                </el-form-item>
                <el-form-item v-if="storageForm.storageType !== 'local'" label="访问密钥ID">
                  <el-input v-model="storageForm.accessKeyId" />
                </el-form-item>
                <el-form-item v-if="storageForm.storageType !== 'local'" label="访问密钥Secret">
                  <el-input v-model="storageForm.accessKeySecret" type="password" show-password />
                </el-form-item>
                <el-form-item v-if="storageForm.storageType !== 'local'" label="区域">
                  <el-input v-model="storageForm.region" placeholder="如：oss-cn-hangzhou" />
                </el-form-item>
                <el-form-item label="文件上传限制">
                  <el-input-number v-model="storageForm.maxFileSize" :min="1" :max="100" />
                  <div class="form-tip">单个文件最大大小（MB）</div>
                </el-form-item>
                <el-form-item label="允许的文件类型">
                  <el-input
                    v-model="storageForm.allowedTypes"
                    type="textarea"
                    :rows="3"
                    placeholder="如：jpg,jpeg,png,pdf,doc,docx"
                  />
                </el-form-item>
                <el-form-item label="图片压缩">
                  <el-switch v-model="storageForm.imageCompression" />
                </el-form-item>
                <el-form-item v-if="storageForm.imageCompression" label="压缩质量">
                  <el-slider v-model="storageForm.compressionQuality" :min="10" :max="100" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSaveStorage">保存设置</el-button>
                  <el-button @click="handleResetStorage">重置</el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 备份设置 -->
            <div v-if="activeMenu === 'backup'" class="settings-section">
              <h3>备份设置</h3>
              <el-form :model="backupForm" label-width="150px" size="default">
                <el-form-item label="自动备份">
                  <el-switch v-model="backupForm.autoBackup" />
                </el-form-item>
                <el-form-item v-if="backupForm.autoBackup" label="备份频率">
                  <el-select v-model="backupForm.frequency" style="width: 100%">
                    <el-option label="每天" value="daily" />
                    <el-option label="每周" value="weekly" />
                    <el-option label="每月" value="monthly" />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="backupForm.autoBackup" label="备份时间">
                  <el-time-picker
                    v-model="backupForm.backupTime"
                    format="HH:mm"
                    placeholder="选择时间"
                  />
                </el-form-item>
                <el-form-item label="备份保留天数">
                  <el-input-number v-model="backupForm.retentionDays" :min="7" :max="365" />
                  <div class="form-tip">超过此天数的备份将被自动删除</div>
                </el-form-item>
                <el-form-item label="备份内容">
                  <el-checkbox-group v-model="backupForm.backupContent">
                    <el-checkbox label="database">数据库</el-checkbox>
                    <el-checkbox label="uploads">上传文件</el-checkbox>
                    <el-checkbox label="config">配置文件</el-checkbox>
                    <el-checkbox label="logs">日志文件</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item label="备份存储位置">
                  <el-radio-group v-model="backupForm.backupLocation">
                    <el-radio label="local">本地存储</el-radio>
                    <el-radio label="cloud">云存储</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSaveBackup">保存设置</el-button>
                  <el-button @click="handleManualBackup" :loading="manualBackupLoading">立即备份</el-button>
                  <el-button @click="handleResetBackup">重置</el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 通知设置 -->
            <div v-if="activeMenu === 'notification'" class="settings-section">
              <h3>通知设置</h3>
              <el-form :model="notificationForm" label-width="150px" size="default">
                <el-form-item label="系统通知">
                  <el-switch v-model="notificationForm.systemNotification" />
                </el-form-item>
                <el-form-item label="邮件通知">
                  <el-switch v-model="notificationForm.emailNotification" />
                </el-form-item>
                <el-form-item label="短信通知">
                  <el-switch v-model="notificationForm.smsNotification" />
                </el-form-item>
                <el-form-item label="通知事件">
                  <el-checkbox-group v-model="notificationForm.notificationEvents">
                    <el-checkbox label="user_login">用户登录</el-checkbox>
                    <el-checkbox label="user_register">用户注册</el-checkbox>
                    <el-checkbox label="enrollment_success">选课成功</el-checkbox>
                    <el-checkbox label="grade_published">成绩发布</el-checkbox>
                    <el-checkbox label="system_error">系统错误</el-checkbox>
                    <el-checkbox label="security_alert">安全警报</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item label="通知频率">
                  <el-select v-model="notificationForm.frequency" style="width: 100%">
                    <el-option label="实时" value="realtime" />
                    <el-option label="每小时汇总" value="hourly" />
                    <el-option label="每日汇总" value="daily" />
                    <el-option label="每周汇总" value="weekly" />
                  </el-select>
                </el-form-item>
                <el-form-item label="免打扰时间">
                  <el-time-picker
                    v-model="notificationForm.quietHours"
                    is-range
                    range-separator="至"
                    start-placeholder="开始时间"
                    end-placeholder="结束时间"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSaveNotification">保存设置</el-button>
                  <el-button @click="handleResetNotification">重置</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, Lock, Message, FolderOpened, Download, Bell
} from '@element-plus/icons-vue'
import { systemConfigApi } from '@/api/system-config'

const router = useRouter()
const activeMenu = ref('basic')
const testEmailLoading = ref(false)
const manualBackupLoading = ref(false)

const basicForm = reactive({
  systemName: '学生信息管理系统',
  systemDescription: '一个功能完善的学生信息管理平台',
  systemVersion: '1.0.0',
  maintenanceMode: false,
  maintenanceMessage: '系统正在维护中，请稍后访问',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN'
})

const securityForm = reactive({
  passwordPolicy: ['length', 'number'],
  passwordExpiry: 90,
  loginLockout: true,
  lockoutThreshold: 5,
  lockoutDuration: 30,
  sessionTimeout: 120,
  forceHttps: false,
  ipWhitelist: ''
})

const emailForm = reactive({
  smtpHost: '',
  smtpPort: 587,
  encryption: 'tls',
  fromEmail: '',
  fromName: '系统通知',
  username: '',
  password: ''
})

const storageForm = reactive({
  storageType: 'local',
  bucketName: '',
  accessKeyId: '',
  accessKeySecret: '',
  region: '',
  maxFileSize: 10,
  allowedTypes: 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx',
  imageCompression: true,
  compressionQuality: 80
})

const backupForm = reactive({
  autoBackup: true,
  frequency: 'daily',
  backupTime: new Date(2000, 1, 1, 2, 0),
  retentionDays: 30,
  backupContent: ['database', 'uploads'],
  backupLocation: 'local'
})

const notificationForm = reactive({
  systemNotification: true,
  emailNotification: true,
  smsNotification: false,
  notificationEvents: ['system_error', 'security_alert'],
  frequency: 'realtime',
  quietHours: null as [Date, Date] | null
})

const handleMenuSelect = (key: string) => {
  activeMenu.value = key
}

const handleSaveBasic = async () => {
  try {
    const configUpdates = [
      { key: 'system.name', value: basicForm.systemName },
      { key: 'system.description', value: basicForm.systemDescription },
      { key: 'system.maintenance_mode', value: basicForm.maintenanceMode },
      { key: 'system.maintenance_message', value: basicForm.maintenanceMessage },
      { key: 'system.timezone', value: basicForm.timezone },
      { key: 'system.language', value: basicForm.language }
    ]

    await systemConfigApi.batchUpdateConfigs({
      configs: configUpdates,
      category: 'basic'
    })
    ElMessage.success('基本设置保存成功')
  } catch (error: any) {
    console.error('保存基本设置失败:', error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  }
}

const handleResetBasic = () => {
  Object.assign(basicForm, {
    systemName: '学生信息管理系统',
    systemDescription: '一个功能完善的学生信息管理平台',
    systemVersion: '1.0.0',
    maintenanceMode: false,
    maintenanceMessage: '系统正在维护中，请稍后访问',
    timezone: 'Asia/Shanghai',
    language: 'zh-CN'
  })
}

const handleSaveSecurity = async () => {
  try {
    const configUpdates = [
      { key: 'security.password_policy', value: securityForm.passwordPolicy },
      { key: 'security.password_expiry', value: securityForm.passwordExpiry },
      { key: 'security.login_lockout', value: securityForm.loginLockout },
      { key: 'security.lockout_threshold', value: securityForm.lockoutThreshold },
      { key: 'security.lockout_duration', value: securityForm.lockoutDuration },
      { key: 'security.session_timeout', value: securityForm.sessionTimeout },
      { key: 'security.force_https', value: securityForm.forceHttps },
      { key: 'security.ip_whitelist', value: securityForm.ipWhitelist }
    ]

    await systemConfigApi.batchUpdateConfigs({
      configs: configUpdates,
      category: 'security'
    })
    ElMessage.success('安全设置保存成功')
  } catch (error: any) {
    console.error('保存安全设置失败:', error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  }
}

const handleResetSecurity = () => {
  Object.assign(securityForm, {
    passwordPolicy: ['length', 'number'],
    passwordExpiry: 90,
    loginLockout: true,
    lockoutThreshold: 5,
    lockoutDuration: 30,
    sessionTimeout: 120,
    forceHttps: false,
    ipWhitelist: ''
  })
}

const handleSaveEmail = async () => {
  try {
    const configUpdates = [
      { key: 'email.smtp_host', value: emailForm.smtpHost },
      { key: 'email.smtp_port', value: emailForm.smtpPort },
      { key: 'email.encryption', value: emailForm.encryption },
      { key: 'email.from_email', value: emailForm.fromEmail },
      { key: 'email.from_name', value: emailForm.fromName },
      { key: 'email.username', value: emailForm.username },
      { key: 'email.password', value: emailForm.password }
    ]

    await systemConfigApi.batchUpdateConfigs({
      configs: configUpdates,
      category: 'email'
    })
    ElMessage.success('邮件设置保存成功')
  } catch (error: any) {
    console.error('保存邮件设置失败:', error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  }
}

const handleTestEmail = async () => {
  try {
    testEmailLoading.value = true
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('测试邮件发送成功')
  } catch (error) {
    ElMessage.error('测试邮件发送失败')
  } finally {
    testEmailLoading.value = false
  }
}

const handleResetEmail = () => {
  Object.assign(emailForm, {
    smtpHost: '',
    smtpPort: 587,
    encryption: 'tls',
    fromEmail: '',
    fromName: '系统通知',
    username: '',
    password: ''
  })
}

const handleSaveStorage = async () => {
  try {
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('存储设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleResetStorage = () => {
  Object.assign(storageForm, {
    storageType: 'local',
    bucketName: '',
    accessKeyId: '',
    accessKeySecret: '',
    region: '',
    maxFileSize: 10,
    allowedTypes: 'jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx',
    imageCompression: true,
    compressionQuality: 80
  })
}

const handleSaveBackup = async () => {
  try {
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('备份设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleManualBackup = async () => {
  try {
    manualBackupLoading.value = true
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 3000))
    ElMessage.success('手动备份创建成功')
  } catch (error) {
    ElMessage.error('备份创建失败')
  } finally {
    manualBackupLoading.value = false
  }
}

const handleResetBackup = () => {
  Object.assign(backupForm, {
    autoBackup: true,
    frequency: 'daily',
    backupTime: new Date(2000, 1, 1, 2, 0),
    retentionDays: 30,
    backupContent: ['database', 'uploads'],
    backupLocation: 'local'
  })
}

const handleSaveNotification = async () => {
  try {
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('通知设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleResetNotification = () => {
  Object.assign(notificationForm, {
    systemNotification: true,
    emailNotification: true,
    smsNotification: false,
    notificationEvents: ['system_error', 'security_alert'],
    frequency: 'realtime',
    quietHours: null
  })
}

const handleBack = () => {
  router.back()
}

const loadSystemConfigs = async () => {
  try {
    const response = await systemConfigApi.getConfigList({
      per_page: 100 // 获取所有配置
    })

    if (response.success) {
      const configs = response.data.configs
      const configDict = configs.reduce((acc, config) => {
        acc[config.key] = config.value
        return acc
      }, {} as Record<string, any>)

      // 填充基本设置表单
      basicForm.systemName = configDict['system.name'] || '学生信息管理系统'
      basicForm.systemDescription = configDict['system.description'] || '一个功能完善的学生信息管理平台'
      basicForm.systemVersion = '1.0.0' // 版本号通常是硬编码的
      basicForm.maintenanceMode = configDict['system.maintenance_mode'] || false
      basicForm.maintenanceMessage = configDict['system.maintenance_message'] || '系统正在维护中，请稍后访问'
      basicForm.timezone = configDict['system.timezone'] || 'Asia/Shanghai'
      basicForm.language = configDict['system.language'] || 'zh-CN'

      // 填充安全设置表单
      securityForm.passwordPolicy = configDict['security.password_policy'] || ['length', 'number']
      securityForm.passwordExpiry = configDict['security.password_expiry'] || 90
      securityForm.loginLockout = configDict['security.login_lockout'] || true
      securityForm.lockoutThreshold = configDict['security.lockout_threshold'] || 5
      securityForm.lockoutDuration = configDict['security.lockout_duration'] || 30
      securityForm.sessionTimeout = configDict['security.session_timeout'] || 120
      securityForm.forceHttps = configDict['security.force_https'] || false
      securityForm.ipWhitelist = configDict['security.ip_whitelist'] || ''

      // 填充邮件设置表单
      emailForm.smtpHost = configDict['email.smtp_host'] || ''
      emailForm.smtpPort = configDict['email.smtp_port'] || 587
      emailForm.encryption = configDict['email.encryption'] || 'tls'
      emailForm.fromEmail = configDict['email.from_email'] || ''
      emailForm.fromName = configDict['email.from_name'] || '系统通知'
      emailForm.username = configDict['email.username'] || ''
      emailForm.password = configDict['email.password'] || ''
    }
  } catch (error: any) {
    console.error('加载系统配置失败:', error)
    // 不显示错误消息，因为可能是首次访问，配置为空
  }
}

onMounted(() => {
  loadSystemConfigs()
})
</script>

<style lang="scss" scoped>
.system-settings {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .settings-container {
    margin-top: 20px;

    .settings-menu {
      .el-menu {
        border-right: none;
      }
    }

    .settings-content {
      min-height: 600px;

      .settings-section {
        h3 {
          margin-bottom: 24px;
          color: var(--el-text-color-primary);
          font-size: 16px;
          font-weight: 600;
        }

        .form-tip {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          margin-top: 4px;
        }
      }
    }
  }
}
</style>