<template>
  <div class="teacher-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>教师管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加教师
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
            placeholder="搜索姓名、工号、专业"
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterDepartment" placeholder="选择院系" clearable>
            <el-option label="全部院系" value="" />
            <el-option label="计算机科学系" value="计算机科学系" />
            <el-option label="软件工程系" value="软件工程系" />
            <el-option label="数据科学系" value="数据科学系" />
            <el-option label="电子工程系" value="电子工程系" />
            <el-option label="数学系" value="数学系" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterTitle" placeholder="选择职称" clearable>
            <el-option label="全部职称" value="" />
            <el-option label="教授" value="教授" />
            <el-option label="副教授" value="副教授" />
            <el-option label="讲师" value="讲师" />
            <el-option label="助教" value="助教" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button @click="handleSearch">搜索</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 教师列表 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="teachers"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="teacher_id" label="工号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="department" label="院系" width="120" />
        <el-table-column prop="title" label="职称" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" />
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

    <!-- 添加/编辑教师对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑教师' : '添加教师'"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="teacherFormRef"
        :model="teacherForm"
        :rules="formRules"
        label-width="100px"
        size="default"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工号" prop="teacher_id">
              <el-input
                v-model="teacherForm.teacher_id"
                placeholder="请输入工号"
                :disabled="isEdit"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="teacherForm.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="teacherForm.username" placeholder="请输入用户名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="teacherForm.password"
                type="password"
                placeholder="请输入密码"
                show-password
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="teacherForm.gender" placeholder="请选择性别">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="teacherForm.birth_date"
                type="date"
                placeholder="选择出生日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="teacherForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="teacherForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="院系" prop="department">
              <el-select v-model="teacherForm.department" placeholder="请选择院系">
                <el-option label="计算机科学系" value="计算机科学系" />
                <el-option label="软件工程系" value="软件工程系" />
                <el-option label="数据科学系" value="数据科学系" />
                <el-option label="电子工程系" value="电子工程系" />
                <el-option label="数学系" value="数学系" />
                <el-option label="物理系" value="物理系" />
                <el-option label="化学系" value="化学系" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="title">
              <el-select v-model="teacherForm.title" placeholder="请选择职称">
                <el-option label="教授" value="教授" />
                <el-option label="副教授" value="副教授" />
                <el-option label="讲师" value="讲师" />
                <el-option label="助教" value="助教" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入职时间" prop="hire_date">
              <el-date-picker
                v-model="teacherForm.hire_date"
                type="date"
                placeholder="选择入职时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="teacherForm.status" placeholder="请选择状态">
                <el-option label="在职" value="active" />
                <el-option label="离职" value="inactive" />
                <el-option label="休假" value="leave" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="家庭地址" prop="address">
          <el-input
            v-model="teacherForm.address"
            type="textarea"
            :rows="2"
            placeholder="请输入家庭地址"
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

    <!-- 教师详情对话框 -->
    <el-dialog v-model="detailVisible" title="教师详情" width="800px">
      <div v-if="selectedTeacher" class="teacher-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="工号">{{ selectedTeacher.teacher_id }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ selectedTeacher.name }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ selectedTeacher.gender }}</el-descriptions-item>
          <el-descriptions-item label="出生日期">{{ selectedTeacher.birth_date }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ selectedTeacher.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedTeacher.email }}</el-descriptions-item>
          <el-descriptions-item label="院系">{{ selectedTeacher.department }}</el-descriptions-item>
          <el-descriptions-item label="职称">{{ selectedTeacher.title }}</el-descriptions-item>
          <el-descriptions-item label="入职时间">{{ selectedTeacher.hire_date }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTeacher.status)">
              {{ getStatusText(selectedTeacher.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="家庭地址" :span="2">{{ selectedTeacher.address }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 批量导入组件 -->
    <TeacherImport
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
import { exportTeachers } from '@/utils/exportExcel'
import TeacherImport from '@/components/TeacherImport.vue'

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const importVisible = ref(false)
const isEdit = ref(false)

// 搜索和筛选
const searchQuery = ref('')
const filterDepartment = ref('')
const filterTitle = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 表单数据
const teacherFormRef = ref()
const teacherForm = reactive({
  teacher_id: '',
  name: '',
  username: '',
  password: '',
  gender: '',
  birth_date: '',
  phone: '',
  email: '',
  department: '',
  title: '',
  hire_date: '',
  address: '',
  status: 'active'
})

// 教师列表
const teachers = ref([])
const selectedTeachers = ref([])
const selectedTeacher = ref(null)

// 搜索超时
let searchTimeout = null

// 表单验证规则
const formRules = {
  teacher_id: [
    { required: true, message: '请输入工号', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9]+$/, message: '工号只能包含字母和数字', trigger: 'blur' }
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
  department: [
    { required: true, message: '请选择院系', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请选择职称', trigger: 'change' }
  ],
  hire_date: [
    { required: true, message: '请选择入职时间', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 全局教师数据存储 - 与后端保持一致
let globalTeachers = [
  {
    id: 1,
    teacher_id: 'T0001',
    name: '张教授',
    username: 'zhangprof',
    password: 'password123',
    gender: '男',
    birth_date: '1975-03-15',
    phone: '13900001001',
    email: 'zhang.prof@university.edu.cn',
    department: '计算机科学系',
    title: '教授',
    hire_date: '2000-09-01',
    address: '北京市海淀区清华大学',
    status: 'active',
    created_at: '2000-09-01T00:00:00'
  },
  {
    id: 2,
    teacher_id: 'T0002',
    name: '李副教授',
    username: 'liprof',
    password: 'password123',
    gender: '女',
    birth_date: '1980-06-20',
    phone: '13900001002',
    email: 'li.prof@university.edu.cn',
    department: '软件工程系',
    title: '副教授',
    hire_date: '2005-03-01',
    address: '上海市闵行区上海交通大学',
    status: 'active',
    created_at: '2005-03-01T00:00:00'
  },
  {
    id: 3,
    teacher_id: 'T0003',
    name: '王讲师',
    username: 'wanglec',
    password: 'password123',
    gender: '男',
    birth_date: '1985-09-10',
    phone: '13900001003',
    email: 'wang.lec@university.edu.cn',
    department: '数据科学系',
    title: '讲师',
    hire_date: '2010-09-01',
    address: '广州市番禺区中山大学',
    status: 'active',
    created_at: '2010-09-01T00:00:00'
  },
  {
    id: 4,
    teacher_id: 'T0004',
    name: '陈助教',
    username: 'chenassist',
    password: 'password123',
    gender: '女',
    birth_date: '1990-12-05',
    phone: '13900001004',
    email: 'chen.assist@university.edu.cn',
    department: '电子工程系',
    title: '助教',
    hire_date: '2018-03-01',
    address: '深圳市南山区深圳大学',
    status: 'active',
    created_at: '2018-03-01T00:00:00'
  },
  {
    id: 5,
    teacher_id: 'T0005',
    name: '刘教授',
    username: 'liuprof',
    password: 'password123',
    gender: '男',
    birth_date: '1972-04-25',
    phone: '13900001005',
    email: 'liu.prof@university.edu.cn',
    department: '数学系',
    title: '教授',
    hire_date: '1998-09-01',
    address: '杭州市西湖区浙江大学',
    status: 'active',
    created_at: '1998-09-01T00:00:00'
  },
  {
    id: 6,
    teacher_id: 'T0006',
    name: '赵副教授',
    username: 'zhaoprof',
    password: 'password123',
    gender: '女',
    birth_date: '1978-07-18',
    phone: '13900001006',
    email: 'zhao.prof@university.edu.cn',
    department: '物理系',
    title: '副教授',
    hire_date: '2003-09-01',
    address: '武汉市洪山区武汉大学',
    status: 'active',
    created_at: '2003-09-01T00:00:00'
  }
]

// 获取模拟数据
const getMockTeachers = () => {
  let filteredData = [...globalTeachers]

  // 根据搜索条件过滤
  if (searchQuery.value) {
    filteredData = filteredData.filter(teacher =>
      teacher.name.includes(searchQuery.value) ||
      teacher.teacher_id.includes(searchQuery.value) ||
      teacher.department.includes(searchQuery.value) ||
      teacher.username.includes(searchQuery.value)
    )
  }

  // 根据院系过滤
  if (filterDepartment.value) {
    filteredData = filteredData.filter(teacher => teacher.department === filterDepartment.value)
  }

  // 根据职称过滤
  if (filterTitle.value) {
    filteredData = filteredData.filter(teacher => teacher.title === filterTitle.value)
  }

  // 按创建时间排序（最新的在前面）
  filteredData.sort((a, b) => b.id - a.id)

  return filteredData
}

// 更新全局教师数据的函数
const updateGlobalTeachers = (newTeachers) => {
  globalTeachers = [...newTeachers]
}

// 数据加载方法
const loadTeachers = async () => {
  loading.value = true

  try {
    // 优先尝试从后端API加载数据
    try {
      const response = await api.getTeachers({
        page: currentPage.value,
        pageSize: pageSize.value,
        keyword: searchQuery.value,
        department: filterDepartment.value,
        title: filterTitle.value
      })

      if (response.success && response.data && response.data.teachers) {
        teachers.value = response.data.teachers
        total.value = response.data.total
        console.log('从后端API加载了', teachers.value.length, '名教师数据')
        return
      }
    } catch (apiError) {
      console.log('从API加载数据失败，使用本地数据:', apiError.message)
    }

    // API失败时使用本地数据
    const mockData = getMockTeachers()
    teachers.value = mockData
    total.value = mockData.length
    console.log('从本地存储加载了', teachers.value.length, '名教师数据')

  } catch (error) {
    console.error('加载教师数据失败:', error)
    teachers.value = []
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
    loadTeachers()
  }, 300)
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  loadTeachers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadTeachers()
}

// 选择处理
const handleSelectionChange = (selection) => {
  selectedTeachers.value = selection
}

// 状态相关方法
const getStatusType = (status) => {
  const statusMap = {
    active: 'success',
    inactive: 'danger',
    leave: 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    active: '在职',
    inactive: '离职',
    leave: '休假'
  }
  return statusMap[status] || '未知'
}

// 添加教师
const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑教师
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(teacherForm, row)
  dialogVisible.value = true
}

// 查看教师详情
const handleView = (row) => {
  selectedTeacher.value = row
  detailVisible.value = true
}

// 删除教师
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除教师 "${row.name}" 吗？`,
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
        await api.deleteTeacher(row.id)
        ElMessage.success('删除成功')
      } catch (apiError) {
        console.log('API删除失败，使用本地删除:', apiError.message)

        // 从全局数据中删除
        const index = globalTeachers.findIndex(t => t.id === row.id)
        if (index !== -1) {
          globalTeachers.splice(index, 1)
          updateGlobalTeachers(globalTeachers)
        }
      }

      await loadTeachers()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 表单提交处理
const handleSubmit = async () => {
  if (!teacherFormRef.value) return

  try {
    await teacherFormRef.value.validate()
    submitting.value = true

    // 生成新的教师数据
    const newTeacher = {
      teacher_id: teacherForm.teacher_id,
      name: teacherForm.name,
      username: teacherForm.username,
      password: teacherForm.password,
      gender: teacherForm.gender,
      birth_date: teacherForm.birth_date ? new Date(teacherForm.birth_date).toISOString().split('T')[0] : '',
      phone: teacherForm.phone,
      email: teacherForm.email,
      department: teacherForm.department,
      title: teacherForm.title,
      hire_date: teacherForm.hire_date ? new Date(teacherForm.hire_date).toISOString().split('T')[0] : '',
      address: teacherForm.address,
      status: teacherForm.status
    }

    // 优先调用后端API
    try {
      let response
      if (isEdit.value) {
        response = await api.updateTeacher(teacherForm.id, newTeacher)
      } else {
        response = await api.createTeacher(newTeacher)
      }

      if (response.success) {
        ElMessage.success(response.message || (isEdit.value ? '更新成功' : '创建成功'))
        dialogVisible.value = false
        await loadTeachers() // 重新加载数据
      } else {
        throw new Error(response.message || '操作失败')
      }
    } catch (apiError) {
      console.error('API调用失败:', apiError)

      // API失败时回退到前端存储
      if (isEdit.value) {
        // 更新现有教师
        const index = globalTeachers.findIndex(t => t.id === teacherForm.id)
        if (index !== -1) {
          globalTeachers[index] = { ...globalTeachers[index], ...newTeacher, id: teacherForm.id }
          updateGlobalTeachers(globalTeachers)
          ElMessage.success('更新成功（前端存储）')
        } else {
          ElMessage.error('未找到要更新的教师')
        }
      } else {
        // 添加新教师到全局数据
        const frontEndTeacher = { ...newTeacher, id: Date.now() }
        globalTeachers.unshift(frontEndTeacher)
        updateGlobalTeachers(globalTeachers)
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
  if (teacherFormRef.value) {
    teacherFormRef.value.resetFields()
  }
  Object.assign(teacherForm, {
    teacher_id: '',
    name: '',
    username: '',
    password: '',
    gender: '',
    birth_date: '',
    phone: '',
    email: '',
    department: '',
    title: '',
    hire_date: '',
    address: '',
    status: 'active'
  })
}

// 导入处理
const handleImport = () => {
  importVisible.value = true
}

const handleImportSuccess = (importedTeachers) => {
  try {
    // 添加到全局数据
    importedTeachers.forEach(teacher => {
      teacher.id = Date.now() + Math.random()
      globalTeachers.unshift(teacher)
    })
    updateGlobalTeachers(globalTeachers)

    ElMessage.success(`成功导入 ${importedTeachers.length} 名教师`)
    loadTeachers()
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
    const dataToExport = selectedTeachers.value.length > 0 ? selectedTeachers.value : teachers.value
    exportTeachers(dataToExport)
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadTeachers()
})
</script>

<style scoped>
.teacher-management {
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

.teacher-detail {
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