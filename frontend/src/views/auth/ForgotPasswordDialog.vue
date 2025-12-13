<template>
  <el-dialog
    v-model="visible"
    title="找回密码"
    width="450px"
    :modal="true"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
      class="forgot-password-form"
    >
      <el-form-item label="邮箱" prop="email">
        <el-input
          v-model="form.email"
          placeholder="请输入注册邮箱"
          prefix-icon="Message"
          clearable
        />
      </el-form-item>

      <el-form-item label="验证码" prop="captcha">
        <div class="captcha-container">
          <el-input
            v-model="form.captcha"
            placeholder="请输入验证码"
            prefix-icon="Key"
            clearable
            style="flex: 1; margin-right: 12px"
          />
          <div class="captcha-image" @click="refreshCaptcha">
            <img v-if="captchaData?.captcha_image" :src="captchaData.captcha_image" alt="验证码" />
            <el-skeleton v-else :rows="1" animated />
          </div>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          发送重置邮件
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { authApi } from '@/api/auth'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const captchaData = ref<{ captcha_image: string; captcha_id: string } | null>(null)

const form = reactive({
  email: '',
  captcha: ''
})

// 表单验证规则
const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码长度为4位', trigger: 'blur' }
  ]
}

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

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

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    loading.value = true

    const response = await authApi.forgotPassword({
      email: form.email,
      captcha: form.captcha
    })

    if (response.data?.success) {
      ElMessage.success('重置密码邮件已发送，请查收')
      visible.value = false
    } else {
      ElMessage.error(response.data?.message || '发送失败')
    }
  } catch (error: any) {
    console.error('Forgot password error:', error)
    ElMessage.error(error.response?.data?.message || '发送失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleClosed = () => {
  // 重置表单
  if (formRef.value) {
    formRef.value.resetFields()
  }

  // 重置数据
  Object.assign(form, {
    email: '',
    captcha: ''
  })

  loading.value = false
}

// 监听对话框显示
watch(visible, (newValue) => {
  if (newValue && !captchaData.value) {
    getCaptcha()
  }
})
</script>

<style lang="scss" scoped>
.forgot-password-form {
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
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>