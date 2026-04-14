<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h2>财务仪表盘</h2>
      <div class="actions">
        <el-date-picker
          v-model="currentDate"
          type="month"
          placeholder="选择月份"
          size="default"
          :clearable="false"
        />
      </div>
    </div>

    <!-- 概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card income-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">本月收入</div>
              <div class="value">¥ {{ Number(statistics.income || 0).toFixed(2) }}</div>
              <div class="trend positive">
                <el-icon><CaretTop /></el-icon> 12% 较上月
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card expense-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">本月支出</div>
              <div class="value">¥ {{ Number(statistics.expense || 0).toFixed(2) }}</div>
              <div class="trend negative">
                <el-icon><CaretBottom /></el-icon> 5% 较上月
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card balance-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Histogram /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">本月结余</div>
              <div class="value" :class="{ 'negative-val': statistics.balance < 0 }">
                ¥ {{ Number(statistics.balance || 0).toFixed(2) }}
              </div>
              <div class="trend normal">
                结余率 {{ ((Number(statistics.balance || 0) / Number(statistics.income || 1)) * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card asset-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><House /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">总资产</div>
              <div class="value">¥ {{ Number(statistics.totalAssets || 0).toFixed(2) }}</div>
              <div class="trend normal">
                包含所有账户
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="16" :xs="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>近期收支趋势</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
      <el-col :span="8" :xs="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>支出分类占比</span>
            </div>
          </template>
          <div class="chart-container" ref="pieChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
     <el-card shadow="hover" class="quick-actions">
      <template #header>
        <div class="card-header">
          <span>常用功能</span>
        </div>
      </template>
      <div class="action-buttons">
         <el-button type="primary" size="large" :icon="Edit" @click="$router.push('/add')">记一笔</el-button>
         <el-button size="large" :icon="DataLine" @click="$router.push('/statistics')">查看报表</el-button>
         <el-button size="large" :icon="Calendar" @click="$router.push('/budget')">预算设置</el-button>
         <el-button size="large" :icon="Upload" @click="$router.push('/import')">导入账单</el-button>
      </div>
    </el-card>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { Wallet, Money, Histogram, House, CaretTop, CaretBottom, Edit, DataLine, Calendar, Upload } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const currentDate = ref(new Date())
const trendPeriod = ref('week')

const statistics = reactive({
  income: 8500.00,
  expense: 3240.50,
  balance: 5259.50,
  totalAssets: 156000.00
})

const trendChartRef = ref<HTMLElement | null>(null)
const pieChartRef = ref<HTMLElement | null>(null)

let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '支出',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.1 },
          data: [120, 132, 101, 134, 90, 230, 210],
          itemStyle: { color: '#f56c6c' }
        },
        {
          name: '收入',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.1 },
          data: [220, 182, 191, 234, 290, 330, 310],
          itemStyle: { color: '#67c23a' }
        }
      ]
    })
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '0%', left: 'center' },
      series: [
        {
          name: '支出分类',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false, position: 'center' },
          emphasis: {
            label: { show: true, fontSize: 16, fontWeight: 'bold' }
          },
          labelLine: { show: false },
          data: [
            { value: 1048, name: '餐饮' },
            { value: 735, name: '购物' },
            { value: 580, name: '交通' },
            { value: 484, name: '娱乐' },
            { value: 300, name: '其他' }
          ]
        }
      ]
    })
  }
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.data-card {
  height: 140px; 
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

:deep(.el-card__body) {
  padding: 20px;
  height: 100%;
  box-sizing: border-box;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 28px;
  flex-shrink: 0;
}

.income-card .card-icon { background-color: #f0f9eb; color: #67c23a; }
.expense-card .card-icon { background-color: #fef0f0; color: #f56c6c; }
.balance-card .card-icon { background-color: #e9e9eb; color: #909399; }
.asset-card .card-icon { background-color: #ecf5ff; color: #409eff; }

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.2;
}

.negative-val {
  color: #f56c6c;
}

.trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.trend.positive { color: #67c23a; }
.trend.negative { color: #f56c6c; }
.trend.normal { color: #909399; }

.charts-row {
  margin-top: 10px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.quick-actions .action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}
</style>