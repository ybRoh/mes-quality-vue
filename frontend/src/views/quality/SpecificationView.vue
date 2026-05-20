<template>
  <div class="page-container">
    <PageHeader title="규격 목록" subtitle="고객규격, 도면, 법규, 내부규격 관리">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 규격
        </el-button>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 규격 목록 -->
      <el-tab-pane label="규격 목록" name="list">
        <div class="filter-bar">
          <el-select
            v-model="filterSpecType"
            placeholder="규격유형"
            clearable
            style="width: 160px;"
            @change="loadList"
          >
            <el-option label="고객규격" value="CUSTOMER" />
            <el-option label="도면" value="DRAWING" />
            <el-option label="법규" value="LEGAL" />
            <el-option label="내부규격" value="INTERNAL" />
          </el-select>
          <el-select
            v-model="filterStatus"
            placeholder="상태"
            clearable
            style="width: 140px;"
            @change="loadList"
          >
            <el-option label="활성" value="ACTIVE" />
            <el-option label="대체" value="SUPERSEDED" />
            <el-option label="폐기" value="OBSOLETE" />
          </el-select>
        </div>

        <el-table :data="tableData" border stripe v-loading="loading" @row-click="selectSpec">
          <el-table-column prop="spec_no" label="규격번호" width="140" />
          <el-table-column prop="spec_type" label="유형" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getSpecTypeTag(row.spec_type)" size="small">
                {{ getSpecTypeLabel(row.spec_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="규격명" show-overflow-tooltip />
          <el-table-column prop="customer_id" label="고객" width="100" />
          <el-table-column prop="revision" label="Rev." width="70" align="center" />
          <el-table-column prop="status" label="상태" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="effective_date" label="유효일" width="110" align="center" />
          <el-table-column prop="drawing_count" label="도면수" width="80" align="center" />
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editItem(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deleteItem(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 도면 개정이력 -->
      <el-tab-pane label="도면 개정이력" name="drawings">
        <el-empty v-if="!selectedSpec" description="규격 목록에서 항목을 선택하세요." />

        <template v-if="selectedSpec">
          <div class="spec-detail-header">
            <h3>{{ selectedSpec.spec_no }}</h3>
            <span>{{ selectedSpec.title }}</span>
            <el-tag :type="getStatusTag(selectedSpec.status)" size="small">
              {{ getStatusLabel(selectedSpec.status) }}
            </el-tag>
          </div>

          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="margin: 0;">도면 개정이력</h4>
            <el-button type="primary" size="small" @click="openDrawingDialog">
              <el-icon><Plus /></el-icon>
              새 도면
            </el-button>
          </div>

          <el-table :data="drawings" border stripe v-loading="drawingsLoading" size="small">
            <el-table-column prop="drawing_no" label="도면번호" width="140" />
            <el-table-column prop="revision_no" label="Rev." width="70" align="center" />
            <el-table-column prop="change_summary" label="변경내용" show-overflow-tooltip />
            <el-table-column prop="changed_by" label="변경자" width="100" />
            <el-table-column prop="change_date" label="변경일" width="110" align="center" />
            <el-table-column prop="file_path" label="파일경로" width="200" show-overflow-tooltip />
          </el-table>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Specification Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '규격 수정' : '새 규격 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="규격번호" required>
              <el-input v-model="formData.spec_no" placeholder="SPEC-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="규격유형" required>
              <el-select v-model="formData.spec_type" style="width: 100%;">
                <el-option label="고객규격" value="CUSTOMER" />
                <el-option label="도면" value="DRAWING" />
                <el-option label="법규" value="LEGAL" />
                <el-option label="내부규격" value="INTERNAL" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="규격명" required>
          <el-input v-model="formData.title" placeholder="규격명을 입력하세요" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="고객 ID">
              <el-input v-model="formData.customer_id" placeholder="C001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="제품 ID">
              <el-input v-model="formData.product_id" placeholder="P001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="개정번호">
              <el-input-number v-model="formData.revision" :min="1" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="상태">
              <el-select v-model="formData.status" style="width: 100%;">
                <el-option label="활성" value="ACTIVE" />
                <el-option label="대체" value="SUPERSEDED" />
                <el-option label="폐기" value="OBSOLETE" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="출처">
              <el-input v-model="formData.source" placeholder="출처" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="유효일">
              <el-date-picker
                v-model="formData.effective_date"
                type="date"
                placeholder="유효일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="만료일">
              <el-date-picker
                v-model="formData.expiry_date"
                type="date"
                placeholder="만료일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="비고">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="3"
            placeholder="비고를 입력하세요"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">취소</el-button>
        <el-button type="primary" @click="submitForm">저장</el-button>
      </template>
    </el-dialog>

    <!-- Drawing Create Dialog -->
    <el-dialog
      v-model="showDrawingDialog"
      title="새 도면 개정이력"
      width="600px"
    >
      <el-form :model="drawingForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="도면번호" required>
              <el-input v-model="drawingForm.drawing_no" placeholder="DWG-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="개정번호" required>
              <el-input-number v-model="drawingForm.revision_no" :min="1" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="변경내용">
          <el-input v-model="drawingForm.change_summary" type="textarea" :rows="3" placeholder="변경 내용을 기술하세요" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="변경자">
              <el-input v-model="drawingForm.changed_by" placeholder="변경자명" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="변경일">
              <el-date-picker
                v-model="drawingForm.change_date"
                type="date"
                placeholder="변경일 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="파일경로">
          <el-input v-model="drawingForm.file_path" placeholder="/docs/drawings/..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDrawingDialog = false">취소</el-button>
        <el-button type="primary" @click="submitDrawing">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { specificationApi } from '@/api/quality'

const activeTab = ref('list')
const loading = ref(false)
const drawingsLoading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)
const showDrawingDialog = ref(false)

// --- Filter state ---
const filterSpecType = ref('')
const filterStatus = ref('')

// --- Data ---
const tableData = ref<any[]>([])
const selectedSpec = ref<any>(null)
const drawings = ref<any[]>([])

const formData = ref({
  spec_mgmt_id: null as number | null,
  spec_no: '',
  spec_type: 'CUSTOMER',
  customer_id: '',
  product_id: '',
  title: '',
  revision: 1,
  status: 'ACTIVE',
  effective_date: '',
  expiry_date: '',
  source: '',
  remarks: ''
})

const drawingForm = ref({
  drawing_no: '',
  revision_no: 1,
  change_summary: '',
  changed_by: '',
  change_date: '',
  file_path: ''
})

// --- Label / Tag helpers ---
function getSpecTypeLabel(type: string): string {
  switch (type) {
    case 'CUSTOMER': return '고객규격'
    case 'DRAWING': return '도면'
    case 'LEGAL': return '법규'
    case 'INTERNAL': return '내부규격'
    default: return type || '-'
  }
}

function getSpecTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (type) {
    case 'CUSTOMER': return ''
    case 'DRAWING': return 'success'
    case 'LEGAL': return 'danger'
    case 'INTERNAL': return 'warning'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'ACTIVE': return '활성'
    case 'SUPERSEDED': return '대체'
    case 'OBSOLETE': return '폐기'
    default: return status || '-'
  }
}

function getStatusTag(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'ACTIVE': return 'success'
    case 'SUPERSEDED': return 'warning'
    case 'OBSOLETE': return 'info'
    default: return 'info'
  }
}

// --- Lifecycle ---
onMounted(() => {
  loadList()
})

// --- Specification CRUD ---
async function loadList() {
  loading.value = true
  try {
    const res = await specificationApi.getList({
      spec_type: filterSpecType.value || undefined,
      status: filterStatus.value || undefined
    })
    tableData.value = res.data.items || res.data
  } catch (e) {
    console.warn('규격 목록 조회 실패:', e)
    ElMessage.error('규격 목록을 불러오는데 실패했습니다')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

function selectSpec(row: any) {
  selectedSpec.value = row
  activeTab.value = 'drawings'
  loadDrawings()
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    spec_mgmt_id: null,
    spec_no: '',
    spec_type: 'CUSTOMER',
    customer_id: '',
    product_id: '',
    title: '',
    revision: 1,
    status: 'ACTIVE',
    effective_date: '',
    expiry_date: '',
    source: '',
    remarks: ''
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    spec_mgmt_id: row.spec_mgmt_id,
    spec_no: row.spec_no || '',
    spec_type: row.spec_type || 'CUSTOMER',
    customer_id: row.customer_id || '',
    product_id: row.product_id || '',
    title: row.title || '',
    revision: row.revision || 1,
    status: row.status || 'ACTIVE',
    effective_date: row.effective_date || '',
    expiry_date: row.expiry_date || '',
    source: row.source || '',
    remarks: row.remarks || ''
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.spec_no}"을(를) 삭제하시겠습니까? 관련 도면 이력도 함께 삭제됩니다.`,
      '삭제 확인',
      { type: 'warning' }
    )
    await specificationApi.delete(row.spec_mgmt_id)
    ElMessage.success('삭제되었습니다.')
    if (selectedSpec.value?.spec_mgmt_id === row.spec_mgmt_id) {
      selectedSpec.value = null
      drawings.value = []
    }
    loadList()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitForm() {
  if (!formData.value.spec_no) {
    ElMessage.warning('규격번호를 입력하세요.')
    return
  }
  if (!formData.value.title) {
    ElMessage.warning('규격명을 입력하세요.')
    return
  }

  try {
    const payload = {
      spec_no: formData.value.spec_no,
      spec_type: formData.value.spec_type,
      customer_id: formData.value.customer_id || undefined,
      product_id: formData.value.product_id || undefined,
      title: formData.value.title,
      revision: formData.value.revision,
      status: formData.value.status,
      effective_date: formData.value.effective_date || undefined,
      expiry_date: formData.value.expiry_date || undefined,
      source: formData.value.source || undefined,
      remarks: formData.value.remarks || undefined
    }

    if (formData.value.spec_mgmt_id) {
      await specificationApi.update(formData.value.spec_mgmt_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await specificationApi.create(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('규격 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// --- Drawings ---
async function loadDrawings() {
  if (!selectedSpec.value) return
  drawingsLoading.value = true
  try {
    const res = await specificationApi.getDrawings(selectedSpec.value.spec_mgmt_id)
    drawings.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('도면 이력 조회 실패:', e)
    ElMessage.error('도면 이력을 불러오는데 실패했습니다')
    drawings.value = []
  } finally {
    drawingsLoading.value = false
  }
}

function openDrawingDialog() {
  drawingForm.value = {
    drawing_no: '',
    revision_no: 1,
    change_summary: '',
    changed_by: '',
    change_date: '',
    file_path: ''
  }
  showDrawingDialog.value = true
}

async function submitDrawing() {
  if (!selectedSpec.value) return
  if (!drawingForm.value.drawing_no) {
    ElMessage.warning('도면번호를 입력하세요.')
    return
  }

  try {
    const payload = {
      drawing_no: drawingForm.value.drawing_no,
      revision_no: drawingForm.value.revision_no,
      change_summary: drawingForm.value.change_summary || undefined,
      changed_by: drawingForm.value.changed_by || undefined,
      change_date: drawingForm.value.change_date || undefined,
      file_path: drawingForm.value.file_path || undefined
    }
    await specificationApi.createDrawing(selectedSpec.value.spec_mgmt_id, payload)
    ElMessage.success('도면 개정이력이 등록되었습니다.')
    showDrawingDialog.value = false
    loadDrawings()
    loadList()
  } catch (e) {
    console.warn('도면 등록 실패:', e)
    ElMessage.error('도면 등록에 실패했습니다.')
  }
}
</script>

<style scoped>
.spec-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #E5E5E5;
}

.spec-detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
</style>
