<template>
  <div class="statistics-page">
    <div class="page-header">
      <h1 class="page-title">统计分析</h1>
      <div class="header-actions">
        <el-date-picker
          v-model="currentMonth"
          type="month"
          value-format="YYYY-MM"
          placeholder="选择月份"
          @change="fetchData"
          style="width: 140px; margin-right: 12px"
        />
        <el-button type="primary" :icon="Download" :loading="exporting" @click="handleExport">导出报表</el-button>
      </div>
    </div>

    <!-- 概览卡片区 -->
    <el-row :gutter="20" class="summary-cards" v-loading="loading">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">该月总收入</div>
          <div class="stat-value income-color">¥ {{ formatNumber(overviewData?.monthly_summary?.income || 0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">该月总支出</div>
          <div class="stat-value expense-color">¥ {{ formatNumber(overviewData?.monthly_summary?.expense || 0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">该月结余</div>
          <div class="stat-value balance-color">¥ {{ formatNumber(overviewData?.monthly_summary?.balance || 0) }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" class="charts-section" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>收支趋势</span>
              <el-radio-group v-model="trendType" size="small" @change="renderTrendChart">
                <el-radio-button value="daily">{{ isCurrentMonth ? '本月' : currentMonthLabel }}</el-radio-button>
                <el-radio-button v-if="isCurrentMonth" value="weekly">本周</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <!-- 避免警告，给出明确高度 -->
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>支出分类占比</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 排行区 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover" class="rank-card">
          <template #header>
            <div class="card-header">
              <span>分类支出排行</span>
            </div>
          </template>
          <el-table :data="overviewData?.category_distribution || []" style="width: 100%" stripe>
            <el-table-column type="index" label="排名" width="80" align="center" />
            <el-table-column prop="name" label="分类名称" />
            <el-table-column label="占比" width="250">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.percentage" 
                  :color="row.color || '#16A34A'" 
                  :stroke-width="10" 
                  :show-text="false" 
                />
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="百分比" width="100" align="right">
              <template #default="{ row }">
                {{ row.percentage }}%
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="150" align="right">
              <template #default="{ row }">
                <span class="expense-color">¥ {{ formatNumber(row.amount) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, shallowRef } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import * as echarts from 'echarts'
import { getStatisticsOverview, exportExcel } from '@/api/statistics'
import type { StatisticsOverview, ExportRequest } from '@/types/statistics'

// 状态
const loading = ref(false)
const currentMonth = ref(dayjs().format('YYYY-MM'))
const trendType = ref('daily')
const overviewData = ref<any>(null)
/** 当前选择的月份是否为系统本月 */
const isCurrentMonth = computed(() => currentMonth.value === dayjs().format('YYYY-MM'))
/** 历史月份时显示的标签，如"12月" */
const currentMonthLabel = computed(() => dayjs(currentMonth.value).format('M月'))

// ECharts 实例
const trendChartRef = ref<HTMLElement | null>(null)
const pieChartRef = ref<HTMLElement | null>(null)
const trendChart = shallowRef<echarts.ECharts | null>(null)
const pieChart = shallowRef<echarts.ECharts | null>(null)

// 工具方法
const formatNumber = (num: number) => {
  return (num || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 渲染趋势图
const renderTrendChart = () => {
  if (!trendChartRef.value || !overviewData.value?.trend_data) return

  if (!trendChart.value) {
    trendChart.value = echarts.init(trendChartRef.value)
  }

  const allData: any[] = overviewData.value.trend_data

  // "本周"：过滤当前自然周（周一~周日）的每日数据，与仪表盘逻辑一致
  const slice = (() => {
    if (trendType.value !== 'weekly') return allData
    const today = dayjs()
    const dow = today.day()
    const weekStart = today.subtract(dow === 0 ? 6 : dow - 1, 'day').startOf('day')
    const weekEnd   = weekStart.add(6, 'day').endOf('day')
    return allData.filter((d: any) => {
      const date = dayjs(d.date)
      return !date.isBefore(weekStart) && !date.isAfter(weekEnd)
    })
  })()

  const xData       = slice.map((d: any) => dayjs(d.date).format('MM-DD'))
  const incomeData  = slice.map((d: any) => d.income  ?? 0)
  const expenseData = slice.map((d: any) => d.expense ?? 0)

  // 与仪表盘「近期收支趋势」相同的折线面积图配置（DashboardView.updateTrendChart）
  trendChart.value.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    legend: { data: ['支出', '收入'], top: 0 },
    xAxis: { type: 'category', boundaryGap: false, data: xData },
    yAxis: { type: 'value' },
    series: [
      {
        name: '支出',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.1 },
        data: expenseData,
        itemStyle: { color: '#f56c6c' },
      },
      {
        name: '收入',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.1 },
        data: incomeData,
        itemStyle: { color: '#16A34A' },
      },
    ],
  })
}

// 渲染分类环形图
const renderPieChart = () => {
  if (!pieChartRef.value || !overviewData.value?.category_distribution) return

  if (!pieChart.value) {
    pieChart.value = echarts.init(pieChartRef.value)
  }

  const rawDistribution = overviewData.value.category_distribution || []
  // 为没有颜色的类型补充默认颜色
  const fallbackColors = ['#Ef4444', '#F59E0B', '#10B981', '#06B6D4', '#6366F1', '#8B5CF6', '#EC4899']
  const data = rawDistribution.map((d: any, idx: number) => ({
    name: d.name,
    value: d.amount,
    itemStyle: { color: d.color || fallbackColors[idx % fallbackColors.length] }
  }))

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      bottom: '0%',
      left: 'center',
      itemWidth: 10,
      itemHeight: 10,
      textStyle: { color: '#4b5563' }
    },
    series: [
      {
        name: '支出分类',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '40%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            formatter: '{b}\n{d}%'
          }
        },
        labelLine: { show: false },
        data: data
      }
    ]
  }

  pieChart.value.setOption(option)
}

// 加载数据
const fetchData = async () => {
  loading.value = true
  // 历史月份不存在"本周"视图，重置为日视图
  if (!isCurrentMonth.value && trendType.value === 'weekly') {
    trendType.value = 'daily'
  }
  try {
    const [year, month] = currentMonth.value.split('-')
    const res = await getStatisticsOverview({
      current_year: parseInt(year),
      current_month: parseInt(month)
    }) as unknown as StatisticsOverview

    overviewData.value = res ?? null
  } catch {
    overviewData.value = null
  } finally {
    loading.value = false
    nextTick(() => {
      // 销毁旧实例重新初始化，确保历史数据能正确渲染
      if (trendChart.value) {
        trendChart.value.dispose()
        trendChart.value = null
      }
      if (pieChart.value) {
        pieChart.value.dispose()
        pieChart.value = null
      }
      renderTrendChart()
      renderPieChart()
    })
  }
}

// 导出报表
const exporting = ref(false)
const handleExport = async () => {
  if (exporting.value) return
  exporting.value = true
  try {
    const [year, month] = currentMonth.value.split('-').map(Number)
    const startDate = dayjs(`${year}-${String(month).padStart(2, '0')}-01`).format('YYYY-MM-DD')
    const endDate = dayjs(startDate).endOf('month').format('YYYY-MM-DD')
    const params: ExportRequest = { start_date: startDate, end_date: endDate }
    const res = await exportExcel(params) as any
    const msg = res?.message || '导出任务已提交，请稍后在下载中心查看'
    ElMessage.success(msg)
  } catch {
    // 错误已由请求拦截器统一提示
  } finally {
    exporting.value = false
  }
}

// 监听窗口大小变化以重新渲染图表
const handleResize = () => {
  trendChart.value?.resize()
  pieChart.value?.resize()
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart.value?.dispose()
  pieChart.value?.dispose()
})
</script>

<style scoped>
.statistics-page {
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

.header-actions {
  display: flex;
  align-items: center;
}

.stat-card {
  border-radius: 12px;
  text-align: center;
  padding: 10px 0;
  border: 1px solid #e5e7eb;
  height: 130px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

/* 覆盖 Element Plus 内部 body，保持内容居中 */
:deep(.stat-card .el-card__body) {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 16px 20px;
}

.stat-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 0;
  letter-spacing: -0.5px;
}

.income-color { color: #16A34A; }
.expense-color { color: #EF4444; }
.balance-color { color: #111827; }

.chart-card {
  border-radius: 12px;
  height: 480px;
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
}

.rank-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #111827;
  font-size: 16px;
}

/* Material overrides for Primary color (#16A34A) */
:deep(.el-button--primary) {
  --el-button-bg-color: #16A34A;
  --el-button-border-color: #16A34A;
  --el-button-hover-bg-color: #15803D;
  --el-button-hover-border-color: #15803D;
}
:deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner) {
  background-color: #16A34A;
  border-color: #16A34A;
  box-shadow: -1px 0 0 0 #16A34A;
}
</style>
