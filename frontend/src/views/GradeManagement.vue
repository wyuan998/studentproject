<template>
  <div class="grade-management">
    <div class="page-header">
      <div class="header-content">
        <h2>成绩管理</h2>
        <p class="page-description">管理学生成绩信息，支持录入、修改、统计和分析</p>
      </div>
    </div>

    <div class="toolbar">
      <div class="search-bar">
        <el-input
          v-model="gradeSearchQuery"
          placeholder="搜索学生姓名、学号、课程名称..."
          @input="handleGradeSearch"
          clearable
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="action-buttons">
        <el-button type="primary" @click="handleAddGrade">
          <el-icon><Plus /></el-icon>
          录入成绩
        </el-button>
        <el-button @click="handleImportGrades">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="handleExportGrades">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        <el-button type="danger" :disabled="!selectedGrades.length" @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </div>
    </div>

    <el-card class="table-card">
      <el-table
        :data="filteredGrades"
        @selection-change="handleGradeSelectionChange"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        empty-text="暂无数据"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="student_name" label="学生姓名" width="120" />
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="course_name" label="课程名称" width="200" show-overflow-tooltip />
        <el-table-column prop="exam_type" label="考试类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getExamTypeTag(row.exam_type)">
              {{ getExamTypeText(row.exam_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分数" width="150">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score, row.max_score), fontWeight: 'bold' }">
              {{ row.score }} / {{ row.max_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="percentage" label="百分比" width="100">
          <template #default="{ row }">
            {{ getPercentage(row.score, row.max_score) }}%
          </template>
        </el-table-column>
        <el-table-column prop="is_published" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'warning'">
              {{ row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleViewGrade(row)">
              查看
            </el-button>
            <el-button type="primary" size="small" link @click="handleEditGrade(row)">
              编辑
            </el-button>
            <el-button v-if="!row.is_published" type="success" size="small" link @click="handlePublishGrade(row)">
              发布
            </el-button>
            <el-button type="danger" size="small" link @click="handleDeleteGrade(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ gradesData.length }}</div>
                <div class="stat-label">总记录数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon published">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ publishedCount }}</div>
                <div class="stat-label">已发布</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon unpublished">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ unpublishedCount }}</div>
                <div class="stat-label">未发布</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon average">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ averageScore }}</div>
                <div class="stat-label">平均分</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <GradeEntryDialog
      v-model="gradeEntryDialogVisible"
      :grade="currentGrade"
      @success="handleGradeDialogSuccess"
      @error="handleGradeDialogError"
    />

    <GradeDetailDialog
      v-model="gradeDetailDialogVisible"
      :grade="selectedGradeForDetail"
    />

    <GradeImportDialog
      v-model="gradeImportDialogVisible"
      @success="handleImportDialogSuccess"
      @error="handleImportDialogError"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Upload, Download, Delete, Document,
  Check, Clock, TrendCharts, Edit, View
} from '@element-plus/icons-vue'
import GradeEntryDialog from '@/components/GradeEntryDialog.vue'
import GradeDetailDialog from '@/components/GradeDetailDialog.vue'
import GradeImportDialog from '@/components/GradeImportDialog.vue'
import { gradeApi } from '@/api'

const gradeSearchQuery = ref('')
const selectedGrades = ref([])
const loading = ref(false)
const gradeEntryDialogVisible = ref(false)
const gradeDetailDialogVisible = ref(false)
const gradeImportDialogVisible = ref(false)
const currentGrade = ref(null)
const selectedGradeForDetail = ref(null)

const gradesData = ref([
  {
    id: 1,
    student_name: '张三',
    student_no: 'S2021001',
    course_name: '计算机科学导论',
    exam_type: '期中考试',
    score: 85,
    max_score: 100,
    is_published: true
  },
  {
    id: 2,
    student_name: '张三',
    student_no: 'S2021001',
    course_name: '计算机科学导论',
    exam_type: '期末考试',
    score: 88,
    max_score: 100,
    is_published: true
  },
  {
    id: 3,
    student_name: '李四',
    student_no: 'S2021002',
    course_name: '计算机科学导论',
    exam_type: '期中考试',
    score: 92,
    max_score: 100,
    is_published: true
  },
  {
    id: 4,
    student_name: '李四',
    student_no: 'S2021002',
    course_name: '软件工程',
    exam_type: '作业',
    score: 95,
    max_score: 100,
    is_published: true
  },
  {
    id: 5,
    student_name: '王五',
    student_no: 'S2021003',
    course_name: '软件工程',
    exam_type: '测验',
    score: 76,
    max_score: 100,
    is_published: false
  },
  {
    id: 6,
    student_name: '王五',
    student_no: 'S2021003',
    course_name: '数据结构与算法',
    exam_type: '项目',
    score: 82,
    max_score: 100,
    is_published: true
  }
])

const filteredGrades = computed(() => {
  if (!gradeSearchQuery.value) return gradesData.value
  const query = gradeSearchQuery.value.toLowerCase()
  return gradesData.value.filter(grade =>
    grade.student_name.toLowerCase().includes(query) ||
    grade.student_no.toLowerCase().includes(query) ||
    grade.course_name.toLowerCase().includes(query) ||
    grade.exam_type.toLowerCase().includes(query)
  )
})

const publishedCount = computed(() => gradesData.value.filter(g => g.is_published).length)
const unpublishedCount = computed(() => gradesData.value.filter(g => !g.is_published).length)
const averageScore = computed(() => {
  const total = gradesData.value.reduce((sum, g) => sum + g.score, 0)
  return (total / gradesData.value.length).toFixed(1)
})

const loadGrades = async () => {
  try {
    loading.value = true
    console.log('开始加载成绩数据...')
    const response = await gradeApi.getGrades({
      page: 1,
      per_page: 100
    })
    console.log('API响应:', response)

    // 如果API返回数据，使用API数据；否则使用本地数据
    if (response && response.data && response.data.grades && response.data.grades.length > 0) {
      gradesData.value = response.data.grades
      console.log('使用API数据:', response.data.grades.length, '条记录')
      console.log('第一条成绩记录:', response.data.grades[0])
      console.log('当前gradesData长度:', gradesData.value.length)
    } else {
      console.log('API返回空数据，使用本地默认数据')
      console.log('response:', response)
    }
  } catch (error) {
    console.error('加载成绩数据失败:', error)
    console.log('使用本地默认数据')
    // 不显示错误消息，因为我们将使用本地数据
  } finally {
    loading.value = false
    console.log('成绩数据加载完成，最终数据长度:', gradesData.value.length)
  }
}

const handleGradeSearch = () => {
  console.log('搜索成绩:', gradeSearchQuery.value)
}

const handleAddGrade = () => {
  currentGrade.value = null
  gradeEntryDialogVisible.value = true
}

const handleImportGrades = () => {
  gradeImportDialogVisible.value = true
}

const handleExportGrades = async () => {
  try {
    const response = await gradeApi.exportGrades({
      format: 'excel'
    })

    const blob = new Blob([response], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `成绩单_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('成绩数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出成绩数据失败')
  }
}

const handleBatchDelete = async () => {
  if (!selectedGrades.value.length) {
    ElMessage.warning('请选择要删除的成绩记录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedGrades.value.length} 条成绩记录吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const deletePromises = selectedGrades.value.map(grade =>
      gradeApi.deleteGrade(grade.id.toString())
    )

    await Promise.all(deletePromises)

    ElMessage.success(`成功删除 ${selectedGrades.value.length} 条成绩记录`)
    await loadGrades()
    selectedGrades.value = []
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

const handleGradeSelectionChange = (selection) => {
  selectedGrades.value = selection
}

const handleViewGrade = async (row) => {
  try {
    const grade = await gradeApi.getGrade(row.id.toString())
    selectedGradeForDetail.value = grade
    gradeDetailDialogVisible.value = true
  } catch (error) {
    console.error('获取成绩详情失败:', error)
    ElMessage.error('获取成绩详情失败')
  }
}

const handleEditGrade = (row) => {
  currentGrade.value = row
  gradeEntryDialogVisible.value = true
}

const handlePublishGrade = async (row) => {
  try {
    await gradeApi.publishGrade(row.id.toString())
    row.is_published = true
    ElMessage.success('成绩已发布')
  } catch (error) {
    console.error('发布成绩失败:', error)
    ElMessage.error('发布成绩失败')
  }
}

const handleDeleteGrade = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.student_name} 的成绩记录吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await gradeApi.deleteGrade(row.id.toString())
    ElMessage.success('成绩记录删除成功')
    await loadGrades()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除成绩失败:', error)
      ElMessage.error('删除成绩失败')
    }
  }
}

const handleGradeDialogSuccess = async () => {
  gradeEntryDialogVisible.value = false
  await loadGrades()
}

const handleGradeDialogError = (error) => {
  console.error('成绩操作失败:', error)
}

const handleImportDialogSuccess = async () => {
  gradeImportDialogVisible.value = false
  await loadGrades()
}

const handleImportDialogError = (error) => {
  console.error('批量导入失败:', error)
}

const getExamTypeTag = (type) => {
  const typeMap = {
    '期中考试': 'warning',
    '期末考试': 'danger',
    '作业': 'primary',
    '测验': 'info',
    '项目': 'success'
  }
  return typeMap[type] || 'info'
}

const getExamTypeText = (type) => {
  return type
}

const getScoreColor = (score, maxScore) => {
  const percentage = (score / maxScore) * 100
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

const getPercentage = (score, maxScore) => {
  return ((score / maxScore) * 100).toFixed(1)
}

onMounted(() => {
  loadGrades()
})
</script>

<style scoped>
.grade-management {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
  padding: 20px 0;
  border-bottom: 1px solid #e4e7ed;
}

.header-content h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.table-card {
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-cards {
  margin-top: 20px;
}

.stat-card {
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.published {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.unpublished {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-icon.average {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #666;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}
</style>