<template>
  <el-date-picker
    v-model="dateRange"
    type="daterange"
    range-separator="~"
    start-placeholder="시작일"
    end-placeholder="종료일"
    format="YYYY-MM-DD"
    value-format="YYYY-MM-DD"
    :shortcuts="shortcuts"
    :clearable="clearable"
    :size="size"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  modelValue?: [string, string] | null
  clearable?: boolean
  size?: 'large' | 'default' | 'small'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  clearable: true,
  size: 'default'
})

const emit = defineEmits<{
  'update:modelValue': [value: [string, string] | null]
}>()

const dateRange = ref<[string, string] | null>(props.modelValue)

const shortcuts = [
  {
    text: '오늘',
    value: () => {
      const today = new Date()
      return [today, today]
    }
  },
  {
    text: '최근 7일',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setDate(start.getDate() - 6)
      return [start, end]
    }
  },
  {
    text: '최근 30일',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setDate(start.getDate() - 29)
      return [start, end]
    }
  },
  {
    text: '이번 달',
    value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      return [start, now]
    }
  },
  {
    text: '지난 달',
    value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth() - 1, 1)
      const end = new Date(now.getFullYear(), now.getMonth(), 0)
      return [start, end]
    }
  },
  {
    text: '올해',
    value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), 0, 1)
      return [start, now]
    }
  }
]

watch(() => props.modelValue, (val) => {
  dateRange.value = val
})

function handleChange(val: [string, string] | null) {
  emit('update:modelValue', val)
}
</script>
