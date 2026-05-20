type TagType = '' | 'success' | 'warning' | 'danger' | 'info'

interface StatusMapping {
  label: string
  tag: TagType
}

const auditStatusMap: Record<string, StatusMapping> = {
  SCHEDULED: { label: '예정', tag: 'info' },
  IN_PROGRESS: { label: '진행중', tag: 'warning' },
  COMPLETED: { label: '완료', tag: 'success' },
  CLOSED: { label: '종결', tag: '' },
}

const findingTypeMap: Record<string, StatusMapping> = {
  MAJOR_NC: { label: '중부적합', tag: 'danger' },
  MINOR_NC: { label: '경부적합', tag: 'warning' },
  OBSERVATION: { label: '관찰사항', tag: 'info' },
  OFI: { label: '개선기회', tag: '' },
}

const findingStatusMap: Record<string, StatusMapping> = {
  OPEN: { label: '미결', tag: 'danger' },
  ACTION_REQUIRED: { label: '조치필요', tag: 'warning' },
  CLOSED: { label: '종결', tag: 'success' },
  VERIFIED: { label: '검증완료', tag: '' },
}

const actionStatusMap: Record<string, StatusMapping> = {
  OPEN: { label: '미결', tag: 'danger' },
  IN_PROGRESS: { label: '진행중', tag: 'warning' },
  COMPLETED: { label: '완료', tag: 'success' },
  VERIFIED: { label: '검증완료', tag: '' },
}

const complianceMap: Record<string, StatusMapping> = {
  COMPLIANT: { label: '준수', tag: 'success' },
  PENDING: { label: '대기', tag: 'warning' },
  NON_COMPLIANT: { label: '미준수', tag: 'danger' },
  NA: { label: '해당없음', tag: 'info' },
}

const auditResultMap: Record<string, StatusMapping> = {
  PASS: { label: '합격', tag: 'success' },
  CONDITIONAL: { label: '조건부', tag: 'warning' },
  FAIL: { label: '불합격', tag: 'danger' },
  PENDING: { label: '대기', tag: 'info' },
}

const auditTypeMap: Record<string, StatusMapping> = {
  SQ: { label: 'SQ', tag: '' },
  PROCESS: { label: '공정심사', tag: 'warning' },
  PRODUCT: { label: '제품심사', tag: 'success' },
  SYSTEM: { label: '시스템심사', tag: 'info' },
}

const docStatusMap: Record<string, StatusMapping> = {
  DRAFT: { label: '초안', tag: 'info' },
  IN_REVIEW: { label: '검토중', tag: 'warning' },
  APPROVED: { label: '승인', tag: 'success' },
  SUPERSEDED: { label: '대체됨', tag: '' },
  OBSOLETE: { label: '폐기', tag: 'danger' },
}

const specStatusMap: Record<string, StatusMapping> = {
  ACTIVE: { label: '유효', tag: 'success' },
  SUPERSEDED: { label: '대체됨', tag: 'warning' },
  OBSOLETE: { label: '폐기', tag: 'danger' },
}

const riskStatusMap: Record<string, StatusMapping> = {
  IDENTIFIED: { label: '식별됨', tag: 'info' },
  MITIGATING: { label: '대응중', tag: 'warning' },
  RESOLVED: { label: '해결', tag: 'success' },
  ACCEPTED: { label: '수용', tag: '' },
}

const issueTypeMap: Record<string, StatusMapping> = {
  RISK: { label: '리스크', tag: 'danger' },
  OPPORTUNITY: { label: '기회', tag: 'success' },
  ISSUE: { label: '이슈', tag: 'warning' },
}

const monitorResultMap: Record<string, StatusMapping> = {
  OK: { label: '적합', tag: 'success' },
  NG: { label: '부적합', tag: 'danger' },
  NA: { label: '해당없음', tag: 'info' },
}

const kpiStatusMap: Record<string, StatusMapping> = {
  GREEN: { label: 'GREEN', tag: 'success' },
  YELLOW: { label: 'YELLOW', tag: 'warning' },
  RED: { label: 'RED', tag: 'danger' },
}

const trainingStatusMap: Record<string, StatusMapping> = {
  PLANNED: { label: '예정', tag: 'info' },
  IN_PROGRESS: { label: '진행중', tag: 'warning' },
  COMPLETED: { label: '완료', tag: 'success' },
  CANCELLED: { label: '취소', tag: 'danger' },
}

const qualStatusMap: Record<string, StatusMapping> = {
  ACTIVE: { label: '유효', tag: 'success' },
  EXPIRED: { label: '만료', tag: 'danger' },
  SUSPENDED: { label: '정지', tag: 'warning' },
  REVOKED: { label: '취소', tag: 'danger' },
}

const fmeaStatusMap: Record<string, StatusMapping> = {
  DRAFT: { label: '초안', tag: 'info' },
  IN_REVIEW: { label: '검토중', tag: 'warning' },
  APPROVED: { label: '승인', tag: 'success' },
  CLOSED: { label: '종결', tag: '' },
}

// Exported maps for direct access
export const statusMaps = {
  audit: auditStatusMap,
  findingType: findingTypeMap,
  findingStatus: findingStatusMap,
  actionStatus: actionStatusMap,
  compliance: complianceMap,
  auditResult: auditResultMap,
  auditType: auditTypeMap,
  docStatus: docStatusMap,
  specStatus: specStatusMap,
  riskStatus: riskStatusMap,
  issueType: issueTypeMap,
  monitorResult: monitorResultMap,
  kpiStatus: kpiStatusMap,
  trainingStatus: trainingStatusMap,
  qualStatus: qualStatusMap,
  fmeaStatus: fmeaStatusMap,
}

// Generic helpers
export function getLabel(map: Record<string, StatusMapping>, value: string | null | undefined): string {
  if (!value) return '-'
  return map[value]?.label ?? value
}

export function getTagType(map: Record<string, StatusMapping>, value: string | null | undefined): TagType {
  if (!value) return 'info'
  return map[value]?.tag ?? 'info'
}
