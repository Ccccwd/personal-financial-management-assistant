<template>
  <div class="transaction-list-page">
    <div class="page-header">
      <h1 class="page-title">交易记录</h1>
      <el-button type="primary" @click="handleToAdd">
        记一笔
      </el-button>
    </div>

    <!-- Filtering Card -->
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
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Content Area -->
    <el-card class="list-card" shadow="never">
      <div v-loading="loading">
        <div v-if="groupedTransactions.length > 0">
          <!-- Iterate over days -->
          <div v-for="(group, index) in groupedTransactions" :key="index" class="day-group">
            <div class="day-header">
              <div class="day-info">
                <span class="day-date">{{ group.date }}</span>
                <span class="day-desc">{{ getDayOfWeek(group.date) }}</span>
              </div>
              <div class="day-summary">
                <span v-if="group.income > 0" class="inc-text">收: {{ group.income.toFixed(2) }}</span>
                <span v-if="group.expense > 0" class="exp-text">支: {{ group.expense.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="day-list">
              <TransactionCard 
                v-for="item in group.items" 
                :key="item.id" 
                :transaction="item"
                @click="handleToDetail(item.id)"
              />
            </div>
          </div>
        </div>
        
        <el-empty v-else description="暂无交易记录数据" />
      </div>

      <!-- Pagination -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import TransactionCard from '@/components/business/TransactionCard.vue'
import { getTransactions } from '@/api/transactions'
import type { Transaction, TransactionQuery } from '@/types/transaction'

const router = useRouter()

// 状态定义
const loading = ref(false)
const transactions = ref<Transaction[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const form = reactive({
  type: '',
  daterange: [] as string[],
  keyword: ''
})

// 模拟假数据方法，因为后端没准备好
const generateMockData = (): Transaction[] => {
  const mock: Transaction[] = []
  const types: ('income' | 'expense' | 'transfer')[] = ['income', 'expense', 'expense', 'expense']
  const categories = ['餐饮美食', '交通出行', '工资收入', '日常购物']
  const colors = ['#f59e0b', '#3b82f6', '#16a34a', '#8b5cf6']
  
  for(let i=0; i<15; i++) {
    const isIncome = i % 4 === 2
    const d = new Date()
    d.setDate(d.getDate() - (i % 5)) // scatter across last 5 days
    
    mock.push({
      id: i + 1,
      type: types[i % 4],
      amount: isIncome ? 5000 + i*100 : (i+1)*15.5,
      account_id: 1,
      account_name: '招商银行',
      category_id: 1,
      category_name: categories[i % 4],
      category_color: colors[i % 4],
      transaction_date: d.toISOString(),
      merchant_name: isIncome ? '薪资发放' : '星巴克咖啡',
      remark: '备注信息...',
      source: 'manual',
    } as any)
  }
  
  // Sort by date descending
  return mock.sort((a, b) => new Date(b.transaction_date).getTime() - new Date(a.transaction_date).getTime())
}

// 分组逻辑
const groupedTransactions = computed(() => {
  const groups: Record<string, { date: string, income: number, expense: number, items: Transaction[] }> = {}
  
  transactions.value.forEach(item => {
    const dateStr = dayjs(item.transaction_date).format('YYYY年MM月DD日')
    if (!groups[dateStr]) {
      groups[dateStr] = { date: dateStr, income: 0, expense: 0, items: [] }
    }
    
    if (item.type === 'income') groups[dateStr].income += item.amount
    if (item.type === 'expense') groups[dateStr].expense += item.amount
    
    groups[dateStr].items.push(item)
  })
  
  return Object.values(groups)
})

// 辅助方法
const getDayOfWeek = (dateStr: string) => {
  const parsed = dayjs(dateStr.replace(/[年月日]/g, '-'))
  const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return days[parsed.day()]
}

// API请求获取数据
const fetchList = async () => {
  loading.value = true
  try {
    const query: TransactionQuery = {
      page: page.value,
      page_size: pageSize.value,
    }
    
    if (form.type) query.type = form.type as any
    if (form.keyword) query.keyword = form.keyword
    if (form.daterange && form.daterange.length === 2) {
      query.start_date = form.daterange[0]
      query.end_date = form.daterange[1]
    }
    
    const res = await getTransactions(query)
    // 注意: 后端API没好时退回假数据
    if (res && res.data && res.data.transactions) {
      transactions.value = res.data.transactions
      total.value = res.data.total
    } else {
      throw new Error('API 返回格式不匹配')
    }
  } catch (error) {
    console.warn("API调用失败或尚未实现，展示假数据做测试")
    transactions.value = generateMockData()
    total.value = 15
  } finally {
    loading.value = false
  }
}

// 交互操作
const handleSearch = () => {
  page.value = 1
  fetchList()
}

const resetForm = () => {
  form.type = ''
  form.daterange = []
  form.keyword = ''
  handleSearch()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchList()
}

const handleCurrentChange = (val: number) => {
  page.value = val
  fetchList()
}

const handleToAdd = () => {
  router.push('/transactions/add')
}

const handleToDetail = (id: number) => {
  router.push(`/transactions/${id}`)
}

onMounted(() => {
  fetchList()
})
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
  color: #111827; /* color-text-primary */
}

.filter-card {
  border-radius: 12px; /* radius matching architecture design */
  border: 1px solid #e5e7eb;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
}

.list-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 0;
}

:deep(.list-card .el-card__body) {
  padding: 0;
}

.day-group {
  border-bottom: 8px solid #f9fafb;
}

.day-group:last-child {
  border-bottom: none;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f9fafb;
  border-bottom: 1px solid #f3f4f6;
}

.day-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.day-date {
  font-size: 14px;
  font-weight: 600;
  color: #4b5563;
}

.day-desc {
  font-size: 12px;
  color: #9ca3af;
}

.day-summary {
  font-size: 12px;
  display: flex;
  gap: 12px;
}

.inc-text {
  color: #16A34A; /* --color-primary green */
}

.exp-text {
  color: #6b7280;
}

.day-list {
  display: flex;
  flex-direction: column;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
}

/* Style overrides to match Material Design token overrides */
:deep(.el-button--primary) {
  --el-button-bg-color: #16A34A;
  --el-button-border-color: #16A34A;
  --el-button-hover-bg-color: #15803D;
  --el-button-hover-border-color: #15803D;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #16A34A;
}
</style>