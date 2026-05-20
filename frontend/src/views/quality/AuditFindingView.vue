<template>
  <div class="page-container">
    <PageHeader title="부적합/관찰 관리" subtitle="심사 발견사항 추적">
      <template #actions>
        <el-button type="primary" @click="openCreateFindingDialog">
          <el-icon><Plus /></el-icon>
          새 발견사항
        </el-button>
      </template>
    </PageHeader>

    <!-- KPI Cards -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <KpiCard title="전체 발견사항" :value="findings.length" color="#0A6ED1" />
      </el-col>
      <el-col :span="6">
        <KpiCard
          title="미결 (OPEN)"
          :value="findings.filter(f => f.status === 'OPEN').length"
          color="#BB0000"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          title="조치필요"
          :value="findings.filter(f => f.status === 'ACTION_REQUIRED').length"
          color="#E78C07"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          title="검증완료"
          :value="findings.filter(f => f.status === 'VERIFIED').length"
          color="#2B7D2B"
        />
      </el-col>
    </el-row>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 전체 발견사항 -->
      <el-tab-pane label="전체 발견사항" name="list">
        <div class="filter-bar">
          <el-select
            v-model="filterType"
            placeholder="유형 선택"
            clearable
            style="width: 180px;"
            @change="loadFindings"
          >
            <el-option label="중부적합" value="MAJOR_NC" />
            <el-option label="경부적합" value="MINOR_NC" />
            <el-option label="관찰" value="OBSERVATION" />
            <el-option label="개선기회" value="OFI" />
          </el-select>
          <el-select
            v-model="filterStatus"
            placeholder="상태 선택"
            clearable
            style="width: 180px;"
            @change="loadFindings"
          >
            <el-option label="미결" value="OPEN" />
            <el-option label="조치필요" value="ACTION_REQUIRED" />
            <el-option label="종결" value="CLOSED" />
            <el-option label="검증완료" value="VERIFIED" />
          </el-select>
        </div>

        <el-table
          :data="findings"
          border
          stripe
          v-loading="loading"
          @row-click="selectFinding"
          style="cursor: pointer;"
        >
          <el-table-column prop="finding_no" label="발견 No." width="140" />
          <el-table-column prop="plan_no" label="연계 심사" width="120" />
          <el-table-column prop="finding_type" label="유형" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getFindingTypeTag(row.finding_type)" size="small">
                {{ getFindingTypeLabel(row.finding_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="clause_ref" label="조항" width="100" />
          <el-table-column prop="description" label="설명" show-overflow-tooltip />
          <el-table-column prop="status" label="상태" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="action_count" label="시정조치" width="90" align="center" />
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editFinding(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deleteFinding(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 상세 -->
      <el-tab-pane label="상세" name="detail">
        <el-empty v-if="!selectedFinding" description="발견사항을 선택하세요" />

        <template v-if="selectedFinding">
          <!-- Finding Header -->
          <div class="finding-detail-header">
            <strong style="font-size: 16px;">{{ selectedFinding.finding_no }}</strong>
            <el-tag :type="getFindingTypeTag(selectedFinding.finding_type)" effect="dark">
              {{ getFindingTypeLabel(selectedFinding.finding_type) }}
            </el-tag>
            <el-tag :type="getStatusTag(selectedFinding.status)">
              {{ getStatusLabel(selectedFinding.status) }}
            </el-tag>
            <span style="color: #6A6D70;">조항: {{ selectedFinding.clause_ref }}</span>
          </div>

          <!-- Description & Evidence -->
          <div class="detail-section">
            <h4 style="margin-bottom: 8px;">설명</h4>
            <div style="white-space: pre-wrap; background: #f5f7fa; padding: 12px; border-radius: 4px;">
              {{ selectedFinding.description || '-' }}
            </div>
          </div>

          <div class="detail-section">
            <h4 style="margin-bottom: 8px;">증거 (Evidence)</h4>
            <div style="white-space: pre-wrap; background: #f5f7fa; padding: 12px; border-radius: 4px;">
              {{ selectedFinding.evidence || '-' }}
            </div>
          </div>

          <!-- 시정조치 Sub-table -->
          <div class="detail-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <h4>시정조치</h4>
              <el-button type="primary" size="small" @click="openActionDialog">
                <el-icon><Plus /></el-icon>
                새 시정조치
              </el-button>
            </div>

            <el-table :data="findingActions" border stripe v-loading="actionsLoading" size="small">
              <el-table-column prop="action_no" label="조치 No." width="120" />
              <el-table-column prop="responsible" label="담당자" width="100" />
              <el-table-column prop="target_date" label="목표일" width="110" align="center" />
              <el-table-column prop="completion_date" label="완료일" width="110" align="center" />
              <el-table-column prop="status" label="상태" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="getActionStatusTag(row.status)" size="small">
                    {{ getActionStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="기한" width="90" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.is_overdue" type="danger" size="small" effect="dark">기한초과</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- Edit Finding Dialog -->
    <el-dialog
      v-model="showFindingDialog"
      :title="isEditing ? '발견사항 수정' : '새 발견사항 등록'"
      width="600px"
    >
      <el-form :model="findingForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="발견 유형" required>
              <el-select v-model="findingForm.finding_type" style="width: 100%;">
                <el-option label="중부적합" value="MAJOR_NC" />
                <el-option label="경부적합" value="MINOR_NC" />
                <el-option label="관찰" value="OBSERVATION" />
                <el-option label="개선기회" value="OFI" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="조항 (Clause)">
              <el-input v-model="findingForm.clause_ref" placeholder="8.5.1" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="설명" required>
          <el-input
            v-model="findingForm.description"
            type="textarea"
            :rows="4"
            placeholder="발견사항 설명을 입력하세요"
          />
        </el-form-item>
        <el-form-item label="증거 (Evidence)">
          <el-input
            v-model="findingForm.evidence"
            type="textarea"
            :rows="3"
            placeholder="관련 증거를 입력하세요"
          />
        </el-form-item>
        <el-form-item label="상태">
          <el-select v-model="findingForm.status" style="width: 100%;">
            <el-option label="미결" value="OPEN" />
            <el-option label="조치필요" value="ACTION_REQUIRED" />
            <el-option label="종결" value="CLOSED" />
            <el-option label="검증완료" value="VERIFIED" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFindingDialog = false">취소</el-button>
        <el-button type="primary" @click="submitFinding">저장</el-button>
      </template>
    </el-dialog>

    <!-- Action Create Dialog -->
    <el-dialog
      v-model="showActionDialog"
      title="새 시정조치 등록"
      width="600px"
    >
      <el-form :model="actionForm" label-position="top">
        <el-form-item label="조치 No." required>
          <el-input v-model="actionForm.action_no" placeholder="CA-001" />
        </el-form-item>
        <el-form-item label="근본 원인 (Root Cause)">
          <el-input
            v-model="actionForm.root_cause"
            type="textarea"
            :rows="3"
            placeholder="근본 원인 분석 결과를 입력하세요"
          />
        </el-form-item>
        <el-form-item label="즉시 조치 (Containment Action)">
          <el-input
            v-model="actionForm.containment_action"
            type="textarea"
            :rows="2"
            placeholder="즉시 조치 내용"
          />
        </el-form-item>
        <el-form-item label="시정 조치 (Corrective Action)">
          <el-input
            v-model="actionForm.corrective_action"
            type="textarea"
            :rows="3"
            placeholder="시정 조치 내용"
          />
        </el-form-item>
        <el-form-item label="예방 조치 (Preventive Action)">
          <el-input
            v-model="actionForm.preventive_action"
            type="textarea"
            :rows="2"
            placeholder="예방 조치 내용"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="담당자" required>
              <el-input v-model="actionForm.responsible" placeholder="담당자 이름" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="목표일" required>
              <el-date-picker
                v-model="actionForm.target_date"
                type="date"
                placeholder="목표 완료일"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showActionDialog = false">취소</el-button>
        <el-button type="primary" @click="submitAction">저장</el-button>
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

const loading = ref(false)
const actionsLoading = ref(false)
const activeTab = ref('list')
const showFindingDialog = ref(false)
const showActionDialog = ref(false)
const isEditing = ref(false)

const filterType = ref('')
const filterStatus = ref('')

const findings = ref<any[]>([])
const selectedFinding = ref<any>(null)
const findingActions = ref<any[]>([])

const findingForm = ref({
  finding_id: null as number | null,
  finding_type: '',
  clause_ref: '',
  description: '',
  evidence: '',
  status: 'OPEN'
})

const actionForm = ref({
  action_no: '',
  root_cause: '',
  containment_action: '',
  corrective_action: '',
  preventive_action: '',
  responsible: '',
  target_date: ''
})

// --- Tag helpers ---

function getFindingTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (type) {
    case 'MAJOR_NC': return 'danger'
    case 'MINOR_NC': return 'warning'
    case 'OBSERVATION': return 'info'
    case 'OFI': return ''
    default: return 'info'
  }
}

function getFindingTypeLabel(type: string): string {
  switch (type) {
    case 'MAJOR_NC': return '중부적합'
    case 'MINOR_NC': return '경부적합'
    case 'OBSERVATION': return '관찰'
    case 'OFI': return '개선기회'
    default: return type
  }
}

function getStatusTag(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'danger'
    case 'ACTION_REQUIRED': return 'warning'
    case 'CLOSED': return 'info'
    case 'VERIFIED': return 'success'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'OPEN': return '미결'
    case 'ACTION_REQUIRED': return '조치필요'
    case 'CLOSED': return '종결'
    case 'VERIFIED': return '검증완료'
    default: return status
  }
}

function getActionStatusTag(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'danger'
    case 'IN_PROGRESS': return 'warning'
    case 'COMPLETED': return 'info'
    case 'VERIFIED': return 'success'
    default: return 'info'
  }
}

function getActionStatusLabel(status: string): string {
  switch (status) {
    case 'OPEN': return '미결'
    case 'IN_PROGRESS': return '진행중'
    case 'COMPLETED': return '완료'
    case 'VERIFIED': return '검증완료'
    default: return status
  }
}

// --- Data loading ---

onMounted(() => {
  loadFindings()
})

async function loadFindings() {
  loading.value = true
  try {
    const params: any = {}
    if (filterType.value) params.finding_type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await auditApi.getFindings(params)
    findings.value = res.data.items || res.data
  } catch (e) {
    console.warn('발견사항 목록 조회 실패:', e)
    ElMessage.error('발견사항 목록을 불러오는데 실패했습니다')
    findings.value = []
  } finally {
    loading.value = false
  }
}

async function selectFinding(row: any) {
  try {
    const res = await auditApi.getFinding(row.finding_id)
    selectedFinding.value = res.data
    activeTab.value = 'detail'
    loadFindingActions()
  } catch (e) {
    console.warn('발견사항 상세 조회 실패:', e)
    ElMessage.error('발견사항 상세 정보를 불러오는데 실패했습니다')
  }
}

async function loadFindingActions() {
  if (!selectedFinding.value) return
  actionsLoading.value = true
  try {
    const res = await auditApi.getFindingActions(selectedFinding.value.finding_id)
    findingActions.value = res.data.items || res.data
  } catch (e) {
    console.warn('시정조치 목록 조회 실패:', e)
    ElMessage.error('시정조치 목록을 불러오는데 실패했습니다')
    findingActions.value = []
  } finally {
    actionsLoading.value = false
  }
}

// --- Finding CRUD ---

function openCreateFindingDialog() {
  isEditing.value = false
  findingForm.value = {
    finding_id: null,
    finding_type: '',
    clause_ref: '',
    description: '',
    evidence: '',
    status: 'OPEN'
  }
  showFindingDialog.value = true
}

function editFinding(row: any) {
  isEditing.value = true
  findingForm.value = {
    finding_id: row.finding_id,
    finding_type: row.finding_type || '',
    clause_ref: row.clause_ref || '',
    description: row.description || '',
    evidence: row.evidence || '',
    status: row.status || 'OPEN'
  }
  showFindingDialog.value = true
}

async function deleteFinding(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.finding_no}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await auditApi.deleteFinding(row.finding_id)
    ElMessage.success('삭제되었습니다.')
    if (selectedFinding.value?.finding_id === row.finding_id) {
      selectedFinding.value = null
      findingActions.value = []
    }
    loadFindings()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitFinding() {
  if (!findingForm.value.finding_type) {
    ElMessage.warning('발견 유형을 선택하세요.')
    return
  }
  if (!findingForm.value.description) {
    ElMessage.warning('설명을 입력하세요.')
    return
  }

  try {
    const payload = {
      finding_type: findingForm.value.finding_type,
      clause_ref: findingForm.value.clause_ref || undefined,
      description: findingForm.value.description,
      evidence: findingForm.value.evidence || undefined,
      status: findingForm.value.status
    }

    if (findingForm.value.finding_id) {
      await auditApi.updateFinding(findingForm.value.finding_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await auditApi.createFinding(0, payload)
      ElMessage.success('생성되었습니다.')
    }
    showFindingDialog.value = false
    isEditing.value = false
    loadFindings()
  } catch (e) {
    console.warn('발견사항 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// --- Action CRUD ---

function openActionDialog() {
  actionForm.value = {
    action_no: '',
    root_cause: '',
    containment_action: '',
    corrective_action: '',
    preventive_action: '',
    responsible: '',
    target_date: ''
  }
  showActionDialog.value = true
}

async function submitAction() {
  if (!actionForm.value.action_no) {
    ElMessage.warning('조치 No.를 입력하세요.')
    return
  }
  if (!actionForm.value.responsible) {
    ElMessage.warning('담당자를 입력하세요.')
    return
  }
  if (!actionForm.value.target_date) {
    ElMessage.warning('목표일을 선택하세요.')
    return
  }
  if (!selectedFinding.value) return

  try {
    const payload = {
      action_no: actionForm.value.action_no,
      root_cause: actionForm.value.root_cause || undefined,
      containment_action: actionForm.value.containment_action || undefined,
      corrective_action: actionForm.value.corrective_action || undefined,
      preventive_action: actionForm.value.preventive_action || undefined,
      responsible: actionForm.value.responsible,
      target_date: actionForm.value.target_date
    }

    await auditApi.createAction(selectedFinding.value.finding_id, payload)
    ElMessage.success('시정조치가 등록되었습니다.')
    showActionDialog.value = false
    loadFindingActions()
  } catch (e) {
    console.warn('시정조치 등록 실패:', e)
    ElMessage.error('시정조치 등록에 실패했습니다.')
  }
}
</script>

<style scoped>
.finding-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--qms-border, #e4e7ed);
}

.detail-section {
  margin-bottom: 20px;
}
</style>
