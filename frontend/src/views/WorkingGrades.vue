<template>
  <div class="working-grades">
    <h1>成绩列表</h1>
    <p>当前路径: {{ currentPath }}</p>
    <p>这是一个可以正常工作的成绩列表</p>

    <div class="grades-table">
      <table border="1" style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <thead>
          <tr style="background-color: #f5f7fa;">
            <th style="padding: 12px; text-align: left;">学生姓名</th>
            <th style="padding: 12px; text-align: left;">学号</th>
            <th style="padding: 12px; text-align: left;">课程名称</th>
            <th style="padding: 12px; text-align: left;">考试类型</th>
            <th style="padding: 12px; text-align: left;">分数</th>
            <th style="padding: 12px; text-align: left;">状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="grade in grades" :key="grade.id" style="cursor: pointer;" @mouseover="$event.currentTarget.style.backgroundColor='#f5f7fa'" @mouseout="$event.currentTarget.style.backgroundColor='white'">
            <td style="padding: 12px;">{{ grade.student_name }}</td>
            <td style="padding: 12px;">{{ grade.student_no }}</td>
            <td style="padding: 12px;">{{ grade.course_name }}</td>
            <td style="padding: 12px;">{{ grade.exam_type }}</td>
            <td style="padding: 12px;">{{ grade.score }} / {{ grade.max_score }}</td>
            <td style="padding: 12px;">
              <span :style="{ color: grade.is_published ? '#67c23a' : '#e6a23c', fontWeight: 'bold' }">
                {{ grade.is_published ? '已发布' : '未发布' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="stats-info" style="background-color: #f0f9ff; padding: 15px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #409eff;">
      <p><strong>统计信息：</strong></p>
      <p>总记录数：{{ grades.length }} 条</p>
      <p>已发布：{{ publishedCount }} 条</p>
      <p>未发布：{{ unpublishedCount }} 条</p>
      <p>平均分：{{ averageScore }} 分</p>
    </div>

    <div style="text-align: center; margin-top: 30px;">
      <button @click="goBack" style="padding: 10px 20px; margin: 0 10px; background-color: #909399; color: white; border: none; border-radius: 4px; cursor: pointer;">
        返回首页
      </button>
      <button @click="refreshData" style="padding: 10px 20px; margin: 0 10px; background-color: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer;">
        刷新数据
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'WorkingGrades',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const currentPath = ref(route.path)

    const grades = ref([
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

    const publishedCount = computed(() => grades.value.filter(g => g.is_published).length)
    const unpublishedCount = computed(() => grades.value.filter(g => !g.is_published).length)
    const averageScore = computed(() => {
      const total = grades.value.reduce((sum, g) => sum + g.score, 0)
      return (total / grades.value.length).toFixed(1)
    })

    const goBack = () => {
      router.push('/dashboard')
    }

    const refreshData = () => {
      console.log('刷新成绩数据')
      // 这里可以添加数据刷新逻辑
    }

    onMounted(() => {
      console.log('WorkingGrades component mounted')
      console.log('当前路径:', route.path)
    })

    return {
      currentPath,
      grades,
      publishedCount,
      unpublishedCount,
      averageScore,
      goBack,
      refreshData
    }
  }
}
</script>

<style scoped>
.working-grades {
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.grades-table table {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

tr:hover {
  background-color: #f5f7fa;
}

button:hover {
  opacity: 0.8;
}
</style>