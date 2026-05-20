<template>
  <div class="page-container">
    <PageHeader title="공정 모니터링" subtitle="공정 모니터링 및 레이어 심사 기록">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 모니터링
        </el-button>
      </template>
    </PageHeader>

    <!-- Filter bar -->
    <div class="filter-bar">
      <el-input
        v-model="filterProcessName"
        placeholder="공정명 검색"
        clearable
        style="width: 180px;"
        @clear="loadList"
        @keyup.enter="loadList"
      />
      <el-select
        v-model="filterMonitorType"
        placeholder="모니터링 유형"
        clearable
        style="width: 160px;"
        @change="loadList"
      >
        <el-option label="정기" value="ROUTINE" />
        <el-option label="특별" value="SPECIAL" />
        <el-option label="레이어" value="LAYERED" />
      </el-select>
      <el-select
        v-model="filterResult"
        placeholder="결과"
        clearable
        style="width: 120px;"
        @change="loadList"
      >
        <el-option label="OK" value="OK" />
        <el-option label="NG" value="NG" />
        <el-option label="NA" value="NA" />
      </el-select>
      <el-select
        v-model="filterStatus"
        placeholder="상태"
        clearable
        style="width: 120px;"
        @change="loadList"
      >
        <el-option label="OPEN" value="OPEN" />
        <el-option label="진행중" value="IN_PROGRESS" />
        <el-option label="종결" value="CLOSED" />
      </el-select>
      <el-button @click="loadList">조회</el-button>
    </div>

    <!-- Monitor table -->
    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column prop="process_name" label="공정명" width="140" />
      <el-table-column prop="monitor_date" label="모니터링 일자" width="130" align="center" />
      <el-table-column prop="monitor_type" label="유형" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="getMonitorTypeTag(row.monitor_type)" size="small">
            {{ getMonitorTypeLabel(row.monitor_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="auditor" label="심사원" width="100" />
      <el-table-column prop="result" label="결과" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="getResultTagType(row.result)" size="small">
            {{ row.result }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="score" label="점수" width="80" align="right">
        <template #default="{ row }">
          {{ row.score !== null && row.score !== undefined ? row.score : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="findings" label="발견사항" show-overflow-tooltip />
      <el-table-column prop="status" label="상태" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
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
      :title="isEditing ? '공정 모니터링 수정' : '새 공정 모니터링 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="공정명" required>
              <el-input v-model="formData.process_name" placeholder="사출공정" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="모니터링 일자" required>
              <el-date-picker
                v-model="formData.monitor_date"
                type="date"
                placeholder="일자 선택"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="모니터링 유형">
              <el-select v-model="formData.monitor_type" style="width: 100%;">
                <el-option label="정기" value="ROUTINE" />
                <el-option label="특별" value="SPECIAL" />
                <el-option label="레이어" value="LAYERED" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="결과">
              <el-select v-model="formData.result" style="width: 100%;">
                <el-option label="OK" value="OK" />
                <el-option label="NG" value="NG" />
                <el-option label="NA" value="NA" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="상태">
              <el-select v-model="formData.status" style="width: 100%;">
                <el-option label="OPEN" value="OPEN" />
                <el-option label="진행중" value="IN_PROGRESS" />
                <el-option label="종결" value="CLOSED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="심사원">
              <el-input v-model="formData.auditor" placeholder="심사원명" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="점수">
              <el-input-number v-model="formData.score" :precision="1" :min="0" :max="100" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="발견사항">
          <el-input
            v-model="formData.findings"
            type="textarea"
            :rows="3"
            placeholder="발견사항을 기술하세요"
          />
        </el-form-item>
        <el-form-item label="필요 조치사항">
          <el-input
            v-model="formData.actions_required"
            type="textarea"
            :rows="3"
            placeholder="필요한 조치사항을 기술하세요"
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
import { kpiApi } from '@/api/quality'

const loading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)

const filterProcessName = ref('')
const filterMonitorType = ref('')
const filterResult = ref('')
const filterStatus = ref('')

const tableData = ref<any[]>([])

const formData = ref({
  monitor_id: null as number | null,
  process_name: '',
  monitor_date: '',
  monitor_type: 'ROUTINE',
  auditor: '',
  result: 'OK',
  score: null as number | null,
  findings: '',
  actions_required: '',
  status: 'OPEN'
})

function getMonitorTypeLabel(type: string): string {
  switch (type) {
    case 'ROUTINE': return '정기'
    case 'SPECIAL': return '특별'
    case 'LAYERED': return '레이어'
    default: return type || '-'
  }
}

function getMonitorTypeTag(type: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (type) {
    case 'ROUTINE': return ''
    case 'SPECIAL': return 'warning'
    case 'LAYERED': return 'success'
    default: return 'info'
  }
}

function getResultTagType(result: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (result) {
    case 'OK': return 'success'
    case 'NG': return 'danger'
    case 'NA': return 'info'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'OPEN': return 'OPEN'
    case 'IN_PROGRESS': return '진행중'
    case 'CLOSED': return '종결'
    default: return status || '-'
  }
}

function getStatusTagType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'danger'
    case 'IN_PROGRESS': return 'warning'
    case 'CLOSED': return 'success'
    default: return 'info'
  }
}

onMounted(() => {
  loadList()
})

async function loadList() {
  loading.value = true
  try {
    const res = await kpiApi.getMonitors({
      process_name: filterProcessName.value || undefined,
      monitor_type: filterMonitorType.value || undefined,
      result: filterResult.value || undefined,
      status: filterStatus.value || undefined
    })
    tableData.value = res.data.items || res.data
  } catch (e) {
    console.warn('공정 모니터링 목록 조회 실패:', e)
    ElMessage.error('공정 모니터링 목록을 불러오는데 실패했습니다')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    monitor_id: null,
    process_name: '',
    monitor_date: '',
    monitor_type: 'ROUTINE',
    auditor: '',
    result: 'OK',
    score: null,
    findings: '',
    actions_required: '',
    status: 'OPEN'
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    monitor_id: row.monitor_id,
    process_name: row.process_name || '',
    monitor_date: row.monitor_date || '',
    monitor_type: row.monitor_type || 'ROUTINE',
    auditor: row.auditor || '',
    result: row.result || 'OK',
    score: row.score ?? null,
    findings: row.findings || '',
    actions_required: row.actions_required || '',
    status: row.status || 'OPEN'
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.process_name} (${row.monitor_date})"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await kpiApi.deleteMonitor(row.monitor_id)
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
  if (!formData.value.process_name) {
    ElMessage.warning('공정명을 입력하세요.')
    return
  }
  if (!formData.value.monitor_date) {
    ElMessage.warning('모니터링 일자를 선택하세요.')
    return
  }

  try {
    const payload = {
      process_name: formData.value.process_name,
      monitor_date: formData.value.monitor_date,
      monitor_type: formData.value.monitor_type,
      auditor: formData.value.auditor || undefined,
      result: formData.value.result,
      score: formData.value.score,
      findings: formData.value.findings || undefined,
      actions_required: formData.value.actions_required || undefined,
      status: formData.value.status
    }

    if (formData.value.monitor_id) {
      await kpiApi.updateMonitor(formData.value.monitor_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await kpiApi.createMonitor(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('공정 모니터링 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
</style>
