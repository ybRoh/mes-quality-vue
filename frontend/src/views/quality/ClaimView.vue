<template>
  <div class="page-container">
    <PageHeader title="클레임 관리 (8D)" subtitle="고객 클레임 접수 및 8D 프로세스 관리">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          새 클레임
        </el-button>
      </template>
    </PageHeader>

    <!-- Claim List -->
    <div class="card" v-if="!selectedClaim">
      <div class="filter-bar">
        <el-select v-model="filterStatus" placeholder="상태 선택" clearable style="width: 150px;">
          <el-option label="접수" value="OPEN" />
          <el-option label="진행중" value="IN_PROGRESS" />
          <el-option label="종결" value="CLOSED" />
        </el-select>
        <DateRangePicker v-model="dateRange" />
        <el-button type="primary" size="small" @click="loadClaimList">조회</el-button>
      </div>

      <el-table :data="claimList" border stripe v-loading="loading" @row-click="selectClaim">
        <el-table-column prop="claim_no" label="클레임 번호" width="150" />
        <el-table-column prop="customer" label="고객사" width="130" />
        <el-table-column prop="product_spec" label="제품규격" width="130" />
        <el-table-column prop="problem_title" label="문제 제목" min-width="200" />
        <el-table-column prop="status" label="상태" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getClaimStatusType(row.status)" size="small">{{ getClaimStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_step" label="단계" width="80" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small" effect="plain">D{{ row.current_step }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity_level" label="심각도" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.severity_level === 'HIGH' ? 'danger' : row.severity_level === 'MEDIUM' ? 'warning' : 'success'" size="small">
              {{ row.severity_level === 'HIGH' ? '높음' : row.severity_level === 'MEDIUM' ? '중간' : '낮음' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="접수일" width="120" align="center" />
        <el-table-column label="작업" width="80" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click.stop="deleteClaim(row)">삭제</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Claim Detail (8D Stepper) -->
    <div v-if="selectedClaim">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <el-button link @click="selectedClaim = null">
              <el-icon><Back /></el-icon>
              목록으로
            </el-button>
            <h3 style="margin: 8px 0 0 0;">{{ selectedClaim.claim_no }} - {{ selectedClaim.problem_title }}</h3>
            <p style="margin: 4px 0; color: #6A6D70;">고객: {{ selectedClaim.customer }} | 제품: {{ selectedClaim.product_spec }}</p>
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <el-tag :type="getClaimStatusType(selectedClaim.status)" effect="dark">{{ getClaimStatusLabel(selectedClaim.status) }}</el-tag>
          </div>
        </div>
      </div>

      <div class="card">
        <EightDStepper
          :claim="selectedClaim"
          :active-step="(selectedClaim.current_step || 1) - 1"
          @save="handleStepSave"
          @complete="handleComplete"
        />
      </div>
    </div>

    <!-- Create Dialog (D1/D2) -->
    <el-dialog v-model="showCreateDialog" title="새 클레임 접수" width="700px" top="5vh">
      <el-form :model="claimForm" label-position="top">
        <el-divider content-position="left">기본 정보</el-divider>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="클레임 번호" required>
              <el-input v-model="claimForm.claim_no" placeholder="CLM-2026-XXX" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="고객사" required>
              <el-input v-model="claimForm.customer" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="제품규격" required>
              <el-input v-model="claimForm.product_spec" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="심각도">
              <el-select v-model="claimForm.severity_level" style="width: 100%;">
                <el-option label="높음" value="HIGH" />
                <el-option label="중간" value="MEDIUM" />
                <el-option label="낮음" value="LOW" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="불량 수량">
              <el-input-number v-model="claimForm.defect_qty" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">D1 - 팀 구성</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="팀장">
              <el-input v-model="claimForm.d1_team_leader" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="팀원 (쉼표 구분)">
              <el-input v-model="claimForm.d1_team_members" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">D2 - 문제 기술</el-divider>
        <el-form-item label="문제 제목" required>
          <el-input v-model="claimForm.problem_title" />
        </el-form-item>
        <el-form-item label="문제 상세">
          <el-input v-model="claimForm.d2_problem_description" type="textarea" :rows="4" placeholder="5W2H: What, When, Where, Who, Why, How, How many" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="createClaim">접수</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Back } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import DateRangePicker from '@/components/common/DateRangePicker.vue'
import EightDStepper from '@/components/quality/EightDStepper.vue'
import { claimApi } from '@/api/quality'
import dayjs from 'dayjs'

const loading = ref(false)
const filterStatus = ref('')
const dateRange = ref<[string, string] | null>(null)
const showCreateDialog = ref(false)

const claimList = ref<any[]>([])
const selectedClaim = ref<any>(null)

const claimForm = ref({
  claim_no: '',
  customer: '',
  product_spec: '',
  problem_title: '',
  severity_level: 'MEDIUM',
  defect_qty: 0,
  d1_team_leader: '',
  d1_team_members: '',
  d2_problem_description: ''
})

function getClaimStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'danger'
    case 'IN_PROGRESS': return 'warning'
    case 'CLOSED': return 'success'
    default: return 'info'
  }
}

