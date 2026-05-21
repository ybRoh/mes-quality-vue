<template>
  <div class="page-container">
    <PageHeader title="Q&A 게시판" subtitle="질문과 답변">
      <template #actions>
        <el-button v-if="!selectedQna" type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 질문
        </el-button>
        <el-button v-if="!authStore.isLoggedIn" @click="goLogin">
          로그인
        </el-button>
      </template>
    </PageHeader>

    <!-- List Mode -->
    <template v-if="!selectedQna">
      <!-- Filter bar -->
      <div class="filter-bar">
        <el-select
          v-model="filterCategory"
          placeholder="분류"
          clearable
          style="width: 120px;"
          @change="loadList"
        >
          <el-option label="전체" value="" />
          <el-option label="일반" value="GENERAL" />
          <el-option label="품질" value="QUALITY" />
          <el-option label="공정" value="PROCESS" />
          <el-option label="설비" value="EQUIPMENT" />
          <el-option label="규격" value="SPEC" />
          <el-option label="기타" value="OTHER" />
        </el-select>
        <el-select
          v-model="filterStatus"
          placeholder="상태"
          clearable
          style="width: 120px;"
          @change="loadList"
        >
          <el-option label="전체" value="" />
          <el-option label="미답변" value="OPEN" />
          <el-option label="답변완료" value="ANSWERED" />
          <el-option label="마감" value="CLOSED" />
        </el-select>
        <el-input
          v-model="filterKeyword"
          placeholder="검색어"
          clearable
          style="width: 200px;"
          @keyup.enter="loadList"
        />
        <el-button type="primary" @click="loadList">
          <el-icon><Search /></el-icon>
          검색
        </el-button>
      </div>

      <!-- Q&A Table -->
      <el-table
        :data="tableData"
        border
        stripe
        v-loading="loading"
        @row-click="viewDetail"
        style="cursor: pointer;"
      >
        <el-table-column prop="qna_id" label="No" width="70" align="center" />
        <el-table-column prop="category" label="분류" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getCategoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="제목" min-width="300">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-text">{{ row.title }}</span>
              <p class="question-preview">{{ truncate(row.question, 80) }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="author_name" label="작성자" width="130" align="center">
          <template #default="{ row }">{{ row.author_name || row.author_email || '익명' }}</template>
        </el-table-column>
        <el-table-column prop="status" label="상태" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="조회수" width="80" align="center" />
        <el-table-column prop="created_at" label="작성일" width="110" align="center">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div style="display: flex; justify-content: center; margin-top: 10px;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalCount"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadList"
          @current-change="loadList"
        />
      </div>
    </template>

    <!-- Detail Mode -->
    <template v-if="selectedQna">
      <div style="margin-bottom: 10px;">
        <el-button @click="selectedQna = null">
          <el-icon><ArrowLeft /></el-icon>
          목록으로
        </el-button>
      </div>

      <div class="card">
        <div class="detail-header">
          <h2 class="detail-title">{{ selectedQna.title }}</h2>
          <div class="detail-meta">
            <el-tag size="small">{{ getCategoryLabel(selectedQna.category) }}</el-tag>
            <el-tag :type="getStatusTagType(selectedQna.status)" size="small">
              {{ getStatusLabel(selectedQna.status) }}
            </el-tag>
            <span class="meta-text">{{ selectedQna.author_name || selectedQna.author_email || '익명' }}</span>
            <span class="meta-text">{{ formatDate(selectedQna.created_at) }}</span>
            <span class="meta-text">조회 {{ selectedQna.view_count }}</span>
          </div>
        </div>

        <!-- Question Section -->
        <div class="qna-section">
          <div class="qna-label">질문</div>
          <div class="qna-content-box question-box">{{ selectedQna.question }}</div>
        </div>

        <!-- Answer Section -->
        <div class="qna-section">
          <div class="qna-label">답변</div>
          <template v-if="selectedQna.status === 'ANSWERED' || selectedQna.status === 'CLOSED'">
            <div class="qna-content-box answer-box">{{ selectedQna.answer }}</div>
            <div class="answer-meta">
              <span>답변자: {{ selectedQna.answered_by || '-' }}</span>
              <span>답변일: {{ formatDate(selectedQna.answered_at) }}</span>
            </div>
          </template>
          <template v-else>
            <template v-if="canAnswer">
              <el-input
                v-model="answerText"
                type="textarea"
                :rows="4"
                placeholder="답변을 입력하세요"
                style="margin-bottom: 8px;"
              />
              <el-button type="primary" @click="submitAnswer">답변 등록</el-button>
            </template>
            <div v-else class="qna-content-box answer-box empty-answer">아직 답변이 없습니다.</div>
          </template>
        </div>

        <!-- Action Buttons -->
        <div class="detail-actions">
          <el-button v-if="canEdit" @click="editQna(selectedQna)">편집</el-button>
          <el-button v-if="canDelete" type="danger" @click="deleteQna(selectedQna)">삭제</el-button>
          <el-button
            v-if="canClose"
            type="warning"
            @click="closeQna(selectedQna)"
          >마감</el-button>
        </div>
      </div>
    </template>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '질문 수정' : '새 질문 등록'"
      width="700px"
    >
      <el-form :model="formData" label-position="top">
        <el-form-item label="제목" required>
          <el-input v-model="formData.title" placeholder="제목을 입력하세요" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="분류">
              <el-select v-model="formData.category" placeholder="분류 선택" style="width: 100%;">
                <el-option label="일반" value="GENERAL" />
                <el-option label="품질" value="QUALITY" />
                <el-option label="공정" value="PROCESS" />
                <el-option label="설비" value="EQUIPMENT" />
                <el-option label="규격" value="SPEC" />
                <el-option label="기타" value="OTHER" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="공개여부">
              <el-switch v-model="formData.is_public" active-text="공개" inactive-text="비공개" />
            </el-form-item>
          </el-col>
        </el-row>
        <template v-if="!authStore.isLoggedIn">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="이메일" required>
                <el-input v-model="formData.author_email" placeholder="example@company.com" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="이름">
                <el-input v-model="formData.author_name_input" placeholder="이름 (선택)" />
              </el-form-item>
            </el-col>
          </el-row>
        </template>
        <el-form-item label="질문내용" required>
          <el-input
            v-model="formData.question"
            type="textarea"
            :rows="6"
            placeholder="질문 내용을 입력하세요"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Search, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { qnaApi } from '@/api/quality'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const showDialog = ref(false)
const isEditing = ref(false)

// --- Filter state ---
const filterCategory = ref('')
const filterStatus = ref('')
const filterKeyword = ref('')

// --- Pagination ---
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

// --- Data ---
const tableData = ref<any[]>([])
const selectedQna = ref<any>(null)
const answerText = ref('')

const formData = ref({
  qna_id: null as number | null,
  title: '',
  category: 'GENERAL',
  question: '',
  is_public: true,
  author_email: '',
  author_name_input: '',
})

// --- Role-based permissions ---
const isPrivilegedRole = computed(() => {
  const r = authStore.role
  return r === 'ADMIN' || r === 'MANAGER' || r === 'QA_ENGINEER'
})

const canAnswer = computed(() => {
  if (!selectedQna.value) return false
  if (selectedQna.value.status !== 'OPEN') return false
  return isPrivilegedRole.value
})

const canEdit = computed(() => {
  if (!selectedQna.value || !authStore.isLoggedIn) return false
  return selectedQna.value.author_id === authStore.userId || isPrivilegedRole.value
})

const canDelete = computed(() => {
  if (!selectedQna.value || !authStore.isLoggedIn) return false
  return isPrivilegedRole.value
})

const canClose = computed(() => {
  if (!selectedQna.value || !authStore.isLoggedIn) return false
  if (selectedQna.value.status === 'CLOSED') return false
  return selectedQna.value.author_id === authStore.userId || isPrivilegedRole.value
})

// --- Label / Tag helpers ---
function getCategoryLabel(category: string): string {
  switch (category) {
    case 'GENERAL': return '일반'
    case 'QUALITY': return '품질'
    case 'PROCESS': return '공정'
    case 'EQUIPMENT': return '설비'
    case 'SPEC': return '규격'
    case 'OTHER': return '기타'
    default: return category || '-'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'OPEN': return '미답변'
    case 'ANSWERED': return '답변완료'
    case 'CLOSED': return '마감'
    default: return status || '-'
  }
}

function getStatusTagType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'OPEN': return 'danger'
    case 'ANSWERED': return 'success'
    case 'CLOSED': return 'info'
    default: return 'info'
  }
}

