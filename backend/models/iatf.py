"""
IATF 16949 QMS 신규 테이블 정의
- QmsBase 사용 (create_all 안전)
- FMEA, Control Plan, MSA, PPAP, APQP 모듈
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, DateTime,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from models.base import QmsBase


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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
