import client from './client'

export interface DateRangeParams {
  from: string
  to: string
}

export interface PeriodDailyParams {
  date: string
}

export interface PeriodMonthlyParams {
  year: number
  month: number
}

export interface PeriodYearlyParams {
  year: number
}

export interface EquipmentParams extends DateRangeParams {
  machine_id?: string
}

export interface SpecParams extends DateRangeParams {
  product_id?: string
}

export const analysisApi = {
  // 기간별 분석 (Period Analysis)
  getDailyProduction(params: PeriodDailyParams) {
    return client.get('/analysis/period/daily', { params })
  },

  getMonthlyProduction(params: PeriodMonthlyParams) {
    return client.get('/analysis/period/monthly', { params })
  },

  getYearlyProduction(params: PeriodYearlyParams) {
    return client.get('/analysis/period/yearly', { params })
  },

  getByEquipment(params: EquipmentParams) {
    return client.get('/analysis/period/by-equipment', { params })
  },

  getBySpec(params: SpecParams) {
    return client.get('/analysis/period/by-spec', { params })
  },

  getMonthlyTrend(params: DateRangeParams) {
    return client.get('/analysis/period/monthly-trend', { params })
  },

  // 유형별 분석 (Type Analysis)
  getProductionShare(params: DateRangeParams) {
    return client.get('/analysis/type/production-share', { params })
  },

  getPartsComposition(params: DateRangeParams) {
    return client.get('/analysis/type/parts-composition', { params })
  },

  getByCustomer(params: DateRangeParams) {
    return client.get('/analysis/type/by-customer', { params })
  },

  // 설비별 분석 (Equipment Analysis)
  getEquipmentCapacity(params: DateRangeParams) {
    return client.get('/analysis/equipment/capacity', { params })
  },

  getStandardTimeAchievement(params: DateRangeParams) {
    return client.get('/analysis/equipment/standard-time-achievement', { params })
  },

  getEquipmentTypeShare(params: DateRangeParams) {
    return client.get('/analysis/equipment/type-share', { params })
  },

  // 규격별 분석 (Specification Analysis)
  getSpecProductionTime(params: DateRangeParams) {
    return client.get('/analysis/specification/production-time', { params })
  },

  getSpecStAchievement(params: DateRangeParams) {
    return client.get('/analysis/specification/st-achievement', { params })
  },

  getSpecDetail(params: SpecParams) {
    return client.get('/analysis/specification/detail', { params })
  },

  // 불량유형별 분석 (Defect Analysis)
  getDefectByType(params: DateRangeParams) {
    return client.get('/analysis/defect/by-type', { params })
  },

  getDefectByProduct(params: DateRangeParams) {
    return client.get('/analysis/defect/by-product', { params })
  },

  getDefectTrend(params: DateRangeParams) {
    return client.get('/analysis/defect/trend', { params })
  },
}
