"""
IATF 16949 QMS 신규 테이블 정의
- QmsBase 사용 (create_all 안전)
- FMEA, Control Plan, MSA, PPAP, APQP 모듈
- 표준문서관리, 내부심사관리, 교육/자격관리 모듈
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, DateTime,
    ForeignKey, UniqueConstraint, Boolean,
)
from sqlalchemy.orm import relationship
from models.base import QmsBase


def _utcnow():
    return datetime.now(timezone.utc)


# ============================================================
# FMEA (고장모드 영향분석)
# ============================================================

class QmsFmea(QmsBase):
    """FMEA 헤더"""
    __tablename__ = "qms_fmea"

    fmea_id = Column(Integer, primary_key=True, autoincrement=True)
    fmea_no = Column(String(50), unique=True, nullable=False)
    product_id = Column(String(50), nullable=False, index=True)  # product 테이블 참조
    fmea_type = Column(String(20), default="PROCESS")        # PROCESS / DESIGN
    revision = Column(Integer, default=1)
    status = Column(String(20), default="DRAFT")             # DRAFT/IN_REVIEW/APPROVED/CLOSED
    prepared_by = Column(String(50))
    approved_by = Column(String(50))
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    items = relationship("QmsFmeaItem", back_populates="fmea", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsFmea(fmea_id={self.fmea_id}, fmea_no='{self.fmea_no}')>"


class QmsFmeaItem(QmsBase):
    """FMEA 항목 (고장모드별 분석)"""
    __tablename__ = "qms_fmea_item"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    fmea_id = Column(Integer, ForeignKey("qms_fmea.fmea_id"), nullable=False, index=True)
    process_step = Column(String(100))                       # 공정단계
    function_requirement = Column(Text)                      # 기능/요구사항
    failure_mode = Column(Text, nullable=False)              # 고장모드
    failure_effect = Column(Text)                            # 고장영향
    severity = Column(Integer, default=1)                    # 심각도 (1-10)
    failure_cause = Column(Text)                             # 고장원인
    occurrence = Column(Integer, default=1)                  # 발생도 (1-10)
    current_control_prevent = Column(Text)                   # 현재 관리방법 (예방)
    current_control_detect = Column(Text)                    # 현재 관리방법 (검출)
    detection = Column(Integer, default=1)                   # 검출도 (1-10)
    rpn = Column(Integer)                                    # RPN = S x O x D
    ap = Column(String(1))                                   # 조치우선순위 H/M/L
    recommended_action = Column(Text)                        # 권고 조치
    responsible = Column(String(50))                         # 담당자
    target_date = Column(Date)                               # 목표일
    action_taken = Column(Text)                              # 실시 조치
    new_severity = Column(Integer)                           # 개선 후 심각도
    new_occurrence = Column(Integer)                         # 개선 후 발생도
    new_detection = Column(Integer)                          # 개선 후 검출도
    new_rpn = Column(Integer)                                # 개선 후 RPN

    fmea = relationship("QmsFmea", back_populates="items")

    def __repr__(self):
        return f"<QmsFmeaItem(item_id={self.item_id}, failure_mode='{self.failure_mode}')>"


# ============================================================
# Control Plan (관리계획서)
# ============================================================

class QmsControlPlan(QmsBase):
    """Control Plan 헤더"""
    __tablename__ = "qms_control_plan"

    cp_id = Column(Integer, primary_key=True, autoincrement=True)
    cp_no = Column(String(50), unique=True, nullable=False)
    product_id = Column(String(50), nullable=False, index=True)
    fmea_id = Column(Integer, index=True)                     # FMEA 연계
    cp_type = Column(String(20), default="PRODUCTION")        # PROTOTYPE/PRE_LAUNCH/PRODUCTION
    revision = Column(Integer, default=1)
    status = Column(String(20), default="DRAFT")
    prepared_by = Column(String(50))
    approved_by = Column(String(50))
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    items = relationship("QmsControlPlanItem", back_populates="control_plan", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsControlPlan(cp_id={self.cp_id}, cp_no='{self.cp_no}')>"


class QmsControlPlanItem(QmsBase):
    """Control Plan 항목"""
    __tablename__ = "qms_control_plan_item"

    cp_item_id = Column(Integer, primary_key=True, autoincrement=True)
    cp_id = Column(Integer, ForeignKey("qms_control_plan.cp_id"), nullable=False, index=True)
    process_no = Column(String(20))                           # 공정번호
    process_name = Column(String(100))                        # 공정명
    machine_id = Column(String(50))                           # 설비 ID
    characteristic_name = Column(String(100))                 # 특성명
    characteristic_class = Column(String(10))                 # CTQ/MAJOR/MINOR
    spec_id = Column(Integer)                                 # inspection_spec FK
    evaluation_method = Column(String(100))                   # 평가방법
    sample_size = Column(String(50))                          # 시료 크기
    sample_frequency = Column(String(50))                     # 시료 빈도
    control_method = Column(String(100))                      # 관리방법
    reaction_plan = Column(Text)                              # 대응계획

    control_plan = relationship("QmsControlPlan", back_populates="items")

    def __repr__(self):
        return f"<QmsControlPlanItem(cp_item_id={self.cp_item_id}, process_no='{self.process_no}')>"


# ============================================================
# MSA (측정시스템분석)
# ============================================================

class QmsMsaStudy(QmsBase):
    """MSA 연구 헤더"""
    __tablename__ = "qms_msa_study"

    msa_id = Column(Integer, primary_key=True, autoincrement=True)
    msa_no = Column(String(50), unique=True, nullable=False)
    product_id = Column(String(50), nullable=False, index=True)
    spec_id = Column(Integer)                                 # inspection_spec FK
    study_type = Column(String(20), default="GRR")            # GRR/BIAS/LINEARITY
    gage_name = Column(String(100))                           # 측정기 이름
    gage_id = Column(String(50))                              # 측정기 ID
    num_operators = Column(Integer, default=3)                # 작업자 수
    num_parts = Column(Integer, default=10)                   # 부품 수
    num_trials = Column(Integer, default=3)                   # 반복 횟수
    tolerance = Column(Float)                                 # 공차 (USL - LSL)
    result_grr_pct = Column(Float)                            # %GR&R 결과
    result_ndc = Column(Integer)                              # ndc 결과
    judgment = Column(String(20))                             # ACCEPTABLE/MARGINAL/UNACCEPTABLE
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    measurements = relationship("QmsMsaMeasurement", back_populates="msa_study", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsMsaStudy(msa_id={self.msa_id}, msa_no='{self.msa_no}')>"


class QmsMsaMeasurement(QmsBase):
    """MSA 측정 데이터"""
    __tablename__ = "qms_msa_measurement"

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    msa_id = Column(Integer, ForeignKey("qms_msa_study.msa_id"), nullable=False, index=True)
    operator_name = Column(String(50), nullable=False)        # 작업자명
    part_no = Column(Integer, nullable=False)                 # 부품 번호
    trial_no = Column(Integer, nullable=False)                # 시행 번호
    measured_value = Column(Float, nullable=False)            # 측정값

    msa_study = relationship("QmsMsaStudy", back_populates="measurements")

    __table_args__ = (
        UniqueConstraint("msa_id", "operator_name", "part_no", "trial_no"),
    )

    def __repr__(self):
        return f"<QmsMsaMeasurement(measurement_id={self.measurement_id}, msa_id={self.msa_id})>"


# ============================================================
# PPAP (생산부품승인절차)
# ============================================================

class QmsPpap(QmsBase):
    """PPAP 헤더"""
    __tablename__ = "qms_ppap"

    ppap_id = Column(Integer, primary_key=True, autoincrement=True)
    ppap_no = Column(String(50), unique=True, nullable=False)
    product_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), index=True)
    submission_level = Column(Integer, default=3)             # 제출 레벨 (1-5)
    reason = Column(Text)                                     # 제출 사유
    status = Column(String(20), default="PLANNING")           # PLANNING/IN_PROGRESS/SUBMITTED/APPROVED/REJECTED
    fmea_id = Column(Integer)                                 # FMEA 연계
    cp_id = Column(Integer)                                   # Control Plan 연계
    msa_id = Column(Integer)                                  # MSA 연계
    apqp_id = Column(Integer)                                 # APQP 연계
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    elements = relationship("QmsPpapElement", back_populates="ppap", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsPpap(ppap_id={self.ppap_id}, ppap_no='{self.ppap_no}')>"


class QmsPpapElement(QmsBase):
    """PPAP 18개 요소"""
    __tablename__ = "qms_ppap_element"

    element_id = Column(Integer, primary_key=True, autoincrement=True)
    ppap_id = Column(Integer, ForeignKey("qms_ppap.ppap_id"), nullable=False, index=True)
    element_no = Column(Integer, nullable=False)              # 1-18
    element_name = Column(String(200), nullable=False)        # 요소명
    is_required = Column(Integer, default=1)                  # 필수 여부
    status = Column(String(20), default="NOT_STARTED")        # NOT_STARTED/IN_PROGRESS/COMPLETED
    document_ref = Column(Text)                               # 문서 참조

    ppap = relationship("QmsPpap", back_populates="elements")

    def __repr__(self):
        return f"<QmsPpapElement(element_id={self.element_id}, element_no={self.element_no})>"


# ============================================================
# APQP (사전품질계획)
# ============================================================

class QmsApqpProject(QmsBase):
    """APQP 프로젝트"""
    __tablename__ = "qms_apqp_project"

    apqp_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(50), index=True)
    project_name = Column(String(200), nullable=False)
    project_no = Column(String(50), unique=True)
    current_phase = Column(Integer, default=1)                # 현재 단계 (1-5)
    sop_date = Column(Date)                                   # 양산 시작일
    team_leader = Column(String(50))
    status = Column(String(20), default="NOT_STARTED")        # NOT_STARTED/IN_PROGRESS/COMPLETED/ON_HOLD
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    phases = relationship("QmsApqpPhase", back_populates="project", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsApqpProject(apqp_id={self.apqp_id}, project_name='{self.project_name}')>"


class QmsApqpPhase(QmsBase):
    """APQP 단계 (5단계)"""
    __tablename__ = "qms_apqp_phase"

    phase_id = Column(Integer, primary_key=True, autoincrement=True)
    apqp_id = Column(Integer, ForeignKey("qms_apqp_project.apqp_id"), nullable=False, index=True)
    phase_no = Column(Integer, nullable=False)                # 1-5
    phase_name = Column(String(100), nullable=False)
    plan_start = Column(Date)                                 # 계획 시작일
    plan_end = Column(Date)                                   # 계획 종료일
    actual_start = Column(Date)                               # 실제 시작일
    actual_end = Column(Date)                                 # 실제 종료일
    status = Column(String(20), default="NOT_STARTED")
    gate_review = Column(Text)                                # 게이트 리뷰 결과

    project = relationship("QmsApqpProject", back_populates="phases")
    deliverables = relationship("QmsApqpDeliverable", back_populates="phase", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsApqpPhase(phase_id={self.phase_id}, phase_no={self.phase_no})>"


class QmsApqpDeliverable(QmsBase):
    """APQP 산출물"""
    __tablename__ = "qms_apqp_deliverable"

    deliverable_id = Column(Integer, primary_key=True, autoincrement=True)
    phase_id = Column(Integer, ForeignKey("qms_apqp_phase.phase_id"), nullable=False, index=True)
    item_name = Column(String(200), nullable=False)           # 산출물명
    responsible = Column(String(50))                          # 담당자
    due_date = Column(Date)                                   # 기한
    status = Column(String(20), default="NOT_STARTED")
    completion_date = Column(Date)                            # 완료일

    phase = relationship("QmsApqpPhase", back_populates="deliverables")

    def __repr__(self):
        return f"<QmsApqpDeliverable(deliverable_id={self.deliverable_id}, item_name='{self.item_name}')>"


# ============================================================
# 표준문서관리
# ============================================================

class QmsDocument(QmsBase):
    """표준문서 헤더"""
    __tablename__ = "qms_document"

    doc_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_no = Column(String(50), unique=True, nullable=False)
    doc_type = Column(String(20), nullable=False)  # MANUAL/PROCESS/REGULATION/GUIDELINE/FORM
    title = Column(String(300), nullable=False)
    department = Column(String(100))
    revision = Column(Integer, default=1)
    status = Column(String(20), default="DRAFT")  # DRAFT/REVIEW/APPROVED/OBSOLETE
    prepared_by = Column(String(50))
    reviewed_by = Column(String(50))
    approved_by = Column(String(50))
    effective_date = Column(Date)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    revisions = relationship("QmsDocumentRevision", back_populates="document", cascade="all, delete-orphan", passive_deletes=True)
    attachments = relationship("QmsDocumentAttachment", back_populates="document", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsDocument(doc_id={self.doc_id}, doc_no='{self.doc_no}')>"


class QmsDocumentRevision(QmsBase):
    """문서 개정 이력"""
    __tablename__ = "qms_document_revision"

    revision_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("qms_document.doc_id"), nullable=False, index=True)
    revision_no = Column(Integer, nullable=False)
    change_summary = Column(Text)
    changed_by = Column(String(50))
    previous_status = Column(String(20))
    new_status = Column(String(20))
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("QmsDocument", back_populates="revisions")

    def __repr__(self):
        return f"<QmsDocumentRevision(revision_id={self.revision_id}, doc_id={self.doc_id})>"


class QmsDocumentAttachment(QmsBase):
    """문서 첨부파일"""
    __tablename__ = "qms_document_attachment"

    attachment_id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(Integer, ForeignKey("qms_document.doc_id"), nullable=False, index=True)
    file_name = Column(String(300), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_by = Column(String(50))
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("QmsDocument", back_populates="attachments")

    def __repr__(self):
        return f"<QmsDocumentAttachment(attachment_id={self.attachment_id}, file_name='{self.file_name}')>"


# ============================================================
# 내부심사관리
# ============================================================

class QmsAuditRequirement(QmsBase):
    """SQ 요구사항"""
    __tablename__ = "qms_audit_requirement"

    req_id = Column(Integer, primary_key=True, autoincrement=True)
    req_no = Column(String(50), unique=True, nullable=False)
    clause_ref = Column(String(50))  # IATF 조항 번호
    category = Column(String(100))
    description = Column(Text, nullable=False)
    audit_criteria = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self):
        return f"<QmsAuditRequirement(req_id={self.req_id}, req_no='{self.req_no}')>"


class QmsAuditPlan(QmsBase):
    """심사 계획"""
    __tablename__ = "qms_audit_plan"

    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_no = Column(String(50), unique=True, nullable=False)
    audit_year = Column(Integer, nullable=False)
    audit_type = Column(String(20), default="INTERNAL")  # INTERNAL/SUPPLIER/PROCESS
    title = Column(String(300), nullable=False)
    scope = Column(Text)
    department = Column(String(100))
    lead_auditor = Column(String(50))
    plan_start = Column(Date)
    plan_end = Column(Date)
    actual_start = Column(Date)
    actual_end = Column(Date)
    status = Column(String(20), default="PLANNED")  # PLANNED/IN_PROGRESS/COMPLETED/CANCELLED
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    findings = relationship("QmsAuditFinding", back_populates="plan", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsAuditPlan(plan_id={self.plan_id}, plan_no='{self.plan_no}')>"


class QmsAuditFinding(QmsBase):
    """부적합/관찰"""
    __tablename__ = "qms_audit_finding"

    finding_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("qms_audit_plan.plan_id"), nullable=False, index=True)
    finding_no = Column(String(50), unique=True, nullable=False)
    finding_type = Column(String(20), nullable=False)  # MAJOR_NC/MINOR_NC/OBSERVATION/OFI
    clause_ref = Column(String(50))
    description = Column(Text, nullable=False)
    evidence = Column(Text)
    status = Column(String(20), default="OPEN")  # OPEN/ACTION_REQUIRED/CLOSED/VERIFIED
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    plan = relationship("QmsAuditPlan", back_populates="findings")
    actions = relationship("QmsCorrectiveAction", back_populates="finding", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsAuditFinding(finding_id={self.finding_id}, finding_no='{self.finding_no}')>"


class QmsCorrectiveAction(QmsBase):
    """시정조치"""
    __tablename__ = "qms_corrective_action"

    action_id = Column(Integer, primary_key=True, autoincrement=True)
    finding_id = Column(Integer, ForeignKey("qms_audit_finding.finding_id"), nullable=False, index=True)
    action_no = Column(String(50), unique=True, nullable=False)
    root_cause = Column(Text)
    containment_action = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    responsible = Column(String(50))
    target_date = Column(Date)
    completion_date = Column(Date)
    status = Column(String(20), default="OPEN")  # OPEN/IN_PROGRESS/COMPLETED/VERIFIED
    verified_by = Column(String(50))
    verified_date = Column(Date)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    finding = relationship("QmsAuditFinding", back_populates="actions")

    def __repr__(self):
        return f"<QmsCorrectiveAction(action_id={self.action_id}, action_no='{self.action_no}')>"


# ============================================================
# 교육/자격관리
# ============================================================

class QmsTrainingCourse(QmsBase):
    """교육과정 마스터"""
    __tablename__ = "qms_training_course"

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    course_no = Column(String(50), unique=True, nullable=False)
    course_name = Column(String(300), nullable=False)
    category = Column(String(100))
    duration_hours = Column(Float)
    training_type = Column(String(20), default="INTERNAL")  # INTERNAL/EXTERNAL/OJT/ONLINE
    recurrence_months = Column(Integer)  # 재교육 주기 (개월)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    records = relationship("QmsTrainingRecord", back_populates="course", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsTrainingCourse(course_id={self.course_id}, course_no='{self.course_no}')>"


class QmsTrainingRecord(QmsBase):
    """교육이수 기록"""
    __tablename__ = "qms_training_record"

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("qms_training_course.course_id"), nullable=False, index=True)
    trainee_id = Column(String(50), nullable=False)
    training_date = Column(Date, nullable=False)
    score = Column(Float)
    result = Column(String(20), default="PENDING")  # PENDING/PASS/FAIL
    next_due_date = Column(Date)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    course = relationship("QmsTrainingCourse", back_populates="records")

    __table_args__ = (
        UniqueConstraint("course_id", "trainee_id", "training_date"),
    )

    def __repr__(self):
        return f"<QmsTrainingRecord(record_id={self.record_id}, trainee_id='{self.trainee_id}')>"


class QmsQualification(QmsBase):
    """자격/인증"""
    __tablename__ = "qms_qualification"

    qual_id = Column(Integer, primary_key=True, autoincrement=True)
    qual_type = Column(String(50), nullable=False)
    qual_name = Column(String(200), nullable=False)
    holder_id = Column(String(50), nullable=False)
    issuing_body = Column(String(200))
    certificate_no = Column(String(100))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    status = Column(String(20), default="ACTIVE")  # ACTIVE/EXPIRED/SUSPENDED
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    audits = relationship("QmsQualAudit", back_populates="qualification", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsQualification(qual_id={self.qual_id}, qual_name='{self.qual_name}')>"


class QmsCompetencyMatrix(QmsBase):
    """역량 매트릭스"""
    __tablename__ = "qms_competency_matrix"

    matrix_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), nullable=False)
    skill_name = Column(String(200), nullable=False)
    required_level = Column(Integer, default=1)  # 1-5
    current_level = Column(Integer, default=0)   # 0-5
    gap = Column(Integer)  # required_level - current_level
    evaluation_date = Column(Date)
    evaluator = Column(String(50))
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        UniqueConstraint("employee_id", "skill_name"),
    )

    def __repr__(self):
        return f"<QmsCompetencyMatrix(matrix_id={self.matrix_id}, employee_id='{self.employee_id}')>"


class QmsQualAudit(QmsBase):
    """자격심사 기록"""
    __tablename__ = "qms_qual_audit"

    qual_audit_id = Column(Integer, primary_key=True, autoincrement=True)
    qual_id = Column(Integer, ForeignKey("qms_qualification.qual_id"), nullable=False, index=True)
    audit_date = Column(Date, nullable=False)
    auditor = Column(String(50))
    result = Column(String(20), default="PASS")  # PASS/FAIL/CONDITIONAL
    score = Column(Float)
    next_audit_date = Column(Date)
    remarks = Column(Text)
    created_at = Column(DateTime, default=_utcnow)

    qualification = relationship("QmsQualification", back_populates="audits")

    def __repr__(self):
        return f"<QmsQualAudit(qual_audit_id={self.qual_audit_id}, qual_id={self.qual_id})>"


# ============================================================
# 규격관리 (Specification Management)
# ============================================================

class QmsSpecification(QmsBase):
    """규격 마스터"""
    __tablename__ = "qms_specification"

    spec_mgmt_id = Column(Integer, primary_key=True, autoincrement=True)
    spec_no = Column(String(50), unique=True, nullable=False)
    spec_type = Column(String(20), default="CUSTOMER")  # CUSTOMER/DRAWING/LEGAL/INTERNAL
    customer_id = Column(String(50), index=True)
    product_id = Column(String(50), index=True)
    title = Column(String(300), nullable=False)
    revision = Column(Integer, default=1)
    status = Column(String(20), default="ACTIVE")  # ACTIVE/SUPERSEDED/OBSOLETE
    effective_date = Column(Date)
    expiry_date = Column(Date)
    source = Column(String(200))
    remarks = Column(Text)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    drawings = relationship("QmsDrawingRevision", back_populates="specification", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsSpecification(spec_mgmt_id={self.spec_mgmt_id}, spec_no='{self.spec_no}')>"


class QmsDrawingRevision(QmsBase):
    """도면 개정이력"""
    __tablename__ = "qms_drawing_revision"

    drawing_rev_id = Column(Integer, primary_key=True, autoincrement=True)
    spec_mgmt_id = Column(Integer, ForeignKey("qms_specification.spec_mgmt_id"), nullable=False, index=True)
    drawing_no = Column(String(50), nullable=False)
    revision_no = Column(Integer, nullable=False)
    change_summary = Column(Text)
    changed_by = Column(String(50))
    change_date = Column(Date)
    file_path = Column(String(500))
    created_at = Column(DateTime, default=_utcnow)

    specification = relationship("QmsSpecification", back_populates="drawings")

    def __repr__(self):
        return f"<QmsDrawingRevision(drawing_rev_id={self.drawing_rev_id}, drawing_no='{self.drawing_no}')>"


class QmsSiFaq(QmsBase):
    """SI FAQ"""
    __tablename__ = "qms_si_faq"

    faq_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), index=True)
    category = Column(String(100))
    question = Column(Text, nullable=False)
    answer = Column(Text)
    reference_spec_id = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self):
        return f"<QmsSiFaq(faq_id={self.faq_id})>"


class QmsCsr(QmsBase):
    """CSR (고객 특별요구사항)"""
    __tablename__ = "qms_csr"

    csr_id = Column(Integer, primary_key=True, autoincrement=True)
    csr_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(50), index=True)
    requirement = Column(Text, nullable=False)
    category = Column(String(100))  # 품질/포장/물류/환경
    iatf_clause = Column(String(50))
    compliance_status = Column(String(20), default="PENDING")  # PENDING/COMPLIANT/NON_COMPLIANT/NA
    responsible = Column(String(50))
    target_date = Column(Date)
    completion_date = Column(Date)
    evidence = Column(Text)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self):
        return f"<QmsCsr(csr_id={self.csr_id}, csr_no='{self.csr_no}')>"


# ============================================================
# 고객심사관리 (Customer Audit Management)
# ============================================================

class QmsCustomerAudit(QmsBase):
    """고객심사"""
    __tablename__ = "qms_customer_audit"

    cust_audit_id = Column(Integer, primary_key=True, autoincrement=True)
    audit_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(String(50), index=True)
    audit_type = Column(String(20), default="SQ")  # SQ/PROCESS/PRODUCT/SYSTEM
    audit_date = Column(Date)
    audit_end_date = Column(Date)
    auditor_name = Column(String(100))
    scope = Column(Text)
    result = Column(String(20), default="PENDING")  # PENDING/PASS/CONDITIONAL/FAIL
    score = Column(Float)
    status = Column(String(20), default="SCHEDULED")  # SCHEDULED/IN_PROGRESS/COMPLETED/CLOSED
    remarks = Column(Text)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    findings = relationship("QmsCustomerAuditFinding", back_populates="audit", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsCustomerAudit(cust_audit_id={self.cust_audit_id}, audit_no='{self.audit_no}')>"


class QmsCustomerAuditFinding(QmsBase):
    """고객심사 발견사항"""
    __tablename__ = "qms_customer_audit_finding"

    cust_finding_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_audit_id = Column(Integer, ForeignKey("qms_customer_audit.cust_audit_id"), nullable=False, index=True)
    finding_no = Column(String(50), unique=True, nullable=False)
    finding_type = Column(String(20), nullable=False)  # MAJOR_NC/MINOR_NC/OBSERVATION/OFI
    clause_ref = Column(String(50))
    description = Column(Text, nullable=False)
    evidence = Column(Text)
    status = Column(String(20), default="OPEN")  # OPEN/ACTION_REQUIRED/CLOSED/VERIFIED
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    audit = relationship("QmsCustomerAudit", back_populates="findings")
    actions = relationship("QmsCustomerAuditAction", back_populates="finding", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsCustomerAuditFinding(cust_finding_id={self.cust_finding_id}, finding_no='{self.finding_no}')>"


class QmsCustomerAuditAction(QmsBase):
    """고객심사 시정조치"""
    __tablename__ = "qms_customer_audit_action"

    cust_action_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_finding_id = Column(Integer, ForeignKey("qms_customer_audit_finding.cust_finding_id"), nullable=False, index=True)
    action_no = Column(String(50), unique=True, nullable=False)
    root_cause = Column(Text)
    containment_action = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    responsible = Column(String(50))
    target_date = Column(Date)
    completion_date = Column(Date)
    status = Column(String(20), default="OPEN")  # OPEN/IN_PROGRESS/COMPLETED/VERIFIED
    verified_by = Column(String(50))
    verified_date = Column(Date)
    customer_feedback = Column(Text)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    finding = relationship("QmsCustomerAuditFinding", back_populates="actions")

    def __repr__(self):
        return f"<QmsCustomerAuditAction(cust_action_id={self.cust_action_id}, action_no='{self.action_no}')>"


# ============================================================
# 성과지표관리
# ============================================================

class QmsKpiDefinition(QmsBase):
    """KPI 정의"""
    __tablename__ = "qms_kpi_definition"

    kpi_id = Column(Integer, primary_key=True, autoincrement=True)
    kpi_no = Column(String(50), unique=True, nullable=False)
    kpi_name = Column(String(200), nullable=False)
    process_name = Column(String(100))
    category = Column(String(50))  # 품질/납기/원가/안전
    unit = Column(String(20))  # %, ppm, 건
    target_value = Column(Float)
    target_direction = Column(String(10), default="HIGHER")  # HIGHER/LOWER
    threshold_yellow = Column(Float)
    threshold_red = Column(Float)
    measurement_frequency = Column(String(20), default="MONTHLY")
    responsible = Column(String(50))
    formula = Column(Text)  # 산출식 설명
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    data_points = relationship("QmsKpiData", back_populates="kpi", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<QmsKpiDefinition(kpi_id={self.kpi_id}, kpi_no='{self.kpi_no}')>"


class QmsKpiData(QmsBase):
    """KPI 실적 데이터"""
    __tablename__ = "qms_kpi_data"

    data_id = Column(Integer, primary_key=True, autoincrement=True)
    kpi_id = Column(Integer, ForeignKey("qms_kpi_definition.kpi_id"), nullable=False, index=True)
    period = Column(String(20), nullable=False)  # 2026-01 등
    actual_value = Column(Float, nullable=False)
    status = Column(String(20))  # GREEN/YELLOW/RED (자동 계산)
    remarks = Column(Text)
    collected_by = Column(String(50))
    collected_at = Column(DateTime)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    kpi = relationship("QmsKpiDefinition", back_populates="data_points")

    __table_args__ = (
        UniqueConstraint("kpi_id", "period"),
    )

    def __repr__(self):
        return f"<QmsKpiData(data_id={self.data_id}, kpi_id={self.kpi_id}, period='{self.period}')>"


class QmsProcessMonitor(QmsBase):
    """공정 모니터링"""
    __tablename__ = "qms_process_monitor"

    monitor_id = Column(Integer, primary_key=True, autoincrement=True)
    process_name = Column(String(100), nullable=False)
    monitor_date = Column(Date, nullable=False)
    monitor_type = Column(String(20), default="ROUTINE")  # ROUTINE/SPECIAL/LAYERED
    auditor = Column(String(50))
    result = Column(String(20), default="OK")  # OK/NG/NA
    score = Column(Float)
    findings = Column(Text)
    actions_required = Column(Text)
    status = Column(String(20), default="OPEN")  # OPEN/CLOSED
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self):
        return f"<QmsProcessMonitor(monitor_id={self.monitor_id}, process_name='{self.process_name}')>"


class QmsRiskIssue(QmsBase):
    """리스크/이슈"""
    __tablename__ = "qms_risk_issue"

    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    issue_no = Column(String(50), unique=True, nullable=False)
    issue_type = Column(String(20), nullable=False)  # RISK/OPPORTUNITY/ISSUE
    category = Column(String(100))
    process_name = Column(String(100))
    description = Column(Text, nullable=False)
    severity = Column(Integer, default=3)  # 1-5
    likelihood = Column(Integer, default=3)  # 1-5
    risk_score = Column(Integer)  # severity * likelihood (자동계산)
    mitigation_plan = Column(Text)
    responsible = Column(String(50))
    target_date = Column(Date)
    status = Column(String(20), default="IDENTIFIED")  # IDENTIFIED/MITIGATING/RESOLVED/ACCEPTED
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def __repr__(self):
        return f"<QmsRiskIssue(issue_id={self.issue_id}, issue_no='{self.issue_no}')>"


# ============================================================
# Q&A (질문/답변)
# ============================================================

class QmsQna(QmsBase):
    """Q&A 질문/답변"""
    __tablename__ = "qms_qna"

    qna_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    category = Column(String(50), default="GENERAL")  # GENERAL/QUALITY/PROCESS/EQUIPMENT/SPEC/OTHER
    author_id = Column(String(50), nullable=True)
    author_name = Column(String(100), nullable=True)
    author_email = Column(String(200), nullable=True)
    status = Column(String(20), default="OPEN")  # OPEN/ANSWERED/CLOSED
    is_public = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    answered_by = Column(String(50), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<QmsQna(qna_id={self.qna_id}, title='{self.title}')>"
