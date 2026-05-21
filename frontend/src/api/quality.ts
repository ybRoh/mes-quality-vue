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
  getList(params?: { product_id?: number; status?: string; fmea_type?: string; page?: number; size?: number }) {
    return client.get('/quality/fmea/', { params })
  },

  getById(id: number) {
    return client.get(`/quality/fmea/${id}`)
  },

  create(data: Record<string, unknown>) {
    return client.post('/quality/fmea/', data)
  },

  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/fmea/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/fmea/${id}`)
  },

  getItems(fmeaId: number) {
    return client.get(`/quality/fmea/${fmeaId}/items`)
  },

  createItem(fmeaId: number, data: Record<string, unknown>) {
    return client.post(`/quality/fmea/${fmeaId}/items`, data)
  },

  updateItem(_fmeaId: number, itemId: number, data: Record<string, unknown>) {
    return client.put(`/quality/fmea/items/${itemId}`, data)
  },

  deleteItem(_fmeaId: number, itemId: number) {
    return client.delete(`/quality/fmea/items/${itemId}`)
  },

  getRpnAnalysis(fmeaId: number) {
    return client.get(`/quality/fmea/${fmeaId}/rpn-analysis`)
  }
}

// Control Plan
export const controlPlanApi = {
  getList(params?: { product_id?: string; page?: number; size?: number }) {
    return client.get('/quality/control-plan/', { params })
  },

  getById(id: number) {
    return client.get(`/quality/control-plan/${id}`)
  },

  create(data: Record<string, unknown>) {
    return client.post('/quality/control-plan/', data)
  },

  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/control-plan/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/control-plan/${id}`)
  },

  getItems(cpId: number) {
    return client.get(`/quality/control-plan/${cpId}/items`)
  },

  createItem(cpId: number, data: Record<string, unknown>) {
    return client.post(`/quality/control-plan/${cpId}/items`, data)
  },

  updateItem(_cpId: number, itemId: number, data: Record<string, unknown>) {
    return client.put(`/quality/control-plan/items/${itemId}`, data)
  },

  deleteItem(_cpId: number, itemId: number) {
    return client.delete(`/quality/control-plan/items/${itemId}`)
  }
}

// MSA (GR&R)
export const msaApi = {
  getList(params?: { page?: number; size?: number }) {
    return client.get('/quality/msa/', { params })
  },

  getById(id: number) {
    return client.get(`/quality/msa/${id}`)
  },

  create(data: Record<string, unknown>) {
    return client.post('/quality/msa/', data)
  },

  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/msa/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/msa/${id}`)
  },

  saveMeasurements(studyId: number, data: Record<string, unknown>[]) {
    return client.post(`/quality/msa/${studyId}/measurements`, { measurements: data })
  },

  getMeasurements(studyId: number) {
    return client.get(`/quality/msa/${studyId}/measurements`)
  },

  calculate(studyId: number) {
    return client.get(`/quality/msa/${studyId}/calculate`)
  }
}

// PPAP
export const ppapApi = {
  getList(params?: { status?: string; page?: number; size?: number }) {
    return client.get('/quality/ppap/', { params })
  },

  getById(id: number) {
    return client.get(`/quality/ppap/${id}`)
  },

  create(data: Record<string, unknown>) {
    return client.post('/quality/ppap/', data)
  },

  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/ppap/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/ppap/${id}`)
  },

  getChecklist(ppapId: number) {
    return client.get(`/quality/ppap/${ppapId}/elements`)
  },

  updateChecklistItem(elementId: number, data: Record<string, unknown>) {
    return client.put(`/quality/ppap/elements/${elementId}`, data)
  }
}