function formatDate(dt: string): string {
  if (!dt) return '-'
  return dt.substring(0, 10)
}

function truncate(text: string, maxLen: number): string {
  if (!text) return ''
  return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
}

// --- Lifecycle ---
onMounted(() => {
  loadList()
})

// --- CRUD ---
async function loadList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      size: pageSize.value
    }
    if (filterCategory.value) params.category = filterCategory.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterKeyword.value) params.keyword = filterKeyword.value

    const res = await qnaApi.list(params)
    const data = res.data
    tableData.value = data.items || data
    totalCount.value = data.total || tableData.value.length
  } catch (e) {
    console.warn('Q&A 목록 조회 실패:', e)
    ElMessage.error('Q&A 목록을 불러오는데 실패했습니다')
    tableData.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

async function viewDetail(row: any) {
  try {
    const res = await qnaApi.get(row.qna_id)
    selectedQna.value = res.data
    answerText.value = ''
  } catch (e) {
    console.warn('Q&A 상세 조회 실패:', e)
    ElMessage.error('상세 정보를 불러오는데 실패했습니다')
  }
}

function openCreateDialog() {
  isEditing.value = false
  formData.value = {
    qna_id: null,
    title: '',
    category: 'GENERAL',
    question: '',
    is_public: true,
    author_email: '',
    author_name_input: '',
  }
  showDialog.value = true
}

function goLogin() {
  router.push('/login')
}

function editQna(row: any) {
  isEditing.value = true
  formData.value = {
    qna_id: row.qna_id,
    title: row.title || '',
    category: row.category || 'GENERAL',
    question: row.question || '',
    is_public: row.is_public ?? true,
    author_email: '',
    author_name_input: '',
  }
  showDialog.value = true
}

async function deleteQna(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.title}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await qnaApi.delete(row.qna_id)
    ElMessage.success('삭제되었습니다.')
    selectedQna.value = null
    loadList()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function closeQna(row: any) {
  try {
    await ElMessageBox.confirm(
      'Q&A를 마감하시겠습니까?',
      '마감 확인',
      { type: 'warning' }
    )
    await qnaApi.close(row.qna_id)
    ElMessage.success('마감되었습니다.')
    await viewDetail(row)
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('마감 실패:', e)
      ElMessage.error('마감에 실패했습니다.')
    }
  }
}

