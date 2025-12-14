<template>
  <el-dialog
    v-model="visible"
    title="成绩详情"
    width="700px"
    @close="handleClose"
  >
    <div v-if="grade" class="grade-detail">
      <!-- 基本信息 -->
      <el-descriptions :column="2" border title="基本信息" class="mb-4">
        <el-descriptions-item label="学生姓名">
          {{ grade.student_name }}
        </el-descriptions-item>
        <el-descriptions-item label="学号">
          {{ grade.student_no || grade.student_id }}
        </el-descriptions-item>
        <el-descriptions-item label="课程名称">
          {{ grade.course_name || grade.course_code }}
        </el-descriptions-item>
        <el-descriptions-item label="考试类型">
          <el-tag :type="getExamTypeTag(grade.exam_type)">
            {{ getExamTypeText(grade.exam_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="考试名称">
          {{ grade.exam_name }}
        </el-descriptions-item>
        <el-descriptions-item label="学期">
          {{ grade.semester }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 成绩信息 -->
      <el-descriptions :column="3" border title="成绩信息" class="mb-4">
        <el-descriptions-item label="分数">
          <span :style="{ color: getScoreColor(grade.score, grade.max_score), fontWeight: 'bold' }">
            {{ grade.score }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="满分">
          {{ grade.max_score }}
        </el-descriptions-item>
        <el-descriptions-item label="百分比">
          {{ getPercentage(grade.score, grade.max_score) }}%
        </el-descriptions-item>
        <el-descriptions-item label="等级">
          <el-tag :type="getGradeTag(getPercentage(grade.score, grade.max_score))">
            {{ getGradeLevel(getPercentage(grade.score, grade.max_score)) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="绩点">
          {{ getGradePoint(getPercentage(grade.score, grade.max_score)) }}
        </el-descriptions-item>
        <el-descriptions-item label="权重">
          {{ grade.weight || 1.0 }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 班级对比 -->
      <el-descriptions :column="3" border title="班级对比" class="mb-4" v-if="grade.class_average">
        <el-descriptions-item label="班级平均分">
          {{ grade.class_average }}
        </el-descriptions-item>
        <el-descriptions-item label="班级最高分">
          {{ grade.class_max }}
        </el-descriptions-item>
        <el-descriptions-item label="班级最低分">
          {{ grade.class_min }}
        </el-descriptions-item>
        <el-descriptions-item label="排名百分位">
          {{ grade.percentile }}%
        </el-descriptions-item>
      </el-descriptions>

      <!-- 教师评语 -->
      <el-descriptions :column="1" border title="教师评语" class="mb-4" v-if="grade.comments">
        <el-descriptions-item>
          <div class="comments-content">{{ grade.comments }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 改进建议 -->
      <el-descriptions :column="1" border title="改进建议" class="mb-4" v-if="grade.improvement_suggestions">
        <el-descriptions-item>
          <div class="suggestions-content">{{ grade.improvement_suggestions }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 操作记录 -->
      <el-descriptions :column="2" border title="操作记录">
        <el-descriptions-item label="评分教师">
          {{ grade.graded_by || '系统' }}
        </el-descriptions-item>
        <el-descriptions-item label="评分时间">
          {{ formatDateTime(grade.graded_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="grade.is_published ? 'success' : 'warning'">
            {{ grade.is_published ? '已发布' : '未发布' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布时间">
          {{ formatDateTime(grade.published_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="锁定状态">
          <el-tag :type="grade.is_locked ? 'danger' : 'info'">
            {{ grade.is_locked ? '已锁定' : '未锁定' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(grade.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handlePrint">打印成绩单</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, toRefs } from 'vue'
import type { Grade } from '@/api'

const emit = defineEmits(['close'])

// 组件属性
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  grade: {
    type: Object as () => Grade | null,
    default: null
  }
})

// 响应式数据
const visible = ref(props.modelValue)

// 监听 modelValue 变化
const { modelValue } = toRefs(props)
watch(modelValue, (val) => {
  visible.value = val
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    emit('close')
  }
})

// 工具函数
const getExamTypeTag = (type: string) => {
  const typeMap: Record<string, string> = {
    'quiz': 'info',
    'assignment': 'primary',
    'midterm': 'warning',
    'final': 'danger',
    'project': 'success',
    'presentation': 'primary',
    'lab': 'info',
    'attendance': 'success',
    'other': 'info'
  }
  return typeMap[type] || 'info'
}

const getExamTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    'quiz': '测验',
    'assignment': '作业',
    'midterm': '期中考试',
    'final': '期末考试',
    'project': '项目',
    'presentation': '演讲',
    'lab': '实验课',
    'attendance': '出勤',
    'other': '其他'
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

const getPercentage = (score: number, maxScore: number) => {
  return ((score / maxScore) * 100).toFixed(1)
}

const getGradeLevel = (percentage: number) => {
  if (percentage >= 90) return '优秀'
  if (percentage >= 80) return '良好'
  if (percentage >= 70) return '中等'
  if (percentage >= 60) return '及格'
  return '不及格'
}

const getGradeTag = (percentage: number) => {
  if (percentage >= 90) return 'success'
  if (percentage >= 80) return 'primary'
  if (percentage >= 70) return 'warning'
  if (percentage >= 60) return 'info'
  return 'danger'
}

const getGradePoint = (percentage: number) => {
  if (percentage >= 90) return '4.0'
  if (percentage >= 85) return '3.7'
  if (percentage >= 82) return '3.3'
  if (percentage >= 78) return '3.0'
  if (percentage >= 75) return '2.7'
  if (percentage >= 72) return '2.3'
  if (percentage >= 68) return '2.0'
  if (percentage >= 64) return '1.5'
  if (percentage >= 60) return '1.0'
  return '0.0'
}

const formatDateTime = (dateTime: string | undefined) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 打印成绩单
const handlePrint = () => {
  if (!props.grade) return

  // 创建打印内容
  const printContent = `
    <div style="padding: 20px; font-family: Arial, sans-serif;">
      <h1 style="text-align: center; margin-bottom: 30px;">成绩单</h1>

      <div style="margin-bottom: 20px;">
        <h3>基本信息</h3>
        <p><strong>学生姓名：</strong>${props.grade.student_name}</p>
        <p><strong>学号：</strong>${props.grade.student_no || props.grade.student_id}</p>
        <p><strong>课程：</strong>${props.grade.course_name || props.grade.course_code}</p>
        <p><strong>考试类型：</strong>${getExamTypeText(props.grade.exam_type)}</p>
        <p><strong>考试名称：</strong>${props.grade.exam_name}</p>
        <p><strong>学期：</strong>${props.grade.semester}</p>
      </div>

      <div style="margin-bottom: 20px;">
        <h3>成绩信息</h3>
        <p><strong>分数：</strong>${props.grade.score} / ${props.grade.max_score}</p>
        <p><strong>百分比：</strong>${getPercentage(props.grade.score, props.grade.max_score)}%</p>
        <p><strong>等级：</strong>${getGradeLevel(getPercentage(props.grade.score, props.grade.max_score))}</p>
        <p><strong>绩点：</strong>${getGradePoint(getPercentage(props.grade.score, props.grade.max_score))}</p>
      </div>

      ${props.grade.comments ? `
      <div style="margin-bottom: 20px;">
        <h3>教师评语</h3>
        <p>${props.grade.comments}</p>
      </div>
      ` : ''}

      ${props.grade.improvement_suggestions ? `
      <div style="margin-bottom: 20px;">
        <h3>改进建议</h3>
        <p>${props.grade.improvement_suggestions}</p>
      </div>
      ` : ''}

      <div style="text-align: right; margin-top: 40px;">
        <p>打印时间：${new Date().toLocaleString('zh-CN')}</p>
      </div>
    </div>
  `

  // 创建打印窗口
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(`
      <html>
        <head>
          <title>成绩单 - ${props.grade.student_name}</title>
          <style>
            body { margin: 0; padding: 0; }
            @media print {
              body { margin: 0; }
            }
          </style>
        </head>
        <body>${printContent}</body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }
}
</script>

<style scoped>
.grade-detail {
  max-height: 600px;
  overflow-y: auto;
}

.mb-4 {
  margin-bottom: 16px;
}

.comments-content,
.suggestions-content {
  white-space: pre-wrap;
  line-height: 1.5;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-descriptions__body) {
  background-color: var(--el-fill-color-light);
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>