<template>
  <div class="student-management">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索学号、姓名、专业..."
          @input="handleSearch"
          clearable
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="action-buttons">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加学生
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button type="danger" :disabled="!selectedStudents.length" @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </div>
    </div>

    <!-- 学生列表表格 -->
    <el-card class="table-card">
      <el-table
        :data="students"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        style="width: 100%"
        empty-text="暂无数据"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="student_id" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.gender === '男' ? 'primary' : 'success'" size="small">
              {{ row.gender }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="birth_date" label="出生日期" width="120" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip />
        <el-table-column prop="major" label="专业" width="150" />
        <el-table-column prop="class_name" label="班级" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enrollment_date" label="入学时间" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="warning" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
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
    </el-card>

    <!-- 学生表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :before-close="handleCloseDialog"
    >
      <el-form
        ref="studentFormRef"
        :model="studentForm"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学号" prop="student_id">
              <el-input v-model="studentForm.student_id" :disabled="isEdit" placeholder="请输入学号，如：S2024001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="studentForm.name" placeholder="请输入学生姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 用户账户信息 -->
        <el-divider content-position="left">登录信息（首次创建需要）</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="studentForm.username" placeholder="用于登录的用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="初始密码" prop="password">
              <el-input v-model="studentForm.password" type="password" placeholder="登录密码" show-password />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="studentForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="studentForm.birth_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input v-model="studentForm.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="studentForm.email" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-select v-model="studentForm.major" placeholder="选择专业" style="width: 100%">
                <el-option label="计算机科学" value="计算机科学" />
                <el-option label="软件工程" value="软件工程" />
                <el-option label="电子信息工程" value="电子信息工程" />
                <el-option label="机械工程" value="机械工程" />
                <el-option label="土木工程" value="土木工程" />
                <el-option label="经济学" value="经济学" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="班级" prop="class_name">
              <el-input v-model="studentForm.class_name" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="studentForm.status" style="width: 100%">
                <el-option label="在读" value="active" />
                <el-option label="休学" value="suspend" />
                <el-option label="毕业" value="graduated" />
                <el-option label="退学" value="dropped" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入学时间" prop="enrollment_date">
              <el-date-picker
                v-model="studentForm.enrollment_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="家庭地址" prop="address">
          <el-input v-model="studentForm.address" type="textarea" :rows="2" />
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

    <!-- 学生详情对话框 -->
    <el-dialog v-model="detailVisible" title="学生详情" width="800px">
      <div v-if="selectedStudent" class="student-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学号">{{ selectedStudent.student_id }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ selectedStudent.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ selectedStudent.gender }}</el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ selectedStudent.birth_date }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ selectedStudent.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedStudent.email }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ selectedStudent.major }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ selectedStudent.class_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedStudent.status)">
              {{ getStatusText(selectedStudent.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="入学时间">{{ selectedStudent.enrollment_date }}</el-descriptions-item>
          <el-descriptions-item label="家庭地址" :span="2">{{ selectedStudent.address }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <StudentImport
      v-model="importDialogVisible"
      @success="handleImportSuccess"
      @error="handleImportError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api/simple'
import { exportStudents } from '@/utils/exportExcel'
import StudentImport from '@/components/StudentImport.vue'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const importDialogVisible = ref(false)
const students = ref([])
const selectedStudents = ref([])
const selectedStudent = ref(null)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 搜索相关
const searchQuery = ref('')
const searchTimeout = ref(null)

// 表单相关
const studentFormRef = ref(null)
const isEdit = ref(false)
const studentForm = reactive({
  student_id: '',
  name: '',
  username: '',
  password: '',
  gender: '男',
  birth_date: '',
  phone: '',
  email: '',
  major: '',
  class_name: '',
  status: 'active',
  enrollment_date: '',
  address: ''
})

// 表单验证规则
const formRules = {
  student_id: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9]+$/, message: '学号只能包含字母和数字', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2到20个字符', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  password: [
    { required: !isEdit.value, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  birth_date: [
    { required: true, message: '请选择出生日期', trigger: 'change' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  major: [
    { required: true, message: '请选择专业', trigger: 'change' }
  ],
  class_name: [
    { required: true, message: '请输入班级', trigger: 'blur' }
  ],
  enrollment_date: [
    { required: true, message: '请选择入学时间', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => {
  return isEdit.value ? '编辑学生' : '添加学生'
})

// 状态相关方法
const getStatusType = (status: string) => {
  const statusMap = {
    active: 'success',
    suspend: 'warning',
    graduated: 'info',
    dropped: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '在读',
    suspend: '休学',
    graduated: '毕业',
    dropped: '退学'
  }
  return statusMap[status] || '未知'
}

// 数据加载方法
const loadStudents = async () => {
  loading.value = true

  try {
    // 优先尝试从后端API加载数据
    try {
      const response = await api.getStudents({
        page: currentPage.value,
        pageSize: pageSize.value,
        keyword: searchQuery.value
      })

      if (response.success && response.data && response.data.students) {
        students.value = response.data.students
        total.value = response.data.total
        console.log('从后端API加载了', students.value.length, '名学生数据')
        return
      }
    } catch (apiError) {
      console.log('从API加载数据失败，使用本地数据:', apiError.message)
    }

    // API失败时使用本地数据
    students.value = getMockStudents()
    total.value = students.value.length
    console.log('从本地存储加载了', students.value.length, '名学生数据')

  } catch (error) {
    console.error('加载学生数据失败:', error)
    students.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 全局学生数据存储
let globalStudents = [
  {
    id: 1,
    student_id: 'S2021001',
    name: '张三',
    username: 'zhangsan',
    password: 'password123',
    gender: '男',
    birth_date: '2000-01-01',
    phone: '13800138001',
    email: 'zhangsan@example.com',
    major: '计算机科学',
    class_name: '计算机科学1班',
    status: 'active',
    enrollment_date: '2021-09-01',
    address: '北京市海淀区中关村大街1号',
    created_at: '2021-09-01T00:00:00'
  },
  {
    id: 2,
    student_id: 'S2021002',
    name: '李四',
    username: 'lisi',
    password: 'password123',
    gender: '女',
    birth_date: '2000-03-15',
    phone: '13800138002',
    email: 'lisi@example.com',
    major: '计算机科学',
    class_name: '计算机科学1班',
    status: 'active',
    enrollment_date: '2021-09-01',
    address: '上海市浦东新区世纪大道100号',
    created_at: '2021-09-01T00:00:00'
  },
  {
    id: 3,
    student_id: 'S2021003',
    name: '王五',
    username: 'wangwu',
    password: 'password123',
    gender: '男',
    birth_date: '2000-05-20',
    phone: '13800138003',
    email: 'wangwu@example.com',
    major: '软件工程',
    class_name: '软件工程2班',
    status: 'active',
    enrollment_date: '2021-09-01',
    address: '广州市天河区珠江新城核心区',
    created_at: '2021-09-01T00:00:00'
  },
  {
    id: 4,
    student_id: 'S2021004',
    name: '赵六',
    username: 'zhaoliu',
    password: 'password123',
    gender: '女',
    birth_date: '2000-07-08',
    phone: '13800138004',
    email: 'zhaoliu@example.com',
    major: '软件工程',
    class_name: '软件工程2班',
    status: 'active',
    enrollment_date: '2021-09-01',
    address: '深圳市南山区科技园南区',
    created_at: '2021-09-01T00:00:00'
  },
  {
    id: 5,
    student_id: 'S2021005',
    name: '陈七',
    username: 'chenqi',
    password: 'password123',
    gender: '男',
    birth_date: '2000-09-12',
    phone: '13800138005',
    email: 'chenqi@example.com',
    major: '数据科学',
    class_name: '数据科学1班',
    status: 'active',
    enrollment_date: '2021-09-01',
    address: '成都市高新区天府大道',
    created_at: '2021-09-01T00:00:00'
  },
  {
    id: 6,
    student_id: 'S2021006',
    name: '刘八',
    username: 'liuba',
    password: 'password123',
    gender: '女',
    birth_date: '2000-11-25',
    phone: '13800138006',
    email: 'liuba@example.com',
    major: '数据科学',
    class_name: '数据科学1班',
    status: 'active',
    enrollment_date: '2021-09-01',
    address: '杭州市西湖区文三路',
    created_at: '2021-09-01T00:00:00'
  }
]

// 获取模拟数据
const getMockStudents = () => {
  let filteredData = [...globalStudents]

  // 根据搜索条件过滤
  if (searchQuery.value) {
    filteredData = filteredData.filter(student =>
      student.name.includes(searchQuery.value) ||
      student.student_id.includes(searchQuery.value) ||
      student.major.includes(searchQuery.value) ||
      student.username.includes(searchQuery.value)
    )
  }

  // 按创建时间排序（最新的在前面）
  filteredData.sort((a, b) => b.id - a.id)

  return filteredData
}

// 更新全局学生数据的函数
const updateGlobalStudents = (newStudents) => {
  globalStudents = [...newStudents]
}

// 搜索处理
const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    currentPage.value = 1
    loadStudents()
  }, 500)
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadStudents()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadStudents()
}

// 表格选择处理
const handleSelectionChange = (selection: any[]) => {
  selectedStudents.value = selection
}

// 操作按钮处理
const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  Object.assign(studentForm, row)
  dialogVisible.value = true
}

const handleView = (row: any) => {
  selectedStudent.value = row
  detailVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学生"${row.name}"吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 从全局数据中删除
    const index = globalStudents.findIndex(s => s.id === row.id)
    if (index !== -1) {
      globalStudents.splice(index, 1)
      updateGlobalStudents(globalStudents)
    }

    // 尝试调用API删除
    try {
      await api.deleteStudent(row.id)
      console.log('API删除成功')
    } catch (error) {
      console.log('API删除失败，仅从全局数据中删除:', error.message)
    }

    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的${selectedStudents.value.length}名学生吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 批量删除逻辑
    ElMessage.success('批量删除成功 (演示模式)')
    selectedStudents.value = []
    loadStudents()
  } catch {
    // 用户取消
  }
}

const handleImport = () => {
  // 显示导入对话框
  importDialogVisible.value = true
}

const handleExport = () => {
  // 导出当前筛选的学生数据
  if (students.value.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }

  exportStudents(students.value)
}

// 表单提交处理
const handleSubmit = async () => {
  if (!studentFormRef.value) return

  try {
    await studentFormRef.value.validate()
    submitting.value = true

    // 生成新的学生数据
    const newStudent = {
      student_id: studentForm.student_id,
      name: studentForm.name,
      username: studentForm.username,
      password: studentForm.password, // 包含密码字段
      gender: studentForm.gender,
      birth_date: studentForm.birth_date ? new Date(studentForm.birth_date).toISOString().split('T')[0] : '',
      phone: studentForm.phone,
      email: studentForm.email,
      major: studentForm.major,
      class_name: studentForm.class_name,
      status: studentForm.status,
      enrollment_date: studentForm.enrollment_date ? new Date(studentForm.enrollment_date).toISOString().split('T')[0] : '',
      address: studentForm.address
    }

    // 优先调用后端API
    try {
      let response
      if (isEdit.value) {
        response = await api.updateStudent(studentForm.id, newStudent)
      } else {
        response = await api.createStudent(newStudent)
      }

      if (response.success) {
        ElMessage.success(response.message || (isEdit.value ? '更新成功' : '创建成功'))
        dialogVisible.value = false
        await loadStudents() // 重新加载数据
      } else {
        throw new Error(response.message || '操作失败')
      }
    } catch (apiError) {
      console.error('API调用失败:', apiError)

      // API失败时回退到前端存储
      if (isEdit.value) {
        // 更新现有学生
        const index = globalStudents.findIndex(s => s.id === studentForm.id)
        if (index !== -1) {
          globalStudents[index] = { ...globalStudents[index], ...newStudent, id: studentForm.id }
          updateGlobalStudents(globalStudents)
          ElMessage.success('更新成功（前端存储）')
        } else {
          ElMessage.error('未找到要更新的学生')
        }
      } else {
        // 添加新学生到全局数据
        const frontEndStudent = { ...newStudent, id: Date.now() }
        globalStudents.unshift(frontEndStudent)
        updateGlobalStudents(globalStudents)
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
const handleCloseDialog = () => {
  dialogVisible.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  if (studentFormRef.value) {
    studentFormRef.value.resetFields()
  }
  Object.assign(studentForm, {
    student_id: '',
    name: '',
    username: '',
    password: '',
    gender: '男',
    birth_date: '',
    phone: '',
    email: '',
    major: '',
    class_name: '',
    status: 'active',
    enrollment_date: '',
    address: ''
  })
}

// 导入成功处理
const handleImportSuccess = (importedStudents: any[]) => {
  ElMessage.success(`成功导入 ${importedStudents.length} 名学生`)
  importDialogVisible.value = false
  loadStudents()
}

// 导入失败处理
const handleImportError = (error: any) => {
  console.error('导入失败:', error)
  ElMessage.error('导入失败，请检查文件格式')
}

// 组件挂载
onMounted(() => {
  loadStudents()
})
</script>

<style scoped>
.student-management {
  padding: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.table-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.student-detail {
  padding: 20px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolbar {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .search-bar {
    justify-content: center;
  }

  .action-buttons {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>