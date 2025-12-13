<template>
  <el-dialog
    v-model="visible"
    title="批量录入成绩"
    width="900px"
    @close="handleClose"
  >
    <div class="bulk-entry-container">
      <!-- 基本信息设置 -->
      <el-form
        ref="basicFormRef"
        :model="basicForm"
        :rules="basicRules"
        label-width="120px"
        style="margin-bottom: 20px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程" prop="course_id">
              <el-select
                v-model="basicForm.course_id"
                placeholder="选择课程"
                style="width: 100%"
                @change="loadStudents"
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
          <el-col :span="12">
            <el-form-item label="考试类型" prop="exam_type">
              <el-select v-model="basicForm.exam_type" placeholder="选择类型" style="width: 100%">
                <el-option label="测验" value="quiz" />
                <el-option label="作业" value="assignment" />
                <el-option label="期中考试" value="midterm" />
                <el-option label="期末考试" value="final" />
                <el-option label="项目" value="project" />
                <el-option label="演讲" value="presentation" />
                <el-option label="实验课" value="lab" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="考试名称" prop="exam_name">
              <el-input v-model="basicForm.exam_name" placeholder="如：期中考试、作业1等" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="满分" prop="max_score">
              <el-input-number
                v-model="basicForm.max_score"
                :min="1"
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="权重" prop="weight">
              <el-input-number
                v-model="basicForm.weight"
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
              <el-select v-model="basicForm.semester" placeholder="选择学期" style="width: 100%">
                <el-option label="2024-春季" value="2024-春季" />
                <el-option label="2024-夏季" value="2024-夏季" />
                <el-option label="2024-秋季" value="2024-秋季" />
                <el-option label="2025-春季" value="2025-春季" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <div class="action-buttons">
              <el-button type="primary" @click="loadStudents" :loading="loading">
                加载学生
              </el-button>
              <el-button @click="fillAllScores">
                统一分数
              </el-button>
              <el-button @click="clearAllScores">
                清空分数
              </el-button>
            </div>
          </el-col>
        </el-row>
      </el-form>

      <!-- 统一分数设置 -->
      <el-card v-if="showFillScores" class="fill-scores-card" style="margin-bottom: 20px">
        <el-form :model="fillForm" inline>
          <el-form-item label="统一分数">
            <el-input-number
              v-model="fillForm.score"
              :min="0"
              :max="basicForm.max_score"
              :precision="1"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFillScores">应用</el-button>
            <el-button @click="showFillScores = false">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 学生成绩表格 -->
      <div class="students-section">
        <div class="section-header">
          <h4>学生名单 ({{ students.length }}人)</h4>
          <div class="header-stats">
            <el-tag type="success">已录入: {{ filledCount }}</el-tag>
            <el-tag type="warning">未录入: {{ students.length - filledCount }}</el-tag>
            <el-tag type="primary">平均分: {{ averageScore.toFixed(1) }}</el-tag>
          </div>
        </div>

        <el-table
          v-loading="loading"
          :data="students"
          border
          stripe
          height="400"
          style="width: 100%"
        >
          <el-table-column type="index" width="50" label="#" />
          <el-table-column label="学号" prop="student_id" width="120" />
          <el-table-column label="姓名" prop="name" width="100" />
          <el-table-column label="专业" prop="major" width="120" />
          <el-table-column label="班级" prop="class_name" width="120" />

          <el-table-column label="分数" width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.score"
                :min="0"
                :max="basicForm.max_score"
                :precision="1"
                size="small"
                style="width: 100px"
                @change="handleScoreChange(row)"
              />
            </template>
          </el-table-column>

          <el-table-column label="百分比" width="100">
            <template #default="{ row }">
              <span :style="{ color: getScoreColor(row.score) }">
                {{ getPercentage(row.score) }}%
              </span>
            </template>
          </el-table-column>

          <el-table-column label="等级" width="100">
            <template #default="{ row }">
              <el-tag :type="getGradeTag(row.score)" size="small">
                {{ getGradeLevel(row.score) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="评语" min-width="150">
            <template #default="{ row }">
              <el-input
                v-model="row.comments"
                size="small"
                placeholder="评语"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 汇总信息 -->
      <div class="summary-section" v-if="students.length > 0">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="学生总数">{{ students.length }}</el-descriptions-item>
          <el-descriptions-item label="已录入">{{ filledCount }}</el-descriptions-item>
          <el-descriptions-item label="平均分">{{ averageScore.toFixed(1) }}</el-descriptions-item>
          <el-descriptions-item label="及格率">{{ passRate.toFixed(1) }}%</el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="success"
          @click="handleImport"
          :loading="importing"
        >
          导入Excel
        </el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
          :disabled="filledCount === 0"
        >
          批量保存 ({{ filledCount }})
        </el-button>
      </div>
    </template>

    <!-- Excel导入对话框 -->
    <GradeImportDialog
      v-model="importDialogVisible"
      @success="handleImportSuccess"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, toRefs } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import GradeImportDialog from './GradeImportDialog.vue'
import { gradeApi } from '@/api'

const emit = defineEmits(['success', 'error'])

// 组件属性
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

// 响应式数据
const visible = ref(props.modelValue)
const loading = ref(false)
const submitting = ref(false)
const importing = ref(false)
const showFillScores = ref(false)
const importDialogVisible = ref(false)
const basicFormRef = ref(null)

// 基本信息表单
const basicForm = reactive({
  course_id: '',
  exam_type: '',
  exam_name: '',
  max_score: 100,
  weight: 1.0,
  semester: '2025-春季'
})

// 统一分数表单
const fillForm = reactive({
  score: 0
})

// 数据
const students = ref([])
const courseOptions = ref([
  { label: 'CS101 - 计算机科学导论', value: '1' },
  { label: 'SE201 - 软件工程', value: '2' },
  { label: 'DS301 - 数据结构与算法', value: '3' },
  { label: 'AI401 - 人工智能导论', value: '4' },
  { label: 'DB201 - 数据库系统', value: '5' },
  { label: 'ML501 - 机器学习', value: '6' }
])

// 验证规则
const basicRules = {
  course_id: [
    { required: true, message: '请选择课程', trigger: 'change' }
  ],
  exam_type: [
    { required: true, message: '请选择考试类型', trigger: 'change' }
  ],
  exam_name: [
    { required: true, message: '请输入考试名称', trigger: 'blur' }
  ],
  max_score: [
    { required: true, message: '请输入满分', trigger: 'blur' }
  ],
  semester: [
    { required: true, message: '请选择学期', trigger: 'change' }
  ]
}

// 计算属性
const filledCount = computed(() => {
  return students.value.filter(student => student.score !== null && student.score !== undefined).length
})

const averageScore = computed(() => {
  const validScores = students.value
    .filter(student => student.score !== null && student.score !== undefined)
    .map(student => student.score)

  if (validScores.length === 0) return 0
  return validScores.reduce((sum, score) => sum + score, 0) / validScores.length
})

const passRate = computed(() => {
  if (students.value.length === 0) return 0
  const passCount = students.value.filter(student => {
    const percentage = (student.score / basicForm.max_score) * 100
    return percentage >= 60
  }).length
  return (passCount / students.value.length) * 100
})

// 监听 modelValue 变化
const { modelValue } = toRefs(props)
watch(modelValue, (val) => {
  visible.value = val
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    resetForm()
  }
})

