<template>
  <div class="page-container">
    <PageHeader title="유형별 분석" subtitle="생산유형, 부품구성, 거래처별 분석" />

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 생산종류 점유율 -->
      <el-tab-pane label="생산종류 점유율" name="processType">
        <div class="filter-bar">
          <DateRangePicker v-model="dateRange" @update:model-value="loadProcessTypeData" />
          <el-button type="primary" size="small" @click="loadProcessTypeData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <div class="chart-row">
          <PieChart title="생산종류별 점유율" :data="processTypeData" donut />
          <BarChart
            title="생산종류별 생산량"
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
          <DateRangePicker v-model="partsDateRange" @update:model-value="loadPartsData" />
          <el-button type="primary" size="small" @click="loadPartsData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
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
          <DateRangePicker v-model="customerDateRange" @update:model-value="loadCustomerData" />
          <el-button type="primary" size="small" @click="loadCustomerData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
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
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import DateRangePicker from '@/components/common/DateRangePicker.vue'
import DataTable from '@/components/common/DataTable.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'
import PieChart from '@/components/charts/PieChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { analysisApi } from '@/api/analysis'
import dayjs from 'dayjs'

const activeTab = ref('processType')
const dateRange = ref<[string, string]>([dayjs().subtract(30, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')])
const partsDateRange = ref<[string, string]>([...dateRange.value] as [string, string])
const customerDateRange = ref<[string, string]>([...dateRange.value] as [string, string])

// Tab 1
const processTypeData = ref<{ name: string; value: number }[]>([])
const processTypeBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const processTypeTable = ref<any[]>([])
const processTypeColumns: TableColumn[] = [
  { prop: 'process_type', label: '생산종류', width: 130 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'good_qty', label: '양품', width: 100, align: 'right' },
  { prop: 'defect_qty', label: '불량', width: 100, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// Tab 2
const partsData = ref<{ name: string; value: number }[]>([])
const partsBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const partsTable = ref<any[]>([])
const partsColumns: TableColumn[] = [
  { prop: 'part_name', label: '부품명', width: 150 },
  { prop: 'product_spec', label: '규격', width: 130 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// Tab 3
const customerData = ref<{ name: string; value: number }[]>([])
const customerBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const customerTable = ref<any[]>([])
const customerColumns: TableColumn[] = [
  { prop: 'customer', label: '거래처', width: 150 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'good_qty', label: '양품', width: 100, align: 'right' },
  { prop: 'defect_qty', label: '불량', width: 100, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

onMounted(() => {
  loadProcessTypeData()
})

async function loadProcessTypeData() {
  try {
    const res = await analysisApi.getProductionShare({ from: dateRange.value[0], to: dateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    processTypeTable.value = items
    processTypeData.value = items.map((r: any) => ({ name: r.process_type, value: r.total_qty }))
    processTypeBar.value = {
      categories: items.map((r: any) => r.process_type),
      series: [{ name: '생산량', data: items.map((r: any) => r.total_qty) }]
    }
  } catch (e) {
    console.warn('생산종류 점유율 조회 실패:', e)
    ElMessage.error('생산종류 점유율 데이터를 불러오는데 실패했습니다')
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
    partsData.value = items.map((r: any) => ({ name: r.part_name, value: r.total_qty }))
    partsBar.value = {
      categories: items.map((r: any) => r.part_name),
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
    customerData.value = items.map((r: any) => ({ name: r.customer, value: r.total_qty }))
    customerBar.value = {
      categories: items.map((r: any) => r.customer),
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
</script>
