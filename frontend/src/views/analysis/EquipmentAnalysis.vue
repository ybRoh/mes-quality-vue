<template>
  <div class="page-container">
    <PageHeader title="설비별 분석" subtitle="설비 생산능력 및 효율 분석" />

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 생산능력 -->
      <el-tab-pane label="생산능력" name="capacity">
        <div class="filter-bar">
          <DateRangePicker v-model="dateRange" />
          <el-button type="primary" size="small" @click="loadCapacityData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
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
          <el-button type="primary" size="small" @click="loadStData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
        </div>

        <BarChart
          title="설비별 표준시간 달성율 (%)"
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

      <!-- Tab 3: Type별 점유율 -->
      <el-tab-pane label="Type별 점유율" name="typeShare">
        <div class="filter-bar">
          <DateRangePicker v-model="tsDateRange" />
          <el-button type="primary" size="small" @click="loadTypeShareData">
            <el-icon><Search /></el-icon>
            조회
          </el-button>
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
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
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
  { prop: 'machine_no', label: '설비번호', width: 120 },
  { prop: 'machine_type', label: '설비유형', width: 120 },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'work_hours', label: '가동시간(h)', width: 110, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'pieces_per_hour', label: 'EA/hr', width: 100, sortable: true, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'utilization_rate', label: '가동율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' }
]

// Tab 2
const stData = ref<any[]>([])
const stChart = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const stColumns: TableColumn[] = [
  { prop: 'machine_no', label: '설비번호', width: 120 },
  { prop: 'standard_time', label: '표준시간(초)', width: 120, align: 'right' },
  { prop: 'actual_time', label: '실제시간(초)', width: 120, align: 'right', formatter: (v: number) => v?.toFixed(1) || '-' },
  { prop: 'achievement_rate', label: '달성율(%)', width: 160, align: 'center' }
]

// Tab 3
const typeShareData = ref<any[]>([])
const typeSharePie = ref<{ name: string; value: number }[]>([])
const typeShareBar = ref<{ categories: string[]; series: { name: string; data: number[] }[] }>({ categories: [], series: [] })
const typeShareColumns: TableColumn[] = [
  { prop: 'machine_type', label: '설비유형', width: 120 },
  { prop: 'machine_count', label: '설비수', width: 80, align: 'center' },
  { prop: 'total_qty', label: '총 생산', width: 120, sortable: true, align: 'right' },
  { prop: 'share_pct', label: '점유율(%)', width: 100, align: 'right', formatter: (v: number) => v?.toFixed(1) || '0.0' }
]

onMounted(() => {
  loadCapacityData()
})

async function loadCapacityData() {
  try {
    const res = await analysisApi.getEquipmentCapacity({ from: dateRange.value[0], to: dateRange.value[1] })
    const raw = res.data.items || res.data
    const items = Array.isArray(raw) ? raw : []
    capacityData.value = items
    capacityChart.value = {
      categories: items.map((r: any) => r.machine_no),
      series: [{ name: 'EA/hr', data: items.map((r: any) => r.pieces_per_hour) }]
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
      categories: items.map((r: any) => r.machine_no),
      series: [{ name: '달성율', data: items.map((r: any) => r.achievement_rate) }]
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
    typeSharePie.value = items.map((r: any) => ({ name: r.machine_type, value: r.total_qty }))
    typeShareBar.value = {
      categories: items.map((r: any) => r.machine_type),
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
