<template>
  <div class="account-list-page">
    <div class="page-header">
      <h1 class="page-title">账户管理</h1>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon>新增账户
      </el-button>
    </div>

    <!-- 总体资产摘要卡片 -->
    <el-card class="summary-card" shadow="never" v-loading="loadingSummary">
      <div class="summary-content">
        <div class="summary-item">
          <div class="summary-label">总资产</div>
          <div class="summary-value amount-positive">{{ summary.total_balance.toFixed(2) }}</div>
        </div>
        <div class="summary-item">
          <div class="summary-label">账户总数</div>
          <div class="summary-value">{{ summary.total_accounts }} 个</div>
        </div>
        <div class="summary-item distribute-item" v-if="summary.account_distribution.length">
          <div class="distribute-bar">
            <!-- 简单的柱状占比展示 -->
            <div 
              v-for="(dist, idx) in summary.account_distribution" 
              :key="idx"
              class="dist-segment"
              :style="{ width: ((dist.balance / summary.total_balance) * 100) + '%', backgroundColor: getAccountTypeColor(dist.type) }"
              :title="`${getAccountTypeName(dist.type)}: ${dist.balance.toFixed(2)}`"
            ></div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 账户列表 -->
    <div v-loading="loadingList">
      <div v-if="accounts.length > 0" class="account-grid">
        <el-card 
          v-for="account in accounts" 
          :key="account.id" 
          class="account-card" 
          shadow="hover"
          @click="handleToDetail(account.id)"
        >
          <div class="account-header">
            <div class="account-icon-wrap" :style="{ backgroundColor: getAccountTypeColor(account.type) + '1A', color: getAccountTypeColor(account.type) }">
              <el-icon><component :is="getAccountTypeIcon(account.type)" /></el-icon>
            </div>
            <div class="account-name-section">
              <div class="account-name">{{ account.name }}</div>
              <div class="account-type">{{ getAccountTypeName(account.type) }}</div>
            </div>
            <el-tag v-if="account.is_default" size="small" type="success" effect="light" class="default-tag">默认</el-tag>
          </div>
          
          <div class="account-balance">
            <span class="currency">¥</span>
            <span class="amount">{{ account.balance.toFixed(2) }}</span>
          </div>

          <div class="account-actions" @click.stop>
            <el-button link type="primary" @click="openTransferDialog(account)">转账</el-button>
            <el-button link type="primary" @click="openEditDialog(account)">编辑</el-button>
            <el-popconfirm title="确定要删除此账户吗？将会检查是否有账单关联。" @confirm="handleDelete(account.id)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </el-card>
      </div>
      
      <el-empty v-else description="暂无账户，请点击右上角新增" />
    </div>

    <!-- 新增/编辑账户对话框 -->
    <el-dialog 
      :title="accountForm.id ? '编辑账户' : '新增账户'" 
      v-model="dialogVisible" 
      width="400px" 
      destroy-on-close
    >
      <el-form :model="accountForm" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="账户名称" prop="name">
          <el-input v-model="accountForm.name" placeholder="请输入账户名称，如招商银行" />
        </el-form-item>
        <el-form-item label="账户类型" prop="type">
          <el-select v-model="accountForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="现金" value="cash" />
            <el-option label="银行卡" value="bank" />
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="饭卡" value="meal_card" />
            <el-option label="其它" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始余额" prop="initial_balance" v-if="!accountForm.id">
          <el-input-number v-model="accountForm.initial_balance" :precision="2" :step="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="默认账户" prop="is_default">
          <el-switch v-model="accountForm.is_default" />
        </el-form-item>
        <el-form-item label="备注说明" prop="description">
          <el-input v-model="accountForm.description" type="textarea" placeholder="可选填写" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAccount" :loading="submitLoading">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 转账对话框 -->
    <el-dialog title="账户间转账" v-model="transferVisible" width="400px" destroy-on-close>
      <el-form :model="transferForm" :rules="transferRules" ref="transferRef" label-width="80px">
        <el-form-item label="转出账户">
          <el-input :value="transferForm.from_account_name" disabled />
        </el-form-item>
        <el-form-item label="转入账户" prop="to_account_id">
          <el-select v-model="transferForm.to_account_id" placeholder="请选择转入账户" style="width: 100%">
            <el-option 
              v-for="acc in selectableAccounts" 
              :key="acc.id" 
              :label="acc.name + (acc.balance ? ' (余额: ' + acc.balance + ')' : '')" 
              :value="acc.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="转账金额" prop="amount">
          <el-input-number v-model="transferForm.amount" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="转账时间" prop="transaction_date">
          <el-date-picker v-model="transferForm.transaction_date" type="datetime" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="transferForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="transferVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTransfer" :loading="submitLoading">确定转账</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'
