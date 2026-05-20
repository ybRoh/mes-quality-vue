<template>
  <div class="page-container">
    <PageHeader title="유형별 분석" subtitle="제품별, 부품구성, 거래처별, 불량항목별 분석" />

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 제품별 점유율 -->
      <el-tab-pane label="제품별 점유율" name="processType">
        <div class="filter-bar">
          <DateRangePicker v-model="dateRange" />
        </div>

        <div class="chart-row">
          <PieChart title="제품별 점유율" :data="processTypeData" donut />
          <BarChart
            title="제품별 생산량"
            :x-data="processTypeBar.categories"
            :series="processTypeBar.series"
            y-axis-name="수량 (EA)"
          />
        </div>

        <div class="card">
          <DataTable :data="processTypeTable" :columns="processTypeColumns" :show-export="true" />
        </div>
      </el-tab-pane>

      <!-- Tab 2: 부품구성 -->
      <el-tab-pane label="부품구성" name="parts">
        <div class="filter-bar">
          <DateRangePicker v-model="partsDateRange" />
        </div>

        <div class="chart-row">
          <PieChart title="부품구성별 생산 비율" :data="partsData" />
          <BarChart
            title="부품별 생산량 비교"
            :x-data="partsBar.categories"
            :series="partsBar.series"
            y-axis-name="수량 (EA)"
          />
        </div>

        <div class="card">
          <DataTable :data="partsTable" :columns="partsColumns" :show-export="true" />
        </div>
      </el-tab-pane>

      <!-- Tab 3: 거래처별 -->
      <el-tab-pane label="거래처별" name="customer">
        <div class="filter-bar">
          <DateRangePicker v-model="customerDateRange" />
        </div>

        <div class="chart-row">
          <PieChart title="거래처별 점유율" :data="customerData" donut />
          <BarChart
            title="거래처별 생산량"
            :x-data="customerBar.categories"
            :series="customerBar.series"
            horizontal
          />
        </div>

        <div class="card">
          <DataTable :data="customerTable" :columns="customerColumns" :show-export="true" />
        </div>
      </el-tab-pane>

      <!-- Tab 4: 불량항목별 -->
      <el-tab-pane label="불량항목별" name="defect">
        <div class="filter-bar">
          <DateRangePicker v-model="defectDateRange" />
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
          <DataTable :data="defectTable" :columns="defectColumns" :show-export="true" />
        </div>
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
import PieChart from '@/components/charts/PieChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import ParetoChart from '@/components/charts/ParetoChart.vue'
import { analysisApi } from '@/api/analysis'
import dayjs from 'dayjs'

