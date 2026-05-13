<template>
  <div class="txn-detail-page" v-loading="loading">
    <!-- 顶部导航 -->
    <div class="page-header">
      <el-button text @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1 class="page-title">交易详情</h1>
      <div class="header-actions">
        <el-button size="small" @click="openEdit">编辑</el-button>
        <el-button size="small" type="danger" plain @click="handleDelete">删除</el-button>
      </div>
    </div>

    <template v-if="txn">
      <!-- 金额展示区（无背景卡片） -->
      <div class="amount-display">
        <div class="amount-display__icon" :style="iconStyle">
          <span v-if="txn.category_icon" class="icon-emoji">{{ txn.category_icon }}</span>
          <span v-else class="icon-fallback">{{ typeFallback }}</span>
        </div>
        <div class="amount-display__label">{{ typeLabel }}</div>
        <div class="amount-display__amount" :class="`amount-display__amount--${txn.type}`">
          {{ formatAmount }}
        </div>
        <div class="amount-display__date">{{ formatDate }}</div>
      </div>

      <!-- 详情列表 -->
      <el-card class="info-card" shadow="never">
        <div class="info-row">
          <span class="info-label">交易类型</span>
          <el-tag size="small" :type="typeTagType">{{ typeLabel }}</el-tag>
        </div>
        <el-divider />
        <div class="info-row">
          <span class="info-label">分类</span>
          <div class="info-val info-val--category">
            <span v-if="txn.category_icon" class="mini-icon">{{ txn.category_icon }}</span>
            <span>{{ txn.category_name || '未分类' }}</span>
          </div>
        </div>
        <el-divider />
        <div class="info-row">
          <span class="info-label">账户</span>
          <span class="info-val">{{ txn.account_name }}</span>
        </div>
        <template v-if="txn.merchant_name">
          <el-divider />
          <div class="info-row">
            <span class="info-label">商户</span>
            <span class="info-val">{{ txn.merchant_name }}</span>
          </div>
        </template>
        <template v-if="txn.remark">
          <el-divider />
          <div class="info-row">
            <span class="info-label">备注</span>
            <span class="info-val">{{ txn.remark }}</span>
          </div>
        </template>
        <el-divider />
        <div class="info-row">
          <span class="info-label">来源</span>
          <span class="info-val">{{ sourceLabel }}</span>
        </div>
        <el-divider />
        <div class="info-row">
          <span class="info-label">记录时间</span>
          <span class="info-val">{{ dayjs(txn.created_at).format('YYYY-MM-DD HH:mm') }}</span>
        </div>
      </el-card>
    </template>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editVisible"
      title="编辑交易"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form
        v-if="editForm"
        :model="editForm"
        label-width="80px"
        label-position="left"
      >
        <el-form-item label="分类">
          <el-select v-model="editForm.category_id" clearable placeholder="请选择分类" style="width:100%">
            <el-option
              v-for="c in categories"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            >
              <span style="margin-right:6px">{{ c.icon }}</span>{{ c.name }}
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="账户">
          <el-select v-model="editForm.account_id" placeholder="请选择账户" style="width:100%">
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="a.name"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="editForm.transaction_date"
            type="datetime"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disableFuture"
            style="width:100%"
          />
        </el-form-item>
        <el-form-item label="商户">
          <el-input v-model="editForm.merchant_name" clearable />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import {
  getTransaction,
  updateTransaction,
  deleteTransaction,
} from '@/api/transactions'
import { getCategories } from '@/api/categories'
import { getAccounts } from '@/api/accounts'
import type { Transaction } from '@/types/transaction'

const router = useRouter()
const route  = useRoute()

const loading = ref(false)
const saving  = ref(false)
const txn     = ref<Transaction | null>(null)

const editVisible = ref(false)
const editForm    = ref<any>(null)
const categories  = ref<any[]>([])
const accounts    = ref<any[]>([])

const txnId = Number(route.params.id)

// ── 计算属性 ──────────────────────────────────────────
const TYPE_META: Record<string, { label: string; fallback: string; tagType: '' | 'success' | 'info' | 'warning' | 'danger' }> = {
  income:   { label: '收入', fallback: '收', tagType: 'success' },
  expense:  { label: '支出', fallback: '支', tagType: 'info' },
  transfer: { label: '转账', fallback: '转', tagType: 'warning' },
}

const typeMeta    = computed(() => TYPE_META[txn.value?.type ?? 'expense'] ?? TYPE_META.expense)
const typeLabel   = computed(() => typeMeta.value.label)
const typeFallback= computed(() => typeMeta.value.fallback)
const typeTagType = computed(() => typeMeta.value.tagType)

