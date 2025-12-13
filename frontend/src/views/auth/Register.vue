<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <img src="/logo.png" alt="Logo" class="logo" />
        <h1 class="title">用户注册</h1>
        <p class="subtitle">创建您的账户</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        label-position="top"
        @keyup.enter="handleRegister"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                prefix-icon="User"
                clearable
                :disabled="loading"
                @blur="checkUsername"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="真实姓名" prop="real_name">
              <el-input
                v-model="registerForm.real_name"
                placeholder="请输入真实姓名"
                prefix-icon="Avatar"
                clearable
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱地址"
                prefix-icon="Message"
                clearable
                :disabled="loading"
                @blur="checkEmail"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="registerForm.phone"
                placeholder="请输入手机号"
                prefix-icon="Phone"
                clearable
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                show-password
                clearable
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="registerForm.confirm_password"
                type="password"
                placeholder="请再次输入密码"
                prefix-icon="Lock"
                show-password
                clearable
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学生号" prop="student_id">
              <el-input
                v-model="registerForm.student_id"
                placeholder="请输入学生号"
                prefix-icon="Postcard"
                clearable
                :disabled="loading"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="验证码" prop="captcha">
              <div class="captcha-container">
                <el-input
                  v-model="registerForm.captcha"
                  placeholder="验证码"
                  prefix-icon="Key"
                  clearable
                  :disabled="loading"
                  style="flex: 1; margin-right: 12px"
                />
                <div class="captcha-image" @click="refreshCaptcha">
                  <img v-if="captchaData?.captcha_image" :src="captchaData.captcha_image" alt="验证码" />
                  <el-skeleton v-else :rows="1" animated />
                </div>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-checkbox v-model="registerForm.agreement" :disabled="loading">
            我已阅读并同意
            <el-button text type="primary" @click="showAgreement = true">《用户协议》</el-button>
            和
            <el-button text type="primary" @click="showPrivacy = true">《隐私政策》</el-button>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="register-button"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="login-link">
            已有账号？
            <el-button text type="primary" @click="$router.push('/login')">
              立即登录
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <div class="register-footer">
      <p>&copy; 2024 学生信息管理系统. All rights reserved.</p>
    </div>

    <!-- 用户协议对话框 -->
    <el-dialog v-model="showAgreement" title="用户协议" width="600px" class="agreement-dialog">
      <div class="agreement-content">
        <h3>1. 服务条款</h3>
        <p>欢迎使用学生信息管理系统。通过注册和使用本系统，您同意遵守以下条款和条件。</p>

        <h3>2. 用户责任</h3>
        <p>用户需要提供真实、准确的个人信息，并负责保护账户安全。</p>

        <h3>3. 隐私保护</h3>
        <p>我们承诺保护用户的个人信息，不会未经授权向第三方透露。</p>

        <h3>4. 使用规范</h3>
        <p>用户应合理使用系统资源，不得进行任何违法或不当操作。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showAgreement = false">我已了解</el-button>
      </template>
    </el-dialog>

    <!-- 隐私政策对话框 -->
    <el-dialog v-model="showPrivacy" title="隐私政策" width="600px" class="agreement-dialog">
      <div class="agreement-content">
        <h3>1. 信息收集</h3>
        <p>我们收集您提供的基本信息，包括姓名、学号、联系方式等，用于系统功能实现。</p>

        <h3>2. 信息使用</h3>
        <p>收集的信息仅用于系统管理和教育服务目的，不会用于商业用途。</p>

        <h3>3. 信息保护</h3>
        <p>我们采取技术措施保护您的个人信息安全，防止信息泄露、丢失或滥用。</p>

        <h3>4. 信息共享</h3>
        <p>除法律要求外，未经您的同意，我们不会向第三方共享您的个人信息。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showPrivacy = false">我已了解</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { authApi } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const registerFormRef = ref<FormInstance>()
const loading = ref(false)
const showAgreement = ref(false)
const showPrivacy = ref(false)
const captchaData = ref<{ captcha_image: string; captcha_id: string } | null>(null)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  phone: '',
  real_name: '',
  student_id: '',
  captcha: '',
  agreement: false
})

