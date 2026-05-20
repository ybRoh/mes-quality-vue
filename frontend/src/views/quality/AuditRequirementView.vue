<template>
  <div class="page-container">
    <PageHeader title="SQ 요구사항 관리" subtitle="IATF 16949 조항별 심사 요구사항">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 요구사항
        </el-button>
      </template>
    </PageHeader>

    <!-- Filter bar -->
    <div class="filter-bar">
      <el-select
        v-model="filterCategory"
        placeholder="카테고리 선택"
        clearable
        style="width: 200px;"
        @change="loadList"
      >
        <el-option
          v-for="cat in categoryOptions"
          :key="cat"
          :label="cat"
          :value="cat"
        />
      </el-select>
    </div>

    <!-- Requirements table -->
    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column prop="req_no" label="요구사항 No." width="120" />
      <el-table-column prop="clause_ref" label="IATF 조항" width="120" />
      <el-table-column prop="category" label="카테고리" width="120" />
      <el-table-column prop="description" label="설명" show-overflow-tooltip />
      <el-table-column prop="audit_criteria" label="심사 기준" show-overflow-tooltip />
      <el-table-column prop="is_active" label="상태" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '활성' : '비활성' }}
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
      :title="isEditing ? '요구사항 수정' : '새 요구사항 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="요구사항 No." required>
              <el-input v-model="formData.req_no" placeholder="SQ-REQ-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="IATF 조항" required>
              <el-input v-model="formData.clause_ref" placeholder="8.5.1" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="카테고리">
              <el-input v-model="formData.category" placeholder="공정관리" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="활성 여부">
              <el-switch v-model="formData.is_active" active-text="활성" inactive-text="비활성" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="설명">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="요구사항 설명을 입력하세요"
          />
        </el-form-item>
        <el-form-item label="심사 기준">
          <el-input
            v-model="formData.audit_criteria"
            type="textarea"
            :rows="3"
            placeholder="심사 시 확인할 기준을 입력하세요"
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
import { auditApi } from '@/api/quality'

const loading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)
const filterCategory = ref('')

const tableData = ref<any[]>([])
const categoryOptions = ref<string[]>([])

const formData = ref({
  requirement_id: null as number | null,
  req_no: '',
  clause_ref: '',
  category: '',
  description: '',
  audit_criteria: '',
  is_active: true
})

onMounted(() => {
  loadList()
})

async function loadList() {
  loading.value = true
  try {
    const res = await auditApi.getRequirements({
      category: filterCategory.value || undefined
    })
    tableData.value = res.data.items || res.data
    // Extract unique categories for filter options
    const cats = new Set<string>()
    for (const item of tableData.value) {
      if (item.category) cats.add(item.category)
    }
    categoryOptions.value = Array.from(cats).sort()
  } catch (e) {
    console.warn('요구사항 목록 조회 실패:', e)
    ElMessage.error('요구사항 목록을 불러오는데 실패했습니다')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    requirement_id: null,
    req_no: '',
    clause_ref: '',
    category: '',
    description: '',
    audit_criteria: '',
    is_active: true
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    requirement_id: row.requirement_id,
    req_no: row.req_no || '',
    clause_ref: row.clause_ref || '',
    category: row.category || '',
    description: row.description || '',
    audit_criteria: row.audit_criteria || '',
    is_active: row.is_active ?? true
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.req_no}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await auditApi.deleteRequirement(row.requirement_id)
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
  if (!formData.value.req_no) {
    ElMessage.warning('요구사항 No.를 입력하세요.')
    return
  }
  if (!formData.value.clause_ref) {
    ElMessage.warning('IATF 조항을 입력하세요.')
    return
  }

  try {
    const payload = {
      req_no: formData.value.req_no,
      clause_ref: formData.value.clause_ref,
      category: formData.value.category || undefined,
      description: formData.value.description || undefined,
      audit_criteria: formData.value.audit_criteria || undefined,
      is_active: formData.value.is_active
    }

    if (formData.value.requirement_id) {
      await auditApi.updateRequirement(formData.value.requirement_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await auditApi.createRequirement(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('요구사항 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
</style>
