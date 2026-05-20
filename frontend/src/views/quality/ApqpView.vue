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
          <el-option label="미시작" value="NOT_STARTED" />
          <el-option label="계획" value="PLANNING" />
          <el-option label="진행중" value="IN_PROGRESS" />
          <el-option label="완료" value="COMPLETED" />
        </el-select>
        <el-button type="primary" size="small" @click="loadProjectList">조회</el-button>
      </div>

      <el-table :data="projectList" border stripe v-loading="loading" @row-click="selectProject">
        <el-table-column prop="project_no" label="프로젝트번호" width="150" />
        <el-table-column prop="project_name" label="프로젝트명" min-width="200" />
        <el-table-column prop="product_name" label="제품" width="130" />
        <el-table-column prop="customer_name" label="고객사" width="130" />
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
        <el-table-column prop="sop_date" label="SOP일" width="120" align="center" />
        <el-table-column prop="team_leader" label="팀장" width="100" align="center" />
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
            <p style="margin: 4px 0; color: #6A6D70;">{{ selectedProject.product_name }} | {{ selectedProject.customer_name || '-' }}</p>
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
      <div class="card" v-for="phase in phaseDataList" :key="phase.phase_no">
        <div class="phase-header" @click="togglePhase(phase.phase_id)">
          <div class="phase-title-row">
            <el-icon v-if="expandedPhases.includes(phase.phase_id)"><ArrowDown /></el-icon>
            <el-icon v-else><ArrowRight /></el-icon>
            <span class="phase-number">Phase {{ phase.phase_no }}</span>
            <span class="phase-name">{{ phase.phase_name }}</span>
            <el-tag
              :type="phase.status === 'COMPLETED' ? 'success' : phase.status === 'IN_PROGRESS' ? 'warning' : 'info'"
              size="small"
              style="margin-left: auto;"
            >
              {{ phase.status === 'COMPLETED' ? '완료' : phase.status === 'IN_PROGRESS' ? '진행중' : '대기' }}
            </el-tag>
          </div>
        </div>

        <div v-if="expandedPhases.includes(phase.phase_id)" class="phase-deliverables">
          <el-table :data="deliverables[phase.phase_id] || []" border stripe size="small">
            <el-table-column prop="item_name" label="산출물" min-width="200" />
            <el-table-column prop="responsible" label="담당자" width="100" align="center" />
            <el-table-column prop="due_date" label="기한" width="120" align="center" />
            <el-table-column prop="status" label="상태" width="120" align="center">
              <template #default="{ row }">
                <el-select v-model="row.status" size="small" @change="updateDeliverable(row)" style="width: 100px;">
                  <el-option label="대기" value="NOT_STARTED" />
                  <el-option label="진행중" value="IN_PROGRESS" />
                  <el-option label="완료" value="COMPLETED" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!deliverables[phase.phase_id]?.length" description="산출물이 없습니다" :image-size="40" />
        </div>
      </div>
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="새 APQP 프로젝트" width="600px">
      <el-form :model="projectForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="프로젝트명" required>
              <el-input v-model="projectForm.project_name" placeholder="APQP 프로젝트명" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="프로젝트 번호">
              <el-input v-model="projectForm.project_no" placeholder="APQP-XXX-001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="제품" required>
              <el-select v-model="projectForm.product_id" filterable placeholder="제품 선택" style="width: 100%;">
                <el-option v-for="p in productOptions" :key="p.product_id" :label="p.product_name" :value="p.product_id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="고객사">
              <el-select v-model="projectForm.customer_id" filterable clearable placeholder="고객사 선택" style="width: 100%;">
                <el-option v-for="c in customerOptions" :key="c.customer_id" :label="c.customer_name" :value="c.customer_id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="SOP일">
              <el-date-picker v-model="projectForm.sop_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="상태">
              <el-select v-model="projectForm.status" style="width: 100%;">
                <el-option label="미시작" value="NOT_STARTED" />
                <el-option label="계획" value="PLANNING" />
                <el-option label="진행중" value="IN_PROGRESS" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
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
import client from '@/api/client'