const activeTab = ref('processType')
const dateRange = ref<[string, string]>([dayjs().subtract(30, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')])
const partsDateRange = ref<[string, string]>([...dateRange.value] as [string, string])
const customerDateRange = ref<[string, string]>([...dateRange.value] as [string, string])
const defectDateRange = ref<[string, string]>([...dateRange.value] as [string, string])

// Tab 1
const processTypeData = ref<{ name: string; value: number }[]>([])
const processTypeBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const processTypeTable = ref<any[]>([])
const processTypeColumns: TableColumn[] = [
  { prop: 'product_name', label: '제품명', width: 150 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// Tab 2
const partsData = ref<{ name: string; value: number }[]>([])
const partsBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const partsTable = ref<any[]>([])
const partsColumns: TableColumn[] = [
  { prop: 'product_name', label: '제품명', width: 150 },
  { prop: 'process_type', label: '공정유형', width: 100 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'composition_pct', label: '구성비(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// Tab 3
const customerData = ref<{ name: string; value: number }[]>([])
const customerBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const customerTable = ref<any[]>([])
const customerColumns: TableColumn[] = [
  { prop: 'customer_name', label: '거래처', width: 150 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'good_qty', label: '양품', width: 100, align: 'right' },
  { prop: 'ng_qty', label: '불량', width: 100, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// Tab 4: 불량항목별
const defectTable = ref<any[]>([])
const paretoChart = ref<{
  categories: string[]
  values: number[]
  pieData: { name: string; value: number }[]
}>({ categories: [], values: [], pieData: [] })
const defectColumns: TableColumn[] = [
  { prop: 'ng_type_name', label: '불량유형', width: 120 },
  { prop: 'ng_type', label: '코드', width: 120 },
  { prop: 'total_qty', label: '불량수량', width: 100, sortable: true, align: 'right' },
  { prop: 'occurrence', label: '발생건수', width: 100, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' },
  { prop: 'cumulative_pct', label: '누적(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// 탭 전환 시 자동 로드
watch(activeTab, (tab) => {
  if (tab === 'processType') loadProcessTypeData()
  else if (tab === 'parts') loadPartsData()
  else if (tab === 'customer') loadCustomerData()
  else if (tab === 'defect') loadDefectData()
})

// 날짜 변경 시 자동 로드
watch(dateRange, () => { if (activeTab.value === 'processType') loadProcessTypeData() }, { deep: true })
watch(partsDateRange, () => { if (activeTab.value === 'parts') loadPartsData() }, { deep: true })
watch(customerDateRange, () => { if (activeTab.value === 'customer') loadCustomerData() }, { deep: true })
watch(defectDateRange, () => { if (activeTab.value === 'defect') loadDefectData() }, { deep: true })

onMounted(() => {
  loadProcessTypeData()
})

async function loadProcessTypeData() {
  try {
    const res = await analysisApi.getProductionShare({ from: dateRange.value[0], to: dateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    processTypeTable.value = items
    processTypeData.value = items.map((r: any) => ({ name: r.product_name, value: r.total_qty }))
    processTypeBar.value = {
      categories: items.map((r: any) => r.product_name),
      series: [{ name: '생산량', data: items.map((r: any) => r.total_qty) }]
    }
  } catch (e) {
    console.warn('제품별 점유율 조회 실패:', e)
    ElMessage.error('제품별 점유율 데이터를 불러오는데 실패했습니다')
    processTypeTable.value = []
    processTypeData.value = []
    processTypeBar.value = { categories: [], series: [] }
  }
}

async function loadPartsData() {
  try {
    const res = await analysisApi.getPartsComposition({ from: partsDateRange.value[0], to: partsDateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    partsTable.value = items
    partsData.value = items.map((r: any) => ({ name: r.product_name, value: r.total_qty }))
    partsBar.value = {
      categories: items.map((r: any) => r.product_name),
      series: [{ name: '생산량', data: items.map((r: any) => r.total_qty) }]
    }
  } catch (e) {
    console.warn('부품구성 조회 실패:', e)
    ElMessage.error('부품구성 데이터를 불러오는데 실패했습니다')
    partsTable.value = []
    partsData.value = []
    partsBar.value = { categories: [], series: [] }
  }
}

async function loadCustomerData() {
  try {
    const res = await analysisApi.getByCustomer({ from: customerDateRange.value[0], to: customerDateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    customerTable.value = items
    customerData.value = items.map((r: any) => ({ name: r.customer_name, value: r.total_qty }))
    customerBar.value = {
      categories: items.map((r: any) => r.customer_name),
      series: [{ name: '생산량', data: items.map((r: any) => r.total_qty) }]
    }
  } catch (e) {
    console.warn('거래처별 데이터 조회 실패:', e)
    ElMessage.error('거래처별 데이터를 불러오는데 실패했습니다')
    customerTable.value = []
    customerData.value = []
    customerBar.value = { categories: [], series: [] }
  }
}

async function loadDefectData() {
  try {
    const res = await analysisApi.getDefectByType({ from: defectDateRange.value[0], to: defectDateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    defectTable.value = items
    paretoChart.value = {
      categories: items.map((r: any) => r.ng_type_name),
      values: items.map((r: any) => r.total_qty),
      pieData: items.map((r: any) => ({ name: r.ng_type_name, value: r.total_qty }))
    }
  } catch (e) {
    console.warn('불량항목별 조회 실패:', e)
    ElMessage.error('불량항목별 데이터를 불러오는데 실패했습니다')
    defectTable.value = []
    paretoChart.value = { categories: [], values: [], pieData: [] }
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
