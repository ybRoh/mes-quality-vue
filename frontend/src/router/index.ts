import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
      }
    ]
  }
]

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (!to.meta.public) {
    const token = authStore.token
    if (!authStore.isLoggedIn || !token || isTokenExpired(token)) {
      authStore.logout()
      next('/login')
      return
    }
  }
  next()
})

export default router
