<template>
  <div class="page-container">
    <PageHeader title="FMEA (고장모드 영향분석)" :subtitle="fmeaTypeLabel + ' 관리'">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 FMEA
        </el-button>
      </template>
    </PageHeader>

    <!-- DFMEA / PFMEA 전환 -->
    <div class="type-selector">
      <el-radio-group v-model="fmeaType" size="default" @change="onTypeChange">
        <el-radio-button value="DESIGN">DFMEA (설계)</el-radio-button>
        <el-radio-button value="PROCESS">PFMEA (공정)</el-radio-button>
      </el-radio-group>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: FMEA 목록 -->
      <el-tab-pane label="FMEA 목록" name="list">
        <div class="filter-bar">
          <el-select v-model="filterStatus" placeholder="상태 선택" clearable style="width: 150px;" @change="loadFmeaList">
            <el-option label="작성중" value="DRAFT" />
            <el-option label="검토중" value="IN_REVIEW" />
            <el-option label="승인" value="APPROVED" />
            <el-option label="종결" value="CLOSED" />
          </el-select>
        </div>

        <el-table :data="fmeaList" border stripe v-loading="loading" @row-click="selectFmea">
          <el-table-column prop="fmea_no" label="FMEA No." width="140" />
          <el-table-column prop="product_name" label="제품" width="150" />
          <el-table-column prop="fmea_type" label="유형" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.fmea_type === 'DESIGN' ? 'warning' : ''" size="small">
                {{ row.fmea_type === 'DESIGN' ? 'DFMEA' : 'PFMEA' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="revision" label="Rev." width="70" align="center" />
          <el-table-column prop="status" label="상태" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="item_count" label="항목수" width="80" align="center" />
          <el-table-column prop="prepared_by" label="작성자" width="100" />
          <el-table-column prop="updated_at" label="수정일" width="120" align="center">
            <template #default="{ row }">
              {{ row.updated_at ? row.updated_at.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editFmea(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deleteFmea(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: FMEA 상세 (Matrix) -->
      <el-tab-pane label="FMEA 항목" name="matrix">
        <el-empty v-if="!selectedFmea" description="FMEA 목록에서 항목을 선택하세요." />
        <div v-if="selectedFmea" class="fmea-detail-header">
          <h3>{{ selectedFmea.fmea_no }}</h3>
          <el-tag :type="selectedFmea.fmea_type === 'DESIGN' ? 'warning' : ''" size="small">
            {{ selectedFmea.fmea_type === 'DESIGN' ? 'DFMEA' : 'PFMEA' }}
          </el-tag>
          <el-tag :type="getStatusType(selectedFmea.status)">{{ getStatusLabel(selectedFmea.status) }}</el-tag>
          <span class="fmea-detail-product">{{ selectedFmea.product_name }}</span>
        </div>

        <FmeaMatrix
          :items="fmeaItems"
          @save="saveFmeaItems"
        />
      </el-tab-pane>

      <!-- Tab 3: RPN 분석 -->
      <el-tab-pane label="RPN 분석" name="rpnAnalysis">
        <el-empty v-if="!selectedFmea" description="FMEA 목록에서 항목을 선택하세요." />
        <div v-if="rpnSummary" class="kpi-row">
          <KpiCard title="총 항목" :value="rpnSummary.total_items" unit="건" color="#0A6ED1" />
          <KpiCard title="High (≥100)" :value="rpnSummary.high_rpn_count" unit="건" color="#BB0000" />
          <KpiCard title="Medium (50~99)" :value="rpnSummary.medium_rpn_count" unit="건" color="#E9730C" />
          <KpiCard title="평균 RPN" :value="rpnSummary.avg_rpn" color="#107E3E" />
        </div>

        <ParetoChart
          v-if="rpnAnalysis.categories.length > 0"
          title="RPN 파레토 분석"
          :categories="rpnAnalysis.categories"
          :values="rpnAnalysis.values"
        />
        <el-empty v-else description="FMEA를 선택하고 항목을 저장하세요." />
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingFmea ? 'FMEA 수정' : '새 FMEA 생성'"
      width="600px"
    >
      <el-form :model="fmeaForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="FMEA No." required>
              <el-input v-model="fmeaForm.fmea_no" placeholder="FMEA-D-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="유형" required>
              <el-select v-model="fmeaForm.fmea_type" style="width: 100%;">
                <el-option label="DFMEA (설계)" value="DESIGN" />
                <el-option label="PFMEA (공정)" value="PROCESS" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="제품 ID" required>
              <el-select v-model="fmeaForm.product_id" placeholder="제품 선택" filterable style="width: 100%;">
                <el-option v-for="p in productOptions" :key="p.product_id" :label="p.product_name" :value="p.product_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="상태">
              <el-select v-model="fmeaForm.status" style="width: 100%;">
                <el-option label="작성중" value="DRAFT" />
                <el-option label="검토중" value="IN_REVIEW" />
                <el-option label="승인" value="APPROVED" />
                <el-option label="종결" value="CLOSED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="작성자">
              <el-input v-model="fmeaForm.prepared_by" placeholder="작성자" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="승인자">
              <el-input v-model="fmeaForm.approved_by" placeholder="승인자" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="submitFmea">저장</el-button>
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
import FmeaMatrix from '@/components/quality/FmeaMatrix.vue'
import ParetoChart from '@/components/charts/ParetoChart.vue'
import { fmeaApi } from '@/api/quality'
import client from '@/api/client'

const activeTab = ref('list')
const fmeaType = ref('PROCESS')
const loading = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const editingFmea = ref(false)

const fmeaList = ref<any[]>([])
const selectedFmea = ref<any>(null)
const fmeaItems = ref<any[]>([])
const rpnAnalysis = ref<{ categories: string[]; values: number[] }>({ categories: [], values: [] })
const rpnSummary = ref<any>(null)
const productOptions = ref<any[]>([])

const fmeaTypeLabel = computed(() => fmeaType.value === 'DESIGN' ? 'DFMEA (설계 FMEA)' : 'PFMEA (공정 FMEA)')

const fmeaForm = ref({
  fmea_id: null as number | null,
  fmea_no: '',
  product_id: '',
  fmea_type: 'PROCESS',
  status: 'DRAFT',
  prepared_by: '',
  approved_by: ''
})

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'DRAFT': return 'info'
    case 'IN_REVIEW': return 'warning'
    case 'APPROVED': return 'success'
    case 'CLOSED': return ''
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'DRAFT': return '작성중'
    case 'IN_REVIEW': return '검토중'
    case 'APPROVED': return '승인'
    case 'CLOSED': return '종결'
    default: return status
  }
}

function onTypeChange() {
  selectedFmea.value = null
  activeTab.value = 'list'
  loadFmeaList()
}

onMounted(() => {
  loadFmeaList()
  loadProducts()
})

async function loadProducts() {
  try {
    const res = await client.get('/master/products', { params: { size: 100 } })
    productOptions.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('제품 목록 조회 실패:', e)
    productOptions.value = []
  }
}

async function loadFmeaList() {
  loading.value = true
  try {
    const res = await fmeaApi.getList({
      fmea_type: fmeaType.value,
      status: filterStatus.value || undefined
    })
    fmeaList.value = res.data.items || res.data
  } catch (e) {
    console.warn('FMEA 목록 조회 실패:', e)
    ElMessage.error('FMEA 목록을 불러오는데 실패했습니다')
    fmeaList.value = []
  } finally {
    loading.value = false
  }
}

async function selectFmea(row: any) {
  selectedFmea.value = row
  activeTab.value = 'matrix'

  try {
    const res = await fmeaApi.getItems(row.fmea_id)
    fmeaItems.value = res.data
  } catch (e) {
    console.warn('FMEA 항목 조회 실패:', e)
    ElMessage.error('FMEA 항목을 불러오는데 실패했습니다')
    fmeaItems.value = []
  }

  loadRpnAnalysis(row.fmea_id)
}

async function loadRpnAnalysis(fmeaId: number) {
  try {
    const res = await fmeaApi.getRpnAnalysis(fmeaId)
    const data = res.data
    rpnSummary.value = {
      total_items: data.total_items,
      high_rpn_count: data.high_rpn_count,
      medium_rpn_count: data.medium_rpn_count,
      avg_rpn: data.avg_rpn,
      max_rpn: data.max_rpn
    }
    // 파레토 차트: top RPN items
    if (data.top_rpn_items && data.top_rpn_items.length > 0) {
      rpnAnalysis.value = {
        categories: data.top_rpn_items.map((i: any) => i.failure_mode || i.process_step || `항목${i.item_id}`),
        values: data.top_rpn_items.map((i: any) => i.rpn || 0)
      }
    } else {
      rpnAnalysis.value = { categories: [], values: [] }
    }
  } catch (e) {
    console.warn('RPN 분석 조회 실패:', e)
    rpnSummary.value = null
    rpnAnalysis.value = { categories: [], values: [] }
  }
}

function openCreateDialog() {
  editingFmea.value = false
  fmeaForm.value = {
    fmea_id: null,
    fmea_no: '',
    product_id: '',
    fmea_type: fmeaType.value,
    status: 'DRAFT',
    prepared_by: '',
    approved_by: ''
  }
  showCreateDialog.value = true
}

function editFmea(row: any) {
  editingFmea.value = true
  fmeaForm.value = {
    fmea_id: row.fmea_id,
    fmea_no: row.fmea_no,
    product_id: row.product_id,
    fmea_type: row.fmea_type,
    status: row.status,
    prepared_by: row.prepared_by || '',
    approved_by: row.approved_by || ''
  }
  showCreateDialog.value = true
}

async function deleteFmea(row: any) {
  try {
    await ElMessageBox.confirm(`"${row.fmea_no}"을(를) 삭제하시겠습니까?`, '삭제 확인', { type: 'warning' })
    await fmeaApi.delete(row.fmea_id)
    ElMessage.success('삭제되었습니다.')
    if (selectedFmea.value?.fmea_id === row.fmea_id) {
      selectedFmea.value = null
    }
    loadFmeaList()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitFmea() {
  if (!fmeaForm.value.fmea_no) {
    ElMessage.warning('FMEA No.를 입력하세요.')
    return
  }
  if (!fmeaForm.value.product_id) {
    ElMessage.warning('제품을 선택하세요.')
    return
  }

  try {
    const payload = {
      fmea_no: fmeaForm.value.fmea_no,
      product_id: fmeaForm.value.product_id,
      fmea_type: fmeaForm.value.fmea_type,
      status: fmeaForm.value.status,
      prepared_by: fmeaForm.value.prepared_by || undefined,
      approved_by: fmeaForm.value.approved_by || undefined
    }

    if (fmeaForm.value.fmea_id) {
      await fmeaApi.update(fmeaForm.value.fmea_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await fmeaApi.create(payload)
      ElMessage.success('생성되었습니다.')
    }
    showCreateDialog.value = false
    editingFmea.value = false
    loadFmeaList()
  } catch {
    ElMessage.error('저장에 실패했습니다.')
  }
}

async function saveFmeaItems(items: any[]) {
  if (!selectedFmea.value) return
  const fmeaId = selectedFmea.value.fmea_id

  const results = await Promise.allSettled(
    items.map(item =>
      item.item_id
        ? fmeaApi.updateItem(fmeaId, item.item_id, item)
        : fmeaApi.createItem(fmeaId, item)
    )
  )

  const succeeded = results.filter(r => r.status === 'fulfilled').length
  const failed = results.filter(r => r.status === 'rejected').length

  if (failed === 0) {
    ElMessage.success('FMEA 항목이 저장되었습니다.')
  } else if (succeeded > 0) {
    ElMessage.warning(`${items.length}건 중 ${succeeded}건 성공, ${failed}건 실패했습니다.`)
  } else {
    ElMessage.error('모든 항목 저장에 실패했습니다.')
  }
  selectFmea(selectedFmea.value)
}
</script>

<style scoped>
.type-selector {
  margin-bottom: 16px;
}

.fmea-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #E5E5E5;
}

.fmea-detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.fmea-detail-product {
  color: var(--qms-text-secondary);
  font-size: 14px;
}

</style>
