<template>
  <div class="transaction-add-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <el-button
        link
        :icon="ArrowLeft"
        class="back-btn"
        @click="router.back()"
      >
        返回
      </el-button>
      <h1 class="page-title">记一笔</h1>
      <div class="header-placeholder" />
    </div>

    <div class="form-wrapper">
      <!-- 交易类型切换 -->
      <div class="type-selector">
        <div
          v-for="tab in transactionTypes"
          :key="tab.value"
          :class="['type-tab', { 'type-tab--active': formData.type === tab.value }]"
          @click="handleTypeChange(tab.value)"
        >
          <span class="type-tab__icon">{{ tab.icon }}</span>
          <span class="type-tab__label">{{ tab.label }}</span>
        </div>
      </div>

      <!-- 金额输入区 -->
      <div class="amount-section">
        <div class="amount-label">金额</div>
        <div class="amount-input-row">
          <span class="currency-sign">¥</span>
          <input
            ref="amountInputRef"
            v-model="amountDisplay"
            class="amount-input"
            type="text"
            inputmode="decimal"
            placeholder="0.00"
            @input="handleAmountInput"
            @focus="handleAmountFocus"
          />
        </div>
        <div v-if="amountError" class="amount-error">{{ amountError }}</div>
      </div>

      <!-- 分类选择（非转账时显示） -->
      <div v-if="formData.type !== 'transfer'" class="section-block">
        <div class="section-title">选择分类</div>
        <div v-if="categoryLoading" class="category-loading">
          <el-skeleton :rows="2" animated />
        </div>
        <div v-else-if="filteredCategories.length > 0" class="category-grid">
          <div
            v-for="cat in filteredCategories"
            :key="cat.id"
            :class="['category-item', { 'category-item--active': formData.category_id === cat.id }]"
            :style="formData.category_id === cat.id && cat.color ? { borderColor: cat.color, backgroundColor: cat.color + '1A' } : {}"
            @click="formData.category_id = cat.id"
          >
            <span class="category-item__icon">{{ cat.icon || '📝' }}</span>
            <span class="category-item__name">{{ cat.name }}</span>
          </div>
        </div>
        <div v-else class="category-empty">
          暂无分类，请先前往设置添加分类
        </div>
        <div v-if="categoryError" class="field-error">{{ categoryError }}</div>
      </div>

      <!-- 账户选择 -->
      <div class="section-block">
        <div class="section-title">{{ formData.type === 'transfer' ? '转出账户' : '账户' }}</div>
        <el-select
          v-model="formData.account_id"
          placeholder="请选择账户"
          style="width: 100%"
          size="large"
          :loading="accountLoading"
        >
          <el-option
            v-for="acc in enabledAccounts"
            :key="acc.id"
            :label="acc.name"
            :value="acc.id"
          >
            <div class="account-option">
              <span class="account-option__icon">{{ acc.icon || getAccountIcon(acc.type) }}</span>
              <span class="account-option__name">{{ acc.name }}</span>
              <span class="account-option__balance">¥{{ Number(acc.balance).toFixed(2) }}</span>
            </div>
          </el-option>
        </el-select>
        <div v-if="accountError" class="field-error">{{ accountError }}</div>
      </div>

      <!-- 转入账户（仅转账时显示） -->
      <div v-if="formData.type === 'transfer'" class="section-block">
        <div class="section-title">转入账户</div>
        <el-select
          v-model="formData.to_account_id"
          placeholder="请选择转入账户"
          style="width: 100%"
          size="large"
        >
          <el-option
            v-for="acc in toAccountOptions"
            :key="acc.id"
            :label="acc.name"
            :value="acc.id"
          >
            <div class="account-option">
              <span class="account-option__icon">{{ acc.icon || getAccountIcon(acc.type) }}</span>
              <span class="account-option__name">{{ acc.name }}</span>
              <span class="account-option__balance">¥{{ Number(acc.balance).toFixed(2) }}</span>
            </div>
          </el-option>
        </el-select>
        <div v-if="toAccountError" class="field-error">{{ toAccountError }}</div>
      </div>

      <!-- 交易时间 -->
      <div class="section-block">
        <div class="section-title">交易时间</div>
        <el-date-picker
          v-model="formData.transaction_date"
          type="datetime"
          placeholder="选择交易时间"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
          size="large"
        />
      </div>

      <!-- 备注 -->
      <div class="section-block">
        <div class="section-title">备注（选填）</div>
        <el-input
          v-model="formData.remark"
          type="textarea"
          :rows="3"
          placeholder="添加备注信息..."
          maxlength="200"
          show-word-limit
          resize="none"
        />
      </div>
    </div>

    <!-- 底部保存按钮 -->
    <div class="submit-bar">
      <el-button
        class="submit-btn"
        type="primary"
        size="large"
        :loading="submitting"
        @click="handleSubmit"
      >
        {{ submitBtnText }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getCategories } from '@/api/categories'
