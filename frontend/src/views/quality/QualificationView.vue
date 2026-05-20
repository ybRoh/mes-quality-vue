<template>
  <div class="page-container">
    <PageHeader title="자격관리" subtitle="자격/인증 현황 및 심사 관리">
      <template #actions>
        <el-button type="primary" @click="openQualDialog()">
          <el-icon><Plus /></el-icon>
          새 자격등록
        </el-button>
      </template>
    </PageHeader>

    <!-- KPI Cards -->
    <div class="kpi-row">
      <KpiCard title="총 자격" :value="kpi.total" unit="건" color="#0A6ED1" />
      <KpiCard title="유효" :value="kpi.active" unit="건" color="#107E3E" />
      <KpiCard title="만료예정" :value="kpi.expiring" unit="건" color="#E9730C" />
      <KpiCard title="만료/정지" :value="kpi.expiredSuspended" unit="건" color="#BB0000" />
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 자격현황 -->
      <el-tab-pane label="자격현황" name="status">
        <div class="filter-bar">
          <el-input
            v-model="qualFilter.qual_type"
            placeholder="유형"
            clearable
            style="width: 150px;"
            @clear="loadQualifications"
            @keyup.enter="loadQualifications"
          />
          <el-input
            v-model="qualFilter.holder_id"
            placeholder="보유자"
            clearable
            style="width: 150px;"
            @clear="loadQualifications"
            @keyup.enter="loadQualifications"
          />
          <el-select
            v-model="qualFilter.status"
            placeholder="상태 선택"
            clearable
            style="width: 150px;"
            @change="loadQualifications"
          >
            <el-option label="유효" value="ACTIVE" />
            <el-option label="만료" value="EXPIRED" />
            <el-option label="정지" value="SUSPENDED" />
          </el-select>
          <el-button type="primary" @click="loadQualifications">조회</el-button>
        </div>

        <el-table :data="qualifications" border stripe v-loading="qualLoading">
          <el-table-column prop="qual_type" label="유형" width="100" />
          <el-table-column prop="qual_name" label="자격명" show-overflow-tooltip />
          <el-table-column prop="holder_id" label="보유자" width="100" />
          <el-table-column prop="issuing_body" label="발급기관" width="120" />
          <el-table-column prop="certificate_no" label="인증번호" width="120" />
          <el-table-column prop="issue_date" label="발급일" width="110" align="center">
            <template #default="{ row }">
              {{ row.issue_date ? row.issue_date.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="expiry_date" label="만료일" width="110" align="center">
            <template #default="{ row }">
              <span :style="{ color: row.days_until_expiry != null && row.days_until_expiry < 90 ? '#BB0000' : '' }">
                {{ row.expiry_date ? row.expiry_date.substring(0, 10) : '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="상태" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getQualStatusType(row.status)" size="small">
                {{ getQualStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="days_until_expiry" label="잔여일" width="80" align="center">
            <template #default="{ row }">
              <span v-if="row.days_until_expiry != null" :style="{ color: getDaysColor(row.days_until_expiry), fontWeight: 600 }">
                {{ row.days_until_expiry }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editQual(row)">편집</el-button>
              <el-button type="danger" link size="small" @click="deleteQual(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 만료예정 -->
      <el-tab-pane label="만료예정" name="expiring">
        <el-table :data="expiringList" border stripe v-loading="expiringLoading">
          <el-table-column prop="qual_name" label="자격명" show-overflow-tooltip />
          <el-table-column prop="holder_id" label="보유자" width="100" />
          <el-table-column prop="issuing_body" label="발급기관" width="120" />
          <el-table-column prop="expiry_date" label="만료일" width="110" align="center">
            <template #default="{ row }">
              {{ row.expiry_date ? row.expiry_date.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="days_until_expiry" label="잔여일" width="100" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="row.days_until_expiry != null"
                :type="row.days_until_expiry < 30 ? 'danger' : row.days_until_expiry < 60 ? 'warning' : 'info'"
                size="small"
              >
                {{ row.days_until_expiry }}일
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="상태" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getQualStatusType(row.status)" size="small">
                {{ getQualStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 3: 자격심사 기록 -->
      <el-tab-pane label="자격심사 기록" name="audits">
        <div class="filter-bar">
          <el-input
            v-model="auditFilter.qual_id"
            placeholder="자격 ID"
            clearable
            style="width: 150px;"
            @clear="loadQualAudits"
            @keyup.enter="loadQualAudits"
          />
          <el-select
            v-model="auditFilter.result"
            placeholder="결과 선택"
            clearable
            style="width: 150px;"
            @change="loadQualAudits"
          >
            <el-option label="합격" value="PASS" />
            <el-option label="불합격" value="FAIL" />
            <el-option label="조건부" value="CONDITIONAL" />
          </el-select>
          <el-button type="primary" @click="loadQualAudits">조회</el-button>
          <el-button type="success" @click="openAuditDialog()">
            <el-icon><Plus /></el-icon>
            새 심사기록
          </el-button>
        </div>

        <el-table :data="qualAudits" border stripe v-loading="auditLoading">
          <el-table-column prop="qual_name" label="자격명" show-overflow-tooltip />
          <el-table-column prop="holder_id" label="보유자" width="100" />
          <el-table-column prop="audit_date" label="심사일" width="110" align="center">
            <template #default="{ row }">
              {{ row.audit_date ? row.audit_date.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="auditor" label="심사원" width="100" />
          <el-table-column prop="result" label="결과" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getAuditResultType(row.result)" size="small">
                {{ getAuditResultLabel(row.result) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="점수" width="80" align="center" />
          <el-table-column prop="next_audit_date" label="차기심사일" width="110" align="center">
            <template #default="{ row }">
              {{ row.next_audit_date ? row.next_audit_date.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editAudit(row)">편집</el-button>
              <el-button type="danger" link size="small" @click="deleteAudit(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Qualification Create/Edit Dialog -->
    <el-dialog
      v-model="showQualDialog"
      :title="editingQual ? '자격 수정' : '새 자격 등록'"
      width="600px"
    >
      <el-form :model="qualForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="유형" required>
              <el-input v-model="qualForm.qual_type" placeholder="자격 유형" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="자격명" required>
              <el-input v-model="qualForm.qual_name" placeholder="자격명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="보유자">
              <el-input v-model="qualForm.holder_id" placeholder="보유자 ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="발급기관">
              <el-input v-model="qualForm.issuing_body" placeholder="발급기관" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="인증번호">
              <el-input v-model="qualForm.certificate_no" placeholder="인증번호" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="상태">
              <el-select v-model="qualForm.status" style="width: 100%;">
                <el-option label="유효" value="ACTIVE" />
                <el-option label="만료" value="EXPIRED" />
                <el-option label="정지" value="SUSPENDED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="발급일">
              <el-date-picker
                v-model="qualForm.issue_date"
                type="date"
                placeholder="발급일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="만료일">
              <el-date-picker
                v-model="qualForm.expiry_date"
                type="date"
                placeholder="만료일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showQualDialog = false">취소</el-button>
        <el-button type="primary" @click="submitQual">저장</el-button>
      </template>
    </el-dialog>

    <!-- Qualification Audit Create/Edit Dialog -->
    <el-dialog
      v-model="showAuditDialog"
      :title="editingAudit ? '심사기록 수정' : '새 심사기록 등록'"
      width="600px"
    >
      <el-form :model="auditForm" label-position="top">
        <el-form-item label="자격" required>
          <el-select v-model="auditForm.qual_id" placeholder="자격 선택" filterable style="width: 100%;">
            <el-option
              v-for="q in qualifications"
              :key="q.qual_id"
              :label="`${q.qual_name} (${q.holder_id || '-'})`"
              :value="q.qual_id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="심사일" required>
              <el-date-picker
                v-model="auditForm.audit_date"
                type="date"
                placeholder="심사일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="심사원">
              <el-input v-model="auditForm.auditor" placeholder="심사원명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="결과" required>
              <el-select v-model="auditForm.result" style="width: 100%;">
                <el-option label="합격" value="PASS" />
                <el-option label="불합격" value="FAIL" />
                <el-option label="조건부" value="CONDITIONAL" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="점수">
              <el-input-number v-model="auditForm.score" :min="0" :max="100" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="차기심사일">
          <el-date-picker
            v-model="auditForm.next_audit_date"
            type="date"
            placeholder="차기심사일 선택"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="비고">
          <el-input
            v-model="auditForm.remarks"
            type="textarea"
            :rows="3"
            placeholder="비고 사항을 입력하세요"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAuditDialog = false">취소</el-button>
        <el-button type="primary" @click="submitAudit">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import { trainingApi } from '@/api/quality'

const activeTab = ref('status')
const qualLoading = ref(false)
const expiringLoading = ref(false)
const auditLoading = ref(false)

// Qualification data
const qualifications = ref<any[]>([])
const expiringList = ref<any[]>([])
const qualAudits = ref<any[]>([])

// Filters
const qualFilter = ref({
  qual_type: '',
  holder_id: '',
  status: ''
})

const auditFilter = ref({
  qual_id: '',
  result: ''
})

// Qualification dialog
const showQualDialog = ref(false)
const editingQual = ref(false)
const qualForm = ref({
  qual_id: null as number | null,
  qual_type: '',
  qual_name: '',
  holder_id: '',
  issuing_body: '',
  certificate_no: '',
  issue_date: '',
  expiry_date: '',
  status: 'ACTIVE'
})

// Audit dialog
const showAuditDialog = ref(false)
const editingAudit = ref(false)
const auditForm = ref({
  audit_id: null as number | null,
  qual_id: null as number | null,
  audit_date: '',
  auditor: '',
  result: 'PASS',
  score: null as number | null,
  next_audit_date: '',
  remarks: ''
})

// KPI
const kpi = computed(() => {
  const list = qualifications.value
  return {
    total: list.length,
    active: list.filter((q: any) => q.status === 'ACTIVE').length,
    expiring: expiringList.value.length,
    expiredSuspended: list.filter((q: any) => q.status === 'EXPIRED' || q.status === 'SUSPENDED').length
  }
})

// Helpers
function getQualStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'ACTIVE': return 'success'
    case 'EXPIRED': return 'danger'
    case 'SUSPENDED': return 'warning'
    default: return 'info'
  }
}

function getQualStatusLabel(status: string): string {
  switch (status) {
    case 'ACTIVE': return '유효'
    case 'EXPIRED': return '만료'
    case 'SUSPENDED': return '정지'
    default: return status
  }
}

function getAuditResultType(result: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (result) {
    case 'PASS': return 'success'
    case 'FAIL': return 'danger'
    case 'CONDITIONAL': return 'warning'
    default: return 'info'
  }
}

function getAuditResultLabel(result: string): string {
  switch (result) {
    case 'PASS': return '합격'
    case 'FAIL': return '불합격'
    case 'CONDITIONAL': return '조건부'
    default: return result
  }
}

function getDaysColor(days: number): string {
  if (days < 30) return '#BB0000'
  if (days < 60) return '#E9730C'
  if (days < 90) return '#C35500'
  return '#107E3E'
}

// Data loading
onMounted(() => {
  loadQualifications()
  loadExpiring()
  loadQualAudits()
})

async function loadQualifications() {
  qualLoading.value = true
  try {
    const res = await trainingApi.getQualifications({
      qual_type: qualFilter.value.qual_type || undefined,
      holder_id: qualFilter.value.holder_id || undefined,
      status: qualFilter.value.status || undefined
    })
    qualifications.value = res.data.items || res.data
  } catch (e) {
    console.warn('자격 목록 조회 실패:', e)
    ElMessage.error('자격 목록을 불러오는데 실패했습니다')
    qualifications.value = []
  } finally {
    qualLoading.value = false
  }
}

async function loadExpiring() {
  expiringLoading.value = true
  try {
    const res = await trainingApi.getExpiringQualifications(90)
    expiringList.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('만료예정 자격 조회 실패:', e)
    ElMessage.error('만료예정 자격을 불러오는데 실패했습니다')
    expiringList.value = []
  } finally {
    expiringLoading.value = false
  }
}

async function loadQualAudits() {
  auditLoading.value = true
  try {
    const res = await trainingApi.getQualAudits({
      qual_id: auditFilter.value.qual_id ? Number(auditFilter.value.qual_id) : undefined,
      result: auditFilter.value.result || undefined
    })
    qualAudits.value = res.data.items || res.data
  } catch (e) {
    console.warn('자격심사 기록 조회 실패:', e)
    ElMessage.error('자격심사 기록을 불러오는데 실패했습니다')
    qualAudits.value = []
  } finally {
    auditLoading.value = false
  }
}

// Qualification CRUD
function openQualDialog() {
  editingQual.value = false
  qualForm.value = {
    qual_id: null,
    qual_type: '',
    qual_name: '',
    holder_id: '',
    issuing_body: '',
    certificate_no: '',
    issue_date: '',
    expiry_date: '',
    status: 'ACTIVE'
  }
  showQualDialog.value = true
}

function editQual(row: any) {
  editingQual.value = true
  qualForm.value = {
    qual_id: row.qual_id,
    qual_type: row.qual_type || '',
    qual_name: row.qual_name || '',
    holder_id: row.holder_id || '',
    issuing_body: row.issuing_body || '',
    certificate_no: row.certificate_no || '',
    issue_date: row.issue_date ? row.issue_date.substring(0, 10) : '',
    expiry_date: row.expiry_date ? row.expiry_date.substring(0, 10) : '',
    status: row.status || 'ACTIVE'
  }
  showQualDialog.value = true
}

async function deleteQual(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.qual_name}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await trainingApi.deleteQualification(row.qual_id)
    ElMessage.success('삭제되었습니다.')
    loadQualifications()
    loadExpiring()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitQual() {
  if (!qualForm.value.qual_type) {
    ElMessage.warning('유형을 입력하세요.')
    return
  }
  if (!qualForm.value.qual_name) {
    ElMessage.warning('자격명을 입력하세요.')
    return
  }

  try {
    const payload = {
      qual_type: qualForm.value.qual_type,
      qual_name: qualForm.value.qual_name,
      holder_id: qualForm.value.holder_id || undefined,
      issuing_body: qualForm.value.issuing_body || undefined,
      certificate_no: qualForm.value.certificate_no || undefined,
      issue_date: qualForm.value.issue_date || undefined,
      expiry_date: qualForm.value.expiry_date || undefined,
      status: qualForm.value.status
    }

    if (qualForm.value.qual_id) {
      await trainingApi.updateQualification(qualForm.value.qual_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await trainingApi.createQualification(payload)
      ElMessage.success('등록되었습니다.')
    }
    showQualDialog.value = false
    editingQual.value = false
    loadQualifications()
    loadExpiring()
  } catch (e) {
    console.warn('자격 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// Audit CRUD
function openAuditDialog() {
  editingAudit.value = false
  auditForm.value = {
    audit_id: null,
    qual_id: null,
    audit_date: '',
    auditor: '',
    result: 'PASS',
    score: null,
    next_audit_date: '',
    remarks: ''
  }
  showAuditDialog.value = true
}

function editAudit(row: any) {
  editingAudit.value = true
  auditForm.value = {
    audit_id: row.audit_id,
    qual_id: row.qual_id,
    audit_date: row.audit_date ? row.audit_date.substring(0, 10) : '',
    auditor: row.auditor || '',
    result: row.result || 'PASS',
    score: row.score ?? null,
    next_audit_date: row.next_audit_date ? row.next_audit_date.substring(0, 10) : '',
    remarks: row.remarks || ''
  }
  showAuditDialog.value = true
}

async function deleteAudit(row: any) {
  try {
    await ElMessageBox.confirm(
      '이 심사기록을 삭제하시겠습니까?',
      '삭제 확인',
      { type: 'warning' }
    )
    await trainingApi.deleteQualAudit(row.audit_id)
    ElMessage.success('삭제되었습니다.')
    loadQualAudits()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitAudit() {
  if (!auditForm.value.qual_id) {
    ElMessage.warning('자격을 선택하세요.')
    return
  }
  if (!auditForm.value.audit_date) {
    ElMessage.warning('심사일을 선택하세요.')
    return
  }
  if (!auditForm.value.result) {
    ElMessage.warning('결과를 선택하세요.')
    return
  }

  try {
    const payload = {
      qual_id: auditForm.value.qual_id,
      audit_date: auditForm.value.audit_date,
      auditor: auditForm.value.auditor || undefined,
      result: auditForm.value.result,
      score: auditForm.value.score ?? undefined,
      next_audit_date: auditForm.value.next_audit_date || undefined,
      remarks: auditForm.value.remarks || undefined
    }

    if (auditForm.value.audit_id) {
      await trainingApi.updateQualAudit(auditForm.value.audit_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await trainingApi.createQualAudit(payload)
      ElMessage.success('등록되었습니다.')
    }
    showAuditDialog.value = false
    editingAudit.value = false
    loadQualAudits()
  } catch (e) {
    console.warn('심사기록 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
</style>
