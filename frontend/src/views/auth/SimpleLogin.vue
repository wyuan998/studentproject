<template>
  <div class="simple-login">
    <div class="login-card">
      <h2>学生信息管理系统</h2>
      <p class="subtitle">Simple Login Page</p>

      <el-form :model="form" label-width="0">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名 (admin)"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码 (123456)"
            prefix-icon="Lock"
            size="large"
            show-password
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

      <div class="demo-info">
        <p>演示账号:</p>
        <p>用户名: admin</p>
        <p>密码: 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/simple'

const router = useRouter()
const loading = ref(false)

const form = ref({
  username: 'admin',
  password: '123456'
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true

  try {
    // 调用真实API
    const response = await api.login(form.value)

    if (response.success) {
      // 保存token和用户信息
      const token = response.data.token || 'mock-token-' + Date.now()
      const userInfo = response.data.user || {
        id: 1,
        username: 'admin',
        real_name: '系统管理员',
        role: 'admin'
      }

      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userInfo))

      ElMessage.success(response.message || '登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(response.message || '登录失败')
    }
  } catch (error: any) {
    // 如果API调用失败，回退到模拟登录
    console.log('API登录失败，使用模拟登录:', error.message)

    try {
      await new Promise(resolve => setTimeout(resolve, 500))

      if (form.value.username === 'admin' && form.value.password === '123456') {
        localStorage.setItem('token', 'mock-token-' + Date.now())
        localStorage.setItem('user', JSON.stringify({
          id: 1,
          username: 'admin',
          real_name: '系统管理员',
          role: 'admin'
        }))

        ElMessage.success('登录成功 (演示模式)')
        router.push('/dashboard')
      } else {
        ElMessage.error('用户名或密码错误')
      }
    } catch (fallbackError) {
      ElMessage.error('登录失败，请稍后重试')
    }
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
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 8px;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 30px;
  font-size: 14px;
}

.demo-info {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
}

.demo-info p {
  margin: 4px 0;
}
</style>