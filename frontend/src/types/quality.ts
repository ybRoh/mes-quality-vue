// Common
export interface PagedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// FMEA
export interface Fmea {
  fmea_id: number
  fmea_no: string
  fmea_type: string
  product_id: string
  product_name?: string
  customer_name?: string
  status: string
  created_at: string
  updated_at: string
  item_count?: number
}

// Control Plan
export interface ControlPlan {
  cp_id: number
  cp_no: string
  cp_type: string
  product_id: string
  product_name?: string
  status: string
  created_at: string
  updated_at: string
  item_count?: number
}

// MSA
export interface MsaStudy {
  study_id: number
  study_no: string
  study_type: string
  product_id: string
  product_name?: string
  status: string
  grr_result?: any
  created_at: string
}

// PPAP
export interface Ppap {
  ppap_id: number
  ppap_no: string
  product_id: string
  product_name?: string
  customer_name?: string
  ppap_level: number
  status: string
  submission_date?: string
}

// APQP
export interface ApqpProject {
  apqp_id: number
  apqp_no: string
  project_name: string
  product_id: string
  product_name?: string
  status: string
  phase_count?: number
}

// Claim
export interface Claim {
  claim_id: number
  claim_no: string
  claim_type: string
  product_id: string
  product_name?: string
  customer_name?: string
  status: string
  severity: string
  claim_date: string
}

// Document
export interface QmsDocument {
  doc_id: number
  doc_no: string
  doc_type: string
  title: string
  revision: number
  status: string
  effective_date?: string
  author?: string
}

// Specification
export interface Specification {
  spec_mgmt_id: number
  spec_no: string
  spec_type: string
  title: string
  customer_id?: string
  revision: number
  status: string
  effective_date?: string
}

// SI FAQ
export interface SiFaq {
  faq_id: number
  customer_id?: string
  category?: string
  question: string
  answer: string
  is_active: boolean
}

// CSR
export interface Csr {
  csr_id: number
  csr_no: string
  customer_id?: string
  requirement: string
  category?: string
  compliance_status: string
  responsible?: string
  target_date?: string
}

// Audit
export interface AuditPlan {
  plan_id: number
  plan_no: string
  audit_type: string
  audit_year: number
  status: string
  lead_auditor?: string
}

export interface AuditFinding {
  finding_id: number
  finding_no: string
  finding_type: string
  description: string
  status: string
  action_count?: number
}

export interface CorrectiveAction {
  action_id: number
  action_no: string
  root_cause?: string
  status: string
  responsible?: string
  target_date?: string
}

export interface AuditRequirement {
  req_id: number
  clause_no: string
  clause_title: string
  requirement_text: string
  is_active: boolean
}

// Customer Audit
export interface CustomerAudit {
  cust_audit_id: number
  audit_no: string
  customer_id?: string
  audit_type: string
  audit_date?: string
  audit_end_date?: string
  auditor_name?: string
  result: string
  score?: number
  status: string
  finding_count?: number
}

export interface CustomerAuditFinding {
  cust_finding_id: number
  cust_audit_id: number
  finding_no: string
  finding_type: string
  description: string
  status: string
  action_count?: number
}

export interface CustomerAuditAction {
  cust_action_id: number
  cust_finding_id: number
  action_no: string
  status: string
  responsible?: string
  target_date?: string
}

// Training
export interface Training {
  training_id: number
  training_no: string
  title: string
  training_type: string
  status: string
  instructor?: string
  start_date?: string
  end_date?: string
}

export interface Qualification {
  qualification_id: number
  qualification_no: string
  employee_id: string
  employee_name?: string
  qualification_type: string
  status: string
  issue_date?: string
  expiry_date?: string
}

export interface Competency {
  matrix_id: number
  employee_id: string
  employee_name?: string
  skill_name: string
  current_level: number
  required_level: number
}

// KPI
export interface KpiDefinition {
  kpi_id: number
  kpi_no: string
  kpi_name: string
  category?: string
  unit?: string
  target_value?: number
  target_direction: string
  is_active: boolean
  latest_value?: number
  latest_status?: string
}

export interface KpiData {
  data_id: number
  kpi_id: number
  period: string
  actual_value: number
  status: string
  kpi_name?: string
}

export interface KpiDashboardItem {
  kpi_id: number
  kpi_no: string
  kpi_name: string
  category?: string
  unit?: string
  target_value?: number
  target_direction: string
  latest_value?: number
  latest_status?: string
  trend: number[]
}

// Process Monitor
export interface ProcessMonitor {
  monitor_id: number
  process_name: string
  monitor_date: string
  monitor_type: string
  auditor?: string
  result: string
  score?: number
  status: string
}

// Risk Issue
export interface RiskIssue {
  issue_id: number
  issue_no: string
  issue_type: string
  category?: string
  process_name?: string
  description: string
  severity: number
  likelihood: number
  risk_score: number
  status: string
  responsible?: string
  target_date?: string
}

// Inspection
export interface InspectionSpec {
  spec_id: number
  product_id: string
  spec_name: string
}

export interface InspectionRecord {
  record_id: number
  product_id: string
  lot_no: string
  result: string
  measured_at: string
}
