<template>
  <div class="grade-entry">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">成绩录入</span>
      </template>
    </el-page-header>

    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="课程">
          <el-select v-model="filterForm.course_id" placeholder="选择课程" style="width: 200px">
            <el-option
              v-for="course in courses"
              :key="course.value"
              :label="course.label"
              :value="course.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select v-model="filterForm.semester" placeholder="选择学期" style="width: 150px">
            <el-option label="2024-春" value="2024-春" />
            <el-option label="2024-夏" value="2024-夏" />
            <el-option label="2024-秋" value="2024-秋" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadStudents">
            查询学生
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-card v-if="filterForm.course_id">
      <template #header>
        <div class="card-header">
          <span class="card-title">成绩录入</span>
          <div class="card-actions">
            <el-button type="success" @click="handleSaveAll" :loading="loading">
              批量保存
            </el-button>
            <el-button @click="handleImport">
              导入成绩
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="tableLoading"
        :data="students"
        stripe
        style="width: 100%"
      >
        <el-table-column label="学号" prop="student_no" width="120" />
        <el-table-column label="姓名" prop="name" width="100" />
        <el-table-column label="专业" prop="major" />
        <el-table-column label="班级" prop="class_name" width="120" />

        <el-table-column label="平时成绩" width="120">
          <template #default="{ row }">
            <el-input-number
              v-model="row.regular_score"
              :min="0"
              :max="100"
              :precision="1"
              size="small"
              style="width: 100px"
              @change="handleGradeChange(row)"
            />
          </template>
        </el-table-column>

        <el-table-column label="期中成绩" width="120">
          <template #default="{ row }">
            <el-input-number
              v-model="row.midterm_score"
              :min="0"
              :max="100"
              :precision="1"
              size="small"
              style="width: 100px"
              @change="handleGradeChange(row)"
            />
          </template>
        </el-table-column>

        <el-table-column label="期末成绩" width="120">
          <template #default="{ row }">
            <el-input-number
              v-model="row.final_score"
              :min="0"
              :max="100"
              :precision="1"
              size="small"
              style="width: 100px"
              @change="handleGradeChange(row)"
            />
          </template>
        </el-table-column>

        <el-table-column label="总评成绩" width="120">
          <template #default="{ row }">
            <el-input
              v-model="row.total_score"
              size="small"
              style="width: 100px"
              readonly
              :class="{ 'grade-excellent': row.total_score >= 90, 'grade-pass': row.total_score >= 60 }"
            />
          </template>
        </el-table-column>

        <el-table-column label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getGradeType(row.total_score)">
              {{ getGradeLevel(row.total_score) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="备注" width="150">
          <template #default="{ row }">
            <el-input
              v-model="row.remark"
              size="small"
              placeholder="备注"
            />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleSaveGrade(row)"
              :loading="row.saving"
            >
              保存
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="grade-summary">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="学生总数">{{ students.length }}</el-descriptions-item>
          <el-descriptions-item label="已录入">{{ savedCount }}</el-descriptions-item>
          <el-descriptions-item label="平均分">{{ averageScore.toFixed(1) }}</el-descriptions-item>
          <el-descriptions-item label="及格率">{{ passRate.toFixed(1) }}%</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 成绩导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入成绩"
      width="500px"
    >
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传xlsx/xls文件，且不超过2MB
          </div>
        </template>
      </el-upload>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importLoading">
          确认导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const tableLoading = ref(false)
const importLoading = ref(false)
const importDialogVisible = ref(false)

interface Course {
  value: number
  label: string
  course_code: string
  credits: number
}

interface Student {
  id: number
  student_no: string
  name: string
  major: string
  class_name: string
  regular_score?: number
  midterm_score?: number
  final_score?: number
  total_score?: string
  remark?: string
  saving?: boolean
  saved?: boolean
}

const filterForm = reactive({
  course_id: '',
  semester: '2024-春'
})

const courses = ref<Course[]>([])
const students = ref<Student[]>([])
const uploadFile = ref<File | null>(null)

const savedCount = computed(() => {
  return students.value.filter(student => student.saved).length
})

const averageScore = computed(() => {
  const validScores = students.value
    .filter(student => student.total_score && parseFloat(student.total_score) >= 0)
    .map(student => parseFloat(student.total_score!))

  if (validScores.length === 0) return 0
  return validScores.reduce((sum, score) => sum + score, 0) / validScores.length
})

const passRate = computed(() => {
  if (students.value.length === 0) return 0
  const passCount = students.value.filter(student =>
    student.total_score && parseFloat(student.total_score) >= 60
  ).length
  return (passCount / students.value.length) * 100
})

const loadCourses = async () => {
  try {
    // Mock API call - 替换为实际的API调用
    const mockCourses: Course[] = [
      { value: 1, label: '计算机科学导论 - 李明', course_code: 'CS101', credits: 3 },
      { value: 2, label: '数据结构与算法 - 王芳', course_code: 'CS102', credits: 4 },
      { value: 3, label: '数据库系统 - 张伟', course_code: 'CS103', credits: 3 },
      { value: 4, label: '操作系统 - 刘洋', course_code: 'CS104', credits: 4 }
    ]
    courses.value = mockCourses
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  }
}

const loadStudents = async () => {
  if (!filterForm.course_id) {
    ElMessage.warning('请先选择课程')
    return
  }

  try {
    tableLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockStudents: Student[] = [
      {
        id: 1,
        student_no: 'S2021001',
        name: '张三',
        major: '计算机科学',
        class_name: '计算机科学1班',
        regular_score: 85,
        midterm_score: 78,
        final_score: 82,
        total_score: '81.7',
        remark: '',
        saved: false
      },
      {
        id: 2,
        student_no: 'S2021002',
        name: '李四',
        major: '计算机科学',
        class_name: '计算机科学1班',
        regular_score: 92,
        midterm_score: 88,
        final_score: 95,
        total_score: '91.9',
        remark: '优秀学生',
        saved: true
      },
      {
        id: 3,
        student_no: 'S2021003',
        name: '王五',
        major: '软件工程',
        class_name: '软件工程1班',
        regular_score: 76,
        midterm_score: 72,
        final_score: 68,
        total_score: '71.2',
        remark: '',
        saved: false
      }
    ]

    students.value = mockStudents
  } catch (error) {
    ElMessage.error('获取学生列表失败')
  } finally {
    tableLoading.value = false
  }
}

const calculateTotalScore = (student: Student) => {
  const regular = student.regular_score || 0
  const midterm = student.midterm_score || 0
  const final = student.final_score || 0

  // 假设权重：平时30%，期中30%，期末40%
  const total = (regular * 0.3) + (midterm * 0.3) + (final * 0.4)
  student.total_score = total.toFixed(1)
}

const handleGradeChange = (student: Student) => {
  calculateTotalScore(student)
  student.saved = false
}

const handleSaveGrade = async (student: Student) => {
  try {
    student.saving = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    student.saved = true
    ElMessage.success(`${student.name} 的成绩保存成功`)
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    student.saving = false
  }
}

const handleSaveAll = async () => {
  const unsavedStudents = students.value.filter(student => !student.saved)

  if (unsavedStudents.length === 0) {
    ElMessage.info('没有需要保存的成绩')
    return
  }

  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1500))

    unsavedStudents.forEach(student => {
      student.saved = true
    })

    ElMessage.success(`批量保存 ${unsavedStudents.length} 条成绩记录成功`)
  } catch (error) {
    ElMessage.error('批量保存失败')
  } finally {
    loading.value = false
  }
}

