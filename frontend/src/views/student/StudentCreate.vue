<template>
  <div class="student-create-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ isEdit ? '编辑学生' : '新增学生' }}</h2>
      </div>
      <div class="header-right">
        <el-button @click="handleSaveDraft">保存草稿</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </div>
    </div>

    <!-- 表单内容 -->
    <el-card class="form-card">
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="120px"
        class="student-form"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="学号" prop="student_id">
                <el-input
                  v-model="form.student_id"
                  placeholder="请输入学号"
                  :disabled="isEdit"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="真实姓名" prop="real_name">
                <el-input
                  v-model="form.real_name"
                  placeholder="请输入真实姓名"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="性别" prop="gender">
                <el-radio-group v-model="form.gender">
                  <el-radio label="male">男</el-radio>
                  <el-radio label="female">女</el-radio>
                  <el-radio label="other">其他</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="出生日期" prop="birth_date">
                <el-date-picker
                  v-model="form.birth_date"
                  type="date"
                  placeholder="选择出生日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="手机号" prop="phone">
                <el-input
                  v-model="form.phone"
                  placeholder="请输入手机号"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="邮箱" prop="email">
                <el-input
                  v-model="form.email"
                  placeholder="请输入邮箱"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="家庭住址">
            <el-input
              v-model="form.address"
              placeholder="请输入家庭住址"
              type="textarea"
              :rows="2"
            />
          </el-form-item>
        </div>

        <!-- 学籍信息 -->
        <div class="form-section">
          <h3 class="section-title">学籍信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="入学日期" prop="enrollment_date">
                <el-date-picker
                  v-model="form.enrollment_date"
                  type="date"
                  placeholder="选择入学日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="预计毕业日期">
                <el-date-picker
                  v-model="form.graduation_date"
                  type="date"
                  placeholder="选择预计毕业日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="专业" prop="major">
                <el-input
                  v-model="form.major"
                  placeholder="请输入专业"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="班级" prop="class_name">
                <el-input
                  v-model="form.class_name"
                  placeholder="请输入班级"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="年级" prop="grade">
                <el-select
                  v-model="form.grade"
                  placeholder="请选择年级"
                  style="width: 100%"
                >
                  <el-option label="2024级" value="2024" />
                  <el-option label="2023级" value="2023" />
                  <el-option label="2022级" value="2022" />
                  <el-option label="2021级" value="2021" />
                  <el-option label="2020级" value="2020" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="学生状态">
            <el-radio-group v-model="form.status">
              <el-radio label="active">在读</el-radio>
              <el-radio label="graduated">已毕业</el-radio>
              <el-radio label="suspended">休学</el-radio>
              <el-radio label="withdrawn">退学</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <!-- 联系人信息 -->
        <div class="form-section">
          <h3 class="section-title">联系人信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="监护人姓名">
                <el-input
                  v-model="form.guardian_name"
                  placeholder="请输入监护人姓名"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="监护人手机">
                <el-input
                  v-model="form.guardian_phone"
                  placeholder="请输入监护人手机"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="监护人邮箱">
                <el-input
                  v-model="form.guardian_email"
                  placeholder="请输入监护人邮箱"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="紧急联系人">
                <el-input
                  v-model="form.emergency_contact"
                  placeholder="请输入紧急联系人"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="紧急联系电话">
            <el-input
              v-model="form.emergency_phone"
              placeholder="请输入紧急联系电话"
            />
          </el-form-item>
        </div>

        <!-- 备注 -->
        <div class="form-section">
          <h3 class="section-title">备注信息</h3>
          <el-form-item label="备注">
            <el-input
              v-model="form.notes"
              type="textarea"
              :rows="4"
              placeholder="请输入备注信息"
            />
          </el-form-item>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  ArrowLeft
} from '@element-plus/icons-vue'
import { studentApi } from '@/api/user'
import type { Student, CreateStudentData, UpdateStudentData } from '@/types/user'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const formRef = ref<FormInstance>()
const isEdit = computed(() => !!route.params.id)

// 表单数据
const form = reactive({
  student_id: '',
  real_name: '',
  gender: '',
  birth_date: '',
  phone: '',
  email: '',
  address: '',
  enrollment_date: '',
  graduation_date: '',
  major: '',
  class_name: '',
  grade: '',
  status: 'active',
  guardian_name: '',
  guardian_phone: '',
  guardian_email: '',
  emergency_contact: '',
  emergency_phone: '',
  notes: ''
})

// 表单验证规则
const formRules: FormRules = {
  student_id: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^\d{10,12}$/, message: '学号应为10-12位数字', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度为2-10位', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  enrollment_date: [
    { required: true, message: '请选择入学日期', trigger: 'change' }
  ],
  major: [
    { required: true, message: '请输入专业', trigger: 'blur' }
  ],
  class_name: [
    { required: true, message: '请输入班级', trigger: 'blur' }
  ],
  grade: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择学生状态', trigger: 'change' }
  ]
}

