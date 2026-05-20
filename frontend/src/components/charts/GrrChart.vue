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
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

use([CanvasRenderer, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

interface GrrComponents {
  EV: number   // Equipment Variation (Repeatability)
  AV: number   // Appraiser Variation (Reproducibility)
  PV: number   // Part Variation
  GRR: number  // Total GR&R
}

interface Props {
  components: GrrComponents
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
  const { EV, AV, PV, GRR } = props.components
  const TV = Math.sqrt(GRR * GRR + PV * PV) || 1

  const evPct = Math.round((EV / TV) * 1000) / 10
  const avPct = Math.round((AV / TV) * 1000) / 10
  const pvPct = Math.round((PV / TV) * 1000) / 10
  const grrPct = Math.round((GRR / TV) * 1000) / 10

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E5E5E5',
      textStyle: { color: '#32363A', fontFamily: 'Noto Sans KR' },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        return `<div style="font-family: Noto Sans KR">
          <strong>${p.name}</strong><br/>
          기여율: ${p.value}%
        </div>`
      }
    },
    grid: {
      top: 20,
      right: 30,
      bottom: 30,
      left: 120
    },
    xAxis: {
      type: 'value',
      name: '기여율 (%)',
      nameTextStyle: { fontFamily: 'Noto Sans KR', fontSize: 11 },
      axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11, formatter: '{value}%' },
      max: 100,
      splitLine: { lineStyle: { type: 'dashed', color: '#E5E5E5' } }
    },
    yAxis: {
      type: 'category',
      data: ['반복성 (EV)', '재현성 (AV)', '부품변동 (PV)', 'GR&R'],
      axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 12 }
    },
    series: [
      {
        type: 'bar',
        data: [
          { value: evPct, itemStyle: { color: '#0A6ED1' } },
          { value: avPct, itemStyle: { color: '#107E3E' } },
          { value: pvPct, itemStyle: { color: '#E9730C' } },
          {
            value: grrPct,
            itemStyle: {
              color: grrPct <= 10 ? '#107E3E' : grrPct <= 30 ? '#E9730C' : '#BB0000'
            }
          }
        ],
        barMaxWidth: 30,
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%',
          fontFamily: 'Noto Sans KR',
          fontSize: 12,
          fontWeight: 'bold'
        }
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
  height: 300px;
}
</style>
