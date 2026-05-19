<template>
  <div class="import-page">
    <!-- 页头 -->
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-title">微信账单导入</h1>
        <p class="page-subtitle">支持微信支付导出的 CSV / XLSX 格式账单文件</p>
      </div>
      <div class="page-header__right">
        <el-button :icon="Clock" plain @click="openHistory">导入历史</el-button>
        <el-button :icon="QuestionFilled" plain @click="showGuide = true">导出说明</el-button>
      </div>
    </div>

    <!-- 主卡片 -->
    <el-card class="main-card" shadow="never">
      <!-- 步骤条 -->
      <el-steps :active="activeStep" finish-status="success" align-center class="import-steps">
        <el-step title="上传文件" />
        <el-step title="预览确认" />
        <el-step title="导入结果" />
      </el-steps>

      <!-- ===== STEP 0: 上传 ===== -->
      <div v-if="activeStep === 0" class="step-body step-upload">
        <el-upload
          class="upload-dragger"
          drag
          :auto-upload="false"
          :show-file-list="false"
          accept=".csv,.xlsx"
          @change="handleFileChange"
        >
          <div class="upload-inner">
            <div class="upload-icon-wrap">
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
            </div>
            <p class="upload-text">拖拽账单文件到此处，或 <em>点击选择</em></p>
            <p class="upload-hint">支持微信支付导出的 .csv 和 .xlsx 文件，最大 10 MB</p>
          </div>
        </el-upload>

        <!-- 已选文件信息 -->
        <transition name="slide-down">
          <div v-if="selectedFile" class="file-info-bar">
            <div class="file-info-bar__left">
              <el-icon class="file-icon"><Document /></el-icon>
              <div>
                <div class="file-name">{{ selectedFile.name }}</div>
                <div class="file-meta">{{ formatFileSize(selectedFile.size) }}</div>
              </div>
            </div>
            <div class="file-info-bar__right">
              <el-button link @click="selectedFile = null">更换文件</el-button>
              <el-button type="primary" :loading="loadingPreview" @click="startPreview">
                解析预览 →
              </el-button>
            </div>
          </div>
        </transition>

        <!-- 快速操作说明 -->
        <div class="quick-guide">
          <div class="quick-guide__title">如何导出微信账单？</div>
          <div class="quick-guide__steps">
            <div class="guide-step">
              <span class="guide-step__num">1</span>
              <span>打开微信 → 我 → 服务 → 钱包</span>
            </div>
            <div class="guide-step">
              <span class="guide-step__num">2</span>
              <span>点击右上角 账单 → 常见问题 → 下载账单</span>
            </div>
            <div class="guide-step">
              <span class="guide-step__num">3</span>
              <span>选择时间范围后发送至邮箱，解压压缩包后上传 CSV 或 XLSX 文件</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== STEP 1: 预览 ===== -->
      <div v-if="activeStep === 1" class="step-body step-preview" v-loading="loadingPreview">
        <div class="preview-layout">
          <!-- 左侧：摘要 + 表格 -->
          <div class="preview-main">
            <!-- 摘要卡片 -->
            <div class="summary-cards">
              <div class="summary-card">
                <div class="summary-card__value">{{ previewData?.total_records ?? 0 }}</div>
                <div class="summary-card__label">总笔数</div>
              </div>
              <div class="summary-card summary-card--income">
                <div class="summary-card__value">{{ previewData?.income_count ?? 0 }}</div>
                <div class="summary-card__label">收入笔数</div>
              </div>
              <div class="summary-card summary-card--expense">
                <div class="summary-card__value">{{ previewData?.expense_count ?? 0 }}</div>
                <div class="summary-card__label">支出笔数</div>
              </div>
              <div v-if="(previewData?.potential_duplicates ?? 0) > 0" class="summary-card summary-card--warn">
                <div class="summary-card__value">{{ previewData?.potential_duplicates }}</div>
                <div class="summary-card__label">潜在重复</div>
              </div>
            </div>

            <!-- 账单周期 -->
            <div v-if="previewData?.date_range" class="date-range-bar">
              <el-icon><Calendar /></el-icon>
              <span>账单周期：{{ previewData.date_range.start_date }} 至 {{ previewData.date_range.end_date }}</span>
            </div>

            <!-- 预览表格（前10条） -->
            <div class="preview-table-wrap">
              <div class="preview-table-title">数据抽样预览（前 10 条）</div>
              <el-table
                :data="previewData?.preview_data ?? []"
                style="width: 100%"
                size="small"
                border
                stripe
              >
                <el-table-column label="交易时间" width="155">
                  <template #default="{ row }">
                    {{ formatDateTime(row.transaction_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="counterparty" label="交易对方" width="130" show-overflow-tooltip />
                <el-table-column prop="description" label="商品说明" show-overflow-tooltip />
                <el-table-column label="收/支" width="70" align="center">
                  <template #default="{ row }">
                    <el-tag
                      :type="row.transaction_type === 'income' ? 'success' : 'danger'"
                      size="small"
                      effect="light"
                    >
                      {{ row.transaction_type === 'income' ? '收入' : '支出' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="金额 (元)" width="105" align="right">
                  <template #default="{ row }">
                    <span :class="row.transaction_type === 'income' ? 'amount-income' : 'amount-expense'">
                      {{ row.transaction_type === 'income' ? '+' : '-' }}{{ row.amount.toFixed(2) }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="payment_method" label="支付方式" width="115" show-overflow-tooltip />
                <el-table-column label="" width="32" align="center">
                  <template #default="{ row }">
                    <el-tooltip v-if="row.is_potential_duplicate" content="疑似重复交易" placement="top">
                      <el-icon color="#F59E0B"><WarningFilled /></el-icon>
                    </el-tooltip>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <!-- 右侧：导入设置 -->
          <div class="import-settings">
            <div class="import-settings__title">导入设置</div>

            <el-form label-position="top" class="settings-form">
              <el-form-item label="导入到账户">
                <el-select
                  v-model="importConfig.account_id"
                  placeholder="请选择账户（可不选）"
                  clearable
                  style="width: 100%"
                  :loading="loadingAccounts"
                >
                  <el-option
                    v-for="acc in accounts"
                    :key="acc.id"
                    :label="`${acc.name}（${getAccountTypeName(acc.type)}）`"
                    :value="acc.id"
                  />
                </el-select>
                <div class="form-hint">不选则自动使用默认账户</div>
              </el-form-item>

              <el-form-item label="默认分类">
                <el-select
                  v-model="importConfig.category_id"
                  placeholder="不指定（可后续手动分类）"
                  clearable
                  style="width: 100%"
                  :loading="loadingCategories"
                >
                  <el-option-group label="支出">
                    <el-option
                      v-for="cat in expenseCategories"
                      :key="cat.id"
                      :label="`${cat.icon ?? ''} ${cat.name}`"
                      :value="cat.id"
                    />
                  </el-option-group>
                  <el-option-group label="收入">
                    <el-option
                      v-for="cat in incomeCategories"
                      :key="cat.id"
                      :label="`${cat.icon ?? ''} ${cat.name}`"
                      :value="cat.id"
                    />
                  </el-option-group>
                </el-select>
                <div class="form-hint">所有导入记录将使用该分类，可留空后续手动修改</div>
              </el-form-item>
            </el-form>

            <div class="auto-dedup-tip">
              <el-icon color="#16a34a"><CircleCheckFilled /></el-icon>
              <span>系统自动识别并跳过已导入的重复交易</span>
            </div>

            <div class="settings-actions">
              <el-button @click="resetImport" :disabled="loadingImport">重新上传</el-button>
              <el-button type="primary" :loading="loadingImport" @click="executeImport">
                确认导入
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== STEP 2: 结果 ===== -->
      <div v-if="activeStep === 2" class="step-body step-result">
        <el-result
          :icon="importResult && importResult.failed_count === 0 ? 'success' : 'warning'"
          :title="importResult && importResult.failed_count === 0 ? '导入完成' : '部分导入成功'"
        >
          <template #sub-title>
            <div class="result-stats">
              <div class="result-stat">
                <span class="result-stat__num result-stat__num--total">{{ importResult?.total ?? 0 }}</span>
                <span class="result-stat__label">共处理</span>
              </div>
              <div class="result-stat">
                <span class="result-stat__num result-stat__num--success">{{ importResult?.success_count ?? 0 }}</span>
                <span class="result-stat__label">成功入账</span>
              </div>
              <div class="result-stat">
                <span class="result-stat__num result-stat__num--skip">{{ importResult?.skipped_count ?? 0 }}</span>
                <span class="result-stat__label">跳过重复</span>
              </div>
              <div v-if="(importResult?.failed_count ?? 0) > 0" class="result-stat">
                <span class="result-stat__num result-stat__num--fail">{{ importResult?.failed_count }}</span>
                <span class="result-stat__label">处理失败</span>
              </div>
            </div>
          </template>
          <template #extra>
            <!-- AI 批量分类区域 -->
            <div class="ai-classify-block">
              <template v-if="!aiClassifyState.done">
                <el-button
                  type="success"
                  :loading="aiClassifyState.loading"
                  @click="runAIBatchClassify"
                >
                  <el-icon v-if="!aiClassifyState.loading"><MagicStick /></el-icon>
                  {{ aiClassifyState.loading ? `AI 识别中 (${aiClassifyState.current}/${aiClassifyState.total})` : 'AI 智能分类' }}
                </el-button>
                <div class="ai-classify-hint">由 AI 自动识别未分类账单的交易类别</div>
              </template>
              <el-alert
                v-else
                type="success"
                :closable="false"
                show-icon
                style="margin-bottom:8px"
              >
                AI 已完成识别：{{ aiClassifyState.successCount }}/{{ aiClassifyState.total }} 条成功分类
              </el-alert>
            </div>
            <div class="result-actions">
              <el-button @click="resetImport">继续导入</el-button>
              <el-button type="primary" @click="$router.push('/transactions')">查看账单流水</el-button>
            </div>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- ===== 导入历史抽屉 ===== -->
    <el-drawer v-model="showHistory" title="导入历史记录" size="480px" destroy-on-close>
      <el-table
        :data="historyLogs"
        v-loading="loadingHistory"
        style="width: 100%"
        empty-text="暂无导入记录"
      >
        <el-table-column label="导入时间" width="155">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="文件名" show-overflow-tooltip>
          <template #default="{ row }">{{ row.file_name || row.source }}</template>
        </el-table-column>
        <el-table-column label="结果" width="150">
          <template #default="{ row }">
            <div class="log-result">
              <span class="log-result__success">✓ {{ row.success_records }}</span>
              <span v-if="row.skipped_records > 0" class="log-result__skip">⊘ {{ row.skipped_records }}</span>
              <span v-if="row.failed_records > 0" class="log-result__fail">✕ {{ row.failed_records }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'completed' ? 'success' : row.status === 'partial' ? 'warning' : 'danger'"
              size="small"
              effect="light"
            >
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>

    <!-- ===== 导出说明对话框 ===== -->
    <el-dialog v-model="showGuide" title="微信账单导出说明" width="480px" align-center>
      <ol class="guide-list">
        <li>打开手机微信，依次点击 <strong>我 → 服务 → 钱包</strong></li>
        <li>点击页面右上角 <strong>账单</strong>，进入账单页面</li>
        <li>点击右上角 <strong>···</strong>，选择 <strong>常见问题</strong></li>
        <li>点击 <strong>下载账单</strong>，选择账单类型与时间范围</li>
        <li>账单将通过邮件发送，<strong>解压附件</strong>后得到 .csv 文件</li>
        <li>将该文件上传至本页即可完成导入</li>
      </ol>
      <template #footer>
        <el-button type="primary" @click="showGuide = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  UploadFilled, Document, Clock, QuestionFilled,
  Calendar, CircleCheckFilled, WarningFilled, MagicStick,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import dayjs from 'dayjs'

import { previewBill, importBill, getImportLogs } from '@/api/wechat'
import { getAccounts } from '@/api/accounts'
import { getCategories } from '@/api/categories'
import { getTransactions } from '@/api/transactions'
import { reclassifyTransaction } from '@/api/ai'

import type { ImportPreviewResponse, ImportResult, ImportLog } from '@/types/wechat'
import type { AccountListPayload } from '@/types/account'
import type { CategoryListPayload, Category } from '@/types/category'

const router = useRouter()

// ── 步骤状态 ──────────────────────────────────────────────
const activeStep = ref(0)
const selectedFile = ref<File | null>(null)

const loadingPreview = ref(false)
const loadingImport  = ref(false)
const loadingAccounts    = ref(false)
const loadingCategories  = ref(false)

// ── 数据 ─────────────────────────────────────────────────
const previewData  = ref<ImportPreviewResponse | null>(null)
const importResult = ref<ImportResult | null>(null)

// ── AI 批量分类 ────────────────────────────────────────────
const aiClassifyState = reactive({
  loading: false,
  done: false,
  total: 0,
  current: 0,
  successCount: 0,
})

const accounts   = ref<{ id: number; name: string; type: string }[]>([])
const allCategories = ref<Category[]>([])

const expenseCategories = computed(() => allCategories.value.filter(c => c.type === 'expense'))
const incomeCategories  = computed(() => allCategories.value.filter(c => c.type === 'income'))

const importConfig = reactive({
  account_id:  undefined as number | undefined,
  category_id: undefined as number | undefined,
})

// ── 历史记录 ──────────────────────────────────────────────
const showHistory    = ref(false)
const loadingHistory = ref(false)
const historyLogs    = ref<ImportLog[]>([])

// ── 对话框 ────────────────────────────────────────────────
const showGuide = ref(false)

// ── 格式化工具 ────────────────────────────────────────────
const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

const formatDateTime = (val: string) => dayjs(val).format('YYYY-MM-DD HH:mm')

const getAccountTypeName = (type: string) => {
  const map: Record<string, string> = {
    cash: '现金', bank: '银行卡', wechat: '微信', alipay: '支付宝',
    meal_card: '饭卡', credit: '信用卡', other: '其它',
  }
  return map[type] ?? type
}

const statusLabel = (status: string) => {
  const map: Record<string, string> = {
    completed: '完成', partial: '部分', failed: '失败',
    processing: '处理中', pending: '待处理',
  }
  return map[status] ?? status
}

// ── 加载基础数据 ──────────────────────────────────────────
const loadAccounts = async () => {
  loadingAccounts.value = true
  try {
    const res = await getAccounts() as unknown as AccountListPayload
    accounts.value = res?.accounts ?? []
    if (accounts.value.length && !importConfig.account_id) {
      const defaultAcc = accounts.value.find((a: any) => a.is_default) ?? accounts.value[0]
      importConfig.account_id = defaultAcc.id
    }
  } catch {
    accounts.value = []
  } finally {
    loadingAccounts.value = false
  }
}

const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const res = await getCategories() as unknown as CategoryListPayload
    allCategories.value = res?.categories ?? []
  } catch {
    allCategories.value = []
  } finally {
    loadingCategories.value = false
  }
}

// ── 文件选择 ──────────────────────────────────────────────
const handleFileChange = (uploadFile: UploadFile) => {
  if (uploadFile.raw) {
    selectedFile.value = uploadFile.raw
  }
}

// ── Step 0 → 1: 预览 ──────────────────────────────────────
const startPreview = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  loadingPreview.value = true
  try {
    const res = await previewBill(selectedFile.value) as unknown as ImportPreviewResponse
    previewData.value = res
    activeStep.value = 1
  } finally {
    loadingPreview.value = false
  }
}

// ── Step 1 → 2: 导入 ──────────────────────────────────────
const executeImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('缺少文件，请重新上传')
    return
  }
  loadingImport.value = true
  try {
    const res = await importBill({
      file: selectedFile.value,
      account_id:  importConfig.account_id,
      category_id: importConfig.category_id,
    }) as unknown as ImportResult
    importResult.value = res
    activeStep.value = 2
    // 刷新历史列表
    loadHistory()
  } finally {
    loadingImport.value = false
  }
}

// ── 重置流程 ──────────────────────────────────────────────
const resetImport = () => {
  activeStep.value   = 0
  selectedFile.value = null
  previewData.value  = null
  importResult.value = null
  importConfig.category_id = undefined
  aiClassifyState.loading = false
  aiClassifyState.done    = false
  aiClassifyState.total   = 0
  aiClassifyState.current = 0
  aiClassifyState.successCount = 0
}

const runAIBatchClassify = async () => {
  if (!previewData.value?.date_range) return
  aiClassifyState.loading = true
  aiClassifyState.done    = false
  aiClassifyState.total   = 0
  aiClassifyState.current = 0
  aiClassifyState.successCount = 0

  try {
    const { start_date, end_date } = previewData.value.date_range
    const listRes = await getTransactions({
      start_date,
      end_date,
      page_size: 500,
      page: 1,
    }) as any
    const all: any[] = listRes?.transactions ?? listRes?.data?.transactions ?? []
    const uncategorized = all.filter((t: any) => !t.category_id)
    aiClassifyState.total = uncategorized.length

    if (uncategorized.length === 0) {
      ElMessage.info('该批账单已全部完成分类，无需 AI 识别')
      aiClassifyState.done = true
      return
    }

    for (const txn of uncategorized) {
      try {
        const res = await reclassifyTransaction(txn.id, false) as any
        if (res?.category_id || res?.data?.category_id) {
          aiClassifyState.successCount++
        }
      } catch {
        // 单条失败不中断
      }
      aiClassifyState.current++
    }

    aiClassifyState.done = true
    ElMessage.success(`AI 分类完成：${aiClassifyState.successCount}/${aiClassifyState.total} 条成功识别`)
  } catch {
    ElMessage.error('AI 批量分类失败，请稍后重试')
  } finally {
    aiClassifyState.loading = false
  }
}

// ── 历史记录 ──────────────────────────────────────────────
const openHistory = () => {
  showHistory.value = true
  loadHistory()
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await getImportLogs({ page: 1, page_size: 50 }) as unknown as { logs: ImportLog[] }
    historyLogs.value = res?.logs ?? []
  } catch {
    historyLogs.value = []
  } finally {
    loadingHistory.value = false
  }
}

onMounted(() => {
  loadAccounts()
  loadCategories()
})
</script>

<style scoped>
/* ── 页面布局 ─────────────────────────────────────────────── */
.import-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 12px;
}