import { getAccounts, transfer as transferApi } from '@/api/accounts'
import { createTransaction } from '@/api/transactions'
import type { Category } from '@/types/category'
import type { Account } from '@/types/account'
import type { TransactionType } from '@/types/transaction'

const router = useRouter()

// 交易类型配置
const transactionTypes = [
  { value: 'expense', label: '支出', icon: '💸' },
  { value: 'income', label: '收入', icon: '💰' },
  { value: 'transfer', label: '转账', icon: '💱' },
] as const

// 表单状态
const formData = reactive({
  type: 'expense' as TransactionType,
  amount: 0,
  category_id: null as number | null,
  account_id: null as number | null,
  to_account_id: null as number | null,
  transaction_date: '',
  remark: '',
})

// 金额显示值
const amountDisplay = ref('')
const amountInputRef = ref<HTMLInputElement | null>(null)

// 加载状态
const categoryLoading = ref(false)
const accountLoading = ref(false)
const submitting = ref(false)

// 数据
const categories = ref<Category[]>([])
const accounts = ref<Account[]>([])

// 错误信息
const amountError = ref('')
const categoryError = ref('')
const accountError = ref('')
const toAccountError = ref('')

// 计算属性：当前类型对应分类
const filteredCategories = computed(() => {
  if (formData.type === 'transfer') return []
  return categories.value.filter(cat => cat.type === formData.type)
})

// 计算属性：可用账户（已启用）
const enabledAccounts = computed(() => accounts.value.filter(acc => acc.is_enabled))

// 计算属性：转入账户（排除已选转出账户）
const toAccountOptions = computed(() =>
  enabledAccounts.value.filter(acc => acc.id !== formData.account_id)
)

// 计算属性：提交按钮文案
const submitBtnText = computed(() => {
  const map: Record<TransactionType, string> = {
    expense: '保存支出',
    income: '保存收入',
    transfer: '保存转账',
  }
  return map[formData.type]
})

// 账户类型图标映射
const getAccountIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    cash: '💵',
    bank: '🏦',
    wechat: '💚',
    alipay: '💙',
    meal_card: '🍽️',
    other: '💳',
  }
  return iconMap[type] || '💳'
}

// 切换交易类型
const handleTypeChange = (type: TransactionType) => {
  formData.type = type
  formData.category_id = null
  formData.to_account_id = null
  categoryError.value = ''
  toAccountError.value = ''
}

// 金额输入处理
const handleAmountInput = () => {
  let val = amountDisplay.value.replace(/[^\d.]/g, '')
  const parts = val.split('.')
  if (parts.length > 2) {
    val = parts[0] + '.' + parts.slice(1).join('')
  }
  if (parts.length === 2 && parts[1].length > 2) {
    val = parts[0] + '.' + parts[1].slice(0, 2)
  }
  amountDisplay.value = val
  formData.amount = parseFloat(val) || 0
  amountError.value = ''
}

// 金额输入框聚焦：全选已有内容
const handleAmountFocus = () => {
  setTimeout(() => {
    amountInputRef.value?.select()
  }, 0)
}

// 表单校验
const validate = (): boolean => {
  let valid = true

  if (!formData.amount || formData.amount <= 0) {
    amountError.value = '请输入有效的金额（必须大于 0）'
    valid = false
  } else {
    amountError.value = ''
  }

  if (formData.type !== 'transfer' && !formData.category_id) {
    categoryError.value = '请选择分类'
    valid = false
  } else {
    categoryError.value = ''
  }

  if (!formData.account_id) {
    accountError.value = '请选择账户'
    valid = false
  } else {
    accountError.value = ''
  }

  if (formData.type === 'transfer') {
    if (!formData.to_account_id) {
      toAccountError.value = '请选择转入账户'
      valid = false
    } else if (formData.to_account_id === formData.account_id) {
      toAccountError.value = '转出账户与转入账户不能相同'
      valid = false
    } else {
      toAccountError.value = ''
    }
  }

  return valid
}

