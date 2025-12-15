<template>
  <div class="simple-app">
    <!-- 如果是登录页面，只显示路由视图 -->
    <template v-if="$route.path === '/login'">
      <router-view />
    </template>

    <!-- 否则显示完整的主界面 -->
    <template v-else>
      <div class="dashboard">
        <!-- 顶部导航栏 -->
        <div class="header">
          <div class="header-left">
            <h1>学生信息管理系统</h1>
          </div>
          <div class="header-right">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRouteMeta?.title">
                {{ currentRouteMeta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
            <div class="user-info">
              <el-dropdown @command="handleUserCommand">
                <span class="user-name">
                  <el-icon><User /></el-icon>
                  {{ userInfo?.real_name || '用户' }}
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                    <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>

        <div class="main-layout">
          <!-- 侧边栏菜单 -->
          <div class="sidebar">
            <el-menu
              :default-active="$route.path"
              class="sidebar-menu"
              @select="handleMenuSelect"
            >
              <el-menu-item index="/dashboard">
                <el-icon><Monitor /></el-icon>
                <span>仪表板</span>
              </el-menu-item>

              <el-menu-item index="/students">
                <el-icon><User /></el-icon>
                <span>学生管理</span>
              </el-menu-item>

              <el-menu-item index="/teachers">
                <el-icon><Avatar /></el-icon>
                <span>教师管理</span>
              </el-menu-item>

              <el-menu-item index="/courses">
                <el-icon><Reading /></el-icon>
                <span>课程管理</span>
              </el-menu-item>

              <el-menu-item index="/grades">
                <el-icon><DocumentChecked /></el-icon>
                <span>成绩管理</span>
              </el-menu-item>
            </el-menu>
          </div>

          <!-- 主内容区域 -->
          <div class="content-area">
            <!-- 个人信息页面 -->
            <div v-if="$route.path === '/profile'" class="profile-page">
              <!-- 个人资料卡片 -->
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
                    <el-avatar :size="120" :src="profileData.avatar_url">
                      {{ getAvatarText() }}
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
                        {{ profileData.real_name }}
                      </el-descriptions-item>
                      <el-descriptions-item label="邮箱">
                        {{ profileData.email }}
                      </el-descriptions-item>
                      <el-descriptions-item label="手机号">
                        {{ profileData.phone || '未设置' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="性别">
                        {{ getGenderLabel(profileData.gender) }}
                      </el-descriptions-item>
                      <el-descriptions-item label="生日">
                        {{ profileData.birthday || '未设置' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="部门">
                        {{ profileData.department || '未设置' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="专业">
                        {{ profileData.major || '未设置' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="学位">
                        {{ profileData.degree || '未设置' }}
                      </el-descriptions-item>
                      <el-descriptions-item label="角色">
                        <el-tag type="danger">管理员</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="地址" :span="2">
                        {{ formatAddress() }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </div>
              </el-card>

              <!-- 安全设置卡片 -->
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
                    <el-button text type="primary" @click="showPasswordDialog = true">
                      修改密码
                    </el-button>
                  </div>
                </div>
              </el-card>

              <!-- 数据管理卡片 -->
              <el-card class="data-card">
                <template #header>
                  <span>数据管理</span>
                </template>

                <div class="data-list">
                  <div class="data-item">
                    <div class="data-info">
                      <div class="data-title">导出个人信息</div>
                      <div class="data-desc">导出您的个人资料数据</div>
                    </div>
                    <el-button text type="primary" @click="handleExportProfile">
                      导出数据
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>
            <!-- 系统设置页面 -->
            <div v-else-if="$route.path === '/system-settings'" class="system-settings-page">
              <el-card>
                <template #header>
                  <h2>系统设置</h2>
                </template>

                <el-tabs v-model="activeSettingsTab" type="card">
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
                      <el-form-item label="启用TLS">
                        <el-switch v-model="emailSettings.enableTLS" />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="saveEmailSettings">保存设置</el-button>
                        <el-button @click="testEmailSettings">测试邮件</el-button>
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
            <!-- 其他页面 -->
            <router-view v-else />
          </div>
        </div>
      </div>
    </template>

    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="600px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="editForm.gender" placeholder="请选择性别">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
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
          <el-select v-model="editForm.degree" placeholder="请选择学位">
            <el-option label="本科" value="本科" />
            <el-option label="硕士" value="硕士" />
            <el-option label="博士" value="博士" />
          </el-select>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editForm.address" placeholder="请输入详细地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleUpdateProfile">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="450px"
    >
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showPasswordDialog = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="showAvatarDialog"
      title="更换头像"
      width="400px"
    >
      <div class="avatar-upload-content">
        <div class="avatar-preview">
          <el-avatar :size="150" :src="avatarPreview" />
        </div>
        <div class="avatar-upload-actions">
          <input
            ref="avatarInput"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleFileChange"
          />
          <el-button @click="triggerFileInput">选择图片</el-button>
          <el-button type="primary" @click="handleUploadAvatar">确认上传</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userInfo = ref<any>(null)

// 个人信息相关状态
const showEditDialog = ref(false)
const showPasswordDialog = ref(false)
const showAvatarDialog = ref(false)
const avatarInput = ref<HTMLInputElement>()
const avatarPreview = ref('')
const avatarFile = ref<File | null>(null)

const profileData = ref({
  real_name: '系统管理员',
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
  degree: '本科',
  avatar_url: ''
})

const editForm = ref({
  real_name: '',
  email: '',
  phone: '',
  gender: '',
  birthday: '',
  address: '',
  city: '',
  province: '',
  postal_code: '',
  department: '',
  major: '',
  degree: ''
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 系统设置相关状态
const activeSettingsTab = ref('basic')

const basicSettings = ref({
  systemName: '学生信息管理系统',
  version: '1.0.0',
  description: '基于Vue3 + Flask的现代化学生信息管理系统',
  maintenanceMode: false
})

const securitySettings = ref({
  minPasswordLength: 8,
  loginLockout: true,
  maxLoginAttempts: 5,
  sessionTimeout: 120
})

const emailSettings = ref({
  smtpHost: '',
  smtpPort: 587,
  fromEmail: '',
  password: '',
  enableTLS: true
})

const notificationSettings = ref({
  emailNotification: true,
  systemNotification: true,
  notificationEmail: 'admin@example.com',
  notificationLevel: 'important'
})

// 当前路由的元信息
const currentRouteMeta = computed(() => route.meta)

// 成绩数据
const gradesData = ref([
  {
    id: 1,
    student_name: '张三',
    student_no: 'S2021001',
    course_name: '计算机科学导论',
    exam_type: '期中考试',
    score: 85,
    max_score: 100,
    is_published: true
  },
  {
    id: 2,
    student_name: '张三',
    student_no: 'S2021001',
    course_name: '计算机科学导论',
    exam_type: '期末考试',
    score: 88,
    max_score: 100,
    is_published: true
  },
  {
    id: 3,
    student_name: '李四',
    student_no: 'S2021002',
    course_name: '计算机科学导论',
    exam_type: '期中考试',
    score: 92,
    max_score: 100,
    is_published: true
  },
  {
    id: 4,
    student_name: '李四',
    student_no: 'S2021002',
    course_name: '软件工程',
    exam_type: '作业',
    score: 95,
    max_score: 100,
    is_published: true
  },
  {
    id: 5,
    student_name: '王五',
    student_no: 'S2021003',
    course_name: '软件工程',
    exam_type: '测验',
    score: 76,
    max_score: 100,
    is_published: false
  },
  {
    id: 6,
    student_name: '王五',
    student_no: 'S2021003',
    course_name: '数据结构与算法',
    exam_type: '项目',
    score: 82,
    max_score: 100,
    is_published: true
  }
])

// 响应式数据
const gradeSearchQuery = ref('')
const selectedGrades = ref([])

// 计算属性
const showGradesList = computed(() => route.path === '/grades/list')

const filteredGrades = computed(() => {
  if (!gradeSearchQuery.value) return gradesData.value
  const query = gradeSearchQuery.value.toLowerCase()
  return gradesData.value.filter(grade =>
    grade.student_name.toLowerCase().includes(query) ||
    grade.student_no.toLowerCase().includes(query) ||
    grade.course_name.toLowerCase().includes(query) ||
    grade.exam_type.toLowerCase().includes(query)
  )
})

const publishedCount = computed(() => gradesData.value.filter(g => g.is_published).length)
const unpublishedCount = computed(() => gradesData.value.filter(g => !g.is_published).length)
const averageScore = computed(() => {
  const total = gradesData.value.reduce((sum, g) => sum + g.score, 0)
  return (total / gradesData.value.length).toFixed(1)
})

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  console.log('菜单点击:', index)
  console.log('当前路径:', route.path)

  
  if (index !== route.path) {
    console.log('跳转到:', index)
    router.push(index)
  } else {
    console.log('路径相同，不跳转')
  }
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/system-settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        logout()
      } catch {
        // 用户取消
      }
      break
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push('/login')
}

const goToDashboard = () => {
  router.push('/dashboard')
}

// 成绩管理相关方法
const handleGradeSearch = () => {
  console.log('搜索成绩:', gradeSearchQuery.value)
}

const handleAddGrade = () => {
  ElMessage.info('录入成绩功能开发中')
}

const handleImportGrades = () => {
  ElMessage.info('批量导入功能开发中')
}

const handleExportGrades = () => {
  ElMessage.info('导出数据功能开发中')
}

const handleBatchDelete = () => {
  ElMessage.info('批量删除功能开发中')
}

const handleGradeSelectionChange = (selection) => {
  selectedGrades.value = selection
}

const handleViewGrade = (row) => {
  ElMessage.info('查看成绩详情功能开发中')
}

const handleEditGrade = (row) => {
  ElMessage.info('编辑成绩功能开发中')
}

const handlePublishGrade = (row) => {
  row.is_published = true
  ElMessage.success('成绩已发布')
}

const handleDeleteGrade = (row) => {
  ElMessage.info('删除成绩功能开发中')
}

// 工具函数
const getExamTypeTag = (type) => {
  const typeMap = {
    '期中考试': 'warning',
    '期末考试': 'danger',
    '作业': 'primary',
    '测验': 'info',
    '项目': 'success'
  }
  return typeMap[type] || 'info'
}

const getExamTypeText = (type) => {
  return type
}

const getScoreColor = (score, maxScore) => {
  const percentage = (score / maxScore) * 100
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

const getPercentage = (score, maxScore) => {
  return ((score / maxScore) * 100).toFixed(1)
}

// 个人信息相关方法
const getAvatarText = () => {
  return (userInfo.value?.username || 'U').charAt(0).toUpperCase()
}

const getGenderLabel = (gender: string) => {
  return gender || '未设置'
}

const formatAddress = () => {
  const addr = profileData.value.address
  const city = profileData.value.city
  const province = profileData.value.province

  const parts = [addr, city, province].filter(Boolean)
  return parts.length > 0 ? parts.join(', ') : '未设置'
}

const handleUpdateProfile = () => {
  // 模拟更新
  Object.assign(profileData.value, editForm.value)
  showEditDialog.value = false
  ElMessage.success('个人信息更新成功')
}

const handleChangePassword = () => {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    ElMessage.warning('请填写完整的密码信息')
    return
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  if (passwordForm.value.new_password.length < 8) {
    ElMessage.error('新密码长度不能少于8位')
    return
  }

  // 模拟修改密码
  showPasswordDialog.value = false
  ElMessage.success('密码修改成功')

  // 重置表单
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
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

const handleUploadAvatar = () => {
  if (!avatarFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }

  // 模拟上传
  profileData.value.avatar_url = avatarPreview.value
  showAvatarDialog.value = false
  ElMessage.success('头像上传成功')
}

const handleExportProfile = () => {
  const exportData = {
    个人信息: {
      姓名: profileData.value.real_name,
      用户名: userInfo.value?.username,
      邮箱: profileData.value.email,
      手机: profileData.value.phone,
      性别: profileData.value.gender,
      生日: profileData.value.birthday
    },
    教育信息: {
      部门: profileData.value.department,
      专业: profileData.value.major,
      学位: profileData.value.degree
    },
    地址信息: {
      地址: profileData.value.address,
      城市: profileData.value.city,
      省份: profileData.value.province,
      邮编: profileData.value.postal_code
    }
  }

  // 创建下载链接
  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
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

// 系统设置相关方法
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

const saveNotificationSettings = () => {
  ElMessage.success('通知设置保存成功')
}

// 监听编辑对话框打开
const watchEditDialog = (show: boolean) => {
  if (show) {
    // 加载当前数据到编辑表单
    Object.assign(editForm.value, profileData.value)
  }
}

watch(showEditDialog, watchEditDialog)

onMounted(() => {
  // 获取用户信息
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

<style scoped>
.simple-app {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left h1 {
  color: #409eff;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-name:hover {
  background-color: #f5f7fa;
}

.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.sidebar-menu {
  border: none;
  height: 100%;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
  padding: 0 20px !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #f5f7fa;
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f5f5f5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }

  .header {
    padding: 0 16px;
  }

  .header-left h1 {
    font-size: 18px;
  }

  .content-area {
    padding: 16px;
  }
}

@media (max-width: 640px) {
  .header {
    padding: 0 12px;
  }

  .header-right {
    gap: 12px;
  }

  .sidebar {
    width: 180px;
  }

  .content-area {
    padding: 12px;
  }
}

/* 个人信息页面样式 */
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card,
.security-card,
.data-card {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-content {
    flex-direction: column;
    gap: 20px;
  }
}

/* 系统设置页面样式 */
.system-settings-page {
  .el-form {
    max-width: 600px;
  }
}
</style>

<style scoped>
/* 成绩管理样式 */
.grade-management {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
  padding: 20px 0;
  border-bottom: 1px solid #e4e7ed;
}

.header-content h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.table-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-cards {
  margin-top: 20px;
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.published {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.unpublished {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-icon.average {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #666;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>