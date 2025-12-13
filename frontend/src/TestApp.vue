<template>
  <div id="test-app">
    <h1>测试页面</h1>
    <p>如果你能看到这个页面，说明Vue应用正在运行</p>
    <el-button type="primary" @click="showMessage">点击测试</el-button>
    <div v-if="message" style="margin-top: 20px; padding: 10px; background: #f0f0f0;">
      {{ message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const message = ref('')

const showMessage = () => {
  message.value = '按钮点击成功！时间：' + new Date().toLocaleString()
  ElMessage.success('Element Plus 组件正常工作')
}
</script>

<style scoped>
#test-app {
  padding: 20px;
  text-align: center;
  font-family: Arial, sans-serif;
}

h1 {
  color: #409eff;
  margin-bottom: 20px;
}
</style>