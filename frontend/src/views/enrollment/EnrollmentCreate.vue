<template>
  <div class="enrollment-create">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">学生选课</span>
      </template>
    </el-page-header>

    <div class="form-container">
      <el-card>
        <template #header>
          <span class="card-title">选课信息</span>
        </template>

        <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-width="120px"
          size="large"
        >
          <el-form-item label="学生信息" prop="student_id">
            <el-select
              v-model="formData.student_id"
              placeholder="请选择学生"
              style="width: 100%"
              filterable
              @change="handleStudentChange"
            >
              <el-option
                v-for="student in students"
                :key="student.value"
                :label="student.label"
                :value="student.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="选择课程" prop="course_id">
            <el-select
              v-model="formData.course_id"
              placeholder="请选择课程"
              style="width: 100%"
              filterable
              :disabled="!formData.student_id"
              @change="handleCourseChange"
            >
              <el-option
                v-for="course in availableCourses"
                :key="course.value"
                :label="course.label"
                :value="course.value"
                :disabled="course.disabled"
              >
                <span>{{ course.label }}</span>
                <span v-if="course.disabled" style="color: #f56c6c; margin-left: 10px;">
                  (已选满/时间冲突)
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="课程信息" v-if="selectedCourse">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="课程编号">{{ selectedCourse.course_code }}</el-descriptions-item>
              <el-descriptions-item label="学分">{{ selectedCourse.credits }}</el-descriptions-item>
              <el-descriptions-item label="学时">{{ selectedCourse.hours }}</el-descriptions-item>
              <el-descriptions-item label="教师">{{ selectedCourse.teacher_name }}</el-descriptions-item>
              <el-descriptions-item label="学期">{{ selectedCourse.semester }}</el-descriptions-item>
              <el-descriptions-item label="剩余名额">{{ selectedCourse.available_spots }}</el-descriptions-item>
            </el-descriptions>
          </el-form-item>

          <el-form-item label="当前已选课程" v-if="studentEnrollments.length > 0">
            <el-table :data="studentEnrollments" size="small">
              <el-table-column label="课程编号" prop="course_code" width="120" />
              <el-table-column label="课程名称" prop="course_name" />
              <el-table-column label="学分" prop="credits" width="80" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>

          <el-form-item label="选课原因" prop="notes">
            <el-input
              v-model="formData.notes"
              type="textarea"
              :rows="4"
              placeholder="请输入选课原因（选填）"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="loading">
              提交选课
            </el-button>
            <el-button @click="handleReset">重置</el-button>
            <el-button @click="handleBack">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)

interface Student {
  value: number
  label: string
  student_no: string
  class_name: string
  major: string
}

interface Course {
  value: number
  label: string
  course_code: string
  credits: number
  hours: number
  teacher_name: string
  semester: string
  available_spots: number
  disabled?: boolean
  disabled_reason?: string
}

interface Enrollment {
  id: number
  course_code: string
  course_name: string
  credits: number
  status: 'pending' | 'approved' | 'rejected'
}

const formData = reactive({
  student_id: '',
  course_id: '',
  notes: ''
})

const rules: FormRules = {
  student_id: [
    { required: true, message: '请选择学生', trigger: 'change' }
  ],
  course_id: [
    { required: true, message: '请选择课程', trigger: 'change' }
  ]
}

const students = ref<Student[]>([])
const availableCourses = ref<Course[]>([])
const studentEnrollments = ref<Enrollment[]>([])

const selectedCourse = computed(() => {
  return availableCourses.value.find(course => course.value === formData.course_id)
})

const selectedStudent = computed(() => {
  return students.value.find(student => student.value === formData.student_id)
})

const loadStudents = async () => {
  try {
    // Mock API call - 替换为实际的API调用
    const mockStudents: Student[] = [
      { value: 1, label: '张三 (S2021001)', student_no: 'S2021001', class_name: '计算机科学1班', major: '计算机科学' },
      { value: 2, label: '李四 (S2021002)', student_no: 'S2021002', class_name: '计算机科学1班', major: '计算机科学' },
      { value: 3, label: '王五 (S2021003)', student_no: 'S2021003', class_name: '软件工程1班', major: '软件工程' },
      { value: 4, label: '赵六 (S2021004)', student_no: 'S2021004', class_name: '软件工程1班', major: '软件工程' }
    ]
    students.value = mockStudents
  } catch (error) {
    ElMessage.error('获取学生列表失败')
  }
}

