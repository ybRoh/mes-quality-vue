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
import { PieChart as EPieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GraphicComponent
} from 'echarts/components'
import { useCharts } from '@/composables/useCharts'

use([CanvasRenderer, EPieChart, TitleComponent, TooltipComponent, LegendComponent, GraphicComponent])

interface DataItem {
  name: string
  value: number
}

interface Props {
  title?: string
  data: DataItem[]
  showLegend?: boolean
  donut?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showLegend: true,
  donut: false
})

const chartRef = ref<InstanceType<typeof VChart> | null>(null)

const { colorPalette } = useCharts()

onBeforeUnmount(() => {
  if (chartRef.value) {
    chartRef.value.dispose()
  }
})

const hasData = computed(() => props.data && props.data.length > 0)

const chartOption = computed(() => ({
  graphic: !hasData.value ? [{
    type: 'text',
    left: 'center',
    top: 'middle',
    style: { text: '데이터 없음', fontSize: 14, fill: '#999' }
  }] : undefined,
  color: colorPalette,
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#E5E5E5',
    textStyle: { color: '#32363A', fontFamily: 'Noto Sans KR' }
  },
  legend: {
    show: props.showLegend,
    orient: 'vertical' as const,
    right: 10,
    top: 'center',
    textStyle: { fontFamily: 'Noto Sans KR', fontSize: 12 }
  },
  series: [
    {
      type: 'pie',
      radius: props.donut ? ['40%', '70%'] : ['0%', '70%'],
      center: props.showLegend ? ['40%', '50%'] : ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontFamily: 'Noto Sans KR',
        fontSize: 11
      },
      labelLine: { show: true },
      data: props.data
    }
  ]
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
