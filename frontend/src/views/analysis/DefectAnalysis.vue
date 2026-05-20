<template>
  <div class="page-container">
    <PageHeader title="불량유형별 분석" subtitle="MES 불량 유형별 점유율, 제품별 불량, 추이 분석" />

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 유형별 점유율 (파레토) -->
      <el-tab-pane label="유형별 점유율" name="byType">
        <div class="filter-bar">
          <DateRangePicker v-model="dateRange" />
        </div>

        <div class="chart-row">
          <ParetoChart
            title="불량유형별 파레토 분석"
            :categories="paretoChart.categories"
            :values="paretoChart.values"
          />
          <PieChart
            title="불량유형별 점유율"
            :data="paretoChart.pieData"
            donut
          />
        </div>

        <div class="card">
          <DataTable :data="byTypeData" :columns="byTypeColumns" :show-export="true" />
        </div>
      </el-tab-pane>

      <!-- Tab 2: 제품별 불량 -->
      <el-tab-pane label="제품별 불량" name="byProduct">
        <div class="filter-bar">
          <DateRangePicker v-model="prodDateRange" />
        </div>

        <BarChart
          title="제품별 불량 수량"
          :x-data="prodChart.categories"
          :series="prodChart.series"
          y-axis-name="수량 (EA)"
          stack
        />

        <div class="card" style="margin-top: 16px;">
          <DataTable :data="byProductData" :columns="byProductColumns" :show-export="true" />
        </div>
      </el-tab-pane>

      <!-- Tab 3: 추이 분석 -->
      <el-tab-pane label="추이 분석" name="trend">
        <div class="filter-bar">
          <DateRangePicker v-model="trendDateRange" />
        </div>

        <LineChart
          title="불량유형별 월별 추이"
          :x-data="trendChart.months"
          :series="trendChart.series"
          y-axis-name="수량 (EA)"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import DateRangePicker from '@/components/common/DateRangePicker.vue'
import DataTable from '@/components/common/DataTable.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'
import ParetoChart from '@/components/charts/ParetoChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import { analysisApi } from '@/api/analysis'
import dayjs from 'dayjs'

const activeTab = ref('byType')
const dateRange = ref<[string, string]>([dayjs().subtract(30, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')])
const prodDateRange = ref<[string, string]>([...dateRange.value] as [string, string])
const trendDateRange = ref<[string, string]>([dayjs().subtract(6, 'month').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')])

// Tab 1: 유형별 점유율
const byTypeData = ref<any[]>([])
const paretoChart = ref<{
  categories: string[]
  values: number[]
  pieData: { name: string; value: number }[]
}>({ categories: [], values: [], pieData: [] })

const byTypeColumns: TableColumn[] = [
  { prop: 'ng_type_name', label: '불량유형', width: 120 },
  { prop: 'ng_type', label: '코드', width: 120 },
  { prop: 'total_qty', label: '불량수량', width: 100, sortable: true, align: 'right' },
  { prop: 'occurrence', label: '발생건수', width: 100, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' },
  { prop: 'cumulative_pct', label: '누적(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// Tab 2: 제품별 불량
const byProductData = ref<any[]>([])
const prodChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })

const byProductColumns: TableColumn[] = [
  { prop: 'product_name', label: '제품명', width: 150 },
  { prop: 'total_ng', label: '총 불량', width: 100, sortable: true, align: 'right' },
  { prop: 'top_type', label: '최다 불량유형', width: 120 },
  { prop: 'top_type_qty', label: '최다 수량', width: 100, align: 'right' },
  { prop: 'type_count', label: '불량유형수', width: 100, align: 'center' }
]

// Tab 3: 추이
const trendChart = ref<{ months: string[]; series: { name: string; data: number[] }[] }>({ months: [], series: [] })

// 탭 전환 시 자동 로드
watch(activeTab, (tab) => {
  if (tab === 'byType') loadByTypeData()
  else if (tab === 'byProduct') loadByProductData()
  else if (tab === 'trend') loadTrendData()
})

// 날짜 변경 시 자동 로드
watch(dateRange, () => { if (activeTab.value === 'byType') loadByTypeData() }, { deep: true })
watch(prodDateRange, () => { if (activeTab.value === 'byProduct') loadByProductData() }, { deep: true })
watch(trendDateRange, () => { if (activeTab.value === 'trend') loadTrendData() }, { deep: true })

onMounted(() => {
  loadByTypeData()
})

async function loadByTypeData() {
  try {
    const res = await analysisApi.getDefectByType({ from: dateRange.value[0], to: dateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    byTypeData.value = items
    paretoChart.value = {
      categories: items.map((r: any) => r.ng_type_name),
      values: items.map((r: any) => r.total_qty),
      pieData: items.map((r: any) => ({ name: r.ng_type_name, value: r.total_qty }))
    }
  } catch (e) {
    console.warn('불량유형별 조회 실패:', e)
    ElMessage.error('불량유형별 데이터를 불러오는데 실패했습니다')
    byTypeData.value = []
    paretoChart.value = { categories: [], values: [], pieData: [] }
  }
}

async function loadByProductData() {
  try {
    const res = await analysisApi.getDefectByProduct({ from: prodDateRange.value[0], to: prodDateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []

    // 테이블 데이터 변환
    byProductData.value = items.map((r: any) => {
      const topType = r.types && r.types.length > 0 ? r.types[0] : null
      return {
        product_id: r.product_id,
        product_name: r.product_name,
        total_ng: r.total_ng,
        top_type: topType ? topType.ng_type_name : '-',
        top_type_qty: topType ? topType.ng_qty : 0,
        type_count: r.types ? r.types.length : 0
      }
    })

    // 스택 차트: 제품별로 주요 불량유형 top5
    const allTypes = new Set<string>()
    items.forEach((r: any) => {
      (r.types || []).forEach((t: any) => allTypes.add(t.ng_type_name))
    })
    const typeList = Array.from(allTypes).slice(0, 8)
    const categories = items.map((r: any) => r.product_name)

    prodChart.value = {
      categories,
      series: typeList.map(typeName => ({
        name: typeName,
        data: items.map((r: any) => {
          const found = (r.types || []).find((t: any) => t.ng_type_name === typeName)
          return found ? found.ng_qty : 0
        })
      }))
    }
  } catch (e) {
    console.warn('제품별 불량 조회 실패:', e)
    ElMessage.error('제품별 불량 데이터를 불러오는데 실패했습니다')
    byProductData.value = []
    prodChart.value = { categories: [], series: [] }
  }
}

async function loadTrendData() {
  try {
    const res = await analysisApi.getDefectTrend({ from: trendDateRange.value[0], to: trendDateRange.value[1] })
    const data = res.data
    trendChart.value = {
      months: data.months || [],
      series: (data.series || []).map((s: any) => ({
        name: s.ng_type_name,
        data: s.data
      }))
    }
  } catch (e) {
    console.warn('불량 추이 조회 실패:', e)
    ElMessage.error('불량 추이 데이터를 불러오는데 실패했습니다')
    trendChart.value = { months: [], series: [] }
  }
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.chart-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}
.chart-row > * {
  flex: 1 1 400px;
  min-width: 0;
}
</style>