const loadAvailableCourses = async (studentId: number) => {
  try {
    // Mock API call - 替换为实际的API调用
    const mockCourses: Course[] = [
      {
        value: 1,
        label: '计算机科学导论 - 李明',
        course_code: 'CS101',
        credits: 3,
        hours: 48,
        teacher_name: '李明',
        semester: '2024-春',
        available_spots: 15
      },
      {
        value: 2,
        label: '数据结构与算法 - 王芳',
        course_code: 'CS102',
        credits: 4,
        hours: 64,
        teacher_name: '王芳',
        semester: '2024-春',
        available_spots: 0,
        disabled: true,
        disabled_reason: '已选满'
      },
      {
        value: 3,
        label: '数据库系统 - 张伟',
        course_code: 'CS103',
        credits: 3,
        hours: 48,
        teacher_name: '张伟',
        semester: '2024-春',
        available_spots: 8
      },
      {
        value: 4,
        label: '操作系统 - 刘洋',
        course_code: 'CS104',
        credits: 4,
        hours: 64,
        teacher_name: '刘洋',
        semester: '2024-春',
        available_spots: 12
      }
    ]
    availableCourses.value = mockCourses
  } catch (error) {
    ElMessage.error('获取可选课程列表失败')
  }
}

const loadStudentEnrollments = async (studentId: number) => {
  try {
    // Mock API call - 替换为实际的API调用
    const mockEnrollments: Enrollment[] = [
      {
        id: 1,
        course_code: 'CS105',
        course_name: '计算机网络',
        credits: 3,
        status: 'approved'
      }
    ]
    studentEnrollments.value = mockEnrollments
  } catch (error) {
    ElMessage.error('获取学生选课记录失败')
  }
}

const handleStudentChange = async (studentId: number) => {
  formData.course_id = ''
  availableCourses.value = []
  studentEnrollments.value = []

  if (studentId) {
    await Promise.all([
      loadAvailableCourses(studentId),
      loadStudentEnrollments(studentId)
    ])
  }
}

const handleCourseChange = async (courseId: number) => {
  if (courseId && selectedCourse.value) {
    // 检查选课冲突
    await checkEnrollmentConflict()
  }
}

const checkEnrollmentConflict = async () => {
  if (!selectedCourse.value) return

  // 检查是否已经选过这门课
  const alreadyEnrolled = studentEnrollments.value.some(
    enrollment => enrollment.course_code === selectedCourse.value?.course_code
  )

  if (alreadyEnrolled) {
    ElMessage.warning('该学生已经选择了这门课程')
    formData.course_id = ''
    return
  }

  // 检查时间冲突（这里简化处理，实际需要更复杂的逻辑）
  const hasTimeConflict = studentEnrollments.value.some(enrollment => {
    // 模拟时间冲突检查
    return enrollment.course_code.startsWith('CS10') && selectedCourse.value?.course_code.startsWith('CS10')
  })

  if (hasTimeConflict) {
    ElMessage.warning('选课时间冲突，请选择其他课程')
    formData.course_id = ''
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    if (!selectedStudent.value || !selectedCourse.value) {
      ElMessage.error('请完整填写选课信息')
      return
    }

    // 确认选课信息
    const confirmResult = await ElMessageBox.confirm(`
      确认为以下学生选课？<br><br>
      <strong>学生：</strong>${selectedStudent.value.label}<br>
      <strong>课程：</strong>${selectedCourse.value.course_code} - ${selectedCourse.value.label}<br>
      <strong>学分：</strong>${selectedCourse.value.credits}<br>
      <strong>教师：</strong>${selectedCourse.value.teacher_name}<br>
      <strong>剩余名额：</strong>${selectedCourse.value.available_spots}
    `, '确认选课', {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确认选课',
      cancelButtonText: '取消'
    })

    if (confirmResult !== 'confirm') return

    loading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('选课申请提交成功，等待审批')

    // 跳转到选课列表页面
    router.push('/enrollments')
  } catch (error) {
    if (error !== 'validation failed') {
      ElMessage.error('选课提交失败')
    }
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  availableCourses.value = []
  studentEnrollments.value = []
}

const handleBack = () => {
  router.back()
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝'
  }
  return statusMap[status] || status
}

onMounted(() => {
  loadStudents()
})
</script>

<style lang="scss" scoped>
.enrollment-create {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .form-container {
    margin-top: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }

    .el-card {
      .el-table {
        margin-top: 8px;
      }
    }
  }
}
</style>