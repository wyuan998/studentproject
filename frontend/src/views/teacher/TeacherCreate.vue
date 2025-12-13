<template>
  <div class="teacher-create-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="router.go(-1)">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ isEdit ? '编辑教师' : '新增教师' }}</h2>
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
        class="teacher-form"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="工号" prop="teacher_id">
                <el-input
                  v-model="form.teacher_id"
                  placeholder="请输入工号"
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

        <!-- 职业信息 -->
        <div class="form-section">
          <h3 class="section-title">职业信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="院系" prop="department">
                <el-input
                  v-model="form.department"
                  placeholder="请输入院系"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职称" prop="title">
                <el-select
                  v-model="form.title"
                  placeholder="请选择职称"
                  style="width: 100%"
                >
                  <el-option label="教授" value="professor" />
                  <el-option label="副教授" value="associate_professor" />
                  <el-option label="讲师" value="lecturer" />
                  <el-option label="助教" value="assistant" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="入职日期" prop="hire_date">
                <el-date-picker
                  v-model="form.hire_date"
                  type="date"
                  placeholder="选择入职日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="办公地点">
                <el-input
                  v-model="form.office_location"
                  placeholder="请输入办公地点"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="最高学历">
                <el-select
                  v-model="form.education"
                  placeholder="请选择最高学历"
                  style="width: 100%"
                >
                  <el-option label="本科" value="bachelor" />
                  <el-option label="硕士" value="master" />
                  <el-option label="博士" value="doctor" />
                  <el-option label="博士后" value="postdoctor" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="毕业院校">
                <el-input
                  v-model="form.graduated_from"
                  placeholder="请输入毕业院校"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="研究方向">
            <el-input
              v-model="form.research_area"
              placeholder="请输入研究方向"
            />
          </el-form-item>

          <el-form-item label="教师状态">
            <el-radio-group v-model="form.status">
              <el-radio label="active">在职</el-radio>
              <el-radio label="inactive">离职</el-radio>
              <el-radio label="on_leave">休假</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <!-- 紧急联系人信息 -->
        <div class="form-section">
          <h3 class="section-title">紧急联系人信息</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="紧急联系人">
                <el-input
                  v-model="form.emergency_contact"
                  placeholder="请输入紧急联系人"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="紧急联系电话">
                <el-input
                  v-model="form.emergency_phone"
                  placeholder="请输入紧急联系电话"
                />
              </el-form-item>
            </el-col>
          </el-row>
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
import { teacherApi } from '@/api/user'
import type { Teacher, CreateTeacherData, UpdateTeacherData } from '@/types/user'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const formRef = ref<FormInstance>()
const isEdit = computed(() => !!route.params.id)

// 表单数据
const form = reactive({
  teacher_id: '',
  real_name: '',
  gender: '',
  birth_date: '',
  phone: '',
  email: '',
  address: '',
  department: '',
  title: '',
  hire_date: '',
  office_location: '',
  education: '',
  graduated_from: '',
  research_area: '',
  status: 'active',
  emergency_contact: '',
  emergency_phone: '',
  notes: ''
})

// 表单验证规则
const formRules: FormRules = {
  teacher_id: [
    { required: true, message: '请输入工号', trigger: 'blur' },
    { pattern: /^\d{6,10}$/, message: '工号应为6-10位数字', trigger: 'blur' }
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
  department: [
    { required: true, message: '请输入院系', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请选择职称', trigger: 'change' }
  ],
  hire_date: [
    { required: true, message: '请选择入职日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择教师状态', trigger: 'change' }
  ]
}

// 方法
const loadTeacherDetail = async () => {
  const teacherId = Number(route.params.id)
  if (!teacherId) {
    ElMessage.error('无效的教师ID')
    router.go(-1)
    return
  }

  try {
    loading.value = true
    const response = await teacherApi.getTeacher(teacherId)

    if (response.data?.success) {
      const teacher = response.data.data
      Object.assign(form, {
        teacher_id: teacher.teacher_id,
        real_name: teacher.real_name,
        gender: teacher.gender,
        birth_date: teacher.birth_date,
        phone: teacher.phone,
        email: teacher.email,
        address: teacher.address,
        department: teacher.department,
        title: teacher.title,
        hire_date: teacher.hire_date,
        office_location: teacher.office_location,
        education: teacher.education,
        graduated_from: teacher.graduated_from,
        research_area: teacher.research_area,
        status: teacher.status,
        emergency_contact: teacher.emergency_contact,
        emergency_phone: teacher.emergency_phone,
        notes: teacher.notes
      })
    } else {
      ElMessage.error(response.data?.message || '加载教师信息失败')
      router.go(-1)
    }
  } catch (error: any) {
    console.error('Load teacher detail error:', error)
    ElMessage.error(error.response?.data?.message || '加载教师信息失败')
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
      // 编辑教师
      const teacherId = Number(route.params.id)
      const updateData: UpdateTeacherData = {
        real_name: form.real_name,
        gender: form.gender as any,
        birth_date: form.birth_date,
        phone: form.phone,
        email: form.email,
        address: form.address,
        department: form.department,
        title: form.title as any,
        office_location: form.office_location,
        education: form.education as any,
        graduated_from: form.graduated_from,
        research_area: form.research_area,
        status: form.status as any,
        emergency_contact: form.emergency_contact,
        emergency_phone: form.emergency_phone,
        notes: form.notes
      }

      const response = await teacherApi.updateTeacher(teacherId, updateData)

      if (response.data?.success) {
        ElMessage.success('更新成功')
        router.push(`/teachers/detail/${teacherId}`)
      } else {
        ElMessage.error(response.data?.message || '更新失败')
      }
    } else {
      // 创建教师
      const createData: CreateTeacherData = {
        teacher_id: form.teacher_id,
        real_name: form.real_name,
        gender: form.gender as any,
        birth_date: form.birth_date,
        phone: form.phone,
        email: form.email,
        address: form.address,
        department: form.department,
        title: form.title as any,
        hire_date: form.hire_date,
        office_location: form.office_location,
        education: form.education as any,
        graduated_from: form.graduated_from,
        research_area: form.research_area,
        status: form.status as any,
        emergency_contact: form.emergency_contact,
        emergency_phone: form.emergency_phone,
        notes: form.notes
      }

      const response = await teacherApi.createTeacher(createData)

      if (response.data?.success) {
        ElMessage.success('创建成功')
        router.push('/teachers/list')
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
  localStorage.setItem('teacher_draft', draftData)
  ElMessage.success('草稿已保存')
}

const loadDraft = () => {
  const draftData = localStorage.getItem('teacher_draft')
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
    loadTeacherDetail()
  } else {
    // 设置默认入职日期为今天
    form.hire_date = new Date().toISOString().split('T')[0]
    loadDraft()
  }
})
</script>

<style lang="scss" scoped>
.teacher-create-container {
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
  .teacher-form {
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
  .teacher-create-container {
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

  .teacher-form {
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