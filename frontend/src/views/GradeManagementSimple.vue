<template>
  <div class="grade-management-simple">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>成绩管理</h2>
      <p>管理学生成绩信息</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-container">
      <el-form :model="queryParams" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="搜索学生姓名、学号、课程名称"
            clearable
            @keyup.enter="handleSearch"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            搜索
          </el-button>
          <el-button @click="resetQuery">
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
      >
        <el-table-column label="学生姓名" prop="student_name" width="120" />
        <el-table-column label="学号" prop="student_no" width="120" />
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
        <el-table-column label="状态" prop="is_published" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'warning'">
              {{ row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="录入时间" prop="graded_at" width="150">
          <template #default="{ row }">
            {{ formatDate(row.graded_at) }}
          </template>
        </el-table-column>
      </el-table>

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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 响应式数据
const loading = ref(false)
const gradeList = ref([])
const total = ref(0)

// 查询参数
const queryParams = reactive({
  page: 1,
  per_page: 20,
  keyword: ''
})

// 获取成绩列表
const getList = async () => {
  try {
    loading.value = true

    // 直接使用fetch API调用后端
    const params = new URLSearchParams({
      page: queryParams.page.toString(),
      per_page: queryParams.per_page.toString(),
      keyword: queryParams.keyword
    })

    const response = await fetch(`http://localhost:5000/api/grades?${params}`)
    const result = await response.json()

    if (result.success) {
      gradeList.value = result.data.grades
      total.value = result.data.total
    } else {
      ElMessage.error('获取成绩列表失败')
    }
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
    keyword: ''
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
.grade-management-simple {
  .page-header {
    margin-bottom: 20px;

    h2 {
      margin: 0 0 4px;
      font-size: 20px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    p {
      margin: 0;
      font-size: 14px;
      color: var(--el-text-color-regular);
    }
  }

  .filter-container {
    background-color: var(--el-bg-color);
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;
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