<template>
  <div class="chart-card">
    <div v-if="title" class="chart-title">{{ title }}</div>
    <v-chart :option="chartOption" :autoresize="true" class="chart-container" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart as ELineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  GraphicComponent
} from 'echarts/components'
import { useCharts } from '@/composables/useCharts'

use([CanvasRenderer, ELineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, GraphicComponent])

interface SeriesItem {
  name: string
  data: number[]
  color?: string
  areaStyle?: boolean
}

interface Props {
  title?: string
  xData: string[]
  series: SeriesItem[]
  yAxisName?: string
  showLegend?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showLegend: true
})

const { colorPalette } = useCharts()

const hasData = computed(() => props.xData && props.xData.length > 0 && props.series && props.series.length > 0)

const chartOption = computed(() => ({
  graphic: !hasData.value ? [{
    type: 'text',
    left: 'center',
    top: 'middle',
    style: { text: '데이터 없음', fontSize: 14, fill: '#999' }
  }] : undefined,
  color: colorPalette,
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#E5E5E5',
    textStyle: { color: '#32363A', fontFamily: 'Noto Sans KR' }
  },
  legend: {
    show: props.showLegend,
    bottom: 0,
    textStyle: { fontFamily: 'Noto Sans KR' }
  },
  grid: {
    top: 20,
    right: 20,
    bottom: props.showLegend ? 40 : 20,
    left: 50,
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: props.xData,
    axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11 },
    axisTick: { alignWithLabel: true }
  },
  yAxis: {
    type: 'value',
    name: props.yAxisName || '',
    nameTextStyle: { fontFamily: 'Noto Sans KR', fontSize: 11 },
    axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11 },
    splitLine: { lineStyle: { type: 'dashed', color: '#E5E5E5' } }
  },
  series: props.series.map((s, idx) => ({
    name: s.name,
    type: 'line',
    data: s.data,
    smooth: true,
    symbol: 'circle',
    symbolSize: 6,
    lineStyle: { width: 2 },
    itemStyle: { color: s.color || colorPalette[idx % colorPalette.length] },
    areaStyle: s.areaStyle
      ? { opacity: 0.15, color: s.color || colorPalette[idx % colorPalette.length] }
      : undefined
  }))
}))
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
  height: 320px;
}
</style>
