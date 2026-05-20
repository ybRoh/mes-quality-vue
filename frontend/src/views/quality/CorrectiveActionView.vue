<template>
  <div class="page-container">
    <PageHeader title="시정조치 관리" subtitle="부적합 시정조치 현황 및 추적">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 시정조치
        </el-button>
      </template>
    </PageHeader>

    <!-- KPI Cards -->
    <div class="kpi-row">
      <KpiCard title="총 시정조치" :value="kpiData.total" color="#0A6ED1" />
      <KpiCard title="진행중" :value="kpiData.inProgress" color="#E9730C" />
      <KpiCard title="완료/검증" :value="kpiData.completed" color="#107E3E" />
      <KpiCard title="기한초과" :value="kpiData.overdue" color="#BB0000" />
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 시정조치 현황 -->
      <el-tab-pane label="시정조치 현황" name="list">
        <div class="filter-bar">
          <el-select
            v-model="filterStatus"
            placeholder="상태 선택"
            clearable
            style="width: 160px;"
            @change="loadActions"
          >
            <el-option label="미결" value="OPEN" />
            <el-option label="진행중" value="IN_PROGRESS" />
            <el-option label="완료" value="COMPLETED" />
            <el-option label="검증" value="VERIFIED" />
          </el-select>
          <el-checkbox v-model="overdueOnly" @change="loadActions">기한초과만</el-checkbox>
        </div>

        <el-table
          :data="actionList"
          border
          stripe
          v-loading="loading"
          @row-click="selectAction"
          style="cursor: pointer;"
        >
          <el-table-column prop="action_no" label="조치 No." width="140" />
          <el-table-column prop="finding_no" label="연계" width="120" />
          <el-table-column prop="responsible" label="담당자" width="100" />
          <el-table-column prop="target_date" label="목표일" width="110" align="center">
            <template #default="{ row }">
              <span :style="{ color: row.is_overdue ? '#BB0000' : 'inherit', fontWeight: row.is_overdue ? '600' : 'normal' }">
                {{ row.target_date }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="completion_date" label="완료일" width="110" align="center" />
          <el-table-column prop="status" label="상태" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" size="small">
                {{ statusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="기한" width="80" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_overdue" type="danger" size="small">초과</el-tag>
              <el-tag v-else type="success" size="small">정상</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="작업" width="150" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editAction(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deleteAction(row)">삭제</el-button>
              <el-button
                v-if="row.status === 'COMPLETED'"
                type="success"
                link
                size="small"
                @click.stop="verifyAction(row)"
              >
                검증
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 조치상세 -->
      <el-tab-pane label="조치상세" name="detail">
        <el-empty v-if="!selectedAction" description="시정조치를 선택하세요" />

        <div v-else>
          <!-- Action Header -->
          <div class="action-detail-header">
            <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
              <h3 style="margin: 0;">{{ selectedAction.action_no }}</h3>
              <el-tag :type="statusTagType(selectedAction.status)" effect="dark">
                {{ statusLabel(selectedAction.status) }}
              </el-tag>
              <span style="color: #666;">담당: {{ selectedAction.responsible }}</span>
              <span
                :style="{
                  color: selectedAction.is_overdue ? '#BB0000' : '#666',
                  fontWeight: selectedAction.is_overdue ? '600' : 'normal'
                }"
              >
                목표일: {{ selectedAction.target_date }}
              </span>
            </div>
            <el-button type="primary" size="small" @click="editAction(selectedAction)">편집</el-button>
          </div>

          <!-- Detail Sections -->
          <div class="detail-section">
            <div class="detail-label">원인분석</div>
            <div class="detail-content">{{ selectedAction.root_cause || '-' }}</div>
          </div>

          <div class="detail-section">
            <div class="detail-label">긴급조치</div>
            <div class="detail-content">{{ selectedAction.containment_action || '-' }}</div>
          </div>

          <div class="detail-section">
            <div class="detail-label">시정조치</div>
            <div class="detail-content">{{ selectedAction.corrective_action || '-' }}</div>
          </div>

          <div class="detail-section">
            <div class="detail-label">예방조치</div>
            <div class="detail-content">{{ selectedAction.preventive_action || '-' }}</div>
          </div>

          <div class="detail-section">
            <div class="detail-label">검증정보</div>
            <div class="detail-content">
              <span v-if="selectedAction.verified_by">
                검증자: {{ selectedAction.verified_by }} | 검증일: {{ selectedAction.verified_date || '-' }}
              </span>
              <span v-else>미검증</span>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Edit/Create Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '시정조치 수정' : '새 시정조치 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-form-item label="원인분석">
          <el-input
            v-model="formData.root_cause"
            type="textarea"
            :rows="3"
            placeholder="원인분석 내용을 입력하세요"
          />
        </el-form-item>
        <el-form-item label="긴급조치">
          <el-input
            v-model="formData.containment_action"
            type="textarea"
            :rows="3"
            placeholder="긴급조치 내용을 입력하세요"
          />
        </el-form-item>
        <el-form-item label="시정조치">
          <el-input
            v-model="formData.corrective_action"
            type="textarea"
            :rows="3"
            placeholder="시정조치 내용을 입력하세요"
          />
        </el-form-item>
        <el-form-item label="예방조치">
          <el-input
            v-model="formData.preventive_action"
            type="textarea"
            :rows="3"
            placeholder="예방조치 내용을 입력하세요"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="담당자">
              <el-input v-model="formData.responsible" placeholder="담당자 이름" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="상태">
              <el-select v-model="formData.status" style="width: 100%;">
                <el-option label="미결" value="OPEN" />
                <el-option label="진행중" value="IN_PROGRESS" />
                <el-option label="완료" value="COMPLETED" />
                <el-option label="검증" value="VERIFIED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="목표일">
              <el-date-picker
                v-model="formData.target_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="목표일 선택"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="완료일">
              <el-date-picker
                v-model="formData.completion_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="완료일 선택"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">취소</el-button>
        <el-button type="primary" @click="submitAction">저장</el-button>
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
import { auditApi } from '@/api/quality'

const loading = ref(false)
const activeTab = ref('list')
const showDialog = ref(false)
const isEditing = ref(false)

const filterStatus = ref('')
const overdueOnly = ref(false)

const actionList = ref<any[]>([])
const totalCount = ref(0)
const selectedAction = ref<any>(null)

const formData = ref({
  action_id: null as number | null,
  finding_id: null as number | null,
  root_cause: '',
  containment_action: '',
  corrective_action: '',
  preventive_action: '',
  responsible: '',
  target_date: '',
  completion_date: '',
  status: 'OPEN'
})

// KPI Computation
const kpiData = computed(() => {
  const list = actionList.value
  return {
    total: list.length || totalCount.value,
    inProgress: list.filter(a => a.status === 'IN_PROGRESS' || a.status === 'OPEN').length,
    completed: list.filter(a => a.status === 'COMPLETED' || a.status === 'VERIFIED').length,
    overdue: list.filter(a => a.is_overdue).length
  }
})

// Status helpers
function statusTagType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'danger'
    case 'IN_PROGRESS': return 'warning'
    case 'COMPLETED': return 'success'
    case 'VERIFIED': return 'success'
    default: return 'info'
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case 'OPEN': return '미결'
    case 'IN_PROGRESS': return '진행중'
    case 'COMPLETED': return '완료'
    case 'VERIFIED': return '검증'
    default: return status
  }
}

onMounted(() => {
  loadActions()
})

async function loadActions() {
  loading.value = true
  try {
    const params: any = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (overdueOnly.value) params.overdue_only = true
    const res = await auditApi.getActions(params)
    actionList.value = res.data.items || res.data
    totalCount.value = res.data.total || actionList.value.length
  } catch (e) {
    console.warn('시정조치 목록 조회 실패:', e)
    ElMessage.error('시정조치 목록을 불러오는데 실패했습니다')
    actionList.value = []
  } finally {
    loading.value = false
  }
}

function selectAction(row: any) {
  selectedAction.value = row
  activeTab.value = 'detail'
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    action_id: null,
    finding_id: null,
    root_cause: '',
    containment_action: '',
    corrective_action: '',
    preventive_action: '',
    responsible: '',
    target_date: '',
    completion_date: '',
    status: 'OPEN'
  }
  showDialog.value = true
}

