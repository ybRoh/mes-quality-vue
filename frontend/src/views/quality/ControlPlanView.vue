<template>
  <div class="page-container">
    <PageHeader title="관리계획서 (Control Plan)" subtitle="IATF 16949 관리계획서 관리">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 관리계획서
        </el-button>
      </template>
    </PageHeader>

    <!-- CP List -->
    <div class="card" v-if="!selectedCp">
      <el-table :data="cpList" border stripe v-loading="loading" @row-click="selectCp">
        <el-table-column prop="cp_no" label="관리계획번호" width="150" />
        <el-table-column prop="product_name" label="제품" width="150" />
        <el-table-column prop="cp_type" label="유형" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getCpTypeLabel(row.cp_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="revision" label="개정" width="70" align="center" />
        <el-table-column prop="fmea_id" label="FMEA" width="80" align="center">
          <template #default="{ row }">{{ row.fmea_id || '-' }}</template>
        </el-table-column>
        <el-table-column prop="item_count" label="항목수" width="80" align="center" />
        <el-table-column prop="status" label="상태" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="prepared_by" label="작성자" width="100" align="center" />
        <el-table-column prop="updated_at" label="수정일" width="120" align="center">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
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
            <h3 style="margin: 8px 0 0 0;">{{ selectedCp.cp_no }} - {{ selectedCp.product_name }}</h3>
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
          <el-table-column prop="machine_id" label="설비" width="100" />
          <el-table-column prop="characteristic_class" label="분류" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.characteristic_class === 'CTQ' ? 'danger' : row.characteristic_class === 'MAJOR' ? 'warning' : 'info'" size="small">
                {{ row.characteristic_class || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="characteristic_name" label="특성명" min-width="130" />
          <el-table-column prop="evaluation_method" label="평가방법" width="130" />
          <el-table-column prop="sample_size" label="시료크기" width="80" align="center" />
          <el-table-column prop="sample_frequency" label="시료빈도" width="100" />
          <el-table-column prop="control_method" label="관리방법" width="130" />
          <el-table-column prop="reaction_plan" label="대응계획" width="130" />
          <el-table-column label="작업" width="80" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editItem(row)">편집</el-button>
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
              <el-input v-model="cpForm.cp_no" placeholder="CP-INJ-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="개정번호">
              <el-input-number v-model="cpForm.revision" :min="1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="제품" required>
              <el-select v-model="cpForm.product_id" filterable placeholder="제품 선택" style="width: 100%;">
                <el-option v-for="p in productOptions" :key="p.product_id" :label="p.product_name" :value="p.product_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="FMEA 연계">
              <el-select v-model="cpForm.fmea_id" clearable placeholder="FMEA 선택" style="width: 100%;">
                <el-option v-for="f in fmeaOptions" :key="f.fmea_id" :label="f.fmea_no" :value="f.fmea_id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="유형">
              <el-select v-model="cpForm.cp_type" style="width: 100%;">
                <el-option label="양산" value="PRODUCTION" />
                <el-option label="시작" value="PROTOTYPE" />
                <el-option label="사전양산" value="PRE_LAUNCH" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="상태">
              <el-select v-model="cpForm.status" style="width: 100%;">
                <el-option label="작성중" value="DRAFT" />
                <el-option label="검토중" value="IN_REVIEW" />
                <el-option label="승인" value="APPROVED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="submitCp">저장</el-button>
      </template>
    </el-dialog>

    <!-- Item Dialog -->
    <el-dialog v-model="showItemDialog" :title="editingItem ? '항목 수정' : '항목 추가'" width="700px">
      <el-form :model="itemForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="공정번호">
              <el-input v-model="itemForm.process_no" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="공정명">
              <el-input v-model="itemForm.process_name" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="설비 ID">
              <el-input v-model="itemForm.machine_id" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="특성명">
              <el-input v-model="itemForm.characteristic_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="분류">
              <el-select v-model="itemForm.characteristic_class" clearable style="width: 100%;">
                <el-option label="CTQ" value="CTQ" />
                <el-option label="MAJOR" value="MAJOR" />
                <el-option label="MINOR" value="MINOR" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="평가방법">
              <el-input v-model="itemForm.evaluation_method" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="시료크기">
              <el-input v-model="itemForm.sample_size" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="시료빈도">
              <el-input v-model="itemForm.sample_frequency" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="관리방법">
              <el-input v-model="itemForm.control_method" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="대응계획">
              <el-input v-model="itemForm.reaction_plan" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showItemDialog = false">취소</el-button>
        <el-button type="primary" @click="submitItem">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Back } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { controlPlanApi, fmeaApi } from '@/api/quality'
import client from '@/api/client'

const loading = ref(false)
const showCreateDialog = ref(false)
const showItemDialog = ref(false)
const editingCp = ref(false)
const editingItem = ref(false)

const cpList = ref<any[]>([])
const selectedCp = ref<any>(null)
const cpItems = ref<any[]>([])
const fmeaOptions = ref<any[]>([])
const productOptions = ref<any[]>([])

const cpForm = ref({
  cp_id: null as number | null,
  cp_no: '',
  product_id: '',
  fmea_id: null as number | null,
  cp_type: 'PRODUCTION',
  revision: 1,
  status: 'DRAFT'
})

const itemForm = ref<any>({})

function getCpTypeLabel(type: string): string {
  switch (type) {
    case 'PRODUCTION': return '양산'
    case 'PROTOTYPE': return '시작'
    case 'PRE_LAUNCH': return '사전양산'
    default: return type
  }
}

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'DRAFT': return 'info'
    case 'IN_REVIEW': return 'warning'
    case 'APPROVED': return 'success'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'DRAFT': return '작성중'
    case 'IN_REVIEW': return '검토중'
    case 'APPROVED': return '승인'
    default: return status
  }
}

