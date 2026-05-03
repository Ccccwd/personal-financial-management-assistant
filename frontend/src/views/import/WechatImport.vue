<template>
  <div class="import-page">
    <div class="page-header">
      <h1 class="page-title">账单导入</h1>
      <div class="header-actions">
        <el-button color="#111827" plain :icon="Document" @click="downloadTemplate">下载模板使用说明</el-button>
        <el-button @click="showHistory = true">导入记录</el-button>
      </div>
    </div>

    <el-card class="import-card" shadow="never">
      <!-- 步骤条 -->
      <el-steps :active="activeStep" finish-status="success" align-center class="import-steps">
        <el-step title="上传文件" description="选择微信账单 CSV 文件" />
        <el-step title="数据预览" description="确认格式与导入设置" />
        <el-step title="导入结果" description="查看成功与失败情况" />
      </el-steps>

      <!-- 第一步：上传区域 -->
      <div v-if="activeStep === 0" class="step-content step-upload">
        <el-upload
          class="upload-area"
          drag
          :auto-upload="false"
          :show-file-list="false"
          accept=".csv"
          @change="handleFileChange"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将微信账单 CSV 文件拖到此处，或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              请在微信支付中导出账单并解压后，上传后缀为 .csv 的文件。
            </div>
          </template>
        </el-upload>
        <div v-if="selectedFile" class="selected-file">
          <el-icon><Document /></el-icon>
          <span class="file-name">{{ selectedFile.name }}</span>
          <span class="file-size">{{ (selectedFile.size / 1024).toFixed(1) }} KB</span>
          <el-button type="primary" :loading="loadingPreview" @click="startPreview" class="btn-next">
            解析并预览
          </el-button>
        </div>
      </div>

      <!-- 第二步：预览与设置 -->
      <div v-if="activeStep === 1" class="step-content step-preview" v-loading="loadingPreview">
        <el-row :gutter="24">
          <!-- 左侧：预览数据信息 -->
          <el-col :span="16">
            <div class="preview-header">
              <h3>解析概览</h3>
              <div class="summary-tags">
                <el-tag type="info">总笔数：{{ previewData?.summary.total_records || 0 }} 笔</el-tag>
                <el-tag type="success">收入：¥ {{ formatNumber(previewData?.summary.total_income) }}</el-tag>
                <el-tag type="danger">支出：¥ {{ formatNumber(previewData?.summary.total_expense) }}</el-tag>
                <el-tag type="warning" v-if="previewData?.summary.potential_duplicates">
                  潜在重复：{{ previewData.summary.potential_duplicates }} 笔
                </el-tag>
              </div>
              <div class="date-range" v-if="previewData?.summary.start_date">
                账单周期：{{ previewData.summary.start_date }} 至 {{ previewData.summary.end_date }}
              </div>
            </div>

            <div class="preview-table">
              <h4>数据抽样 (前 10 条)</h4>
              <el-table :data="previewData?.preview_data || []" style="width: 100%" size="small" border>
                <el-table-column prop="transaction_date" label="交易时间" width="160" />
                <el-table-column prop="merchant_name" label="交易对象" width="150" show-overflow-tooltip />
                <el-table-column prop="product_name" label="商品/说明" show-overflow-tooltip />
                <el-table-column prop="amount" label="金额 (元)" width="100" align="right">
                  <template #default="{ row }">
                    <span :class="row.amount >= 0 ? 'income' : 'expense'">
                      {{ row.amount >= 0 ? '+' : '' }}{{ row.amount }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="payment_method" label="支付方式" width="120" />
              </el-table>
            </div>
          </el-col>
          
          <!-- 右侧：导入设置 -->
          <el-col :span="8">
            <div class="import-settings">
              <h3>导入设置</h3>
              <el-form label-position="top">
                <el-form-item label="默认资金账户">
                  <el-select v-model="importConfig.default_account_id" placeholder="请选择收款/付款账户" style="width:100%">
                    <el-option
                      v-for="acc in accounts"
                      :key="acc.id"
                      :label="acc.name + ' (' + getAccountTypeName(acc.type) + ')'"
                      :value="acc.id"
                    />
                  </el-select>
                  <div class="setting-hint">非转账交易将默认计入此账户，通常为零钱或银行卡</div>
                </el-form-item>

                <el-form-item>
                  <template #label>
                    智能分类 (AI)
                  </template>
                  <el-switch v-model="importConfig.ai_classify" />
                  <div class="setting-hint">使用 AI 大模型根据商品名称自动归类，此操作会增加几十秒服务器处理时间</div>
                </el-form-item>

                <el-form-item>
                  <template #label>
                    跳过重复账单
                  </template>
                  <el-switch v-model="importConfig.skip_duplicates" />
                  <div class="setting-hint">对比已有交易单号，防止同月份流水被多次记账</div>
                </el-form-item>
              </el-form>

              <div class="step-actions">
                <el-button @click="activeStep = 0; selectedFile = null" :disabled="loadingImport">重新上传</el-button>
                <el-button type="primary" @click="executeImport" :loading="loadingImport">确认开始导入</el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 第三步：导入结果 -->
      <div v-if="activeStep === 2" class="step-content step-result">
        <el-result :icon="importResult?.fail_count === 0 ? 'success' : 'warning'" :title="importResult?.fail_count === 0 ? '导入成功' : '部分导入成功'">
          <template #sub-title>
            本次共处理 {{ importResult?.total_count || 0 }} 条记录。
            成功 <span class="income">{{ importResult?.success_count || 0 }}</span> 条，
            跳过重复 <span class="warning">{{ importResult?.duplicate_count || 0 }}</span> 条，
            失败 <span class="error-text">{{ importResult?.fail_count || 0 }}</span> 条。
            <br /><br />
            <span v-if="importConfig.ai_classify" style="color: #6b7280">AI大模型成功为您分类了 {{ importResult?.ai_classified_count || 0 }} 条记录。</span>
          </template>
          <template #extra>
            <el-button @click="resetImport">继续导入更多</el-button>
            <el-button type="primary" @click="$router.push('/transactions')">前往查看流水</el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 导入记录抽屉 -->
    <el-drawer
      v-model="showHistory"
      title="导入历史记录"
      size="50%"
    >
      <el-table :data="historyLogs" v-loading="loadingHistory" style="width: 100%">
        <el-table-column prop="import_time" label="导入时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.import_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源文件" show-overflow-tooltip />
        <el-table-column label="结果状态" width="180">
          <template #default="{ row }">
            <div><span class="income">成功入库: {{ row.success_count }}</span></div>
            <div><span class="warning">过滤重复: {{ row.duplicate_count }}</span></div>
            <div v-if="row.fail_count > 0"><span class="expense">处理失败: {{ row.fail_count }}</span></div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button v-if="row.fail_count > 0" link type="primary">报错详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import dayjs from 'dayjs'
import { previewBill, importBill, getImportLogs } from '@/api/wechat'
import { getAccounts } from '@/api/accounts'

const activeStep = ref(0)
const selectedFile = ref<File | null>(null)
const loadingPreview = ref(false)
const loadingImport = ref(false)

const previewData = ref<any>(null)
const importResult = ref<any>(null)
const accounts = ref<any[]>([])

const importConfig = reactive({
  default_account_id: undefined as number | undefined,
  ai_classify: true,
  skip_duplicates: true
})

// 历史记录
const showHistory = ref(false)
const loadingHistory = ref(false)
const historyLogs = ref<any[]>([])

const formatNumber = (num?: number) => {
  return (num || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const getAccountTypeName = (type: string) => {
  const map: Record<string, string> = {
    cash: '现金', bank: '银行卡', wechat: '微信', alipay: '支付宝', meal_card: '饭卡', other: '其它'
  }
  return map[type] || type
}

const loadDependencyData = async () => {
  try {
    const listRes = await getAccounts()
    const listData = listRes as any
    if (listData?.accounts) {
      accounts.value = listData.accounts
      // 默认选中第一个
      if (accounts.value.length > 0) {
        importConfig.default_account_id = accounts.value[0].id
      }
    }
  } catch (error) {
    accounts.value = [
      { id: 1, name: '招商银行信用卡', type: 'bank' },
      { id: 2, name: '微信零钱', type: 'wechat' }
    ]
    importConfig.default_account_id = 2
  }
}

const handleFileChange = (uploadFile: UploadFile) => {
  if (uploadFile.raw) {
    selectedFile.value = uploadFile.raw
  }
}

const startPreview = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  loadingPreview.value = true
  try {
    const res = await previewBill(selectedFile.value)
    previewData.value = (res as any)?.data || res
    activeStep.value = 1
  } catch (error) {
    console.warn("预览 API 失败，注入 Mock 数据")
    // Mock Data Fallback
    previewData.value = {
      summary: {
        total_records: 142,
        income_count: 12,
        expense_count: 130,
        total_income: 15400.0,
        total_expense: 3450.5,
        start_date: '2026-03-01',
        end_date: '2026-03-31',
        potential_duplicates: 2
      },
      preview_data: [
        { transaction_date: '2026-03-31 18:30:00', merchant_name: '星巴克', product_name: '拿铁咖啡大杯', amount: -32.0, payment_method: '零钱' },
        { transaction_date: '2026-03-30 09:12:00', merchant_name: '腾讯乘车码', product_name: '广州地铁二维码', amount: -5.0, payment_method: '招商银行(1234)' },
        { transaction_date: '2026-03-29 12:00:00', merchant_name: '公司财务', product_name: '3月工资发放', amount: 15000.0, payment_method: '招商银行(1234)' },
        { transaction_date: '2026-03-28 20:15:00', merchant_name: '美团外卖', product_name: '麦当劳订单', amount: -45.5, payment_method: '零钱' },
        { transaction_date: '2026-03-27 10:00:00', merchant_name: '全家便利店', product_name: '便当及饮料', amount: -18.9, payment_method: '零钱' }
      ]
    }
    setTimeout(() => {
      loadingPreview.value = false
      activeStep.value = 1
    }, 800)
  }
}

const executeImport = async () => {
  if (!importConfig.default_account_id) {
    ElMessage.warning('请确保选择了默认资金账户')
    return
  }

  loadingImport.value = true
  try {
    const res = await importBill({
      file: selectedFile.value!,
      skip_duplicates: importConfig.skip_duplicates,
      ai_classify: importConfig.ai_classify,
      default_account_id: importConfig.default_account_id
    })
    importResult.value = (res as any)?.data || res
    activeStep.value = 2
  } catch (error) {
    console.warn("导入 API 失败，注入 Mock 数据")
    ElMessage.info('后端服务未启动，当前模拟导入效果，耗时1.5秒')
    setTimeout(() => {
      loadingImport.value = false
      importResult.value = {
        total_count: previewData.value?.summary?.total_records || 142,
        success_count: 140,
        duplicate_count: 2,
        fail_count: 0,
        ai_classified_count: 125
      }
      activeStep.value = 2
      loadHistory()
    }, 1500)
  }
}

const resetImport = () => {
  activeStep.value = 0
  selectedFile.value = null
  previewData.value = null
  importResult.value = null
  importConfig.default_account_id = accounts.value.length > 0 ? accounts.value[0].id : undefined
}

const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await getImportLogs()
    const rawData = (res as any)?.data || res
    if (rawData?.logs) {
      historyLogs.value = rawData.logs
    }
  } catch (error) {
    historyLogs.value = [
      { import_time: new Date().toISOString(), source: '微信账单(近期).csv', success_count: 140, duplicate_count: 2, fail_count: 0 },
      { import_time: '2026-03-01T10:00:00Z', source: 'alipay_record_202602.csv', success_count: 89, duplicate_count: 0, fail_count: 3 }
    ]
  } finally {
    loadingHistory.value = false
  }
}

