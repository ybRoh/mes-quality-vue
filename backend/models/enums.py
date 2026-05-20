"""
IATF 16949 QMS 열거형 정의
- FMEA, Control Plan, MSA, PPAP, APQP 관련 상태 및 유형
"""

import enum


class FmeaStatus(str, enum.Enum):
    """FMEA 상태"""
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    CLOSED = "CLOSED"


class CpType(str, enum.Enum):
    """Control Plan 유형"""
    PROTOTYPE = "PROTOTYPE"
    PRE_LAUNCH = "PRE_LAUNCH"
    PRODUCTION = "PRODUCTION"


class MsaStudyType(str, enum.Enum):
    """MSA 연구 유형"""
    GRR = "GRR"
    BIAS = "BIAS"
    LINEARITY = "LINEARITY"


class MsaJudgment(str, enum.Enum):
    """MSA 판정 결과"""
    ACCEPTABLE = "ACCEPTABLE"
    MARGINAL = "MARGINAL"
    UNACCEPTABLE = "UNACCEPTABLE"


class PpapStatus(str, enum.Enum):
    """PPAP 상태"""
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApqpPhase(int, enum.Enum):
    """APQP 단계 (1~5)"""
    PLAN_DEFINE = 1
    PRODUCT_DESIGN = 2
    PROCESS_DESIGN = 3
    VALIDATION = 4
    PRODUCTION = 5


class ApqpStatus(str, enum.Enum):
    """APQP 상태"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ON_HOLD = "ON_HOLD"


class ActionPriority(str, enum.Enum):
    """조치 우선순위"""
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


class CharacteristicClass(str, enum.Enum):
    """특성 등급"""
    CTQ = "CTQ"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
