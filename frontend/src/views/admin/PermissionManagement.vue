<template>
  <div class="permission-management">
    <el-page-header @back="handleBack">
      <template #content>
        <span class="title">权限管理</span>
      </template>
    </el-page-header>

    <!-- 操作栏 -->
    <div class="action-container">
      <el-button type="primary" @click="handleCreateRole">
        <el-icon><Plus /></el-icon>
        新增角色
      </el-button>
      <el-button @click="handleRefreshPermissions" :loading="refreshLoading">
        <el-icon><Refresh /></el-icon>
        刷新权限
      </el-button>
    </div>

    <!-- 权限管理标签页 -->
    <el-card>
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <!-- 角色管理 -->
        <el-tab-pane label="角色管理" name="roles">
          <div class="filter-container">
            <el-form :model="roleFilter" :inline="true" size="default">
              <el-form-item label="角色类型">
                <el-select v-model="roleFilter.type" placeholder="全部类型" clearable style="width: 150px">
                  <el-option label="系统角色" value="system" />
                  <el-option label="业务角色" value="business" />
                </el-select>
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="roleFilter.status" placeholder="全部状态" clearable style="width: 100px">
                  <el-option label="启用" value="active" />
                  <el-option label="禁用" value="disabled" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-input
                  v-model="roleFilter.keyword"
                  placeholder="搜索角色名称"
                  style="width: 200px"
                  clearable
                  @keyup.enter="handleSearchRoles"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSearchRoles">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table
            v-loading="rolesLoading"
            :data="filteredRoles"
            stripe
            style="width: 100%"
          >
            <el-table-column label="角色名称" prop="name" min-width="150" />
            <el-table-column label="角色编码" prop="code" width="120" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getRoleTypeColor(row.type)">
                  {{ getRoleTypeText(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="描述" prop="description" min-width="200" show-overflow-tooltip />
            <el-table-column label="用户数量" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.user_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-switch
                  v-model="row.status"
                  :active-value="'active'"
                  :inactive-value="'disabled'"
                  @change="handleRoleStatusChange(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="创建时间" prop="created_at" width="160">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button
                  size="small"
                  type="primary"
                  @click="handleEditRole(row)"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="success"
                  @click="handleAssignPermissions(row)"
                >
                  分配权限
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="handleDeleteRole(row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 权限列表 -->
        <el-tab-pane label="权限列表" name="permissions">
          <div class="filter-container">
            <el-form :model="permissionFilter" :inline="true" size="default">
              <el-form-item label="权限模块">
                <el-select v-model="permissionFilter.module" placeholder="全部模块" clearable style="width: 150px">
                  <el-option label="学生管理" value="student" />
                  <el-option label="教师管理" value="teacher" />
                  <el-option label="课程管理" value="course" />
                  <el-option label="选课管理" value="enrollment" />
                  <el-option label="成绩管理" value="grade" />
                  <el-option label="系统管理" value="system" />
                </el-select>
              </el-form-item>
              <el-form-item label="权限类型">
                <el-select v-model="permissionFilter.type" placeholder="全部类型" clearable style="width: 120px">
                  <el-option label="菜单" value="menu" />
                  <el-option label="按钮" value="button" />
                  <el-option label="接口" value="api" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-input
                  v-model="permissionFilter.keyword"
                  placeholder="搜索权限名称"
                  style="width: 200px"
                  clearable
                  @keyup.enter="handleSearchPermissions"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSearchPermissions">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table
            v-loading="permissionsLoading"
            :data="filteredPermissions"
            stripe
            style="width: 100%"
            row-key="id"
            :tree-props="{ children: 'children', hasChildren: 'has_children' }"
          >
            <el-table-column prop="name" label="权限名称" min-width="200" />
            <el-table-column prop="code" label="权限编码" width="150" />
            <el-table-column label="模块" width="120">
              <template #default="{ row }">
                <el-tag type="info">{{ row.module }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getPermissionTypeColor(row.type)">
                  {{ getPermissionTypeText(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="描述" prop="description" min-width="200" show-overflow-tooltip />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 用户权限分配 -->
        <el-tab-pane label="用户权限" name="user-permissions">
          <div class="filter-container">
            <el-form :model="userFilter" :inline="true" size="default">
              <el-form-item label="用户角色">
                <el-select v-model="userFilter.role" placeholder="全部角色" clearable style="width: 150px">
                  <el-option
                    v-for="role in roles"
                    :key="role.value"
                    :label="role.label"
                    :value="role.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-input
                  v-model="userFilter.keyword"
                  placeholder="搜索用户名/姓名"
                  style="width: 200px"
                  clearable
                  @keyup.enter="handleSearchUsers"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSearchUsers">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table
            v-loading="usersLoading"
            :data="filteredUsers"
            stripe
            style="width: 100%"
            @selection-change="handleUserSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column label="用户名" prop="username" width="120" />
            <el-table-column label="姓名" prop="real_name" width="100" />
            <el-table-column label="角色" width="150">
              <template #default="{ row }">
                <el-tag
                  v-for="role in row.roles"
                  :key="role"
                  size="small"
                  style="margin-right: 4px;"
                >
                  {{ getRoleText(role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="权限数量" width="100">
              <template #default="{ row }">
                <el-tag type="info">{{ row.permission_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="最后更新" prop="updated_at" width="160">
              <template #default="{ row }">
                {{ formatDateTime(row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button
                  size="small"
                  type="primary"
                  @click="handleEditUserPermissions(row)"
                >
                  编辑权限
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="batch-actions" v-if="selectedUsers.length > 0">
            <span>已选择 {{ selectedUsers.length }} 个用户</span>
            <el-button type="success" @click="handleBatchAssignRoles">批量分配角色</el-button>
            <el-button type="warning" @click="handleBatchAssignPermissions">批量分配权限</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 创建/编辑角色对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      :title="isEditRole ? '编辑角色' : '新增角色'"
      width="600px"
    >
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleRules"
        label-width="100px"
        size="default"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="roleForm.code" placeholder="请输入角色编码" :disabled="isEditRole" />
        </el-form-item>
        <el-form-item label="角色类型" prop="type">
          <el-select v-model="roleForm.type" placeholder="请选择角色类型" style="width: 100%">
            <el-option label="系统角色" value="system" />
            <el-option label="业务角色" value="business" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="roleForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRole" :loading="saveRoleLoading">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 分配权限对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="分配权限"
      width="800px"
    >
      <div class="permission-assignment">
        <div class="role-info">
          <h4>角色信息</h4>
          <p><strong>角色名称：</strong>{{ currentRole?.name }}</p>
          <p><strong>角色编码：</strong>{{ currentRole?.code }}</p>
        </div>

        <div class="permission-tree">
          <h4>权限列表</h4>
          <el-tree
            ref="permissionTreeRef"
            :data="permissionTree"
            show-checkbox
            node-key="id"
            :default-checked="selectedPermissions"
            @check="handlePermissionCheck"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermissions" :loading="savePermissionsLoading">
          保存权限
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'

const router = useRouter()
const roleFormRef = ref<FormInstance>()
const permissionTreeRef = ref<any>(null)

const activeTab = ref('roles')
const rolesLoading = ref(false)
const permissionsLoading = ref(false)
const usersLoading = ref(false)
const refreshLoading = ref(false)
const saveRoleLoading = ref(false)
const savePermissionsLoading = ref(false)
const roleDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const isEditRole = ref(false)
const currentRole = ref<any>(null)
const selectedPermissions = ref<string[]>([])
const selectedUsers = ref<any[]>([])

interface Role {
  id: number
  name: string
  code: string
  type: 'system' | 'business'
  description: string
  status: 'active' | 'disabled'
  user_count: number
  created_at: string
}

interface Permission {
  id: string
  name: string
  code: string
  module: string
  type: 'menu' | 'button' | 'api'
  description: string
  status: 'active'
  parent_id?: string
  children?: Permission[]
  has_children?: boolean
}

interface User {
  id: number
  username: string
  real_name: string
  roles: string[]
  permission_count: number
  updated_at: string
}

const roleFilter = reactive({
  type: '',
  status: '',
  keyword: ''
})

const permissionFilter = reactive({
  module: '',
  type: '',
  keyword: ''
})

const userFilter = reactive({
  role: '',
  keyword: ''
})

const roleForm = reactive({
  name: '',
  code: '',
  type: 'business',
  description: '',
  status: 'active'
})

const roleRules: FormRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { min: 2, max: 20, message: '角色编码长度在2-20个字符之间', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择角色类型', trigger: 'change' }
  ]
}

const roles = ref<Role[]>([])
const permissions = ref<Permission[]>([])
const users = ref<User[]>([])
const permissionTree = ref<Permission[]>([])

const filteredRoles = computed(() => {
  return roles.value.filter(role => {
    const matchType = !roleFilter.type || role.type === roleFilter.type
    const matchStatus = !roleFilter.status || role.status === roleFilter.status
    const matchKeyword = !roleFilter.keyword ||
      role.name.includes(roleFilter.keyword) ||
      role.code.includes(roleFilter.keyword)

    return matchType && matchStatus && matchKeyword
  })
})

const filteredPermissions = computed(() => {
  return permissions.value.filter(permission => {
    const matchModule = !permissionFilter.module || permission.module === permissionFilter.module
    const matchType = !permissionFilter.type || permission.type === permissionFilter.type
    const matchKeyword = !permissionFilter.keyword ||
      permission.name.includes(permissionFilter.keyword) ||
      permission.code.includes(permissionFilter.keyword)

    return matchModule && matchType && matchKeyword
  })
})

const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchRole = !userFilter.role || user.roles.includes(userFilter.role)
    const matchKeyword = !userFilter.keyword ||
      user.username.includes(userFilter.keyword) ||
      user.real_name.includes(userFilter.keyword)

    return matchRole && matchKeyword
  })
})

const loadRoles = async () => {
  try {
    rolesLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockRoles: Role[] = [
      {
        id: 1,
        name: '系统管理员',
        code: 'ROLE_ADMIN',
        type: 'system',
        description: '系统管理员角色，拥有所有权限',
        status: 'active',
        user_count: 3,
        created_at: '2024-02-20T10:30:00Z'
      },
      {
        id: 2,
        name: '教师',
        code: 'ROLE_TEACHER',
        type: 'business',
        description: '教师角色，拥有教学相关权限',
        status: 'active',
        user_count: 156,
        created_at: '2024-02-18T14:20:00Z'
      },
      {
        id: 3,
        name: '学生',
        code: 'ROLE_STUDENT',
        type: 'business',
        description: '学生角色，拥有学习相关权限',
        status: 'active',
        user_count: 1248,
        created_at: '2024-02-15T09:15:00Z'
      }
    ]

    roles.value = mockRoles
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    rolesLoading.value = false
  }
}

const loadPermissions = async () => {
  try {
    permissionsLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockPermissions: Permission[] = [
      {
        id: '1',
        name: '学生管理',
        code: 'student_management',
        module: 'student',
        type: 'menu',
        description: '学生管理模块',
        status: 'active',
        children: [
          {
            id: '1-1',
            name: '学生列表',
            code: 'student_list',
            module: 'student',
            type: 'menu',
            description: '查看学生列表',
            status: 'active'
          },
          {
            id: '1-2',
            name: '新增学生',
            code: 'student_create',
            module: 'student',
            type: 'button',
            description: '新增学生信息',
            status: 'active'
          },
          {
            id: '1-3',
            name: '编辑学生',
            code: 'student_edit',
            module: 'student',
            type: 'button',
            description: '编辑学生信息',
            status: 'active'
          }
        ]
      },
      {
        id: '2',
        name: '教师管理',
        code: 'teacher_management',
        module: 'teacher',
        type: 'menu',
        description: '教师管理模块',
        status: 'active',
        children: [
          {
            id: '2-1',
            name: '教师列表',
            code: 'teacher_list',
            module: 'teacher',
            type: 'menu',
            description: '查看教师列表',
            status: 'active'
          }
        ]
      },
      {
        id: '3',
        name: '系统管理',
        code: 'system_management',
        module: 'system',
        type: 'menu',
        description: '系统管理模块',
        status: 'active',
        children: [
          {
            id: '3-1',
            name: '用户管理',
            code: 'user_management',
            module: 'system',
            type: 'menu',
            description: '用户管理',
            status: 'active'
          },
          {
            id: '3-2',
            name: '角色权限',
            code: 'permission_management',
            module: 'system',
            type: 'menu',
            description: '角色权限管理',
            status: 'active'
          }
        ]
      }
    ]

    permissions.value = mockPermissions
    buildPermissionTree()
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    permissionsLoading.value = false
  }
}

const buildPermissionTree = () => {
  // 构建权限树
  const tree: Permission[] = []
  const map = new Map()

  permissions.value.forEach(permission => {
    const node = { ...permission }
    map.set(permission.id, node)

    if (!permission.parent_id) {
      tree.push(node)
    } else {
      const parent = map.get(permission.parent_id)
      if (parent) {
        if (!parent.children) parent.children = []
        parent.children.push(node)
        parent.has_children = true
      }
    }
  })

  permissionTree.value = tree
}

const loadUsers = async () => {
  try {
    usersLoading.value = true

    // Mock API call - 替换为实际的API调用
    const mockUsers: User[] = [
      {
        id: 1,
        username: 'admin',
        real_name: '系统管理员',
        roles: ['ROLE_ADMIN'],
        permission_count: 45,
        updated_at: '2024-02-20T10:30:00Z'
      },
      {
        id: 2,
        username: 'teacher001',
        real_name: '李明',
        roles: ['ROLE_TEACHER'],
        permission_count: 12,
        updated_at: '2024-02-19T16:20:00Z'
      },
      {
        id: 3,
        username: 'student001',
        real_name: '张三',
        roles: ['ROLE_STUDENT'],
        permission_count: 8,
        updated_at: '2024-02-18T14:15:00Z'
      }
    ]

    users.value = mockUsers
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    usersLoading.value = false
  }
}

const getRoleTypeColor = (type: string) => {
  return type === 'system' ? 'danger' : 'primary'
}

const getRoleTypeText = (type: string) => {
  return type === 'system' ? '系统' : '业务'
}

const getPermissionTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    menu: 'primary',
    button: 'success',
    api: 'warning'
  }
  return colorMap[type] || 'info'
}

const getPermissionTypeText = (type: string) => {
  const textMap: Record<string, string> = {
    menu: '菜单',
    button: '按钮',
    api: '接口'
  }
  return textMap[type] || type
}

const getRoleText = (roleCode: string) => {
  const role = roles.value.find(r => r.code === roleCode)
  return role ? role.name : roleCode
}

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString()
}

const handleTabChange = (tabName: string) => {
  activeTab.value = tabName
}

const handleSearchRoles = () => {
  // 触发重新计算过滤后的角色
}

const handleSearchPermissions = () => {
  // 触发重新计算过滤后的权限
}

const handleSearchUsers = () => {
  // 触发重新计算过滤后的用户
}

const handleCreateRole = () => {
  isEditRole.value = false
  Object.assign(roleForm, {
    name: '',
    code: '',
    type: 'business',
    description: '',
    status: 'active'
  })
  roleDialogVisible.value = true
}

const handleEditRole = (role: Role) => {
  isEditRole.value = true
  Object.assign(roleForm, role)
  roleDialogVisible.value = true
}

const handleSaveRole = async () => {
  if (!roleFormRef.value) return

  try {
    await roleFormRef.value.validate()

    saveRoleLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success(isEditRole.value ? '角色更新成功' : '角色创建成功')
    roleDialogVisible.value = false
    loadRoles()
  } catch (error) {
    if (error !== 'validation failed') {
      ElMessage.error('保存失败')
    }
  } finally {
    saveRoleLoading.value = false
  }
}

const handleRoleStatusChange = async (role: Role) => {
  try {
    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    ElMessage.success(`角色已${role.status === 'active' ? '启用' : '禁用'}`)
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

const handleDeleteRole = async (role: Role) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    const index = roles.value.findIndex(r => r.id === role.id)
    if (index > -1) {
      roles.value.splice(index, 1)
    }

    ElMessage.success('角色删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleAssignPermissions = (role: Role) => {
  currentRole.value = role
  selectedPermissions.value = [] // 这里应该从角色现有权限中获取
  permissionDialogVisible.value = true

  nextTick(() => {
    if (permissionTreeRef.value) {
      // 设置默认选中的权限
      permissionTreeRef.value.setCheckedKeys(selectedPermissions.value)
    }
  })
}

const handlePermissionCheck = (data: any, checked: boolean) => {
  if (checked) {
    selectedPermissions.value.push(data.id)
  } else {
    const index = selectedPermissions.value.indexOf(data.id)
    if (index > -1) {
      selectedPermissions.value.splice(index, 1)
    }
  }
}

const handleSavePermissions = async () => {
  if (!currentRole.value) return

  try {
    savePermissionsLoading.value = true

    // Mock API call - 替换为实际的API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('权限分配成功')
    permissionDialogVisible.value = false
  } catch (error) {
    ElMessage.error('权限分配失败')
  } finally {
    savePermissionsLoading.value = false
  }
}

const handleRefreshPermissions = async () => {
  try {
    refreshLoading.value = true
    await loadPermissions()
    ElMessage.success('权限刷新成功')
  } catch (error) {
    ElMessage.error('权限刷新失败')
  } finally {
    refreshLoading.value = false
  }
}

const handleUserSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection
}

const handleEditUserPermissions = (user: User) => {
  ElMessage.info('功能开发中...')
}

const handleBatchAssignRoles = () => {
  ElMessage.info('功能开发中...')
}

const handleBatchAssignPermissions = () => {
  ElMessage.info('功能开发中...')
}

const handleBack = () => {
  router.back()
}

onMounted(() => {
  loadRoles()
  loadPermissions()
  loadUsers()
})
</script>

<style lang="scss" scoped>
.permission-management {
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

  .permission-assignment {
    .role-info {
      margin-bottom: 20px;
      padding: 16px;
      background-color: var(--el-fill-color-light);
      border-radius: 8px;

      h4 {
        margin-bottom: 8px;
        color: var(--el-text-color-primary);
      }

      p {
        margin: 4px 0;
        color: var(--el-text-color-regular);
      }
    }

    .permission-tree {
      h4 {
        margin-bottom: 16px;
        color: var(--el-text-color-primary);
      }
    }
  }
}
</style>