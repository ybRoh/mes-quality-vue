<template>
  <div class="page-container">
    <PageHeader title="SPC (통계적 공정관리)" subtitle="관리도 및 공정능력 분석" />

    <div class="card">
      <div class="filter-bar">
        <el-select v-model="selectedProduct" placeholder="제품 선택" filterable @change="loadSpecs" style="width: 200px;">
          <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-select v-model="selectedSpec" placeholder="특성 선택 (CTQ)" filterable style="width: 250px;">
          <el-option v-for="s in specs" :key="s.id" :label="`${s.name} (${s.usl}/${s.lsl})`" :value="s.id" />
        </el-select>
        <el-select v-model="sampleCount" placeholder="샘플 수" style="width: 130px;">
          <el-option :value="25" label="25개" />
          <el-option :value="50" label="50개" />
          <el-option :value="100" label="100개" />
          <el-option :value="200" label="200개" />
        </el-select>
        <el-button type="primary" @click="loadSpcData">
          <el-icon><Search /></el-icon>
          분석
        </el-button>
      </div>
    </div>

    <div v-if="spcData" v-loading="loading">
      <!-- SPC Chart -->
      <SpcChart
        :values="spcData.values"
        :mean="spcData.mean"
        :ucl="spcData.ucl"
        :lcl="spcData.lcl"
        :usl="spcData.usl"
        :lsl="spcData.lsl"
        title="X-bar 관리도"
      />

      <!-- Capability Indices -->
      <div class="kpi-row" style="margin-top: 16px;">
        <KpiCard
          title="Cp"
          :value="capability.cp"
          :color="getCpkColor(capability.cp)"
        >
          <template #footer>공정능력 (양쪽)</template>
        </KpiCard>
        <KpiCard
          title="Cpk"
          :value="capability.cpk"
          :color="getCpkColor(capability.cpk)"
        >
          <template #footer>공정능력지수 (한쪽)</template>
        </KpiCard>
        <KpiCard
          title="Pp"
          :value="capability.pp"
          :color="getCpkColor(capability.pp)"
        >
          <template #footer>공정성능 (양쪽)</template>
        </KpiCard>
        <KpiCard
          title="Ppk"
          :value="capability.ppk"
          :color="getCpkColor(capability.ppk)"
        >
          <template #footer>공정성능지수 (한쪽)</template>
        </KpiCard>
      </div>

      <!-- Statistics Summary -->
      <div class="card" style="margin-top: 16px;">
        <div class="card-title">통계 요약</div>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="평균 (Mean)">{{ stats.mean?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="표준편차 (Std)">{{ stats.std?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="최소값 (Min)">{{ stats.min?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="최대값 (Max)">{{ stats.max?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="데이터 수">{{ stats.count }}</el-descriptions-item>
          <el-descriptions-item label="UCL">{{ spcData.ucl?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="LCL">{{ spcData.lcl?.toFixed(4) }}</el-descriptions-item>
          <el-descriptions-item label="이탈 건수">
            <el-tag :type="stats.oocCount > 0 ? 'danger' : 'success'">{{ stats.oocCount }}건</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- Judgment -->
      <div class="card" style="margin-top: 16px;">
        <div class="card-title">공정능력 판정</div>
        <el-result
          :icon="judgmentIcon"
          :title="judgmentTitle"
          :sub-title="judgmentSubtitle"
        />
      </div>
    </div>

    <el-empty v-else-if="!loading" description="제품과 특성을 선택하고 분석 버튼을 클릭하세요." />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import KpiCard from '@/components/common/KpiCard.vue'
import SpcChart from '@/components/charts/SpcChart.vue'
import { spcApi } from '@/api/quality'

const loading = ref(false)
const products = ref<{ id: number; name: string }[]>([])
const specs = ref<{ id: number; name: string; usl: number; lsl: number }[]>([])
const selectedProduct = ref<number | null>(null)
const selectedSpec = ref<number | null>(null)
const sampleCount = ref(50)

const spcData = ref<{
  values: number[]
  mean: number
  ucl: number
  lcl: number
  usl?: number
  lsl?: number
} | null>(null)

const capability = ref({ cp: 0, cpk: 0, pp: 0, ppk: 0 })
const stats = ref({ mean: 0, std: 0, min: 0, max: 0, count: 0, oocCount: 0 })

const judgmentIcon = computed(() => {
  if (capability.value.cpk >= 1.33) return 'success'
  if (capability.value.cpk >= 1.0) return 'warning'
  return 'error'
})

const judgmentTitle = computed(() => {
  if (capability.value.cpk >= 1.67) return '우수 (Excellent)'
  if (capability.value.cpk >= 1.33) return '양호 (Good)'
  if (capability.value.cpk >= 1.0) return '한계 (Marginal)'
  return '부적합 (Poor)'
})

const judgmentSubtitle = computed(() => {
  if (capability.value.cpk >= 1.33) return 'Cpk >= 1.33: 공정이 안정적이고 규격을 충족합니다.'
  if (capability.value.cpk >= 1.0) return 'Cpk >= 1.0: 공정 개선이 필요합니다.'
  return 'Cpk < 1.0: 즉각적인 조치가 필요합니다.'
})

function getCpkColor(value: number): string {
  if (value >= 1.33) return '#107E3E'
  if (value >= 1.0) return '#E9730C'
  return '#BB0000'
}

onMounted(async () => {
  try {
    const res = await spcApi.getProducts()
    products.value = res.data
  } catch (e) {
    console.warn('제품 목록 조회 실패:', e)
    ElMessage.error('제품 목록을 불러오는데 실패했습니다')
    products.value = []
  }
})

async function loadSpecs() {
  if (!selectedProduct.value) return
  selectedSpec.value = null
  spcData.value = null

  try {
    const res = await spcApi.getSpecs(selectedProduct.value)
    specs.value = res.data
  } catch (e) {
    console.warn('특성 목록 조회 실패:', e)
    ElMessage.error('특성 목록을 불러오는데 실패했습니다')
    specs.value = []
  }
}

async function loadSpcData() {
  if (!selectedSpec.value) return
  loading.value = true

  try {
    const [dataRes, capRes] = await Promise.all([
      spcApi.getData({ spec_id: selectedSpec.value, sample_count: sampleCount.value }),
      spcApi.getCapability(selectedSpec.value, sampleCount.value)
    ])

    spcData.value = dataRes.data
    capability.value = capRes.data.capability || capRes.data

    const rawValues = dataRes.data.values
    const values = Array.isArray(rawValues) ? rawValues : []
    const mean = values.length > 0 ? values.reduce((s: number, v: number) => s + v, 0) / values.length : 0
    const std = values.length > 1 ? Math.sqrt(values.reduce((s: number, v: number) => s + Math.pow(v - mean, 2), 0) / (values.length - 1)) : 0
    const oocCount = values.filter((v: number) => v > dataRes.data.ucl || v < dataRes.data.lcl).length

    stats.value = {
      mean,
      std,
      min: values.length > 0 ? Math.min(...values) : 0,
      max: values.length > 0 ? Math.max(...values) : 0,
      count: values.length,
      oocCount
    }
  } catch (e) {
    console.warn('SPC 데이터 조회 실패:', e)
    ElMessage.error('SPC 데이터를 불러오는데 실패했습니다')
    spcData.value = null
    capability.value = { cp: 0, cpk: 0, pp: 0, ppk: 0 }
    stats.value = { mean: 0, std: 0, min: 0, max: 0, count: 0, oocCount: 0 }
  } finally {
    loading.value = false
  }
}
</script>