const iconStyle = computed(() => {
  if (!txn.value) return {}
  const color = (txn.value as any).category_color
  if (txn.value.category_icon && color) {
    return { background: `linear-gradient(135deg, ${color}CC, ${color}88)` }
  }
  if (txn.value.category_icon) return { background: '#f3f4f6' }
  const fallbackBg: Record<string, string> = {
    income: '#16a34a', expense: '#ef4444', transfer: '#9ca3af',
  }
  return { background: fallbackBg[txn.value.type] ?? '#6b7280' }
})

const formatAmount = computed(() => {
  if (!txn.value) return ''
  const num = Math.abs(txn.value.amount).toFixed(2)
  if (txn.value.type === 'income')  return `+${num}`
  if (txn.value.type === 'expense') return `-${num}`
  return num
})

const formatDate = computed(() =>
  txn.value ? dayjs(txn.value.transaction_date).format('YYYY年MM月DD日 HH:mm') : ''
)

const sourceLabel = computed(() => {
  const map: Record<string, string> = {
    manual: '手动录入', wechat: '微信导入', alipay: '支付宝导入',
  }
  return map[txn.value?.source ?? 'manual'] ?? '手动录入'
})

// ── 加载数据 ──────────────────────────────────────────
const loadTxn = async () => {
  loading.value = true
  try {
    const res = await getTransaction(txnId) as unknown as Transaction
    txn.value = res
  } catch {
    ElMessage.error('加载交易详情失败')
  } finally {
    loading.value = false
  }
}

const loadDropdowns = async () => {
  const [catRes, accRes] = await Promise.all([
    getCategories() as any,
    getAccounts()    as any,
  ])
  categories.value = catRes?.categories ?? []
  accounts.value   = accRes?.accounts ?? []
}

// ── 编辑 ─────────────────────────────────────────────
const openEdit = async () => {
  if (!txn.value) return
  await loadDropdowns()
  editForm.value = {
    category_id:      txn.value.category_id ?? null,
    account_id:       txn.value.account_id,
    transaction_date: txn.value.transaction_date,
    merchant_name:    txn.value.merchant_name ?? '',
    remark:           txn.value.remark ?? '',
  }
  editVisible.value = true
}

const submitEdit = async () => {
  saving.value = true
  try {
    await updateTransaction(txnId, editForm.value)
    ElMessage.success('修改成功')
    editVisible.value = false
    await loadTxn()
  } catch {
    // 拦截器已提示
  } finally {
    saving.value = false
  }
}

const disableFuture = (date: Date) => date > new Date()

// ── 删除 ─────────────────────────────────────────────
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这笔交易吗？此操作不可恢复。', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger',
    })
    await deleteTransaction(txnId)
    ElMessage.success('已删除')
    router.replace('/transactions')
  } catch {
    // 取消或接口错误，不处理
  }
}

onMounted(loadTxn)
</script>

<style scoped>
.txn-detail-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 640px;
  margin: 0 auto;
}

/* 顶部导航 */
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  flex: 1;
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 金额展示区：无背景，纯内容居中 */
.amount-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 24px 0 16px;
}

.amount-display__icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.icon-emoji {
  font-size: 26px;
  line-height: 1;
}

.icon-fallback {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.amount-display__label {
  font-size: 13px;
  color: #9ca3af;
  letter-spacing: 0.5px;
}

.amount-display__amount {
  font-size: 42px;
  font-weight: 700;
  letter-spacing: -1px;
  color: #111827;
}

.amount-display__amount--income   { color: #16a34a; }
.amount-display__amount--expense  { color: #ef4444; }
.amount-display__amount--transfer { color: #6b7280; }

.amount-display__date {
  font-size: 13px;
  color: #9ca3af;
}

/* 详情卡片 */
.info-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.info-label {
  font-size: 14px;
  color: #6b7280;
  flex-shrink: 0;
}

.info-val {
  font-size: 14px;
  color: #111827;
  text-align: right;
}

.info-val--category {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mini-icon {
  font-size: 18px;
}

:deep(.el-divider--horizontal) {
  margin: 10px 0;
}

:deep(.el-button--primary) {
  --el-button-bg-color: #16a34a;
  --el-button-border-color: #16a34a;
  --el-button-hover-bg-color: #15803d;
  --el-button-hover-border-color: #15803d;
}
</style>