function formatDate(dt: string): string {
  if (!dt) return '-'
  return dt.substring(0, 10)
}

onMounted(async () => {
  await loadCpList()
  try {
    const [fmeaRes, prodRes] = await Promise.all([
      fmeaApi.getList(),
      client.get('/master/products')
    ])
    const items = fmeaRes.data.items || fmeaRes.data
    fmeaOptions.value = items
    productOptions.value = prodRes.data.items || prodRes.data
  } catch {
    fmeaOptions.value = []
    productOptions.value = []
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
    const res = await controlPlanApi.getItems(row.cp_id)
    cpItems.value = res.data
  } catch (e) {
    console.warn('관리계획서 항목 조회 실패:', e)
    ElMessage.error('관리계획서 항목을 불러오는데 실패했습니다')
    cpItems.value = []
  }
}

function openCreateDialog() {
  editingCp.value = false
  cpForm.value = { cp_id: null, cp_no: '', product_id: '', fmea_id: null, cp_type: 'PRODUCTION', revision: 1, status: 'DRAFT' }
  showCreateDialog.value = true
}

function editCp(row: any) {
  editingCp.value = true
  cpForm.value = {
    cp_id: row.cp_id,
    cp_no: row.cp_no,
    product_id: row.product_id,
    fmea_id: row.fmea_id,
    cp_type: row.cp_type,
    revision: row.revision,
    status: row.status
  }
  showCreateDialog.value = true
}

async function deleteCp(row: any) {
  try {
    await ElMessageBox.confirm(`"${row.cp_no}"을(를) 삭제하시겠습니까?`, '삭제 확인', { type: 'warning' })
    await controlPlanApi.delete(row.cp_id)
    ElMessage.success('삭제되었습니다.')
    loadCpList()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitCp() {
  if (!cpForm.value.cp_no || !cpForm.value.product_id) {
    ElMessage.warning('관리계획번호와 제품을 입력하세요.')
    return
  }
  try {
    if (cpForm.value.cp_id) {
      await controlPlanApi.update(cpForm.value.cp_id, cpForm.value)
    } else {
      await controlPlanApi.create(cpForm.value)
    }
    ElMessage.success('저장되었습니다.')
    showCreateDialog.value = false
    editingCp.value = false
    loadCpList()
  } catch {
    ElMessage.error('저장에 실패했습니다.')
  }
}

function editItem(row: any) {
  editingItem.value = true
  itemForm.value = { ...row }
  showItemDialog.value = true
}

async function submitItem() {
  if (!selectedCp.value) return
  try {
    if (itemForm.value.cp_item_id) {
      await controlPlanApi.updateItem(selectedCp.value.cp_id, itemForm.value.cp_item_id, itemForm.value)
    } else {
      await controlPlanApi.createItem(selectedCp.value.cp_id, itemForm.value)
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
