<template>
  <el-container class="app-layout">
    <!-- Sidebar -->
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="app-sidebar">
      <div class="sidebar-header">
        <div v-if="!isCollapsed" class="sidebar-title">
          <el-icon :size="24"><Setting /></el-icon>
          <span>품질관리시스템</span>
        </div>
        <div v-else class="sidebar-title-collapsed">
          <el-icon :size="20"><Setting /></el-icon>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :router="true"
        background-color="#354A5F"
        text-color="#FFFFFF"
        active-text-color="#6CC0F7"
        class="sidebar-menu"
      >
        <!-- 대시보드 -->
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <template #title>대시보드</template>
        </el-menu-item>

        <!-- 생산분석 -->
        <el-sub-menu index="analysis">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>생산분석</span>
          </template>
          <el-menu-item index="/analysis/period">
            <el-icon><Calendar /></el-icon>
            <span>기간별 분석</span>
          </el-menu-item>
          <el-menu-item index="/analysis/type">
            <el-icon><PieChart /></el-icon>
            <span>유형별 분석</span>
          </el-menu-item>
          <el-menu-item index="/analysis/equipment">
            <el-icon><Monitor /></el-icon>
            <span>설비별 분석</span>
          </el-menu-item>
          <el-menu-item index="/analysis/spec">
            <el-icon><Document /></el-icon>
            <span>규격별 분석</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- IATF 16949 -->
        <el-sub-menu index="quality">
          <template #title>
            <el-icon><Trophy /></el-icon>
            <span>IATF 16949</span>
          </template>
          <el-menu-item index="/quality/apqp">
            <el-icon><List /></el-icon>
            <span>APQP</span>
          </el-menu-item>
          <el-menu-item index="/quality/fmea">
            <el-icon><Warning /></el-icon>
            <span>FMEA</span>
          </el-menu-item>
          <el-menu-item index="/quality/control-plan">
            <el-icon><Notebook /></el-icon>
            <span>관리계획서</span>
          </el-menu-item>
          <el-menu-item index="/quality/msa">
            <el-icon><Aim /></el-icon>
            <span>MSA (GR&amp;R)</span>
          </el-menu-item>
          <el-menu-item index="/quality/spc">
            <el-icon><TrendCharts /></el-icon>
            <span>SPC</span>
          </el-menu-item>
          <el-menu-item index="/quality/ppap">
            <el-icon><Stamp /></el-icon>
            <span>PPAP</span>
          </el-menu-item>
          <el-menu-item index="/quality/claim">
            <el-icon><ChatDotSquare /></el-icon>
            <span>클레임 (8D)</span>
          </el-menu-item>
          <el-menu-item index="/quality/inspection">
            <el-icon><Search /></el-icon>
            <span>검사이력</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- Main Area -->
    <el-container class="app-main-container">
      <!-- Header -->
      <el-header class="app-header" height="56px">
        <div class="header-left">
          <el-icon
            class="collapse-toggle"
            :size="20"
            @click="isCollapsed = !isCollapsed"
            aria-label="사이드바 접기/펼치기"
          >
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <span class="user-info">
            <el-icon><User /></el-icon>
            {{ authStore.userName || '사용자' }}
            <el-tag size="small" type="info" style="margin-left: 4px;">{{ authStore.role || 'USER' }}</el-tag>
          </span>
          <el-button text @click="handleLogout" class="logout-btn" aria-label="로그아웃">
            <el-icon><SwitchButton /></el-icon>
            로그아웃
          </el-button>
        </div>
      </el-header>

      <!-- Content -->
      <el-main class="app-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Setting,
  Odometer,
  DataAnalysis,
  Calendar,
  PieChart,
  Monitor,
  Document,
  Trophy,
  List,
  Warning,
  Notebook,
  Aim,
  TrendCharts,
  Stamp,
  ChatDotSquare,
  Search,
  User,
  SwitchButton,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const authStore = useAuthStore()
const route = useRoute()
const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)

function handleLogout() {
  authStore.logout()
}
</script>

<style scoped>
.app-layout {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.app-sidebar {
  background-color: var(--qms-bg-sidebar);
  transition: width 0.3s ease;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--qms-bg-white);
  font-size: 16px;
  font-weight: 700;
  white-space: nowrap;
}

.sidebar-title-collapsed {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  color: var(--qms-bg-white);
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.app-main-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--qms-bg-white);
  border-bottom: 1px solid var(--qms-border);
  padding: 0 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-toggle {
  cursor: pointer;
  color: var(--qms-text-secondary);
  transition: color 0.2s;
}

.collapse-toggle:hover {
  color: var(--qms-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--qms-text-primary);
}

.logout-btn {
  color: var(--qms-text-secondary);
}

.logout-btn:hover {
  color: var(--qms-danger);
}

.app-content {
  flex: 1;
  overflow-y: auto;
  background-color: var(--qms-bg-light);
  padding: 20px;
}
</style>
