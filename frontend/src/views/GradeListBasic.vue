<template>
  <div class="grade-list-basic">
    <h1>成绩列表</h1>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else>
      <div class="stats">
        <p>总共 {{ total }} 条成绩记录</p>
      </div>

      <table class="grade-table">
        <thead>
          <tr>
            <th>学生姓名</th>
            <th>学号</th>
            <th>课程代码</th>
            <th>课程名称</th>
            <th>考试类型</th>
            <th>分数</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="grade in gradeList" :key="grade.id">
            <td>{{ grade.student_name }}</td>
            <td>{{ grade.student_no }}</td>
            <td>{{ grade.course_code }}</td>
            <td>{{ grade.course_name }}</td>
            <td>{{ getExamTypeText(grade.exam_type) }}</td>
            <td>{{ grade.score }} / {{ grade.max_score }}</td>
            <td>
              <span :class="grade.is_published ? 'published' : 'unpublished'">
                {{ grade.is_published ? '已发布' : '未发布' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="gradeList.length === 0" class="no-data">
        暂无成绩数据
      </div>
    </div>

    <div class="actions">
      <button @click="$router.push('/dashboard')">返回首页</button>
      <button @click="$router.push('/test-grades')">测试页面</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const error = ref('')
const gradeList = ref([])
const total = ref(0)

const getExamTypeText = (type: string) => {
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

const loadGrades = async () => {
  try {
    loading.value = true
    error.value = ''

    console.log('开始加载成绩数据...')

    const response = await fetch('http://localhost:5000/api/grades')

    console.log('Response status:', response.status)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()

    console.log('API result:', result)

    if (result.success) {
      gradeList.value = result.data.grades || []
      total.value = result.data.total || 0
      console.log('成绩数据加载成功，共', gradeList.value.length, '条记录')
    } else {
      throw new Error(result.message || '获取成绩数据失败')
    }
  } catch (err) {
    console.error('加载成绩数据失败:', err)
    error.value = `加载失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  console.log('GradeListBasic component mounted')
  console.log('当前路由:', window.location.pathname)
  loadGrades()
})
</script>

<style scoped>
.grade-list-basic {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 30px;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 40px;
  font-size: 18px;
}

.error {
  color: #f56c6c;
  background-color: #fef0f0;
  border: 1px solid #f56c6c;
  border-radius: 4px;
}

.stats {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.grade-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.grade-table th,
.grade-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.grade-table th {
  background-color: #f5f7fa;
  font-weight: bold;
  color: #333;
  position: sticky;
  top: 0;
}

.grade-table tr:hover {
  background-color: #f5f7fa;
}

.published {
  color: #67c23a;
  font-weight: bold;
}

.unpublished {
  color: #e6a23c;
  font-weight: bold;
}

.actions {
  text-align: center;
  margin-top: 30px;
}

.actions button {
  margin: 0 10px;
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.actions button:hover {
  background-color: #337ecc;
}

.no-data {
  color: #909399;
  font-style: italic;
}
</style>