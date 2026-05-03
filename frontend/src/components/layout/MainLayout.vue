<template>
  <el-container class="layout-container">
    <AppSidebar />
    <el-container class="main-body-container">
      <AppHeader />
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
import AppSidebar from '@/components/common/AppSidebar.vue'
import AppHeader from '@/components/common/AppHeader.vue'
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #F9FAFB; /* color-bg */
  display: flex;
}

.main-body-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-main {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* Page transition styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