import { Plus, Wallet, CreditCard, ChatRound, Grid, Food, Money } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { 
  getAccounts, 
  getAccountSummary, 
  createAccount, 
  updateAccount, 
  deleteAccount,
  transfer
} from '@/api/accounts'
import type { Account, AccountSummary } from '@/types/account'

const router = useRouter()

// 状态控制
const loadingSummary = ref(false)
const loadingList = ref(false)
const dialogVisible = ref(false)
const transferVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const transferRef = ref<FormInstance>()

// 数据
const accounts = ref<Account[]>([])
const summary = ref<AccountSummary>({
  total_balance: 0,
  total_accounts: 0,
  account_distribution: []
})

// 可选择的转入账户
const selectableAccounts = computed(() => {
  return accounts.value.filter(a => a.id !== transferForm.from_account_id)
})

// 表单模型
const accountForm = reactive({
  id: 0,
  name: '',
  type: 'bank',
  initial_balance: 0,
  is_default: false,
  description: ''
})

const transferForm = reactive({
  from_account_id: 0,
  from_account_name: '',
  to_account_id: undefined as number | undefined,
  amount: undefined as number | undefined,
  transaction_date: '',
  remark: ''
})

// 校验规则
const rules = {
  name: [{ required: true, message: '请输入账户名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择账户类型', trigger: 'change' }]
}
const transferRules = {
  to_account_id: [{ required: true, message: '请选择转入账户', trigger: 'change' }],
  amount: [{ required: true, message: '请输入转账金额', trigger: 'blur' }]
}

// 字典映射
const getAccountTypeName = (type: string) => {
  const map: Record<string, string> = {
    cash: '现金', bank: '银行卡', wechat: '微信', alipay: '支付宝', meal_card: '饭卡', other: '其它'
  }
  return map[type] || '未知'
}

const getAccountTypeIcon = (type: string) => {
  const map: Record<string, any> = {
    cash: Money, bank: CreditCard, wechat: ChatRound, alipay: Grid, meal_card: Food, other: Wallet
  }
  return map[type] || Wallet
}

const getAccountTypeColor = (type: string) => {
  const map: Record<string, string> = {
    cash: '#F59E0B', bank: '#3B82F6', wechat: '#10B981', alipay: '#3B82F6', meal_card: '#F43F5E', other: '#6B7280'
  }
  return map[type] || '#6B7280'
}

