<template>
  <div class="chart-card">
    <div v-if="title" class="chart-title">{{ title }}</div>
    <v-chart ref="chartRef" :option="chartOption" :autoresize="true" class="chart-container" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onBeforeUnmount } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([CanvasRenderer, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface Props {
  categories: string[]
  values: number[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: ''
})

const chartRef = ref<InstanceType<typeof VChart> | null>(null)

onBeforeUnmount(() => {
  if (chartRef.value) {
    chartRef.value.dispose()
  }
})

const chartOption = computed(() => {
  const total = props.values.reduce((sum, v) => sum + v, 0)
  const cumulative: number[] = []
  let running = 0
  props.values.forEach(v => {
    running += v
    cumulative.push(total > 0 ? Math.round((running / total) * 1000) / 10 : 0)
  })

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E5E5E5',
      textStyle: { color: '#32363A', fontFamily: 'Noto Sans KR' }
    },
    legend: {
      data: ['빈도', '누적 %'],
      bottom: 0,
      textStyle: { fontFamily: 'Noto Sans KR' }
    },
    grid: {
      top: 20,
      right: 60,
      bottom: 50,
      left: 50,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: props.categories,
      axisLabel: {
        fontFamily: 'Noto Sans KR',
        fontSize: 11,
        interval: 0,
        rotate: props.categories.length > 6 ? 30 : 0
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '빈도',
        nameTextStyle: { fontFamily: 'Noto Sans KR', fontSize: 11 },
        axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11 },
        splitLine: { lineStyle: { type: 'dashed', color: '#E5E5E5' } }
      },
      {
        type: 'value',
        name: '누적 %',
        nameTextStyle: { fontFamily: 'Noto Sans KR', fontSize: 11 },
        axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11, formatter: '{value}%' },
        min: 0,
        max: 100,
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '빈도',
        type: 'bar',
        data: props.values,
        barMaxWidth: 40,
        itemStyle: {
          color: '#0A6ED1',
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '누적 %',
        type: 'line',
        yAxisIndex: 1,
        data: cumulative,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#E9730C', width: 2 },
        itemStyle: { color: '#E9730C' }
      }
    ]
  }
})
</script>

<style scoped>
.chart-card {
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  padding: 16px;
}

.chart-title {
  font-size: 15px;
  font-weight: 500;
  color: #32363A;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #E5E5E5;
}

.chart-container {
  width: 100%;
  height: 350px;
}
</style>
