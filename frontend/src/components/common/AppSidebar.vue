<template>
  <el-aside width="240px" class="layout-aside">
    <div class="logo">
      <el-icon class="logo-icon"><Wallet /></el-icon>
      <span class="logo-text">个人记账系统</span>
    </div>
    
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      router
      :border="false"
    >
      <el-menu-item index="/dashboard">
        <el-icon><Odometer /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>
      <el-menu-item index="/transactions">
        <el-icon><List /></el-icon>
        <span>交易记录</span>
      </el-menu-item>
      <el-menu-item index="/accounts">
        <el-icon><CreditCard /></el-icon>
        <span>账户管理</span>
      </el-menu-item>
      <el-menu-item index="/budgets">
        <el-icon><Calendar /></el-icon>
        <span>预算管理</span>
      </el-menu-item>
      <el-menu-item index="/statistics">
        <el-icon><DataLine /></el-icon>
        <span>统计分析</span>
      </el-menu-item>
      <el-menu-item index="/import">
        <el-icon><Upload /></el-icon>
        <span>数据导入</span>
      </el-menu-item>
      <el-menu-item index="/settings">
        <el-icon><User /></el-icon>
        <span>个人设置</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Odometer,
  List,
  CreditCard,
  DataLine,
  Calendar,
  Upload,
  Wallet,
  User
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.layout-aside {
  background-color: #fff;
  border-right: 1px solid #e5e7eb; /* color-border */
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #f9fafb;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
  color: #16A34A; /* color-primary */
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #111827; /* color-text-primary */
}

.el-menu-vertical {
  border-right: none;
  flex: 1;
}

:deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 8px;
  height: 48px;
  line-height: 48px;
}

:deep(.el-menu-item.is-active) {
  background-color: #f0fdf4; /* Light green */
  color: #16A34A;
  font-weight: 600;
}

:deep(.el-menu-item:hover:not(.is-active)) {
  background-color: #f9fafb;
}
</style>
