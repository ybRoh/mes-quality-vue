"""
MSA (측정시스템분석) Pydantic 스키마
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class MsaStudyCreate(BaseModel):
    """MSA 연구 생성 요청"""
    msa_no: str
    product_id: str
    spec_id: Optional[int] = None
    study_type: str = "GRR"
    gage_name: Optional[str] = None
    gage_id: Optional[str] = None
    num_operators: int = 3
    num_parts: int = 10
    num_trials: int = 3
    tolerance: Optional[float] = None


class MsaStudyUpdate(BaseModel):
    """MSA 연구 수정 요청"""
    product_id: Optional[str] = None
    spec_id: Optional[int] = None
    study_type: Optional[str] = None
    gage_name: Optional[str] = None
    gage_id: Optional[str] = None
    num_operators: Optional[int] = None
    num_parts: Optional[int] = None
    num_trials: Optional[int] = None
    tolerance: Optional[float] = None


class MsaStudyResponse(BaseModel):
    """MSA 연구 응답"""
    model_config = ConfigDict(from_attributes=True)

    msa_id: int
    msa_no: str
    product_id: str
    spec_id: Optional[int] = None
    study_type: str
    gage_name: Optional[str] = None
    gage_id: Optional[str] = None
    num_operators: int
    num_parts: int
    num_trials: int
    tolerance: Optional[float] = None
    result_grr_pct: Optional[float] = None
    result_ndc: Optional[int] = None
    judgment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    product_name: Optional[str] = None
    measurement_count: Optional[int] = None


class MsaMeasurementCreate(BaseModel):
    """MSA 측정 데이터 생성"""
    operator_name: str
    part_no: int
    trial_no: int
    measured_value: float


class MsaMeasurementBulkCreate(BaseModel):
    """MSA 측정 데이터 일괄 생성"""
    measurements: List[MsaMeasurementCreate]


class MsaMeasurementResponse(BaseModel):
    """MSA 측정 데이터 응답"""
    model_config = ConfigDict(from_attributes=True)

    measurement_id: int
    msa_id: int
    operator_name: str
    part_no: int
    trial_no: int
    measured_value: float


class GrrResultResponse(BaseModel):
    """GR&R 계산 결과 응답"""
    msa_id: int
    ev: float                     # 장비 변동 (Equipment Variation)
    av: float                     # 작업자 변동 (Appraiser Variation)
    grr: float                    # GR&R = sqrt(EV^2 + AV^2)
    pv: float                     # 부품 변동 (Part Variation)
    tv: float                     # 총 변동 (Total Variation)
    grr_pct: float                # %GR&R
    ndc: int                      # 구별범주수
    ev_pct: float                 # %EV
    av_pct: float                 # %AV
    pv_pct: float                 # %PV
    judgment: str                 # ACCEPTABLE/MARGINAL/UNACCEPTABLE