const loading = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const expandedPhases = ref<number[]>([])

const projectList = ref<any[]>([])
const selectedProject = ref<any>(null)
const phaseDataList = ref<any[]>([])
const deliverables = ref<Record<number, any[]>>({})
const productOptions = ref<any[]>([])
const customerOptions = ref<any[]>([])

const phases = [
  { no: 1, title: '계획 및 정의', description: '고객 요구사항 분석, 프로그램 계획 수립' },
  { no: 2, title: '제품 설계 및 개발', description: 'DFMEA, 설계검증, 프로토타입 제작' },
  { no: 3, title: '공정 설계 및 개발', description: 'PFMEA, 관리계획서, 공정흐름도 작성' },
  { no: 4, title: '제품 및 공정 유효성 확인', description: 'MSA, SPC, PPAP, 시험 생산' },
  { no: 5, title: '양산 및 피드백', description: '양산 이행, 지속적 개선' }
]

const projectForm = ref({
  project_name: '',
  project_no: '',
  product_id: '',
  customer_id: '',
  sop_date: '',
  status: 'NOT_STARTED'
})

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'NOT_STARTED': return 'info'
    case 'PLANNING': return 'info'
    case 'IN_PROGRESS': return 'warning'
    case 'COMPLETED': return 'success'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'NOT_STARTED': return '미시작'
    case 'PLANNING': return '계획'
    case 'IN_PROGRESS': return '진행중'
    case 'COMPLETED': return '완료'
    default: return status
  }
}

onMounted(async () => {
  loadProjectList()
  try {
    const [prodRes, custRes] = await Promise.all([
      client.get('/master/products'),
      client.get('/master/customers')
    ])
    productOptions.value = prodRes.data.items || prodRes.data
    customerOptions.value = custRes.data.items || custRes.data
  } catch {
    productOptions.value = []
    customerOptions.value = []
  }
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

  try {
    const res = await apqpApi.getPhases(row.apqp_id)
    phaseDataList.value = res.data
    expandedPhases.value = []

    // Load deliverables for each phase
    for (const phase of res.data) {
      if (phase.phase_id) {
        try {
          const delRes = await apqpApi.getDeliverables(phase.phase_id)
          deliverables.value[phase.phase_id] = delRes.data
        } catch {
          deliverables.value[phase.phase_id] = []
        }
      }
    }

    // Auto-expand current phase
    const currentPhase = res.data.find((p: any) => p.phase_no === row.current_phase)
    if (currentPhase) {
      expandedPhases.value = [currentPhase.phase_id]
    }
  } catch (e) {
    console.warn('APQP 단계 정보 조회 실패:', e)
    ElMessage.error('APQP 단계 정보를 불러오는데 실패했습니다')
    phaseDataList.value = []
    deliverables.value = {}
  }
}

function togglePhase(phaseId: number) {
  const idx = expandedPhases.value.indexOf(phaseId)
  if (idx >= 0) {
    expandedPhases.value.splice(idx, 1)
  } else {
    expandedPhases.value.push(phaseId)
  }
}

async function updateDeliverable(deliverable: any) {
  try {
    await apqpApi.updateDeliverable(deliverable.deliverable_id, { status: deliverable.status })
  } catch {
    // silent
  }
}

async function createProject() {
  if (!projectForm.value.project_name || !projectForm.value.product_id) {
    ElMessage.warning('프로젝트명과 제품을 입력하세요.')
    return
  }
  try {
    await apqpApi.create(projectForm.value)
    ElMessage.success('APQP 프로젝트가 생성되었습니다.')
    showCreateDialog.value = false
    projectForm.value = { project_name: '', project_no: '', product_id: '', customer_id: '', sop_date: '', status: 'NOT_STARTED' }
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
