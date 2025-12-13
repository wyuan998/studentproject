<template>
  <div class="forbidden-container">
    <div class="forbidden-content">
      <div class="error-code">403</div>
      <div class="error-message">访问被拒绝</div>
      <div class="error-description">
        抱歉，您没有权限访问此页面
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
      <el-icon size="200" color="#e6a23c">
        <Lock />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Lock } from '@element-plus/icons-vue'

const router = useRouter()
</script>

<style lang="scss" scoped>
.forbidden-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.forbidden-content {
  text-align: center;
  max-width: 500px;

  .error-code {
    font-size: 120px;
    font-weight: bold;
    color: #e6a23c;
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
}

@media (max-width: 768px) {
  .forbidden-container {
    flex-direction: column;
    padding: 40px 20px;
  }

  .forbidden-content {
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
  }
}
</style>