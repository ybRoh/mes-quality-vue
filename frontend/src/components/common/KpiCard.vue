<template>
  <div class="kpi-card" :style="{ borderTopColor: cardColor }">
    <div class="kpi-header">
      <span class="kpi-title">{{ title }}</span>
      <span v-if="trend !== undefined" class="kpi-trend" :class="trendClass">
        <el-icon v-if="trend > 0"><Top /></el-icon>
        <el-icon v-else-if="trend < 0"><Bottom /></el-icon>
        <el-icon v-else><Minus /></el-icon>
        {{ Math.abs(trend) }}%
      </span>
    </div>
    <div class="kpi-value" :style="{ color: cardColor }">
      {{ formattedValue }}
      <span v-if="unit" class="kpi-unit">{{ unit }}</span>
    </div>
    <div v-if="$slots.footer" class="kpi-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Top, Bottom, Minus } from '@element-plus/icons-vue'

interface Props {
  title: string
  value: number | string
  unit?: string
  trend?: number
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  color: '#0A6ED1'
})

const cardColor = computed(() => props.color)

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    if (Number.isInteger(props.value)) {
      return props.value.toLocaleString('ko-KR')
    }
    return props.value.toLocaleString('ko-KR', { minimumFractionDigits: 1, maximumFractionDigits: 2 })
  }
  return props.value
})

const trendClass = computed(() => {
  if (props.trend === undefined) return ''
  if (props.trend > 0) return 'trend-up'
  if (props.trend < 0) return 'trend-down'
  return 'trend-flat'
})
</script>

<style scoped>
.kpi-card {
  background: var(--qms-bg-white);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  padding: 20px;
  border-top: 3px solid var(--qms-primary);
  transition: box-shadow 0.2s;
}

.kpi-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.kpi-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.kpi-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--qms-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  font-weight: 500;
}

.trend-up {
  color: var(--qms-success);
}

.trend-down {
  color: var(--qms-danger);
}

.trend-flat {
  color: var(--qms-text-secondary);
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

.kpi-unit {
  font-size: 16px;
  font-weight: 400;
  color: var(--qms-text-secondary);
  margin-left: 4px;
}

.kpi-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--qms-border);
  font-size: 12px;
  color: var(--qms-text-secondary);
}
</style>
