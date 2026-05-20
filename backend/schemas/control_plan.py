"""
Control Plan Pydantic 스키마
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class ControlPlanCreate(BaseModel):
    """Control Plan 생성 요청"""
    cp_no: str
    product_id: str
    fmea_id: Optional[int] = None
    cp_type: str = "PRODUCTION"
    revision: int = 1
    status: str = "DRAFT"
    prepared_by: Optional[str] = None
    approved_by: Optional[str] = None


class ControlPlanUpdate(BaseModel):
    """Control Plan 수정 요청"""
    product_id: Optional[str] = None
    fmea_id: Optional[int] = None
    cp_type: Optional[str] = None
    revision: Optional[int] = None
    status: Optional[str] = None
    prepared_by: Optional[str] = None
    approved_by: Optional[str] = None


class ControlPlanResponse(BaseModel):
    """Control Plan 응답"""
    model_config = ConfigDict(from_attributes=True)

    cp_id: int
    cp_no: str
    product_id: str
    fmea_id: Optional[int] = None
    cp_type: str
    revision: int
    status: str
    prepared_by: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    product_name: Optional[str] = None
    item_count: Optional[int] = None


class ControlPlanItemCreate(BaseModel):
    """Control Plan 항목 생성"""
    process_no: Optional[str] = None
    process_name: Optional[str] = None
    machine_id: Optional[str] = None
    characteristic_name: Optional[str] = None
    characteristic_class: Optional[str] = None
    spec_id: Optional[int] = None
    evaluation_method: Optional[str] = None
    sample_size: Optional[str] = None
    sample_frequency: Optional[str] = None
    control_method: Optional[str] = None
    reaction_plan: Optional[str] = None


class ControlPlanItemUpdate(BaseModel):
    """Control Plan 항목 수정"""
    process_no: Optional[str] = None
    process_name: Optional[str] = None
    machine_id: Optional[str] = None
    characteristic_name: Optional[str] = None
    characteristic_class: Optional[str] = None
    spec_id: Optional[int] = None
    evaluation_method: Optional[str] = None
    sample_size: Optional[str] = None
    sample_frequency: Optional[str] = None
    control_method: Optional[str] = None
    reaction_plan: Optional[str] = None


class ControlPlanItemResponse(BaseModel):
    """Control Plan 항목 응답"""
    model_config = ConfigDict(from_attributes=True)

    cp_item_id: int
    cp_id: int
    process_no: Optional[str] = None
    process_name: Optional[str] = None
    machine_id: Optional[str] = None
    characteristic_name: Optional[str] = None
    characteristic_class: Optional[str] = None
    spec_id: Optional[int] = None
    evaluation_method: Optional[str] = None
    sample_size: Optional[str] = None
    sample_frequency: Optional[str] = None
    control_method: Optional[str] = None
    reaction_plan: Optional[str] = None
