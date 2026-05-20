<template>
  <div class="page-container">
    <PageHeader title="APQP (사전품질계획)" subtitle="제품 품질 사전기획 프로젝트 관리">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          새 APQP 프로젝트
        </el-button>
      </template>
    </PageHeader>

    <!-- Project List -->
    <div class="card" v-if="!selectedProject">
      <div class="filter-bar">
        <el-select v-model="filterStatus" placeholder="상태 선택" clearable style="width: 150px;">
          <el-option label="계획" value="PLANNING" />
          <el-option label="진행중" value="IN_PROGRESS" />
          <el-option label="완료" value="COMPLETED" />
        </el-select>
        <el-button type="primary" size="small" @click="loadProjectList">조회</el-button>
      </div>

      <el-table :data="projectList" border stripe v-loading="loading" @row-click="selectProject">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="project_name" label="프로젝트명" min-width="200" />
        <el-table-column prop="product_name" label="제품" width="130" />
        <el-table-column prop="customer" label="고객사" width="130" />
        <el-table-column prop="current_phase" label="현재 단계" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">Phase {{ row.current_phase }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="상태" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="시작일" width="120" align="center" />
        <el-table-column prop="target_date" label="목표일" width="120" align="center" />
      </el-table>
    </div>

    <!-- Project Detail -->
    <div v-if="selectedProject">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <el-button link @click="selectedProject = null">
              <el-icon><Back /></el-icon>
              목록으로
            </el-button>
            <h3 style="margin: 8px 0 0 0;">{{ selectedProject.project_name }}</h3>
            <p style="margin: 4px 0; color: #6A6D70;">{{ selectedProject.product_name }} | {{ selectedProject.customer }}</p>
          </div>
          <el-tag :type="getStatusType(selectedProject.status)" effect="dark">{{ getStatusLabel(selectedProject.status) }}</el-tag>
        </div>
      </div>

      <!-- Phase Timeline -->
      <div class="card">
        <div class="card-title">APQP 5단계 진행 현황</div>
        <el-steps :active="selectedProject.current_phase - 1" finish-status="success" align-center>
          <el-step v-for="phase in phases" :key="phase.no" :title="phase.title" :description="phase.description">
            <template #icon>
              <div class="phase-icon" :class="{ 'phase-active': phase.no === selectedProject.current_phase, 'phase-done': phase.no < selectedProject.current_phase }">
                {{ phase.no }}
              </div>
            </template>
          </el-step>
        </el-steps>
      </div>

      <!-- Phase Details with Deliverables -->
      <div class="card" v-for="phase in phases" :key="phase.no">
        <div class="phase-header" @click="togglePhase(phase.no)">
          <div class="phase-title-row">
            <el-icon v-if="expandedPhases.includes(phase.no)"><ArrowDown /></el-icon>
            <el-icon v-else><ArrowRight /></el-icon>
            <span class="phase-number">Phase {{ phase.no }}</span>
            <span class="phase-name">{{ phase.title }}</span>
            <el-tag
              :type="phase.no < selectedProject.current_phase ? 'success' : phase.no === selectedProject.current_phase ? 'warning' : 'info'"
              size="small"
              style="margin-left: auto;"
            >
              {{ phase.no < selectedProject.current_phase ? '완료' : phase.no === selectedProject.current_phase ? '진행중' : '대기' }}
            </el-tag>
          </div>
          <p class="phase-desc">{{ phase.description }}</p>
        </div>

        <div v-if="expandedPhases.includes(phase.no)" class="phase-deliverables">
          <el-table :data="getPhaseDeliverables(phase.no)" border stripe size="small">
            <el-table-column prop="deliverable_name" label="산출물" min-width="200" />
            <el-table-column prop="responsible" label="담당자" width="100" align="center" />
            <el-table-column prop="due_date" label="기한" width="120" align="center" />
            <el-table-column prop="status" label="상태" width="120" align="center">
              <template #default="{ row }">
                <el-select v-model="row.status" size="small" @change="updateDeliverable(row)" style="width: 100px;">
                  <el-option label="대기" value="PENDING" />
                  <el-option label="진행중" value="IN_PROGRESS" />
                  <el-option label="완료" value="COMPLETED" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- Gate Review -->
      <div class="card">
        <div class="card-title">Gate Review 현황</div>
        <el-table :data="gateReviews" border stripe size="small">
          <el-table-column prop="gate" label="Gate" width="100" align="center" />
          <el-table-column prop="review_date" label="검토일" width="120" align="center" />
          <el-table-column prop="result" label="결과" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.result" :type="row.result === 'PASS' ? 'success' : 'danger'" size="small">
                {{ row.result === 'PASS' ? '통과' : '불통과' }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="remarks" label="비고" min-width="200" />
        </el-table>
      </div>
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="새 APQP 프로젝트" width="600px">
      <el-form :model="projectForm" label-position="top">
        <el-form-item label="프로젝트명" required>
          <el-input v-model="projectForm.project_name" placeholder="APQP 프로젝트명" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="제품명" required>
              <el-input v-model="projectForm.product_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="고객사">
              <el-input v-model="projectForm.customer" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="시작일">
              <el-date-picker v-model="projectForm.start_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="목표 완료일">
              <el-date-picker v-model="projectForm.target_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="비고">
          <el-input v-model="projectForm.remarks" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="createProject">생성</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Back, ArrowDown, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { apqpApi } from '@/api/quality'

const loading = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const expandedPhases = ref<number[]>([])

const projectList = ref<any[]>([])
const selectedProject = ref<any>(null)
const deliverables = ref<Record<number, any[]>>({})
const gateReviews = ref<any[]>([])

const phases = [
  { no: 1, title: '계획 및 정의', description: '고객 요구사항 분석, 프로그램 계획 수립' },
  { no: 2, title: '제품 설계 및 개발', description: 'DFMEA, 설계검증, 프로토타입 제작' },
  { no: 3, title: '공정 설계 및 개발', description: 'PFMEA, 관리계획서, 공정흐름도 작성' },
  { no: 4, title: '제품 및 공정 유효성 확인', description: 'MSA, SPC, PPAP, 시험 생산' },
  { no: 5, title: '양산 및 피드백', description: '양산 이행, 지속적 개선' }
]

const projectForm = ref({
  project_name: '',
  product_name: '',
  customer: '',
  start_date: '',
  target_date: '',
  remarks: ''
})

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'PLANNING': return 'info'
    case 'IN_PROGRESS': return 'warning'
    case 'COMPLETED': return 'success'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'PLANNING': return '계획'
    case 'IN_PROGRESS': return '진행중'
    case 'COMPLETED': return '완료'
    default: return status
  }
}

