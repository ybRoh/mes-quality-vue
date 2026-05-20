<template>
  <div class="page-container">
    <PageHeader title="교육관리" subtitle="교육과정 및 이수 기록 관리">
      <template #actions>
        <el-button type="primary" @click="openCourseDialog()">
          <el-icon><Plus /></el-icon>
          새 교육과정
        </el-button>
      </template>
    </PageHeader>

    <!-- KPI Cards -->
    <div class="kpi-row">
      <KpiCard title="총 교육과정" :value="courses.length" color="#0A6ED1" />
      <KpiCard title="총 이수기록" :value="records.length" color="#107E3E" />
      <KpiCard title="재교육 예정" :value="dueSoonList.length" color="#E9730C" />
      <KpiCard title="미이수" :value="failOrPendingCount" color="#BB0000" />
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 교육과정 마스터 -->
      <el-tab-pane label="교육과정 마스터" name="courses">
        <div class="filter-bar">
          <el-select
            v-model="courseFilter.training_type"
            placeholder="교육유형 선택"
            clearable
            style="width: 160px;"
            @change="loadCourses"
          >
            <el-option label="사내" value="INTERNAL" />
            <el-option label="사외" value="EXTERNAL" />
            <el-option label="현장" value="OJT" />
            <el-option label="온라인" value="ONLINE" />
          </el-select>
          <el-input
            v-model="courseFilter.category"
            placeholder="카테고리 검색"
            clearable
            style="width: 180px;"
            @clear="loadCourses"
            @keyup.enter="loadCourses"
          />
          <el-button type="primary" size="small" @click="loadCourses">조회</el-button>
        </div>

        <el-table :data="courses" border stripe v-loading="loadingCourses">
          <el-table-column prop="course_no" label="과정코드" width="120" />
          <el-table-column prop="course_name" label="과정명" show-overflow-tooltip />
          <el-table-column prop="category" label="카테고리" width="100" />
          <el-table-column prop="training_type" label="유형" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="trainingTypeTag(row.training_type)" size="small">
                {{ trainingTypeLabel(row.training_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration_hours" label="시간" width="80" align="center" />
          <el-table-column prop="recurrence_months" label="재교육주기" width="100" align="center">
            <template #default="{ row }">
              {{ row.recurrence_months ? row.recurrence_months + '개월' : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="상태" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                {{ row.is_active ? '활성' : '비활성' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="record_count" label="이수자" width="80" align="center" />
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editCourse(row)">편집</el-button>
              <el-button type="danger" link size="small" @click="deleteCourse(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 교육이수 기록 -->
      <el-tab-pane label="교육이수 기록" name="records">
        <div class="filter-bar">
          <el-select
            v-model="recordFilter.course_id"
            placeholder="교육과정 선택"
            clearable
            filterable
            style="width: 220px;"
            @change="loadRecords"
          >
            <el-option
              v-for="c in courses"
              :key="c.course_id"
              :label="c.course_name"
              :value="c.course_id"
            />
          </el-select>
          <el-input
            v-model="recordFilter.trainee_id"
            placeholder="교육생 ID"
            clearable
            style="width: 150px;"
            @clear="loadRecords"
            @keyup.enter="loadRecords"
          />
          <el-select
            v-model="recordFilter.result"
            placeholder="결과 선택"
            clearable
            style="width: 130px;"
            @change="loadRecords"
          >
            <el-option label="대기" value="PENDING" />
            <el-option label="합격" value="PASS" />
            <el-option label="불합격" value="FAIL" />
          </el-select>
          <el-button type="primary" size="small" @click="loadRecords">조회</el-button>
          <div style="flex: 1;" />
          <el-button type="primary" @click="openRecordDialog()">새 이수기록</el-button>
          <el-button type="success" @click="openBulkDialog">일괄등록</el-button>
        </div>

        <el-table :data="records" border stripe v-loading="loadingRecords">
          <el-table-column prop="course_no" label="과정코드" width="120" />
          <el-table-column prop="course_name" label="과정명" show-overflow-tooltip />
          <el-table-column prop="trainee_id" label="교육생" width="100" />
          <el-table-column prop="training_date" label="교육일" width="120" align="center" />
          <el-table-column prop="score" label="점수" width="80" align="center" />
          <el-table-column prop="result" label="결과" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="resultTagType(row.result)" size="small">
                {{ resultLabel(row.result) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="next_due_date" label="재교육기한" width="120" align="center" />
          <el-table-column label="작업" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="editRecord(row)">편집</el-button>
              <el-button type="danger" link size="small" @click="deleteRecord(row)">삭제</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 3: 재교육 알림 -->
      <el-tab-pane label="재교육 알림" name="dueSoon">
        <el-table :data="dueSoonList" border stripe v-loading="loadingDueSoon">
          <el-table-column prop="course_no" label="과정코드" width="120" />
          <el-table-column prop="course_name" label="과정명" show-overflow-tooltip />
          <el-table-column prop="trainee_id" label="교육생" width="100" />
          <el-table-column prop="training_date" label="최근이수" width="120" align="center" />
          <el-table-column prop="next_due_date" label="재교육기한" width="120" align="center" />
          <el-table-column label="잔여일" width="100" align="center">
            <template #default="{ row }">
              <span :style="{ color: getDaysRemaining(row.next_due_date) < 30 ? '#BB0000' : '', fontWeight: getDaysRemaining(row.next_due_date) < 30 ? 'bold' : 'normal' }">
                {{ getDaysRemaining(row.next_due_date) }}일
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Course Create/Edit Dialog -->
    <el-dialog
      v-model="showCourseDialog"
      :title="isEditingCourse ? '교육과정 수정' : '새 교육과정 등록'"
      width="600px"
    >
      <el-form :model="courseForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="과정코드" required>
              <el-input v-model="courseForm.course_no" placeholder="TRN-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="과정명" required>
              <el-input v-model="courseForm.course_name" placeholder="교육과정명" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="카테고리">
              <el-input v-model="courseForm.category" placeholder="품질, 안전 등" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="교육유형">
              <el-select v-model="courseForm.training_type" style="width: 100%;">
                <el-option label="사내" value="INTERNAL" />
                <el-option label="사외" value="EXTERNAL" />
                <el-option label="현장" value="OJT" />
                <el-option label="온라인" value="ONLINE" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="교육시간 (시간)">
              <el-input-number v-model="courseForm.duration_hours" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="재교육주기 (개월)">
              <el-input-number v-model="courseForm.recurrence_months" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="활성 여부">
          <el-switch v-model="courseForm.is_active" active-text="활성" inactive-text="비활성" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCourseDialog = false">취소</el-button>
        <el-button type="primary" @click="submitCourse">저장</el-button>
      </template>
    </el-dialog>

    <!-- Record Create/Edit Dialog -->
    <el-dialog
      v-model="showRecordDialog"
      :title="isEditingRecord ? '이수기록 수정' : '새 이수기록 등록'"
      width="600px"
    >
      <el-form :model="recordForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="교육과정" required>
              <el-select v-model="recordForm.course_id" filterable style="width: 100%;">
                <el-option
                  v-for="c in courses"
                  :key="c.course_id"
                  :label="c.course_name"
                  :value="c.course_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="교육생 ID" required>
              <el-input v-model="recordForm.trainee_id" placeholder="EMP001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="교육일" required>
              <el-date-picker
                v-model="recordForm.training_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="점수">
              <el-input-number v-model="recordForm.score" :min="0" :max="100" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="결과">
          <el-select v-model="recordForm.result" style="width: 100%;">
            <el-option label="대기" value="PENDING" />
            <el-option label="합격" value="PASS" />
            <el-option label="불합격" value="FAIL" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecordDialog = false">취소</el-button>
        <el-button type="primary" @click="submitRecord">저장</el-button>
      </template>
    </el-dialog>

    <!-- Bulk Record Dialog -->
    <el-dialog v-model="showBulkDialog" title="교육이수 일괄등록" width="600px">
      <el-form :model="bulkForm" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="교육과정" required>
              <el-select v-model="bulkForm.course_id" filterable style="width: 100%;">
                <el-option
                  v-for="c in courses"
                  :key="c.course_id"
                  :label="c.course_name"
                  :value="c.course_id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="교육일" required>
              <el-date-picker
                v-model="bulkForm.training_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="교육생 ID (쉼표 구분)" required>
          <el-input
            v-model="bulkForm.trainee_ids"
            type="textarea"
            :rows="4"
            placeholder="EMP001, EMP002, EMP003"
          />
        </el-form-item>
        <el-form-item label="결과">
          <el-select v-model="bulkForm.result" style="width: 100%;">
            <el-option label="대기" value="PENDING" />
            <el-option label="합격" value="PASS" />
            <el-option label="불합격" value="FAIL" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBulkDialog = false">취소</el-button>
        <el-button type="primary" @click="submitBulkRecords">일괄등록</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import { trainingApi } from '@/api/quality'
import dayjs from 'dayjs'

// ---------- State ----------
const activeTab = ref('courses')
const loadingCourses = ref(false)
const loadingRecords = ref(false)
const loadingDueSoon = ref(false)

const courses = ref<any[]>([])
const records = ref<any[]>([])
const dueSoonList = ref<any[]>([])

// Filters
const courseFilter = ref({ training_type: '', category: '' })
const recordFilter = ref({ course_id: null as number | null, trainee_id: '', result: '' })

// Dialogs
const showCourseDialog = ref(false)
const isEditingCourse = ref(false)
const showRecordDialog = ref(false)
const isEditingRecord = ref(false)
const showBulkDialog = ref(false)

// Forms
const courseForm = ref({
  course_id: null as number | null,
  course_no: '',
  course_name: '',
  category: '',
  training_type: 'INTERNAL',
  duration_hours: 0,
  recurrence_months: 0,
  is_active: true
})

const recordForm = ref({
  record_id: null as number | null,
  course_id: null as number | null,
  trainee_id: '',
  training_date: '',
  score: 0,
  result: 'PENDING'
})

const bulkForm = ref({
  course_id: null as number | null,
  training_date: '',
  trainee_ids: '',
  result: 'PENDING'
})

// ---------- Computed ----------
const failOrPendingCount = computed(() => {
  return records.value.filter(r => r.result === 'FAIL' || r.result === 'PENDING').length
})

// ---------- Helpers ----------
function trainingTypeTag(type: string): '' | 'success' | 'warning' | 'info' | 'danger' {
  switch (type) {
    case 'INTERNAL': return ''
    case 'EXTERNAL': return 'warning'
    case 'OJT': return 'success'
    case 'ONLINE': return 'info'
    default: return 'info'
  }
}

function trainingTypeLabel(type: string): string {
  switch (type) {
    case 'INTERNAL': return '사내'
    case 'EXTERNAL': return '사외'
    case 'OJT': return '현장'
    case 'ONLINE': return '온라인'
    default: return type
  }
}

function resultTagType(result: string): '' | 'success' | 'warning' | 'info' | 'danger' {
  switch (result) {
    case 'PASS': return 'success'
    case 'FAIL': return 'danger'
    case 'PENDING': return 'info'
    default: return 'info'
  }
}

function resultLabel(result: string): string {
  switch (result) {
    case 'PASS': return '합격'
    case 'FAIL': return '불합격'
    case 'PENDING': return '대기'
    default: return result
  }
}

function getDaysRemaining(dateStr: string): number {
  if (!dateStr) return 0
  const due = dayjs(dateStr)
  const today = dayjs()
  return due.diff(today, 'day')
}

// ---------- Data Loading ----------
onMounted(() => {
  loadCourses()
  loadRecords()
  loadDueSoon()
})

async function loadCourses() {
  loadingCourses.value = true
  try {
    const params: any = {}
    if (courseFilter.value.training_type) params.training_type = courseFilter.value.training_type
    if (courseFilter.value.category) params.category = courseFilter.value.category
    const res = await trainingApi.getCourses(params)
    courses.value = res.data.items || res.data
  } catch (e) {
    console.warn('교육과정 목록 조회 실패:', e)
    ElMessage.error('교육과정 목록을 불러오는데 실패했습니다')
    courses.value = []
  } finally {
    loadingCourses.value = false
  }
}

async function loadRecords() {
  loadingRecords.value = true
  try {
    const params: any = {}
    if (recordFilter.value.course_id) params.course_id = recordFilter.value.course_id
    if (recordFilter.value.trainee_id) params.trainee_id = recordFilter.value.trainee_id
    if (recordFilter.value.result) params.result = recordFilter.value.result
    const res = await trainingApi.getRecords(params)
    records.value = res.data.items || res.data
  } catch (e) {
    console.warn('이수기록 목록 조회 실패:', e)
    ElMessage.error('이수기록 목록을 불러오는데 실패했습니다')
    records.value = []
  } finally {
    loadingRecords.value = false
  }
}

async function loadDueSoon() {
  loadingDueSoon.value = true
  try {
    const res = await trainingApi.getDueSoon(90)
    dueSoonList.value = res.data.items || res.data
  } catch (e) {
    console.warn('재교육 알림 조회 실패:', e)
    ElMessage.error('재교육 알림을 불러오는데 실패했습니다')
    dueSoonList.value = []
  } finally {
    loadingDueSoon.value = false
  }
}

// ---------- Course CRUD ----------
function openCourseDialog() {
  isEditingCourse.value = false
  courseForm.value = {
    course_id: null,
    course_no: '',
    course_name: '',
    category: '',
    training_type: 'INTERNAL',
    duration_hours: 0,
    recurrence_months: 0,
    is_active: true
  }
  showCourseDialog.value = true
}

function editCourse(row: any) {
  isEditingCourse.value = true
  courseForm.value = {
    course_id: row.course_id,
    course_no: row.course_no || '',
    course_name: row.course_name || '',
    category: row.category || '',
    training_type: row.training_type || 'INTERNAL',
    duration_hours: row.duration_hours || 0,
    recurrence_months: row.recurrence_months || 0,
    is_active: row.is_active ?? true
  }
  showCourseDialog.value = true
}

async function deleteCourse(row: any) {
  try {
    await ElMessageBox.confirm(
      `"${row.course_name}"을(를) 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await trainingApi.deleteCourse(row.course_id)
    ElMessage.success('삭제되었습니다.')
    loadCourses()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitCourse() {
  if (!courseForm.value.course_no || !courseForm.value.course_name) {
    ElMessage.warning('과정코드와 과정명을 입력하세요.')
    return
  }

  try {
    const payload = {
      course_no: courseForm.value.course_no,
      course_name: courseForm.value.course_name,
      category: courseForm.value.category || undefined,
      training_type: courseForm.value.training_type,
      duration_hours: courseForm.value.duration_hours,
      recurrence_months: courseForm.value.recurrence_months,
      is_active: courseForm.value.is_active
    }

    if (courseForm.value.course_id) {
      await trainingApi.updateCourse(courseForm.value.course_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await trainingApi.createCourse(payload)
      ElMessage.success('생성되었습니다.')
    }
    showCourseDialog.value = false
    loadCourses()
  } catch (e) {
    console.warn('교육과정 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// ---------- Record CRUD ----------
function openRecordDialog() {
  isEditingRecord.value = false
  recordForm.value = {
    record_id: null,
    course_id: null,
    trainee_id: '',
    training_date: '',
    score: 0,
    result: 'PENDING'
  }
  showRecordDialog.value = true
}

function editRecord(row: any) {
  isEditingRecord.value = true
  recordForm.value = {
    record_id: row.record_id,
    course_id: row.course_id,
    trainee_id: row.trainee_id || '',
    training_date: row.training_date || '',
    score: row.score || 0,
    result: row.result || 'PENDING'
  }
  showRecordDialog.value = true
}

async function deleteRecord(row: any) {
  try {
    await ElMessageBox.confirm(
      `이수기록을 삭제하시겠습니까?`,
      '삭제 확인',
      { type: 'warning' }
    )
    await trainingApi.deleteRecord(row.record_id)
    ElMessage.success('삭제되었습니다.')
    loadRecords()
    loadDueSoon()
  } catch (e: unknown) {
    if (e !== 'cancel' && String(e) !== 'cancel') {
      console.warn('삭제 실패:', e)
      ElMessage.error('삭제에 실패했습니다.')
    }
  }
}

async function submitRecord() {
  if (!recordForm.value.course_id || !recordForm.value.trainee_id || !recordForm.value.training_date) {
    ElMessage.warning('교육과정, 교육생 ID, 교육일을 입력하세요.')
    return
  }

  try {
    const payload = {
      course_id: recordForm.value.course_id,
      trainee_id: recordForm.value.trainee_id,
      training_date: recordForm.value.training_date,
      score: recordForm.value.score,
      result: recordForm.value.result
    }

    if (recordForm.value.record_id) {
      await trainingApi.updateRecord(recordForm.value.record_id, payload)
      ElMessage.success('수정되었습니다.')
    } else {
      await trainingApi.createRecord(payload)
      ElMessage.success('등록되었습니다.')
    }
    showRecordDialog.value = false
    loadRecords()
    loadDueSoon()
  } catch (e) {
    console.warn('이수기록 저장 실패:', e)
    ElMessage.error('저장에 실패했습니다.')
  }
}

// ---------- Bulk Records ----------
function openBulkDialog() {
  bulkForm.value = {
    course_id: null,
    training_date: '',
    trainee_ids: '',
    result: 'PENDING'
  }
  showBulkDialog.value = true
}

async function submitBulkRecords() {
  if (!bulkForm.value.course_id || !bulkForm.value.training_date || !bulkForm.value.trainee_ids.trim()) {
    ElMessage.warning('교육과정, 교육일, 교육생 ID를 입력하세요.')
    return
  }

  try {
    const traineeIds = bulkForm.value.trainee_ids
      .split(',')
      .map(id => id.trim())
      .filter(id => id.length > 0)

    if (traineeIds.length === 0) {
      ElMessage.warning('유효한 교육생 ID를 입력하세요.')
      return
    }

    await trainingApi.bulkCreateRecords({
      course_id: bulkForm.value.course_id,
      training_date: bulkForm.value.training_date,
      trainee_ids: traineeIds,
      result: bulkForm.value.result
    })
    ElMessage.success(`${traineeIds.length}건이 일괄등록되었습니다.`)
    showBulkDialog.value = false
    loadRecords()
    loadDueSoon()
  } catch (e) {
    console.warn('일괄등록 실패:', e)
    ElMessage.error('일괄등록에 실패했습니다.')
  }
}
</script>

<style scoped>
</style>