// 加载学生列表
const loadStudents = async () => {
  if (!basicForm.course_id) {
    ElMessage.warning('请先选择课程')
    return
  }

  try {
    loading.value = true

    // 模拟加载学生数据
    const mockStudents = [
      {
        id: '1',
        student_id: 'S2021001',
        name: '张三',
        major: '计算机科学',
        class_name: '计算机科学1班',
        score: null,
        comments: ''
      },
      {
        id: '2',
        student_id: 'S2021002',
        name: '李四',
        major: '计算机科学',
        class_name: '计算机科学1班',
        score: null,
        comments: ''
      },
      {
        id: '3',
        student_id: 'S2021003',
        name: '王五',
        major: '软件工程',
        class_name: '软件工程1班',
        score: null,
        comments: ''
      },
      {
        id: '4',
        student_id: 'S2021004',
        name: '赵六',
        major: '软件工程',
        class_name: '软件工程1班',
        score: null,
        comments: ''
      },
      {
        id: '5',
        student_id: 'S2021005',
        name: '钱七',
        major: '数据科学',
        class_name: '数据科学1班',
        score: null,
        comments: ''
      }
    ]

    students.value = mockStudents
    ElMessage.success(`已加载 ${mockStudents.length} 名学生`)
  } catch (error) {
    console.error('加载学生失败:', error)
    ElMessage.error('加载学生失败')
  } finally {
    loading.value = false
  }
}

