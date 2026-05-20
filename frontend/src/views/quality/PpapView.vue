<template>
  <div class="page-container">
    <PageHeader title="PPAP (양산부품 승인절차)" subtitle="PPAP 제출 및 관리">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          새 PPAP
        </el-button>
      </template>
    </PageHeader>

    <!-- PPAP List -->
    <div class="card" v-if="!selectedPpap">
      <div class="filter-bar">
        <el-select v-model="filterStatus" placeholder="상태 선택" clearable style="width: 150px;">
          <el-option label="진행중" value="IN_PROGRESS" />
          <el-option label="제출" value="SUBMITTED" />
          <el-option label="승인" value="APPROVED" />
          <el-option label="반려" value="REJECTED" />
        </el-select>
        <el-button type="primary" size="small" @click="loadPpapList">조회</el-button>
      </div>

      <el-table :data="ppapList" border stripe v-loading="loading" @row-click="selectPpap">
        <el-table-column prop="ppap_id" label="ID" width="60" align="center" />
        <el-table-column prop="ppap_no" label="PPAP 번호" width="150" />
        <el-table-column prop="product_name" label="제품" width="130" />
        <el-table-column prop="customer_name" label="고객사" width="130" />
        <el-table-column prop="submission_level" label="Level" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small">Lv.{{ row.submission_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="completeness_pct" label="완료율" width="120" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.completeness_pct || 0" :stroke-width="12" :text-inside="true" style="width: 90px;" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="상태" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getPpapStatusType(row.status)" size="small">{{ getPpapStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="생성일" width="120" align="center" />
        <el-table-column label="작업" width="80" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click.stop="deletePpap(row)">삭제</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- PPAP Detail -->
    <div v-if="selectedPpap">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <el-button link @click="selectedPpap = null">
              <el-icon><Back /></el-icon>
              목록으로
            </el-button>
            <h3 style="margin: 8px 0 0 0;">{{ selectedPpap.ppap_no }} - {{ selectedPpap.product_name }}</h3>
            <p style="margin: 4px 0; color: #6A6D70;">고객사: {{ selectedPpap.customer_name }}</p>
          </div>
        </div>
      </div>

      <!-- Links -->
      <div class="card">
        <div class="card-title">관련 문서 연계</div>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="FMEA">{{ selectedPpap.fmea_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="관리계획서">{{ selectedPpap.cp_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="MSA">{{ selectedPpap.msa_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="APQP">{{ selectedPpap.apqp_id || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Checklist -->
      <div class="card">
        <div class="card-title">PPAP 18개 요소 체크리스트</div>
        <PpapChecklist
          :elements="checklistElements"
          :submission-level="selectedPpap.submission_level"
          @change="handleChecklistChange"
        />
      </div>
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="새 PPAP 생성" width="600px">
      <el-form :model="ppapForm" label-position="top">
        <el-form-item label="PPAP 번호" required>
          <el-input v-model="ppapForm.ppap_no" placeholder="PPAP-2026-001" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="제품 ID" required>
              <el-input v-model="ppapForm.product_id" placeholder="P001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="고객 ID">
              <el-input v-model="ppapForm.customer_id" placeholder="C001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="제출 Level">
          <el-radio-group v-model="ppapForm.submission_level">
            <el-radio-button :value="1">Level 1</el-radio-button>
            <el-radio-button :value="2">Level 2</el-radio-button>
            <el-radio-button :value="3">Level 3</el-radio-button>
            <el-radio-button :value="4">Level 4</el-radio-button>
            <el-radio-button :value="5">Level 5</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="createPpap">생성</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Back } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import PpapChecklist from '@/components/quality/PpapChecklist.vue'
import { ppapApi } from '@/api/quality'

const loading = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)

const ppapList = ref<any[]>([])
const selectedPpap = ref<any>(null)
const checklistElements = ref<any[]>([])

const ppapForm = ref({
  ppap_no: '',
  product_id: '',
  customer_id: '',
  submission_level: 3,
})

function getPpapStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'IN_PROGRESS': return 'warning'
    case 'SUBMITTED': return ''
    case 'APPROVED': return 'success'
    case 'REJECTED': return 'danger'
    default: return 'info'
  }
}

function getPpapStatusLabel(status: string): string {
  switch (status) {
    case 'IN_PROGRESS': return '진행중'
    case 'SUBMITTED': return '제출'
    case 'APPROVED': return '승인'
    case 'REJECTED': return '반려'
    default: return status
  }
}

onMounted(() => {
  loadPpapList()
})

async function loadPpapList() {
  loading.value = true
  try {
    const res = await ppapApi.getList({ status: filterStatus.value || undefined })
    ppapList.value = res.data.items || res.data
  } catch (e) {
    console.warn('PPAP 목록 조회 실패:', e)
    ElMessage.error('PPAP 목록을 불러오는데 실패했습니다')
    ppapList.value = []
  } finally {
    loading.value = false
  }
}

async function selectPpap(row: any) {
  selectedPpap.value = row
  try {
    const res = await ppapApi.getChecklist(row.ppap_id)
    const elements = res.data.elements || res.data || []
    checklistElements.value = Array.isArray(elements) ? elements.map((e: any) => ({
      ...e,
      is_required: e.is_required === 1 || e.is_required === true
    })) : []
  } catch {
    checklistElements.value = []
  }
}

async function handleChecklistChange(element: any) {
  if (!selectedPpap.value || !element.element_id) return
  try {
    await ppapApi.updateChecklistItem(element.element_id, {
      status: element.status,
      document_ref: element.document_ref
    })
  } catch {
    // silent
  }
}

async function deletePpap(row: any) {
  try {
    await ElMessageBox.confirm(`"${row.ppap_no}"을(를) 삭제하시겠습니까?`, '삭제 확인', { type: 'warning' })
    await ppapApi.delete(row.ppap_id)
    ElMessage.success('삭제되었습니다.')
    loadPpapList()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function createPpap() {
  if (!ppapForm.value.ppap_no || !ppapForm.value.product_id) {
    ElMessage.warning('필수항목을 입력하세요.')
    return
  }
  try {
    await ppapApi.create(ppapForm.value)
    ElMessage.success('PPAP가 생성되었습니다.')
    showCreateDialog.value = false
    ppapForm.value = { ppap_no: '', product_id: '', customer_id: '', submission_level: 3 }
    loadPpapList()
  } catch {
    ElMessage.error('생성에 실패했습니다.')
  }
}
</script>
