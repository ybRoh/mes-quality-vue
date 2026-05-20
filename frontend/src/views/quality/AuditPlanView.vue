<template>
  <div class="page-container">
    <PageHeader title="심사 일정/계획 관리" subtitle="내부심사 계획 수립 및 진행">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 심사계획
        </el-button>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 심사계획 목록 -->
      <el-tab-pane label="심사계획 목록" name="list">
        <div class="filter-bar">
          <el-input-number
            v-model="filterYear"
            :min="2020"
            :max="2099"
            controls-position="right"
            style="width: 120px;"
            placeholder="심사년도"
            @change="loadPlans"
          />
          <el-select v-model="filterType" placeholder="심사유형" clearable style="width: 140px;" @change="loadPlans">
            <el-option label="내부" value="INTERNAL" />
            <el-option label="공급자" value="SUPPLIER" />
            <el-option label="공정" value="PROCESS" />
          </el-select>
          <el-select v-model="filterStatus" placeholder="상태" clearable style="width: 140px;" @change="loadPlans">
            <el-option label="계획" value="PLANNED" />
            <el-option label="진행중" value="IN_PROGRESS" />
            <el-option label="완료" value="COMPLETED" />
            <el-option label="취소" value="CANCELLED" />
          </el-select>
        </div>

        <el-table :data="plans" border stripe v-loading="loading" @row-click="selectPlan">
          <el-table-column prop="plan_no" label="계획번호" width="140" />
          <el-table-column prop="title" label="심사명" show-overflow-tooltip />
          <el-table-column prop="audit_type" label="유형" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getAuditTypeTag(row.audit_type)" size="small">
                {{ getAuditTypeLabel(row.audit_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="부서" width="100" />
          <el-table-column prop="lead_auditor" label="선임심사원" width="100" />
          <el-table-column label="심사기간" width="180" align="center">
            <template #default="{ row }">
              {{ row.plan_start || '-' }} ~ {{ row.plan_end || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="상태" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="finding_count" label="발견사항" width="90" align="center" />
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editPlan(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deletePlan(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 심사상세 -->
      <el-tab-pane label="심사상세" name="detail">
        <el-empty v-if="!selectedPlan" description="심사계획 목록에서 항목을 선택하세요." />

        <template v-if="selectedPlan">
          <div class="plan-detail-header">
            <h3>{{ selectedPlan.plan_no }}</h3>
            <span>{{ selectedPlan.title }}</span>
            <el-tag :type="getStatusType(selectedPlan.status)" size="small">
              {{ getStatusLabel(selectedPlan.status) }}
            </el-tag>
            <span style="color: var(--qms-text-secondary); font-size: 14px;">
              선임심사원: {{ selectedPlan.lead_auditor || '-' }}
            </span>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin: 0;">발견사항</h4>
            <el-button type="primary" size="small" @click="openFindingDialog">
              <el-icon><Plus /></el-icon>
              새 발견사항
            </el-button>
          </div>

          <el-table :data="findings" border stripe v-loading="findingsLoading" size="small">
            <el-table-column prop="finding_no" label="발견번호" width="130" />
            <el-table-column prop="finding_type" label="유형" width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="getFindingTypeTag(row.finding_type)" size="small">
                  {{ getFindingTypeLabel(row.finding_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="clause_ref" label="조항" width="120" />
            <el-table-column prop="description" label="설명" show-overflow-tooltip />
            <el-table-column prop="status" label="상태" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getFindingStatusType(row.status)" size="small">
                  {{ row.status || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="작업" width="80" align="center" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewFinding(row)">보기</el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
      </el-tab-pane>

      <!-- Tab 3: 연간현황 -->
      <el-tab-pane label="연간현황" name="summary">
        <div class="filter-bar" style="margin-bottom: 16px;">
          <el-input-number
            v-model="summaryYear"
            :min="2020"
            :max="2099"
            controls-position="right"
            style="width: 120px;"
            @change="loadSummary"
          />
        </div>

        <div class="kpi-row">
          <KpiCard title="총 심사계획" :value="summary.total_plans" unit="건" color="#0A6ED1" />
          <KpiCard title="완료" :value="summary.completed" unit="건" color="#107E3E" />
          <KpiCard title="총 발견사항" :value="summary.total_findings" unit="건" color="#BB0000" />
          <KpiCard title="중부적합" :value="summary.major_nc" unit="건" color="#E9730C" />
          <KpiCard title="경부적합" :value="summary.minor_nc" unit="건" color="#1B90FF" />
          <KpiCard title="시정조치(기한초과)" :value="summary.overdue_actions" unit="건" color="#BB0000" />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Plan Create/Edit Dialog -->
    <el-dialog
      v-model="showPlanDialog"
      :title="editingPlan ? '심사계획 수정' : '새 심사계획'"
      width="700px"
    >
      <el-form :model="planForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="계획번호" required>
              <el-input v-model="planForm.plan_no" placeholder="AUD-2026-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="심사년도" required>
              <el-input-number v-model="planForm.audit_year" :min="2020" :max="2099" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="심사유형" required>
              <el-select v-model="planForm.audit_type" style="width: 100%;">
                <el-option label="내부" value="INTERNAL" />
                <el-option label="공급자" value="SUPPLIER" />
                <el-option label="공정" value="PROCESS" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="상태">
              <el-select v-model="planForm.status" style="width: 100%;">
                <el-option label="계획" value="PLANNED" />
                <el-option label="진행중" value="IN_PROGRESS" />
                <el-option label="완료" value="COMPLETED" />
                <el-option label="취소" value="CANCELLED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="심사명" required>
          <el-input v-model="planForm.title" placeholder="심사 제목을 입력하세요" />
        </el-form-item>
        <el-form-item label="범위">
          <el-input v-model="planForm.scope" type="textarea" :rows="3" placeholder="심사 범위를 입력하세요" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="부서">
              <el-input v-model="planForm.department" placeholder="대상 부서" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="선임심사원">
              <el-input v-model="planForm.lead_auditor" placeholder="선임심사원명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="시작일">
              <el-date-picker
                v-model="planForm.plan_start"
                type="date"
                placeholder="시작일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="종료일">
              <el-date-picker
                v-model="planForm.plan_end"
                type="date"
                placeholder="종료일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showPlanDialog = false">취소</el-button>
        <el-button type="primary" @click="submitPlan">저장</el-button>
      </template>
    </el-dialog>

    <!-- Finding Create Dialog -->
    <el-dialog
      v-model="showFindingDialog"
      title="새 발견사항"
      width="600px"
    >
      <el-form :model="findingForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="발견번호" required>
              <el-input v-model="findingForm.finding_no" placeholder="FND-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="유형" required>
              <el-select v-model="findingForm.finding_type" style="width: 100%;">
                <el-option label="중부적합 (Major NC)" value="MAJOR_NC" />
                <el-option label="경부적합 (Minor NC)" value="MINOR_NC" />
                <el-option label="관찰사항 (Observation)" value="OBSERVATION" />
                <el-option label="개선기회 (OFI)" value="OFI" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="관련 조항">
          <el-input v-model="findingForm.clause_ref" placeholder="예: 8.5.1, 7.1.5" />
        </el-form-item>
        <el-form-item label="설명" required>
          <el-input v-model="findingForm.description" type="textarea" :rows="3" placeholder="발견사항 상세 설명" />
        </el-form-item>
        <el-form-item label="객관적 증거">
          <el-input v-model="findingForm.evidence" type="textarea" :rows="3" placeholder="증거 내용을 기술하세요" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFindingDialog = false">취소</el-button>
        <el-button type="primary" @click="submitFinding">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import { auditApi } from '@/api/quality'

const activeTab = ref('list')
const loading = ref(false)
const findingsLoading = ref(false)

// --- Filter state ---
const currentYear = new Date().getFullYear()
const filterYear = ref(currentYear)
const filterType = ref('')
const filterStatus = ref('')
const summaryYear = ref(currentYear)

// --- Data ---
const plans = ref<any[]>([])
const selectedPlan = ref<any>(null)
const findings = ref<any[]>([])
const summary = ref({
  total_plans: 0,
  completed: 0,
  total_findings: 0,
  major_nc: 0,
  minor_nc: 0,
  overdue_actions: 0
})

// --- Dialogs ---
const showPlanDialog = ref(false)
const editingPlan = ref(false)
const showFindingDialog = ref(false)

const planForm = ref({
  plan_id: null as number | null,
  plan_no: '',
  audit_year: currentYear,
  audit_type: 'INTERNAL',
  title: '',
  scope: '',
  department: '',
  lead_auditor: '',
  plan_start: '',
  plan_end: '',
  status: 'PLANNED'
})

const findingForm = ref({
  finding_no: '',
  finding_type: 'MINOR_NC',
  clause_ref: '',
  description: '',
  evidence: ''
})

// --- Label / Tag helpers ---
function getAuditTypeLabel(type: string): string {
  switch (type) {
    case 'INTERNAL': return '내부'
    case 'SUPPLIER': return '공급자'
    case 'PROCESS': return '공정'
    default: return type || '-'
  }
}

function getAuditTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (type) {
    case 'INTERNAL': return ''
    case 'SUPPLIER': return 'warning'
    case 'PROCESS': return 'success'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'PLANNED': return '계획'
    case 'IN_PROGRESS': return '진행중'
    case 'COMPLETED': return '완료'
    case 'CANCELLED': return '취소'
    default: return status || '-'
  }
}

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'PLANNED': return 'info'
    case 'IN_PROGRESS': return 'warning'
    case 'COMPLETED': return 'success'
    case 'CANCELLED': return 'danger'
    default: return 'info'
  }
}

function getFindingTypeLabel(type: string): string {
  switch (type) {
    case 'MAJOR_NC': return '중부적합'
    case 'MINOR_NC': return '경부적합'
    case 'OBSERVATION': return '관찰사항'
    case 'OFI': return '개선기회'
    default: return type || '-'
  }
}

function getFindingTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (type) {
    case 'MAJOR_NC': return 'danger'
    case 'MINOR_NC': return 'warning'
    case 'OBSERVATION': return 'info'
    case 'OFI': return ''
    default: return 'info'
  }
}

function getFindingStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'danger'
    case 'IN_PROGRESS': return 'warning'
    case 'CLOSED': return 'success'
    case 'VERIFIED': return 'success'
    default: return 'info'
  }
}

// --- Lifecycle ---
onMounted(() => {
  loadPlans()
  loadSummary()
})

// --- Plan CRUD ---
async function loadPlans() {
  loading.value = true
  try {
    const res = await auditApi.getPlans({
      audit_year: filterYear.value || undefined,
      audit_type: filterType.value || undefined,
      status: filterStatus.value || undefined
    })
    plans.value = res.data.items || res.data
  } catch (e) {
    console.warn('심사계획 목록 조회 실패:', e)
    ElMessage.error('심사계획 목록을 불러오는데 실패했습니다')
    plans.value = []
  } finally {
    loading.value = false
  }
}

function selectPlan(row: any) {
  selectedPlan.value = row
  activeTab.value = 'detail'
  loadPlanFindings()
}

function openCreateDialog() {
  editingPlan.value = false
  planForm.value = {
    plan_id: null,
    plan_no: '',
    audit_year: currentYear,
    audit_type: 'INTERNAL',
    title: '',
    scope: '',
    department: '',
    lead_auditor: '',
    plan_start: '',
    plan_end: '',
    status: 'PLANNED'
  }
  showPlanDialog.value = true
}

function editPlan(row: any) {
  editingPlan.value = true
  planForm.value = {
    plan_id: row.plan_id,
    plan_no: row.plan_no || '',
    audit_year: row.audit_year || currentYear,
    audit_type: row.audit_type || 'INTERNAL',
    title: row.title || '',
    scope: row.scope || '',
    department: row.department || '',
    lead_auditor: row.lead_auditor || '',
    plan_start: row.plan_start || '',
    plan_end: row.plan_end || '',
    status: row.status || 'PLANNED'
  }
  showPlanDialog.value = true
}

async function deletePlan(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.plan_no}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await auditApi.deletePlan(row.plan_id)
    ElMessage.success('삭제되었습니다.')
    if (selectedPlan.value?.plan_id === row.plan_id) {
      selectedPlan.value = null
      findings.value = []
    }
    loadPlans()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitPlan() {
  if (!planForm.value.plan_no) {
    ElMessage.warning('계획번호를 입력하세요.')
    return
  }
  if (!planForm.value.title) {
    ElMessage.warning('심사명을 입력하세요.')
    return
  }

  try {
    const payload = {
      plan_no: planForm.value.plan_no,
      audit_year: planForm.value.audit_year,
      audit_type: planForm.value.audit_type,
      title: planForm.value.title,
      scope: planForm.value.scope || undefined,
      department: planForm.value.department || undefined,
      lead_auditor: planForm.value.lead_auditor || undefined,
      plan_start: planForm.value.plan_start || undefined,
      plan_end: planForm.value.plan_end || undefined,
      status: planForm.value.status
    }

    if (planForm.value.plan_id) {
      await auditApi.updatePlan(planForm.value.plan_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await auditApi.createPlan(payload)
      ElMessage.success('생성되었습니다.')
    }
    showPlanDialog.value = false
    editingPlan.value = false
    loadPlans()
  } catch (e) {
    console.warn('심사계획 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// --- Findings ---
async function loadPlanFindings() {
  if (!selectedPlan.value) return
  findingsLoading.value = true
  try {
    const res = await auditApi.getPlanFindings(selectedPlan.value.plan_id)
    findings.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('발견사항 조회 실패:', e)
    ElMessage.error('발견사항을 불러오는데 실패했습니다')
    findings.value = []
  } finally {
    findingsLoading.value = false
  }
}

function openFindingDialog() {
  findingForm.value = {
    finding_no: '',
    finding_type: 'MINOR_NC',
    clause_ref: '',
    description: '',
    evidence: ''
  }
  showFindingDialog.value = true
}

async function submitFinding() {
  if (!selectedPlan.value) return
  if (!findingForm.value.finding_no) {
    ElMessage.warning('발견번호를 입력하세요.')
    return
  }
  if (!findingForm.value.description) {
    ElMessage.warning('설명을 입력하세요.')
    return
  }

  try {
    const payload = {
      finding_no: findingForm.value.finding_no,
      finding_type: findingForm.value.finding_type,
      clause_ref: findingForm.value.clause_ref || undefined,
      description: findingForm.value.description,
      evidence: findingForm.value.evidence || undefined
    }
    await auditApi.createFinding(selectedPlan.value.plan_id, payload)
    ElMessage.success('발견사항이 등록되었습니다.')
    showFindingDialog.value = false
    loadPlanFindings()
    loadPlans()
  } catch (e) {
    console.warn('발견사항 등록 실패:', e)
    ElMessage.error('발견사항 등록에 실패했습니다.')
  }
}

function viewFinding(row: any) {
  ElMessage.info(`발견사항 ${row.finding_no} 상세보기는 추후 구현 예정입니다.`)
}

// --- Summary ---
async function loadSummary() {
  try {
    const res = await auditApi.getSummary(summaryYear.value)
    const data = res.data
    summary.value = {
      total_plans: data.total_plans ?? 0,
      completed: data.completed ?? 0,
      total_findings: data.total_findings ?? 0,
      major_nc: data.major_nc ?? 0,
      minor_nc: data.minor_nc ?? 0,
      overdue_actions: data.overdue_actions ?? 0
    }
  } catch (e) {
    console.warn('연간 요약 조회 실패:', e)
    ElMessage.error('연간 현황을 불러오는데 실패했습니다')
    summary.value = {
      total_plans: 0,
      completed: 0,
      total_findings: 0,
      major_nc: 0,
      minor_nc: 0,
      overdue_actions: 0
    }
  }
}
</script>

<style scoped>
.plan-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #E5E5E5;
}

.plan-detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
</style>
