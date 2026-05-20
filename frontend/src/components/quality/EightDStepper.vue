<template>
  <div class="eight-d-stepper">
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step v-for="step in steps" :key="step.no" :title="step.title" :description="step.description" />
    </el-steps>

    <div class="step-content">
      <!-- D1: 팀 구성 -->
      <div v-if="currentStep === 0" class="step-form">
        <h3 class="step-heading">D1 - 팀 구성</h3>
        <el-form label-position="top">
          <el-form-item label="팀장">
            <el-input v-model="formData.d1_team_leader" placeholder="팀장명 입력" />
          </el-form-item>
          <el-form-item label="팀원">
            <el-input v-model="formData.d1_team_members" type="textarea" :rows="3" placeholder="팀원명 (쉼표로 구분)" />
          </el-form-item>
          <el-form-item label="팀 구성일">
            <el-date-picker v-model="formData.d1_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" placeholder="날짜 선택" style="width: 100%;" />
          </el-form-item>
        </el-form>
      </div>

      <!-- D2: 문제 기술 -->
      <div v-if="currentStep === 1" class="step-form">
        <h3 class="step-heading">D2 - 문제 기술</h3>
        <el-form label-position="top">
          <el-form-item label="문제 제목">
            <el-input v-model="formData.d2_problem_title" placeholder="문제 제목" />
          </el-form-item>
          <el-form-item label="문제 상세 (5W2H)">
            <el-input v-model="formData.d2_problem_description" type="textarea" :rows="5" placeholder="What, When, Where, Who, Why, How, How many" />
          </el-form-item>
          <el-form-item label="영향 범위">
            <el-input v-model="formData.d2_impact_scope" type="textarea" :rows="2" placeholder="영향받은 제품/공정/고객" />
          </el-form-item>
        </el-form>
      </div>

      <!-- D3: 임시 조치 -->
      <div v-if="currentStep === 2" class="step-form">
        <h3 class="step-heading">D3 - 잠정 봉쇄조치</h3>
        <el-form label-position="top">
          <el-form-item label="잠정 봉쇄조치 내용">
            <el-input v-model="formData.d3_containment_action" type="textarea" :rows="4" placeholder="즉각적인 봉쇄/격리 조치 내용" />
          </el-form-item>
          <el-form-item label="조치 실행일">
            <el-date-picker v-model="formData.d3_action_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" placeholder="날짜 선택" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="검증 결과">
            <el-input v-model="formData.d3_verification" type="textarea" :rows="2" placeholder="봉쇄조치 효과 검증" />
          </el-form-item>
        </el-form>
      </div>

      <!-- D4: 근본 원인 분석 -->
      <div v-if="currentStep === 3" class="step-form">
        <h3 class="step-heading">D4 - 근본원인 분석</h3>
        <el-form label-position="top">
          <el-form-item label="근본원인 (발생)">
            <el-input v-model="formData.d4_root_cause_occurrence" type="textarea" :rows="4" placeholder="5 Why, 특성요인도 등을 통한 발생 원인 분석" />
          </el-form-item>
          <el-form-item label="근본원인 (유출)">
            <el-input v-model="formData.d4_root_cause_escape" type="textarea" :rows="4" placeholder="검출 실패 원인 분석" />
          </el-form-item>
          <el-form-item label="검증 방법">
            <el-input v-model="formData.d4_verification_method" type="textarea" :rows="2" placeholder="근본원인 검증 방법" />
          </el-form-item>
        </el-form>
      </div>

      <!-- D5: 영구 대책 선정 -->
      <div v-if="currentStep === 4" class="step-form">
        <h3 class="step-heading">D5 - 영구대책 선정</h3>
        <el-form label-position="top">
          <el-form-item label="영구대책 (발생 방지)">
            <el-input v-model="formData.d5_permanent_action_occurrence" type="textarea" :rows="4" placeholder="발생 방지를 위한 영구대책" />
          </el-form-item>
          <el-form-item label="영구대책 (유출 방지)">
            <el-input v-model="formData.d5_permanent_action_escape" type="textarea" :rows="4" placeholder="유출 방지를 위한 영구대책" />
          </el-form-item>
        </el-form>
      </div>

      <!-- D6: 대책 실행 및 검증 -->
      <div v-if="currentStep === 5" class="step-form">
        <h3 class="step-heading">D6 - 대책 실행 및 검증</h3>
        <el-form label-position="top">
          <el-form-item label="실행 내용">
            <el-input v-model="formData.d6_implementation" type="textarea" :rows="4" placeholder="영구대책 실행 내용" />
          </el-form-item>
          <el-form-item label="실행일">
            <el-date-picker v-model="formData.d6_implementation_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" placeholder="날짜 선택" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="효과 검증 결과">
            <el-input v-model="formData.d6_effectiveness_verification" type="textarea" :rows="3" placeholder="대책 효과 검증 결과 (데이터 기반)" />
          </el-form-item>
        </el-form>
      </div>

      <!-- D7: 재발 방지 -->
      <div v-if="currentStep === 6" class="step-form">
        <h3 class="step-heading">D7 - 재발 방지</h3>
        <el-form label-position="top">
          <el-form-item label="시스템 변경사항">
            <el-input v-model="formData.d7_system_changes" type="textarea" :rows="4" placeholder="관리계획서, FMEA, 작업표준서 등 변경사항" />
          </el-form-item>
          <el-form-item label="수평전개">
            <el-input v-model="formData.d7_horizontal_deployment" type="textarea" :rows="3" placeholder="유사 공정/제품 수평전개 내용" />
          </el-form-item>
          <el-form-item label="교육/훈련">
            <el-input v-model="formData.d7_training" type="textarea" :rows="2" placeholder="관련 교육 계획 및 실행" />
          </el-form-item>
        </el-form>
      </div>

      <!-- D8: 팀 인정 및 종결 -->
      <div v-if="currentStep === 7" class="step-form">
        <h3 class="step-heading">D8 - 팀 인정 및 종결</h3>
        <el-form label-position="top">
          <el-form-item label="팀 활동 요약">
            <el-input v-model="formData.d8_team_summary" type="textarea" :rows="4" placeholder="전체 8D 활동 요약" />
          </el-form-item>
          <el-form-item label="종결일">
            <el-date-picker v-model="formData.d8_close_date" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" placeholder="날짜 선택" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="승인자">
            <el-input v-model="formData.d8_approved_by" placeholder="승인자" />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div class="step-actions">
      <el-button v-if="currentStep > 0" @click="prevStep">이전</el-button>
      <el-button type="primary" @click="handleSave" aria-label="현재 단계 저장">
        저장
      </el-button>
      <el-button v-if="currentStep < 7" type="success" @click="nextStep" aria-label="다음 단계로 이동">
        다음 단계
      </el-button>
      <el-button v-if="currentStep === 7" type="success" @click="handleComplete" aria-label="8D 프로세스 종결">
        8D 종결
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  claim: Record<string, any>
  activeStep?: number
}

