import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/components/common/AppLayout.vue'),
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      // 생산분석
      {
        path: 'analysis/period',
        name: 'PeriodAnalysis',
        component: () => import('@/views/analysis/PeriodAnalysis.vue')
      },
      {
        path: 'analysis/type',
        name: 'TypeAnalysis',
        component: () => import('@/views/analysis/TypeAnalysis.vue')
      },
      {
        path: 'analysis/equipment',
        name: 'EquipmentAnalysis',
        component: () => import('@/views/analysis/EquipmentAnalysis.vue')
      },
      {
        path: 'analysis/spec',
        name: 'SpecAnalysis',
        component: () => import('@/views/analysis/SpecAnalysis.vue')
      },
      // IATF 16949
      {
        path: 'quality/apqp',
        name: 'APQP',
        component: () => import('@/views/quality/ApqpView.vue')
      },
      {
        path: 'quality/fmea',
        name: 'FMEA',
        component: () => import('@/views/quality/FmeaView.vue')
      },
      {
        path: 'quality/control-plan',
        name: 'ControlPlan',
        component: () => import('@/views/quality/ControlPlanView.vue')
      },
      {
        path: 'quality/msa',
        name: 'MSA',
        component: () => import('@/views/quality/MsaView.vue')
      },
      {
        path: 'quality/spc',
        name: 'SPC',
        component: () => import('@/views/quality/SpcView.vue')
      },
      {
        path: 'quality/ppap',
        name: 'PPAP',
        component: () => import('@/views/quality/PpapView.vue')
      },
      {
        path: 'quality/claim',
        name: 'Claim',
        component: () => import('@/views/quality/ClaimView.vue')
      },
      {
        path: 'quality/inspection',
        name: 'Inspection',
        component: () => import('@/views/quality/InspectionView.vue')
      },
      // 표준문서관리
      {
        path: 'quality/document',
        name: 'Document',
        component: () => import('@/views/quality/DocumentView.vue')
      },
      // 규격관리
      {
        path: 'quality/specification',
        name: 'Specification',
        component: () => import('@/views/quality/SpecificationView.vue')
      },
      {
        path: 'quality/si-faq',
        name: 'SiFaq',
        component: () => import('@/views/quality/SiFaqView.vue')
      },
      {
        path: 'quality/csr',
        name: 'Csr',
        component: () => import('@/views/quality/CsrView.vue')
      },
      // 내부심사관리
      {
        path: 'quality/audit-requirement',
        name: 'AuditRequirement',
        component: () => import('@/views/quality/AuditRequirementView.vue')
      },
      {
        path: 'quality/audit-plan',
        name: 'AuditPlan',
        component: () => import('@/views/quality/AuditPlanView.vue')
      },
      {
        path: 'quality/audit-finding',
        name: 'AuditFinding',
        component: () => import('@/views/quality/AuditFindingView.vue')
      },
      {
        path: 'quality/corrective-action',
        name: 'CorrectiveAction',
        component: () => import('@/views/quality/CorrectiveActionView.vue')
      },
      // 고객심사관리
      {
        path: 'quality/customer-audit',
        name: 'CustomerAudit',
        component: () => import('@/views/quality/CustomerAuditView.vue')
      },
      {
        path: 'quality/customer-audit-finding',
        name: 'CustomerAuditFinding',
        component: () => import('@/views/quality/CustomerAuditFindingView.vue')
      },
      {
        path: 'quality/customer-audit-action',
        name: 'CustomerAuditAction',
        component: () => import('@/views/quality/CustomerAuditActionView.vue')
      },
      // 교육/자격관리
      {
        path: 'quality/training',
        name: 'Training',
        component: () => import('@/views/quality/TrainingView.vue')
      },
      {
        path: 'quality/qualification',
        name: 'Qualification',
        component: () => import('@/views/quality/QualificationView.vue')
      },
      {
        path: 'quality/competency',
        name: 'Competency',
        component: () => import('@/views/quality/CompetencyView.vue')
      },
      // 성과지표관리
      {
        path: 'quality/kpi-dashboard',
        name: 'KpiDashboard',
        component: () => import('@/views/quality/KpiDashboardView.vue')
      },
      {
        path: 'quality/kpi-definition',
        name: 'KpiDefinition',
        component: () => import('@/views/quality/KpiDefinitionView.vue')
      },
      {
        path: 'quality/process-monitor',
        name: 'ProcessMonitor',
        component: () => import('@/views/quality/ProcessMonitorView.vue')
      },
      {
        path: 'quality/risk-issue',
        name: 'RiskIssue',
        component: () => import('@/views/quality/RiskIssueView.vue')
      },
      // Q&A
      {
        path: 'quality/qna',
        name: 'QnA',
        component: () => import('@/views/quality/QnaView.vue'),
        meta: { title: 'Q&A' },
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let sessionVerified = false

router.beforeEach(async (to, _from, next) => {
  // Reset session verification flag when navigating to login (e.g. after logout)
  if (to.path === '/login') {
    sessionVerified = false
  }

  if (to.meta.public) {
    next()
    return
  }

  const authStore = useAuthStore()
  if (!authStore.isLoggedIn) {
    next('/login')
    return
  }

  if (!sessionVerified) {
    try {
      await authStore.checkSession()
      sessionVerified = true
    } catch {
      authStore.logout()
      next('/login')
      return
    }
  }

  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!to.meta.roles.includes(authStore.role)) {
      ElMessage.warning('접근 권한이 없습니다.')
      next('/')
      return
    }
  }

  next()
})

export default router
