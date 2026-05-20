<template>
  <div class="page-container">
    <PageHeader title="KPI 정의 관리" subtitle="핵심 성과지표 정의 및 데이터 관리">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 KPI 정의
        </el-button>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: KPI 목록 -->
      <el-tab-pane label="KPI 목록" name="list">
        <div class="filter-bar">
          <el-select
            v-model="filterCategory"
            placeholder="카테고리 선택"
            clearable
            style="width: 160px;"
            @change="loadDefinitions"
          >
            <el-option label="품질" value="품질" />
            <el-option label="납기" value="납기" />
            <el-option label="원가" value="원가" />
            <el-option label="안전" value="안전" />
          </el-select>
        </div>

        <el-table :data="definitions" border stripe v-loading="loading" @row-click="selectKpi">
          <el-table-column prop="kpi_no" label="KPI No." width="120" />
          <el-table-column prop="kpi_name" label="KPI명" show-overflow-tooltip />
          <el-table-column prop="process_name" label="공정명" width="120" />
          <el-table-column prop="category" label="카테고리" width="90" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.category" :type="getCategoryTagType(row.category)" size="small">
                {{ row.category }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="unit" label="단위" width="70" align="center" />
          <el-table-column prop="target_value" label="목표값" width="90" align="right">
            <template #default="{ row }">
              {{ row.target_value !== null && row.target_value !== undefined ? row.target_value : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="target_direction" label="방향" width="80" align="center">
            <template #default="{ row }">
              {{ row.target_direction === 'HIGHER' ? '↑ 상향' : '↓ 하향' }}
            </template>
          </el-table-column>
          <el-table-column prop="measurement_frequency" label="측정주기" width="90" align="center">
            <template #default="{ row }">
              {{ getFrequencyLabel(row.measurement_frequency) }}
            </template>
          </el-table-column>
          <el-table-column prop="latest_value" label="최신값" width="90" align="right">
            <template #default="{ row }">
              {{ row.latest_value !== null && row.latest_value !== undefined ? row.latest_value : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="latest_status" label="상태" width="80" align="center">
            <template #default="{ row }">
              <el-tag
                v-if="row.latest_status"
                :type="getStatusTagType(row.latest_status)"
                size="small"
                effect="dark"
              >
                {{ row.latest_status }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editItem(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deleteItem(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 데이터 이력 -->
      <el-tab-pane label="데이터 이력" name="data">
        <el-empty v-if="!selectedKpi" description="KPI 목록에서 항목을 선택하세요." />

        <template v-if="selectedKpi">
          <div class="data-header">
            <div class="data-header-info">
              <h3>{{ selectedKpi.kpi_no }} - {{ selectedKpi.kpi_name }}</h3>
              <span style="color: #909399; font-size: 14px;">
                목표: {{ selectedKpi.target_value ?? '-' }} {{ selectedKpi.unit || '' }}
                ({{ selectedKpi.target_direction === 'HIGHER' ? '상향' : '하향' }})
              </span>
            </div>
          </div>

          <!-- Add data form -->
          <div class="add-data-form">
            <el-form :inline="true">
              <el-form-item label="기간">
                <el-input v-model="dataForm.period" placeholder="2026-01" style="width: 140px;" />
              </el-form-item>
              <el-form-item label="실적값">
                <el-input-number v-model="dataForm.actual_value" :precision="2" controls-position="right" style="width: 140px;" />
              </el-form-item>
              <el-form-item label="비고">
                <el-input v-model="dataForm.remarks" placeholder="비고 입력" style="width: 200px;" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitData">데이터 추가</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- Data table -->
          <el-table :data="kpiDataList" border stripe v-loading="dataLoading" size="small">
            <el-table-column prop="period" label="기간" width="120" align="center" />
            <el-table-column prop="actual_value" label="실적값" width="120" align="right" />
            <el-table-column prop="status" label="상태" width="90" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="getStatusTagType(row.status)"
                  size="small"
                  effect="dark"
                >
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="collected_by" label="수집자" width="120" />
            <el-table-column prop="collected_at" label="수집일시" width="180">
              <template #default="{ row }">
                {{ row.collected_at || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="remarks" label="비고" show-overflow-tooltip />
          </el-table>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? 'KPI 정의 수정' : '새 KPI 정의 등록'"
      width="750px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="KPI No." required>
              <el-input v-model="formData.kpi_no" placeholder="KPI-Q-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="KPI명" required>
              <el-input v-model="formData.kpi_name" placeholder="불량률" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="카테고리">
              <el-select v-model="formData.category" placeholder="선택" clearable style="width: 100%;">
                <el-option label="품질" value="품질" />
                <el-option label="납기" value="납기" />
                <el-option label="원가" value="원가" />
                <el-option label="안전" value="안전" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="공정명">
              <el-input v-model="formData.process_name" placeholder="사출공정" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="단위">
              <el-select v-model="formData.unit" placeholder="선택" clearable allow-create filterable style="width: 100%;">
                <el-option label="%" value="%" />
                <el-option label="ppm" value="ppm" />
                <el-option label="건" value="건" />
                <el-option label="점" value="점" />
                <el-option label="일" value="일" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="목표값">
              <el-input-number v-model="formData.target_value" :precision="2" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="목표 방향">
              <el-select v-model="formData.target_direction" style="width: 100%;">
                <el-option label="높을수록 양호 (HIGHER)" value="HIGHER" />
                <el-option label="낮을수록 양호 (LOWER)" value="LOWER" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="측정주기">
              <el-select v-model="formData.measurement_frequency" style="width: 100%;">
                <el-option label="일간" value="DAILY" />
                <el-option label="주간" value="WEEKLY" />
                <el-option label="월간" value="MONTHLY" />
                <el-option label="분기" value="QUARTERLY" />
                <el-option label="연간" value="YEARLY" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Yellow 임계값">
              <el-input-number v-model="formData.threshold_yellow" :precision="2" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Red 임계값">
              <el-input-number v-model="formData.threshold_red" :precision="2" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="담당자">
              <el-input v-model="formData.responsible" placeholder="담당자명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="산출 공식">
          <el-input v-model="formData.formula" type="textarea" :rows="2" placeholder="불량수 / 총생산수 x 100" />
        </el-form-item>
        <el-form-item label="활성 여부">
          <el-switch v-model="formData.is_active" active-text="활성" inactive-text="비활성" />
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
import { kpiApi } from '@/api/quality'

const activeTab = ref('list')
const loading = ref(false)
const dataLoading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)

const filterCategory = ref('')

const definitions = ref<any[]>([])
const selectedKpi = ref<any>(null)
const kpiDataList = ref<any[]>([])

const formData = ref({
  kpi_id: null as number | null,
  kpi_no: '',
  kpi_name: '',
  process_name: '',
  category: '',
  unit: '',
  target_value: null as number | null,
  target_direction: 'HIGHER',
  threshold_yellow: null as number | null,
  threshold_red: null as number | null,
  measurement_frequency: 'MONTHLY',
  responsible: '',
  formula: '',
  is_active: true
})

const dataForm = ref({
  period: '',
  actual_value: 0,
  remarks: ''
})

function getCategoryTagType(category: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (category) {
    case '품질': return ''
    case '납기': return 'warning'
    case '원가': return 'success'
    case '안전': return 'danger'
    default: return 'info'
  }
}

function getStatusTagType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'GREEN': return 'success'
    case 'YELLOW': return 'warning'
    case 'RED': return 'danger'
    default: return 'info'
  }
}

function getFrequencyLabel(freq: string): string {
  switch (freq) {
    case 'DAILY': return '일간'
    case 'WEEKLY': return '주간'
    case 'MONTHLY': return '월간'
    case 'QUARTERLY': return '분기'
    case 'YEARLY': return '연간'
    default: return freq || '-'
  }
}

onMounted(() => {
  loadDefinitions()
})

// --- KPI Definitions ---
async function loadDefinitions() {
  loading.value = true
  try {
    const res = await kpiApi.getDefinitions({
      category: filterCategory.value || undefined
    })
    definitions.value = res.data.items || res.data
  } catch (e) {
    console.warn('KPI 목록 조회 실패:', e)
    ElMessage.error('KPI 목록을 불러오는데 실패했습니다')
    definitions.value = []
  } finally {
    loading.value = false
  }
}

function selectKpi(row: any) {
  selectedKpi.value = row
  activeTab.value = 'data'
  loadKpiData()
}

async function loadKpiData() {
  if (!selectedKpi.value) return
  dataLoading.value = true
  try {
    const res = await kpiApi.getData(selectedKpi.value.kpi_id)
    kpiDataList.value = res.data || []
  } catch (e) {
    console.warn('KPI 데이터 조회 실패:', e)
    ElMessage.error('KPI 데이터를 불러오는데 실패했습니다')
    kpiDataList.value = []
  } finally {
    dataLoading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    kpi_id: null,
    kpi_no: '',
    kpi_name: '',
    process_name: '',
    category: '',
    unit: '',
    target_value: null,
    target_direction: 'HIGHER',
    threshold_yellow: null,
    threshold_red: null,
    measurement_frequency: 'MONTHLY',
    responsible: '',
    formula: '',
    is_active: true
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    kpi_id: row.kpi_id,
    kpi_no: row.kpi_no || '',
    kpi_name: row.kpi_name || '',
    process_name: row.process_name || '',
    category: row.category || '',
    unit: row.unit || '',
    target_value: row.target_value ?? null,
    target_direction: row.target_direction || 'HIGHER',
    threshold_yellow: row.threshold_yellow ?? null,
    threshold_red: row.threshold_red ?? null,
    measurement_frequency: row.measurement_frequency || 'MONTHLY',
    responsible: row.responsible || '',
    formula: row.formula || '',
    is_active: row.is_active ?? true
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.kpi_no} - ${row.kpi_name}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await kpiApi.deleteDefinition(row.kpi_id)
    ElMessage.success('삭제되었습니다.')
    if (selectedKpi.value?.kpi_id === row.kpi_id) {
      selectedKpi.value = null
      kpiDataList.value = []
    }
    loadDefinitions()
  } catch {
    // cancelled or error
  }
}

async function submitForm() {
  if (!formData.value.kpi_no) {
    ElMessage.warning('KPI No.를 입력하세요.')
    return
  }
  if (!formData.value.kpi_name) {
    ElMessage.warning('KPI명을 입력하세요.')
    return
  }

  try {
    const payload = {
      kpi_no: formData.value.kpi_no,
      kpi_name: formData.value.kpi_name,
      process_name: formData.value.process_name || undefined,
      category: formData.value.category || undefined,
      unit: formData.value.unit || undefined,
      target_value: formData.value.target_value,
      target_direction: formData.value.target_direction,
      threshold_yellow: formData.value.threshold_yellow,
      threshold_red: formData.value.threshold_red,
      measurement_frequency: formData.value.measurement_frequency,
      responsible: formData.value.responsible || undefined,
      formula: formData.value.formula || undefined,
      is_active: formData.value.is_active
    }

    if (formData.value.kpi_id) {
      await kpiApi.updateDefinition(formData.value.kpi_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await kpiApi.createDefinition(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadDefinitions()
  } catch (e) {
    console.warn('KPI 정의 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// --- KPI Data ---
async function submitData() {
  if (!selectedKpi.value) return
  if (!dataForm.value.period) {
    ElMessage.warning('기간을 입력하세요. (예: 2026-01)')
    return
  }

  try {
    const payload = {
      period: dataForm.value.period,
      actual_value: dataForm.value.actual_value,
      remarks: dataForm.value.remarks || undefined
    }
    await kpiApi.addData(selectedKpi.value.kpi_id, payload)
    ElMessage.success('데이터가 추가되었습니다.')
    dataForm.value = { period: '', actual_value: 0, remarks: '' }
    loadKpiData()
    loadDefinitions()
  } catch (e) {
    console.warn('KPI 데이터 추가 실패:', e)
    ElMessage.error('데이터 추가에 실패했습니다.')
  }
}
</script>

<style scoped>
.filter-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

.data-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #E5E5E5;
}

.data-header-info h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.add-data-form {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
}
</style>
