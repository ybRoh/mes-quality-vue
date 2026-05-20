<template>
  <div class="page-container">
    <PageHeader title="기간별 분석" subtitle="생산 실적 분석" />

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 일/월/년 실적 -->
      <el-tab-pane label="일/월/년 실적" name="daily">
        <div class="filter-bar">
          <el-radio-group v-model="periodType" size="small" @change="loadDailyData">
            <el-radio-button value="daily">일별</el-radio-button>
            <el-radio-button value="monthly">월별</el-radio-button>
            <el-radio-button value="yearly">년별</el-radio-button>
          </el-radio-group>
          <DateRangePicker v-model="dateRange" @update:model-value="loadDailyData" />
          <el-button type="primary" size="small" @click="loadDailyData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <div class="kpi-row">
          <KpiCard title="총 생산" :value="dailyKpi.total" unit="EA" color="#0A6ED1" />
          <KpiCard title="양품" :value="dailyKpi.good" unit="EA" color="#107E3E" />
          <KpiCard title="불량" :value="dailyKpi.defect" unit="EA" color="#BB0000" />
          <KpiCard title="불량률" :value="dailyKpi.defectRate" unit="%" :color="dailyKpi.defectRate > 1 ? '#BB0000' : '#107E3E'" />
        </div>

        <div class="card">
          <DataTable :data="dailyData" :columns="dailyColumns" :show-export="true" />
        </div>

        <BarChart
          title="설비별 생산량"
          :x-data="machineChart.categories"
          :series="machineChart.series"
          y-axis-name="수량 (EA)"
        />
      </el-tab-pane>

      <!-- Tab 2: 설비/규격별 실적 -->
      <el-tab-pane label="설비/규격별 실적" name="machineSpec">
        <div class="filter-bar">
          <DateRangePicker v-model="msDateRange" />
          <el-select v-model="selectedMachine" placeholder="설비 선택" clearable size="default">
            <el-option v-for="m in machineOptions" :key="m" :label="m" :value="m" />
          </el-select>
          <el-select v-model="selectedSpec" placeholder="규격 선택" clearable size="default">
            <el-option v-for="s in specOptions" :key="s" :label="s" :value="s" />
          </el-select>
          <el-button type="primary" size="small" @click="loadMachineSpecData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <div class="card">
          <DataTable :data="machineSpecData" :columns="machineSpecColumns" :show-export="true" />
        </div>

        <BarChart
          title="설비/규격별 생산 비교"
          :x-data="msChart.categories"
          :series="msChart.series"
          y-axis-name="수량 (EA)"
          stack
        />
      </el-tab-pane>

      <!-- Tab 3: 월별 추이 -->
      <el-tab-pane label="월별 추이" name="trend">
        <div class="filter-bar">
          <DateRangePicker v-model="trendDateRange" />
          <el-button type="primary" size="small" @click="loadTrendData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <LineChart
          title="월별 생산 추이"
          :x-data="trendChart.months"
          :series="trendChart.series"
          y-axis-name="수량 (EA)"
        />
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
import KpiCard from '@/components/common/KpiCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { analysisApi } from '@/api/analysis'
import dayjs from 'dayjs'