// APQP
export const apqpApi = {
  getList(params?: { status?: string; page?: number; size?: number }) {
    return client.get('/quality/apqp/', { params })
  },

  getById(id: number) {
    return client.get(`/quality/apqp/${id}`)
  },

  create(data: Record<string, unknown>) {
    return client.post('/quality/apqp/', data)
  },

  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/apqp/${id}`, data)
  },

  delete(id: number) {
    return client.delete(`/quality/apqp/${id}`)
  },

  getPhases(apqpId: number) {
    return client.get(`/quality/apqp/${apqpId}/phases`)
  },

  updatePhase(phaseId: number, data: Record<string, unknown>) {
    return client.put(`/quality/apqp/phases/${phaseId}`, data)
  },

  getDeliverables(phaseId: number) {
    return client.get(`/quality/apqp/phases/${phaseId}/deliverables`)
  },

  updateDeliverable(deliverableId: number, data: Record<string, unknown>) {
    return client.put(`/quality/apqp/deliverables/${deliverableId}`, data)
  }
}

// Claim (8D)
export const claimApi = {
  getList(params?: { status?: string; customer_id?: string; product_id?: string; page?: number; size?: number }) {
    return client.get('/quality/claim/', { params })
  },

  getById(id: string) {
    return client.get(`/quality/claim/${id}`)
  },

  create(data: Record<string, unknown>) {
    return client.post('/quality/claim/', data)
  },

  update(id: string, data: Record<string, unknown>) {
    return client.put(`/quality/claim/${id}`, data)
  },

  delete(id: string) {
    return client.delete(`/quality/claim/${id}`)
  },

  updateStep(claimId: string, step: number, data: Record<string, unknown>) {
    return client.put(`/quality/claim/${claimId}/d${step}`, data)
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

// 표준문서관리
export const documentApi = {
  getList(params?: { doc_type?: string; status?: string; department?: string; keyword?: string; page?: number; size?: number }) {
    return client.get('/quality/document/', { params })
  },
  getById(id: number) {
    return client.get(`/quality/document/${id}`)
  },
  create(data: Record<string, unknown>) {
    return client.post('/quality/document/', data)
  },
  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/document/${id}`, data)
  },
  delete(id: number) {
    return client.delete(`/quality/document/${id}`)
  },
  approve(id: number) {
    return client.put(`/quality/document/${id}/approve`)
  },
  obsolete(id: number) {
    return client.put(`/quality/document/${id}/obsolete`)
  },
  getRevisions(docId: number) {
    return client.get(`/quality/document/${docId}/revisions`)
  },
  createRevision(docId: number, data: Record<string, unknown>) {
    return client.post(`/quality/document/${docId}/revisions`, data)
  },
  getAttachments(docId: number) {
    return client.get(`/quality/document/${docId}/attachments`)
  },
  uploadAttachment(docId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return client.post(`/quality/document/${docId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteAttachment(attachmentId: number) {
    return client.delete(`/quality/document/attachments/${attachmentId}`)
  },
  downloadAttachment(attachmentId: number) {
    return client.get(`/quality/document/attachments/${attachmentId}/download`, { responseType: 'blob' })
  }
}

// 내부심사관리
export const auditApi = {
  // 요구사항
  getRequirements(params?: { category?: string; is_active?: boolean; page?: number; size?: number }) {
    return client.get('/quality/audit/requirements', { params })
  },
  createRequirement(data: Record<string, unknown>) {
    return client.post('/quality/audit/requirements', data)
  },
  getRequirement(id: number) {
    return client.get(`/quality/audit/requirements/${id}`)
  },
  updateRequirement(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/audit/requirements/${id}`, data)
  },
  deleteRequirement(id: number) {
    return client.delete(`/quality/audit/requirements/${id}`)
  },
  // 심사계획
  getPlans(params?: { audit_year?: number; audit_type?: string; status?: string; page?: number; size?: number }) {
    return client.get('/quality/audit/plans', { params })
  },
  createPlan(data: Record<string, unknown>) {
    return client.post('/quality/audit/plans', data)
  },
  getPlan(id: number) {
    return client.get(`/quality/audit/plans/${id}`)
  },
  updatePlan(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/audit/plans/${id}`, data)
  },
  deletePlan(id: number) {
    return client.delete(`/quality/audit/plans/${id}`)
  },
  // 발견사항
  getPlanFindings(planId: number) {
    return client.get(`/quality/audit/plans/${planId}/findings`)
  },
  createFinding(planId: number, data: Record<string, unknown>) {
    return client.post(`/quality/audit/plans/${planId}/findings`, data)
  },
  getFindings(params?: { finding_type?: string; status?: string; page?: number; size?: number }) {
    return client.get('/quality/audit/findings', { params })
  },
  getFinding(id: number) {
    return client.get(`/quality/audit/findings/${id}`)
  },
  updateFinding(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/audit/findings/${id}`, data)
  },
  deleteFinding(id: number) {
    return client.delete(`/quality/audit/findings/${id}`)
  },
  // 시정조치
  getFindingActions(findingId: number) {
    return client.get(`/quality/audit/findings/${findingId}/actions`)
  },
  createAction(findingId: number, data: Record<string, unknown>) {
    return client.post(`/quality/audit/findings/${findingId}/actions`, data)
  },
  getActions(params?: { status?: string; overdue_only?: boolean; page?: number; size?: number }) {
    return client.get('/quality/audit/actions', { params })
  },
  getAction(id: number) {
    return client.get(`/quality/audit/actions/${id}`)
  },
  updateAction(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/audit/actions/${id}`, data)
  },
  deleteAction(id: number) {
    return client.delete(`/quality/audit/actions/${id}`)
  },
  verifyAction(id: number) {
    return client.put(`/quality/audit/actions/${id}/verify`)
  },
  // 연간 요약
  getSummary(year: number) {
    return client.get(`/quality/audit/summary/${year}`)
  }
}

// 교육/자격관리
export const trainingApi = {
  // 교육과정
  getCourses(params?: { category?: string; training_type?: string; is_active?: boolean; page?: number; size?: number }) {
    return client.get('/quality/training/courses', { params })
  },
  createCourse(data: Record<string, unknown>) {
    return client.post('/quality/training/courses', data)
  },
  getCourse(id: number) {
    return client.get(`/quality/training/courses/${id}`)
  },
  updateCourse(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/training/courses/${id}`, data)
  },
  deleteCourse(id: number) {
    return client.delete(`/quality/training/courses/${id}`)
  },
  // 교육이수
  getRecords(params?: { course_id?: number; trainee_id?: string; result?: string; page?: number; size?: number }) {
    return client.get('/quality/training/records', { params })
  },
  createRecord(data: Record<string, unknown>) {
    return client.post('/quality/training/records', data)
  },
  bulkCreateRecords(data: Record<string, unknown>) {
    return client.post('/quality/training/records/bulk', data)
  },
  updateRecord(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/training/records/${id}`, data)
  },
  deleteRecord(id: number) {
    return client.delete(`/quality/training/records/${id}`)
  },
  getDueSoon(days?: number) {
    return client.get('/quality/training/records/due-soon', { params: { days } })
  },
  // 자격
  getQualifications(params?: { qual_type?: string; holder_id?: string; status?: string; page?: number; size?: number }) {
    return client.get('/quality/training/qualifications', { params })
  },
  createQualification(data: Record<string, unknown>) {
    return client.post('/quality/training/qualifications', data)
  },
  getQualification(id: number) {
    return client.get(`/quality/training/qualifications/${id}`)
  },
  updateQualification(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/training/qualifications/${id}`, data)
  },
  deleteQualification(id: number) {
    return client.delete(`/quality/training/qualifications/${id}`)
  },
  getExpiringQualifications(days?: number) {
    return client.get('/quality/training/qualifications/expiring', { params: { days } })
  },
  // 역량매트릭스
  getCompetency(params?: { employee_id?: string; skill_name?: string; page?: number; size?: number }) {
    return client.get('/quality/training/competency', { params })
  },
  createCompetency(data: Record<string, unknown>) {
    return client.post('/quality/training/competency', data)
  },
  updateCompetency(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/training/competency/${id}`, data)
  },
  deleteCompetency(id: number) {
    return client.delete(`/quality/training/competency/${id}`)
  },
  getGapAnalysis() {
    return client.get('/quality/training/competency/gap-analysis')
  },
  // 자격심사
  getQualAudits(params?: { qual_id?: number; result?: string; page?: number; size?: number }) {
    return client.get('/quality/training/qual-audits', { params })
  },
  createQualAudit(data: Record<string, unknown>) {
    return client.post('/quality/training/qual-audits', data)
  },
  updateQualAudit(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/training/qual-audits/${id}`, data)
  },
  deleteQualAudit(id: number) {
    return client.delete(`/quality/training/qual-audits/${id}`)
  }
}

