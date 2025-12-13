<template>
  <div class="course-create">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">创建课程</span>
      </template>
    </el-page-header>

    <div class="form-container">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        size="large"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程编号" prop="course_code">
              <el-input v-model="formData.course_code" placeholder="请输入课程编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入课程名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入课程描述"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学分" prop="credits">
              <el-input-number
                v-model="formData.credits"
                :min="1"
                :max="10"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学时" prop="hours">
              <el-input-number
                v-model="formData.hours"
                :min="1"
                :max="200"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最大人数" prop="max_students">
              <el-input-number
                v-model="formData.max_students"
                :min="1"
                :max="500"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="授课教师" prop="teacher_id">
              <el-select v-model="formData.teacher_id" placeholder="选择授课教师" style="width: 100%">
                <el-option
                  v-for="teacher in teachers"
                  :key="teacher.value"
                  :label="teacher.label"
                  :value="teacher.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学期" prop="semester">
              <el-select v-model="formData.semester" placeholder="选择学期" style="width: 100%">
                <el-option label="2024-春" value="2024-春" />
                <el-option label="2024-夏" value="2024-夏" />
                <el-option label="2024-秋" value="2024-秋" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            创建课程
          </el-button>
          <el-button @click="handleBack">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createCourse } from '@/api/course'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

const formData = reactive({
  course_code: '',
  name: '',
  description: '',
  credits: 3,
  hours: 48,
  max_students: 60,
  teacher_id: '',
  semester: '',
  academic_year: '2023-2024'
})

const rules: FormRules = {
  course_code: [
    { required: true, message: '请输入课程编号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入课程描述', trigger: 'blur' }
  ],
  teacher_id: [
    { required: true, message: '请选择授课教师', trigger: 'change' }
  ],
  semester: [
    { required: true, message: '请选择学期', trigger: 'change' }
  ]
}

const teachers = ref([
  { label: '张伟', value: '1' },
  { label: '李明', value: '2' },
  { label: '王芳', value: '3' }
])

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    await createCourse(formData)
    ElMessage.success('课程创建成功')
    router.push('/courses/list')
  } catch (error) {
    if (error !== 'validation failed') {
      ElMessage.error('课程创建失败')
    }
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.back()
}
</script>

<style lang="scss" scoped>
.course-create {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .form-container {
    margin-top: 20px;
    padding: 24px;
    background-color: var(--el-bg-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
}
</style>