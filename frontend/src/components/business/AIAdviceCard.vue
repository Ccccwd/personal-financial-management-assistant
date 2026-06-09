<template>
  <el-card shadow="hover" :class="['advice-card', `advice-card--${type}`]">
    <template #header>
      <div class="advice-header">
        <span :class="['advice-icon', `advice-icon--${type}`]">{{ iconMap[type] }}</span>
        <span class="advice-title">{{ title }}</span>
        <el-tag size="small" :type="tagTypeMap[type]" round>{{ items.length }}条</el-tag>
      </div>
    </template>
    <div v-if="items.length === 0" class="advice-empty">暂无内容</div>
    <ul v-else class="advice-list">
      <li v-for="(item, idx) in items" :key="idx" class="advice-item">
        <span :class="['item-dot', `item-dot--${type}`]"></span>
        <span class="item-text">{{ item }}</span>
      </li>
    </ul>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  type: 'highlight' | 'warning' | 'suggestion'
  items: string[]
}>()

const iconMap: Record<string, string> = {
  highlight: '✦',
  warning: '⚠',
  suggestion: '💡',
}

const tagTypeMap: Record<string, string> = {
  highlight: 'success',
  warning: 'warning',
  suggestion: 'info',
}
</script>

<style scoped>
.advice-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.advice-card--highlight { border-left: 4px solid #16A34A; }
.advice-card--warning { border-left: 4px solid #F59E0B; }
.advice-card--suggestion { border-left: 4px solid #3B82F6; }

.advice-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.advice-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.advice-icon--highlight { background: #f0fdf4; color: #16A34A; }
.advice-icon--warning { background: #fffbeb; color: #F59E0B; }
.advice-icon--suggestion { background: #eff6ff; color: #3B82F6; }

.advice-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  flex: 1;
}

.advice-empty {
  text-align: center;
  padding: 20px 0;
  color: #9ca3af;
  font-size: 14px;
}

.advice-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.advice-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
}

.advice-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.item-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-top: 8px;
  flex-shrink: 0;
}

.item-dot--highlight { background: #16A34A; }
.item-dot--warning { background: #F59E0B; }
.item-dot--suggestion { background: #3B82F6; }

.item-text {
  flex: 1;
}
</style>
