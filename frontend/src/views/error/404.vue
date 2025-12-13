<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被移除
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="router.push('/dashboard')">
          返回首页
        </el-button>
        <el-button @click="router.go(-1)">
          返回上页
        </el-button>
      </div>
    </div>
    <div class="error-image">
      <img src="/404.svg" alt="404" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style lang="scss" scoped>
.not-found-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.not-found-content {
  text-align: center;
  max-width: 500px;

  .error-code {
    font-size: 120px;
    font-weight: bold;
    color: #409eff;
    line-height: 1;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  }

  .error-message {
    font-size: 32px;
    color: #303133;
    margin-bottom: 16px;
    font-weight: 600;
  }

  .error-description {
    font-size: 16px;
    color: #606266;
    margin-bottom: 40px;
    line-height: 1.6;
  }

  .error-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
  }
}

.error-image {
  margin-left: 60px;

  img {
    width: 300px;
    height: auto;
    opacity: 0.8;
  }
}

@media (max-width: 768px) {
  .not-found-container {
    flex-direction: column;
    padding: 40px 20px;
  }

  .not-found-content {
    .error-code {
      font-size: 80px;
    }

    .error-message {
      font-size: 24px;
    }

    .error-actions {
      flex-direction: column;
    }
  }

  .error-image {
    margin-left: 0;
    margin-top: 40px;

    img {
      width: 200px;
    }
  }
}
</style>