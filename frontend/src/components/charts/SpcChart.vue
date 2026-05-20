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
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  MarkLineComponent,
  MarkPointComponent,
  GraphicComponent
} from 'echarts/components'

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, MarkLineComponent, MarkPointComponent, GraphicComponent])

interface Props {
  values: number[]
  mean: number
  ucl: number
  lcl: number
  usl?: number
  lsl?: number
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  values: () => [],
  title: ''
})

const chartRef = ref<InstanceType<typeof VChart> | null>(null)

onBeforeUnmount(() => {
  if (chartRef.value) {
    chartRef.value.dispose()
  }
})

const hasData = computed(() => props.values && props.values.length > 0)

const chartOption = computed(() => {
  const xLabels = props.values.map((_, i) => String(i + 1))
  const oocIndices: number[] = []

  props.values.forEach((v, i) => {
    if (v > props.ucl || v < props.lcl) {
      oocIndices.push(i)
    }
  })

  const markLineData: any[] = [
    {
      yAxis: props.mean,
      name: 'CL',
      lineStyle: { color: '#0A6ED1', width: 2, type: 'solid' },
      label: { formatter: 'CL={c}', position: 'insideEndTop', fontFamily: 'Noto Sans KR', fontSize: 11 }
    },
    {
      yAxis: props.ucl,
      name: 'UCL',
      lineStyle: { color: '#E9730C', width: 2, type: 'dashed' },
      label: { formatter: 'UCL={c}', position: 'insideEndTop', fontFamily: 'Noto Sans KR', fontSize: 11 }
    },
    {
      yAxis: props.lcl,
      name: 'LCL',
      lineStyle: { color: '#E9730C', width: 2, type: 'dashed' },
      label: { formatter: 'LCL={c}', position: 'insideEndBottom', fontFamily: 'Noto Sans KR', fontSize: 11 }
    }
  ]

  if (props.usl !== undefined) {
    markLineData.push({
      yAxis: props.usl,
      name: 'USL',
      lineStyle: { color: '#BB0000', width: 2, type: 'solid' },
      label: { formatter: 'USL={c}', position: 'insideEndTop', fontFamily: 'Noto Sans KR', fontSize: 11, color: '#BB0000' }
    })
  }

  if (props.lsl !== undefined) {
    markLineData.push({
      yAxis: props.lsl,
      name: 'LSL',
      lineStyle: { color: '#BB0000', width: 2, type: 'solid' },
      label: { formatter: 'LSL={c}', position: 'insideEndBottom', fontFamily: 'Noto Sans KR', fontSize: 11, color: '#BB0000' }
    })
  }

  return {
    graphic: !hasData.value ? [{
      type: 'text',
      left: 'center',
      top: 'middle',
      style: { text: '데이터 없음', fontSize: 14, fill: '#999' }
    }] : undefined,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E5E5E5',
      textStyle: { color: '#32363A', fontFamily: 'Noto Sans KR' },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        const idx = p.dataIndex
        const isOoc = oocIndices.includes(idx)
        return `<div style="font-family: Noto Sans KR">
          <strong>샘플 #${idx + 1}</strong><br/>
          측정값: ${p.value}${isOoc ? '<br/><span style="color:#BB0000;font-weight:bold">관리이탈!</span>' : ''}
        </div>`
      }
    },
    grid: {
      top: 20,
      right: 80,
      bottom: 30,
      left: 60
    },
    xAxis: {
      type: 'category',
      data: xLabels,
      name: '샘플',
      nameTextStyle: { fontFamily: 'Noto Sans KR', fontSize: 11 },
      axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      name: '측정값',
      nameTextStyle: { fontFamily: 'Noto Sans KR', fontSize: 11 },
      axisLabel: { fontFamily: 'Noto Sans KR', fontSize: 11 },
      splitLine: { lineStyle: { type: 'dashed', color: '#E5E5E5' } }
    },
    series: [
      {
        type: 'line',
        data: props.values,
        symbol: 'circle',
        symbolSize: (value: number, params: any) => {
          return oocIndices.includes(params.dataIndex) ? 10 : 6
        },
        itemStyle: {
          color: (params: any) => {
            return oocIndices.includes(params.dataIndex) ? '#BB0000' : '#0A6ED1'
          }
        },
        lineStyle: { color: '#0A6ED1', width: 1.5 },
        markLine: {
          silent: true,
          symbol: 'none',
          data: markLineData
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
  height: 350px;
}
</style>
