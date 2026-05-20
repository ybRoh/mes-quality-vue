import client from './client'

// SPC
export const spcApi = {
  getProducts() {
    return client.get('/quality/spc/products')
  },

  getSpecs(productId: number) {
    return client.get(`/quality/spc/specs/${productId}`)
  },

  getData(params: { spec_id: number; sample_count?: number; start_date?: string; end_date?: string }) {
    return client.get('/quality/spc/data', { params })
  },

  getCapability(specId: number, sampleCount?: number) {
    return client.get(`/quality/spc/capability/${specId}`, { params: { sample_count: sampleCount } })
  }
}

// FMEA
export const fmeaApi = {
  getList(params?: { product_id?: number; status?: string; page?: number; page_size?: number }) {
    return client.get('/quality/fmea', { params })
  },

  getById(id: number) {
    return client.get(`/quality/fmea/${id}`)
  },

  create(data: any) {
    return client.post('/quality/fmea', data)
  },

  update(id: number, data: any) {
    return client.put(`/quality/fmea/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/fmea/${id}`)
  },

  getItems(fmeaId: number) {
    return client.get(`/quality/fmea/${fmeaId}/items`)
  },

  createItem(fmeaId: number, data: any) {
    return client.post(`/quality/fmea/${fmeaId}/items`, data)
  },

  updateItem(fmeaId: number, itemId: number, data: any) {
    return client.put(`/quality/fmea/${fmeaId}/items/${itemId}`, data)
  },

  deleteItem(fmeaId: number, itemId: number) {
    return client.delete(`/quality/fmea/${fmeaId}/items/${itemId}`)
  },

  getRpnAnalysis(fmeaId: number) {
    return client.get(`/quality/fmea/${fmeaId}/rpn-analysis`)
  }
}

// Control Plan
export const controlPlanApi = {
  getList(params?: { product_id?: number; page?: number; page_size?: number }) {
    return client.get('/quality/control-plan', { params })
  },

  getById(id: number) {
    return client.get(`/quality/control-plan/${id}`)
  },

  create(data: any) {
    return client.post('/quality/control-plan', data)
  },

  update(id: number, data: any) {
    return client.put(`/quality/control-plan/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/control-plan/${id}`)
  },

  getItems(cpId: number) {
    return client.get(`/quality/control-plan/${cpId}/items`)
  },

  createItem(cpId: number, data: any) {
    return client.post(`/quality/control-plan/${cpId}/items`, data)
  },

  updateItem(cpId: number, itemId: number, data: any) {
    return client.put(`/quality/control-plan/${cpId}/items/${itemId}`, data)
  },

  deleteItem(cpId: number, itemId: number) {
    return client.delete(`/quality/control-plan/${cpId}/items/${itemId}`)
  }
}

// MSA (GR&R)
export const msaApi = {
  getList(params?: { page?: number; page_size?: number }) {
    return client.get('/quality/msa', { params })
  },

  getById(id: number) {
    return client.get(`/quality/msa/${id}`)
  },

  create(data: any) {
    return client.post('/quality/msa', data)
  },

  update(id: number, data: any) {
    return client.put(`/quality/msa/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/msa/${id}`)
  },

  saveMeasurements(studyId: number, data: any[]) {
    return client.post(`/quality/msa/${studyId}/measurements`, data)
  },

  getMeasurements(studyId: number) {
    return client.get(`/quality/msa/${studyId}/measurements`)
  },

  calculate(studyId: number) {
    return client.post(`/quality/msa/${studyId}/calculate`)
  },

  getResults(studyId: number) {
    return client.get(`/quality/msa/${studyId}/results`)
  }
}

// PPAP
export const ppapApi = {
  getList(params?: { status?: string; page?: number; page_size?: number }) {
    return client.get('/quality/ppap', { params })
  },

  getById(id: number) {
    return client.get(`/quality/ppap/${id}`)
  },

  create(data: any) {
    return client.post('/quality/ppap', data)
  },

  update(id: number, data: any) {
    return client.put(`/quality/ppap/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/ppap/${id}`)
  },

  getChecklist(ppapId: number) {
    return client.get(`/quality/ppap/${ppapId}/checklist`)
  },

  updateChecklistItem(ppapId: number, elementNo: number, data: any) {
    return client.put(`/quality/ppap/${ppapId}/checklist/${elementNo}`, data)
  }
}

// APQP
export const apqpApi = {
  getList(params?: { status?: string; page?: number; page_size?: number }) {
    return client.get('/quality/apqp', { params })
  },

  getById(id: number) {
    return client.get(`/quality/apqp/${id}`)
  },

  create(data: any) {
    return client.post('/quality/apqp', data)
  },

  update(id: number, data: any) {
    return client.put(`/quality/apqp/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/apqp/${id}`)
  },

  getPhases(apqpId: number) {
    return client.get(`/quality/apqp/${apqpId}/phases`)
  },

  updatePhase(apqpId: number, phaseId: number, data: any) {
    return client.put(`/quality/apqp/${apqpId}/phases/${phaseId}`, data)
  },

  getDeliverables(apqpId: number, phaseNumber: number) {
    return client.get(`/quality/apqp/${apqpId}/phases/${phaseNumber}/deliverables`)
  },

  updateDeliverable(apqpId: number, deliverableId: number, data: any) {
    return client.put(`/quality/apqp/${apqpId}/deliverables/${deliverableId}`, data)
  }
}

// Claim (8D)
export const claimApi = {
  getList(params?: { status?: string; customer_id?: string; product_id?: string; page?: number; size?: number }) {
    return client.get('/quality/claim', { params })
  },

  getById(id: number) {
    return client.get(`/quality/claim/${id}`)
  },

  create(data: any) {
    return client.post('/quality/claim', data)
  },

  update(id: number, data: any) {
    return client.put(`/quality/claim/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/claim/${id}`)
  },

  updateStep(claimId: number, step: number, data: any) {
    return client.put(`/quality/claim/${claimId}/step/${step}`, data)
  }
}

// Inspection
export const inspectionApi = {
  getList(params?: {
    product_id?: string
    lot_no?: string
    insp_stage?: string
    result?: string
    page?: number
    size?: number
  }) {
    return client.get('/quality/inspection/records', { params })
  },

  getById(id: number) {
    return client.get(`/quality/inspection/records/${id}`)
  },

  getMeasurements(inspectionId: number) {
    return client.get(`/quality/inspection/records/${inspectionId}`)
  }
}
