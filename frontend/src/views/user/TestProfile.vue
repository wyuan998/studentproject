<template>
  <div style="padding: 20px;">
    <h1>个人信息页面测试</h1>
    <p>如果您能看到这个页面，说明路由配置正常。</p>
    <el-button type="primary" @click="showMessage">测试按钮</el-button>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'

const showMessage = () => {
  ElMessage.success('页面正常工作！')
}
</script>