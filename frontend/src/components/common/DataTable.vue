<template>
  <div class="data-table-wrapper">
    <div v-if="showExport" class="data-table-toolbar">
      <slot name="toolbar" />
      <el-button size="small" @click="handleExport" aria-label="데이터 내보내기">
        <el-icon><Download /></el-icon>
        내보내기
      </el-button>
    </div>

    <el-table
      :data="pagedData"
      :border="border"
      :stripe="stripe"
      :max-height="maxHeight"
      :empty-text="emptyText"
      style="width: 100%"
      @sort-change="handleSortChange"
      v-loading="loading"
    >
      <el-table-column
        v-for="col in columns"
        :key="col.prop"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
        :min-width="col.minWidth"
        :sortable="col.sortable ? 'custom' : false"
        :fixed="col.fixed"
        :align="col.align || 'center'"
      >
        <template #default="scope">
          <slot :name="col.prop" :row="scope.row" :index="scope.$index">
            <span v-if="col.formatter">{{ col.formatter(scope.row[col.prop], scope.row) }}</span>
            <span v-else>{{ scope.row[col.prop] }}</span>
          </slot>
        </template>
      </el-table-column>
      <slot name="columns" />
    </el-table>

    <div v-if="showPagination && total > 0" class="data-table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="currentPageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Download } from '@element-plus/icons-vue'

export interface TableColumn {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  sortable?: boolean
  fixed?: boolean | 'left' | 'right'
  align?: 'left' | 'center' | 'right'
  formatter?: (value: any, row: any) => string
}

interface Props {
  data: any[]
  columns: TableColumn[]
  border?: boolean
  stripe?: boolean
  maxHeight?: number | string
  showPagination?: boolean
  showExport?: boolean
  pageSize?: number
  emptyText?: string
  loading?: boolean
  serverSide?: boolean
  total?: number
}

const props = withDefaults(defineProps<Props>(), {
  border: true,
  stripe: true,
  showPagination: true,
  showExport: false,
  pageSize: 20,
  emptyText: '데이터가 없습니다',
  loading: false,
  serverSide: false,
  total: 0
})

const emit = defineEmits<{
  'page-change': [page: number, pageSize: number]
  'sort-change': [prop: string, order: string]
  'export': []
}>()

const currentPage = ref(1)
const currentPageSize = ref(props.pageSize)
const sortProp = ref('')
const sortOrder = ref('')

const total = computed(() => {
  if (props.serverSide) return props.total
  return props.data.length
})

const sortedData = computed(() => {
  if (props.serverSide) return props.data
  if (!sortProp.value || !sortOrder.value) return props.data

  const data = [...props.data]
  data.sort((a, b) => {
    const valA = a[sortProp.value]
    const valB = b[sortProp.value]
    let result = 0
    if (valA == null) result = -1
    else if (valB == null) result = 1
    else if (typeof valA === 'number' && typeof valB === 'number') result = valA - valB
    else result = String(valA).localeCompare(String(valB), 'ko')

    return sortOrder.value === 'ascending' ? result : -result
  })
  return data
})

const pagedData = computed(() => {
  if (props.serverSide) return props.data
  if (!props.showPagination) return sortedData.value
  const start = (currentPage.value - 1) * currentPageSize.value
  return sortedData.value.slice(start, start + currentPageSize.value)
})

watch(() => props.data, () => {
  if (!props.serverSide) {
    currentPage.value = 1
  }
})

function handlePageChange(page: number) {
  currentPage.value = page
  emit('page-change', page, currentPageSize.value)
}

function handleSizeChange(size: number) {
  currentPageSize.value = size
  currentPage.value = 1
  emit('page-change', 1, size)
}

function handleSortChange({ prop, order }: { prop: string; order: string }) {
  sortProp.value = prop
  sortOrder.value = order
  emit('sort-change', prop, order)
}

function handleExport() {
  emit('export')
  exportToCsv()
}

function exportToCsv() {
  const headers = props.columns.map(c => c.label)
  const rows = (props.serverSide ? props.data : sortedData.value).map(row =>
    props.columns.map(c => {
      const val = row[c.prop]
      if (c.formatter) return c.formatter(val, row)
      return val ?? ''
    })
  )

  const csvContent = [
    headers.join(','),
    ...rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(','))
  ].join('\n')

  const BOM = '\uFEFF'
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `export_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.data-table-wrapper {
  background: #FFFFFF;
  border-radius: 8px;
}

.data-table-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 0 0 12px 0;
}

.data-table-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0 0 0;
}
</style>
