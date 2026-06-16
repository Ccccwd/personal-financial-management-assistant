<template>
  <div class="budget-chart-wrapper">
    <div ref="chartRef" class="chart-container" :style="{ height: chartHeight }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { AIAdviceBudgetBreakdownItem } from '@/types/ai'

const props = defineProps<{
  breakdown: AIAdviceBudgetBreakdownItem[]
  total: number
}>()

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const chartHeight = computed(() => `${Math.max(props.breakdown.length * 50, 200)}px`)

const colors = ['#16A34A', '#10B981', '#34D399', '#6EE7B7', '#A7F3D0', '#059669', '#047857']

const renderChart = () => {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const categories = props.breakdown.map(b => b.category)
  const amounts = props.breakdown.map(b => b.suggested_amount)

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        const pct = props.total > 0 ? ((item.value / props.total) * 100).toFixed(1) : '0'
        return `${item.name}<br/>¥${item.value.toFixed(0)} (${pct}%)`
      }
    },
    grid: { left: '3%', right: '12%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', axisLabel: { formatter: '¥{value}' } },
    yAxis: { type: 'category', data: categories, inverse: true },
    series: [{
      type: 'bar',
      data: amounts.map((v, i) => ({
        value: v,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: colors[i % colors.length] },
            { offset: 1, color: colors[(i + 1) % colors.length] + '88' },
          ]),
          borderRadius: [0, 6, 6, 0],
        }
      })),
      barWidth: 24,
      label: {
        show: true,
        position: 'right',
        formatter: '¥{c}',
        fontSize: 12,
        color: '#6b7280',
      }
    }]
  })
}

const handleResize = () => chart?.resize()

watch(() => props.breakdown, () => nextTick(renderChart), { deep: true })

onMounted(() => {
  nextTick(() => {
    renderChart()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.chart-container {
  width: 100%;
}
</style>
