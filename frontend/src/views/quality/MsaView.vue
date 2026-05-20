<template>
  <div class="page-container">
    <PageHeader title="MSA (측정시스템 분석)" subtitle="GR&amp;R (Gage R&amp;R) 분석">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          새 MSA 연구
        </el-button>
      </template>
    </PageHeader>

    <!-- Study List -->
    <div class="card" v-if="!selectedStudy">
      <el-table :data="studyList" border stripe v-loading="loading" @row-click="selectStudy">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="study_name" label="연구명" min-width="200" />
        <el-table-column prop="gage_name" label="측정기기" width="130" />
        <el-table-column prop="gage_no" label="기기번호" width="120" />
        <el-table-column prop="operators" label="측정자 수" width="90" align="center" />
        <el-table-column prop="parts" label="부품 수" width="90" align="center" />
        <el-table-column prop="trials" label="반복 횟수" width="90" align="center" />
        <el-table-column prop="grr_pct" label="GR&R(%)" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.grr_pct !== null && row.grr_pct !== undefined"
              :type="row.grr_pct <= 10 ? 'success' : row.grr_pct <= 30 ? 'warning' : 'danger'"
              effect="dark"
            >
              {{ row.grr_pct?.toFixed(1) }}%
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="judgment" label="판정" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.judgment" :type="getJudgmentType(row.judgment)" size="small">{{ getJudgmentLabel(row.judgment) }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="생성일" width="120" align="center" />
      </el-table>
    </div>

    <!-- Study Detail -->
    <div v-if="selectedStudy">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <el-button link @click="selectedStudy = null">
              <el-icon><Back /></el-icon>
              목록으로
            </el-button>
            <h3 style="margin: 8px 0 0 0;">{{ selectedStudy.study_name }}</h3>
            <p style="margin: 4px 0; color: #6A6D70;">측정기기: {{ selectedStudy.gage_name }} ({{ selectedStudy.gage_no }})</p>
          </div>
          <el-button type="primary" @click="calculateGrr" :loading="calculating">
            <el-icon><DataAnalysis /></el-icon>
            GR&amp;R 계산
          </el-button>
        </div>
      </div>

      <!-- Measurement Data Entry -->
      <div class="card">
        <div class="card-title">측정 데이터 입력</div>
        <el-table :data="measurementGrid" border stripe size="small" max-height="400">
          <el-table-column prop="operator" label="측정자" width="100" fixed="left" />
          <el-table-column prop="part" label="부품" width="80" fixed="left" align="center" />
          <el-table-column prop="trial" label="반복" width="80" fixed="left" align="center" />
          <el-table-column label="측정값" min-width="150">
            <template #default="{ row, $index }">
              <el-input-number
                v-model="row.value"
                :precision="4"
                :controls="false"
                size="small"
                style="width: 120px;"
                @change="updateMeasurement($index, row.value)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Results -->
      <div v-if="grrResults" class="card">
        <div class="card-title">GR&amp;R 분석 결과</div>

        <el-descriptions :column="3" border style="margin-bottom: 16px;">
          <el-descriptions-item label="EV (반복성)">{{ grrResults.EV?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="AV (재현성)">{{ grrResults.AV?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="GR&R">{{ grrResults.GRR?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="PV (부품변동)">{{ grrResults.PV?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="TV (총변동)">{{ grrResults.TV?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="GR&R %">
            <el-tag :type="grrResults.grr_pct <= 10 ? 'success' : grrResults.grr_pct <= 30 ? 'warning' : 'danger'" effect="dark" size="large">
              {{ grrResults.grr_pct?.toFixed(1) }}%
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="ndc">{{ grrResults.ndc }}</el-descriptions-item>
        </el-descriptions>

        <!-- Judgment -->
        <el-result
          :icon="grrResults.grr_pct <= 10 ? 'success' : grrResults.grr_pct <= 30 ? 'warning' : 'error'"
          :title="getJudgmentLabel(grrResults.judgment)"
          :sub-title="getJudgmentDescription(grrResults.judgment)"
        />

        <!-- GR&R Chart -->
        <GrrChart
          :components="{ EV: grrResults.EV, AV: grrResults.AV, PV: grrResults.PV, GRR: grrResults.GRR }"
          title="변동 기여율 분석"
        />
      </div>
    </div>

    <!-- Create Study Dialog -->
    <el-dialog v-model="showCreateDialog" title="새 MSA 연구" width="600px">
      <el-form :model="studyForm" label-position="top">
        <el-form-item label="연구명" required>
          <el-input v-model="studyForm.study_name" placeholder="MSA 연구명" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="측정기기명" required>
              <el-input v-model="studyForm.gage_name" placeholder="예: 마이크로미터" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="기기번호">
              <el-input v-model="studyForm.gage_no" placeholder="예: GM-001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="측정자 수">
              <el-input-number v-model="studyForm.operators" :min="2" :max="5" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="부품 수">
              <el-input-number v-model="studyForm.parts" :min="5" :max="20" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="반복 횟수">
              <el-input-number v-model="studyForm.trials" :min="2" :max="5" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="공차 (Tolerance)">
          <el-input-number v-model="studyForm.tolerance" :precision="4" :step="0.01" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="createStudy">생성</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Back, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import GrrChart from '@/components/charts/GrrChart.vue'
import { msaApi } from '@/api/quality'

const loading = ref(false)
const calculating = ref(false)
const showCreateDialog = ref(false)

const studyList = ref<any[]>([])
const selectedStudy = ref<any>(null)
const measurementGrid = ref<{ operator: string; part: number; trial: number; value: number | null }[]>([])
const grrResults = ref<any>(null)

const studyForm = ref({
  study_name: '',
  gage_name: '',
  gage_no: '',
  operators: 3,
  parts: 10,
  trials: 3,
  tolerance: 0.2
})

function getJudgmentType(judgment: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (judgment) {
    case 'ACCEPTABLE': return 'success'
    case 'MARGINAL': return 'warning'
    case 'UNACCEPTABLE': return 'danger'
    default: return 'info'
  }
}

function getJudgmentLabel(judgment: string): string {
  switch (judgment) {
    case 'ACCEPTABLE': return '적합 (Acceptable)'
    case 'MARGINAL': return '조건부 적합 (Marginal)'
    case 'UNACCEPTABLE': return '부적합 (Unacceptable)'
    default: return judgment
  }
}

function getJudgmentDescription(judgment: string): string {
  switch (judgment) {
    case 'ACCEPTABLE': return 'GR&R <= 10%: 측정시스템이 적합합니다.'
    case 'MARGINAL': return 'GR&R 10~30%: 조건부 적합. 측정시스템 개선을 권고합니다.'
    case 'UNACCEPTABLE': return 'GR&R > 30%: 측정시스템이 부적합합니다. 즉각적 개선이 필요합니다.'
    default: return ''
  }
}

onMounted(() => {
  loadStudyList()
})

async function loadStudyList() {
  loading.value = true
  try {
    const res = await msaApi.getList()
    studyList.value = res.data.items || res.data
  } catch (e) {
    console.warn('MSA 연구 목록 조회 실패:', e)
    ElMessage.error('MSA 연구 목록을 불러오는데 실패했습니다')
    studyList.value = []
  } finally {
    loading.value = false
  }
}

function selectStudy(row: any) {
  selectedStudy.value = row
  grrResults.value = null
  generateMeasurementGrid(row.operators || 3, row.parts || 10, row.trials || 3)
  loadMeasurements(row.id)
}

function generateMeasurementGrid(operators: number, parts: number, trials: number) {
  const grid: any[] = []
  const operatorNames = ['작업자A', '작업자B', '작업자C', '작업자D', '작업자E']
  for (let op = 0; op < operators; op++) {
    for (let part = 1; part <= parts; part++) {
      for (let trial = 1; trial <= trials; trial++) {
        grid.push({
          operator: operatorNames[op],
          part,
          trial,
          value: null
        })
      }
    }
  }
  measurementGrid.value = grid
}

async function loadMeasurements(studyId: number) {
  try {
    const res = await msaApi.getMeasurements(studyId)
    const data = res.data
    data.forEach((m: any) => {
      const idx = measurementGrid.value.findIndex(
        g => g.operator === m.operator && g.part === m.part && g.trial === m.trial
      )
      if (idx >= 0) measurementGrid.value[idx].value = m.value
    })
  } catch (e) {
    console.warn('측정 데이터 조회 실패:', e)
    ElMessage.error('측정 데이터를 불러오는데 실패했습니다')
  }
}

function updateMeasurement(_index: number, _value: number | null) {
  // Local update only; saves on calculate
}

async function calculateGrr() {
  if (!selectedStudy.value) return
  calculating.value = true

  try {
    await msaApi.saveMeasurements(selectedStudy.value.id, measurementGrid.value.filter(m => m.value !== null))
    const res = await msaApi.calculate(selectedStudy.value.id)
    grrResults.value = res.data
  } catch (e) {
    console.warn('GR&R 계산 실패:', e)
    ElMessage.error('GR&R 계산에 실패했습니다')
    grrResults.value = null
  } finally {
    calculating.value = false
  }
}

async function createStudy() {
  if (!studyForm.value.study_name || !studyForm.value.gage_name) {
    ElMessage.warning('필수항목을 입력하세요.')
    return
  }
  try {
    await msaApi.create(studyForm.value)
    ElMessage.success('MSA 연구가 생성되었습니다.')
    showCreateDialog.value = false
    studyForm.value = { study_name: '', gage_name: '', gage_no: '', operators: 3, parts: 10, trials: 3, tolerance: 0.2 }
    loadStudyList()
  } catch {
    ElMessage.error('생성에 실패했습니다.')
  }
}
</script>
