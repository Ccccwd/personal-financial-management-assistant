<template>
  <div class="transaction-list-page">
    <div class="page-header">
      <h1 class="page-title">交易记录</h1>
      <el-button type="primary" @click="handleToAdd">记一笔</el-button>
    </div>

    <!-- 过滤栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="form" class="filter-form">
        <el-form-item label="交易类型">
          <el-select v-model="form.type" placeholder="全部类型" clearable style="width: 140px">
            <el-option label="支出" value="expense" />
            <el-option label="收入" value="income" />
            <el-option label="转账" value="transfer" />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
            v-model="form.daterange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 300px"
          />
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="form.keyword"
            placeholder="搜索商户名或备注"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetForm">重置</el-button>
          <!-- 未分类快速过滤 -->
          <el-button
            :type="onlyUncategorized ? 'warning' : ''"
            :plain="!onlyUncategorized"
            @click="toggleUncategorized"
          >
            {{ onlyUncategorized ? '✓ 仅看未分类' : '仅看未分类' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 未分类提示横幅 -->
      <el-alert
        v-if="uncategorizedCount > 0"
        :title="`当前页有 ${uncategorizedCount} 条未分类交易，点击条目中的「待分类」可快速设置`"
        type="warning"
        :closable="false"
        show-icon
        style="margin-top: 8px"
      />
    </el-card>

    <!-- 列表区 -->
    <el-card class="list-card" shadow="never">
      <div v-loading="loading">
        <div v-if="displayedGroups.length > 0">
          <div v-for="(group, index) in displayedGroups" :key="index" class="day-group">
            <div class="day-header">
              <div class="day-info">
                <span class="day-date">{{ group.date }}</span>
                <span class="day-desc">{{ getDayOfWeek(group.date) }}</span>
              </div>
              <div class="day-summary">
                <span v-if="Number(group.income || 0) > 0" class="inc-text">收: {{ Number(group.income || 0).toFixed(2) }}</span>
                <span v-if="Number(group.expense || 0) > 0" class="exp-text">支: {{ Number(group.expense || 0).toFixed(2) }}</span>
              </div>
            </div>

            <div class="day-list">
              <div
                v-for="item in group.items"
                :key="item.id"
                class="txn-row"
              >
                <!-- 可点击跳转区域 -->
                <div class="txn-row__main" @click="handleToDetail(item.id)">
                  <TransactionCard :transaction="item" />
                </div>
                <!-- 未分类快速入口（独立，不触发跳转） -->
                <div
                  v-if="!item.category_id && item.type !== 'transfer'"
                  class="quick-classify-btn"
                  @click.stop="openClassify(item)"
                >
                  待分类
                </div>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else :description="onlyUncategorized ? '当前页没有未分类交易 🎉' : '暂无交易记录'" />
      </div>

      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 快速分类弹窗 -->
    <el-dialog
      v-model="classifyVisible"
      title="设置分类"
      width="420px"
      :close-on-click-modal="true"
      destroy-on-close
    >
      <div v-if="classifyTarget" class="classify-txn-info">
        <span class="classify-txn-name">{{ classifyTarget.merchant_name || classifyTarget.category_name || '未知商户' }}</span>
        <span class="classify-txn-amount" :class="`is-${classifyTarget.type}`">
          {{ classifyTarget.type === 'income' ? '+' : '-' }}{{ Math.abs(classifyTarget.amount).toFixed(2) }}
        </span>
      </div>

      <div class="category-picker" v-loading="loadingCategories">
        <template v-if="expenseCategories.length || incomeCategories.length">
          <!-- 支出分类 -->
          <div v-if="expenseCategories.length" class="category-group">
            <div class="category-group__title">支出分类</div>
            <div class="category-grid">
              <div
                v-for="cat in expenseCategories"
                :key="cat.id"
                :class="['cat-item', { 'cat-item--active': selectedCategoryId === cat.id }]"
                @click="selectedCategoryId = cat.id"
              >
                <span class="cat-item__icon" :style="cat.color ? { background: `linear-gradient(135deg,${cat.color}CC,${cat.color}88)` } : {}">
                  {{ cat.icon || '📝' }}
                </span>
                <span class="cat-item__name">{{ cat.name }}</span>
              </div>
            </div>
          </div>
          <!-- 收入分类 -->
          <div v-if="incomeCategories.length" class="category-group">
            <div class="category-group__title">收入分类</div>
            <div class="category-grid">
              <div
                v-for="cat in incomeCategories"
                :key="cat.id"
                :class="['cat-item', { 'cat-item--active': selectedCategoryId === cat.id }]"
                @click="selectedCategoryId = cat.id"
              >
                <span class="cat-item__icon" :style="cat.color ? { background: `linear-gradient(135deg,${cat.color}CC,${cat.color}88)` } : {}">
                  {{ cat.icon || '📝' }}
                </span>
                <span class="cat-item__name">{{ cat.name }}</span>
              </div>
            </div>
          </div>
        </template>
        <el-empty v-else description="暂无分类数据" :image-size="60" />
      </div>

      <template #footer>
        <el-button @click="classifyVisible = false">取消</el-button>
        <el-button plain :loading="aiReclassifying" @click="handleAIClassify">
          AI 识别
        </el-button>
        <el-button type="primary" :loading="classifying" :disabled="!selectedCategoryId" @click="submitClassify">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import TransactionCard from '@/components/business/TransactionCard.vue'
import { getTransactions, updateTransaction } from '@/api/transactions'
import { getCategories } from '@/api/categories'
import { useAIStore } from '@/stores/ai'
import type { Transaction, TransactionQuery, TransactionListPayload } from '@/types/transaction'

const router = useRouter()
const aiStore = useAIStore()

// ── 列表状态 ────────────────────────────────────────────
const loading = ref(false)
const transactions = ref<Transaction[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const onlyUncategorized = ref(false)

const form = reactive({
  type: '',
  daterange: [] as string[],
  keyword: '',
})

// ── 分组 ────────────────────────────────────────────────
const groupedTransactions = computed(() => {
  const groups: Record<string, { date: string; income: number; expense: number; items: Transaction[] }> = {}
  transactions.value.forEach(item => {
    const dateStr = dayjs(item.transaction_date).format('YYYY年MM月DD日')
    if (!groups[dateStr]) groups[dateStr] = { date: dateStr, income: 0, expense: 0, items: [] }
    if (item.type === 'income')  groups[dateStr].income  += Number(item.amount)
    if (item.type === 'expense') groups[dateStr].expense += Number(item.amount)
    groups[dateStr].items.push(item)
  })
  return Object.values(groups)
})

// 仅看未分类时对当前页做客户端过滤
const displayedGroups = computed(() => {
  if (!onlyUncategorized.value) return groupedTransactions.value
  return groupedTransactions.value
    .map(g => ({ ...g, items: g.items.filter(i => !i.category_id && i.type !== 'transfer') }))
    .filter(g => g.items.length > 0)
})

const uncategorizedCount = computed(() =>
  transactions.value.filter(t => !t.category_id && t.type !== 'transfer').length
)

const toggleUncategorized = () => {
  onlyUncategorized.value = !onlyUncategorized.value
}

// ── 辅助 ────────────────────────────────────────────────
const getDayOfWeek = (dateStr: string) => {
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return days[dayjs(dateStr.replace(/[年月日]/g, '-')).day()]
}

// ── 拉取列表 ────────────────────────────────────────────
const fetchList = async () => {
  loading.value = true
  try {
    const query: TransactionQuery = { page: page.value, page_size: pageSize.value }
    if (form.type) query.type = form.type as any
    if (form.keyword) query.keyword = form.keyword
    if (form.daterange?.length === 2) {
      query.start_date = form.daterange[0]
      query.end_date   = form.daterange[1]
    }
    const res = await getTransactions(query) as unknown as TransactionListPayload
    if (res?.transactions) {
      transactions.value = res.transactions
      total.value = res.total ?? 0
    } else {
      transactions.value = []
      total.value = 0
    }
  } catch {
    transactions.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleSearch  = () => { page.value = 1; fetchList() }
const resetForm     = () => { form.type = ''; form.daterange = []; form.keyword = ''; onlyUncategorized.value = false; handleSearch() }
const handleSizeChange    = (v: number) => { pageSize.value = v; fetchList() }
const handleCurrentChange = (v: number) => { page.value = v; fetchList() }
const handleToAdd    = () => router.push('/transactions/add')
const handleToDetail = (id: number) => router.push(`/transactions/${id}`)

// ── 快速分类 ─────────────────────────────────────────────
const classifyVisible   = ref(false)
const classifyTarget    = ref<Transaction | null>(null)
const selectedCategoryId = ref<number | null>(null)
const classifying       = ref(false)
const aiReclassifying   = ref(false)
const loadingCategories = ref(false)
const allCategories     = ref<any[]>([])

const expenseCategories = computed(() => allCategories.value.filter(c => c.type === 'expense'))
const incomeCategories  = computed(() => allCategories.value.filter(c => c.type === 'income'))

const loadCategoriesOnce = async () => {
  if (allCategories.value.length) return
  loadingCategories.value = true
  try {
    const res = await getCategories() as any
    allCategories.value = res?.categories ?? []
  } finally {
    loadingCategories.value = false
  }
}

const openClassify = async (txn: Transaction) => {
  classifyTarget.value = txn
  selectedCategoryId.value = txn.category_id ?? null
  classifyVisible.value = true
  await loadCategoriesOnce()
}

const handleAIClassify = async () => {
  if (!classifyTarget.value) return
  const txn = classifyTarget.value
  aiReclassifying.value = true
  try {
    const preview = await aiStore.reclassify(txn.id, true)
    if (!preview?.category_id) return
    const currentName = txn.category_name || '未分类'
    if (preview.category_name === currentName) {
      ElMessage.info('AI 推荐分类与当前一致')
      return
    }
    await ElMessageBox.confirm(
      `建议将分类从「${currentName}」改为「${preview.category_name}」，是否应用？`,
      'AI 智能分类',
      { confirmButtonText: '应用', cancelButtonText: '取消' }
    )
    await aiStore.reclassify(txn.id, false)
    ElMessage.success('AI 分类已应用')
    classifyVisible.value = false
    await fetchList()
  } catch {
    // 取消或错误
  } finally {
    aiReclassifying.value = false
  }
}

const submitClassify = async () => {
  if (!classifyTarget.value || !selectedCategoryId.value) return
  classifying.value = true
  try {
    await updateTransaction(classifyTarget.value.id, { category_id: selectedCategoryId.value })
    // 本地更新，避免刷新整页
    const cat = allCategories.value.find(c => c.id === selectedCategoryId.value)
    const idx = transactions.value.findIndex(t => t.id === classifyTarget.value!.id)
    if (idx !== -1) {
      transactions.value[idx] = {
        ...transactions.value[idx],
        category_id:   selectedCategoryId.value,
        category_name: cat?.name,
        category_icon: cat?.icon,
      } as Transaction
    }
    ElMessage.success('分类已更新')
    classifyVisible.value = false
  } catch {
    // 拦截器已提示
  } finally {
    classifying.value = false
  }
}


onMounted(fetchList)
</script>

<style scoped>
.transaction-list-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.filter-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.filter-form { display: flex; flex-wrap: wrap; }

.list-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 0;
}

:deep(.list-card .el-card__body) { padding: 0; }

.day-group { border-bottom: 8px solid #f9fafb; }
.day-group:last-child { border-bottom: none; }

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f9fafb;
  border-bottom: 1px solid #f3f4f6;
}

.day-info { display: flex; align-items: center; gap: 8px; }
.day-date { font-size: 14px; font-weight: 600; color: #4b5563; }
.day-desc { font-size: 12px; color: #9ca3af; }
.day-summary { font-size: 12px; display: flex; gap: 12px; }
.inc-text { color: #16a34a; }
.exp-text { color: #6b7280; }

.day-list { display: flex; flex-direction: column; }

/* 每行：卡片 + 快速分类按钮 */
.txn-row {
  position: relative;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f3f4f6;
}
.txn-row:last-child { border-bottom: none; }

.txn-row__main {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

/* 去掉 TransactionCard 自带的底边，由 txn-row 统一控制 */
.txn-row__main :deep(.transaction-item) {
  border-bottom: none;
}

.quick-classify-btn {
  flex-shrink: 0;
  margin-right: 12px;
  padding: 3px 10px;
  font-size: 12px;
  color: #d97706;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 20px;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.quick-classify-btn:hover {
  background: #fde68a;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
}

/* 快速分类弹窗 */
.classify-txn-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 16px;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 16px;
}
.classify-txn-name { font-size: 15px; font-weight: 500; color: #111827; }
.classify-txn-amount { font-size: 16px; font-weight: 600; }
.classify-txn-amount.is-income   { color: #16a34a; }
.classify-txn-amount.is-expense  { color: #ef4444; }
.classify-txn-amount.is-transfer { color: #6b7280; }

.category-picker { max-height: 360px; overflow-y: auto; }

.category-group { margin-bottom: 12px; }
.category-group__title {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.category-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 64px;
  cursor: pointer;
  padding: 6px 4px;
  border-radius: 10px;
  transition: background 0.15s;
}
.cat-item:hover { background: #f3f4f6; }
.cat-item--active { background: #f0fdf4; }

.cat-item__icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: #e5e7eb;
}
.cat-item--active .cat-item__icon {
  box-shadow: 0 0 0 2px #16a34a;
}

.cat-item__name {
  font-size: 11px;
  color: #374151;
  text-align: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

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
