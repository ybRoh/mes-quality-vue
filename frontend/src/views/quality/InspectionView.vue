<template>
  <div class="page-container">
    <PageHeader title="검사이력 조회" subtitle="제품 검사 이력 및 측정값 조회" />

    <div class="card">
      <div class="filter-bar">
        <DateRangePicker v-model="dateRange" />
        <el-input v-model="searchSpec" placeholder="제품규격 검색" clearable style="width: 200px;">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStage" placeholder="검사 단계" clearable style="width: 150px;">
          <el-option label="수입검사" value="INCOMING" />
          <el-option label="공정검사" value="IN_PROCESS" />
          <el-option label="최종검사" value="FINAL" />
          <el-option label="출하검사" value="OUTGOING" />
        </el-select>
        <el-button type="primary" @click="loadInspections">
          <el-icon><Search /></el-icon>
          조회
        </el-button>
      </div>
    </div>

    <!-- Inspection List -->
    <div class="card" v-if="!selectedInspection">
      <DataTable
        :data="inspections"
        :columns="inspectionColumns"
        :show-export="true"
        :loading="loading"
      >
        <template #result="{ row }">
          <el-tag :type="row.result === 'PASS' ? 'success' : 'danger'" size="small" effect="dark">
            {{ row.result === 'PASS' ? '합격' : '불합격' }}
          </el-tag>
        </template>
        <template #stage="{ row }">
          {{ getStageLabel(row.stage) }}
        </template>
        <template #columns>
          <el-table-column label="상세" width="80" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewDetail(row)">보기</el-button>
            </template>
          </el-table-column>
        </template>
      </DataTable>
    </div>

    <!-- Inspection Detail -->
    <div v-if="selectedInspection">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <el-button link @click="selectedInspection = null">
              <el-icon><Back /></el-icon>
              목록으로
            </el-button>
            <h3 style="margin: 8px 0 0 0;">검사번호: {{ selectedInspection.inspection_no }}</h3>
          </div>
          <el-tag :type="selectedInspection.result === 'PASS' ? 'success' : 'danger'" effect="dark" size="large">
            {{ selectedInspection.result === 'PASS' ? '합격' : '불합격' }}
          </el-tag>
        </div>
      </div>

      <!-- Inspection Info -->
      <div class="card">
        <div class="card-title">검사 정보</div>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="검사번호">{{ selectedInspection.inspection_no }}</el-descriptions-item>
          <el-descriptions-item label="제품규격">{{ selectedInspection.product_spec }}</el-descriptions-item>
          <el-descriptions-item label="로트번호">{{ selectedInspection.lot_no }}</el-descriptions-item>
          <el-descriptions-item label="검사 단계">{{ getStageLabel(selectedInspection.stage) }}</el-descriptions-item>
          <el-descriptions-item label="검사일">{{ selectedInspection.inspection_date }}</el-descriptions-item>
          <el-descriptions-item label="검사자">{{ selectedInspection.inspector }}</el-descriptions-item>
          <el-descriptions-item label="검사 수량">{{ selectedInspection.sample_qty }}</el-descriptions-item>
          <el-descriptions-item label="합격 수량">{{ selectedInspection.pass_qty }}</el-descriptions-item>
          <el-descriptions-item label="불합격 수량">{{ selectedInspection.fail_qty }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Measurement Values -->
      <div class="card">
        <div class="card-title">측정값 상세</div>
        <el-table :data="measurements" border stripe size="small">
          <el-table-column prop="item_no" label="번호" width="60" align="center" />
          <el-table-column prop="characteristic" label="검사항목" min-width="150" />
          <el-table-column prop="specification" label="규격" width="130" align="center" />
          <el-table-column prop="lsl" label="LSL" width="90" align="right" />
          <el-table-column prop="usl" label="USL" width="90" align="right" />
          <el-table-column prop="measured_value" label="측정값" width="100" align="right">
            <template #default="{ row }">
              <span :class="{ 'value-fail': row.measured_value < row.lsl || row.measured_value > row.usl }">
                {{ row.measured_value }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="unit" label="단위" width="60" align="center" />
          <el-table-column label="판정" width="80" align="center">
            <template #default="{ row }">
              <el-tag
                :type="row.measured_value >= row.lsl && row.measured_value <= row.usl ? 'success' : 'danger'"
                size="small"
              >
                {{ row.measured_value >= row.lsl && row.measured_value <= row.usl ? 'OK' : 'NG' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Remarks -->
      <div v-if="selectedInspection.remarks" class="card">
        <div class="card-title">비고</div>
        <p>{{ selectedInspection.remarks }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Back } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import DateRangePicker from '@/components/common/DateRangePicker.vue'
import DataTable from '@/components/common/DataTable.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'
import { inspectionApi } from '@/api/quality'
import dayjs from 'dayjs'

const loading = ref(false)
const dateRange = ref<[string, string]>([
  dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])
const searchSpec = ref('')
const filterStage = ref('')

const inspections = ref<any[]>([])
const selectedInspection = ref<any>(null)
const measurements = ref<any[]>([])

const inspectionColumns: TableColumn[] = [
  { prop: 'inspection_no', label: '검사번호', width: 150 },
  { prop: 'product_spec', label: '제품규격', width: 130 },
  { prop: 'lot_no', label: '로트번호', width: 130 },
  { prop: 'stage', label: '검사단계', width: 100 },
  { prop: 'inspection_date', label: '검사일', width: 120, sortable: true },
  { prop: 'inspector', label: '검사자', width: 90 },
  { prop: 'sample_qty', label: '검사수량', width: 90, align: 'right' },
  { prop: 'result', label: '판정', width: 90 }
]

function getStageLabel(stage: string): string {
  switch (stage) {
    case 'INCOMING': return '수입검사'
    case 'IN_PROCESS': return '공정검사'
    case 'FINAL': return '최종검사'
    case 'OUTGOING': return '출하검사'
    default: return stage
  }
}

onMounted(() => {
  loadInspections()
})

async function loadInspections() {
  loading.value = true
  try {
    const res = await inspectionApi.getList({
      product_id: searchSpec.value || undefined,
      insp_stage: filterStage.value || undefined
    })
    inspections.value = res.data.items || res.data
  } catch (e) {
    console.warn('검사이력 조회 실패:', e)
    ElMessage.error('검사이력을 불러오는데 실패했습니다')
    inspections.value = []
  } finally {
    loading.value = false
  }
}

async function viewDetail(row: any) {
  selectedInspection.value = row

  try {
    const res = await inspectionApi.getMeasurements(row.id)
    measurements.value = res.data
  } catch (e) {
    console.warn('측정값 조회 실패:', e)
    ElMessage.error('측정값 데이터를 불러오는데 실패했습니다')
    measurements.value = []
  }
}
</script>

<style scoped>
.value-fail {
  color: #BB0000;
  font-weight: 700;
}
</style>
