<template>
  <div class="course-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>课程管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加课程
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索课程名称、代码、教师"
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filterSemester" placeholder="选择学期" clearable>
            <el-option label="全部学期" value="" />
            <el-option label="2024-春季" value="2024-春季" />
            <el-option label="2024-夏季" value="2024-夏季" />
            <el-option label="2024-秋季" value="2024-秋季" />
            <el-option label="2024-冬季" value="2024-冬季" />
            <el-option label="2025-春季" value="2025-春季" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filterDepartment" placeholder="选择院系" clearable>
            <el-option label="全部院系" value="" />
            <el-option label="计算机科学系" value="计算机科学系" />
            <el-option label="软件工程系" value="软件工程系" />
            <el-option label="数据科学系" value="数据科学系" />
            <el-option label="电子工程系" value="电子工程系" />
            <el-option label="数学系" value="数学系" />
            <el-option label="物理系" value="物理系" />
            <el-option label="化学系" value="化学系" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 课程列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="courses"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="course_code" label="课程代码" width="120" />
        <el-table-column prop="course_name" label="课程名称" width="180" />
        <el-table-column prop="credits" label="学分" width="80" />
        <el-table-column prop="hours" label="学时" width="80" />
        <el-table-column prop="teacher_name" label="授课教师" width="120" />
        <el-table-column prop="department" label="院系" width="120" />
        <el-table-column prop="semester" label="学期" width="100" />
        <el-table-column prop="max_students" label="最大人数" width="100" />
        <el-table-column prop="current_students" label="当前人数" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="getEnrollmentPercentage(row)"
              :color="getEnrollmentColor(row)"
              :stroke-width="6"
            />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="warning" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 添加/编辑课程对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑课程' : '添加课程'"
      width="900px"
      @close="handleDialogClose"
    >
      <el-form
        ref="courseFormRef"
        :model="courseForm"
        :rules="formRules"
        label-width="120px"
        size="default"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程代码" prop="course_code">
              <el-input
                v-model="courseForm.course_code"
                placeholder="请输入课程代码"
                :disabled="isEdit"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程名称" prop="course_name">
              <el-input v-model="courseForm.course_name" placeholder="请输入课程名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学分" prop="credits">
              <el-input-number
                v-model="courseForm.credits"
                :min="1"
                :max="10"
                placeholder="学分"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学时" prop="hours">
              <el-input-number
                v-model="courseForm.hours"
                :min="1"
                :max="200"
                placeholder="学时"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="课程类型" prop="course_type">
              <el-select v-model="courseForm.course_type" placeholder="请选择课程类型">
                <el-option label="必修课" value="required" />
                <el-option label="选修课" value="elective" />
                <el-option label="实验课" value="lab" />
                <el-option label="研讨课" value="seminar" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="授课教师" prop="teacher_name">
              <el-input v-model="courseForm.teacher_name" placeholder="请输入授课教师姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="教师工号" prop="teacher_id">
              <el-input v-model="courseForm.teacher_id" placeholder="请输入教师工号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="院系" prop="department">
              <el-select v-model="courseForm.department" placeholder="请选择院系">
                <el-option label="计算机科学系" value="计算机科学系" />
                <el-option label="软件工程系" value="软件工程系" />
                <el-option label="数据科学系" value="数据科学系" />
                <el-option label="电子工程系" value="电子工程系" />
                <el-option label="数学系" value="数学系" />
                <el-option label="物理系" value="物理系" />
                <el-option label="化学系" value="化学系" />
                <el-option label="外语系" value="外语系" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学期" prop="semester">
              <el-select v-model="courseForm.semester" placeholder="请选择学期">
                <el-option label="2024-春季" value="2024-春季" />
                <el-option label="2024-夏季" value="2024-夏季" />
                <el-option label="2024-秋季" value="2024-秋季" />
                <el-option label="2024-冬季" value="2024-冬季" />
                <el-option label="2025-春季" value="2025-春季" />
                <el-option label="2025-夏季" value="2025-夏季" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="最大人数" prop="max_students">
              <el-input-number
                v-model="courseForm.max_students"
                :min="1"
                :max="500"
                placeholder="最大人数"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="当前人数" prop="current_students">
              <el-input-number
                v-model="courseForm.current_students"
                :min="0"
                :max="courseForm.max_students"
                placeholder="当前人数"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-select v-model="courseForm.status" placeholder="请选择状态">
                <el-option label="正常" value="active" />
                <el-option label="已满" value="full" />
                <el-option label="暂停" value="suspended" />
                <el-option label="已结束" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上课时间" prop="schedule">
              <el-input v-model="courseForm.schedule" placeholder="如：周一 14:00-16:00" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上课地点" prop="location">
              <el-input v-model="courseForm.location" placeholder="请输入上课地点" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="课程描述" prop="description">
          <el-input
            v-model="courseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入课程描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 课程详情对话框 -->
    <el-dialog v-model="detailVisible" title="课程详情" width="900px">
      <div v-if="selectedCourse" class="course-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="课程代码">{{ selectedCourse.course_code }}</el-descriptions-item>
          <el-descriptions-item label="课程名称">{{ selectedCourse.course_name }}</el-descriptions-item>
          <el-descriptions-item label="学分">{{ selectedCourse.credits }}</el-descriptions-item>
          <el-descriptions-item label="学时">{{ selectedCourse.hours }}</el-descriptions-item>
          <el-descriptions-item label="课程类型">
            <el-tag :type="getCourseTypeTag(selectedCourse.course_type)">
              {{ getCourseTypeText(selectedCourse.course_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="授课教师">{{ selectedCourse.teacher_name }}</el-descriptions-item>
          <el-descriptions-item label="教师工号">{{ selectedCourse.teacher_id }}</el-descriptions-item>
          <el-descriptions-item label="院系">{{ selectedCourse.department }}</el-descriptions-item>
          <el-descriptions-item label="学期">{{ selectedCourse.semester }}</el-descriptions-item>
          <el-descriptions-item label="上课时间">{{ selectedCourse.schedule }}</el-descriptions-item>
          <el-descriptions-item label="上课地点">{{ selectedCourse.location }}</el-descriptions-item>
          <el-descriptions-item label="最大人数">{{ selectedCourse.max_students }}</el-descriptions-item>
          <el-descriptions-item label="当前人数">{{ selectedCourse.current_students }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedCourse.status)">
              {{ getStatusText(selectedCourse.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="课程描述" :span="2">{{ selectedCourse.description }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 批量导入组件 -->
    <CourseImport
      v-model="importVisible"
      @success="handleImportSuccess"
      @error="handleImportError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api/simple'
import { exportCourses } from '@/utils/exportExcel'
import CourseImport from '@/components/CourseImport.vue'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const importVisible = ref(false)
const isEdit = ref(false)

// 搜索和筛选
const searchQuery = ref('')
const filterSemester = ref('')
const filterDepartment = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 表单数据
const courseFormRef = ref()
const courseForm = reactive({
  course_code: '',
  course_name: '',
  credits: 3,
  hours: 48,
  course_type: '',
  teacher_name: '',
  teacher_id: '',
  department: '',
  semester: '',
  max_students: 50,
  current_students: 0,
  status: 'active',
  schedule: '',
  location: '',
  description: ''
})

// 课程列表
const courses = ref([])
const selectedCourses = ref([])
const selectedCourse = ref(null)

// 搜索超时
let searchTimeout = null

// 表单验证规则
const formRules = {
  course_code: [
    { required: true, message: '请输入课程代码', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9]+$/, message: '课程代码只能包含字母和数字', trigger: 'blur' }
  ],
  course_name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' },
    { min: 2, max: 50, message: '课程名称长度在2到50个字符', trigger: 'blur' }
  ],
  credits: [
    { required: true, message: '请输入学分', trigger: 'change' },
    { type: 'number', min: 1, max: 10, message: '学分在1到10之间', trigger: 'change' }
  ],
  hours: [
    { required: true, message: '请输入学时', trigger: 'change' },
    { type: 'number', min: 1, max: 200, message: '学时在1到200之间', trigger: 'change' }
  ],
  course_type: [
    { required: true, message: '请选择课程类型', trigger: 'change' }
  ],
  teacher_name: [
    { required: true, message: '请输入授课教师姓名', trigger: 'blur' }
  ],
  teacher_id: [
    { required: true, message: '请输入教师工号', trigger: 'blur' }
  ],
  department: [
    { required: true, message: '请选择院系', trigger: 'change' }
  ],
  semester: [
    { required: true, message: '请选择学期', trigger: 'change' }
  ],
  max_students: [
    { required: true, message: '请输入最大人数', trigger: 'change' },
    { type: 'number', min: 1, max: 500, message: '最大人数在1到500之间', trigger: 'change' }
  ],
  current_students: [
    { type: 'number', min: 0, message: '当前人数不能为负数', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 全局课程数据存储 - 与后端保持一致
let globalCourses = [
  {
    id: 1,
    course_code: 'CS101',
    course_name: '计算机科学导论',
    credits: 3,
    hours: 48,
    course_type: 'required',
    teacher_name: '张教授',
    teacher_id: 'T0001',
    department: '计算机科学系',
    semester: '2025-春季',
    max_students: 50,
    current_students: 25,
    status: 'active',
    schedule: '周一 14:00-16:00',
    location: '教学楼A201',
    description: '计算机科学基础课程，涵盖计算机基本概念、编程入门等内容。',
    created_at: '2025-01-01T00:00:00'
  },
  {
    id: 2,
    course_code: 'SE201',
    course_name: '软件工程',
    credits: 4,
    hours: 64,
    course_type: 'required',
    teacher_name: '李副教授',
    teacher_id: 'T0002',
    department: '软件工程系',
    semester: '2025-春季',
    max_students: 40,
    current_students: 38,
    status: 'active',
    schedule: '周二、周四 10:00-12:00',
    location: '实验楼B305',
    description: '软件工程理论与实践，包括软件开发生命周期、项目管理等内容。',
    created_at: '2025-01-01T00:00:00'
  },
  {
    id: 3,
    course_code: 'DS301',
    course_name: '数据结构与算法',
    credits: 4,
    hours: 64,
    course_type: 'required',
    teacher_name: '王讲师',
    teacher_id: 'T0003',
    department: '数据科学系',
    semester: '2025-春季',
    max_students: 35,
    current_students: 30,
    status: 'active',
    schedule: '周三、周五 14:00-16:00',
    location: '教学楼C102',
    description: '深入学习数据结构和算法，包括排序、搜索、图算法等。',
    created_at: '2025-01-01T00:00:00'
  },
  {
    id: 4,
    course_code: 'AI401',
    course_name: '人工智能导论',
    credits: 3,
    hours: 48,
    course_type: 'elective',
    teacher_name: '刘教授',
    teacher_id: 'T0005',
    department: '数学系',
    semester: '2024-秋季',
    max_students: 30,
    current_students: 15,
    status: 'active',
    schedule: '周一 18:00-20:00',
    location: '教学楼D203',
    description: '人工智能基础概念，包括机器学习、深度学习、自然语言处理等。',
    created_at: '2024-09-01T00:00:00'
  },
  {
    id: 5,
    course_code: 'DB201',
    course_name: '数据库系统',
    credits: 3,
    hours: 48,
    course_type: 'required',
    teacher_name: '陈助教',
    teacher_id: 'T0004',
    department: '电子工程系',
    semester: '2024-秋季',
    max_students: 40,
    current_students: 40,
    status: 'full',
    schedule: '周二、周四 14:00-16:00',
    location: '实验楼E401',
    description: '关系型数据库设计、SQL语言、NoSQL数据库等内容。',
    created_at: '2024-09-01T00:00:00'
  },
  {
    id: 6,
    course_code: 'ML501',
    course_name: '机器学习',
    credits: 4,
    hours: 64,
    course_type: 'elective',
    teacher_name: '赵副教授',
    teacher_id: 'T0006',
    department: '物理系',
    semester: '2024-夏季',
    max_students: 25,
    current_students: 18,
    status: 'suspended',
    schedule: '周一、周三、周五 16:00-18:00',
    location: '教学楼F101',
    description: '机器学习算法原理与实践，包括监督学习、无监督学习等。',
    created_at: '2024-06-01T00:00:00'
  }
]

// 获取模拟数据
const getMockCourses = () => {
  let filteredData = [...globalCourses]

  // 根据搜索条件过滤
  if (searchQuery.value) {
    filteredData = filteredData.filter(course =>
      course.course_name.includes(searchQuery.value) ||
      course.course_code.includes(searchQuery.value) ||
      course.teacher_name.includes(searchQuery.value) ||
      course.department.includes(searchQuery.value)
    )
  }

  // 根据学期过滤
  if (filterSemester.value) {
    filteredData = filteredData.filter(course => course.semester === filterSemester.value)
  }

  // 根据院系过滤
  if (filterDepartment.value) {
    filteredData = filteredData.filter(course => course.department === filterDepartment.value)
  }

  // 按创建时间排序（最新的在前面）
  filteredData.sort((a, b) => b.id - a.id)

  return filteredData
}

// 更新全局课程数据的函数
const updateGlobalCourses = (newCourses) => {
  globalCourses = [...newCourses]
}

// 数据加载方法
const loadCourses = async () => {
  loading.value = true

  try {
    // 优先尝试从后端API加载数据
    try {
      const response = await api.getCourses({
        page: currentPage.value,
        pageSize: pageSize.value,
        keyword: searchQuery.value,
        semester: filterSemester.value,
        department: filterDepartment.value
      })

      if (response.success && response.data && response.data.courses) {
        courses.value = response.data.courses
        total.value = response.data.total
        console.log('从后端API加载了', courses.value.length, '门课程数据')
        return
      }
    } catch (apiError) {
      console.log('从API加载数据失败，使用本地数据:', apiError.message)
    }

    // API失败时使用本地数据
    const mockData = getMockCourses()
    courses.value = mockData
    total.value = mockData.length
    console.log('从本地存储加载了', courses.value.length, '门课程数据')

  } catch (error) {
    console.error('加载课程数据失败:', error)
    courses.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout.value = setTimeout(() => {
    currentPage.value = 1
    loadCourses()
  }, 300)
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  loadCourses()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadCourses()
}

// 选择处理
const handleSelectionChange = (selection) => {
  selectedCourses.value = selection
}

// 状态相关方法
const getStatusType = (status) => {
  const statusMap = {
    active: 'success',
    full: 'warning',
    suspended: 'info',
    completed: 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    active: '正常',
    full: '已满',
    suspended: '暂停',
    completed: '已结束'
  }
  return statusMap[status] || '未知'
}

const getCourseTypeTag = (type) => {
  const typeMap = {
    required: '',
    elective: 'warning',
    lab: 'success',
    seminar: 'danger'
  }
  return typeMap[type] || ''
}

const getCourseTypeText = (type) => {
  const typeMap = {
    required: '必修课',
    elective: '选修课',
    lab: '实验课',
    seminar: '研讨课'
  }
  return typeMap[type] || '未知'
}

const getEnrollmentPercentage = (course) => {
  if (!course.max_students || course.max_students === 0) return 0
  return Math.round((course.current_students / course.max_students) * 100)
}

const getEnrollmentColor = (course) => {
  const percentage = getEnrollmentPercentage(course)
  if (percentage >= 90) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
}

// 添加课程
const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑课程
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(courseForm, row)
  dialogVisible.value = true
}

// 查看课程详情
const handleView = (row) => {
  selectedCourse.value = row
  detailVisible.value = true
}

// 删除课程
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除课程 "${row.course_name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      // 优先调用API删除
      try {
        await api.deleteCourse(row.id)
        ElMessage.success('删除成功')
      } catch (apiError) {
        console.log('API删除失败，使用本地删除:', apiError.message)

        // 从全局数据中删除
        const index = globalCourses.findIndex(c => c.id === row.id)
        if (index !== -1) {
          globalCourses.splice(index, 1)
          updateGlobalCourses(globalCourses)
        }
      }

      await loadCourses()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 表单提交处理
const handleSubmit = async () => {
  if (!courseFormRef.value) return

  try {
    await courseFormRef.value.validate()
    submitting.value = true

    // 验证选课人数
    if (courseForm.current_students > courseForm.max_students) {
      ElMessage.error('当前人数不能超过最大人数')
      return
    }

    // 生成新的课程数据
    const newCourse = {
      course_code: courseForm.course_code,
      course_name: courseForm.course_name,
      credits: courseForm.credits,
      hours: courseForm.hours,
      course_type: courseForm.course_type,
      teacher_name: courseForm.teacher_name,
      teacher_id: courseForm.teacher_id,
      department: courseForm.department,
      semester: courseForm.semester,
      max_students: courseForm.max_students,
      current_students: courseForm.current_students,
      status: courseForm.status,
      schedule: courseForm.schedule,
      location: courseForm.location,
      description: courseForm.description
    }

    // 优先调用后端API
    try {
      let response
      if (isEdit.value) {
        response = await api.updateCourse(courseForm.id, newCourse)
      } else {
        response = await api.createCourse(newCourse)
      }

      if (response.success) {
        ElMessage.success(response.message || (isEdit.value ? '更新成功' : '创建成功'))
        dialogVisible.value = false
        await loadCourses() // 重新加载数据
      } else {
        throw new Error(response.message || '操作失败')
      }
    } catch (apiError) {
      console.error('API调用失败:', apiError)

      // API失败时回退到前端存储
      if (isEdit.value) {
        // 更新现有课程
        const index = globalCourses.findIndex(c => c.id === courseForm.id)
        if (index !== -1) {
          globalCourses[index] = { ...globalCourses[index], ...newCourse, id: courseForm.id }
          updateGlobalCourses(globalCourses)
          ElMessage.success('更新成功（前端存储）')
        } else {
          ElMessage.error('未找到要更新的课程')
        }
      } else {
        // 添加新课程到全局数据
        const frontEndCourse = { ...newCourse, id: Date.now() }
        globalCourses.unshift(frontEndCourse)
        updateGlobalCourses(globalCourses)
        ElMessage.success('创建成功（前端存储）')
      }

      dialogVisible.value = false
      ElMessage.info('数据已保存，后端服务未连接')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败: ' + (error.message || '未知错误'))
  } finally {
    submitting.value = false
  }
}

// 对话框关闭处理
const handleDialogClose = () => {
  dialogVisible.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  if (courseFormRef.value) {
    courseFormRef.value.resetFields()
  }
  Object.assign(courseForm, {
    course_code: '',
    course_name: '',
    credits: 3,
    hours: 48,
    course_type: '',
    teacher_name: '',
    teacher_id: '',
    department: '',
    semester: '',
    max_students: 50,
    current_students: 0,
    status: 'active',
    schedule: '',
    location: '',
    description: ''
  })
}

// 导入处理
const handleImport = () => {
  importVisible.value = true
}

const handleImportSuccess = (importedCourses) => {
  try {
    // 添加到全局数据
    importedCourses.forEach(course => {
      course.id = Date.now() + Math.random()
      globalCourses.unshift(course)
    })
    updateGlobalCourses(globalCourses)

    ElMessage.success(`成功导入 ${importedCourses.length} 门课程`)
    loadCourses()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  }
}

const handleImportError = (error) => {
  ElMessage.error(`导入失败: ${error.message}`)
}

// 导出处理
const handleExport = () => {
  try {
    const dataToExport = selectedCourses.value.length > 0 ? selectedCourses.value : courses.value
    exportCourses(dataToExport)
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.course-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-section {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table-section {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination-wrapper {
  padding: 20px;
  text-align: right;
}

.course-detail {
  padding: 20px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .filter-section .el-row {
    flex-direction: column;
  }

  .filter-section .el-col {
    width: 100% !important;
    margin-bottom: 10px;
  }
}
</style>