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
        <el-button type="primary" size="small" @click="loadClaimList">조회</el-button>
      </div>

      <el-table :data="claimList" border stripe v-loading="loading" @row-click="selectClaim">
        <el-table-column prop="claim_id" label="클레임 ID" width="150" />
        <el-table-column prop="customer_name" label="고객사" width="130" />
        <el-table-column prop="product_name" label="제품명" width="130" />
        <el-table-column prop="description" label="문제 설명" min-width="200" />
        <el-table-column prop="status" label="상태" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getClaimStatusType(row.status)" size="small">{{ getClaimStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="defect_type" label="불량유형" width="100" align="center" />
        <el-table-column prop="claim_date" label="접수일" width="120" align="center" />
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
            <h3 style="margin: 8px 0 0 0;">{{ selectedClaim.claim_id }} - {{ selectedClaim.description }}</h3>
            <p style="margin: 4px 0; color: #6A6D70;">고객: {{ selectedClaim.customer_name }} | 제품: {{ selectedClaim.product_name }}</p>
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <el-tag :type="getClaimStatusType(selectedClaim.status)" effect="dark">{{ getClaimStatusLabel(selectedClaim.status) }}</el-tag>
          </div>
        </div>
      </div>

      <div class="card">
        <EightDStepper
          :claim="selectedClaim"
          :active-step="getCurrentStep(selectedClaim) - 1"
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
            <el-form-item label="클레임 ID" required>
              <el-input v-model="claimForm.claim_id" placeholder="CLM-2026-XXX" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="고객 ID" required>
              <el-input v-model="claimForm.customer_id" placeholder="C001" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="제품 ID">
              <el-input v-model="claimForm.product_id" placeholder="P001" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="불량유형">
              <el-select v-model="claimForm.defect_type" style="width: 100%;">
                <el-option label="치수불량" value="치수불량" />
                <el-option label="외관불량" value="외관불량" />
                <el-option label="기능불량" value="기능불량" />
                <el-option label="기타" value="기타" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="불량 수량">
              <el-input-number v-model="claimForm.claim_qty" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">D1 - 팀 구성</el-divider>
        <el-form-item label="팀 구성원 (쉼표 구분)">
          <el-input v-model="claimForm.team_members" />
        </el-form-item>

        <el-divider content-position="left">D2 - 문제 기술</el-divider>
        <el-form-item label="문제 설명" required>
          <el-input v-model="claimForm.description" />
        </el-form-item>
        <el-form-item label="문제 정의 (상세)">
          <el-input v-model="claimForm.problem_definition" type="textarea" :rows="4" placeholder="5W2H: What, When, Where, Who, Why, How, How many" />
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
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import EightDStepper from '@/components/quality/EightDStepper.vue'
import { claimApi } from '@/api/quality'
import dayjs from 'dayjs'

const loading = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)

const claimList = ref<any[]>([])
const selectedClaim = ref<any>(null)

const claimForm = ref({
  claim_id: '',
  customer_id: '',
  product_id: '',
  description: '',
  defect_type: '',
  claim_qty: 0,
  team_members: '',
  problem_definition: '',
  claim_date: dayjs().format('YYYY-MM-DD')
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

function getCurrentStep(claim: any): number {
  if (claim.close_date) return 8
  if (claim.deployment_targets) return 7
  if (claim.verification_result) return 6
  if (claim.countermeasure) return 5
  if (claim.root_cause) return 4
  if (claim.immediate_action) return 3
  return 2
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
    const res = await claimApi.getById(row.claim_id)
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
    const res = await claimApi.updateStep(selectedClaim.value.claim_id, step, data)
    ElMessage.success(`D${step} 단계가 저장되었습니다.`)
    selectedClaim.value = res.data
  } catch (e) {
    console.warn(`D${step} 단계 저장 실패:`, e)
    ElMessage.error(`D${step} 단계 저장에 실패했습니다`)
  }
}

async function handleComplete() {
  if (!selectedClaim.value) return
  try {
    const res = await claimApi.updateStep(selectedClaim.value.claim_id, 8, {
      status: 'CLOSED',
      close_date: dayjs().format('YYYY-MM-DD')
    })
    ElMessage.success('8D가 종결되었습니다.')
    selectedClaim.value = res.data
  } catch (e) {
    console.warn('8D 종결 처리 실패:', e)
    ElMessage.error('8D 종결 처리에 실패했습니다')
  }
}

async function createClaim() {
  if (!claimForm.value.claim_id || !claimForm.value.customer_id || !claimForm.value.description) {
    ElMessage.warning('필수항목을 입력하세요.')
    return
  }
  try {
    await claimApi.create({
      ...claimForm.value,
      status: 'OPEN'
    })
    ElMessage.success('클레임이 접수되었습니다.')
    showCreateDialog.value = false
    claimForm.value = { claim_id: '', customer_id: '', product_id: '', description: '', defect_type: '', claim_qty: 0, team_members: '', problem_definition: '', claim_date: dayjs().format('YYYY-MM-DD') }
    loadClaimList()
  } catch {
    ElMessage.error('접수에 실패했습니다.')
  }
}
</script>
