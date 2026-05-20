<template>
  <div class="page-container">
    <PageHeader title="고객심사 관리" subtitle="고객(SQ) 심사 이력 관리">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 고객심사
        </el-button>
      </template>
    </PageHeader>

    <!-- KPI Cards -->
    <div class="kpi-row">
      <KpiCard title="총 심사" :value="kpiData.total" color="#0A6ED1" />
      <KpiCard title="합격" :value="kpiData.pass" color="#107E3E" />
      <KpiCard title="조건부" :value="kpiData.conditional" color="#E9730C" />
      <KpiCard title="불합격" :value="kpiData.fail" color="#BB0000" />
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <el-input
        v-model="filterCustomerId"
        placeholder="고객 ID"
        clearable
        style="width: 160px;"
        @change="loadList"
      />
      <el-select
        v-model="filterAuditType"
        placeholder="심사유형"
        clearable
        style="width: 160px;"
        @change="loadList"
      >
        <el-option label="SQ" value="SQ" />
        <el-option label="공정심사" value="PROCESS" />
        <el-option label="제품심사" value="PRODUCT" />
        <el-option label="시스템심사" value="SYSTEM" />
      </el-select>
      <el-select
        v-model="filterStatus"
        placeholder="상태"
        clearable
        style="width: 140px;"
        @change="loadList"
      >
        <el-option label="예정" value="SCHEDULED" />
        <el-option label="진행중" value="IN_PROGRESS" />
        <el-option label="완료" value="COMPLETED" />
        <el-option label="종결" value="CLOSED" />
      </el-select>
      <el-select
        v-model="filterResult"
        placeholder="결과"
        clearable
        style="width: 140px;"
        @change="loadList"
      >
        <el-option label="대기" value="PENDING" />
        <el-option label="합격" value="PASS" />
        <el-option label="조건부" value="CONDITIONAL" />
        <el-option label="불합격" value="FAIL" />
      </el-select>
    </div>

    <!-- Audit table -->
    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column prop="audit_no" label="심사번호" width="140" />
      <el-table-column prop="customer_id" label="고객 ID" width="120" />
      <el-table-column prop="audit_type" label="심사유형" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="auditTypeTag(row.audit_type)" size="small">
            {{ auditTypeLabel(row.audit_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="audit_date" label="심사일" width="110" align="center" />
      <el-table-column prop="auditor_name" label="심사원" width="100" />
      <el-table-column prop="result" label="결과" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="resultTag(row.result)" size="small">
            {{ resultLabel(row.result) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="score" label="점수" width="80" align="center">
        <template #default="{ row }">
          {{ row.score != null ? row.score : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="상태" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="finding_count" label="발견사항" width="90" align="center" />
      <el-table-column label="작업" width="120" align="center" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="editItem(row)">편집</el-button>
          <el-button type="danger" link size="small" @click="deleteItem(row)">삭제</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '고객심사 수정' : '새 고객심사 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="심사번호" required>
              <el-input v-model="formData.audit_no" placeholder="CA-2026-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="고객 ID">
              <el-input v-model="formData.customer_id" placeholder="고객 ID" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="심사유형">
              <el-select v-model="formData.audit_type" style="width: 100%;">
                <el-option label="SQ" value="SQ" />
                <el-option label="공정심사" value="PROCESS" />
                <el-option label="제품심사" value="PRODUCT" />
                <el-option label="시스템심사" value="SYSTEM" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="심사원">
              <el-input v-model="formData.auditor_name" placeholder="심사원명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="심사 시작일">
              <el-date-picker
                v-model="formData.audit_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="시작일 선택"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="심사 종료일">
              <el-date-picker
                v-model="formData.audit_end_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="종료일 선택"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="결과">
              <el-select v-model="formData.result" style="width: 100%;">
                <el-option label="대기" value="PENDING" />
                <el-option label="합격" value="PASS" />
                <el-option label="조건부" value="CONDITIONAL" />
                <el-option label="불합격" value="FAIL" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="점수">
              <el-input-number v-model="formData.score" :min="0" :max="100" :precision="1" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="상태">
              <el-select v-model="formData.status" style="width: 100%;">
                <el-option label="예정" value="SCHEDULED" />
                <el-option label="진행중" value="IN_PROGRESS" />
                <el-option label="완료" value="COMPLETED" />
                <el-option label="종결" value="CLOSED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="심사 범위">
          <el-input
            v-model="formData.scope"
            type="textarea"
            :rows="3"
            placeholder="심사 범위를 입력하세요"
          />
        </el-form-item>
        <el-form-item label="비고">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="2"
            placeholder="비고 사항"
          />
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
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import { customerAuditApi } from '@/api/quality'

const loading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)

const filterCustomerId = ref('')
const filterAuditType = ref('')
const filterStatus = ref('')
const filterResult = ref('')

const tableData = ref<any[]>([])
const totalCount = ref(0)

const formData = ref({
  cust_audit_id: null as number | null,
  audit_no: '',
  customer_id: '',
  audit_type: 'SQ',
  audit_date: '',
  audit_end_date: '',
  auditor_name: '',
  scope: '',
  result: 'PENDING',
  score: null as number | null,
  status: 'SCHEDULED',
  remarks: ''
})

// KPI computation
const kpiData = computed(() => {
  const list = tableData.value
  return {
    total: totalCount.value || list.length,
    pass: list.filter(a => a.result === 'PASS').length,
    conditional: list.filter(a => a.result === 'CONDITIONAL').length,
    fail: list.filter(a => a.result === 'FAIL').length
  }
})

// Tag helpers
function auditTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (type) {
    case 'SQ': return ''
    case 'PROCESS': return 'warning'
    case 'PRODUCT': return 'success'
    case 'SYSTEM': return 'info'
    default: return 'info'
  }
}

function auditTypeLabel(type: string): string {
  switch (type) {
    case 'SQ': return 'SQ'
    case 'PROCESS': return '공정심사'
    case 'PRODUCT': return '제품심사'
    case 'SYSTEM': return '시스템심사'
    default: return type || '-'
  }
}

function resultTag(result: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (result) {
    case 'PASS': return 'success'
    case 'CONDITIONAL': return 'warning'
    case 'FAIL': return 'danger'
    case 'PENDING': return 'info'
    default: return 'info'
  }
}

function resultLabel(result: string): string {
  switch (result) {
    case 'PASS': return '합격'
    case 'CONDITIONAL': return '조건부'
    case 'FAIL': return '불합격'
    case 'PENDING': return '대기'
    default: return result || '-'
  }
}

function statusTag(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'SCHEDULED': return 'info'
    case 'IN_PROGRESS': return 'warning'
    case 'COMPLETED': return 'success'
    case 'CLOSED': return ''
    default: return 'info'
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case 'SCHEDULED': return '예정'
    case 'IN_PROGRESS': return '진행중'
    case 'COMPLETED': return '완료'
    case 'CLOSED': return '종결'
    default: return status || '-'
  }
}

onMounted(() => {
  loadList()
})

async function loadList() {
  loading.value = true
  try {
    const params: any = {}
    if (filterCustomerId.value) params.customer_id = filterCustomerId.value
    if (filterAuditType.value) params.audit_type = filterAuditType.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterResult.value) params.result = filterResult.value
    const res = await customerAuditApi.getList(params)
    tableData.value = res.data.items || res.data
    totalCount.value = res.data.total || tableData.value.length
  } catch (e) {
    console.warn('고객심사 목록 조회 실패:', e)
    ElMessage.error('고객심사 목록을 불러오는데 실패했습니다')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    cust_audit_id: null,
    audit_no: '',
    customer_id: '',
    audit_type: 'SQ',
    audit_date: '',
    audit_end_date: '',
    auditor_name: '',
    scope: '',
    result: 'PENDING',
    score: null,
    status: 'SCHEDULED',
    remarks: ''
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    cust_audit_id: row.cust_audit_id,
    audit_no: row.audit_no || '',
    customer_id: row.customer_id || '',
    audit_type: row.audit_type || 'SQ',
    audit_date: row.audit_date || '',
    audit_end_date: row.audit_end_date || '',
    auditor_name: row.auditor_name || '',
    scope: row.scope || '',
    result: row.result || 'PENDING',
    score: row.score ?? null,
    status: row.status || 'SCHEDULED',
    remarks: row.remarks || ''
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.audit_no}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await customerAuditApi.delete(row.cust_audit_id)
    ElMessage.success('삭제되었습니다.')
    loadList()
  } catch {
    // cancelled or error
  }
}

async function submitForm() {
  if (!formData.value.audit_no) {
    ElMessage.warning('심사번호를 입력하세요.')
    return
  }

  try {
    const payload: any = {
      audit_no: formData.value.audit_no,
      customer_id: formData.value.customer_id || undefined,
      audit_type: formData.value.audit_type,
      audit_date: formData.value.audit_date || undefined,
      audit_end_date: formData.value.audit_end_date || undefined,
      auditor_name: formData.value.auditor_name || undefined,
      scope: formData.value.scope || undefined,
      result: formData.value.result,
      score: formData.value.score ?? undefined,
      status: formData.value.status,
      remarks: formData.value.remarks || undefined
    }

    if (formData.value.cust_audit_id) {
      await customerAuditApi.update(formData.value.cust_audit_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await customerAuditApi.create(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('고객심사 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
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
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}
</style>