// 규격관리
export const specificationApi = {
  // 규격
  getList(params?: { spec_type?: string; customer_id?: string; status?: string; page?: number; size?: number }) {
    return client.get('/quality/specification/', { params })
  },
  getById(id: number) {
    return client.get(`/quality/specification/${id}`)
  },
  create(data: Record<string, unknown>) {
    return client.post('/quality/specification/', data)
  },
  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/specification/${id}`, data)
  },
  delete(id: number) {
    return client.delete(`/quality/specification/${id}`)
  },
  // 도면이력
  getDrawings(specId: number) {
    return client.get(`/quality/specification/${specId}/drawings`)
  },
  createDrawing(specId: number, data: Record<string, unknown>) {
    return client.post(`/quality/specification/${specId}/drawings`, data)
  },
  // SI FAQ
  getSiFaq(params?: { customer_id?: string; category?: string; is_active?: boolean; page?: number; size?: number }) {
    return client.get('/quality/specification/si-faq', { params })
  },
  createSiFaq(data: Record<string, unknown>) {
    return client.post('/quality/specification/si-faq', data)
  },
  updateSiFaq(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/specification/si-faq/${id}`, data)
  },
  deleteSiFaq(id: number) {
    return client.delete(`/quality/specification/si-faq/${id}`)
  },
  // CSR
  getCsr(params?: { customer_id?: string; compliance_status?: string; category?: string; page?: number; size?: number }) {
    return client.get('/quality/specification/csr', { params })
  },
  getCsrById(id: number) {
    return client.get(`/quality/specification/csr/${id}`)
  },
  createCsr(data: Record<string, unknown>) {
    return client.post('/quality/specification/csr', data)
  },
  updateCsr(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/specification/csr/${id}`, data)
  },
  deleteCsr(id: number) {
    return client.delete(`/quality/specification/csr/${id}`)
  }
}

// 고객심사관리
export const customerAuditApi = {
  // 심사
  getList(params?: { customer_id?: string; audit_type?: string; status?: string; result?: string; page?: number; size?: number }) {
    return client.get('/quality/customer-audit/', { params })
  },
  getById(id: number) {
    return client.get(`/quality/customer-audit/${id}`)
  },
  create(data: Record<string, unknown>) {
    return client.post('/quality/customer-audit/', data)
  },
  update(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/customer-audit/${id}`, data)
  },
  delete(id: number) {
    return client.delete(`/quality/customer-audit/${id}`)
  },
  // 발견사항
  getAuditFindings(auditId: number) {
    return client.get(`/quality/customer-audit/${auditId}/findings`)
  },
  createFinding(auditId: number, data: Record<string, unknown>) {
    return client.post(`/quality/customer-audit/${auditId}/findings`, data)
  },
  getFindings(params?: { finding_type?: string; status?: string; page?: number; size?: number }) {
    return client.get('/quality/customer-audit/findings', { params })
  },
  getFinding(id: number) {
    return client.get(`/quality/customer-audit/findings/${id}`)
  },
  updateFinding(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/customer-audit/findings/${id}`, data)
  },
  deleteFinding(id: number) {
    return client.delete(`/quality/customer-audit/findings/${id}`)
  },
  // 시정조치
  getFindingActions(findingId: number) {
    return client.get(`/quality/customer-audit/findings/${findingId}/actions`)
  },
  createAction(findingId: number, data: Record<string, unknown>) {
    return client.post(`/quality/customer-audit/findings/${findingId}/actions`, data)
  },
  getActions(params?: { status?: string; overdue_only?: boolean; page?: number; size?: number }) {
    return client.get('/quality/customer-audit/actions', { params })
  },
  getAction(id: number) {
    return client.get(`/quality/customer-audit/actions/${id}`)
  },
  updateAction(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/customer-audit/actions/${id}`, data)
  },
  deleteAction(id: number) {
    return client.delete(`/quality/customer-audit/actions/${id}`)
  },
  verifyAction(id: number) {
    return client.put(`/quality/customer-audit/actions/${id}/verify`)
  },
  // 연간 요약
  getSummary(year: number) {
    return client.get(`/quality/customer-audit/summary/${year}`)
  }
}

