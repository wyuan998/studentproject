<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <img src="/logo.png" alt="Logo" class="logo" />
        <h1 class="title">学生信息管理系统</h1>
        <p class="subtitle">Student Information Management System</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
            clearable
            :disabled="loading"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
            clearable
            :disabled="loading"
          />
        </el-form-item>

        <el-form-item v-if="showCaptcha" prop="captcha">
          <div class="captcha-container">
            <el-input
              v-model="loginForm.captcha"
              placeholder="验证码"
              size="large"
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

        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
            <el-button text @click="showForgotPassword = true">忘记密码？</el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="register-link">
            还没有账号？
            <el-button text type="primary" @click="$router.push('/register')">
              立即注册
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <div class="login-footer">
      <p>&copy; 2024 学生信息管理系统. All rights reserved.</p>
    </div>

    <!-- 忘记密码对话框 -->
    <ForgotPasswordDialog v-model="showForgotPassword" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { authApi } from '@/api/auth'
import ForgotPasswordDialog from './ForgotPasswordDialog.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式数据
const loginFormRef = ref<FormInstance>()
const loading = ref(false)
const showCaptcha = ref(false)
const showForgotPassword = ref(false)
const captchaData = ref<{ captcha_image: string; captcha_id: string } | null>(null)

const loginForm = reactive({
  username: '',
  password: '',
  captcha: '',
  remember: false
})

// 表单验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度至少为3位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  captcha: showCaptcha.value ? [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码长度为4位', trigger: 'blur' }
  ] : []
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

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()

    loading.value = true

    const success = await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
      remember: loginForm.remember,
      captcha: loginForm.captcha
    })

    if (success) {
      // 如果有重定向地址，跳转到指定页面
      const redirect = route.query.redirect as string
      if (redirect) {
        await router.replace(redirect)
      }
    } else {
      // 登录失败，显示验证码
      showCaptcha.value = true
      if (!captchaData.value) {
        await getCaptcha()
      }
      loginForm.captcha = ''
    }
  } catch (error) {
    console.error('Login error:', error)
    ElMessage.error('登录失败，请稍后重试')
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

  // 获取记住的用户名
  const rememberedUsername = localStorage.getItem('remembered_username')
  if (rememberedUsername) {
    loginForm.username = rememberedUsername
    loginForm.remember = true
  }
})
</script>

<style lang="scss" scoped>
.login-container {
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

.login-card {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  position: relative;
  z-index: 1;

  @media (max-width: 480px) {
    padding: 30px 20px;
  }
}

.login-header {
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
    font-size: 14px;
    color: #7f8c8d;
    margin: 0;
    font-style: italic;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .login-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    .el-button {
      padding: 0;
      font-size: 14px;
    }
  }

  .login-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 8px;
  }

  .register-link {
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

.login-footer {
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

// 暗色主题适配
@media (prefers-color-scheme: dark) {
  .login-container {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  }

  .login-card {
    background: #1a1a1a;
    color: #ffffff;
  }

  .login-header {
    .title {
      color: #ffffff;
    }

    .subtitle {
      color: #b0b0b0;
    }
  }
}
</style>