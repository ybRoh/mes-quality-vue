"""
FMEA Pydantic 스키마
- Create, Update, Response 모델
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, List


# ============================================================
# FMEA 헤더
# ============================================================

class FmeaCreate(BaseModel):
    """FMEA 생성 요청"""
    fmea_no: str
    product_id: str
    fmea_type: str = "PROCESS"
    revision: int = 1
    status: str = "DRAFT"
    prepared_by: Optional[str] = None
    approved_by: Optional[str] = None


class FmeaUpdate(BaseModel):
    """FMEA 수정 요청"""
    product_id: Optional[str] = None
    fmea_type: Optional[str] = None
    revision: Optional[int] = None
    status: Optional[str] = None
    prepared_by: Optional[str] = None
    approved_by: Optional[str] = None


class FmeaResponse(BaseModel):
    """FMEA 응답"""
    model_config = ConfigDict(from_attributes=True)

    fmea_id: int
    fmea_no: str
    product_id: str
    fmea_type: str
    revision: int
    status: str
    prepared_by: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    product_name: Optional[str] = None   # JOIN 결과
    item_count: Optional[int] = None     # 항목 수


# ============================================================
# FMEA 항목
# ============================================================

class FmeaItemCreate(BaseModel):
    """FMEA 항목 생성 요청"""
    process_step: Optional[str] = None
    function_requirement: Optional[str] = None
    failure_mode: str
    failure_effect: Optional[str] = None
    severity: int = Field(1, ge=1, le=10)
    failure_cause: Optional[str] = None
    occurrence: int = Field(1, ge=1, le=10)
    current_control_prevent: Optional[str] = None
    current_control_detect: Optional[str] = None
    detection: int = Field(1, ge=1, le=10)
    recommended_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    action_taken: Optional[str] = None
    new_severity: Optional[int] = Field(None, ge=1, le=10)
    new_occurrence: Optional[int] = Field(None, ge=1, le=10)
    new_detection: Optional[int] = Field(None, ge=1, le=10)


class FmeaItemUpdate(BaseModel):
    """FMEA 항목 수정 요청"""
    process_step: Optional[str] = None
    function_requirement: Optional[str] = None
    failure_mode: Optional[str] = None
    failure_effect: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=10)
    failure_cause: Optional[str] = None
    occurrence: Optional[int] = Field(None, ge=1, le=10)
    current_control_prevent: Optional[str] = None
    current_control_detect: Optional[str] = None
    detection: Optional[int] = Field(None, ge=1, le=10)
    recommended_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    action_taken: Optional[str] = None
    new_severity: Optional[int] = Field(None, ge=1, le=10)
    new_occurrence: Optional[int] = Field(None, ge=1, le=10)
    new_detection: Optional[int] = Field(None, ge=1, le=10)


class FmeaItemResponse(BaseModel):
    """FMEA 항목 응답"""
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    fmea_id: int
    process_step: Optional[str] = None
    function_requirement: Optional[str] = None
    failure_mode: str
    failure_effect: Optional[str] = None
    severity: int
    failure_cause: Optional[str] = None
    occurrence: int
    current_control_prevent: Optional[str] = None
    current_control_detect: Optional[str] = None
    detection: int
    rpn: Optional[int] = None
    ap: Optional[str] = None
    recommended_action: Optional[str] = None
    responsible: Optional[str] = None
    target_date: Optional[date] = None
    action_taken: Optional[str] = None
    new_severity: Optional[int] = None
    new_occurrence: Optional[int] = None
    new_detection: Optional[int] = None
    new_rpn: Optional[int] = None


# ============================================================
# RPN 분석
# ============================================================

class RpnAnalysisResponse(BaseModel):
    """RPN 분석 응답"""
    fmea_id: int
    total_items: int
    high_rpn_count: int          # RPN >= 100
    medium_rpn_count: int        # 50 <= RPN < 100
    low_rpn_count: int           # RPN < 50
    avg_rpn: float
    max_rpn: int
    top_rpn_items: List[FmeaItemResponse]