// 统一分数设置
const fillAllScores = () => {
  showFillScores.value = true
}

const applyFillScores = () => {
  students.value.forEach(student => {
    student.score = fillForm.score
  })
  showFillScores.value = false
  ElMessage.success('统一分数已应用')
}

// 清空分数
const clearAllScores = () => {
  students.value.forEach(student => {
    student.score = null
    student.comments = ''
  })
  ElMessage.success('分数已清空')
}

// 处理分数变化
const handleScoreChange = (row: any) => {
  // 可以在这里添加逻辑，如自动计算等级等
}

// 获取百分比
const getPercentage = (score: number) => {
  if (score === null || score === undefined) return 0
  return ((score / basicForm.max_score) * 100).toFixed(1)
}

// 获取成绩等级
const getGradeLevel = (score: number) => {
  if (score === null || score === undefined) return '-'
  const percentage = (score / basicForm.max_score) * 100
  if (percentage >= 90) return '优秀'
  if (percentage >= 80) return '良好'
  if (percentage >= 70) return '中等'
  if (percentage >= 60) return '及格'
  return '不及格'
}

// 获取成绩标签类型
const getGradeTag = (score: number) => {
  if (score === null || score === undefined) return 'info'
  const percentage = (score / basicForm.max_score) * 100
  if (percentage >= 90) return 'success'
  if (percentage >= 80) return 'primary'
  if (percentage >= 70) return 'warning'
  if (percentage >= 60) return 'info'
  return 'danger'
}

// 获取分数颜色
const getScoreColor = (score: number) => {
  if (score === null || score === undefined) return '#909399'
  const percentage = (score / basicForm.max_score) * 100
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

// 导入Excel
const handleImport = () => {
  importDialogVisible.value = true
}

const handleImportSuccess = (importedData: any[]) => {
  // 处理导入的数据
  importedData.forEach(data => {
    const student = students.value.find(s => s.student_id === data.student_id)
    if (student) {
      student.score = data.score
      student.comments = data.comments || ''
    }
  })
  ElMessage.success(`已导入 ${importedData.length} 条成绩记录`)
}

// 提交批量保存
const handleSubmit = async () => {
  try {
    await basicFormRef.value.validate()

    if (filledCount.value === 0) {
      ElMessage.warning('请至少录入一条成绩')
      return
    }

    await ElMessageBox.confirm(
      `确定要批量保存 ${filledCount.value} 条成绩记录吗？`,
      '批量保存确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    submitting.value = true

    // 准备批量数据
    const gradesData = students.value
      .filter(student => student.score !== null && student.score !== undefined)
      .map(student => ({
        student_id: student.id,
        course_id: basicForm.course_id,
        exam_type: basicForm.exam_type,
        exam_name: basicForm.exam_name,
        score: student.score,
        max_score: basicForm.max_score,
        weight: basicForm.weight,
        semester: basicForm.semester,
        comments: student.comments
      }))

    // 调用批量录入API
    await gradeApi.bulkCreateGrades({
      course_id: basicForm.course_id,
      exam_type: basicForm.exam_type,
      exam_name: basicForm.exam_name,
      max_score: basicForm.max_score,
      weight: basicForm.weight,
      semester: basicForm.semester,
      grades: gradesData
    })

    ElMessage.success(`批量保存 ${gradesData.length} 条成绩成功`)
    emit('success')
  } catch (error) {
    console.error('批量保存失败:', error)
    if (error !== 'cancel') {
      ElMessage.error('批量保存失败')
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(basicForm, {
    course_id: '',
    exam_type: '',
    exam_name: '',
    max_score: 100,
    weight: 1.0,
    semester: '2025-春季'
  })
  students.value = []
  showFillScores.value = false
  fillForm.score = 0
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.bulk-entry-container {
  max-height: 70vh;
  overflow-y: auto;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 32px;
}

.students-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  color: #303133;
}

.header-stats {
  display: flex;
  gap: 8px;
}

.summary-section {
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-input-number--small) {
  width: 100px;
}
</style>