// 获取列表数据 & Mock 测试数据
const fetchData = async () => {
  loadingList.value = true
  loadingSummary.value = true
  try {
    const listRes = await getAccounts()
    // 修正：request.ts 拦截器已经直接返回了 res.data，所以这里使用 listRes.accounts
    const listData = listRes as any
    if (listData?.accounts) {
      accounts.value = listData.accounts
    }
    
    const sumRes = await getAccountSummary()
    if (sumRes) {
      summary.value = sumRes as any
    }
  } catch (error) {
    console.warn("API调用失败或未找到后端，加载测试 Mock 数据")
    // Mock accounts
    accounts.value = [
      { id: 1, name: '招商银行信用卡', type: 'bank', balance: -2000.5, initial_balance: 0, is_default: false, is_enabled: true },
      { id: 2, name: '微信零钱', type: 'wechat', balance: 5400.0, initial_balance: 0, is_default: true, is_enabled: true },
      { id: 3, name: '支付宝余额宝', type: 'alipay', balance: 13500.5, initial_balance: 0, is_default: false, is_enabled: true },
      { id: 4, name: '饭卡', type: 'meal_card', balance: 156.0, initial_balance: 0, is_default: false, is_enabled: true }
    ] as Account[]
    // Mock summary
    let sum = 0
    const distribution: any[] = []
    accounts.value.forEach(a => {
      sum += a.balance
      const existing = distribution.find(d => d.type === a.type)
      if(existing) {
        existing.balance += a.balance
        existing.count += 1
      } else {
        distribution.push({ type: a.type, balance: a.balance, count: 1 })
      }
    })
    summary.value = {
      total_balance: sum,
      total_accounts: accounts.value.length,
      account_distribution: distribution.filter(d => d.balance > 0)
    }
  } finally {
    loadingList.value = false
    loadingSummary.value = false
  }
}

// 弹窗交互
const openAddDialog = () => {
  accountForm.id = 0
  accountForm.name = ''
  accountForm.type = 'bank'
  accountForm.initial_balance = 0
  accountForm.is_default = false
  accountForm.description = ''
  dialogVisible.value = true
}

const openEditDialog = (item: Account) => {
  accountForm.id = item.id
  accountForm.name = item.name
  accountForm.type = item.type
  accountForm.initial_balance = item.initial_balance
  accountForm.is_default = item.is_default
  accountForm.description = item.description || ''
  dialogVisible.value = true
}

const openTransferDialog = (item: Account) => {
  transferForm.from_account_id = item.id
  transferForm.from_account_name = item.name
  transferForm.to_account_id = undefined
  transferForm.amount = undefined
  transferForm.transaction_date = dayjs().format('YYYY-MM-DD HH:mm:ss')
  transferForm.remark = ''
  transferVisible.value = true
}

const handleToDetail = (id: number) => {
  router.push(`/accounts/${id}`)
}

// 提交动作
const submitAccount = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (accountForm.id) {
          await updateAccount(accountForm.id, accountForm as any)
          ElMessage.success('账户修改成功')
        } else {
          await createAccount(accountForm as any)
          ElMessage.success('账户创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (err) {
        ElMessage.error('操作失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const submitTransfer = async () => {
  if (!transferRef.value) return
  await transferRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await transfer(transferForm as any)
        ElMessage.success('转账成功')
        transferVisible.value = false
        fetchData()
      } catch (err) {
        ElMessage.error('转账失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = async (id: number) => {
  try {
    await deleteAccount(id)
    ElMessage.success('账户删除成功')
    fetchData()
  } catch (err) {
    ElMessage.error('删除账户失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.account-list-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.summary-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.summary-content {
  display: flex;
  gap: 40px;
  align-items: center;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.distribute-item {
  flex: 1;
  max-width: 400px;
}

.summary-label {
  font-size: 14px;
  color: #6b7280;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
}

.amount-positive {
  color: #16A34A;
}

.distribute-bar {
  display: flex;
  height: 8px;
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
  background-color: #f3f4f6;
  margin-top: 8px;
}

.dist-segment {
  height: 100%;
}

.account-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.account-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.account-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.account-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
  position: relative;
}

.account-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.account-name-section {
  display: flex;
  flex-direction: column;
}

.account-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.account-type {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.default-tag {
  position: absolute;
  right: 0;
  top: 0;
}

.account-balance {
  margin-bottom: 20px;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.currency {
  font-size: 16px;
  color: #4b5563;
  font-weight: 500;
}

.amount {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.5px;
}

.account-actions {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

/* Material overrides for Primary color (#16A34A) */
:deep(.el-button--primary) {
  --el-button-bg-color: #16A34A;
  --el-button-border-color: #16A34A;
  --el-button-hover-bg-color: #15803D;
  --el-button-hover-border-color: #15803D;
}
</style>