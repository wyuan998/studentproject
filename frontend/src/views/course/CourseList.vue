<template>
  <div class="course-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">课程列表</h2>
        <p class="page-description">管理所有课程信息</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建课程
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-container">
      <el-form :model="queryParams" inline class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="搜索课程名称、编号"
            clearable
            @keyup.enter="handleSearch"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item label="教师">
          <el-select
            v-model="queryParams.teacher_id"
            placeholder="选择教师"
            clearable
            style="width: 160px"
          >
            <el-option
              v-for="item in teacherOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="queryParams.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="已发布" value="published" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已完成" value="completed" />
            <el-option label="草稿" value="draft" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="courseList"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column label="课程编号" prop="course_code" width="120" />
        <el-table-column label="课程名称" prop="name" width="200" show-overflow-tooltip />
        <el-table-column label="教师" prop="teacher_name" width="120" />
        <el-table-column label="学分" prop="credits" width="80" />
        <el-table-column label="学时" prop="hours" width="80" />
        <el-table-column label="学期" prop="semester" width="100" />
        <el-table-column label="已选人数" prop="current_students" width="100">
          <template #default="{ row }">
            {{ row.current_students }} / {{ row.max_students }}
          </template>
        </el-table-column>
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getCourseList, deleteCourse } from '@/api/course'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const courseList = ref([])
const total = ref(0)

// 查询参数
const queryParams = reactive({
  page: 1,
  size: 20,
  keyword: '',
  teacher_id: '',
  status: ''
})

// 教师选项
const teacherOptions = ref([
  { label: '张伟', value: '1' },
  { label: '李明', value: '2' },
  { label: '王芳', value: '3' }
])

// 获取课程列表
const getList = async () => {
  try {
    loading.value = true
    const { data } = await getCourseList(queryParams)
    courseList.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  queryParams.page = 1
  getList()
}

// 重置查询
const resetQuery = () => {
  Object.assign(queryParams, {
    page: 1,
    size: 20,
    keyword: '',
    teacher_id: '',
    status: ''
  })
  getList()
}

// 分页处理
const handleSizeChange = (val: number) => {
  queryParams.size = val
  getList()
}

const handleCurrentChange = (val: number) => {
  queryParams.page = val
  getList()
}

// 操作处理
const handleCreate = () => {
  router.push('/courses/create')
}

const handleView = (row: any) => {
  router.push(`/courses/detail/${row.id}`)
}

const handleEdit = (row: any) => {
  router.push(`/courses/edit/${row.id}`)
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除课程"${row.name}"吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteCourse(row.id)
    ElMessage.success('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: 'info',
    published: 'success',
    ongoing: 'warning',
    completed: 'primary',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    published: '已发布',
    ongoing: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// 初始化
onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.course-list {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .header-left {
      .page-title {
        margin: 0 0 4px;
        font-size: 20px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      .page-description {
        margin: 0;
        font-size: 14px;
        color: var(--el-text-color-regular);
      }
    }
  }

  .filter-container {
    background-color: var(--el-bg-color);
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;

    .filter-form {
      margin: 0;
    }
  }

  .table-container {
    background-color: var(--el-bg-color);
    padding: 20px;
    border-radius: 4px;

    .pagination-container {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>