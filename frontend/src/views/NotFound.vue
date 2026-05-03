<template>
  <div class="not-found-container">
    <div class="content">
      <div class="icon-wrapper">
        <el-icon class="error-icon"><WarningFilled /></el-icon>
      </div>
      <h1 class="error-code">404</h1>
      <p class="error-message">页面未找到 (Not Found)</p>
      <p class="error-description">抱歉，您访问的页面不存在，请检查您输入的网址是否正确，或点击下方按钮返回。</p>
      <div class="options-container">
        <el-button type="primary" size="large" class="primary-btn" @click="router.push('/dashboard')">
          返回仪表盘
        </el-button>
        <el-button size="large" class="secondary-btn" @click="router.go(-1)">
          返回上一页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'

const router = useRouter()
</script>

<style scoped>
:root {
  --color-primary: #16A34A;
  --color-primary-hover: #15803D;
  --color-bg: #F9FAFB;
  --color-text-primary: #111827;
  --color-text-secondary: #4B5563;
  --color-accent: #F59E0B;
}

.not-found-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #F9FAFB; /* --color-bg */
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-image: radial-gradient(#16A34A 1px, transparent 1px);
  background-size: 40px 40px;
}

.content {
  text-align: center;
  background: white;
  padding: 64px 40px;
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  max-width: 480px;
  width: 90%;
}

.icon-wrapper {
  margin-bottom: 20px;
}

.error-icon {
  font-size: 64px;
  color: #F59E0B; /* --color-accent */
}

.error-code {
  font-size: 96px;
  font-weight: 800;
  color: #111827; /* --color-text-primary */
  margin: 0;
  line-height: 1;
  letter-spacing: -2px;
}

.error-message {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 16px 0 12px;
}

.error-description {
  font-size: 15px;
  color: #4B5563; /* --color-text-secondary */
  margin-bottom: 36px;
  line-height: 1.6;
}

.options-container {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.primary-btn {
  background-color: #16A34A;
  border-color: #16A34A;
  font-weight: 600;
  padding: 12px 24px;
}

.primary-btn:hover, .primary-btn:focus {
  background-color: #15803D;
  border-color: #15803D;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.3);
}

.primary-btn:active {
  transform: translateY(0);
}

.secondary-btn {
  font-weight: 600;
  padding: 12px 24px;
  color: #4B5563;
}

.secondary-btn:hover, .secondary-btn:focus {
  color: #111827;
  border-color: #D1D5DB;
  background-color: #F3F4F6;
}
</style>
