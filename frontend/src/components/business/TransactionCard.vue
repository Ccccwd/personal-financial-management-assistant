<template>
  <div class="transaction-item">
    <div class="item-left">
      <div 
        class="category-icon" 
        :style="{ backgroundColor: transaction.category_color || '#e5e7eb' }"
      >
        <span class="icon-text">{{ getCategoryInitial(transaction.category_name) }}</span>
      </div>
      <div class="item-info">
        <div class="item-title">
          {{ transaction.merchant_name || transaction.category_name || '未分类' }}
        </div>
        <div class="item-meta">
          <span class="account-name">{{ transaction.account_name }}</span>
          <span class="divider" v-if="transaction.remark">|</span>
          <span class="remark" v-if="transaction.remark">{{ getShortRemark(transaction.remark) }}</span>
        </div>
      </div>
    </div>
    
    <div class="item-right">
      <div 
        class="item-amount" 
        :class="{
          'is-income': transaction.type === 'income',
          'is-expense': transaction.type === 'expense',
          'is-transfer': transaction.type === 'transfer'
        }"
      >
        {{ formatAmount(transaction.amount, transaction.type) }}
      </div>
      <div class="item-time">
        {{ formatTime(transaction.transaction_date) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
import dayjs from 'dayjs'

defineProps({
  transaction: {
    type: Object as PropType<any>,
    required: true
  }
})

// 工具函数
const formatAmount = (amount: number, type: string) => {
  const num = Math.abs(amount).toFixed(2)
  if (type === 'income') return `+${num}`
  if (type === 'expense') return `-${num}`
  return num // transfer
}

const formatTime = (dateStr: string) => {
  return dayjs(dateStr).format('HH:mm')
}

const getCategoryInitial = (name: string | undefined) => {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

const getShortRemark = (remark: string) => {
  if (!remark) return ''
  return remark.length > 10 ? remark.substring(0, 10) + '...' : remark
}
</script>

<style scoped>
.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s;
  cursor: pointer;
}

.transaction-item:hover {
  background-color: #f9fafb;
}

.item-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  flex-shrink: 0;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-title {
  font-size: 15px;
  font-weight: 500;
  color: #111827;
}

.item-meta {
  font-size: 12px;
  color: #6b7280;
  display: flex;
  align-items: center;
}

.divider {
  margin: 0 6px;
  color: #d1d5db;
  font-size: 10px;
}

.remark {
  color: #9ca3af;
}

.item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.item-amount {
  font-size: 16px;
  font-weight: 600;
}

.item-amount.is-income {
  color: #16A34A; /* --color-primary green */
}

.item-amount.is-expense {
  color: #111827; /* Dark black for expense */
}

.item-amount.is-transfer {
  color: #6b7280; /* Gray for transfer */
}

.item-time {
  font-size: 12px;
  color: #9ca3af;
}
</style>
