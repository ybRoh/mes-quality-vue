<template>
  <div class="page-container">
    <PageHeader title="설비별 분석" subtitle="설비 생산능력 및 효율 분석" />

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 생산능력 -->
      <el-tab-pane label="생산능력" name="capacity">
        <div class="filter-bar">
          <DateRangePicker v-model="dateRange" />
        </div>

        <BarChart
          title="설비별 시간당 생산능력 (EA/hr)"
          :x-data="capacityChart.categories"
          :series="capacityChart.series"
          y-axis-name="EA/hr"
        />

        <div class="card" style="margin-top: 16px;">
          <DataTable :data="capacityData" :columns="capacityColumns" :show-export="true" />
        </div>
      </el-tab-pane>

      <!-- Tab 2: S/T 달성율 -->
      <el-tab-pane label="S/T 달성율" name="stAchievement">
        <div class="filter-bar">
          <DateRangePicker v-model="stDateRange" />
        </div>

        <BarChart
          title="설비별 표준시간 달성율 (%)"
          :x-data="stChart.categories"
          :series="stChart.series"
          y-axis-name="%"
        />

        <div class="card" style="margin-top: 16px;">
          <DataTable :data="stData" :columns="stColumns" :show-export="true">
            <template #st_achievement="{ row }">
              <el-progress
                :percentage="row.st_achievement || 0"
                :status="(row.st_achievement || 0) >= 95 ? 'success' : (row.st_achievement || 0) >= 80 ? '' : 'exception'"
                :stroke-width="14"
                :text-inside="true"
                style="width: 120px;"
              />
            </template>
          </DataTable>
        </div>
      </el-tab-pane>

      <!-- Tab 3: Type별 점유율 -->
      <el-tab-pane label="Type별 점유율" name="typeShare">
        <div class="filter-bar">
          <DateRangePicker v-model="tsDateRange" />
        </div>

        <div class="chart-row">
          <PieChart title="설비 유형별 점유율" :data="typeSharePie" donut />
          <BarChart
            title="설비 유형별 생산량"
            :x-data="typeShareBar.categories"
            :series="typeShareBar.series"
            y-axis-name="수량 (EA)"
          />
        </div>

        <div class="card">
          <DataTable :data="typeShareData" :columns="typeShareColumns" :show-export="true" />
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
import BarChart from '@/components/charts/BarChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import { analysisApi } from '@/api/analysis'
import dayjs from 'dayjs'

const activeTab = ref('capacity')
const dateRange = ref<[string, string]>([dayjs().subtract(30, 'day').format('YYYY-MM-DD'), dayjs().format('YYYY-MM-DD')])
const stDateRange = ref<[string, string]>([...dateRange.value] as [string, string])
const tsDateRange = ref<[string, string]>([...dateRange.value] as [string, string])

// Tab 1
const capacityData = ref<any[]>([])
const capacityChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const capacityColumns: TableColumn[] = [
  { prop: 'machine_id', label: '설비번호', width: 120 },
  { prop: 'machine_name', label: '설비명', width: 120 },
  { prop: 'process_type', label: '설비유형', width: 120 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'operating_hours', label: '가동시간(h)', width: 110, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'pieces_per_hour', label: 'EA/hr', width: 100, sortable: true, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'capacity_rate', label: '가동율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' }
]

// Tab 2
const stData = ref<any[]>([])
const stChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const stColumns: TableColumn[] = [
  { prop: 'machine_id', label: '설비번호', width: 120 },
  { prop: 'machine_name', label: '설비명', width: 120 },
  { prop: 'product_name', label: '제품명', width: 150 },
  { prop: 'std_cycle_time', label: '표준시간(초)', width: 120, align: 'right' },
  { prop: 'avg_cycle_time', label: '실제시간(초)', width: 120, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'st_achievement', label: '달성율(%)', width: 160, align: 'center' }
]

// Tab 3
const typeShareData = ref<any[]>([])
const typeSharePie = ref<{ name: string; value: number }[]>([])
const typeShareBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const typeShareColumns: TableColumn[] = [
  { prop: 'process_name', label: '설비유형', width: 120 },
  { prop: 'machine_count', label: '설비수', width: 80, align: 'center' },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

// 탭 전환 시 자동 로드
watch(activeTab, (tab) => {
  if (tab === 'capacity') loadCapacityData()
  else if (tab === 'stAchievement') loadStData()
  else if (tab === 'typeShare') loadTypeShareData()
})

// 날짜 변경 시 자동 로드
watch(dateRange, () => { if (activeTab.value === 'capacity') loadCapacityData() }, { deep: true })
watch(stDateRange, () => { if (activeTab.value === 'stAchievement') loadStData() }, { deep: true })
watch(tsDateRange, () => { if (activeTab.value === 'typeShare') loadTypeShareData() }, { deep: true })

onMounted(() => {
  loadCapacityData()
})

async function loadCapacityData() {
  try {
    const res = await analysisApi.getEquipmentCapacity({ from: dateRange.value[0], to: dateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    capacityData.value = items.map((r: any) => ({
      ...r,
      pieces_per_hour: r.operating_hours > 0 ? Math.round(r.total_qty / r.operating_hours * 10) / 10 : 0
    }))
    capacityChart.value = {
      categories: capacityData.value.map((r: any) => r.machine_name),
      series: [{ name: 'EA/hr', data: capacityData.value.map((r: any) => r.pieces_per_hour) }]
    }
  } catch (e) {
    console.warn('설비 생산능력 조회 실패:', e)
    ElMessage.error('설비 생산능력 데이터를 불러오는데 실패했습니다')
    capacityData.value = []
    capacityChart.value = { categories: [], series: [] }
  }
}

async function loadStData() {
  try {
    const res = await analysisApi.getStandardTimeAchievement({ from: stDateRange.value[0], to: stDateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    stData.value = items
    stChart.value = {
      categories: items.map((r: any) => r.machine_name),
      series: [{ name: '달성율', data: items.map((r: any) => r.st_achievement || 0) }]
    }
  } catch (e) {
    console.warn('S/T 달성율 조회 실패:', e)
    ElMessage.error('S/T 달성율 데이터를 불러오는데 실패했습니다')
    stData.value = []
    stChart.value = { categories: [], series: [] }
  }
}

async function loadTypeShareData() {
  try {
    const res = await analysisApi.getEquipmentTypeShare({ from: tsDateRange.value[0], to: tsDateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    typeShareData.value = items
    typeSharePie.value = items.map((r: any) => ({ name: r.process_name, value: r.total_qty }))
    typeShareBar.value = {
      categories: items.map((r: any) => r.process_name),
      series: [{ name: '생산량', data: items.map((r: any) => r.total_qty) }]
    }
  } catch (e) {
    console.warn('설비 유형별 점유율 조회 실패:', e)
    ElMessage.error('설비 유형별 점유율 데이터를 불러오는데 실패했습니다')
    typeShareData.value = []
    typeSharePie.value = []
    typeShareBar.value = { categories: [], series: [] }
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
