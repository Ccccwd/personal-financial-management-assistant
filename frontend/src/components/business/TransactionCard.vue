<template>
  <div class="transaction-item">
    <div class="item-left">
      <!-- 分类图标：优先显示 emoji，无则用类型色块 -->
      <div
        class="category-icon"
        :style="iconStyle"
      >
        <span v-if="transaction.category_icon" class="icon-emoji">{{ transaction.category_icon }}</span>
        <span v-else class="icon-fallback">{{ typeFallback }}</span>
      </div>

      <div class="item-info">
        <div class="item-title">
          {{ transaction.merchant_name || transaction.category_name || typeLabel }}
        </div>
        <div class="item-meta">
          <span class="account-name">{{ transaction.account_name }}</span>
          <span v-if="transaction.remark" class="meta-dot">·</span>
          <span v-if="transaction.remark" class="remark">{{ shortRemark }}</span>
        </div>
      </div>
    </div>

    <div class="item-right">
      <div class="item-amount" :class="amountClass">
        {{ formatAmount(transaction.amount, transaction.type) }}
      </div>
      <div class="item-time">{{ formatTime(transaction.transaction_date) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, PropType } from 'vue'
import dayjs from 'dayjs'
import type { Transaction } from '@/types/transaction'

const props = defineProps({
  transaction: {
    type: Object as PropType<Transaction>,
    required: true,
  },
})

// 收支类型对应的备用颜色和符号
const TYPE_META: Record<string, { bg: string; symbol: string; label: string }> = {
  income:   { bg: '#16a34a', symbol: '收', label: '收入' },
  expense:  { bg: '#ef4444', symbol: '支', label: '支出' },
  transfer: { bg: '#9ca3af', symbol: '转', label: '转账' },
}

const typeMeta = computed(() => TYPE_META[props.transaction.type] ?? TYPE_META.expense)
const typeFallback = computed(() => typeMeta.value.symbol)
const typeLabel    = computed(() => typeMeta.value.label)

const iconStyle = computed(() => {
  if (props.transaction.category_icon) {
    // 有 emoji：使用分类颜色或浅灰背景
    const color = (props.transaction as any).category_color
    return color
      ? { background: `linear-gradient(135deg, ${color}CC, ${color}88)` }
      : { background: '#f3f4f6' }
  }
  // 无 emoji：用类型色
  return { background: typeMeta.value.bg }
})

const amountClass = computed(() => ({
  'is-income':   props.transaction.type === 'income',
  'is-expense':  props.transaction.type === 'expense',
  'is-transfer': props.transaction.type === 'transfer',
}))

const formatAmount = (amount: number, type: string) => {
  const num = Math.abs(amount).toFixed(2)
  if (type === 'income')  return `+${num}`
  if (type === 'expense') return `-${num}`
  return num
}

const formatTime = (dateStr: string) => dayjs(dateStr).format('HH:mm')

const shortRemark = computed(() => {
  const r = props.transaction.remark ?? ''
  return r.length > 12 ? r.substring(0, 12) + '…' : r
})
</script>

<style scoped>
.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.15s;
  cursor: pointer;
}

.transaction-item:last-child {
  border-bottom: none;
}

.transaction-item:hover {
  background-color: #f9fafb;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.category-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-emoji {
  font-size: 22px;
  line-height: 1;
}

.icon-fallback {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-dot {
  color: #d1d5db;
}

.remark {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-right {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  margin-left: 12px;
}

.item-amount {
  font-size: 15px;
  font-weight: 600;
}

.item-amount.is-income   { color: #16a34a; }
.item-amount.is-expense  { color: #111827; }
.item-amount.is-transfer { color: #6b7280; }

.item-time {
  font-size: 12px;
  color: #9ca3af;
}
</style>
