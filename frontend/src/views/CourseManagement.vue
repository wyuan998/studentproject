<template>
  <div class="coming-soon">
    <el-card>
      <div class="content">
        <div class="icon">
          <el-icon size="80"><Reading /></el-icon>
        </div>
        <h2>课程管理</h2>
        <p>课程管理功能正在开发中...</p>
        <el-button type="primary" @click="$router.push('/dashboard')">
          <el-icon><ArrowLeft /></el-icon>
          返回仪表板
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 课程管理页面 - 开发中占位
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
}

.icon {
  margin-bottom: 20px;
  color: #e6a23c;
  opacity: 0.8;
}

h2 {
  color: #303133;
  margin-bottom: 12px;
}
</style>