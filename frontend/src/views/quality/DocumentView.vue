<template>
  <div class="page-container">
    <PageHeader title="표준문서관리" subtitle="문서 등록 및 승인 관리">
      <template #actions>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          새 문서
        </el-button>
      </template>
    </PageHeader>

    <!-- 문서유형 필터 -->
    <div class="type-selector">
      <el-radio-group v-model="docTypeFilter" size="default" @change="onDocTypeChange">
        <el-radio-button value="">전체</el-radio-button>
        <el-radio-button value="MANUAL">매뉴얼</el-radio-button>
        <el-radio-button value="PROCESS">프로세스</el-radio-button>
        <el-radio-button value="REGULATION">규정/지침</el-radio-button>
        <el-radio-button value="GUIDELINE">가이드라인</el-radio-button>
        <el-radio-button value="FORM">양식</el-radio-button>
      </el-radio-group>
    </div>

    <!-- KPI 요약 -->
    <div class="kpi-row">
      <KpiCard title="전체 문서" :value="kpi.total" unit="건" color="#0A6ED1" />
      <KpiCard title="승인 완료" :value="kpi.approved" unit="건" color="#107E3E" />
      <KpiCard title="검토중" :value="kpi.review" unit="건" color="#E9730C" />
      <KpiCard title="작성중" :value="kpi.draft" unit="건" color="#5B738B" />
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 문서목록 -->
      <el-tab-pane label="문서목록" name="list">
        <div class="filter-bar">
          <el-select v-model="filterStatus" placeholder="상태 선택" clearable style="width: 150px;" @change="loadDocuments">
            <el-option label="작성중" value="DRAFT" />
            <el-option label="검토중" value="REVIEW" />
            <el-option label="승인" value="APPROVED" />
            <el-option label="폐기" value="OBSOLETE" />
          </el-select>
        </div>

        <el-table :data="documentList" border stripe v-loading="loading" @row-click="selectDocument">
          <el-table-column prop="doc_no" label="문서번호" width="150" />
          <el-table-column prop="title" label="제목" min-width="200" />
          <el-table-column prop="doc_type" label="문서유형" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small">{{ getDocTypeLabel(row.doc_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="revision" label="Rev." width="70" align="center" />
          <el-table-column prop="status" label="상태" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="부서" width="120" />
          <el-table-column prop="prepared_by" label="작성자" width="100" />
          <el-table-column prop="updated_at" label="수정일" width="120" align="center">
            <template #default="{ row }">
              {{ row.updated_at ? row.updated_at.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="editDocument(row)">편집</el-button>
              <el-button type="danger" link size="small" @click.stop="deleteDocument(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 문서상세 -->
      <el-tab-pane label="문서상세" name="detail">
        <el-empty v-if="!selectedDocument" description="문서목록에서 항목을 선택하세요." />

        <div v-if="selectedDocument">
          <!-- 문서 헤더 -->
          <div class="doc-detail-header">
            <h3>{{ selectedDocument.doc_no }}</h3>
            <span class="doc-detail-title">{{ selectedDocument.title }}</span>
            <el-tag :type="getStatusType(selectedDocument.status)" size="small">
              {{ getStatusLabel(selectedDocument.status) }}
            </el-tag>
            <span class="doc-detail-revision">Rev. {{ selectedDocument.revision }}</span>
          </div>

          <!-- 승인 워크플로우 -->
          <div class="workflow-section">
            <h4>승인 워크플로우</h4>
            <div class="workflow-buttons">
              <el-button
                v-if="selectedDocument.status === 'DRAFT'"
                type="warning"
                @click="submitForReview"
              >
                검토요청
              </el-button>
              <el-button
                v-if="selectedDocument.status === 'REVIEW'"
                type="success"
                @click="approveDocument"
              >
                승인
              </el-button>
              <el-button
                v-if="selectedDocument.status !== 'OBSOLETE'"
                type="danger"
                @click="obsoleteDocument"
              >
                폐기
              </el-button>
            </div>
          </div>

          <!-- 개정이력 타임라인 -->
          <div class="revision-section">
            <h4>개정이력</h4>
            <el-timeline v-if="revisions.length > 0">
              <el-timeline-item
                v-for="rev in revisions"
                :key="rev.revision_id || rev.revision_no"
                :timestamp="rev.created_at ? rev.created_at.substring(0, 10) : ''"
                placement="top"
              >
                <div class="revision-item">
                  <strong>Rev. {{ rev.revision_no }}</strong>
                  <span>{{ rev.change_summary }}</span>
                  <span class="revision-by">{{ rev.changed_by }}</span>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="개정이력이 없습니다." :image-size="60" />
          </div>

          <!-- 첨부파일 -->
          <div class="attachment-section">
            <div class="attachment-header">
              <h4>첨부파일</h4>
              <el-upload
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleUpload"
              >
                <el-button type="primary" size="small">
                  <el-icon><Plus /></el-icon>
                  파일 업로드
                </el-button>
              </el-upload>
            </div>
            <el-table v-if="attachments.length > 0" :data="attachments" border size="small">
              <el-table-column prop="file_name" label="파일명" min-width="200" />
              <el-table-column label="파일크기" width="120" align="center">
                <template #default="{ row }">
                  {{ formatFileSize(row.file_size) }}
                </template>
              </el-table-column>
              <el-table-column prop="uploaded_by" label="업로드자" width="120" />
              <el-table-column label="작업" width="140" align="center">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="downloadAttachment(row)">다운로드</el-button>
                  <el-button type="danger" link size="small" @click="deleteAttachment(row)">삭제</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="첨부파일이 없습니다." :image-size="60" />
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 3: 개정이력 -->
      <el-tab-pane label="개정이력" name="revisions">
        <el-empty v-if="!selectedDocument" description="문서목록에서 항목을 선택하세요." />
        <el-table v-if="selectedDocument" :data="revisions" border stripe v-loading="revisionsLoading">
          <el-table-column prop="revision_no" label="개정번호" width="100" align="center" />
          <el-table-column prop="change_summary" label="변경내용" min-width="300" />
          <el-table-column prop="changed_by" label="변경자" width="120" />
          <el-table-column prop="created_at" label="변경일" width="150" align="center">
            <template #default="{ row }">
              {{ row.created_at ? row.created_at.substring(0, 10) : '-' }}
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingDocument ? '문서 수정' : '새 문서 등록'"
      width="700px"
    >
      <el-form :model="docForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="문서번호" required>
              <el-input v-model="docForm.doc_no" placeholder="DOC-MAN-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="문서유형" required>
              <el-select v-model="docForm.doc_type" style="width: 100%;">
                <el-option label="매뉴얼" value="MANUAL" />
                <el-option label="프로세스" value="PROCESS" />
                <el-option label="규정/지침" value="REGULATION" />
                <el-option label="가이드라인" value="GUIDELINE" />
                <el-option label="양식" value="FORM" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="제목" required>
          <el-input v-model="docForm.title" placeholder="문서 제목" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="부서">
              <el-input v-model="docForm.department" placeholder="품질보증팀" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="상태">
              <el-select v-model="docForm.status" style="width: 100%;">
                <el-option label="작성중" value="DRAFT" />
                <el-option label="검토중" value="REVIEW" />
                <el-option label="승인" value="APPROVED" />
                <el-option label="폐기" value="OBSOLETE" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="작성자">
              <el-input v-model="docForm.prepared_by" placeholder="작성자" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="검토자">
              <el-input v-model="docForm.reviewed_by" placeholder="검토자" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="승인자">
              <el-input v-model="docForm.approved_by" placeholder="승인자" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="시행일">
          <el-date-picker
            v-model="docForm.effective_date"
            type="date"
            placeholder="시행일 선택"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">취소</el-button>
        <el-button type="primary" @click="submitDocument">저장</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import { documentApi } from '@/api/quality'

const route = useRoute()

const activeTab = ref('list')
const docTypeFilter = ref('')
const loading = ref(false)
const revisionsLoading = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const editingDocument = ref(false)

const documentList = ref<any[]>([])
const selectedDocument = ref<any>(null)
const revisions = ref<any[]>([])
const attachments = ref<any[]>([])

const kpi = computed(() => {
  const list = documentList.value
  return {
    total: list.length,
    approved: list.filter((d: any) => d.status === 'APPROVED').length,
    review: list.filter((d: any) => d.status === 'REVIEW').length,
    draft: list.filter((d: any) => d.status === 'DRAFT').length
  }
})

const docForm = ref({
  doc_id: null as number | null,
  doc_no: '',
  doc_type: 'MANUAL',
  title: '',
  department: '',
  status: 'DRAFT',
  prepared_by: '',
  reviewed_by: '',
  approved_by: '',
  effective_date: ''
})

function getStatusType(status: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'DRAFT': return 'info'
    case 'REVIEW': return 'warning'
    case 'APPROVED': return 'success'
    case 'OBSOLETE': return 'danger'
    default: return 'info'
  }
}

function getStatusLabel(status: string): string {
  switch (status) {
    case 'DRAFT': return '작성중'
    case 'REVIEW': return '검토중'
    case 'APPROVED': return '승인'
    case 'OBSOLETE': return '폐기'
    default: return status
  }
}

function getDocTypeLabel(docType: string): string {
  switch (docType) {
    case 'MANUAL': return '매뉴얼'
    case 'PROCESS': return '프로세스'
    case 'REGULATION': return '규정/지침'
    case 'GUIDELINE': return '가이드라인'
    case 'FORM': return '양식'
    default: return docType
  }
}

function formatFileSize(bytes: number): string {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

function onDocTypeChange() {
  selectedDocument.value = null
  activeTab.value = 'list'
  loadDocuments()
}

onMounted(() => {
  // route query param 으로 초기 문서유형 설정
  if (route.query.doc_type && typeof route.query.doc_type === 'string') {
    docTypeFilter.value = route.query.doc_type
  }
  loadDocuments()
})

async function loadDocuments() {
  loading.value = true
  try {
    const res = await documentApi.getList({
      doc_type: docTypeFilter.value || undefined,
      status: filterStatus.value || undefined
    })
    documentList.value = res.data.items || res.data
  } catch (e) {
    console.warn('문서 목록 조회 실패:', e)
    ElMessage.error('문서 목록을 불러오는데 실패했습니다')
    documentList.value = []
  } finally {
    loading.value = false
  }
}

async function selectDocument(row: any) {
  selectedDocument.value = row
  activeTab.value = 'detail'
  loadRevisions()
  loadAttachments()
}

function openCreateDialog() {
  editingDocument.value = false
  docForm.value = {
    doc_id: null,
    doc_no: '',
    doc_type: docTypeFilter.value || 'MANUAL',
    title: '',
    department: '',
    status: 'DRAFT',
    prepared_by: '',
    reviewed_by: '',
    approved_by: '',
    effective_date: ''
  }
  showCreateDialog.value = true
}

function editDocument(row: any) {
  editingDocument.value = true
  docForm.value = {
    doc_id: row.doc_id,
    doc_no: row.doc_no,
    doc_type: row.doc_type,
    title: row.title,
    department: row.department || '',
    status: row.status,
    prepared_by: row.prepared_by || '',
    reviewed_by: row.reviewed_by || '',
    approved_by: row.approved_by || '',
    effective_date: row.effective_date || ''
  }
  showCreateDialog.value = true
}

async function deleteDocument(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.title}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await documentApi.delete(row.doc_id)
    ElMessage.success('삭제되었습니다.')
    if (selectedDocument.value?.doc_id === row.doc_id) {
      selectedDocument.value = null
    }
    loadDocuments()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitDocument() {
  if (!docForm.value.doc_no) {
    ElMessage.warning('문서번호를 입력하세요.')
    return
  }
  if (!docForm.value.title) {
    ElMessage.warning('제목을 입력하세요.')
    return
  }

  try {
    const payload = {
      doc_no: docForm.value.doc_no,
      doc_type: docForm.value.doc_type,
      title: docForm.value.title,
      department: docForm.value.department || undefined,
      status: docForm.value.status,
      prepared_by: docForm.value.prepared_by || undefined,
      reviewed_by: docForm.value.reviewed_by || undefined,
      approved_by: docForm.value.approved_by || undefined,
      effective_date: docForm.value.effective_date || undefined
    }

    if (docForm.value.doc_id) {
      await documentApi.update(docForm.value.doc_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await documentApi.create(payload)
      ElMessage.success('등록되었습니다.')
    }
    showCreateDialog.value = false
    editingDocument.value = false
    loadDocuments()
  } catch (e) {
    console.warn('문서 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// 승인 워크플로우
async function submitForReview() {
  if (!selectedDocument.value) return
  try {
    await ElMessageBox.confirm('검토 요청을 하시겠습니까?', '검토 요청', { type: 'warning' })
    await documentApi.update(selectedDocument.value.doc_id, { status: 'REVIEW' })
    ElMessage.success('검토 요청되었습니다.')
    selectedDocument.value.status = 'REVIEW'
    loadDocuments()
  } catch (e) {
    console.warn('검토 요청 실패:', e)
    ElMessage.error('검토 요청에 실패했습니다.')
  }
}

async function approveDocument() {
  if (!selectedDocument.value) return
  try {
    await ElMessageBox.confirm('문서를 승인하시겠습니까?', '승인', { type: 'success' })
    await documentApi.approve(selectedDocument.value.doc_id)
    ElMessage.success('승인되었습니다.')
    selectedDocument.value.status = 'APPROVED'
    loadDocuments()
  } catch (e) {
    console.warn('승인 실패:', e)
    ElMessage.error('승인에 실패했습니다.')
  }
}

async function obsoleteDocument() {
  if (!selectedDocument.value) return
  try {
    await ElMessageBox.confirm('문서를 폐기하시겠습니까? 이 작업은 되돌릴 수 없습니다.', '폐기', { type: 'error' })
    await documentApi.obsolete(selectedDocument.value.doc_id)
    ElMessage.success('폐기되었습니다.')
    selectedDocument.value.status = 'OBSOLETE'
    loadDocuments()
  } catch (e) {
    console.warn('폐기 실패:', e)
    ElMessage.error('폐기에 실패했습니다.')
  }
}

// 개정이력
async function loadRevisions() {
  if (!selectedDocument.value) return
  revisionsLoading.value = true
  try {
    const res = await documentApi.getRevisions(selectedDocument.value.doc_id)
    revisions.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('개정이력 조회 실패:', e)
    ElMessage.error('개정이력을 불러오는데 실패했습니다')
    revisions.value = []
  } finally {
    revisionsLoading.value = false
  }
}

// 첨부파일
async function loadAttachments() {
  if (!selectedDocument.value) return
  try {
    const res = await documentApi.getAttachments(selectedDocument.value.doc_id)
    attachments.value = res.data.items || res.data || []
  } catch (e) {
    console.warn('첨부파일 조회 실패:', e)
    ElMessage.error('첨부파일을 불러오는데 실패했습니다')
    attachments.value = []
  }
}

async function handleUpload(uploadFile: any) {
  if (!selectedDocument.value) return
  const file = uploadFile.raw || uploadFile
  if (!file) return
  try {
    await documentApi.uploadAttachment(selectedDocument.value.doc_id, file)
    ElMessage.success('파일이 업로드되었습니다.')
    loadAttachments()
  } catch (e) {
    console.warn('파일 업로드 실패:', e)
    ElMessage.error('파일 업로드에 실패했습니다.')
  }
}

async function deleteAttachment(att: any) {
  try {
    await ElMessageBox.confirm(`"${att.file_name}"을(를) 삭제하시겠습니까?`, '삭제 확인', { type: 'warning' })
    await documentApi.deleteAttachment(att.attachment_id)
    ElMessage.success('삭제되었습니다.')
    loadAttachments()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function downloadAttachment(att: any) {
  try {
    const res = await documentApi.downloadAttachment(att.attachment_id)
    const blob = new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = att.file_name || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.warn('파일 다운로드 실패:', e)
    ElMessage.error('파일 다운로드에 실패했습니다.')
  }
}
</script>

<style scoped>
.type-selector {
  margin-bottom: 16px;
}

.doc-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #E5E5E5;
}

.doc-detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.doc-detail-title {
  font-size: 16px;
  color: var(--qms-text-secondary);
}

.doc-detail-revision {
  font-size: 13px;
  color: var(--qms-text-secondary);
  font-weight: 500;
}

.workflow-section {
  margin-bottom: 24px;
}

.workflow-section h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.workflow-buttons {
  display: flex;
  gap: 8px;
}

.revision-section {
  margin-bottom: 24px;
}

.revision-section h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.revision-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.revision-by {
  font-size: 12px;
  color: var(--qms-text-secondary);
}

.attachment-section {
  margin-bottom: 24px;
}

.attachment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.attachment-header h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}
</style>