const activeTab = ref('daily')
const periodType = ref('daily')
const dateRange = ref<[string, string]>([
  dayjs().subtract(7, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])

// Tab 1 state
const dailyKpi = ref({ total: 0, good: 0, defect: 0, defectRate: 0 })
const dailyData = ref<any[]>([])
const machineChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({
  categories: [],
  series: []
})

const dailyColumns: TableColumn[] = [
  { prop: 'date', label: '날짜', width: 120, sortable: true },
  { prop: 'machine_no', label: '설비', width: 100 },
  { prop: 'product_spec', label: '규격', width: 130 },
  { prop: 'total_qty', label: '총 생산', width: 100, sortable: true, align: 'right' },
  { prop: 'good_qty', label: '양품', width: 100, align: 'right' },
  { prop: 'defect_qty', label: '불량', width: 100, align: 'right' },
  { prop: 'defect_rate', label: '불량률(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(2) || '0.00' }
]

// Tab 2 state
const msDateRange = ref<[string, string]>([
  dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])
const selectedMachine = ref('')
const selectedSpec = ref('')
const machineOptions = ref<string[]>(['MC-01', 'MC-02', 'MC-03', 'MC-04', 'MC-05'])
const specOptions = ref<string[]>(['PN-A1020', 'PN-B2030', 'PN-C3040'])
const machineSpecData = ref<any[]>([])
const msChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({
  categories: [],
  series: []
})

const machineSpecColumns: TableColumn[] = [
  { prop: 'machine_no', label: '설비', width: 100 },
  { prop: 'product_spec', label: '규격', width: 130 },
  { prop: 'total_qty', label: '총 생산', width: 100, sortable: true, align: 'right' },
  { prop: 'good_qty', label: '양품', width: 100, align: 'right' },
  { prop: 'defect_qty', label: '불량', width: 100, align: 'right' },
  { prop: 'defect_rate', label: '불량률(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(2) || '0.00' },
  { prop: 'avg_cycle_time', label: '평균 C/T(초)', width: 120, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' }
]

// Tab 3 state
const trendDateRange = ref<[string, string]>([
  dayjs().subtract(12, 'month').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])
const trendChart = ref<{ months: string[]; series: { name: string; data: number[] }[] }>({
  months: [],
  series: []
})

onMounted(() => {
  loadDailyData()
})

async function loadDailyData() {
  try {
    let res
    if (periodType.value === 'daily') {
      res = await analysisApi.getDailyProduction({ date: dateRange.value[0] })
    } else if (periodType.value === 'monthly') {
      const d = dayjs(dateRange.value[0])
      res = await analysisApi.getMonthlyProduction({ year: d.year(), month: d.month() + 1 })
    } else {
      const d = dayjs(dateRange.value[0])
      res = await analysisApi.getYearlyProduction({ year: d.year() })
    }

    const raw = res.data.items || res.data
    const data = Array.isArray(raw) ? raw : []
    dailyData.value = data

    const total = data.reduce((s: number, r: any) => s + (r.total_qty || 0), 0)
    const good = data.reduce((s: number, r: any) => s + (r.good_qty || 0), 0)
    const defect = data.reduce((s: number, r: any) => s + (r.defect_qty || 0), 0)
    dailyKpi.value = {
      total,
      good,
      defect,
      defectRate: total > 0 ? Math.round((defect / total) * 10000) / 100 : 0
    }

    // Machine chart grouping
    const machineMap: Record<string, number> = {}
    data.forEach((r: any) => {
      const key = r.machine_no || '기타'
      machineMap[key] = (machineMap[key] || 0) + (r.total_qty || 0)
    })
    machineChart.value = {
      categories: Object.keys(machineMap),
      series: [{ name: '생산량', data: Object.values(machineMap) }]
    }
  } catch (e) {
    console.warn('일/월/년 실적 조회 실패:', e)
    ElMessage.error('실적 데이터를 불러오는데 실패했습니다')
    dailyData.value = []
    dailyKpi.value = { total: 0, good: 0, defect: 0, defectRate: 0 }
    machineChart.value = { categories: [], series: [] }
  }
}

async function loadMachineSpecData() {
  try {
    const res = await analysisApi.getByEquipment({
      from: msDateRange.value[0],
      to: msDateRange.value[1],
      machine_id: selectedMachine.value || undefined
    })
    const rawMs = res.data.items || res.data
    const data = Array.isArray(rawMs) ? rawMs : []
    machineSpecData.value = data
    msChart.value = {
      categories: data.map((r: any) => `${r.machine_no}-${r.product_spec}`),
      series: [
        { name: '양품', data: data.map((r: any) => r.good_qty) },
        { name: '불량', data: data.map((r: any) => r.defect_qty) }
      ]
    }
  } catch (e) {
    console.warn('설비/규격별 실적 조회 실패:', e)
    ElMessage.error('설비/규격별 실적을 불러오는데 실패했습니다')
    machineSpecData.value = []
    msChart.value = { categories: [], series: [] }
  }
}

async function loadTrendData() {
  try {
    const res = await analysisApi.getMonthlyTrend({
      from: trendDateRange.value[0],
      to: trendDateRange.value[1]
    })
    const data = res.data
    trendChart.value = {
      months: data.months,
      series: [
        { name: '양품', data: data.good },
        { name: '불량', data: data.defect }
      ]
    }
  } catch (e) {
    console.warn('월별 추이 조회 실패:', e)
    ElMessage.error('월별 추이 데이터를 불러오는데 실패했습니다')
    trendChart.value = { months: [], series: [] }
  }
}
</script>
