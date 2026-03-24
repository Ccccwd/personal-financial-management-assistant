<template>
  <el-container class="layout-container">
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
        <!-- Temporary disabled other menu items
        <el-menu-item index="/transactions">
          <el-icon><List /></el-icon>
          <span>交易记录</span>
        </el-menu-item>
        ...
        -->
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <!-- 可以在这里放面包屑 -->
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="el-dropdown-link user-info">
              <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span class="username">{{ userStore.user?.username || 'User' }}</span>
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  Odometer,
  List,
  CirclePlus,
  DataLine,
  Calendar,
  User,
  Upload,
  Wallet,
  ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #f5f7fa;
}

.layout-aside {
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #f0f0f0;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
  color: #409eff;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.el-menu-vertical {
  border-right: none;
  flex: 1;
}

.layout-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
}

.layout-main {
  padding: 20px;
  overflow-y: auto;
}

:deep(.el-menu-item) {
  margin: 4px 0;
}

:deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  border-right: 3px solid #409eff;
  color: #409eff;
}
</style>
