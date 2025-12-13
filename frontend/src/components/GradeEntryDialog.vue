<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑成绩' : '录入成绩'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      label-position="right"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="学生" prop="student_id">
            <el-select
              v-model="form.student_id"
              placeholder="选择学生"
              filterable
              remote
              :remote-method="searchStudents"
              :loading="studentLoading"
              style="width: 100%"
              :disabled="isEdit"
            >
              <el-option
                v-for="student in studentOptions"
                :key="student.value"
                :label="student.label"
                :value="student.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="课程" prop="course_id">
            <el-select
              v-model="form.course_id"
              placeholder="选择课程"
              style="width: 100%"
              @change="handleCourseChange"
              :disabled="isEdit"
            >
              <el-option
                v-for="course in courseOptions"
                :key="course.value"
                :label="course.label"
                :value="course.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="考试类型" prop="exam_type">
            <el-select v-model="form.exam_type" placeholder="选择类型" style="width: 100%">
              <el-option label="测验" value="quiz" />
              <el-option label="作业" value="assignment" />
              <el-option label="期中考试" value="midterm" />
              <el-option label="期末考试" value="final" />
              <el-option label="项目" value="project" />
              <el-option label="演讲" value="presentation" />
              <el-option label="实验课" value="lab" />
              <el-option label="出勤" value="attendance" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="考试名称" prop="exam_name">
            <el-input v-model="form.exam_name" placeholder="如：期中考试、作业1等" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="分数" prop="score">
            <el-input-number
              v-model="form.score"
              :min="0"
              :max="form.max_score"
              :precision="1"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="满分" prop="max_score">
            <el-input-number
              v-model="form.max_score"
              :min="1"
              :precision="1"
              style="width: 100%"
              @change="handleMaxScoreChange"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="权重" prop="weight">
            <el-input-number
              v-model="form.weight"
              :min="0"
              :max="10"
              :precision="2"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="学期" prop="semester">
            <el-select v-model="form.semester" placeholder="选择学期" style="width: 100%">
              <el-option label="2024-春季" value="2024-春季" />
              <el-option label="2024-夏季" value="2024-夏季" />
              <el-option label="2024-秋季" value="2024-秋季" />
              <el-option label="2025-春季" value="2025-春季" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态">
            <el-switch
              v-model="form.is_published"
              active-text="已发布"
              inactive-text="未发布"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="评语">
        <el-input
          v-model="form.comments"
          type="textarea"
          :rows="3"
          placeholder="输入教师评语..."
        />
      </el-form-item>

      <el-form-item label="改进建议">
        <el-input
          v-model="form.improvement_suggestions"
          type="textarea"
          :rows="2"
          placeholder="输入改进建议..."
        />
      </el-form-item>

      <!-- 成绩预览 -->
      <el-divider content-position="left">成绩预览</el-divider>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="百分比">
          {{ percentage.toFixed(1) }}%
        </el-descriptions-item>
        <el-descriptions-item label="等级">
          <el-tag :type="getGradeTag(percentage)">
            {{ getGradeLevel(percentage) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="绩点">
          {{ getGradePoint(percentage) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
        >
          {{ isEdit ? '更新' : '保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, toRefs } from 'vue'
import { ElMessage } from 'element-plus'
import { gradeApi } from '@/api'

const emit = defineEmits(['success', 'error'])

// 组件属性
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  grade: {
    type: Object,
    default: null
  }
})

// 响应式数据
const visible = ref(props.modelValue)
const submitting = ref(false)
const studentLoading = ref(false)
const formRef = ref(null)

// 表单数据
const form = reactive({
  student_id: '',
  course_id: '',
  exam_type: '',
  exam_name: '',
  score: 0,
  max_score: 100,
  weight: 1.0,
  semester: '2025-春季',
  is_published: false,
  comments: '',
  improvement_suggestions: ''
})

// 选项数据
const studentOptions = ref([])
const courseOptions = ref([
  { label: 'CS101 - 计算机科学导论', value: '1' },
  { label: 'SE201 - 软件工程', value: '2' },
  { label: 'DS301 - 数据结构与算法', value: '3' },
  { label: 'AI401 - 人工智能导论', value: '4' },
  { label: 'DB201 - 数据库系统', value: '5' },
  { label: 'ML501 - 机器学习', value: '6' }
])

// 计算属性
const isEdit = computed(() => !!props.grade)
const percentage = computed(() => {
  if (form.max_score && form.score !== null) {
    return (form.score / form.max_score) * 100
  }
  return 0
})

// 表单验证规则
const rules = {
  student_id: [
    { required: true, message: '请选择学生', trigger: 'change' }
  ],
  course_id: [
    { required: true, message: '请选择课程', trigger: 'change' }
  ],
  exam_type: [
    { required: true, message: '请选择考试类型', trigger: 'change' }
  ],
  exam_name: [
    { required: true, message: '请输入考试名称', trigger: 'blur' }
  ],
  score: [
    { required: true, message: '请输入分数', trigger: 'blur' }
  ],
  max_score: [
    { required: true, message: '请输入满分', trigger: 'blur' }
  ],
  semester: [
    { required: true, message: '请选择学期', trigger: 'change' }
  ]
}

// 监听 modelValue 变化
const { modelValue } = toRefs(props)
watch(modelValue, (val) => {
  visible.value = val
  if (val) {
    if (props.grade) {
      // 编辑模式：填充表单数据
      Object.assign(form, {
        student_id: props.grade.student_id || '',
        course_id: props.grade.course_id || '',
        exam_type: props.grade.exam_type || '',
        exam_name: props.grade.exam_name || '',
        score: props.grade.score || 0,
        max_score: props.grade.max_score || 100,
        weight: props.grade.weight || 1.0,
        semester: props.grade.semester || '2025-春季',
        is_published: props.grade.is_published || false,
        comments: props.grade.comments || '',
        improvement_suggestions: props.grade.improvement_suggestions || ''
      })
    } else {
      // 新建模式：重置表单
      resetForm()
    }
  }
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 搜索学生
const searchStudents = async (query: string) => {
  if (!query) {
    studentOptions.value = []
    return
  }

  try {
    studentLoading.value = true
    // 模拟搜索结果
    const mockStudents = [
      { label: 'S2021001 - 张三', value: '1' },
      { label: 'S2021002 - 李四', value: '2' },
      { label: 'S2021003 - 王五', value: '3' },
      { label: 'S2021004 - 赵六', value: '4' },
      { label: 'S2021005 - 钱七', value: '5' }
    ].filter(student => student.label.toLowerCase().includes(query.toLowerCase()))

    studentOptions.value = mockStudents
  } catch (error) {
    console.error('搜索学生失败:', error)
  } finally {
    studentLoading.value = false
  }
}

// 处理课程变化
const handleCourseChange = (courseId: string) => {
  const course = courseOptions.value.find(c => c.value === courseId)
  if (course) {
    // 可以根据课程预设一些信息
    if (!form.exam_name) {
      form.exam_name = form.exam_type === 'final' ? '期末考试' : '成绩'
    }
  }
}

// 处理满分变化
const handleMaxScoreChange = (maxScore: number) => {
  if (form.score > maxScore) {
    form.score = maxScore
  }
}

// 获取成绩等级
const getGradeLevel = (percentage: number) => {
  if (percentage >= 90) return '优秀'
  if (percentage >= 80) return '良好'
  if (percentage >= 70) return '中等'
  if (percentage >= 60) return '及格'
  return '不及格'
}

// 获取成绩标签类型
const getGradeTag = (percentage: number) => {
  if (percentage >= 90) return 'success'
  if (percentage >= 80) return 'primary'
  if (percentage >= 70) return 'warning'
  if (percentage >= 60) return 'info'
  return 'danger'
}

// 获取绩点
const getGradePoint = (percentage: number) => {
  if (percentage >= 90) return '4.0'
  if (percentage >= 85) return '3.7'
  if (percentage >= 82) return '3.3'
  if (percentage >= 78) return '3.0'
  if (percentage >= 75) return '2.7'
  if (percentage >= 72) return '2.3'
  if (percentage >= 68) return '2.0'
  if (percentage >= 64) return '1.5'
  if (percentage >= 60) return '1.0'
  return '0.0'
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    student_id: '',
    course_id: '',
    exam_type: '',
    exam_name: '',
    score: 0,
    max_score: 100,
    weight: 1.0,
    semester: '2025-春季',
    is_published: false,
    comments: '',
    improvement_suggestions: ''
  })
  studentOptions.value = []
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    const gradeData = {
      ...form,
      score: Number(form.score),
      max_score: Number(form.max_score),
      weight: Number(form.weight)
    }

    if (isEdit.value) {
      await gradeApi.updateGrade(props.grade.id, gradeData)
      ElMessage.success('成绩更新成功')
    } else {
      await gradeApi.createGrade(gradeData)
      ElMessage.success('成绩录入成功')
    }

    emit('success')
  } catch (error) {
    console.error('保存成绩失败:', error)
    if (error !== 'cancel') {
      ElMessage.error(isEdit.value ? '更新成绩失败' : '录入成绩失败')
    }
    emit('error', error)
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-descriptions__body) {
  background-color: var(--el-fill-color-light);
}
</style>