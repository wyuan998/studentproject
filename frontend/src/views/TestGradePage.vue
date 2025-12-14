<template>
  <div class="test-grade-page">
    <h1>测试成绩页面</h1>
    <p>这是一个简化的测试页面，用于验证成绩数据是否能正常显示</p>

    <div class="test-section">
      <h2>API测试</h2>
      <el-button @click="testAPI" type="primary">测试成绩API</el-button>
      <div v-if="apiResult" class="api-result">
        <h3>API结果:</h3>
        <pre>{{ JSON.stringify(apiResult, null, 2) }}</pre>
      </div>
    </div>

    <div class="test-section">
      <h2>直接显示成绩数据</h2>
      <el-button @click="loadGrades" type="success">加载成绩数据</el-button>
      <div v-if="grades.length > 0" class="grades-display">
        <table border="1" style="border-collapse: collapse; margin-top: 20px;">
          <thead>
            <tr>
              <th>学生姓名</th>
              <th>学号</th>
              <th>课程名称</th>
              <th>分数</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="grade in grades" :key="grade.id">
              <td>{{ grade.student_name }}</td>
              <td>{{ grade.student_no }}</td>
              <td>{{ grade.course_name }}</td>
              <td>{{ grade.score }} / {{ grade.max_score }}</td>
              <td>{{ grade.is_published ? '已发布' : '未发布' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="test-section">
      <h2>用户信息</h2>
      <el-button @click="checkUser" type="info">检查用户登录状态</el-button>
      <div v-if="userInfo" class="user-info">
        <p><strong>用户名:</strong> {{ userInfo.username }}</p>
        <p><strong>角色:</strong> {{ userInfo.role }}</p>
        <p><strong>是否登录:</strong> {{ isLoggedIn ? '是' : '否' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const apiResult = ref(null)
const grades = ref([])
const userInfo = ref(null)
const isLoggedIn = ref(false)

const testAPI = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/grades')
    const result = await response.json()
    apiResult.value = result
    ElMessage.success('API测试成功')
  } catch (error) {
    console.error('API测试失败:', error)
    ElMessage.error('API测试失败')
    apiResult.value = { error: error.message }
  }
}

const loadGrades = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/grades')
    const result = await response.json()
    grades.value = result.data?.grades || []
    ElMessage.success(`成功加载 ${grades.value.length} 条成绩记录`)
  } catch (error) {
    console.error('加载成绩失败:', error)
    ElMessage.error('加载成绩失败')
  }
}

const checkUser = async () => {
  // 检查localStorage中的用户信息
  const token = localStorage.getItem('token')
  const storedUserInfo = localStorage.getItem('userInfo')

  if (token && storedUserInfo) {
    try {
      userInfo.value = JSON.parse(storedUserInfo)
      isLoggedIn.value = true
      ElMessage.success('用户已登录')
    } catch (error) {
      userInfo.value = { error: '无法解析用户信息' }
      isLoggedIn.value = false
    }
  } else {
    userInfo.value = { message: '未找到登录信息' }
    isLoggedIn.value = false
    ElMessage.warning('用户未登录')
  }
}
</script>

<style scoped>
.test-grade-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.test-section h2 {
  margin-top: 0;
  color: #409eff;
}

.api-result {
  margin-top: 15px;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.api-result pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.grades-display table {
  width: 100%;
}

.grades-display th,
.grades-display td {
  padding: 8px 12px;
  text-align: left;
  border: 1px solid #ddd;
}

.grades-display th {
  background-color: #f5f7fa;
  font-weight: bold;
}

.user-info {
  margin-top: 15px;
  padding: 15px;
  background-color: #f0f9ff;
  border-radius: 4px;
}

.user-info p {
  margin: 5px 0;
}
</style>