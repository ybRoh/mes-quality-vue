<template>
  <div class="page-container">
    <PageHeader title="규격별 분석" subtitle="제품 규격별 생산시간 및 실적 분석" />

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 생산시간 -->
      <el-tab-pane label="생산시간" name="productionTime">
        <div class="filter-bar">
          <DateRangePicker v-model="dateRange" />
          <el-button type="primary" size="small" @click="loadProductionTimeData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <BarChart
          title="규격별 총 생산시간 (시간)"
          :x-data="ptChart.categories"
          :series="ptChart.series"
          y-axis-name="시간 (h)"
        />

        <div class="card" style="margin-top: 16px;">
          <DataTable :data="ptData" :columns="ptColumns" :show-export="true" />
        </div>
      </el-tab-pane>

      <!-- Tab 2: S/T 달성율 -->
      <el-tab-pane label="S/T 달성율" name="stAchievement">
        <div class="filter-bar">
          <DateRangePicker v-model="stDateRange" />
          <el-button type="primary" size="small" @click="loadStAchievementData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <BarChart
          title="규격별 표준시간 달성율 (%)"
          :x-data="stChart.categories"
          :series="stChart.series"
          y-axis-name="%"
        />

        <div class="card" style="margin-top: 16px;">
          <DataTable :data="stData" :columns="stColumns" :show-export="true">
            <template #achievement_rate="{ row }">
              <el-progress
                :percentage="row.achievement_rate"
                :status="row.achievement_rate >= 95 ? 'success' : row.achievement_rate >= 80 ? '' : 'exception'"
                :stroke-width="14"
                :text-inside="true"
                style="width: 120px;"
              />
            </template>
          </DataTable>
        </div>
      </el-tab-pane>

      <!-- Tab 3: 개별 실적 -->
      <el-tab-pane label="개별 실적" name="individual">
        <div class="filter-bar">
          <DateRangePicker v-model="indDateRange" />
          <el-select v-model="selectedSpec" placeholder="규격 선택" clearable filterable size="default">
            <el-option v-for="s in specOptions" :key="s" :label="s" :value="s" />
          </el-select>
          <el-button type="primary" size="small" @click="loadIndividualData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <div class="kpi-row" v-if="indKpi.total > 0">
          <KpiCard title="총 생산" :value="indKpi.total" unit="EA" color="#0A6ED1" />
          <KpiCard title="양품" :value="indKpi.good" unit="EA" color="#107E3E" />
          <KpiCard title="불량" :value="indKpi.defect" unit="EA" color="#BB0000" />
          <KpiCard title="평균 C/T" :value="indKpi.avgCt" unit="초" color="#E9730C" />
        </div>

        <div class="card">
          <DataTable :data="indData" :columns="indColumns" :show-export="true" />
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
import KpiCard from '@/components/common/KpiCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { analysisApi } from '@/api/analysis'
import dayjs from 'dayjs'

const activeTab = ref('productionTime')
const dateRange = ref<[string, string]>([dayjs().subtract(30, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')])
const stDateRange = ref<[string, string]>([...dateRange.value] as [string, string])
const indDateRange = ref<[string, string]>([...dateRange.value] as [string, string])
const selectedSpec = ref('')
const specOptions = ref<string[]>(['PN-A1020', 'PN-B2030', 'PN-C3040', 'PN-D4050'])

// Tab 1
const ptData = ref<any[]>([])
const ptChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const ptColumns: TableColumn[] = [
  { prop: 'product_spec', label: '규격', width: 130 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'total_hours', label: '총 시간(h)', width: 110, sortable: true, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'avg_cycle_time', label: '평균 C/T(초)', width: 120, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'time_per_unit', label: '개당 시간(초)', width: 120, align: 'right', formatter: (v: number) => v?.toFixed(2) || '-' }
]

// Tab 2
const stData = ref<any[]>([])
const stChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const stColumns: TableColumn[] = [
  { prop: 'product_spec', label: '규격', width: 130 },
  { prop: 'standard_time', label: '표준시간(초)', width: 120, align: 'right' },
  { prop: 'actual_time', label: '실제시간(초)', width: 120, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'achievement_rate', label: '달성율(%)', width: 160, align: 'center' }
]

// Tab 3
const indData = ref<any[]>([])
const indKpi = ref({ total: 0, good: 0, defect: 0, avgCt: 0 })
const indColumns: TableColumn[] = [
  { prop: 'date', label: '날짜', width: 120, sortable: true },
  { prop: 'machine_no', label: '설비', width: 100 },
  { prop: 'product_spec', label: '규격', width: 130 },
  { prop: 'total_qty', label: '총 생산', width: 100, align: 'right' },
  { prop: 'good_qty', label: '양품', width: 100, align: 'right' },
  { prop: 'defect_qty', label: '불량', width: 80, align: 'right' },
  { prop: 'cycle_time', label: 'C/T(초)', width: 90, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' }
]

onMounted(() => {
  loadProductionTimeData()
})

async function loadProductionTimeData() {
  try {
    const res = await analysisApi.getSpecProductionTime({ from: dateRange.value[0], to: dateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    ptData.value = items
    ptChart.value = {
      categories: items.map((r: any) => r.product_spec),
      series: [{ name: '시간(h)', data: items.map((r: any) => r.total_hours) }]
    }
  } catch (e) {
    console.warn('규격별 생산시간 조회 실패:', e)
    ElMessage.error('규격별 생산시간 데이터를 불러오는데 실패했습니다')
    ptData.value = []
    ptChart.value = { categories: [], series: [] }
  }
}

async function loadStAchievementData() {
  try {
    const res = await analysisApi.getSpecStAchievement({ from: stDateRange.value[0], to: stDateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    stData.value = items
    stChart.value = {
      categories: items.map((r: any) => r.product_spec),
      series: [{ name: '달성율', data: items.map((r: any) => r.achievement_rate) }]
    }
  } catch (e) {
    console.warn('규격별 S/T 달성율 조회 실패:', e)
    ElMessage.error('규격별 S/T 달성율 데이터를 불러오는데 실패했습니다')
    stData.value = []
    stChart.value = { categories: [], series: [] }
  }
}

async function loadIndividualData() {
  try {
    const res = await analysisApi.getSpecDetail({
      from: indDateRange.value[0],
      to: indDateRange.value[1],
      product_id: selectedSpec.value || undefined
    })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    indData.value = items
    const total = items.reduce((s: number, r: any) => s + (r.total_qty || 0), 0)
    const good = items.reduce((s: number, r: any) => s + (r.good_qty || 0), 0)
    const defect = items.reduce((s: number, r: any) => s + (r.defect_qty || 0), 0)
    const avgCt = items.length > 0 ? items.reduce((s: number, r: any) => s + (r.cycle_time || 0), 0) / items.length : 0
    indKpi.value = { total, good, defect, avgCt: Math.round(avgCt * 10) / 10 }
  } catch (e) {
    console.warn('개별 실적 조회 실패:', e)
    ElMessage.error('개별 실적 데이터를 불러오는데 실패했습니다')
    indData.value = []
    indKpi.value = { total: 0, good: 0, defect: 0, avgCt: 0 }
  }
}
</script>