function editAction(row: any) {
  isEditing.value = true
  formData.value = {
    action_id: row.action_id,
    finding_id: row.finding_id || null,
    root_cause: row.root_cause || '',
    containment_action: row.containment_action || '',
    corrective_action: row.corrective_action || '',
    preventive_action: row.preventive_action || '',
    responsible: row.responsible || '',
    target_date: row.target_date || '',
    completion_date: row.completion_date || '',
    status: row.status || 'OPEN'
  }
  showDialog.value = true
}

async function deleteAction(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.action_no}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await auditApi.deleteAction(row.action_id)
    ElMessage.success('삭제되었습니다.')
    if (selectedAction.value?.action_id === row.action_id) {
      selectedAction.value = null
    }
    loadActions()
  } catch {
    // cancelled or error
  }
}

async function submitAction() {
  try {
    const payload: any = {
      root_cause: formData.value.root_cause || undefined,
      containment_action: formData.value.containment_action || undefined,
      corrective_action: formData.value.corrective_action || undefined,
      preventive_action: formData.value.preventive_action || undefined,
      responsible: formData.value.responsible || undefined,
      target_date: formData.value.target_date || undefined,
      completion_date: formData.value.completion_date || undefined,
      status: formData.value.status
    }

    if (formData.value.action_id) {
      const res = await auditApi.updateAction(formData.value.action_id, payload)
      ElMessage.success('수정되었습니다.')
      // Update selected action if viewing it
      if (selectedAction.value?.action_id === formData.value.action_id) {
        selectedAction.value = res.data
      }
    } else {
      if (!formData.value.finding_id) {
        ElMessage.warning('연계할 발견사항을 선택해야 합니다.')
        return
      }
      await auditApi.createAction(formData.value.finding_id, payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    loadActions()
  } catch (e) {
    console.warn('시정조치 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

async function verifyAction(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.action_no}" 시정조치를 검증 완료 처리하시겠습니까?`,
      '검증 확인',
      { type: 'info', confirmButtonText: '검증 완료', cancelButtonText: '취소' }
    )
    const res = await auditApi.verifyAction(row.action_id)
    ElMessage.success('검증 완료 처리되었습니다.')
    // Update selected action if viewing it
    if (selectedAction.value?.action_id === row.action_id) {
      selectedAction.value = res.data
    }
    loadActions()
  } catch (e) {
    // cancelled or error - only show error if it was an API failure
    if (e !== 'cancel' && (e as any) !== 'cancel') {
      const err = e as any
      if (err?.response || err?.message) {
        console.warn('검증 처리 실패:', e)
        ElMessage.error('검증 처리에 실패했습니다.')
      }
    }
  }
}
</script>

<style scoped>
.kpi-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.kpi-row > * {
  flex: 1;
  min-width: 180px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.action-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-label {
  font-weight: 600;
  margin-bottom: 4px;
  color: #666;
}

.detail-content {
  white-space: pre-wrap;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 4px;
  min-height: 40px;
}
</style>
