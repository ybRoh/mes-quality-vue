<template>
  <div class="page-container">
    <PageHeader title="관리계획서 (Control Plan)" subtitle="IATF 16949 관리계획서 관리">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          새 관리계획서
        </el-button>
      </template>
    </PageHeader>

    <!-- CP List -->
    <div class="card" v-if="!selectedCp">
      <div class="filter-bar">
        <el-input v-model="searchKeyword" placeholder="검색 (제목, 제품)" clearable style="width: 250px;" @keyup.enter="loadCpList">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" size="small" @click="loadCpList">조회</el-button>
      </div>

      <el-table :data="cpList" border stripe v-loading="loading" @row-click="selectCp">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="cp_no" label="관리계획번호" width="150" />
        <el-table-column prop="title" label="제목" min-width="200" />
        <el-table-column prop="product_name" label="제품" width="130" />
        <el-table-column prop="revision" label="개정번호" width="90" align="center" />
        <el-table-column prop="fmea_ref" label="FMEA 연계" width="130" />
        <el-table-column prop="status" label="상태" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="수정일" width="120" align="center" />
        <el-table-column label="작업" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="editCp(row)">편집</el-button>
            <el-button type="danger" link size="small" @click.stop="deleteCp(row)">삭제</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- CP Detail with Items -->
    <div v-if="selectedCp">
      <div class="card">
        <div class="cp-detail-header">
          <div>
            <el-button link @click="selectedCp = null">
              <el-icon><Back /></el-icon>
              목록으로
            </el-button>
            <h3 style="margin: 8px 0 0 0;">{{ selectedCp.title }} ({{ selectedCp.cp_no }})</h3>
          </div>
          <el-button type="primary" size="small" @click="showItemDialog = true">
            <el-icon><Plus /></el-icon>
            항목 추가
          </el-button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">관리 항목</div>
        <el-table :data="cpItems" border stripe>
          <el-table-column prop="process_no" label="공정번호" width="90" align="center" />
          <el-table-column prop="process_name" label="공정명" width="120" />
          <el-table-column prop="machine" label="설비" width="100" />
          <el-table-column prop="characteristic_class" label="분류" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.characteristic_class === 'CTQ' ? 'danger' : row.characteristic_class === 'MAJOR' ? 'warning' : 'info'" size="small">
                {{ row.characteristic_class }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="product_characteristic" label="제품특성" min-width="130" />
          <el-table-column prop="specification" label="규격/공차" width="130" />
          <el-table-column prop="evaluation_method" label="평가방법" width="130" />
          <el-table-column prop="sample_size" label="시료크기" width="80" align="center" />
          <el-table-column prop="sample_frequency" label="시료빈도" width="100" />
          <el-table-column prop="control_method" label="관리방법" width="130" />
          <el-table-column prop="reaction_plan" label="대응계획" width="130" />
          <el-table-column label="작업" width="80" align="center" fixed="right">
            <template #default="{ row, $index }">
              <el-button type="primary" link size="small" @click="editItem(row, $index)">편집</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Create CP Dialog -->
    <el-dialog v-model="showCreateDialog" :title="editingCp ? '관리계획서 수정' : '새 관리계획서'" width="600px">
      <el-form :model="cpForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="관리계획번호" required>
              <el-input v-model="cpForm.cp_no" placeholder="CP-2026-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="개정번호">
              <el-input v-model="cpForm.revision" placeholder="Rev.01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="제목" required>
          <el-input v-model="cpForm.title" placeholder="관리계획서 제목" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="제품명">
              <el-input v-model="cpForm.product_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="FMEA 연계">
              <el-input v-model="cpForm.fmea_ref" placeholder="FMEA 번호" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="상태">
          <el-select v-model="cpForm.status" style="width: 100%;">
            <el-option label="작성중" value="DRAFT" />
            <el-option label="검토중" value="REVIEW" />
            <el-option label="승인" value="APPROVED" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="submitCp">저장</el-button>
      </template>
    </el-dialog>

    <!-- Item Dialog -->
    <el-dialog v-model="showItemDialog" :title="editingItem ? '항목 수정' : '항목 추가'" width="800px" top="5vh">
      <ControlPlanForm
        :model-value="itemForm"
        :fmea-list="fmeaOptions"
        @submit="submitItem"
        @cancel="showItemDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Search, Back } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import ControlPlanForm from '@/components/quality/ControlPlanForm.vue'
import { controlPlanApi, fmeaApi } from '@/api/quality'

const loading = ref(false)
const searchKeyword = ref('')
const showCreateDialog = ref(false)
const showItemDialog = ref(false)
const editingCp = ref(false)
const editingItem = ref(false)
const editingItemIndex = ref(-1)

const cpList = ref<any[]>([])
const selectedCp = ref<any>(null)
const cpItems = ref<any[]>([])
const fmeaOptions = ref<{ id: number; name: string }[]>([])

const cpForm = ref({
  id: null as number | null,
  cp_no: '',
  title: '',
  product_name: '',
  revision: 'Rev.01',
  fmea_ref: '',
  status: 'DRAFT'
})

const itemForm = ref<any>({})

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

onMounted(async () => {
  await loadCpList()
  try {
    const res = await fmeaApi.getList()
    const items = res.data.items || res.data
    fmeaOptions.value = items.map((f: any) => ({ id: f.id, name: f.title }))
  } catch (e) {
    console.warn('FMEA 옵션 목록 조회 실패:', e)
    fmeaOptions.value = []
  }
})

async function loadCpList() {
  loading.value = true
  try {
    const res = await controlPlanApi.getList()
    cpList.value = res.data.items || res.data
  } catch (e) {
    console.warn('관리계획서 목록 조회 실패:', e)
    ElMessage.error('관리계획서 목록을 불러오는데 실패했습니다')
    cpList.value = []
  } finally {
    loading.value = false
  }
}

async function selectCp(row: any) {
  selectedCp.value = row
  try {
    const res = await controlPlanApi.getItems(row.id)
    cpItems.value = res.data
  } catch (e) {
    console.warn('관리계획서 항목 조회 실패:', e)
    ElMessage.error('관리계획서 항목을 불러오는데 실패했습니다')
    cpItems.value = []
  }
}

function editCp(row: any) {
  editingCp.value = true
  cpForm.value = { ...row }
  showCreateDialog.value = true
}

async function deleteCp(row: any) {
  try {
    await ElMessageBox.confirm(`"${row.title}"을(를) 삭제하시겠습니까?`, '삭제 확인', { type: 'warning' })
    await controlPlanApi.delete(row.id)
    ElMessage.success('삭제되었습니다.')
    loadCpList()
  } catch { /* cancelled */ }
}

async function submitCp() {
  if (!cpForm.value.title || !cpForm.value.cp_no) {
    ElMessage.warning('필수항목을 입력하세요.')
    return
  }
  try {
    if (cpForm.value.id) {
      await controlPlanApi.update(cpForm.value.id, cpForm.value)
    } else {
      await controlPlanApi.create(cpForm.value)
    }
    ElMessage.success('저장되었습니다.')
    showCreateDialog.value = false
    editingCp.value = false
    cpForm.value = { id: null, cp_no: '', title: '', product_name: '', revision: 'Rev.01', fmea_ref: '', status: 'DRAFT' }
    loadCpList()
  } catch {
    ElMessage.error('저장에 실패했습니다.')
  }
}

function editItem(row: any, index: number) {
  editingItem.value = true
  editingItemIndex.value = index
  itemForm.value = { ...row }
  showItemDialog.value = true
}

async function submitItem(data: any) {
  if (!selectedCp.value) return
  try {
    if (data.id) {
      await controlPlanApi.updateItem(selectedCp.value.id, data.id, data)
    } else {
      await controlPlanApi.createItem(selectedCp.value.id, data)
    }
    ElMessage.success('항목이 저장되었습니다.')
    showItemDialog.value = false
    editingItem.value = false
    itemForm.value = {}
    selectCp(selectedCp.value)
  } catch {
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
.cp-detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
</style>
