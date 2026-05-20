<template>
  <div class="fmea-matrix">
    <div class="fmea-toolbar">
      <el-button type="primary" size="small" @click="addRow" aria-label="FMEA 항목 추가">
        <el-icon><Plus /></el-icon>
        행 추가
      </el-button>
      <el-button size="small" @click="emit('save', localItems)">
        <el-icon><Check /></el-icon>
        저장
      </el-button>
    </div>

    <el-table
      :data="localItems"
      border
      stripe
      :max-height="600"
      style="width: 100%"
      class="fmea-table"
    >
      <!-- 공정단계 -->
      <el-table-column label="공정단계" width="130" fixed="left">
        <template #default="{ row }">
          <el-input v-model="row.process_step" size="small" placeholder="공정단계" />
        </template>
      </el-table-column>

      <!-- 고장모드 -->
      <el-table-column label="잠재적 고장모드" width="160">
        <template #default="{ row }">
          <el-input v-model="row.failure_mode" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" size="small" placeholder="고장모드" />
        </template>
      </el-table-column>

      <!-- 고장영향 -->
      <el-table-column label="잠재적 고장영향" width="160">
        <template #default="{ row }">
          <el-input v-model="row.failure_effect" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" size="small" placeholder="고장영향" />
        </template>
      </el-table-column>

      <!-- 심각도 S -->
      <el-table-column label="심각도(S)" width="90" align="center">
        <template #default="{ row }">
          <el-input-number v-model="row.severity" :min="1" :max="10" size="small" controls-position="right" @change="calculateRpn(row)" />
        </template>
      </el-table-column>

      <!-- 고장원인 -->
      <el-table-column label="잠재적 고장원인" width="160">
        <template #default="{ row }">
          <el-input v-model="row.failure_cause" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" size="small" placeholder="고장원인" />
        </template>
      </el-table-column>

      <!-- 발생도 O -->
      <el-table-column label="발생도(O)" width="90" align="center">
        <template #default="{ row }">
          <el-input-number v-model="row.occurrence" :min="1" :max="10" size="small" controls-position="right" @change="calculateRpn(row)" />
        </template>
      </el-table-column>

      <!-- 현재관리방법 (예방) -->
      <el-table-column label="현재관리(예방)" width="150">
        <template #default="{ row }">
          <el-input v-model="row.current_control_prevent" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" size="small" placeholder="예방관리" />
        </template>
      </el-table-column>

      <!-- 현재관리방법 (검출) -->
      <el-table-column label="현재관리(검출)" width="150">
        <template #default="{ row }">
          <el-input v-model="row.current_control_detect" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" size="small" placeholder="검출관리" />
        </template>
      </el-table-column>

      <!-- 검출도 D -->
      <el-table-column label="검출도(D)" width="90" align="center">
        <template #default="{ row }">
          <el-input-number v-model="row.detection" :min="1" :max="10" size="small" controls-position="right" @change="calculateRpn(row)" />
        </template>
      </el-table-column>

      <!-- RPN -->
      <el-table-column label="RPN" width="80" align="center" fixed="right">
        <template #default="{ row }">
          <el-tag
            :type="getRpnTagType(row.rpn)"
            effect="dark"
            size="default"
            style="font-weight: 700; font-size: 14px;"
          >
            {{ row.rpn || 0 }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- AP -->
      <el-table-column label="AP" width="60" align="center" fixed="right">
        <template #default="{ row }">
          <el-tag
            :type="getApTagType(row.ap)"
            size="small"
            effect="plain"
          >
            {{ row.ap || '-' }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 권고조치 -->
      <el-table-column label="권고조치사항" width="180" fixed="right">
        <template #default="{ row }">
          <el-input v-model="row.recommended_action" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" size="small" placeholder="권고조치" />
        </template>
      </el-table-column>

      <!-- 삭제 -->
      <el-table-column label="" width="50" align="center" fixed="right">
        <template #default="{ $index }">
          <el-button type="danger" link size="small" @click="removeRow($index)" aria-label="항목 삭제">
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Check, Delete } from '@element-plus/icons-vue'

interface FmeaItem {
  id?: number
  process_step: string
  failure_mode: string
  failure_effect: string
  severity: number
  failure_cause: string
  occurrence: number
  current_control_prevent: string
  current_control_detect: string
  detection: number
  rpn: number
  ap: string
  recommended_action: string
}

interface Props {
  items: FmeaItem[]
}

const props = withDefaults(defineProps<Props>(), {
  items: () => []
})

const emit = defineEmits<{
  save: [items: FmeaItem[]]
  'update:items': [items: FmeaItem[]]
}>()

const localItems = ref<FmeaItem[]>([])

watch(() => props.items, (val) => {
  localItems.value = val.map(item => ({ ...item }))
}, { immediate: true, deep: true })

function createEmptyRow(): FmeaItem {
  return {
    process_step: '',
    failure_mode: '',
    failure_effect: '',
    severity: 1,
    failure_cause: '',
    occurrence: 1,
    current_control_prevent: '',
    current_control_detect: '',
    detection: 1,
    rpn: 1,
    ap: 'L',
    recommended_action: ''
  }
}

function addRow() {
  localItems.value.push(createEmptyRow())
}

function removeRow(index: number) {
  localItems.value.splice(index, 1)
}

function calculateRpn(row: FmeaItem) {
  const s = row.severity || 1
  const o = row.occurrence || 1
  const d = row.detection || 1
  row.rpn = s * o * d
  row.ap = determineAp(row.rpn, s)
}

function determineAp(rpn: number, severity: number): string {
  if (rpn >= 200 || severity >= 9) return 'H'
  if (rpn >= 100) return 'M'
  return 'L'
}

function getRpnTagType(rpn: number): '' | 'success' | 'warning' | 'danger' | 'info' {
  if (rpn >= 200) return 'danger'
  if (rpn >= 100) return 'warning'
  return 'success'
}

function getApTagType(ap: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  if (ap === 'H') return 'danger'
  if (ap === 'M') return 'warning'
  return 'success'
}
</script>

<style scoped>
.fmea-matrix {
  width: 100%;
}

.fmea-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.fmea-table :deep(.el-input__inner) {
  font-size: 12px;
}

.fmea-table :deep(.el-textarea__inner) {
  font-size: 12px;
  font-family: 'Noto Sans KR', sans-serif;
}

.fmea-table :deep(.el-input-number) {
  width: 70px;
}

.fmea-table :deep(.el-input-number .el-input__inner) {
  text-align: center;
}
</style>
