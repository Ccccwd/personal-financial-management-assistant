<template>
  <div class="not-found-container">
    <div class="content">
      <h1 class="error-code">404</h1>
      <p class="error-message">抱歉，您访问的页面不存在</p>
      <p class="error-description">请检查您输入的网址是否正确，或点击下方按钮返回首页</p>
      <el-button type="primary" size="large" @click="router.push('/dashboard')">
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<style scoped>
.not-found-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  color: #409eff;
  margin: 0;
  line-height: 1;
}

.error-message {
  font-size: 24px;
  color: #303133;
  margin: 20px 0 10px;
}

.error-description {
  font-size: 14px;
  color: #909399;
  margin-bottom: 30px;
}
</style>
