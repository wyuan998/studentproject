<template>
  <div class="coming-soon">
    <el-card>
      <div class="content">
        <div class="icon">
          <el-icon size="80"><Tools /></el-icon>
        </div>
        <h2>学生管理</h2>
        <p>学生管理功能正在开发中...</p>
        <p style="margin-top: 20px; color: #909399;">
          此模块将包含以下功能：
        </p>
        <ul class="feature-list">
          <li>学生信息录入和管理</li>
          <li>学生信息查询和搜索</li>
          <li>学生档案管理</li>
          <li>学生成绩查看</li>
        </ul>
        <div style="margin-top: 30px;">
          <el-button type="primary" @click="$router.push('/dashboard')">
            <el-icon><ArrowLeft /></el-icon>
            返回仪表板
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 学生管理页面 - 开发中占位
</script>

<style scoped>
.coming-soon {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.content {
  text-align: center;
  padding: 40px;
  max-width: 500px;
}

.icon {
  margin-bottom: 20px;
  color: #409eff;
  opacity: 0.8;
}

h2 {
  color: #303133;
  margin-bottom: 12px;
}

.feature-list {
  text-align: left;
  color: #606266;
  line-height: 1.8;
  max-width: 300px;
  margin: 20px auto 0;
}

.feature-list li {
  margin-bottom: 8px;
  position: relative;
  padding-left: 20px;
}

.feature-list li::before {
  content: "•";
  color: #409eff;
  font-weight: bold;
  position: absolute;
  left: 0;
}
</style>