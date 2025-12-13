<template>
  <div class="grade-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">成绩管理</h2>
        <p class="page-description">管理学生成绩信息，支持录入、修改、统计和分析</p>
      </div>
      <div class="header-right">
        <el-button type="success" @click="handleBulkEntry">
          <el-icon><DocumentAdd /></el-icon>
          批量录入
        </el-button>
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
            placeholder="搜索学生姓名、学号、课程名称"
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
        <el-form-item label="考试类型">
          <el-select
            v-model="queryParams.exam_type"
            placeholder="选择类型"
            clearable
            style="width: 120px"
          >
            <el-option label="测验" value="quiz" />
            <el-option label="作业" value="assignment" />
            <el-option label="期中考试" value="midterm" />
            <el-option label="期末考试" value="final" />
            <el-option label="项目" value="project" />
            <el-option label="演讲" value="presentation" />
            <el-option label="实验课" value="lab" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select
            v-model="queryParams.semester"
            placeholder="选择学期"
            clearable
            style="width: 150px"
          >
            <el-option label="2024-春季" value="2024-春季" />
            <el-option label="2024-夏季" value="2024-夏季" />
            <el-option label="2024-秋季" value="2024-秋季" />
            <el-option label="2025-春季" value="2025-春季" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="queryParams.is_published"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="未发布" :value="false" />
            <el-option label="已发布" :value="true" />
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
        <el-table-column label="学号" prop="student_id" width="120" />
        <el-table-column label="课程代码" prop="course_code" width="120" />
        <el-table-column label="课程名称" prop="course_name" width="200" show-overflow-tooltip />
        <el-table-column label="考试名称" prop="exam_name" width="150" />
        <el-table-column label="类型" prop="exam_type" width="100">
          <template #default="{ row }">
            <el-tag :type="getGradeTypeTag(row.exam_type)">
              {{ getGradeTypeText(row.exam_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分数" prop="score" width="120">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score, row.max_score) }">
              {{ row.score }} / {{ row.max_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="百分比" prop="percentage" width="100">
          <template #default="{ row }">
            {{ row.percentage?.toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column label="等级" prop="letter_grade" width="80" />
        <el-table-column label="绩点" prop="grade_point" width="80" />
        <el-table-column label="状态" prop="is_published" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'warning'">
              {{ row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="学期" prop="semester" width="100" />
        <el-table-column label="录入时间" prop="graded_at" width="150">
          <template #default="{ row }">
            {{ formatDate(row.graded_at) }}
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
              v-if="!row.is_published"
              type="success"
              size="small"
              link
              @click="handlePublish(row)"
            >
              发布
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

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedIds.length > 0">
        <el-button type="success" @click="batchPublish">
          批量发布 ({{ selectedIds.length }})
        </el-button>
        <el-button type="danger" @click="batchDelete">
          批量删除 ({{ selectedIds.length }})
        </el-button>
      </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.per_page"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 成绩录入对话框 -->
    <GradeEntryDialog
      v-model="entryDialogVisible"
      :grade="currentGrade"
      @success="handleEntrySuccess"
    />

    <!-- 批量录入对话框 -->
    <BulkEntryDialog
      v-model="bulkEntryVisible"
      @success="handleBulkEntrySuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, DocumentAdd } from '@element-plus/icons-vue'
import GradeEntryDialog from '@/components/GradeEntryDialog.vue'
import BulkEntryDialog from '@/components/BulkEntryDialog.vue'
import { gradeApi } from '@/api'

// 响应式数据
const loading = ref(false)
const gradeList = ref([])
const total = ref(0)
const selectedIds = ref([])
const entryDialogVisible = ref(false)
const bulkEntryVisible = ref(false)
const currentGrade = ref(null)

// 查询参数
const queryParams = reactive({
  page: 1,
  per_page: 20,
  keyword: '',
  course_id: '',
  exam_type: '',
  semester: '',
  is_published: null
})

// 课程选项
const courseOptions = ref([
  { label: 'CS101 - 计算机科学导论', value: '1' },
  { label: 'SE201 - 软件工程', value: '2' },
  { label: 'DS301 - 数据结构与算法', value: '3' },
  { label: 'AI401 - 人工智能导论', value: '4' },
  { label: 'DB201 - 数据库系统', value: '5' },
  { label: 'ML501 - 机器学习', value: '6' }
])

// 获取成绩列表
const getList = async () => {
  try {
    loading.value = true
    const params = {
      ...queryParams,
      is_published: queryParams.is_published
    }

    const response = await gradeApi.getGrades(params)
    gradeList.value = response.data.grades
    total.value = response.data.total
  } catch (error) {
    console.error('获取成绩列表失败:', error)
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
    per_page: 20,
    keyword: '',
    course_id: '',
    exam_type: '',
    semester: '',
    is_published: null
  })
  getList()
}

// 分页处理
const handleSizeChange = (val: number) => {
  queryParams.per_page = val
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
  currentGrade.value = null
  entryDialogVisible.value = true
}

const handleEdit = (row: any) => {
  currentGrade.value = row
  entryDialogVisible.value = true
}

const handleView = (row: any) => {
  // 可以跳转到详情页或显示详情对话框
  ElMessage.info('查看成绩详情功能待开发')
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

    await gradeApi.deleteGrade(row.id)
    ElMessage.success('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handlePublish = async (row: any) => {
  try {
    await gradeApi.publishGrade(row.id)
    ElMessage.success('成绩发布成功')
    getList()
  } catch (error) {
    console.error('发布失败:', error)
    ElMessage.error('发布失败')
  }
}

const handleBulkEntry = () => {
  bulkEntryVisible.value = true
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

    // 批量发布逻辑
    for (const id of selectedIds.value) {
      await gradeApi.publishGrade(id)
    }

    ElMessage.success(`批量发布 ${selectedIds.value.length} 条成绩成功`)
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量发布失败:', error)
      ElMessage.error('批量发布失败')
    }
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这 ${selectedIds.value.length} 条成绩记录吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 批量删除逻辑
    for (const id of selectedIds.value) {
      await gradeApi.deleteGrade(id)
    }

    ElMessage.success(`批量删除 ${selectedIds.value.length} 条成绩成功`)
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 对话框成功回调
const handleEntrySuccess = () => {
  entryDialogVisible.value = false
  getList()
}

const handleBulkEntrySuccess = () => {
  bulkEntryVisible.value = false
  getList()
}

// 工具函数
const getGradeTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    quiz: 'info',
    assignment: 'primary',
    midterm: 'warning',
    final: 'danger',
    project: 'success',
    presentation: 'success',
    lab: 'warning',
    other: 'info'
  }
  return typeMap[type] || 'info'
}

const getGradeTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    quiz: '测验',
    assignment: '作业',
    midterm: '期中考试',
    final: '期末考试',
    project: '项目',
    presentation: '演讲',
    lab: '实验课',
    other: '其他'
  }
  return typeMap[type] || type
}

const getScoreColor = (score: number, maxScore: number) => {
  const percentage = (score / maxScore) * 100
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 初始化
onMounted(() => {
  getList()
})
</script>

<style lang="scss" scoped>
.grade-management {
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