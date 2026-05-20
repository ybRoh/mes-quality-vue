<template>
  <div class="page-container">
    <PageHeader title="FMEA (고장모드 영향분석)" subtitle="IATF 16949 공정 FMEA 관리">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          새 FMEA
        </el-button>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: FMEA 목록 -->
      <el-tab-pane label="FMEA 목록" name="list">
        <div class="filter-bar">
          <el-select v-model="filterStatus" placeholder="상태 선택" clearable style="width: 150px;">
            <el-option label="작성중" value="DRAFT" />
            <el-option label="검토중" value="REVIEW" />
            <el-option label="승인" value="APPROVED" />
          </el-select>
          <el-input v-model="searchKeyword" placeholder="검색 (제목, 제품)" clearable style="width: 250px;" @keyup.enter="loadFmeaList">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button type="primary" size="small" @click="loadFmeaList">조회</el-button>
        </div>

        <el-table :data="fmeaList" border stripe v-loading="loading" @row-click="selectFmea">
          <el-table-column prop="id" label="ID" width="60" align="center" />
          <el-table-column prop="title" label="제목" min-width="200" />
          <el-table-column prop="product_name" label="제품" width="130" />
          <el-table-column prop="process_name" label="공정" width="130" />
          <el-table-column prop="status" label="상태" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="max_rpn" label="최대RPN" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.max_rpn >= 200 ? 'danger' : row.max_rpn >= 100 ? 'warning' : 'success'" effect="dark">
                {{ row.max_rpn || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="수정일" width="120" align="center" />
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editFmea(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deleteFmea(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: FMEA 상세 (Matrix) -->
      <el-tab-pane label="FMEA 항목" name="matrix" :disabled="!selectedFmea">
        <div v-if="selectedFmea" class="fmea-detail-header">
          <h3>{{ selectedFmea.title }}</h3>
          <el-tag :type="getStatusType(selectedFmea.status)">{{ getStatusLabel(selectedFmea.status) }}</el-tag>
        </div>

        <FmeaMatrix
          :items="fmeaItems"
          @save="saveFmeaItems"
        />
      </el-tab-pane>

      <!-- Tab 3: RPN 분석 -->
      <el-tab-pane label="RPN 분석" name="rpnAnalysis" :disabled="!selectedFmea">
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
        <el-form-item label="제목" required>
          <el-input v-model="fmeaForm.title" placeholder="FMEA 제목 입력" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="제품명">
              <el-input v-model="fmeaForm.product_name" placeholder="제품명" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="공정명">
              <el-input v-model="fmeaForm.process_name" placeholder="공정명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="상태">
          <el-select v-model="fmeaForm.status" style="width: 100%;">
            <el-option label="작성중" value="DRAFT" />
            <el-option label="검토중" value="REVIEW" />
            <el-option label="승인" value="APPROVED" />
          </el-select>
        </el-form-item>
        <el-form-item label="비고">
          <el-input v-model="fmeaForm.remarks" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="submitFmea">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FmeaMatrix from '@/components/quality/FmeaMatrix.vue'
import ParetoChart from '@/components/charts/ParetoChart.vue'
import { fmeaApi } from '@/api/quality'

const activeTab = ref('list')
const loading = ref(false)
const filterStatus = ref('')
const searchKeyword = ref('')
const showCreateDialog = ref(false)
const editingFmea = ref(false)

const fmeaList = ref<any[]>([])
const selectedFmea = ref<any>(null)
const fmeaItems = ref<any[]>([])
const rpnAnalysis = ref<{ categories: string[]; values: number[] }>({ categories: [], values: [] })

const fmeaForm = ref({
  id: null as number | null,
  title: '',
  product_name: '',
  process_name: '',
  status: 'DRAFT',
  remarks: ''
})

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'DRAFT': return 'info'
    case 'REVIEW': return 'warning'
    case 'APPROVED': return 'success'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'DRAFT': return '작성중'
    case 'REVIEW': return '검토중'
    case 'APPROVED': return '승인'
    default: return status
  }
}

onMounted(() => {
  loadFmeaList()
})

async function loadFmeaList() {
  loading.value = true
  try {
    const res = await fmeaApi.getList({ status: filterStatus.value || undefined })
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
    const res = await fmeaApi.getItems(row.id)
    fmeaItems.value = res.data
  } catch (e) {
    console.warn('FMEA 항목 조회 실패:', e)
    ElMessage.error('FMEA 항목을 불러오는데 실패했습니다')
    fmeaItems.value = []
  }

  loadRpnAnalysis(row.id)
}

async function loadRpnAnalysis(fmeaId: number) {
  try {
    const res = await fmeaApi.getRpnAnalysis(fmeaId)
    rpnAnalysis.value = res.data
  } catch (e) {
    console.warn('RPN 분석 조회 실패:', e)
    ElMessage.error('RPN 분석 데이터를 불러오는데 실패했습니다')
    rpnAnalysis.value = { categories: [], values: [] }
  }
}

function editFmea(row: any) {
  editingFmea.value = true
  fmeaForm.value = {
    id: row.id,
    title: row.title,
    product_name: row.product_name,
    process_name: row.process_name,
    status: row.status,
    remarks: row.remarks || ''
  }
  showCreateDialog.value = true
}

async function deleteFmea(row: any) {
  try {
    await ElMessageBox.confirm(`"${row.title}"을(를) 삭제하시겠습니까?`, '삭제 확인', { type: 'warning' })
    await fmeaApi.delete(row.id)
    ElMessage.success('삭제되었습니다.')
    loadFmeaList()
  } catch {
    // cancelled or error
  }
}

async function submitFmea() {
  if (!fmeaForm.value.title) {
    ElMessage.warning('제목을 입력하세요.')
    return
  }

  try {
    if (fmeaForm.value.id) {
      await fmeaApi.update(fmeaForm.value.id, fmeaForm.value)
      ElMessage.success('수정되었습니다.')
    } else {
      await fmeaApi.create(fmeaForm.value)
      ElMessage.success('생성되었습니다.')
    }
    showCreateDialog.value = false
    editingFmea.value = false
    fmeaForm.value = { id: null, title: '', product_name: '', process_name: '', status: 'DRAFT', remarks: '' }
    loadFmeaList()
  } catch {
    ElMessage.error('저장에 실패했습니다.')
  }
}

async function saveFmeaItems(items: any[]) {
  if (!selectedFmea.value) return
  try {
    for (const item of items) {
      if (item.id) {
        await fmeaApi.updateItem(selectedFmea.value.id, item.id, item)
      } else {
        await fmeaApi.createItem(selectedFmea.value.id, item)
      }
    }
    ElMessage.success('FMEA 항목이 저장되었습니다.')
    selectFmea(selectedFmea.value)
  } catch {
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
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
</style>
