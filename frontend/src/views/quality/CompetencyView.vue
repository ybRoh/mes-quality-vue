<template>
  <div class="page-container">
    <PageHeader title="역량평가" subtitle="직원 역량 매트릭스 및 Gap 분석">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 역량등록
        </el-button>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 역량 매트릭스 -->
      <el-tab-pane label="역량 매트릭스" name="matrix">
        <div class="filter-bar">
          <el-input
            v-model="filters.employee_id"
            placeholder="직원ID"
            clearable
            style="width: 180px;"
            @clear="loadCompetency"
            @keyup.enter="loadCompetency"
          />
          <el-input
            v-model="filters.skill_name"
            placeholder="스킬명"
            clearable
            style="width: 180px;"
            @clear="loadCompetency"
            @keyup.enter="loadCompetency"
          />
          <el-button type="primary" @click="loadCompetency">검색</el-button>
        </div>

        <el-table :data="competencyList" border stripe v-loading="loading">
          <el-table-column prop="employee_id" label="직원ID" width="120" />
          <el-table-column prop="skill_name" label="스킬명" show-overflow-tooltip />
          <el-table-column prop="required_level" label="필요수준" width="90" align="center" />
          <el-table-column prop="current_level" label="현재수준" width="90" align="center" />
          <el-table-column label="Gap" width="80" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="getGap(row) <= 0"
                type="success"
                size="small"
              >
                충족
              </el-tag>
              <el-tag
                v-else-if="getGap(row) === 1"
                type="warning"
                size="small"
              >
                -1
              </el-tag>
              <el-tag
                v-else
                type="danger"
                size="small"
              >
                -{{ getGap(row) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="evaluation_date" label="평가일" width="110" align="center">
            <template #default="{ row }">
              {{ row.evaluation_date ? row.evaluation_date.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="evaluator" label="평가자" width="100" />
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editItem(row)">편집</el-button>
              <el-button type="danger" link size="small" @click="deleteItem(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: Gap 분석 -->
      <el-tab-pane label="Gap 분석" name="gap">
        <div class="kpi-row">
          <KpiCard title="총 직원수" :value="gapKpi.totalEmployees" unit="명" color="#0A6ED1" />
          <KpiCard title="평균 Gap" :value="gapKpi.avgGap" color="#E9730C" />
          <KpiCard title="Gap 보유 직원" :value="gapKpi.employeesWithGap" unit="명" color="#BB0000" />
          <KpiCard title="역량 충족 직원" :value="gapKpi.employeesMet" unit="명" color="#107E3E" />
        </div>

        <el-table :data="gapAnalysisList" border stripe v-loading="gapLoading">
          <el-table-column prop="employee_id" label="직원ID" width="120" />
          <el-table-column prop="total_skills" label="총 스킬" width="90" align="center" />
          <el-table-column label="평균Gap" width="100" align="center">
            <template #default="{ row }">
              <span :style="{ color: row.avg_gap > 0 ? '#BB0000' : '#107E3E', fontWeight: 600 }">
                {{ typeof row.avg_gap === 'number' ? row.avg_gap.toFixed(1) : row.avg_gap }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="max_gap" label="최대Gap" width="90" align="center" />
          <el-table-column label="미달 스킬" width="100" align="center">
            <template #default="{ row }">
              <span :style="{ color: row.skills_with_gap > 0 ? '#BB0000' : 'inherit', fontWeight: row.skills_with_gap > 0 ? 600 : 400 }">
                {{ row.skills_with_gap }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="충족 스킬" width="100" align="center">
            <template #default="{ row }">
              <span style="color: #107E3E; font-weight: 600;">{{ row.skills_met }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="editingItem ? '역량 수정' : '새 역량 등록'"
      width="500px"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="직원ID" required>
          <el-input v-model="form.employee_id" placeholder="직원ID를 입력하세요" />
        </el-form-item>
        <el-form-item label="스킬명" required>
          <el-input v-model="form.skill_name" placeholder="스킬명을 입력하세요" />
        </el-form-item>
        <el-form-item label="필요수준">
          <el-input-number v-model="form.required_level" :min="1" :max="5" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="현재수준">
          <el-input-number v-model="form.current_level" :min="0" :max="5" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="평가일">
          <el-date-picker
            v-model="form.evaluation_date"
            type="date"
            placeholder="평가일 선택"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="평가자">
          <el-input v-model="form.evaluator" placeholder="평가자를 입력하세요" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">취소</el-button>
        <el-button type="primary" @click="submitForm">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import { trainingApi } from '@/api/quality'

const activeTab = ref('matrix')
const loading = ref(false)
const gapLoading = ref(false)
const showDialog = ref(false)
const editingItem = ref(false)

const competencyList = ref<any[]>([])
const gapAnalysisList = ref<any[]>([])

const filters = reactive({
  employee_id: '',
  skill_name: ''
})

const form = ref({
  competency_id: null as number | null,
  employee_id: '',
  skill_name: '',
  required_level: 3,
  current_level: 0,
  evaluation_date: '',
  evaluator: ''
})

// Gap KPI computed from gap analysis data
const gapKpi = computed(() => {
  const list = gapAnalysisList.value
  if (list.length === 0) {
    return { totalEmployees: 0, avgGap: 0, employeesWithGap: 0, employeesMet: 0 }
  }
  const totalEmployees = list.length
  const totalGap = list.reduce((sum: number, r: any) => sum + (r.avg_gap || 0), 0)
  const avgGap = totalEmployees > 0 ? Math.round((totalGap / totalEmployees) * 10) / 10 : 0
  const employeesWithGap = list.filter((r: any) => r.skills_with_gap > 0).length
  const employeesMet = list.filter((r: any) => r.skills_with_gap === 0).length
  return { totalEmployees, avgGap, employeesWithGap, employeesMet }
})

function getGap(row: any): number {
  return (row.required_level || 0) - (row.current_level || 0)
}

onMounted(() => {
  loadCompetency()
  loadGapAnalysis()
})

async function loadCompetency() {
  loading.value = true
  try {
    const res = await trainingApi.getCompetency({
      employee_id: filters.employee_id || undefined,
      skill_name: filters.skill_name || undefined
    })
    competencyList.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('역량 목록 조회 실패:', e)
    ElMessage.error('역량 목록을 불러오는데 실패했습니다')
    competencyList.value = []
  } finally {
    loading.value = false
  }
}

async function loadGapAnalysis() {
  gapLoading.value = true
  try {
    const res = await trainingApi.getGapAnalysis()
    gapAnalysisList.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('Gap 분석 조회 실패:', e)
    ElMessage.error('Gap 분석 데이터를 불러오는데 실패했습니다')
    gapAnalysisList.value = []
  } finally {
    gapLoading.value = false
  }
}

function openCreateDialog() {
  editingItem.value = false
  form.value = {
    competency_id: null,
    employee_id: '',
    skill_name: '',
    required_level: 3,
    current_level: 0,
    evaluation_date: '',
    evaluator: ''
  }
  showDialog.value = true
}

function editItem(row: any) {
  editingItem.value = true
  form.value = {
    competency_id: row.competency_id,
    employee_id: row.employee_id || '',
    skill_name: row.skill_name || '',
    required_level: row.required_level ?? 3,
    current_level: row.current_level ?? 0,
    evaluation_date: row.evaluation_date ? row.evaluation_date.substring(0, 10) : '',
    evaluator: row.evaluator || ''
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.employee_id} - ${row.skill_name}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await trainingApi.deleteCompetency(row.competency_id)
    ElMessage.success('삭제되었습니다.')
    loadCompetency()
    loadGapAnalysis()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitForm() {
  if (!form.value.employee_id) {
    ElMessage.warning('직원ID를 입력하세요.')
    return
  }
  if (!form.value.skill_name) {
    ElMessage.warning('스킬명을 입력하세요.')
    return
  }

  try {
    const payload = {
      employee_id: form.value.employee_id,
      skill_name: form.value.skill_name,
      required_level: form.value.required_level,
      current_level: form.value.current_level,
      evaluation_date: form.value.evaluation_date || undefined,
      evaluator: form.value.evaluator || undefined
    }

    if (form.value.competency_id) {
      await trainingApi.updateCompetency(form.value.competency_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await trainingApi.createCompetency(payload)
      ElMessage.success('등록되었습니다.')
    }
    showDialog.value = false
    editingItem.value = false
    loadCompetency()
    loadGapAnalysis()
  } catch (e) {
    console.warn('역량 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
</style>