// 表单验证规则
const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度为2-10位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!/(?=.*[a-z])(?=.*\d)/.test(value)) {
          callback(new Error('密码必须包含字母和数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  student_id: [
    { required: true, message: '请输入学生号', trigger: 'blur' },
    { pattern: /^\d{10,12}$/, message: '学生号应为10-12位数字', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码长度为4位', trigger: 'blur' }
  ],
  agreement: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请阅读并同意用户协议和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 方法
const getCaptcha = async () => {
  try {
    const response = await authApi.getCaptcha()
    if (response.data?.data) {
      captchaData.value = response.data.data
    }
  } catch (error) {
    console.error('Get captcha error:', error)
  }
}

const refreshCaptcha = () => {
  captchaData.value = null
  getCaptcha()
}

const checkUsername = async () => {
  if (!registerForm.username || registerForm.username.length < 3) return

  try {
    const response = await authApi.checkUsername(registerForm.username)
    if (!response.data?.success) {
      ElMessage.warning('用户名已存在')
    }
  } catch (error) {
    console.error('Check username error:', error)
  }
}

const checkEmail = async () => {
  if (!registerForm.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) return

  try {
    const response = await authApi.checkEmail(registerForm.email)
    if (!response.data?.success) {
      ElMessage.warning('邮箱已被注册')
    }
  } catch (error) {
    console.error('Check email error:', error)
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()

    loading.value = true

    const success = await userStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      confirm_password: registerForm.confirm_password,
      phone: registerForm.phone,
      real_name: registerForm.real_name,
      student_id: registerForm.student_id,
      captcha: registerForm.captcha
    })

    if (success) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    }
  } catch (error) {
    console.error('Register error:', error)
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  // 如果已经登录，跳转到首页
  if (userStore.isAuthenticated) {
    router.replace('/dashboard')
    return
  }

  getCaptcha()
})
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('/pattern.svg') repeat;
    opacity: 0.1;
    pointer-events: none;
  }
}

.register-card {
  width: 100%;
  max-width: 800px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  position: relative;
  z-index: 1;

  @media (max-width: 768px) {
    max-width: 500px;
    padding: 30px 20px;
  }
}

.register-header {
  text-align: center;
  margin-bottom: 40px;

  .logo {
    width: 64px;
    height: 64px;
    margin-bottom: 16px;
  }

  .title {
    font-size: 28px;
    font-weight: 700;
    color: #2c3e50;
    margin: 0 0 8px 0;
    line-height: 1.2;
  }

  .subtitle {
    font-size: 16px;
    color: #7f8c8d;
    margin: 0;
  }
}

.register-form {
  .el-form-item {
    margin-bottom: 20px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .register-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 8px;
  }

  .login-link {
    text-align: center;
    color: var(--el-text-color-regular);
    font-size: 14px;

    .el-button {
      padding: 0;
      font-size: 14px;
      font-weight: 600;
    }
  }
}

.captcha-container {
  display: flex;
  align-items: center;
  width: 100%;
}

.captcha-image {
  width: 100px;
  height: 40px;
  cursor: pointer;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--el-fill-color-blank);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.register-footer {
  margin-top: 40px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  position: relative;
  z-index: 1;

  p {
    margin: 0;
  }
}

.agreement-dialog {
  :deep(.el-dialog__body) {
    max-height: 400px;
    overflow-y: auto;
  }
}

.agreement-content {
  h3 {
    color: var(--el-text-color-primary);
    font-size: 16px;
    margin: 20px 0 10px 0;

    &:first-child {
      margin-top: 0;
    }
  }

  p {
    color: var(--el-text-color-regular);
    line-height: 1.6;
    margin: 0 0 15px 0;
  }
}

// 暗色主题适配
@media (prefers-color-scheme: dark) {
  .register-container {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  }

  .register-card {
    background: #1a1a1a;
    color: #ffffff;
  }

  .register-header {
    .title {
      color: #ffffff;
    }

    .subtitle {
      color: #b0b0b0;
    }
  }
}
</style>