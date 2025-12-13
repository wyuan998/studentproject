<template>
  <div class="grade-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">成绩列表</h2>
        <p class="page-description">管理学生成绩信息</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          录入成绩
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-container">
      <el-form :model="queryParams" inline class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="搜索学生姓名、课程名称"
            clearable
            @keyup.enter="handleSearch"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item label="课程">
          <el-select
            v-model="queryParams.course_id"
            placeholder="选择课程"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="item in courseOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="成绩类型">
          <el-select
            v-model="queryParams.grade_type"
            placeholder="选择类型"
            clearable
            style="width: 120px"
          >
            <el-option label="考试" value="exam" />
            <el-option label="作业" value="assignment" />
            <el-option label="测验" value="quiz" />
            <el-option label="项目" value="project" />
            <el-option label="期末" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="queryParams.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="最终" value="final" />
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
        :data="gradeList"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="学生姓名" prop="student_name" width="120" />
        <el-table-column label="学号" prop="student_no" width="120" />
        <el-table-column label="课程名称" prop="course_name" width="200" show-overflow-tooltip />
        <el-table-column label="成绩名称" prop="grade_name" width="150" />
        <el-table-column label="类型" prop="grade_type" width="100">
          <template #default="{ row }">
            <el-tag :type="getGradeTypeTag(row.grade_type)">
              {{ getGradeTypeText(row.grade_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分数" prop="score" width="100">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score, row.max_score) }">
              {{ row.score }} / {{ row.max_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="百分比" prop="percentage" width="100">
          <template #default="{ row }">
            {{ row.percentage.toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column label="等级" prop="grade_letter" width="80" />
        <el-table-column label="绩点" prop="grade_point" width="80" />
        <el-table-column label="状态" prop="status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="录入时间" prop="graded_date" width="120" />
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
              v-if="row.status !== 'final'"
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

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedIds.length > 0">
        <el-button type="success" @click="batchPublish">
          批量发布 ({{ selectedIds.length }})
        </el-button>
        <el-button type="warning" @click="batchFinalize">
          批量确定 ({{ selectedIds.length }})
        </el-button>
      </div>

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
import { getGradeList, deleteGrade, publishGrades } from '@/api/grade'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const gradeList = ref([])
const total = ref(0)
const selectedIds = ref([])

// 查询参数
const queryParams = reactive({
  page: 1,
  size: 20,
  keyword: '',
  course_id: '',
  grade_type: '',
  status: ''
})

// 课程选项
const courseOptions = ref([
  { label: '计算机科学导论', value: '1' },
  { label: '数据结构与算法', value: '2' },
  { label: '操作系统原理', value: '3' }
])

// 获取成绩列表
const getList = async () => {
  try {
    loading.value = true
    const { data } = await getGradeList(queryParams)
    gradeList.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error('获取成绩列表失败')
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
    course_id: '',
    grade_type: '',
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

// 表格选择
const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map(item => item.id)
}

// 操作处理
const handleCreate = () => {
  router.push('/grades/entry')
}

const handleView = (row: any) => {
  router.push(`/grades/detail/${row.id}`)
}

const handleEdit = (row: any) => {
  router.push(`/grades/edit/${row.id}`)
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条成绩记录吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteGrade(row.id)
    ElMessage.success('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量操作
const batchPublish = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要发布这 ${selectedIds.value.length} 条成绩吗？`,
      '批量发布',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await publishGrades(selectedIds.value)
    ElMessage.success('批量发布成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量发布失败')
    }
  }
}

const batchFinalize = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要最终确定这 ${selectedIds.value.length} 条成绩吗？确定后将无法修改。`,
      '批量确定',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里应该调用最终确定的API
    ElMessage.success('批量确定成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量确定失败')
    }
  }
}

// 获取成绩类型标签
const getGradeTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    exam: 'danger',
    assignment: 'primary',
    quiz: 'warning',
    project: 'success',
    final: 'danger'
  }
  return typeMap[type] || 'info'
}

// 获取成绩类型文本
const getGradeTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    exam: '考试',
    assignment: '作业',
    quiz: '测验',
    project: '项目',
    final: '期末'
  }
  return typeMap[type] || type
}

// 获取分数颜色
const getScoreColor = (score: number, maxScore: number) => {
  const percentage = (score / maxScore) * 100
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: 'info',
    published: 'success',
    final: 'warning'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    published: '已发布',
    final: '最终'
  }
  return statusMap[status] || status
}

// 初始化
onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.grade-list {
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

    .batch-actions {
      margin: 16px 0;
      display: flex;
      gap: 12px;
    }

    .pagination-container {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>