const downloadTemplate = () => {
  ElMessage.info('操作说明：在微信中点击 我->服务->钱包->账单->常见问题->下载账单。解压后即为所需 CSV 文件')
}

onMounted(() => {
  loadDependencyData()
  loadHistory()
})
</script>

<style scoped>
.import-page {
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

.import-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  min-height: 500px;
}

.import-steps {
  margin: 30px 0 40px;
  padding: 0 40px;
}

.step-content {
  padding: 0 20px 40px;
}

/* 上传区样式 */
.step-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 600px;
  margin: 0 auto;
}

.upload-area {
  width: 100%;
}

.selected-file {
  width: 100%;
  margin-top: 24px;
  padding: 16px 20px;
  background-color: #f9fafb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #e5e7eb;
}

.file-name {
  font-weight: 600;
  color: #111827;
  flex: 1;
}

.file-size {
  color: #6b7280;
  font-size: 13px;
  margin-right: 16px;
}

.btn-next {
  margin-left: auto;
}

/* 预览区样式 */
.preview-header {
  background-color: #f9fafb;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #e5e7eb;
}

.preview-header h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #111827;
}

.summary-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.date-range {
  font-size: 13px;
  color: #6b7280;
}

.preview-table h4 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #374151;
}

.import-settings {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.import-settings h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #111827;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 12px;
}

.setting-hint {
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.4;
  margin-top: 4px;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
}

/* 结果区样式 */
.step-result {
  max-width: 600px;
  margin: 20px auto 0;
}

.error-text {
  color: #EF4444;
  font-weight: 600;
}
.income { color: #16A34A; }
.expense { color: #EF4444; }
.warning { color: #F59E0B; }

/* Material Primary Color overrides */
:deep(.el-button--primary) {
  --el-button-bg-color: #16A34A;
  --el-button-border-color: #16A34A;
  --el-button-hover-bg-color: #15803D;
  --el-button-hover-border-color: #15803D;
}
:deep(.el-step__head.is-success) {
  color: #16A34A;
  border-color: #16A34A;
}
:deep(.el-step__title.is-success) {
  color: #16A34A;
}
:deep(.el-switch.is-checked .el-switch__core) {
  background-color: #16A34A;
  border-color: #16A34A;
}
</style>