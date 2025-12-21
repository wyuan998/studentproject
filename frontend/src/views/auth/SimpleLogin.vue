<template>
  <div class="simple-login">
    <div class="login-card">
      <div class="logo-section">
        <div class="logo">
          <el-icon size="48"><School /></el-icon>
        </div>
        <h2>学生信息管理系统</h2>
        <p class="subtitle">Student Information Management System</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="0" @submit.prevent>
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            @click="handleLogin"
            :loading="loading"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <div class="register-link">
          还没有账号？
          <router-link to="/register" class="link">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { School } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    const success = await userStore.login({
      username: form.username.trim(),
      password: form.password
    })

    if (success) {
      ElMessage.success('登录成功')
    }
  } catch (error) {
    console.error('登录错误:', error)
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.simple-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.simple-login::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(-20px, -20px) rotate(10deg); }
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 420px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  color: white;
  margin-bottom: 20px;
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

h2 {
  text-align: center;
  margin-bottom: 8px;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 40px;
  font-size: 14px;
  font-weight: 400;
}

.login-footer {
  margin-top: 30px;
  text-align: center;
}

.register-link {
  color: #606266;
  font-size: 14px;
}

.register-link .link {
  color: #409eff;
  text-decoration: none;
  margin-left: 5px;
  font-weight: 500;
  transition: color 0.3s;
}

.register-link .link:hover {
  color: #337ecc;
  text-decoration: underline;
}

/* 表单样式优化 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

:deep(.el-button--primary) {
  border-radius: 8px;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.3s;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    padding: 30px 20px;
    margin: 20px;
  }

  h2 {
    font-size: 24px;
  }

  .logo {
    width: 60px;
    height: 60px;
    margin-bottom: 15px;
  }

  .logo .el-icon {
    font-size: 32px;
  }
}
</style>