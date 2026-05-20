<template>
  <div class="page-container">
    <PageHeader title="리스크/이슈 관리" subtitle="품질 리스크 및 기회/이슈 관리">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 리스크/이슈
        </el-button>
      </template>
    </PageHeader>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 리스크 목록 -->
      <el-tab-pane label="리스크 목록" name="list">
        <div class="filter-bar">
          <el-select
            v-model="filterIssueType"
            placeholder="유형"
            clearable
            style="width: 140px;"
            @change="loadList"
          >
            <el-option label="리스크" value="RISK" />
            <el-option label="기회" value="OPPORTUNITY" />
            <el-option label="이슈" value="ISSUE" />
          </el-select>
          <el-select
            v-model="filterStatus"
            placeholder="상태"
            clearable
            style="width: 140px;"
            @change="loadList"
          >
            <el-option label="식별" value="IDENTIFIED" />
            <el-option label="분석중" value="ANALYZING" />
            <el-option label="완화중" value="MITIGATING" />
            <el-option label="종결" value="CLOSED" />
            <el-option label="수용" value="ACCEPTED" />
          </el-select>
          <el-input
            v-model="filterCategory"
            placeholder="카테고리 검색"
            clearable
            style="width: 160px;"
            @clear="loadList"
            @keyup.enter="loadList"
          />
          <el-button @click="loadList">조회</el-button>
        </div>

        <el-table :data="tableData" border stripe v-loading="loading">
          <el-table-column prop="issue_no" label="이슈 No." width="120" />
          <el-table-column prop="issue_type" label="유형" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getIssueTypeTag(row.issue_type)" size="small">
                {{ getIssueTypeLabel(row.issue_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="카테고리" width="100" />
          <el-table-column prop="process_name" label="공정명" width="100" />
          <el-table-column prop="description" label="설명" show-overflow-tooltip />
          <el-table-column prop="severity" label="심각도" width="70" align="center" />
          <el-table-column prop="likelihood" label="발생도" width="70" align="center" />
          <el-table-column prop="risk_score" label="위험점수" width="90" align="center">
            <template #default="{ row }">
              <el-tag
                :type="getRiskScoreTagType(row.risk_score)"
                size="small"
                effect="dark"
              >
                {{ row.risk_score ?? '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="상태" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="responsible" label="담당자" width="90" />
          <el-table-column prop="target_date" label="목표일" width="110" align="center">
            <template #default="{ row }">
              {{ row.target_date || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editItem(row)">편집</el-button>
              <el-button type="danger" link size="small" @click="deleteItem(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 리스크 매트릭스 -->
      <el-tab-pane label="리스크 매트릭스" name="matrix">
        <div class="matrix-container" v-loading="matrixLoading">
          <h3 class="matrix-title">5x5 리스크 매트릭스 (심각도 x 발생도)</h3>
          <p class="matrix-subtitle">활성 리스크 건수 합계: {{ matrixTotal }}건</p>

          <table class="risk-matrix-table">
            <thead>
              <tr>
                <th class="axis-label">심각도 \ 발생도</th>
                <th v-for="l in 5" :key="l" class="col-header">{{ l }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in [5, 4, 3, 2, 1]" :key="s">
                <td class="row-header">{{ s }}</td>
                <td
                  v-for="l in 5"
                  :key="l"
                  class="matrix-cell"
                  :style="{ backgroundColor: getMatrixCellColor(s, l) }"
                >
                  <span class="cell-count" v-if="getMatrixCount(s, l) > 0">
                    {{ getMatrixCount(s, l) }}
                  </span>
                  <span class="cell-score">{{ s * l }}</span>
                </td>
              </tr>
            </tbody>
          </table>

          <div class="matrix-legend">
            <span class="legend-item">
              <span class="legend-box" style="background-color: #F56C6C;"></span> 높음 (15-25)
            </span>
            <span class="legend-item">
              <span class="legend-box" style="background-color: #E6A23C;"></span> 중간 (8-14)
            </span>
            <span class="legend-item">
              <span class="legend-box" style="background-color: #67C23A;"></span> 낮음 (1-7)
            </span>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '리스크/이슈 수정' : '새 리스크/이슈 등록'"
      width="750px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="이슈 No." required>
              <el-input v-model="formData.issue_no" placeholder="RISK-2026-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="유형" required>
              <el-select v-model="formData.issue_type" style="width: 100%;">
                <el-option label="리스크" value="RISK" />
                <el-option label="기회" value="OPPORTUNITY" />
                <el-option label="이슈" value="ISSUE" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="카테고리">
              <el-input v-model="formData.category" placeholder="품질/공정/설비" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="공정명">
              <el-input v-model="formData.process_name" placeholder="관련 공정명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="설명" required>
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="리스크/이슈에 대한 상세 설명"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="심각도 (1-5)">
              <el-input-number v-model="formData.severity" :min="1" :max="5" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="발생도 (1-5)">
              <el-input-number v-model="formData.likelihood" :min="1" :max="5" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="위험점수">
              <el-input :model-value="formData.severity * formData.likelihood" disabled style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="완화 계획">
          <el-input
            v-model="formData.mitigation_plan"
            type="textarea"
            :rows="3"
            placeholder="리스크 완화를 위한 계획"
          />
        </el-form-item>
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
            <el-form-item label="상태">
              <el-select v-model="formData.status" style="width: 100%;">
                <el-option label="식별" value="IDENTIFIED" />
                <el-option label="분석중" value="ANALYZING" />
                <el-option label="완화중" value="MITIGATING" />
                <el-option label="종결" value="CLOSED" />
                <el-option label="수용" value="ACCEPTED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">취소</el-button>
        <el-button type="primary" @click="submitForm">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { kpiApi } from '@/api/quality'

const activeTab = ref('list')
const loading = ref(false)
const matrixLoading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)

const filterIssueType = ref('')
const filterStatus = ref('')
const filterCategory = ref('')

const tableData = ref<any[]>([])
const matrixData = ref<any>({})
const matrixTotal = ref(0)

const formData = ref({
  issue_id: null as number | null,
  issue_no: '',
  issue_type: 'RISK',
  category: '',
  process_name: '',
  description: '',
  severity: 3,
  likelihood: 3,
  mitigation_plan: '',
  responsible: '',
  target_date: '',
  status: 'IDENTIFIED'
})

function getIssueTypeLabel(type: string): string {
  switch (type) {
    case 'RISK': return '리스크'
    case 'OPPORTUNITY': return '기회'
    case 'ISSUE': return '이슈'
    default: return type || '-'
  }
}

function getIssueTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (type) {
    case 'RISK': return 'danger'
    case 'OPPORTUNITY': return 'success'
    case 'ISSUE': return 'warning'
    default: return 'info'
  }
}

function getRiskScoreTagType(score: number | null): '' | 'success' | 'warning' | 'danger' | 'info' {
  if (score === null || score === undefined) return 'info'
  if (score >= 15) return 'danger'
  if (score >= 8) return 'warning'
  return 'success'
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'IDENTIFIED': return '식별'
    case 'ANALYZING': return '분석중'
    case 'MITIGATING': return '완화중'
    case 'CLOSED': return '종결'
    case 'ACCEPTED': return '수용'
    default: return status || '-'
  }
}

function getStatusTagType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'IDENTIFIED': return 'info'
    case 'ANALYZING': return 'warning'
    case 'MITIGATING': return ''
    case 'CLOSED': return 'success'
    case 'ACCEPTED': return 'success'
    default: return 'info'
  }
}

function getMatrixCellColor(severity: number, likelihood: number): string {
  const score = severity * likelihood
  if (score >= 15) return '#F56C6C'
  if (score >= 8) return '#E6A23C'
  return '#67C23A'
}

function getMatrixCount(severity: number, likelihood: number): number {
  if (!matrixData.value || !matrixData.value[severity]) return 0
  return matrixData.value[severity][likelihood] || 0
}

onMounted(() => {
  loadList()
})

watch(activeTab, (val) => {
  if (val === 'matrix') {
    loadMatrix()
  }
})

async function loadList() {
  loading.value = true
  try {
    const res = await kpiApi.getRisks({
      issue_type: filterIssueType.value || undefined,
      status: filterStatus.value || undefined,
      category: filterCategory.value || undefined
    })
    tableData.value = res.data.items || res.data
  } catch (e) {
    console.warn('리스크/이슈 목록 조회 실패:', e)
    ElMessage.error('리스크/이슈 목록을 불러오는데 실패했습니다')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

async function loadMatrix() {
  matrixLoading.value = true
  try {
    const res = await kpiApi.getRiskMatrix()
    matrixData.value = res.data.matrix || {}
    matrixTotal.value = res.data.total_risks || 0
  } catch (e) {
    console.warn('리스크 매트릭스 조회 실패:', e)
    ElMessage.error('리스크 매트릭스를 불러오는데 실패했습니다')
    matrixData.value = {}
    matrixTotal.value = 0
  } finally {
    matrixLoading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    issue_id: null,
    issue_no: '',
    issue_type: 'RISK',
    category: '',
    process_name: '',
    description: '',
    severity: 3,
    likelihood: 3,
    mitigation_plan: '',
    responsible: '',
    target_date: '',
    status: 'IDENTIFIED'
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    issue_id: row.issue_id,
    issue_no: row.issue_no || '',
    issue_type: row.issue_type || 'RISK',
    category: row.category || '',
    process_name: row.process_name || '',
    description: row.description || '',
    severity: row.severity ?? 3,
    likelihood: row.likelihood ?? 3,
    mitigation_plan: row.mitigation_plan || '',
    responsible: row.responsible || '',
    target_date: row.target_date || '',
    status: row.status || 'IDENTIFIED'
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.issue_no}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await kpiApi.deleteRisk(row.issue_id)
    ElMessage.success('삭제되었습니다.')
    loadList()
  } catch {
    // cancelled or error
  }
}

async function submitForm() {
  if (!formData.value.issue_no) {
    ElMessage.warning('이슈 No.를 입력하세요.')
    return
  }
  if (!formData.value.description) {
    ElMessage.warning('설명을 입력하세요.')
    return
  }

  try {
    const payload = {
      issue_no: formData.value.issue_no,
      issue_type: formData.value.issue_type,
      category: formData.value.category || undefined,
      process_name: formData.value.process_name || undefined,
      description: formData.value.description,
      severity: formData.value.severity,
      likelihood: formData.value.likelihood,
      mitigation_plan: formData.value.mitigation_plan || undefined,
      responsible: formData.value.responsible || undefined,
      target_date: formData.value.target_date || undefined,
      status: formData.value.status
    }

    if (formData.value.issue_id) {
      await kpiApi.updateRisk(formData.value.issue_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await kpiApi.createRisk(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('리스크/이슈 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
.filter-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.matrix-container {
  padding: 16px;
}

.matrix-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #303133;
}

.matrix-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0 0 20px 0;
}

.risk-matrix-table {
  border-collapse: collapse;
  margin: 0 auto 20px auto;
}

.risk-matrix-table th,
.risk-matrix-table td {
  border: 1px solid #DCDFE6;
  padding: 0;
  text-align: center;
  width: 80px;
  height: 60px;
}

.risk-matrix-table .axis-label {
  font-size: 12px;
  color: #606266;
  background: #F5F7FA;
  width: 120px;
  font-weight: 600;
}

.risk-matrix-table .col-header {
  background: #F5F7FA;
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.risk-matrix-table .row-header {
  background: #F5F7FA;
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.matrix-cell {
  position: relative;
  cursor: default;
  transition: opacity 0.2s;
}

.matrix-cell:hover {
  opacity: 0.85;
}

.cell-count {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.cell-score {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.matrix-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  font-size: 13px;
  color: #606266;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-box {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 3px;
}
</style>