// 方法
const loadStudentDetail = async () => {
  const studentId = Number(route.params.id)
  if (!studentId) {
    ElMessage.error('无效的学生ID')
    router.go(-1)
    return
  }

  try {
    loading.value = true
    const response = await studentApi.getStudent(studentId)

    if (response.data?.success) {
      const student = response.data.data
      Object.assign(form, {
        student_id: student.student_id,
        real_name: student.real_name,
        gender: student.gender,
        birth_date: student.birth_date,
        phone: student.phone,
        email: student.email,
        address: student.address,
        enrollment_date: student.enrollment_date,
        graduation_date: student.graduation_date,
        major: student.major,
        class_name: student.class_name,
        grade: student.grade,
        status: student.status,
        guardian_name: student.guardian_name,
        guardian_phone: student.guardian_phone,
        guardian_email: student.guardian_email,
        emergency_contact: student.emergency_contact,
        emergency_phone: student.emergency_phone,
        notes: student.notes
      })
    } else {
      ElMessage.error(response.data?.message || '加载学生信息失败')
      router.go(-1)
    }
  } catch (error: any) {
    console.error('Load student detail error:', error)
    ElMessage.error(error.response?.data?.message || '加载学生信息失败')
    router.go(-1)
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    loading.value = true

    if (isEdit.value) {
      // 编辑学生
      const studentId = Number(route.params.id)
      const updateData: UpdateStudentData = {
        real_name: form.real_name,
        gender: form.gender as any,
        birth_date: form.birth_date,
        phone: form.phone,
        email: form.email,
        address: form.address,
        graduation_date: form.graduation_date,
        major: form.major,
        class_name: form.class_name,
        grade: form.grade,
        status: form.status as any,
        guardian_name: form.guardian_name,
        guardian_phone: form.guardian_phone,
        guardian_email: form.guardian_email,
        emergency_contact: form.emergency_contact,
        emergency_phone: form.emergency_phone,
        notes: form.notes
      }

      const response = await studentApi.updateStudent(studentId, updateData)

      if (response.data?.success) {
        ElMessage.success('更新成功')
        router.push(`/students/detail/${studentId}`)
      } else {
        ElMessage.error(response.data?.message || '更新失败')
      }
    } else {
      // 创建学生
      const createData: CreateStudentData = {
        student_id: form.student_id,
        real_name: form.real_name,
        gender: form.gender as any,
        birth_date: form.birth_date,
        phone: form.phone,
        email: form.email,
        address: form.address,
        enrollment_date: form.enrollment_date,
        graduation_date: form.graduation_date,
        major: form.major,
        class_name: form.class_name,
        grade: form.grade,
        status: form.status as any,
        guardian_name: form.guardian_name,
        guardian_phone: form.guardian_phone,
        guardian_email: form.guardian_email,
        emergency_contact: form.emergency_contact,
        emergency_phone: form.emergency_phone,
        notes: form.notes
      }

      const response = await studentApi.createStudent(createData)

      if (response.data?.success) {
        ElMessage.success('创建成功')
        router.push('/students/list')
      } else {
        ElMessage.error(response.data?.message || '创建失败')
      }
    }
  } catch (error: any) {
    console.error('Submit error:', error)
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleSaveDraft = () => {
  const draftData = JSON.stringify(form)
  localStorage.setItem('student_draft', draftData)
  ElMessage.success('草稿已保存')
}

const loadDraft = () => {
  const draftData = localStorage.getItem('student_draft')
  if (draftData) {
    try {
      const parsedData = JSON.parse(draftData)
      Object.assign(form, parsedData)
      ElMessage.info('已加载草稿')
    } catch (error) {
      console.error('Load draft error:', error)
    }
  }
}

// 生命周期
onMounted(() => {
  if (isEdit.value) {
    loadStudentDetail()
  } else {
    // 设置默认入学日期为今天
    form.enrollment_date = new Date().toISOString().split('T')[0]
    loadDraft()
  }
})
</script>

<style lang="scss" scoped>
.student-create-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }

  .header-right {
    display: flex;
    gap: 12px;
  }
}

.form-card {
  .student-form {
    .form-section {
      margin-bottom: 40px;
      padding-bottom: 30px;
      border-bottom: 1px solid var(--el-border-color-lighter);

      &:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
      }

      .section-title {
        margin: 0 0 20px 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        position: relative;
        padding-left: 12px;

        &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 4px;
          height: 18px;
          background-color: var(--el-color-primary);
          border-radius: 2px;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .student-create-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .header-right {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .student-form {
    .el-form-item {
      margin-bottom: 18px;
    }

    :deep(.el-form-item__label) {
      width: 100px !important;
      text-align: left;
    }
  }

  .el-col {
    width: 100% !important;
    margin-bottom: 0;
  }
}
</style>