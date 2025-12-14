<template>
  <div>
    <h1>调试页面</h1>
    <p>当前时间: {{ currentTime }}</p>
    <p>当前路径: {{ $route.path }}</p>
    <button @click="testClick">测试点击</button>
    <p v-if="clicked">按钮被点击了！</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const currentTime = ref('')
const clicked = ref(false)

onMounted(() => {
  console.log('DebugPage mounted')
  currentTime.value = new Date().toLocaleString()
})

const testClick = () => {
  console.log('Test button clicked')
  clicked.value = true
  alert('按钮点击测试成功！')
}
</script>

<style scoped>
div {
  padding: 20px;
  text-align: center;
}

button {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 10px;
}

button:hover {
  background-color: #337ecc;
}
</style>