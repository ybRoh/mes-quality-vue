"""
SPC (통계적 공정관리) Pydantic 스키마
"""

from pydantic import BaseModel
from typing import Optional, List


class ControlChartResponse(BaseModel):
    """관리도 응답"""
    spec_id: int
    insp_item: Optional[str] = None
    product_id: Optional[str] = None
    values: List[float]
    mean: float
    ucl: float
    lcl: float
    std: float
    count: int
    usl: Optional[float] = None
    lsl: Optional[float] = None
    nominal: Optional[float] = None
    lot_nos: Optional[List[str]] = None


class CapabilityResponse(BaseModel):
    """공정능력 응답"""
    spec_id: int
    insp_item: Optional[str] = None
    product_id: Optional[str] = None
    mean: float
    std_within: float
    std_overall: float
    cp: float
    cpk: float
    pp: float
    ppk: float
    cpu: float
    cpl: float
    count: int
    min_val: float
    max_val: float
    usl: Optional[float] = None
    lsl: Optional[float] = None
    nominal: Optional[float] = None