const handleImport = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadFile.value = file.raw
}

const handleImportSubmit = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  try {
    importLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 2000))

    ElMessage.success('成绩导入成功')
    importDialogVisible.value = false
    uploadFile.value = null

    // 重新加载数据
    await loadStudents()
  } catch (error) {
    ElMessage.error('成绩导入失败')
  } finally {
    importLoading.value = false
  }
}

const getGradeType = (score: string | undefined) => {
  if (!score) return 'info'
  const numScore = parseFloat(score)

  if (numScore >= 90) return 'success'
  if (numScore >= 80) return 'primary'
  if (numScore >= 70) return 'warning'
  if (numScore >= 60) return 'info'
  return 'danger'
}

const getGradeLevel = (score: string | undefined) => {
  if (!score) return '-'
  const numScore = parseFloat(score)

  if (numScore >= 90) return '优秀'
  if (numScore >= 80) return '良好'
  if (numScore >= 70) return '中等'
  if (numScore >= 60) return '及格'
  return '不及格'
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadCourses()
})
</script>

<style lang="scss" scoped>
.grade-entry {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .filter-container {
    margin: 20px 0;
    padding: 20px;
    background-color: var(--el-bg-color-page);
    border-radius: 8px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .grade-excellent {
    color: var(--el-color-success);
    font-weight: 600;
  }

  .grade-pass {
    color: var(--el-color-primary);
  }

  .grade-summary {
    margin-top: 20px;
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 8px;
  }
}
</style>