// 성과지표관리
export const kpiApi = {
  // KPI 정의
  getDefinitions(params?: { category?: string; is_active?: boolean; page?: number; size?: number }) {
    return client.get('/quality/kpi/definitions', { params })
  },
  getDefinition(id: number) {
    return client.get(`/quality/kpi/definitions/${id}`)
  },
  createDefinition(data: Record<string, unknown>) {
    return client.post('/quality/kpi/definitions', data)
  },
  updateDefinition(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/kpi/definitions/${id}`, data)
  },
  deleteDefinition(id: number) {
    return client.delete(`/quality/kpi/definitions/${id}`)
  },
  // KPI 데이터
  getData(kpiId: number) {
    return client.get(`/quality/kpi/definitions/${kpiId}/data`)
  },
  addData(kpiId: number, data: Record<string, unknown>) {
    return client.post(`/quality/kpi/definitions/${kpiId}/data`, data)
  },
  // 대시보드
  getDashboard() {
    return client.get('/quality/kpi/dashboard')
  },
  // 공정 모니터링
  getMonitors(params?: { process_name?: string; monitor_type?: string; result?: string; status?: string; page?: number; size?: number }) {
    return client.get('/quality/kpi/monitors', { params })
  },
  getMonitor(id: number) {
    return client.get(`/quality/kpi/monitors/${id}`)
  },
  createMonitor(data: Record<string, unknown>) {
    return client.post('/quality/kpi/monitors', data)
  },
  updateMonitor(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/kpi/monitors/${id}`, data)
  },
  deleteMonitor(id: number) {
    return client.delete(`/quality/kpi/monitors/${id}`)
  },
  // 리스크/이슈
  getRisks(params?: { issue_type?: string; status?: string; category?: string; page?: number; size?: number }) {
    return client.get('/quality/kpi/risks', { params })
  },
  getRisk(id: number) {
    return client.get(`/quality/kpi/risks/${id}`)
  },
  createRisk(data: Record<string, unknown>) {
    return client.post('/quality/kpi/risks', data)
  },
  updateRisk(id: number, data: Record<string, unknown>) {
    return client.put(`/quality/kpi/risks/${id}`, data)
  },
  deleteRisk(id: number) {
    return client.delete(`/quality/kpi/risks/${id}`)
  },
  getRiskMatrix() {
    return client.get('/quality/kpi/risks/matrix')
  }
}