function getClaimStatusLabel(status: string): string {
  switch (status) {
    case 'OPEN': return '접수'
    case 'IN_PROGRESS': return '진행중'
    case 'CLOSED': return '종결'
    default: return status
  }
}

onMounted(() => {
  loadClaimList()
})

async function loadClaimList() {
  loading.value = true
  try {
    const params: any = {}
    if (filterStatus.value) params.status = filterStatus.value
    const res = await claimApi.getList(params)
    claimList.value = res.data.items || res.data
  } catch (e) {
    console.warn('클레임 목록 조회 실패:', e)
    ElMessage.error('클레임 목록을 불러오는데 실패했습니다')
    claimList.value = []
  } finally {
    loading.value = false
  }
}

async function selectClaim(row: any) {
  try {
    const res = await claimApi.getById(row.id)
    selectedClaim.value = res.data
  } catch (e) {
    console.warn('클레임 상세 조회 실패:', e)
    ElMessage.error('클레임 상세 정보를 불러오는데 실패했습니다')
    selectedClaim.value = null
  }
}

async function handleStepSave(step: number, data: Record<string, any>) {
  if (!selectedClaim.value) return
  try {
    await claimApi.updateStep(selectedClaim.value.id, step, data)
    ElMessage.success(`D${step} 단계가 저장되었습니다.`)
    selectedClaim.value = { ...selectedClaim.value, ...data, current_step: Math.max(selectedClaim.value.current_step, step) }
  } catch (e) {
    console.warn(`D${step} 단계 저장 실패:`, e)
    ElMessage.error(`D${step} 단계 저장에 실패했습니다`)
  }
}

async function handleComplete() {
  if (!selectedClaim.value) return
  try {
    await claimApi.update(selectedClaim.value.id, { ...selectedClaim.value, status: 'CLOSED', current_step: 8 })
    ElMessage.success('8D가 종결되었습니다.')
    selectedClaim.value.status = 'CLOSED'
    selectedClaim.value.current_step = 8
  } catch (e) {
    console.warn('8D 종결 처리 실패:', e)
    ElMessage.error('8D 종결 처리에 실패했습니다')
  }
}

async function deleteClaim(row: any) {
  try {
    await ElMessageBox.confirm(`"${row.claim_no}"을(를) 삭제하시겠습니까?`, '삭제 확인', { type: 'warning' })
    await claimApi.delete(row.id)
    ElMessage.success('삭제되었습니다.')
    loadClaimList()
  } catch { /* cancelled */ }
}

async function createClaim() {
  if (!claimForm.value.claim_no || !claimForm.value.customer || !claimForm.value.problem_title) {
    ElMessage.warning('필수항목을 입력하세요.')
    return
  }
  try {
    await claimApi.create({
      ...claimForm.value,
      status: 'OPEN',
      current_step: 2,
      created_at: dayjs().format('YYYY-MM-DD')
    })
    ElMessage.success('클레임이 접수되었습니다.')
    showCreateDialog.value = false
    claimForm.value = { claim_no: '', customer: '', product_spec: '', problem_title: '', severity_level: 'MEDIUM', defect_qty: 0, d1_team_leader: '', d1_team_members: '', d2_problem_description: '' }
    loadClaimList()
  } catch {
    ElMessage.error('접수에 실패했습니다.')
  }
}
</script>
