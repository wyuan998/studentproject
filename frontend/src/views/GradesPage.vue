<template>
  <div class="grades-container">
    <h1>成绩列表</h1>

    <div class="stats-info">
      <p>共找到 {{ grades.length }} 条成绩记录</p>
    </div>

    <div class="grades-table">
      <table>
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
          <tr v-for="grade in grades" :key="grade.id">
            <td>{{ grade.student_name }}</td>
            <td>{{ grade.student_no }}</td>
            <td>{{ grade.course_code }}</td>
            <td>{{ grade.course_name }}</td>
            <td>{{ getExamTypeName(grade.exam_type) }}</td>
            <td>{{ grade.score }} / {{ grade.max_score }}</td>
            <td>
              <span :class="grade.is_published ? 'published' : 'unpublished'">
                {{ grade.is_published ? '已发布' : '未发布' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="navigation-buttons">
      <button @click="goBack">返回首页</button>
      <button @click="refreshData">刷新数据</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const grades = ref([])

const getExamTypeName = (type) => {
  const typeMap = {
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
    // 模拟成绩数据
    grades.value = [
      {
        id: 1,
        student_name: '张三',
        student_no: 'S2021001',
        course_code: 'CS101',
        course_name: '计算机科学导论',
        exam_type: 'midterm',
        score: 85,
        max_score: 100,
        is_published: true
      },
      {
        id: 2,
        student_name: '张三',
        student_no: 'S2021001',
        course_code: 'CS101',
        course_name: '计算机科学导论',
        exam_type: 'final',
        score: 88,
        max_score: 100,
        is_published: true
      },
      {
        id: 3,
        student_name: '李四',
        student_no: 'S2021002',
        course_code: 'CS101',
        course_name: '计算机科学导论',
        exam_type: 'midterm',
        score: 92,
        max_score: 100,
        is_published: true
      },
      {
        id: 4,
        student_name: '李四',
        student_no: 'S2021002',
        course_code: 'SE201',
        course_name: '软件工程',
        exam_type: 'assignment',
        score: 95,
        max_score: 100,
        is_published: true
      },
      {
        id: 5,
        student_name: '王五',
        student_no: 'S2021003',
        course_code: 'SE201',
        course_name: '软件工程',
        exam_type: 'quiz',
        score: 76,
        max_score: 100,
        is_published: false
      },
      {
        id: 6,
        student_name: '王五',
        student_no: 'S2021003',
        course_code: 'DS301',
        course_name: '数据结构与算法',
        exam_type: 'project',
        score: 82,
        max_score: 100,
        is_published: true
      }
    ]
    console.log('成绩数据加载完成:', grades.value.length, '条记录')
  } catch (error) {
    console.error('加载成绩数据失败:', error)
  }
}

const goBack = () => {
  window.location.href = '/dashboard'
}

const refreshData = () => {
  console.log('刷新数据')
  loadGrades()
}

onMounted(() => {
  console.log('成绩页面已挂载')
  loadGrades()
})
</script>

<style scoped>
.grades-container {
  padding: 20px;
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.stats-info {
  background-color: #f0f9ff;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  border-left: 4px solid #409eff;
}

.grades-table {
  overflow-x: auto;
  margin-bottom: 30px;
}

table {
  width: 100%;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  background: white;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f7fa;
  font-weight: bold;
  color: #333;
  position: sticky;
  top: 0;
}

tr:hover {
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

.navigation-buttons {
  text-align: center;
  margin-top: 30px;
}

button {
  padding: 10px 20px;
  margin: 0 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

button:first-child {
  background-color: #909399;
  color: white;
}

button:first-child:hover {
  background-color: #767a82;
}

button:last-child {
  background-color: #409eff;
  color: white;
}

button:last-child:hover {
  background-color: #337ecc;
}
</style>