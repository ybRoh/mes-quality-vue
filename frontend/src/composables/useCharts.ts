import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
} from 'echarts/components'

// Register ECharts components
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DataZoomComponent,
  ToolboxComponent
])

export function useCharts() {
  // Chart color palette - keep in sync with --qms-chart-* variables in @/styles/variables.css
  // ECharts requires hex values; CSS variables cannot be used here.
  const colorPalette = [
    '#0A6ED1', // --qms-chart-1  (Fiori Blue)
    '#107E3E', // --qms-chart-2  (Fiori Green)
    '#E9730C', // --qms-chart-3  (Fiori Orange)
    '#BB0000', // --qms-chart-4  (Fiori Red)
    '#1B90FF', // --qms-chart-5  (Light Blue)
    '#61A656', // --qms-chart-6  (Soft Green)
    '#C87B23', // --qms-chart-7  (Amber)
    '#8B47D0', // --qms-chart-8  (Purple)
    '#DB1F77', // --qms-chart-9  (Pink)
    '#0F828F'  // --qms-chart-10 (Teal)
  ]

  const baseTheme = {
    fontFamily: 'Noto Sans KR, sans-serif',
    backgroundColor: 'transparent',
    textStyle: {
      fontFamily: 'Noto Sans KR, sans-serif',
      color: '#32363A' // --qms-text-primary
    },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E5E5E5', // --qms-border
      textStyle: {
        color: '#32363A', // --qms-text-primary
        fontFamily: 'Noto Sans KR'
      }
    },
    grid: {
      top: 20,
      right: 20,
      bottom: 30,
      left: 50,
      containLabel: true
    }
  }

  function formatNumber(value: number): string {
    if (Math.abs(value) >= 1e6) {
      return (value / 1e6).toFixed(1) + 'M'
    }
    if (Math.abs(value) >= 1e3) {
      return (value / 1e3).toFixed(1) + 'K'
    }
    return value.toLocaleString('ko-KR')
  }

  function formatPercent(value: number): string {
    return value.toFixed(1) + '%'
  }

  return {
    colorPalette,
    baseTheme,
    formatNumber,
    formatPercent
  }
}
