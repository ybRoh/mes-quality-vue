<template>
  <div class="page-container">
    <PageHeader title="KPI 대시보드" subtitle="핵심 성과지표 현황판" />

    <!-- Summary row -->
    <div class="summary-row">
      <div class="summary-card">
        <div class="summary-label">활성 KPI</div>
        <div class="summary-value">{{ dashboardItems.length }}</div>
      </div>
      <div class="summary-card summary-green">
        <div class="summary-label">GREEN</div>
        <div class="summary-value">{{ greenCount }}</div>
      </div>
      <div class="summary-card summary-yellow">
        <div class="summary-label">YELLOW</div>
        <div class="summary-value">{{ yellowCount }}</div>
      </div>
      <div class="summary-card summary-red">
        <div class="summary-label">RED</div>
        <div class="summary-value">{{ redCount }}</div>
      </div>
    </div>

    <!-- KPI Cards Grid -->
    <div class="kpi-grid" v-loading="loading">
      <el-empty v-if="!loading && dashboardItems.length === 0" description="등록된 활성 KPI가 없습니다." />

      <el-card
        v-for="item in dashboardItems"
        :key="item.kpi_id"
        class="kpi-card"
        shadow="hover"
      >
        <div class="kpi-card-header">
          <span class="kpi-card-name">{{ item.kpi_name }}</span>
          <el-tag v-if="item.category" size="small" type="info">{{ item.category }}</el-tag>
        </div>

        <div class="kpi-card-body">
          <div class="kpi-card-value-row">
            <span
              class="kpi-status-dot"
              :style="{ backgroundColor: getStatusColor(item.latest_status) }"
            />
            <span class="kpi-card-value">
              {{ item.latest_value !== null && item.latest_value !== undefined ? item.latest_value : '-' }}
            </span>
            <span class="kpi-card-unit">{{ item.unit || '' }}</span>
          </div>

          <div class="kpi-card-target">
            목표: {{ item.target_value !== null && item.target_value !== undefined ? item.target_value : '-' }}
            {{ item.unit || '' }}
            <span class="kpi-direction">({{ item.target_direction === 'HIGHER' ? '높을수록 양호' : '낮을수록 양호' }})</span>
          </div>

          <div class="kpi-card-trend" v-if="item.trend && item.trend.length > 0">
            <span class="trend-label">추이 (최근 {{ item.trend.length }}기):</span>
            <span class="trend-values">
              {{ item.trend.map((v: number) => v.toFixed(1)).join(' → ') }}
            </span>
          </div>
          <div class="kpi-card-trend" v-else>
            <span class="trend-label">데이터 없음</span>
          </div>
        </div>

        <div class="kpi-card-footer">
          <span class="kpi-card-no">{{ item.kpi_no }}</span>
          <el-tag
            :type="getStatusTagType(item.latest_status)"
            size="small"
            effect="dark"
          >
            {{ item.latest_status || 'N/A' }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { kpiApi } from '@/api/quality'

const loading = ref(false)
const dashboardItems = ref<any[]>([])

const greenCount = computed(() => dashboardItems.value.filter(i => i.latest_status === 'GREEN').length)
const yellowCount = computed(() => dashboardItems.value.filter(i => i.latest_status === 'YELLOW').length)
const redCount = computed(() => dashboardItems.value.filter(i => i.latest_status === 'RED').length)

function getStatusColor(status: string | null): string {
  switch (status) {
    case 'GREEN': return '#67C23A'
    case 'YELLOW': return '#E6A23C'
    case 'RED': return '#F56C6C'
    default: return '#C0C4CC'
  }
}

function getStatusTagType(status: string | null): '' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status) {
    case 'GREEN': return 'success'
    case 'YELLOW': return 'warning'
    case 'RED': return 'danger'
    default: return 'info'
  }
}

onMounted(() => {
  loadDashboard()
})

async function loadDashboard() {
  loading.value = true
  try {
    const res = await kpiApi.getDashboard()
    dashboardItems.value = res.data || []
  } catch (e) {
    console.warn('KPI 대시보드 조회 실패:', e)
    ElMessage.error('KPI 대시보드를 불러오는데 실패했습니다')
    dashboardItems.value = []
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.summary-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  flex: 1;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px 20px;
  text-align: center;
  border-left: 4px solid #909399;
}

.summary-card.summary-green {
  border-left-color: #67C23A;
  background: #f0f9eb;
}

.summary-card.summary-yellow {
  border-left-color: #E6A23C;
  background: #fdf6ec;
}

.summary-card.summary-red {
  border-left-color: #F56C6C;
  background: #fef0f0;
}

.summary-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.kpi-card {
  border-radius: 8px;
}

.kpi-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.kpi-card-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.kpi-card-body {
  margin-bottom: 12px;
}

.kpi-card-value-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.kpi-status-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
}

.kpi-card-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
}

.kpi-card-unit {
  font-size: 14px;
  color: #909399;
  align-self: flex-end;
  margin-bottom: 4px;
}

.kpi-card-target {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.kpi-direction {
  color: #909399;
  font-size: 12px;
}

.kpi-card-trend {
  font-size: 12px;
  color: #606266;
}

.trend-label {
  color: #909399;
  margin-right: 4px;
}

.trend-values {
  font-family: monospace;
  color: #303133;
}

.kpi-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid #EBEEF5;
}

.kpi-card-no {
  font-size: 12px;
  color: #909399;
}
</style>
