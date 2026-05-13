<template>
  <div class="account-detail-page" v-loading="loadingAccount">
    <!-- 页头 -->
    <div class="page-header">
      <el-button link :icon="ArrowLeft" class="back-btn" @click="router.push('/accounts')">
        返回账户
      </el-button>
      <div class="header-actions">
        <el-button :icon="Edit" plain @click="openEditDialog">编辑</el-button>
        <el-button :icon="Switch" plain @click="openTransferDialog">转账</el-button>
        <el-button :icon="Setting" plain @click="openAdjustDialog">调整余额</el-button>
        <el-popconfirm
          title="确定删除该账户？有交易记录的账户无法删除。"
          confirm-button-text="确认删除"
          confirm-button-type="danger"
          @confirm="handleDelete"
        >
          <template #reference>
            <el-button :icon="Delete" plain type="danger">删除</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 账户概览卡片 -->
    <div v-if="account" class="overview-card">
      <!-- 卡片顶行：账户名 + 类型标签 -->
      <div class="card-top">
        <div class="card-account-name">{{ account.name }}</div>
        <div class="card-tags">
          <el-tag size="small" class="type-tag">{{ getAccountTypeName(account.type) }}</el-tag>
          <el-tag v-if="account.is_default" size="small" class="default-tag-overview">默认</el-tag>
        </div>
      </div>

      <!-- 卡片中部：余额 -->
      <div class="card-balance">
        <div class="balance-label">当前余额</div>
        <div class="balance-value">
          <span class="balance-currency">¥</span>
          <span class="balance-amount">{{ formatAmount(account.balance) }}</span>
        </div>
      </div>

      <!-- 卡片底行：收支统计 + 图标 -->
      <div class="card-bottom">
        <div class="card-stats">
          <div class="card-stat">
            <span class="card-stat__label">累计收入</span>
            <span class="card-stat__value card-stat__value--income">¥{{ formatAmount(account.income_total ?? 0) }}</span>
          </div>
          <div class="card-stat">
            <span class="card-stat__label">累计支出</span>
            <span class="card-stat__value card-stat__value--expense">¥{{ formatAmount(account.expense_total ?? 0) }}</span>
          </div>
        </div>
        <div class="card-icon">
          <el-icon size="32" style="opacity:0.4"><component :is="accountIcon" /></el-icon>
        </div>
      </div>
    </div>

    <!-- 交易记录 -->
    <el-card class="history-card" shadow="never">
      <template #header>
        <div class="history-header">
          <span class="history-title">交易记录</span>
          <el-select
            v-model="filterType"
            placeholder="全部类型"
            clearable
            size="small"
            style="width: 120px"
            @change="handleFilterChange"
          >
            <el-option label="收入" value="income" />
            <el-option label="支出" value="expense" />
            <el-option label="转账" value="transfer" />
          </el-select>
        </div>
      </template>

      <div v-loading="loadingHistory">
        <!-- 有数据 -->
        <div v-if="historyItems.length > 0" class="history-list">
          <!-- 按日期分组 -->
          <div v-for="(group, date) in groupedItems" :key="date" class="date-group">
            <div class="date-group__header">
              <span class="date-label">{{ date }}</span>
              <span class="date-summary">
                <span v-if="group.income > 0" class="income-text">+¥{{ formatAmount(group.income) }}</span>
                <span v-if="group.expense > 0" class="expense-text">-¥{{ formatAmount(group.expense) }}</span>
              </span>
            </div>
            <div v-for="item in group.items" :key="item.id" class="history-item">
              <!-- 分类图标 -->
              <div
                class="item-icon"
                :style="historyIconStyle(item)"
              >
                <span v-if="item.category?.icon" class="item-icon__emoji">{{ item.category.icon }}</span>
                <span v-else class="item-icon__fallback">{{ { income: '收', expense: '支', transfer: '转' }[item.type] ?? '?' }}</span>
              </div>
              <!-- 内容 -->
              <div class="item-content">
                <div class="item-title">
                  {{ item.merchant_name || item.category?.name || item.remark || typeLabel(item.type) }}
                </div>
                <div class="item-meta">
                  <span v-if="item.category">{{ item.category.name }}</span>
                  <span v-if="item.remark" class="item-remark">{{ item.remark }}</span>
                  <span class="item-time">{{ formatTime(item.transaction_date) }}</span>
                </div>
              </div>
              <!-- 金额 -->
              <div :class="['item-amount', `item-amount--${item.type}`]">
                {{ item.type === 'income' ? '+' : item.type === 'expense' ? '-' : '' }}¥{{ formatAmount(item.amount) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 无数据 -->
        <el-empty v-else description="暂无交易记录" :image-size="80" />
      </div>

      <!-- 分页 -->
      <div v-if="historyTotal > pageSize" class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="historyTotal"
          layout="prev, pager, next"
          background
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- ===== 编辑对话框 ===== -->
    <el-dialog title="编辑账户" v-model="editVisible" width="400px" destroy-on-close>
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="80px">
        <el-form-item label="账户名称" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="账户类型" prop="type">
          <el-select v-model="editForm.type" style="width:100%">
            <el-option label="现金" value="cash" />
            <el-option label="银行卡" value="bank" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="饭卡" value="meal_card" />
            <el-option label="其它" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="默认账户">
          <el-switch v-model="editForm.is_default" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- ===== 转账对话框 ===== -->
    <el-dialog title="转账到其他账户" v-model="transferVisible" width="400px" destroy-on-close>
      <el-form :model="transferForm" :rules="transferRules" ref="transferFormRef" label-width="80px">
        <el-form-item label="转出账户">
          <el-input :value="account?.name" disabled />
        </el-form-item>
        <el-form-item label="转入账户" prop="to_account_id">
          <el-select v-model="transferForm.to_account_id" placeholder="请选择" style="width:100%" :loading="loadingOtherAccounts">
            <el-option
              v-for="acc in otherAccounts"
              :key="acc.id"
              :label="`${acc.name}（余额 ¥${formatAmount(acc.balance)}）`"
              :value="acc.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="转账金额" prop="amount">
          <el-input-number v-model="transferForm.amount" :min="0.01" :precision="2" :step="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="transferForm.remark" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitTransfer">确认转账</el-button>
      </template>
    </el-dialog>

    <!-- ===== 调整余额对话框 ===== -->
    <el-dialog title="手动调整余额" v-model="adjustVisible" width="380px" destroy-on-close>
      <el-form :model="adjustForm" ref="adjustFormRef" label-width="90px">
        <el-form-item label="当前余额">
          <el-input :value="`¥ ${formatAmount(account?.balance ?? 0)}`" disabled />
        </el-form-item>
        <el-form-item label="调整为" prop="new_balance">
          <el-input-number v-model="adjustForm.new_balance" :precision="2" :step="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="调整原因">
          <el-input v-model="adjustForm.remark" placeholder="例如：盘点校正" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitAdjust">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'
import {
  ArrowLeft, Edit, Switch, Setting, Delete,
  Wallet, CreditCard, ChatRound, Grid, Food, Money,
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import {
  getAccount, updateAccount, deleteAccount,
  transfer, adjustBalance, getAccounts, getAccountBalanceHistory,
} from '@/api/accounts'
import type { AccountDetail, Account } from '@/types/account'

const router = useRouter()
const route  = useRoute()
const accountId = Number(route.params.id)

// ── 数据 ─────────────────────────────────────────────────
const loadingAccount = ref(false)
const loadingHistory = ref(false)
const loadingOtherAccounts = ref(false)
const submitting = ref(false)

const account = ref<AccountDetail | null>(null)
const historyItems = ref<any[]>([])
const historyTotal = ref(0)

const otherAccounts = ref<Account[]>([])

// ── 分页 & 过滤 ───────────────────────────────────────────
const currentPage = ref(1)
const pageSize    = 20
const filterType  = ref('')

// ── 对话框状态 ────────────────────────────────────────────
const editVisible     = ref(false)
const transferVisible = ref(false)
const adjustVisible   = ref(false)

const editFormRef     = ref<FormInstance>()
const transferFormRef = ref<FormInstance>()
const adjustFormRef   = ref<FormInstance>()

const editForm = reactive({ name: '', type: '', is_default: false, description: '' })
const transferForm = reactive({ to_account_id: undefined as number | undefined, amount: undefined as number | undefined, remark: '' })
const adjustForm = reactive({ new_balance: 0, remark: '' })

const editRules = {
  name: [{ required: true, message: '请输入账户名称', trigger: 'blur' }],
}
const transferRules = {
  to_account_id: [{ required: true, message: '请选择转入账户', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
}

// ── 工具函数 ──────────────────────────────────────────────
const formatAmount = (val: number | string) => Number(val || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
const formatTime   = (val: string) => dayjs(val).format('HH:mm')

const TYPE_NAME: Record<string, string> = {
  cash: '现金', bank: '银行卡', wechat: '微信',
  alipay: '支付宝', meal_card: '饭卡', other: '其它',
}
const TYPE_ICON: Record<string, any> = {
  cash: Money, bank: CreditCard, wechat: ChatRound,
  alipay: Grid, meal_card: Food, other: Wallet,
}

const getAccountTypeName = (t: string) => TYPE_NAME[t] ?? t
const accountIcon = computed(() => TYPE_ICON[account.value?.type ?? 'other'] ?? Wallet)

const HISTORY_TYPE_BG: Record<string, string> = {
  income: '#16a34a', expense: '#ef4444', transfer: '#9ca3af',
}
const historyIconStyle = (item: any) => {
  if (item.category?.color) {
    const c = item.category.color
    return { background: `linear-gradient(135deg, ${c}CC, ${c}88)` }
  }
  // 无分类颜色时用类型色
  return { background: HISTORY_TYPE_BG[item.type] ?? '#6b7280' }
}
const typeLabel = (type: string) => ({ income: '收入', expense: '支出', transfer: '转账' }[type] ?? type)

// ── 分组 ─────────────────────────────────────────────────
const groupedItems = computed(() => {
  const groups: Record<string, { items: any[]; income: number; expense: number }> = {}
  historyItems.value.forEach(item => {
    const date = dayjs(item.transaction_date).format('YYYY-MM-DD')
    if (!groups[date]) groups[date] = { items: [], income: 0, expense: 0 }
    groups[date].items.push(item)
    if (item.type === 'income')  groups[date].income  += item.amount
    if (item.type === 'expense') groups[date].expense += item.amount
  })
  return groups
})

// ── 数据加载 ──────────────────────────────────────────────
const loadAccount = async () => {
  loadingAccount.value = true
  try {
    const res = await getAccount(accountId) as unknown as AccountDetail
    account.value = res
  } finally {
    loadingAccount.value = false
  }
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const offset = (currentPage.value - 1) * pageSize
    const params: Record<string, any> = { limit: pageSize, offset }
    if (filterType.value) params.change_type = filterType.value

    const res = await getAccountBalanceHistory(accountId, params) as unknown as {
      items: any[]; total: number
    }
    historyItems.value = res?.items ?? []
    historyTotal.value = res?.total ?? 0
  } finally {
    loadingHistory.value = false
  }
}

const loadOtherAccounts = async () => {
  loadingOtherAccounts.value = true
  try {
    const res = await getAccounts() as unknown as { accounts: Account[] }
    otherAccounts.value = (res?.accounts ?? []).filter(a => a.id !== accountId && a.is_enabled)
  } finally {
    loadingOtherAccounts.value = false
  }
}

// ── 过滤 & 分页 ───────────────────────────────────────────
const handleFilterChange = () => {
  currentPage.value = 1
  loadHistory()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadHistory()
}

// ── 编辑 ──────────────────────────────────────────────────
const openEditDialog = () => {
  if (!account.value) return
  editForm.name        = account.value.name
  editForm.type        = account.value.type
  editForm.is_default  = account.value.is_default
  editForm.description = account.value.description ?? ''
  editVisible.value    = true
}

const submitEdit = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      await updateAccount(accountId, {
        name: editForm.name,
        type: editForm.type as any,
        is_default: editForm.is_default,
        description: editForm.description,
      })
      ElMessage.success('账户更新成功')
      editVisible.value = false
      loadAccount()
    } finally {
      submitting.value = false
    }
  })
}

// ── 删除 ──────────────────────────────────────────────────
const handleDelete = async () => {
  try {
    await deleteAccount(accountId)
    ElMessage.success('账户已删除')
    router.push('/accounts')
  } catch {
    // 错误由拦截器统一提示
  }
}

// ── 转账 ──────────────────────────────────────────────────
const openTransferDialog = () => {
  transferForm.to_account_id = undefined
  transferForm.amount        = undefined
  transferForm.remark        = ''
  loadOtherAccounts()
  transferVisible.value = true
}

const submitTransfer = async () => {
  if (!transferFormRef.value) return
  await transferFormRef.value.validate(async valid => {
    if (!valid) return
    submitting.value = true
    try {
      await transfer({
        from_account_id: accountId,
        to_account_id:   transferForm.to_account_id!,
        amount:          transferForm.amount!,
        remark:          transferForm.remark || undefined,
      })
      ElMessage.success('转账成功')
      transferVisible.value = false
      loadAccount()
      loadHistory()
    } finally {
      submitting.value = false
    }
  })
}

// ── 调整余额 ──────────────────────────────────────────────
const openAdjustDialog = () => {
  adjustForm.new_balance = Number(account.value?.balance ?? 0)
  adjustForm.remark      = ''
  adjustVisible.value    = true
}

const submitAdjust = async () => {
  submitting.value = true
  try {
    await adjustBalance(accountId, {
      new_balance: adjustForm.new_balance,
      remark:      adjustForm.remark || undefined,
    })
    ElMessage.success('余额调整成功')
    adjustVisible.value = false
    loadAccount()
    loadHistory()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadAccount()
  loadHistory()
})
</script>

<style scoped>
.account-detail-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── 页头 ────────────────────────────────────────────────── */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.back-btn {
  font-size: 14px;
  color: #6b7280;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* ── 账户概览卡片（银行卡比例） ───────────────────────────── */
.overview-card {
  width: 380px;
  height: 220px;
  margin: 0 auto;
  border-radius: 18px;
  padding: 24px 28px;
  color: #fff;
  background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 8px 24px rgba(22, 163, 74, 0.35);
  position: relative;
  overflow: hidden;
}

/* 装饰圆圈（模拟银行卡光晕效果） */
.overview-card::before {
  content: '';
  position: absolute;
  right: -40px;
  top: -40px;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  pointer-events: none;
}

.overview-card::after {
  content: '';
  position: absolute;
  right: 20px;
  top: 60px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  pointer-events: none;
}

/* 顶行 */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-account-name {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.card-tags {
  display: flex;
  gap: 6px;
}

/* 中部余额 */
.card-balance {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.balance-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0.5px;
}

.balance-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.balance-currency {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.balance-amount {
  font-size: 34px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -1px;
  line-height: 1;
}

/* 底行 */
.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.card-stats {
  display: flex;
  gap: 20px;
}

.card-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-stat__label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.65);
  letter-spacing: 0.3px;
}

.card-stat__value {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.card-stat__value--income  { color: #bbf7d0; }
.card-stat__value--expense { color: #fecaca; }

.card-icon {
  color: #fff;
}

/* ── 交易记录卡片 ─────────────────────────────────────────── */
.history-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
}

/* 日期分组 */
.date-group {
  margin-bottom: 4px;
}

.date-group__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 6px;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 2px;
}

.date-label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
}

.date-summary {
  display: flex;
  gap: 10px;
  font-size: 12px;
  font-weight: 600;
}

.income-text  { color: #16a34a; }
.expense-text { color: #ef4444; }

/* 交易条目 */
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 4px;
  border-radius: 8px;
  transition: background 0.15s;
}

.history-item:hover {
  background: #f9fafb;
}

.item-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon__emoji {
  font-size: 22px;
  line-height: 1;
}

.item-icon__fallback {
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
}

.item-content {
  flex: 1;
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
  display: flex;
  gap: 8px;
  margin-top: 2px;
  font-size: 12px;
  color: #9ca3af;
  flex-wrap: wrap;
}

.item-remark {
  color: #d1d5db;
}

.item-time {
  color: #d1d5db;
}

.item-amount {
  flex-shrink: 0;
  font-size: 15px;
  font-weight: 600;
}

.item-amount--income   { color: #16a34a; }
.item-amount--expense  { color: #ef4444; }
.item-amount--transfer { color: #6b7280; }

/* 分页 */
.pagination-wrap {
  display: flex;
  justify-content: center;
  padding-top: 20px;
}

/* 概览卡片内标签 */
.type-tag {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: transparent !important;
  color: #fff !important;
}

.default-tag-overview {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
  color: #fff !important;
  margin-left: 6px;
}

/* ── Element Plus 主题覆盖 ───────────────────────────────── */
:deep(.el-button--primary) {
  --el-button-bg-color: #16a34a;
  --el-button-border-color: #16a34a;
  --el-button-hover-bg-color: #15803d;
  --el-button-hover-border-color: #15803d;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #16a34a;
}
</style>
