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
import { BarChart as EBarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  GraphicComponent
} from 'echarts/components'
import { useCharts } from '@/composables/useCharts'

use([CanvasRenderer, EBarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, GraphicComponent])

interface SeriesItem {
  name: string
  data: number[]
  color?: string
}

interface Props {
  title?: string
  xData: string[]
  series: SeriesItem[]
  horizontal?: boolean
  stack?: boolean
  yAxisName?: string
  showLegend?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  horizontal: false,
  stack: false,
  showLegend: true
})

const chartRef = ref<InstanceType<typeof VChart> | null>(null)

const { colorPalette } = useCharts()

onBeforeUnmount(() => {
  if (chartRef.value) {
    chartRef.value.dispose()
  }
})

const hasData = computed(() => props.xData && props.xData.length > 0 && props.series && props.series.length > 0)

const chartOption = computed(() => {
  const categoryAxis = {
    type: 'category' as const,
    data: props.xData,
    axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11, interval: 0, rotate: props.xData.length > 8 ? 30 : 0 },
    axisTick: { alignWithLabel: true }
  }

  const valueAxis = {
    type: 'value' as const,
    name: props.yAxisName || '',
    nameTextStyle: { fontFamily: 'Noto Sans KR', fontSize: 11 },
    axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11 },
    splitLine: { lineStyle: { type: 'dashed' as const, color: '#E5E5E5' } }
  }

  return {
    graphic: !hasData.value ? [{
      type: 'text',
      left: 'center',
      top: 'middle',
      style: { text: '데이터 없음', fontSize: 14, fill: '#999' }
    }] : undefined,
    color: colorPalette,
    tooltip: {
      trigger: 'axis' as const,
      axisPointer: { type: 'shadow' as const },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E5E5E5',
      textStyle: { color: '#32363A', fontFamily: 'Noto Sans KR' }
    },
    legend: {
      show: props.showLegend && props.series.length > 1,
      bottom: 0,
      textStyle: { fontFamily: 'Noto Sans KR' }
    },
    grid: {
      top: 20,
      right: 20,
      bottom: props.showLegend && props.series.length > 1 ? 40 : 20,
      left: 50,
      containLabel: true
    },
    xAxis: props.horizontal ? valueAxis : categoryAxis,
    yAxis: props.horizontal ? categoryAxis : valueAxis,
    series: props.series.map((s, idx) => ({
      name: s.name,
      type: 'bar' as const,
      data: s.data,
      stack: props.stack ? 'total' : undefined,
      barMaxWidth: 40,
      itemStyle: {
        color: s.color || colorPalette[idx % colorPalette.length],
        borderRadius: props.stack ? 0 : [4, 4, 0, 0]
      }
    }))
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
  height: 320px;
}
</style>