// 提交
const handleSubmit = async () => {
  if (!validate()) return

  submitting.value = true
  try {
    if (formData.type === 'transfer') {
      await transferApi({
        from_account_id: formData.account_id!,
        to_account_id: formData.to_account_id!,
        amount: formData.amount,
        remark: formData.remark || undefined,
        transaction_date: formData.transaction_date || undefined,
      })
    } else {
      await createTransaction({
        type: formData.type,
        amount: formData.amount,
        category_id: formData.category_id ?? undefined,
        account_id: formData.account_id!,
        transaction_date: formData.transaction_date,
        remark: formData.remark || undefined,
      })
    }

    ElMessage.success('记账成功！')
    router.push('/transactions')
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
    ElMessage.error(msg || '记账失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 加载分类列表
const loadCategories = async () => {
  categoryLoading.value = true
  try {
    const res = await getCategories()
    if (res?.data?.categories) {
      categories.value = res.data.categories
    }
  } catch {
    ElMessage.warning('分类加载失败，请刷新重试')
  } finally {
    categoryLoading.value = false
  }
}

// 加载账户列表
const loadAccounts = async () => {
  accountLoading.value = true
  try {
    const res = await getAccounts({ is_enabled: true })
    if (res?.data?.accounts) {
      accounts.value = res.data.accounts
      const defaultAcc = accounts.value.find(a => a.is_default) ?? accounts.value[0]
      if (defaultAcc) {
        formData.account_id = defaultAcc.id
      }
    }
  } catch {
    ElMessage.warning('账户加载失败，请刷新重试')
  } finally {
    accountLoading.value = false
  }
}

onMounted(() => {
  formData.transaction_date = dayjs().format('YYYY-MM-DD HH:mm:ss')
  loadCategories()
  loadAccounts()
})
</script>

<style scoped>
.transaction-add-page {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 48px);
  background-color: #f9fafb;
}

/* 页面标题 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0 20px 0;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.back-btn {
  color: #4b5563;
  font-size: 14px;
}

.header-placeholder {
  width: 64px;
}

/* 表单区域 */
.form-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 20px;
}

/* 类型切换 */
.type-selector {
  display: flex;
  gap: 8px;
  background-color: #e5e7eb;
  border-radius: 12px;
  padding: 4px;
}

.type-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  transition: all 0.2s;
  user-select: none;
}

.type-tab:hover {
  background-color: rgba(255, 255, 255, 0.6);
}

.type-tab--active {
  background-color: #ffffff;
  color: #16a34a;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}

.type-tab__icon {
  font-size: 18px;
  line-height: 1;
}

.type-tab__label {
  font-size: 14px;
}

/* 金额输入 */
.amount-section {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px 20px 20px;
  border: 1px solid #e5e7eb;
  text-align: center;
}

.amount-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.amount-input-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.currency-sign {
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.amount-input {
  font-size: 48px;
  font-weight: 700;
  color: #111827;
  border: none;
  outline: none;
  background: transparent;
  width: 220px;
  text-align: left;
  caret-color: #16a34a;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.amount-input::placeholder {
  color: #d1d5db;
}

.amount-error {
  margin-top: 8px;
  font-size: 12px;
  color: #ef4444;
}

/* 通用区块 */
.section-block {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 12px;
}

/* 分类网格 */
.category-loading {
  padding: 8px 0;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

@media (max-width: 480px) {
  .category-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 900px) {
  .category-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 6px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #f9fafb;
  min-height: 76px;
  box-sizing: border-box;
}

.category-item:hover {
  border-color: #16a34a;
  background-color: #f0fdf4;
  transform: translateY(-1px);
}

.category-item--active {
  border-color: #16a34a;
  background-color: #f0fdf4;
}

.category-item__icon {
  font-size: 26px;
  line-height: 1;
  margin-bottom: 5px;
}

.category-item__name {
  font-size: 12px;
  color: #4b5563;
  text-align: center;
  word-break: keep-all;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.category-item--active .category-item__name {
  color: #16a34a;
  font-weight: 600;
}

.category-empty {
  text-align: center;
  padding: 20px 0;
  font-size: 14px;
  color: #9ca3af;
}

/* 账户选项 */
.account-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.account-option__icon {
  font-size: 16px;
  flex-shrink: 0;
}

.account-option__name {
  flex: 1;
  font-size: 14px;
  color: #111827;
}

.account-option__balance {
  font-size: 13px;
  color: #9ca3af;
}

/* 错误提示 */
.field-error {
  margin-top: 6px;
  font-size: 12px;
  color: #ef4444;
}

/* 提交按钮栏：sticky 吸底，限定在内容区宽度内 */
.submit-bar {
  position: sticky;
  bottom: -24px;
  /* 向外撑开抵消 el-main 的 24px 内边距，使按钮栏与内容区两侧对齐 */
  margin: 16px -24px -24px -24px;
  padding: 12px 24px;
  background-color: #ffffff;
  border-top: 1px solid #e5e7eb;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 10px;
  background-color: #16a34a;
  border-color: #16a34a;
}

.submit-btn:hover {
  background-color: #15803d;
  border-color: #15803d;
}

/* Element Plus 覆盖 */
:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e5e7eb inset;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
  border-color: #e5e7eb;
  font-size: 14px;
  color: #111827;
}

:deep(.el-date-editor.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e5e7eb inset;
}

:deep(.el-button--primary) {
  --el-button-bg-color: #16a34a;
  --el-button-border-color: #16a34a;
  --el-button-hover-bg-color: #15803d;
  --el-button-hover-border-color: #15803d;
  --el-button-active-bg-color: #166534;
  --el-button-active-border-color: #166534;
}
</style>
