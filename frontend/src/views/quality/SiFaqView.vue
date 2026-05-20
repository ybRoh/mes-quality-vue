<template>
  <div class="page-container">
    <PageHeader title="SI FAQ 관리" subtitle="Supplier Interface FAQ">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 FAQ
        </el-button>
      </template>
    </PageHeader>

    <!-- Filter bar -->
    <div class="filter-bar">
      <el-input
        v-model="filterCustomerId"
        placeholder="고객 ID"
        clearable
        style="width: 160px;"
        @change="loadList"
      />
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

    <!-- FAQ table -->
    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column prop="customer_id" label="고객 ID" width="100" />
      <el-table-column prop="category" label="카테고리" width="120" />
      <el-table-column prop="question" label="질문" show-overflow-tooltip />
      <el-table-column prop="answer" label="답변" show-overflow-tooltip />
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
      :title="isEditing ? 'FAQ 수정' : '새 FAQ 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="고객 ID">
              <el-input v-model="formData.customer_id" placeholder="C001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="카테고리">
              <el-input v-model="formData.category" placeholder="카테고리 입력" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="질문" required>
          <el-input
            v-model="formData.question"
            type="textarea"
            :rows="3"
            placeholder="질문을 입력하세요"
          />
        </el-form-item>
        <el-form-item label="답변">
          <el-input
            v-model="formData.answer"
            type="textarea"
            :rows="3"
            placeholder="답변을 입력하세요"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="참조 규격 ID">
              <el-input-number v-model="formData.reference_spec_id" :min="0" controls-position="right" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="활성 여부">
              <el-switch v-model="formData.is_active" active-text="활성" inactive-text="비활성" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { specificationApi } from '@/api/quality'

const loading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)
const filterCustomerId = ref('')
const filterCategory = ref('')

const tableData = ref<any[]>([])
const categoryOptions = ref<string[]>([])

const formData = ref({
  faq_id: null as number | null,
  customer_id: '',
  category: '',
  question: '',
  answer: '',
  reference_spec_id: null as number | null,
  is_active: true
})

onMounted(() => {
  loadList()
})

async function loadList() {
  loading.value = true
  try {
    const res = await specificationApi.getSiFaq({
      customer_id: filterCustomerId.value || undefined,
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
    console.warn('FAQ 목록 조회 실패:', e)
    ElMessage.error('FAQ 목록을 불러오는데 실패했습니다')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    faq_id: null,
    customer_id: '',
    category: '',
    question: '',
    answer: '',
    reference_spec_id: null,
    is_active: true
  }
  showDialog.value = true
}

function editItem(row: any) {
  isEditing.value = true
  formData.value = {
    faq_id: row.faq_id,
    customer_id: row.customer_id || '',
    category: row.category || '',
    question: row.question || '',
    answer: row.answer || '',
    reference_spec_id: row.reference_spec_id || null,
    is_active: row.is_active ?? true
  }
  showDialog.value = true
}

async function deleteItem(row: any) {
  try {
    await ElMessageBox.confirm(
      'FAQ를 삭제하시겠습니까?',
      '삭제 확인',
      { type: 'warning' }
    )
    await specificationApi.deleteSiFaq(row.faq_id)
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
  if (!formData.value.question) {
    ElMessage.warning('질문을 입력하세요.')
    return
  }

  try {
    const payload = {
      customer_id: formData.value.customer_id || undefined,
      category: formData.value.category || undefined,
      question: formData.value.question,
      answer: formData.value.answer || undefined,
      reference_spec_id: formData.value.reference_spec_id || undefined,
      is_active: formData.value.is_active
    }

    if (formData.value.faq_id) {
      await specificationApi.updateSiFaq(formData.value.faq_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await specificationApi.createSiFaq(payload)
      ElMessage.success('생성되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('FAQ 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
</style>