onMounted(() => {
  loadProjectList()
})

async function loadProjectList() {
  loading.value = true
  try {
    const res = await apqpApi.getList({ status: filterStatus.value || undefined })
    projectList.value = res.data.items || res.data
  } catch (e) {
    console.warn('APQP 프로젝트 목록 조회 실패:', e)
    ElMessage.error('APQP 프로젝트 목록을 불러오는데 실패했습니다')
    projectList.value = []
  } finally {
    loading.value = false
  }
}

async function selectProject(row: any) {
  selectedProject.value = row
  expandedPhases.value = [row.current_phase]

  try {
    const res = await apqpApi.getPhases(row.id)
    const phaseData = res.data
    phaseData.forEach((p: any) => {
      deliverables.value[p.phase_number] = p.deliverables || []
    })
  } catch (e) {
    console.warn('APQP 단계 정보 조회 실패:', e)
    ElMessage.error('APQP 단계 정보를 불러오는데 실패했습니다')
    deliverables.value = {}
  }

  // Gate reviews
  gateReviews.value = [
    { gate: 'Gate 1', review_date: '2026-03-01', result: 'PASS', remarks: '요구사항 정의 완료' },
    { gate: 'Gate 2', review_date: '2026-05-01', result: 'PASS', remarks: '설계 검증 완료' },
    { gate: 'Gate 3', review_date: '', result: null, remarks: '예정: 2026-06-30' },
    { gate: 'Gate 4', review_date: '', result: null, remarks: '예정: 2026-07-30' },
    { gate: 'Gate 5', review_date: '', result: null, remarks: '예정: 2026-09-30' }
  ]
}

function getPhaseDeliverables(phaseNo: number): any[] {
  return deliverables.value[phaseNo] || []
}

function togglePhase(phaseNo: number) {
  const idx = expandedPhases.value.indexOf(phaseNo)
  if (idx >= 0) {
    expandedPhases.value.splice(idx, 1)
  } else {
    expandedPhases.value.push(phaseNo)
  }
}

async function updateDeliverable(deliverable: any) {
  if (!selectedProject.value) return
  try {
    await apqpApi.updateDeliverable(selectedProject.value.id, deliverable.id, deliverable)
  } catch {
    // silent
  }
}

async function createProject() {
  if (!projectForm.value.project_name || !projectForm.value.product_name) {
    ElMessage.warning('필수항목을 입력하세요.')
    return
  }
  try {
    await apqpApi.create(projectForm.value)
    ElMessage.success('APQP 프로젝트가 생성되었습니다.')
    showCreateDialog.value = false
    projectForm.value = { project_name: '', product_name: '', customer: '', start_date: '', target_date: '', remarks: '' }
    loadProjectList()
  } catch {
    ElMessage.error('생성에 실패했습니다.')
  }
}
</script>

<style scoped>
.phase-header {
  cursor: pointer;
  padding: 8px 0;
}

.phase-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.phase-number {
  font-weight: 700;
  color: #0A6ED1;
}

.phase-name {
  font-weight: 500;
  font-size: 15px;
}

.phase-desc {
  margin: 4px 0 0 24px;
  font-size: 13px;
  color: #6A6D70;
}

.phase-deliverables {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #E5E5E5;
}

.phase-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  background: #E5E5E5;
  color: #6A6D70;
}

.phase-icon.phase-active {
  background: #0A6ED1;
  color: #FFFFFF;
}

.phase-icon.phase-done {
  background: #107E3E;
  color: #FFFFFF;
}
</style>
