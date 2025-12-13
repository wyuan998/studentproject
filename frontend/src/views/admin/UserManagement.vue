<template>
  <div class="user-management">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">用户管理</span>
      </template>
    </el-page-header>

    <!-- 操作栏 -->
    <div class="action-container">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
      <el-button @click="handleBatchImport" :loading="importLoading">
        <el-icon><Upload /></el-icon>
        批量导入
      </el-button>
      <el-button @click="handleExport" :loading="exportLoading">
        <el-icon><Download /></el-icon>
        导出用户
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-container">
      <el-form :model="filterForm" :inline="true" size="default">
        <el-form-item label="用户角色">
          <el-select v-model="filterForm.role" placeholder="全部角色" clearable style="width: 120px">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 100px">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
            <el-option label="锁定" value="locked" />
          </el-select>
        </el-form-item>
        <el-form-item label="学院">
          <el-select v-model="filterForm.college" placeholder="全部学院" clearable style="width: 150px">
            <el-option label="计算机学院" value="计算机学院" />
            <el-option label="软件学院" value="软件学院" />
            <el-option label="数据科学学院" value="数据科学学院" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="filterForm.keyword"
            placeholder="搜索用户名/姓名/工号"
            style="width: 200px"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 用户列表 -->
    <el-card>
      <el-table
        v-loading="loading"
        :data="filteredUsers"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar" :alt="row.name">
              {{ row.name.charAt(0) }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column label="用户名" prop="username" width="120" />
        <el-table-column label="姓名" prop="real_name" width="100" />
        <el-table-column label="工号/学号" prop="user_id" width="120" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="学院" prop="college" />
        <el-table-column label="专业/部门" prop="department" />
        <el-table-column label="邮箱" prop="email" min-width="180" />
        <el-table-column label="手机号" prop="phone" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最后登录" prop="last_login" width="160">
          <template #default="{ row }">
            {{ row.last_login ? formatDateTime(row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-dropdown @command="(command) => handleDropdownCommand(command, row)">
              <el-button size="small" type="info">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="reset-password">重置密码</el-dropdown-item>
                  <el-dropdown-item command="change-status">更改状态</el-dropdown-item>
                  <el-dropdown-item command="view-logs">查看日志</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除用户</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="batch-actions" v-if="selectedUsers.length > 0">
        <span>已选择 {{ selectedUsers.length }} 个用户</span>
        <el-button type="success" @click="handleBatchStatusChange">批量修改状态</el-button>
        <el-button type="warning" @click="handleBatchResetPassword">批量重置密码</el-button>
        <el-button type="danger" @click="handleBatchDelete">批量删除</el-button>
      </div>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="userForm"
        :rules="userRules"
        label-width="100px"
        size="default"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="userForm.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="工号/学号" prop="user_id">
          <el-input v-model="userForm.user_id" placeholder="请输入工号或学号" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        <el-form-item label="学院" prop="college">
          <el-select v-model="userForm.college" placeholder="请选择学院" style="width: 100%">
            <el-option label="计算机学院" value="计算机学院" />
            <el-option label="软件学院" value="软件学院" />
            <el-option label="数据科学学院" value="数据科学学院" />
          </el-select>
        </el-form-item>
        <el-form-item label="专业/部门" prop="department">
          <el-input v-model="userForm.department" placeholder="请输入专业或部门" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="userForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="disabled">禁用</el-radio>
            <el-radio label="locked">锁定</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser" :loading="saveLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 状态更改对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="更改用户状态"
      width="400px"
    >
      <el-form :model="statusForm" label-width="80px">
        <el-form-item label="状态">
          <el-radio-group v-model="statusForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="disabled">禁用</el-radio>
            <el-radio label="locked">锁定</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="原因" v-if="statusForm.status === 'locked' || statusForm.status === 'disabled'">
          <el-input
            v-model="statusForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入更改原因"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveStatusChange" :loading="statusLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Upload, Download, Search, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref<FormInstance>()
const loading = ref(false)
const importLoading = ref(false)
const exportLoading = ref(false)
const saveLoading = ref(false)
const statusLoading = ref(false)
const userDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const isEdit = ref(false)
const currentUser = ref<any>(null)

interface User {
  id: number
  username: string
  password?: string
  real_name: string
  user_id: string
  role: 'admin' | 'teacher' | 'student'
  college: string
  department: string
  email: string
  phone: string
  status: 'active' | 'disabled' | 'locked'
  last_login?: string
  avatar: string
}

const filterForm = reactive({
  role: '',
  status: '',
  college: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const userForm = reactive({
  username: '',
  password: '',
  real_name: '',
  user_id: '',
  role: 'student',
  college: '',
  department: '',
  email: '',
  phone: '',
  status: 'active'
})

const statusForm = reactive({
  status: 'active',
  reason: ''
})

const userRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6-20个字符之间', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  user_id: [
    { required: true, message: '请输入工号或学号', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  college: [
    { required: true, message: '请选择学院', trigger: 'change' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' }
  ]
}

const users = ref<User[]>([])
const selectedUsers = ref<User[]>([])

const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchRole = !filterForm.role || user.role === filterForm.role
    const matchStatus = !filterForm.status || user.status === filterForm.status
    const matchCollege = !filterForm.college || user.college === filterForm.college
    const matchKeyword = !filterForm.keyword ||
      user.username.includes(filterForm.keyword) ||
      user.real_name.includes(filterForm.keyword) ||
      user.user_id.includes(filterForm.keyword)

    return matchRole && matchStatus && matchCollege && matchKeyword
  })
})

const loadUsers = async () => {
  try {
    loading.value = true

    // Mock API call - 替换为实际的API调用
    const mockUsers: User[] = [
      {
        id: 1,
        username: 'admin',
        real_name: '系统管理员',
        user_id: 'A001',
        role: 'admin',
        college: '计算机学院',
        department: '系统管理',
        email: 'admin@university.edu.cn',
        phone: '13800138000',
        status: 'active',
        last_login: '2024-02-20T10:30:00Z',
        avatar: ''
      },
      {
        id: 2,
        username: 'teacher001',
        real_name: '李明',
        user_id: 'T001',
        role: 'teacher',
        college: '计算机学院',
        department: '计算机科学系',
        email: 'liming@university.edu.cn',
        phone: '13800138001',
        status: 'active',
        last_login: '2024-02-20T09:15:00Z',
        avatar: ''
      },
      {
        id: 3,
        username: 'student001',
        real_name: '张三',
        user_id: 'S2021001',
        role: 'student',
        college: '计算机学院',
        department: '计算机科学',
        email: 'zhangsan@student.edu.cn',
        phone: '13800138002',
        status: 'active',
        last_login: '2024-02-20T14:20:00Z',
        avatar: ''
      }
    ]

    users.value = mockUsers
    pagination.total = mockUsers.length
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const getRoleType = (role: string) => {
  const typeMap: Record<string, string> = {
    admin: 'danger',
    teacher: 'warning',
    student: 'primary'
  }
  return typeMap[role] || 'info'
}

const getRoleText = (role: string) => {
  const textMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return textMap[role] || role
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    disabled: 'info',
    locked: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    active: '启用',
    disabled: '禁用',
    locked: '锁定'
  }
  return textMap[status] || status
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

const handleSearch = () => {
  pagination.page = 1
}

const handleReset = () => {
  filterForm.role = ''
  filterForm.status = ''
  filterForm.college = ''
  filterForm.keyword = ''
  pagination.page = 1
}

const handleCreate = () => {
  isEdit.value = false
  Object.assign(userForm, {
    username: '',
    password: '',
    real_name: '',
    user_id: '',
    role: 'student',
    college: '',
    department: '',
    email: '',
    phone: '',
    status: 'active'
  })
  userDialogVisible.value = true
}

const handleEdit = (user: User) => {
  isEdit.value = true
  Object.assign(userForm, { ...user, password: '' })
  userDialogVisible.value = true
}

const handleSaveUser = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    saveLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(isEdit.value ? '用户更新成功' : '用户创建成功')
    userDialogVisible.value = false
    loadUsers()
  } catch (error) {
    if (error !== 'validation failed') {
      ElMessage.error('保存失败')
    }
  } finally {
    saveLoading.value = false
  }
}

const handleSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection
}

const handleDropdownCommand = async (command: string, user: User) => {
  currentUser.value = user

  switch (command) {
    case 'reset-password':
      await handleResetPassword(user)
      break
    case 'change-status':
      statusForm.status = user.status
      statusForm.reason = ''
      statusDialogVisible.value = true
      break
    case 'view-logs':
      ElMessage.info('功能开发中...')
      break
    case 'delete':
      await handleDelete(user)
      break
  }
}

const handleResetPassword = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户 "${user.real_name}" 的密码吗？`,
      '确认重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('密码重置成功，新密码为：123456')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('密码重置失败')
    }
  }
}

const handleSaveStatusChange = async () => {
  if (!currentUser.value) return

  try {
    statusLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 更新本地状态
    const user = users.value.find(u => u.id === currentUser.value.id)
    if (user) {
      user.status = statusForm.status as any
    }

    ElMessage.success('状态更改成功')
    statusDialogVisible.value = false
  } catch (error) {
    ElMessage.error('状态更改失败')
  } finally {
    statusLoading.value = false
  }
}

const handleDelete = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.real_name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    const index = users.value.findIndex(u => u.id === user.id)
    if (index > -1) {
      users.value.splice(index, 1)
      pagination.total--
    }

    ElMessage.success('用户删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('用户删除失败')
    }
  }
}

const handleBatchImport = async () => {
  try {
    importLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('用户导入成功')
    loadUsers()
  } catch (error) {
    ElMessage.error('用户导入失败')
  } finally {
    importLoading.value = false
  }
}

const handleExport = async () => {
  try {
    exportLoading.value = true
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('用户导出成功')
  } catch (error) {
    ElMessage.error('用户导出失败')
  } finally {
    exportLoading.value = false
  }
}

const handleBatchStatusChange = () => {
  statusForm.status = 'active'
  statusForm.reason = ''
  statusDialogVisible.value = true
}

const handleBatchResetPassword = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要重置选中的 ${selectedUsers.value.length} 个用户的密码吗？`,
      '确认批量重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(`批量重置 ${selectedUsers.value.length} 个用户密码成功，新密码为：123456`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量重置密码失败')
    }
  }
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedUsers.value.length} 个用户吗？`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(`批量删除 ${selectedUsers.value.length} 个用户成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  loadUsers()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadUsers()
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadUsers()
})
</script>

<style lang="scss" scoped>
.user-management {
  .title {
    font-size: 18px;
    font-weight: 600;
  }

  .action-container {
    margin: 20px 0;
    display: flex;
    gap: 12px;
  }

  .filter-container {
    margin: 20px 0;
    padding: 20px;
    background-color: var(--el-bg-color-page);
    border-radius: 8px;
  }

  .batch-actions {
    margin: 20px 0;
    padding: 16px;
    background-color: var(--el-fill-color-light);
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>