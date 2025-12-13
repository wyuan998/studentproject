<template>
  <el-dialog
    v-model="visible"
    title="修改密码"
    width="450px"
    :modal="true"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      class="change-password-form"
    >
      <el-form-item label="当前密码" prop="old_password">
        <el-input
          v-model="form.old_password"
          type="password"
          placeholder="请输入当前密码"
          show-password
          clearable
          @keyup.enter="handleSubmit"
        />
      </el-form-item>

      <el-form-item label="新密码" prop="new_password">
        <el-input
          v-model="form.new_password"
          type="password"
          placeholder="请输入新密码"
          show-password
          clearable
          @keyup.enter="handleSubmit"
        />
        <div class="password-tips">
          <div>密码需满足以下要求：</div>
          <div :class="{ 'tip-active': form.new_password.length >= 6 }">
            至少6个字符
          </div>
          <div :class="{ 'tip-active': /[a-z]/.test(form.new_password) }">
            包含小写字母
          </div>
          <div :class="{ 'tip-active': /[0-9]/.test(form.new_password) }">
            包含数字
          </div>
        </div>
      </el-form-item>

      <el-form-item label="确认密码" prop="confirm_password">
        <el-input
          v-model="form.confirm_password"
          type="password"
          placeholder="请再次输入新密码"
          show-password
          clearable
          @keyup.enter="handleSubmit"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定修改
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const userStore = useUserStore()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const rules = reactive<FormRules>({
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value === form.old_password) {
          callback(new Error('新密码不能与当前密码相同'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 方法
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    loading.value = true

    const success = await userStore.changePassword(form.old_password, form.new_password)

    if (success) {
      visible.value = false
    }
  } catch (error) {
    console.error('Form validation error:', error)
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
    old_password: '',
    new_password: '',
    confirm_password: ''
  })

  loading.value = false
}
</script>

<style lang="scss" scoped>
.change-password-form {
  .password-tips {
    margin-top: 8px;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    line-height: 1.6;

    .tip-active {
      color: var(--el-color-success);
    }
  }

  :deep(.el-form-item__label) {
    color: var(--el-text-color-primary);
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .change-password-form {
    :deep(.el-form-item__label) {
      width: 80px !important;
    }

    .password-tips {
      font-size: 11px;
    }
  }
}
</style>