const props = withDefaults(defineProps<Props>(), {
  activeStep: 0
})

const emit = defineEmits<{
  save: [step: number, data: Record<string, any>]
  complete: []
}>()

const currentStep = ref(props.activeStep)
const formData = ref<Record<string, any>>({})

const steps = [
  { no: 1, title: 'D1', description: '팀 구성' },
  { no: 2, title: 'D2', description: '문제 기술' },
  { no: 3, title: 'D3', description: '봉쇄조치' },
  { no: 4, title: 'D4', description: '근본원인' },
  { no: 5, title: 'D5', description: '영구대책' },
  { no: 6, title: 'D6', description: '실행/검증' },
  { no: 7, title: 'D7', description: '재발방지' },
  { no: 8, title: 'D8', description: '종결' }
]

watch(() => props.claim, (val) => {
  formData.value = { ...val }
}, { immediate: true, deep: true })

watch(() => props.activeStep, (val) => {
  currentStep.value = val
})

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function nextStep() {
  handleSave()
  if (currentStep.value < 7) {
    currentStep.value++
  }
}

function handleSave() {
  emit('save', currentStep.value + 1, { ...formData.value })
}

function handleComplete() {
  handleSave()
  emit('complete')
}
</script>

<style scoped>
.eight-d-stepper {
  padding: 20px;
}

.step-content {
  margin-top: 30px;
  min-height: 300px;
}

.step-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #FFFFFF;
  border-radius: 8px;
  border: 1px solid #E5E5E5;
}

.step-heading {
  font-size: 18px;
  font-weight: 600;
  color: #354A5F;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #0A6ED1;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #E5E5E5;
}
</style>
