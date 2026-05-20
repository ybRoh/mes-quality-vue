<template>
  <div class="ppap-checklist">
    <div class="ppap-summary">
      <div class="ppap-progress-info">
        <span class="ppap-label">제출 Level: </span>
        <el-tag :type="levelTagType" effect="dark">Level {{ submissionLevel }}</el-tag>
        <span class="ppap-label" style="margin-left: 20px;">완료율: </span>
        <el-progress
          :percentage="completionPct"
          :status="completionPct === 100 ? 'success' : ''"
          :stroke-width="18"
          :text-inside="true"
          style="width: 200px; display: inline-flex; margin-left: 8px;"
        />
      </div>
    </div>

    <el-table :data="localElements" border stripe style="width: 100%;">
      <el-table-column label="No" prop="element_no" width="60" align="center" />

      <el-table-column label="PPAP 요소" prop="element_name" min-width="250">
        <template #default="{ row }">
          <span :class="{ 'required-element': row.is_required }">{{ row.element_name }}</span>
        </template>
      </el-table-column>

      <el-table-column label="필수" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_required" type="danger" size="small">필수</el-tag>
          <el-tag v-else type="info" size="small">선택</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="상태" width="160" align="center">
        <template #default="{ row }">
          <el-select v-model="row.status" size="small" @change="handleStatusChange(row)" style="width: 130px;">
            <el-option label="미착수" value="NOT_STARTED" />
            <el-option label="진행중" value="IN_PROGRESS" />
            <el-option label="완료" value="COMPLETED" />
            <el-option label="해당없음" value="N/A" />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column label="문서번호/참조" min-width="180">
        <template #default="{ row }">
          <el-input v-model="row.document_ref" size="small" placeholder="문서번호 입력" @change="handleStatusChange(row)" />
        </template>
      </el-table-column>

      <el-table-column label="상태" width="60" align="center">
        <template #default="{ row }">
          <el-icon v-if="row.status === 'COMPLETED'" :size="18" color="#107E3E"><CircleCheckFilled /></el-icon>
          <el-icon v-else-if="row.status === 'IN_PROGRESS'" :size="18" color="#E9730C"><Loading /></el-icon>
          <el-icon v-else-if="row.status === 'N/A'" :size="18" color="#6A6D70"><RemoveFilled /></el-icon>
          <el-icon v-else :size="18" color="#C0C4CC"><CircleCloseFilled /></el-icon>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CircleCheckFilled, Loading, RemoveFilled, CircleCloseFilled } from '@element-plus/icons-vue'

interface PpapElement {
  element_no: number
  element_name: string
  is_required: boolean
  status: string
  document_ref: string
}

interface Props {
  elements?: PpapElement[]
  submissionLevel?: number
}

const props = withDefaults(defineProps<Props>(), {
  elements: () => getDefaultElements(),
  submissionLevel: 3
})

const emit = defineEmits<{
  'update:elements': [elements: PpapElement[]]
  change: [element: PpapElement]
}>()

const localElements = ref<PpapElement[]>([])

watch(() => props.elements, (val) => {
  localElements.value = val.map(e => ({ ...e }))
  updateRequiredByLevel()
}, { immediate: true, deep: true })

watch(() => props.submissionLevel, () => {
  updateRequiredByLevel()
})

const completionPct = computed(() => {
  const required = localElements.value.filter(e => e.is_required)
  if (required.length === 0) return 0
  const completed = required.filter(e => e.status === 'COMPLETED' || e.status === 'N/A').length
  return Math.round((completed / required.length) * 100)
})

const levelTagType = computed(() => {
  switch (props.submissionLevel) {
    case 1: return 'info'
    case 2: return ''
    case 3: return 'warning'
    case 4: return 'danger'
    case 5: return 'danger'
    default: return 'info'
  }
})

function updateRequiredByLevel() {
  const level = props.submissionLevel
  // Level 3 requires all; other levels require a subset
  const level1Required = [1, 18]
  const level2Required = [1, 2, 4, 7, 9, 11, 13, 18]
  const level4Required = [1, 18]
  const level5Required: number[] = []

  localElements.value.forEach(e => {
    if (level === 3) {
      e.is_required = true
    } else if (level === 1) {
      e.is_required = level1Required.includes(e.element_no)
    } else if (level === 2) {
      e.is_required = level2Required.includes(e.element_no)
    } else if (level === 4) {
      e.is_required = level4Required.includes(e.element_no)
    } else if (level === 5) {
      e.is_required = level5Required.includes(e.element_no)
    }
  })
}

function handleStatusChange(element: PpapElement) {
  emit('change', { ...element })
  emit('update:elements', localElements.value.map(e => ({ ...e })))
}

function getDefaultElements(): PpapElement[] {
  const names = [
    '설계기록 (Design Records)',
    '기술변경 문서 (Engineering Change Documents)',
    '고객 기술승인 (Customer Engineering Approval)',
    '설계 FMEA (Design FMEA)',
    '공정 흐름도 (Process Flow Diagram)',
    '공정 FMEA (Process FMEA)',
    '관리계획서 (Control Plan)',
    'MSA (Measurement System Analysis)',
    '치수검사 결과 (Dimensional Results)',
    '재료/성능 시험 결과 (Material/Performance Test Results)',
    '초기 공정능력 조사 (Initial Process Studies)',
    '공인시험소 문서 (Qualified Laboratory Documentation)',
    '외관승인 보고서 (AAR - Appearance Approval Report)',
    '양산시료 (Sample Production Parts)',
    '마스터 시료 (Master Sample)',
    '검사구 (Checking Aids)',
    '고객 고유 요구사항 (Customer-Specific Requirements)',
    'PSW (Part Submission Warrant)'
  ]
  return names.map((name, i) => ({
    element_no: i + 1,
    element_name: name,
    is_required: true,
    status: 'NOT_STARTED',
    document_ref: ''
  }))
}
</script>

<style scoped>
.ppap-checklist {
  width: 100%;
}

.ppap-summary {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--qms-bg-light);
  border-radius: 8px;
  border: 1px solid var(--qms-border);
}

.ppap-progress-info {
  display: flex;
  align-items: center;
}

.ppap-label {
  font-weight: 500;
  color: var(--qms-text-primary);
}

.required-element {
  font-weight: 500;
}
</style>
