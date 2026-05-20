"""
클레임 (8D 프로세스) Pydantic 스키마
"""

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class ClaimCreate(BaseModel):
    """클레임 생성 요청 (D1/D2)"""
    claim_id: str
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    lot_no: Optional[str] = None
    claim_date: date
    claim_qty: Optional[int] = None
    defect_type: Optional[str] = None
    description: Optional[str] = None
    status: str = "OPEN"
    due_date: Optional[date] = None
    # D1: 팀 구성
    team_members: Optional[str] = None
    # D2: 문제 정의
    defect_source: Optional[str] = None
    problem_definition: Optional[str] = None


class ClaimD3Update(BaseModel):
    """D3: 즉각 조치"""
    immediate_action: Optional[str] = None
    immediate_action_date: Optional[date] = None


class ClaimD4Update(BaseModel):
    """D4: 원인 분석 (4M + 5Why)"""
    cause_man: Optional[str] = None
    cause_machine: Optional[str] = None
    cause_material: Optional[str] = None
    cause_method: Optional[str] = None
    why1: Optional[str] = None
    why2: Optional[str] = None
    why3: Optional[str] = None
    why4: Optional[str] = None
    why5: Optional[str] = None
    root_cause: Optional[str] = None


class ClaimD5Update(BaseModel):
    """D5: 시정 조치"""
    cause: Optional[str] = None
    countermeasure: Optional[str] = None
    corrective_action_date: Optional[date] = None


class ClaimD6Update(BaseModel):
    """D6: 유효성 검증"""
    verification_result: Optional[str] = None
    verification_date: Optional[date] = None
    verification_by: Optional[str] = None


class ClaimD7Update(BaseModel):
    """D7: 수평 전개"""
    deployment_targets: Optional[str] = None
    deployment_action: Optional[str] = None
    deployment_date: Optional[date] = None


class ClaimD8Update(BaseModel):
    """D8: 완료"""
    close_date: Optional[date] = None
    close_approver: Optional[str] = None
    lessons_learned: Optional[str] = None
    status: str = "CLOSED"


class ClaimResponse(BaseModel):
    """클레임 응답"""
    model_config = ConfigDict(from_attributes=True)

    claim_id: str
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    lot_no: Optional[str] = None
    claim_date: Optional[date] = None
    claim_qty: Optional[int] = None
    defect_type: Optional[str] = None
    description: Optional[str] = None
    cause: Optional[str] = None
    countermeasure: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    created_at: Optional[datetime] = None
    # D1
    team_members: Optional[str] = None
    # D2
    defect_source: Optional[str] = None
    problem_definition: Optional[str] = None
    # D3
    immediate_action: Optional[str] = None
    immediate_action_date: Optional[date] = None
    # D4
    cause_man: Optional[str] = None
    cause_machine: Optional[str] = None
    cause_material: Optional[str] = None
    cause_method: Optional[str] = None
    why1: Optional[str] = None
    why2: Optional[str] = None
    why3: Optional[str] = None
    why4: Optional[str] = None
    why5: Optional[str] = None
    root_cause: Optional[str] = None
    # D5
    corrective_action_date: Optional[date] = None
    # D6
    verification_result: Optional[str] = None
    verification_date: Optional[date] = None
    verification_by: Optional[str] = None
    # D7
    deployment_targets: Optional[str] = None
    deployment_action: Optional[str] = None
    deployment_date: Optional[date] = None
    # D8
    close_date: Optional[date] = None
    close_approver: Optional[str] = None
    lessons_learned: Optional[str] = None
    # 추가 정보 (JOIN)
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