async function submitAnswer() {
  if (!answerText.value.trim()) {
    ElMessage.warning('답변을 입력하세요.')
    return
  }

  try {
    await qnaApi.answer(selectedQna.value.qna_id, { answer: answerText.value })
    ElMessage.success('답변이 등록되었습니다.')
    answerText.value = ''
    await viewDetail(selectedQna.value)
  } catch (e) {
    console.warn('답변 등록 실패:', e)
    ElMessage.error('답변 등록에 실패했습니다.')
  }
}

async function submitForm() {
  if (!formData.value.title) {
    ElMessage.warning('제목을 입력하세요.')
    return
  }
  if (!formData.value.question) {
    ElMessage.warning('질문 내용을 입력하세요.')
    return
  }
  if (!authStore.isLoggedIn && !formData.value.author_email) {
    ElMessage.warning('이메일 주소를 입력하세요.')
    return
  }

  try {
    const payload: Record<string, unknown> = {
      title: formData.value.title,
      category: formData.value.category,
      question: formData.value.question,
      is_public: formData.value.is_public,
    }
    if (!authStore.isLoggedIn) {
      payload.author_email = formData.value.author_email
      if (formData.value.author_name_input) {
        payload.author_name = formData.value.author_name_input
      }
    }

    if (formData.value.qna_id) {
      await qnaApi.update(formData.value.qna_id, payload)
      ElMessage.success('수정되었습니다.')
      // Refresh detail if viewing
      if (selectedQna.value && selectedQna.value.qna_id === formData.value.qna_id) {
        await viewDetail(selectedQna.value)
      }
    } else {
      await qnaApi.create(payload)
      ElMessage.success('질문이 등록되었습니다.')
    }
    showDialog.value = false
    isEditing.value = false
    loadList()
  } catch (e) {
    console.warn('Q&A 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
.title-cell {
  padding: 2px 0;
}

.title-text {
  font-weight: 600;
  color: var(--qms-text-primary);
}

.question-preview {
  margin: 3px 0 0 0;
  font-size: 11px;
  color: var(--qms-text-secondary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap !important;
  max-width: 100%;
}

.detail-header {
  margin-bottom: 16px;
}

.detail-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--qms-text-primary);
  margin: 0 0 8px 0;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-text {
  font-size: 12px;
  color: var(--qms-text-secondary);
}

.qna-section {
  margin-bottom: 16px;
}

.qna-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--qms-text-primary);
  margin-bottom: 6px;
  padding-left: 8px;
  border-left: 3px solid var(--qms-primary);
}

.qna-content-box {
  background: var(--qms-bg-light);
  border: 1px solid var(--qms-border);
  border-radius: 6px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--qms-text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.question-box {
  border-left: 3px solid var(--qms-primary);
}

.answer-box {
  border-left: 3px solid var(--qms-success);
}

.empty-answer {
  color: var(--qms-text-secondary);
  font-style: italic;
}

.answer-meta {
  display: flex;
  gap: 16px;
  margin-top: 6px;
  font-size: 11px;
  color: var(--qms-text-secondary);
}

.detail-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--qms-border);
}
</style>