.page-title {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.page-subtitle {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.page-header__right {
  display: flex;
  gap: 10px;
}

.main-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

/* ── 步骤条 ──────────────────────────────────────────────── */
.import-steps {
  padding: 24px 60px 32px;
}

/* ── 步骤通用容器 ────────────────────────────────────────── */
.step-body {
  padding: 0 24px 36px;
}

/* ── Step 0: 上传 ────────────────────────────────────────── */
.step-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  max-width: 680px;
  margin: 0 auto;
}

.upload-dragger {
  width: 100%;
}

.upload-inner {
  padding: 36px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.upload-icon-wrap {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #dcfce7, #bbf7d0);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.upload-icon {
  font-size: 32px;
  color: #16a34a;
}

.upload-text {
  margin: 0;
  font-size: 15px;
  color: #374151;
}

.upload-text em {
  color: #16a34a;
  font-style: normal;
  font-weight: 600;
}

.upload-hint {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
}

/* 已选文件信息栏 */
.file-info-bar {
  width: 100%;
  padding: 14px 18px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.file-info-bar__left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 28px;
  color: #3b82f6;
}

.file-name {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.file-meta {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.file-info-bar__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* 快速指引 */
.quick-guide {
  width: 100%;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  padding: 16px 20px;
}

.quick-guide__title {
  font-size: 13px;
  font-weight: 600;
  color: #15803d;
  margin-bottom: 12px;
}

.quick-guide__steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.guide-step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: #374151;
}

.guide-step__num {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  background: #16a34a;
  color: #fff;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── Step 1: 预览 ────────────────────────────────────────── */
.preview-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.preview-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 摘要卡片组 */
.summary-cards {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.summary-card {
  flex: 1;
  min-width: 100px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px 16px;
  text-align: center;
}

.summary-card--income {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.summary-card--expense {
  background: #fef2f2;
  border-color: #fecaca;
}

.summary-card--warn {
  background: #fffbeb;
  border-color: #fde68a;
}

.summary-card__value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
}

.summary-card--income .summary-card__value { color: #16a34a; }
.summary-card--expense .summary-card__value { color: #ef4444; }
.summary-card--warn .summary-card__value    { color: #d97706; }

.summary-card__label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

/* 账单周期 */
.date-range-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

/* 预览表格 */
.preview-table-wrap {
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.preview-table-title {
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.amount-income {
  color: #16a34a;
  font-weight: 600;
}

.amount-expense {
  color: #ef4444;
  font-weight: 600;
}

/* 导入设置面板 */
.import-settings {
  width: 280px;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.import-settings__title {
  font-size: 15px;
  font-weight: 700;
  color: #111827;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.settings-form {
  flex: 1;
}

.form-hint {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 4px;
  line-height: 1.4;
}

.auto-dedup-tip {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: #16a34a;
  background: #f0fdf4;
  border-radius: 8px;
  padding: 8px 12px;
}

.settings-actions {
  display: flex;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.settings-actions .el-button {
  flex: 1;
}

/* ── Step 2: 结果 ────────────────────────────────────────── */
.step-result {
  max-width: 600px;
  margin: 0 auto;
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.result-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.result-stat__num {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.result-stat__num--total   { color: #374151; }
.result-stat__num--success { color: #16a34a; }
.result-stat__num--skip    { color: #d97706; }
.result-stat__num--fail    { color: #ef4444; }

.result-stat__label {
  font-size: 12px;
  color: #9ca3af;
}

/* ── 历史记录 ────────────────────────────────────────────── */
.log-result {
  display: flex;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
}

.log-result__success { color: #16a34a; }
.log-result__skip    { color: #d97706; }
.log-result__fail    { color: #ef4444; }

/* ── 说明弹窗 ────────────────────────────────────────────── */
.guide-list {
  padding-left: 20px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
}

/* ── Element Plus 主题覆盖 ───────────────────────────────── */
:deep(.el-button--primary) {
  --el-button-bg-color: #16a34a;
  --el-button-border-color: #16a34a;
  --el-button-hover-bg-color: #15803d;
  --el-button-hover-border-color: #15803d;
}

:deep(.el-step__head.is-success),
:deep(.el-step__title.is-success) {
  color: #16a34a;
  border-color: #16a34a;
}

:deep(.el-step__head.is-process) {
  color: #16a34a;
  border-color: #16a34a;
}

.ai-classify-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin-bottom: 16px;
}

.ai-classify-hint {
  font-size: 12px;
  color: #9ca3af;
}

.result-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}
</style>
