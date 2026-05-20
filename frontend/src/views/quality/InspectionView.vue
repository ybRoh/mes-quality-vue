<template>
  <div class="page-container">
    <PageHeader title="검사이력 조회" subtitle="제품 검사 이력 및 측정값 조회" />

    <div class="card">
      <div class="filter-bar">
        <el-input v-model="searchLot" placeholder="로트번호 검색" clearable style="width: 200px;">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="filterStage" placeholder="검사 단계" clearable style="width: 150px;">
          <el-option label="초물검사" value="FIRST" />
          <el-option label="중간검사" value="MIDDLE" />
          <el-option label="최종검사" value="LAST" />
        </el-select>
        <el-select v-model="filterResult" placeholder="판정" clearable style="width: 120px;">
          <el-option label="합격" value="PASS" />
          <el-option label="불합격" value="FAIL" />
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
        <template #insp_stage="{ row }">
          {{ getStageLabel(row.insp_stage) }}
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
            <h3 style="margin: 8px 0 0 0;">검사 #{{ selectedInspection.insp_id }}</h3>
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
          <el-descriptions-item label="검사 ID">{{ selectedInspection.insp_id }}</el-descriptions-item>
          <el-descriptions-item label="제품">{{ selectedInspection.product_name || selectedInspection.product_id }}</el-descriptions-item>
          <el-descriptions-item label="로트번호">{{ selectedInspection.lot_no }}</el-descriptions-item>
          <el-descriptions-item label="검사 단계">{{ getStageLabel(selectedInspection.insp_stage) }}</el-descriptions-item>
          <el-descriptions-item label="검사일">{{ selectedInspection.insp_date }}</el-descriptions-item>
          <el-descriptions-item label="검사자">{{ selectedInspection.inspector_name || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Measurement Values -->
      <div class="card" v-if="measurements.length > 0">
        <div class="card-title">측정값 상세</div>
        <el-table :data="measurements" border stripe size="small">
          <el-table-column prop="sample_no" label="시료" width="60" align="center" />
          <el-table-column prop="insp_item" label="검사항목" min-width="150" />
          <el-table-column prop="spec_nominal" label="기준값" width="100" align="right" />
          <el-table-column prop="spec_lsl" label="LSL" width="90" align="right" />
          <el-table-column prop="spec_usl" label="USL" width="90" align="right" />
          <el-table-column prop="measured_value" label="측정값" width="100" align="right">
            <template #default="{ row }">
              <span :class="{ 'value-fail': isOutOfSpec(row) }">
                {{ row.measured_value ?? '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="judgment" label="판정" width="80" align="center">
            <template #default="{ row }">
              <el-tag
                :type="row.judgment === 'OK' ? 'success' : 'danger'"
                size="small"
              >
                {{ row.judgment }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="card" v-else>
        <el-empty description="측정값 데이터가 없습니다" :image-size="60" />
      </div>

      <!-- Remarks -->
      <div v-if="selectedInspection.remark" class="card">
        <div class="card-title">비고</div>
        <p>{{ selectedInspection.remark }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Back } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import DataTable from '@/components/common/DataTable.vue'
import type { TableColumn } from '@/components/common/DataTable.vue'
import { inspectionApi } from '@/api/quality'

const loading = ref(false)
const searchLot = ref('')
const filterStage = ref('')
const filterResult = ref('')

const inspections = ref<any[]>([])
const selectedInspection = ref<any>(null)
const measurements = ref<any[]>([])

const inspectionColumns: TableColumn[] = [
  { prop: 'insp_id', label: '검사ID', width: 80 },
  { prop: 'product_name', label: '제품명', width: 130 },
  { prop: 'lot_no', label: '로트번호', width: 200 },
  { prop: 'insp_stage', label: '검사단계', width: 100 },
  { prop: 'insp_date', label: '검사일', width: 120, sortable: true },
  { prop: 'inspector_name', label: '검사자', width: 90 },
  { prop: 'result', label: '판정', width: 90 }
]

function getStageLabel(stage: string): string {
  switch (stage) {
    case 'FIRST': return '초물검사'
    case 'MIDDLE': return '중간검사'
    case 'LAST': return '최종검사'
    default: return stage || '-'
  }
}

function isOutOfSpec(row: any): boolean {
  if (row.measured_value == null) return false
  if (row.spec_lsl != null && row.measured_value < row.spec_lsl) return true
  if (row.spec_usl != null && row.measured_value > row.spec_usl) return true
  return false
}

onMounted(() => {
  loadInspections()
})

async function loadInspections() {
  loading.value = true
  try {
    const res = await inspectionApi.getList({
      lot_no: searchLot.value || undefined,
      insp_stage: filterStage.value || undefined,
      result: filterResult.value || undefined
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
  try {
    const res = await inspectionApi.getById(row.insp_id)
    selectedInspection.value = res.data
    measurements.value = res.data.values || []
  } catch (e) {
    console.warn('검사 상세 조회 실패:', e)
    ElMessage.error('검사 상세 데이터를 불러오는데 실패했습니다')
    selectedInspection.value = row
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
