<template>
  <div class="teacher-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>教师管理</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>教师管理</el-breadcrumb-item>
          <el-breadcrumb-item>教师列表</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增教师
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form
        ref="filterFormRef"
        :model="filterForm"
        :inline="true"
        class="filter-form"
      >
        <el-form-item label="关键词搜索">
          <el-input
            v-model="filterForm.search"
            placeholder="请输入教师工号、姓名或手机号"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="教师状态">
          <el-select
            v-model="filterForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="在职" value="active" />
            <el-option label="离职" value="inactive" />
            <el-option label="休假" value="on_leave" />
          </el-select>
        </el-form-item>
        <el-form-item label="院系">
          <el-input
            v-model="filterForm.department"
            placeholder="请输入院系名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="职称">
          <el-select
            v-model="filterForm.title"
            placeholder="请选择职称"
            clearable
            style="width: 150px"
          >
            <el-option label="教授" value="professor" />
            <el-option label="副教授" value="associate_professor" />
            <el-option label="讲师" value="lecturer" />
            <el-option label="助教" value="assistant" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="teacher_id" label="工号" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag :type="getGenderTagType(row.gender)">
              {{ getGenderLabel(row.gender) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip />
        <el-table-column prop="department" label="院系" width="150" />
        <el-table-column prop="title" label="职称" width="100">
          <template #default="{ row }">
            <el-tag :type="getTitleTagType(row.title)">
              {{ getTitleLabel(row.title) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hire_date" label="入职日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.hire_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button
              text
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              text
              type="warning"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              text
              type="info"
              size="small"
              @click="handleViewCourses(row)"
            >
              课程
            </el-button>
            <el-popconfirm
              title="确定要删除这个教师吗？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button
                  text
                  type="danger"
                  size="small"
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 批量操作 -->
    <div v-if="selectedRows.length > 0" class="batch-actions">
      <el-card>
        <div class="batch-actions-content">
          <span>已选择 {{ selectedRows.length }} 项</span>
          <div class="batch-buttons">
            <el-button type="warning" @click="handleBatchExport">
              批量导出
            </el-button>
            <el-button type="danger" @click="handleBatchDelete">
              批量删除
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  Download
} from '@element-plus/icons-vue'
import { teacherApi } from '@/api/user'
import type { Teacher, TeacherQueryParams } from '@/types/user'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const tableData = ref<Teacher[]>([])
const selectedRows = ref<Teacher[]>([])
const filterFormRef = ref<FormInstance>()

// 筛选表单
const filterForm = reactive({
  search: '',
  status: '',
  department: '',
  title: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 查询参数
const queryParams = computed<TeacherQueryParams>(() => ({
  page: pagination.page,
  per_page: pagination.per_page,
  search: filterForm.search || undefined,
  status: filterForm.status as any || undefined,
  department: filterForm.department || undefined,
  title: filterForm.title || undefined,
  sort_by: 'created_at',
  sort_order: 'desc'
}))

// 方法
const loadTeachers = async () => {
  try {
    loading.value = true
    const response = await teacherApi.getTeachers(queryParams.value)

    if (response.data?.success) {
      tableData.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data?.message || '加载教师列表失败')
    }
  } catch (error: any) {
    console.error('Load teachers error:', error)
    ElMessage.error(error.response?.data?.message || '加载教师列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadTeachers()
}

const handleReset = () => {
  if (filterFormRef.value) {
    filterFormRef.value.resetFields()
  }
  Object.assign(filterForm, {
    search: '',
    status: '',
    department: '',
    title: ''
  })
  pagination.page = 1
  loadTeachers()
}

const handleCreate = () => {
  router.push('/teachers/create')
}

const handleView = (row: Teacher) => {
  router.push(`/teachers/detail/${row.id}`)
}

const handleEdit = (row: Teacher) => {
  router.push(`/teachers/edit/${row.id}`)
}

const handleViewCourses = (row: Teacher) => {
  router.push(`/teachers/courses/${row.id}`)
}

const handleDelete = async (row: Teacher) => {
  try {
    const response = await teacherApi.deleteTeacher(row.id)

    if (response.data?.success) {
      ElMessage.success('删除成功')
      loadTeachers()
    } else {
      ElMessage.error(response.data?.message || '删除失败')
    }
  } catch (error: any) {
    console.error('Delete teacher error:', error)
    ElMessage.error(error.response?.data?.message || '删除失败')
  }
}

const handleExport = async () => {
  try {
    const response = await teacherApi.exportTeachers(queryParams.value)

    // 创建下载链接
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `教师列表_${new Date().toLocaleDateString()}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败')
  }
}

const handleSelectionChange = (rows: Teacher[]) => {
  selectedRows.value = rows
}

const handleBatchExport = async () => {
  // 实现批量导出逻辑
  ElMessage.info('批量导出功能开发中...')
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 个教师吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const ids = selectedRows.value.map(row => row.id)
    const response = await teacherApi.batchDeleteTeachers(ids)

    if (response.data?.success) {
      ElMessage.success('批量删除成功')
      selectedRows.value = []
      loadTeachers()
    } else {
      ElMessage.error(response.data?.message || '批量删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Batch delete error:', error)
      ElMessage.error(error.response?.data?.message || '批量删除失败')
    }
  }
}

const handleSizeChange = (size: number) => {
  pagination.per_page = size
  loadTeachers()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadTeachers()
}

// 工具方法
const getGenderTagType = (gender: string) => {
  const typeMap: Record<string, string> = {
    male: 'primary',
    female: 'danger'
  }
  return typeMap[gender] || 'info'
}

const getGenderLabel = (gender: string) => {
  const labelMap: Record<string, string> = {
    male: '男',
    female: '女',
    other: '其他'
  }
  return labelMap[gender] || gender
}

const getTitleTagType = (title: string) => {
  const typeMap: Record<string, string> = {
    professor: 'danger',
    associate_professor: 'warning',
    lecturer: 'primary',
    assistant: 'info'
  }
  return typeMap[title] || 'info'
}

const getTitleLabel = (title: string) => {
  const labelMap: Record<string, string> = {
    professor: '教授',
    associate_professor: '副教授',
    lecturer: '讲师',
    assistant: '助教'
  }
  return labelMap[title] || title
}

const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    inactive: 'danger',
    on_leave: 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    active: '在职',
    inactive: '离职',
    on_leave: '休假'
  }
  return labelMap[status] || status
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadTeachers()
})
</script>

<style lang="scss" scoped>
.teacher-list-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .header-left {
    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    .el-breadcrumb {
      font-size: 14px;
    }
  }

  .header-right {
    display: flex;
    gap: 12px;
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-form {
    .el-form-item {
      margin-bottom: 0;
      margin-right: 16px;
    }
  }
}

.table-card {
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  width: auto;
  min-width: 400px;

  .batch-actions-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;

    .batch-buttons {
      display: flex;
      gap: 12px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .teacher-list-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .header-right {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .filter-form {
    .el-form-item {
      width: 100%;
      margin-right: 0;
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      .el-input,
      .el-select {
        width: 100% !important;
      }
    }
  }

  .el-table {
    font-size: 12px;

    .el-table-column {
      padding: 8px 4px;
    }
  }

  .batch-actions {
    width: 90%;
    min-width: 300px;
  }
}
</style>