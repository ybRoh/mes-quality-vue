<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" label-position="top">
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="공정번호" prop="process_no">
          <el-input v-model="form.process_no" placeholder="공정번호 입력" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="공정명" prop="process_name">
          <el-input v-model="form.process_name" placeholder="공정명 입력" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="설비/장치" prop="machine">
          <el-input v-model="form.machine" placeholder="설비/장치 입력" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="특성 분류" prop="characteristic_class">
          <el-select v-model="form.characteristic_class" placeholder="선택" style="width: 100%;">
            <el-option label="CTQ (중요)" value="CTQ" />
            <el-option label="Major" value="MAJOR" />
            <el-option label="Minor" value="MINOR" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="제품특성" prop="product_characteristic">
          <el-input v-model="form.product_characteristic" placeholder="제품특성 입력" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="공정특성" prop="process_characteristic">
          <el-input v-model="form.process_characteristic" placeholder="공정특성 입력" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="규격/공차" prop="specification">
          <el-input v-model="form.specification" placeholder="예: 10.0 +/- 0.1" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="특별특성 기호" prop="special_char_symbol">
          <el-select v-model="form.special_char_symbol" placeholder="선택" style="width: 100%;" clearable>
            <el-option label="없음" value="" />
            <el-option label="CC (Critical)" value="CC" />
            <el-option label="SC (Significant)" value="SC" />
            <el-option label="HI (High Impact)" value="HI" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="FMEA 연계" prop="fmea_id">
          <el-select v-model="form.fmea_id" placeholder="FMEA 선택" style="width: 100%;" clearable filterable>
            <el-option
              v-for="fmea in fmeaList"
              :key="fmea.id"
              :label="fmea.name"
              :value="fmea.id"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">평가/측정 방법</el-divider>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="평가/측정 기법" prop="evaluation_method">
          <el-input v-model="form.evaluation_method" placeholder="예: 마이크로미터, 하이트게이지" />
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="시료크기" prop="sample_size">
          <el-input-number v-model="form.sample_size" :min="1" style="width: 100%;" />
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="시료빈도" prop="sample_frequency">
          <el-input v-model="form.sample_frequency" placeholder="예: 2시간/1회" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="관리방법" prop="control_method">
          <el-input v-model="form.control_method" type="textarea" :rows="2" placeholder="관리방법 입력" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="대응계획" prop="reaction_plan">
          <el-input v-model="form.reaction_plan" type="textarea" :rows="2" placeholder="이상발생 시 대응계획" />
        </el-form-item>
      </el-col>
    </el-row>

    <div class="form-actions">
      <el-button @click="emit('cancel')" aria-label="취소">취소</el-button>
      <el-button type="primary" @click="handleSubmit" aria-label="저장">저장</el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

interface ControlPlanItem {
  id?: number
  process_no: string
  process_name: string
  machine: string
  characteristic_class: string
  product_characteristic: string
  process_characteristic: string
  specification: string
  special_char_symbol: string
  fmea_id: number | null
  evaluation_method: string
  sample_size: number
  sample_frequency: string
  control_method: string
  reaction_plan: string
}

interface FmeaOption {
  id: number
  name: string
}

interface Props {
  modelValue?: Partial<ControlPlanItem>
  fmeaList?: FmeaOption[]
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => ({}),
  fmeaList: () => []
})

const emit = defineEmits<{
  submit: [data: ControlPlanItem]
  cancel: []
}>()

const formRef = ref<FormInstance>()

const defaultForm: ControlPlanItem = {
  process_no: '',
  process_name: '',
  machine: '',
  characteristic_class: 'MINOR',
  product_characteristic: '',
  process_characteristic: '',
  specification: '',
  special_char_symbol: '',
  fmea_id: null,
  evaluation_method: '',
  sample_size: 5,
  sample_frequency: '',
  control_method: '',
  reaction_plan: ''
}

const form = ref<ControlPlanItem>({ ...defaultForm })

watch(() => props.modelValue, (val) => {
  form.value = { ...defaultForm, ...val }
}, { immediate: true, deep: true })

const rules: FormRules = {
  process_no: [{ required: true, message: '공정번호를 입력하세요', trigger: 'blur' }],
  process_name: [{ required: true, message: '공정명을 입력하세요', trigger: 'blur' }],
  product_characteristic: [{ required: true, message: '제품특성을 입력하세요', trigger: 'blur' }],
  specification: [{ required: true, message: '규격/공차를 입력하세요', trigger: 'blur' }],
  evaluation_method: [{ required: true, message: '평가방법을 입력하세요', trigger: 'blur' }],
  control_method: [{ required: true, message: '관리방법을 입력하세요', trigger: 'blur' }],
  reaction_plan: [{ required: true, message: '대응계획을 입력하세요', trigger: 'blur' }]
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    emit('submit', { ...form.value })
  } catch {
    // validation failed
  }
}
</script>

<style scoped>
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #E5E5E5;
}
</style>
