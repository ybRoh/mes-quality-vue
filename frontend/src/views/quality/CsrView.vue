<template>
  <div class="page-container">
    <PageHeader title="고객 특별요구사항 (CSR)" subtitle="Customer Specific Requirements 관리">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 CSR
        </el-button>
      </template>
    </PageHeader>

    <!-- KPI Cards -->
    <div class="kpi-row">
      <KpiCard title="총 건수" :value="kpi.total" unit="건" color="#0A6ED1" />
      <KpiCard title="COMPLIANT" :value="kpi.compliant" unit="건" color="#107E3E" />
      <KpiCard title="PENDING" :value="kpi.pending" unit="건" color="#E9730C" />
      <KpiCard title="NON_COMPLIANT" :value="kpi.nonCompliant" unit="건" color="#BB0000" />
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
        v-model="filterComplianceStatus"
        placeholder="준수상태"
        clearable
        style="width: 180px;"
        @change="loadList"
      >
        <el-option label="준수" value="COMPLIANT" />
        <el-option label="대기" value="PENDING" />
        <el-option label="미준수" value="NON_COMPLIANT" />
        <el-option label="해당없음" value="NA" />
      </el-select>
      <el-select
        v-model="filterCategory"
        placeholder="카테고리"
        clearable
        style="width: 140px;"
        @change="loadList"
      >
        <el-option label="품질" value="품질" />
        <el-option label="포장" value="포장" />
        <el-option label="물류" value="물류" />
        <el-option label="환경" value="환경" />
      </el-select>
    </div>

    <!-- CSR table -->
    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column prop="csr_no" label="CSR No." width="130" />
      <el-table-column prop="customer_id" label="고객" width="100" />
      <el-table-column prop="requirement" label="요구사항" show-overflow-tooltip />
      <el-table-column prop="category" label="카테고리" width="90" align="center" />
      <el-table-column prop="iatf_clause" label="IATF 조항" width="100" />
      <el-table-column prop="compliance_status" label="준수상태" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="getComplianceTag(row.compliance_status)" size="small">
            {{ getComplianceLabel(row.compliance_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="responsible" label="담당자" width="100" />
      <el-table-column prop="target_date" label="목표일" width="110" align="center" />
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
      :title="isEditing ? 'CSR 수정' : '새 CSR 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="CSR No." required>
              <el-input v-model="formData.csr_no" placeholder="CSR-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="고객 ID">
              <el-input v-model="formData.customer_id" placeholder="C001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="요구사항" required>
          <el-input
            v-model="formData.requirement"
            type="textarea"
            :rows="3"
            placeholder="고객 요구사항을 입력하세요"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="카테고리">
              <el-select v-model="formData.category" placeholder="선택" clearable style="width: 100%;">
                <el-option label="품질" value="품질" />
                <el-option label="포장" value="포장" />
                <el-option label="물류" value="물류" />
                <el-option label="환경" value="환경" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="IATF 조항">
              <el-input v-model="formData.iatf_clause" placeholder="8.5.1" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="준수상태">
              <el-select v-model="formData.compliance_status" style="width: 100%;">
                <el-option label="준수" value="COMPLIANT" />
                <el-option label="대기" value="PENDING" />
                <el-option label="미준수" value="NON_COMPLIANT" />
                <el-option label="해당없음" value="NA" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="담당자">
              <el-input v-model="formData.responsible" placeholder="담당자명" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="목표일">
              <el-date-picker
                v-model="formData.target_date"
                type="date"
                placeholder="목표일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="완료일">
              <el-date-picker
                v-model="formData.completion_date"
                type="date"
                placeholder="완료일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="증빙자료">
          <el-input
            v-model="formData.evidence"
            type="textarea"
            :rows="2"
            placeholder="증빙자료 또는 참조문서를 기술하세요"
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
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import { specificationApi } from '@/api/quality'

const loading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)

// --- Filter state ---
const filterCustomerId = ref('')
const filterComplianceStatus = ref('')
const filterCategory = ref('')

// --- Data ---
const tableData = ref<any[]>([])
const kpi = ref({
  total: 0,
  compliant: 0,
  pending: 0,
  nonCompliant: 0
})

const formData = ref({
  csr_id: null as number | null,
  csr_no: '',
  customer_id: '',
  requirement: '',
  category: '',
  iatf_clause: '',
  compliance_status: 'PENDING',
  responsible: '',
  target_date: '',
  completion_date: '',
  evidence: ''
})

// --- Label / Tag helpers ---
function getComplianceLabel(status: string): string {
  switch (status) {
    case 'COMPLIANT': return '준수'
    case 'PENDING': return '대기'
    case 'NON_COMPLIANT': return '미준수'
    case 'NA': return '해당없음'
    default: return status || '-'
  }
}

function getComplianceTag(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'COMPLIANT': return 'success'
    case 'PENDING': return 'warning'
    case 'NON_COMPLIANT': return 'danger'
    case 'NA': return 'info'
    default: return 'info'
  }
}

// --- Lifecycle ---
onMounted(() => {
  loadList()
})

// --- CSR CRUD ---
async function loadList() {
  loading.value = true
  try {
    const res = await specificationApi.getCsr({
      customer_id: filterCustomerId.value || undefined,
      compliance_status: filterComplianceStatus.value || undefined,
      category: filterCategory.value || undefined
    })
    tableData.value = res.data.items || res.data
    computeKpi()
  } catch (e) {
    console.warn('CSR 목록 조회 실패:', e)
    ElMessage.error('CSR 목록을 불러오는데 실패했습니다')
    tableData.value = []
    kpi.value = { total: 0, compliant: 0, pending: 0, nonCompliant: 0 }
  } finally {
    loading.value = false
  }
}

function computeKpi() {
  const data = tableData.value
  kpi.value = {
    total: data.length,
    compliant: data.filter((d: any) => d.compliance_status === 'COMPLIANT').length,
    pending: data.filter((d: any) => d.compliance_status === 'PENDING').length,
    nonCompliant: data.filter((d: any) => d.compliance_status === 'NON_COMPLIANT').length
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    csr_id: null,
    csr_no: '',
    customer_id: '',
    requirement: '',
    category: '',
    iatf_clause: '',
    compliance_status: 'PENDING',
    responsible: '',
    target_date: '',
    completion_date: '',
    evidence: ''
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    csr_id: row.csr_id,
    csr_no: row.csr_no || '',
    customer_id: row.customer_id || '',
    requirement: row.requirement || '',
    category: row.category || '',
    iatf_clause: row.iatf_clause || '',
    compliance_status: row.compliance_status || 'PENDING',
    responsible: row.responsible || '',
    target_date: row.target_date || '',
    completion_date: row.completion_date || '',
    evidence: row.evidence || ''
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.csr_no}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await specificationApi.deleteCsr(row.csr_id)
    ElMessage.success('삭제되었습니다.')
    loadList()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitForm() {
  if (!formData.value.csr_no) {
    ElMessage.warning('CSR No.를 입력하세요.')
    return
  }
  if (!formData.value.requirement) {
    ElMessage.warning('요구사항을 입력하세요.')
    return
  }

  try {
    const payload: any = {
      csr_no: formData.value.csr_no,
      customer_id: formData.value.customer_id || undefined,
      requirement: formData.value.requirement,
      category: formData.value.category || undefined,
      iatf_clause: formData.value.iatf_clause || undefined,
      compliance_status: formData.value.compliance_status,
      responsible: formData.value.responsible || undefined,
      target_date: formData.value.target_date || undefined,
      evidence: formData.value.evidence || undefined
    }

    if (isEditing.value) {
      payload.completion_date = formData.value.completion_date || undefined
    }

    if (formData.value.csr_id) {
      await specificationApi.updateCsr(formData.value.csr_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await specificationApi.createCsr(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('CSR 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
</style>
