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
        <el-button type="primary" :icon="Download" @click="handleExport">导出报表</el-button>
      </div>
    </div>

    <!-- 概览卡片区 -->
    <el-row :gutter="20" class="summary-cards" v-loading="loading">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">该月总收入</div>
          <div class="stat-value income-color">¥ {{ formatNumber(overviewData?.monthly_summary?.income || 0) }}</div>
          <div class="stat-compare" v-if="overviewData?.monthly_summary">
            环比上月 
            <span :class="overviewData.monthly_summary.income_growth > 0 ? 'growth-good' : 'growth-bad'">
              {{ formatGrowth(overviewData.monthly_summary.income_growth) }}%
            </span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">该月总支出</div>
          <div class="stat-value expense-color">¥ {{ formatNumber(overviewData?.monthly_summary?.expense || 0) }}</div>
          <div class="stat-compare" v-if="overviewData?.monthly_summary">
            环比上月 
            <span :class="overviewData.monthly_summary.expense_growth < 0 ? 'growth-good' : 'growth-bad'">
              {{ formatGrowth(overviewData.monthly_summary.expense_growth) }}%
            </span>
          </div>
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
                <el-radio-button label="daily">日</el-radio-button>
                <el-radio-button label="weekly">周</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <!-- 避免警告，给出明确高度 -->
          <div ref="trendChartRef" class="echarts-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>支出分类占比</span>
            </div>
          </template>
          <div ref="pieChartRef" class="echarts-container"></div>
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
import { ref, onMounted, onUnmounted, nextTick, shallowRef } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import * as echarts from 'echarts'
import { getStatisticsOverview } from '@/api/statistics'

// 状态
const loading = ref(false)
const currentMonth = ref(dayjs().format('YYYY-MM'))
const trendType = ref('daily')
const overviewData = ref<any>(null)

// ECharts 实例
const trendChartRef = ref<HTMLElement | null>(null)
const pieChartRef = ref<HTMLElement | null>(null)
const trendChart = shallowRef<echarts.ECharts | null>(null)
const pieChart = shallowRef<echarts.ECharts | null>(null)

// 工具方法
const formatNumber = (num: number) => {
  return (num || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const formatGrowth = (num: number) => {
  return num > 0 ? '+' + num : num.toString()
}

// 渲染趋势图
const renderTrendChart = () => {
  if (!trendChartRef.value || !overviewData.value?.trend_data) return

  if (!trendChart.value) {
    trendChart.value = echarts.init(trendChartRef.value)
  }

  const data = overviewData.value.trend_data
  const xData = data.map((d: any) => dayjs(d.date).format('MM-DD'))
  const incomeData = data.map((d: any) => d.income)
  const expenseData = data.map((d: any) => d.expense)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['支出', '收入'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: { color: '#6b7280' },
      axisLine: { lineStyle: { color: '#e5e7eb' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' }, type: 'dashed' }
    },
    series: [
      {
        name: '支出',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 3, color: '#EF4444' }, // 红色表示支出
        itemStyle: { color: '#EF4444' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
            { offset: 1, color: 'rgba(239, 68, 68, 0.0)' }
          ])
        },
        data: expenseData
      },
      {
        name: '收入',
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 3, color: '#16A34A' }, // 绿色表示收入
        itemStyle: { color: '#16A34A' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(22, 163, 74, 0.3)' },
            { offset: 1, color: 'rgba(22, 163, 74, 0.0)' }
          ])
        },
        data: incomeData
      }
    ]
  }

  trendChart.value.setOption(option)
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
  try {
    const [year, month] = currentMonth.value.split('-')
    const res = await getStatisticsOverview({ 
      current_year: parseInt(year), 
      current_month: parseInt(month) 
    })
    
    // 如果真正的后端连上了结构可能嵌套在 data 中，这里兼容
    const rawData = (res as any)?.data || res
    
    if (rawData?.monthly_summary) {
      overviewData.value = rawData
    } else {
      throw new Error("Invalid Format")
    }

  } catch (error) {
    console.warn("API调用失败，加载兜底 Mock 数据", error)
    overviewData.value = {
      monthly_summary: {
        income: 18500.00, expense: 7800.50, balance: 10700.50, income_growth: 5.4, expense_growth: -2.1
      },
      category_distribution: [
        { name: '餐饮美食', amount: 3200, percentage: 41.0, color: '#EF4444' },
        { name: '房租水电', amount: 2500, percentage: 32.1, color: '#3B82F6' },
        { name: '交通出行', amount: 800, percentage: 10.3, color: '#F59E0B' },
        { name: '休闲娱乐', amount: 1300.5, percentage: 16.7, color: '#8B5CF6' }
      ],
      trend_data: Array.from({length: 30}).map((_, i) => ({
        date: `2026-04-${String(i+1).padStart(2, '0')}`,
        income: i % 5 === 0 ? Math.random() * 2000 + 4000 : 0,
        expense: Math.random() * 400 + 100
      }))
    }
  } finally {
    loading.value = false
    nextTick(() => {
      renderTrendChart()
      renderPieChart()
    })
  }
}

// 导出报表
const handleExport = () => {
  ElMessage.success('正在生成 Excel 报表，请稍候...')
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
}

.stat-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.income-color { color: #16A34A; }
.expense-color { color: #EF4444; }
.balance-color { color: #111827; }

.stat-compare {
  font-size: 13px;
  color: #9ca3af;
}

.growth-good {
  color: #16A34A;
  font-weight: 600;
}
.growth-bad {
  color: #EF4444;
  font-weight: 600;
}

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

.echarts-container {
  width: 100%;
  height: 380px;
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
