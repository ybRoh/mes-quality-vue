"""
내부심사관리 API 라우터
- 요구사항, 심사계획, 부적합/관찰, 시정조치 CRUD
- 연간 요약 대시보드
"""

import logging
from datetime import datetime, timezone, date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user, require_role
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser
from models.iatf import (
    QmsAuditRequirement, QmsAuditPlan, QmsAuditFinding, QmsCorrectiveAction,
)
from schemas.audit import (
    AuditRequirementCreate, AuditRequirementUpdate, AuditRequirementResponse,
    AuditPlanCreate, AuditPlanUpdate, AuditPlanResponse,
    AuditFindingCreate, AuditFindingUpdate, AuditFindingResponse,
    CorrectiveActionCreate, CorrectiveActionUpdate, CorrectiveActionResponse,
    AuditSummaryResponse,
)
from schemas.common import PagedResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/audit", tags=["내부심사관리"])


# ============================================================
# 요구사항
# ============================================================

@router.get("/requirements", response_model=PagedResponse[AuditRequirementResponse])
def list_requirements(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsAuditRequirement)
    if category:
        query = query.filter(QmsAuditRequirement.category == category)
    if is_active is not None:
        query = query.filter(QmsAuditRequirement.is_active == is_active)

    total = query.count()
    items = query.order_by(QmsAuditRequirement.req_no).offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size
    return PagedResponse(
        items=[AuditRequirementResponse.model_validate(r) for r in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.post("/requirements", response_model=AuditRequirementResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_requirement(
    data: AuditRequirementCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsAuditRequirement).filter(QmsAuditRequirement.req_no == data.req_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"요구사항 번호 '{data.req_no}'가 이미 존재합니다")

    req = QmsAuditRequirement(
        req_no=data.req_no, clause_ref=data.clause_ref, category=data.category,
        description=data.description, audit_criteria=data.audit_criteria, is_active=data.is_active,
    )
    db.add(req)
    log_create(db, current_user.user_id, "qms_audit_requirement", data.req_no, "요구사항 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(req)
    return AuditRequirementResponse.model_validate(req)


@router.get("/requirements/{req_id}", response_model=AuditRequirementResponse)
def get_requirement(req_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    req = db.query(QmsAuditRequirement).filter(QmsAuditRequirement.req_id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="요구사항을 찾을 수 없습니다")
    return AuditRequirementResponse.model_validate(req)


@router.put("/requirements/{req_id}", response_model=AuditRequirementResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_requirement(
    req_id: int, data: AuditRequirementUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    req = db.query(QmsAuditRequirement).filter(QmsAuditRequirement.req_id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="요구사항을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(req, key, None)
        setattr(req, key, value)
        log_update(db, current_user.user_id, "qms_audit_requirement", req.req_no, key, old_value, value)

    req.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(req)
    return AuditRequirementResponse.model_validate(req)


@router.delete("/requirements/{req_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_requirement(req_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    req = db.query(QmsAuditRequirement).filter(QmsAuditRequirement.req_id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="요구사항을 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_audit_requirement", req.req_no, "요구사항 삭제")
    db.delete(req)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "요구사항이 삭제되었습니다"}


# ============================================================
# 심사 계획
# ============================================================

@router.get("/plans", response_model=PagedResponse[AuditPlanResponse])
def list_plans(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    audit_year: Optional[int] = None,
    audit_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsAuditPlan)
    if audit_year:
        query = query.filter(QmsAuditPlan.audit_year == audit_year)
    if audit_type:
        query = query.filter(QmsAuditPlan.audit_type == audit_type)
    if status:
        query = query.filter(QmsAuditPlan.status == status)

    total = query.count()
    plans = query.order_by(QmsAuditPlan.created_at.desc()).offset((page - 1) * size).limit(size).all()

    plan_ids = [p.plan_id for p in plans]
    finding_counts = {}
    if plan_ids:
        fc = db.query(QmsAuditFinding.plan_id, func.count(QmsAuditFinding.finding_id)).filter(
            QmsAuditFinding.plan_id.in_(plan_ids)
        ).group_by(QmsAuditFinding.plan_id).all()
        finding_counts = {pid: cnt for pid, cnt in fc}

    items = []
    for p in plans:
        resp = AuditPlanResponse.model_validate(p)
        resp.finding_count = finding_counts.get(p.plan_id, 0)
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/plans", response_model=AuditPlanResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_plan(
    data: AuditPlanCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_no == data.plan_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"심사계획 번호 '{data.plan_no}'가 이미 존재합니다")

    plan = QmsAuditPlan(
        plan_no=data.plan_no, audit_year=data.audit_year, audit_type=data.audit_type,
        title=data.title, scope=data.scope, department=data.department,
        lead_auditor=data.lead_auditor, plan_start=data.plan_start, plan_end=data.plan_end,
        status=data.status,
    )
    db.add(plan)
    log_create(db, current_user.user_id, "qms_audit_plan", data.plan_no, "심사계획 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(plan)
    resp = AuditPlanResponse.model_validate(plan)
    resp.finding_count = 0
    return resp


@router.get("/plans/{plan_id}", response_model=AuditPlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    plan = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="심사계획을 찾을 수 없습니다")
    fc = db.query(func.count(QmsAuditFinding.finding_id)).filter(QmsAuditFinding.plan_id == plan_id).scalar()
    resp = AuditPlanResponse.model_validate(plan)
    resp.finding_count = fc
    return resp


@router.put("/plans/{plan_id}", response_model=AuditPlanResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_plan(
    plan_id: int, data: AuditPlanUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    plan = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="심사계획을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(plan, key, None)
        setattr(plan, key, value)
        log_update(db, current_user.user_id, "qms_audit_plan", plan.plan_no, key, old_value, value)

    plan.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(plan)
    fc = db.query(func.count(QmsAuditFinding.finding_id)).filter(QmsAuditFinding.plan_id == plan_id).scalar()
    resp = AuditPlanResponse.model_validate(plan)
    resp.finding_count = fc
    return resp


@router.delete("/plans/{plan_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_plan(plan_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    plan = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="심사계획을 찾을 수 없습니다")

    # 하위 시정조치 → 발견사항 삭제
    findings = db.query(QmsAuditFinding).filter(QmsAuditFinding.plan_id == plan_id).all()
    for f in findings:
        db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.finding_id == f.finding_id).delete()
    db.query(QmsAuditFinding).filter(QmsAuditFinding.plan_id == plan_id).delete()

    log_delete(db, current_user.user_id, "qms_audit_plan", plan.plan_no, "심사계획 삭제")
    db.delete(plan)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "심사계획이 삭제되었습니다"}


# ============================================================
# 발견사항 (Findings)
# ============================================================

@router.get("/plans/{plan_id}/findings", response_model=List[AuditFindingResponse])
def list_plan_findings(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    plan = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="심사계획을 찾을 수 없습니다")

    findings = db.query(QmsAuditFinding).filter(
        QmsAuditFinding.plan_id == plan_id
    ).order_by(QmsAuditFinding.finding_id).all()

    # Batch load action counts to avoid N+1
    finding_ids = [f.finding_id for f in findings]
    action_counts = {}
    if finding_ids:
        ac = db.query(QmsCorrectiveAction.finding_id, func.count(QmsCorrectiveAction.action_id)).filter(
            QmsCorrectiveAction.finding_id.in_(finding_ids)
        ).group_by(QmsCorrectiveAction.finding_id).all()
        action_counts = {fid: cnt for fid, cnt in ac}

    result = []
    for f in findings:
        resp = AuditFindingResponse.model_validate(f)
        resp.action_count = action_counts.get(f.finding_id, 0)
        resp.plan_no = plan.plan_no
        result.append(resp)
    return result


@router.post("/plans/{plan_id}/findings", response_model=AuditFindingResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_finding(
    plan_id: int, data: AuditFindingCreate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    plan = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="심사계획을 찾을 수 없습니다")

    existing = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_no == data.finding_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"발견사항 번호 '{data.finding_no}'가 이미 존재합니다")

    finding = QmsAuditFinding(
        plan_id=plan_id, finding_no=data.finding_no, finding_type=data.finding_type,
        clause_ref=data.clause_ref, description=data.description, evidence=data.evidence,
        status=data.status,
    )
    db.add(finding)
    log_create(db, current_user.user_id, "qms_audit_finding", data.finding_no, "발견사항 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(finding)
    resp = AuditFindingResponse.model_validate(finding)
    resp.action_count = 0
    resp.plan_no = plan.plan_no
    return resp


@router.get("/findings", response_model=PagedResponse[AuditFindingResponse])
def list_all_findings(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    finding_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsAuditFinding)
    if finding_type:
        query = query.filter(QmsAuditFinding.finding_type == finding_type)
    if status:
        query = query.filter(QmsAuditFinding.status == status)

    total = query.count()
    findings = query.order_by(QmsAuditFinding.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # batch load counts and plan_no
    finding_ids = [f.finding_id for f in findings]
    plan_ids = list(set(f.plan_id for f in findings))
    action_counts = {}
    plan_map = {}

    if finding_ids:
        ac = db.query(QmsCorrectiveAction.finding_id, func.count(QmsCorrectiveAction.action_id)).filter(
            QmsCorrectiveAction.finding_id.in_(finding_ids)
        ).group_by(QmsCorrectiveAction.finding_id).all()
        action_counts = {fid: cnt for fid, cnt in ac}

    if plan_ids:
        plans = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id.in_(plan_ids)).all()
        plan_map = {p.plan_id: p.plan_no for p in plans}

    items = []
    for f in findings:
        resp = AuditFindingResponse.model_validate(f)
        resp.action_count = action_counts.get(f.finding_id, 0)
        resp.plan_no = plan_map.get(f.plan_id)
        items.append(resp)

    pages_count = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages_count)


@router.get("/findings/{finding_id}", response_model=AuditFindingResponse)
def get_finding(finding_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")
    ac = db.query(func.count(QmsCorrectiveAction.action_id)).filter(
        QmsCorrectiveAction.finding_id == finding_id
    ).scalar()
    plan = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id == finding.plan_id).first()
    resp = AuditFindingResponse.model_validate(finding)
    resp.action_count = ac
    resp.plan_no = plan.plan_no if plan else None
    return resp


@router.put("/findings/{finding_id}", response_model=AuditFindingResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_finding(
    finding_id: int, data: AuditFindingUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(finding, key, None)
        setattr(finding, key, value)
        log_update(db, current_user.user_id, "qms_audit_finding", finding.finding_no, key, old_value, value)

    finding.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(finding)
    ac = db.query(func.count(QmsCorrectiveAction.action_id)).filter(
        QmsCorrectiveAction.finding_id == finding_id
    ).scalar()
    plan = db.query(QmsAuditPlan).filter(QmsAuditPlan.plan_id == finding.plan_id).first()
    resp = AuditFindingResponse.model_validate(finding)
    resp.action_count = ac
    resp.plan_no = plan.plan_no if plan else None
    return resp


@router.delete("/findings/{finding_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_finding(finding_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")
    db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.finding_id == finding_id).delete()
    log_delete(db, current_user.user_id, "qms_audit_finding", finding.finding_no, "발견사항 삭제")
    db.delete(finding)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "발견사항이 삭제되었습니다"}


# ============================================================
# 시정조치 (Corrective Actions)
# ============================================================

@router.get("/findings/{finding_id}/actions", response_model=List[CorrectiveActionResponse])
def list_finding_actions(
    finding_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")

    actions = db.query(QmsCorrectiveAction).filter(
        QmsCorrectiveAction.finding_id == finding_id
    ).order_by(QmsCorrectiveAction.action_id).all()

    result = []
    for a in actions:
        resp = CorrectiveActionResponse.model_validate(a)
        resp.finding_no = finding.finding_no
        resp.is_overdue = (
            a.target_date is not None
            and a.status not in ("COMPLETED", "VERIFIED")
            and a.target_date < date.today()
        )
        result.append(resp)
    return result


@router.post("/findings/{finding_id}/actions", response_model=CorrectiveActionResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_action(
    finding_id: int, data: CorrectiveActionCreate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")

    existing = db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.action_no == data.action_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"시정조치 번호 '{data.action_no}'가 이미 존재합니다")

    action = QmsCorrectiveAction(
        finding_id=finding_id, action_no=data.action_no, root_cause=data.root_cause,
        containment_action=data.containment_action, corrective_action=data.corrective_action,
        preventive_action=data.preventive_action, responsible=data.responsible,
        target_date=data.target_date, status=data.status,
    )
    db.add(action)

    # 발견사항 상태를 ACTION_REQUIRED로 변경
    if finding.status == "OPEN":
        finding.status = "ACTION_REQUIRED"
        finding.updated_at = datetime.now(timezone.utc)

    log_create(db, current_user.user_id, "qms_corrective_action", data.action_no, "시정조치 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(action)
    resp = CorrectiveActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no
    resp.is_overdue = False
    return resp


@router.get("/actions", response_model=PagedResponse[CorrectiveActionResponse])
def list_all_actions(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    overdue_only: bool = False,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsCorrectiveAction)
    if status:
        query = query.filter(QmsCorrectiveAction.status == status)
    if overdue_only:
        query = query.filter(
            QmsCorrectiveAction.target_date < date.today(),
            QmsCorrectiveAction.status.notin_(["COMPLETED", "VERIFIED"]),
        )

    total = query.count()
    actions = query.order_by(QmsCorrectiveAction.created_at.desc()).offset((page - 1) * size).limit(size).all()

    finding_ids = list(set(a.finding_id for a in actions))
    finding_map = {}
    if finding_ids:
        findings = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id.in_(finding_ids)).all()
        finding_map = {f.finding_id: f.finding_no for f in findings}

    items = []
    for a in actions:
        resp = CorrectiveActionResponse.model_validate(a)
        resp.finding_no = finding_map.get(a.finding_id)
        resp.is_overdue = (
            a.target_date is not None
            and a.status not in ("COMPLETED", "VERIFIED")
            and a.target_date < date.today()
        )
        items.append(resp)

    pages_count = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages_count)


@router.get("/actions/{action_id}", response_model=CorrectiveActionResponse)
def get_action(action_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    action = db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == action.finding_id).first()
    resp = CorrectiveActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no if finding else None
    resp.is_overdue = (
        action.target_date is not None
        and action.status not in ("COMPLETED", "VERIFIED")
        and action.target_date < date.today()
    )
    return resp


@router.put("/actions/{action_id}", response_model=CorrectiveActionResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_action(
    action_id: int, data: CorrectiveActionUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    action = db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(action, key, None)
        setattr(action, key, value)
        log_update(db, current_user.user_id, "qms_corrective_action", action.action_no, key, old_value, value)

    action.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(action)
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == action.finding_id).first()
    resp = CorrectiveActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no if finding else None
    resp.is_overdue = (
        action.target_date is not None
        and action.status not in ("COMPLETED", "VERIFIED")
        and action.target_date < date.today()
    )
    return resp


@router.delete("/actions/{action_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_action(action_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    action = db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_corrective_action", action.action_no, "시정조치 삭제")
    db.delete(action)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "시정조치가 삭제되었습니다"}


@router.put("/actions/{action_id}/verify", response_model=CorrectiveActionResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def verify_action(
    action_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """시정조치 검증"""
    action = db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")

    if action.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="완료 상태인 시정조치만 검증할 수 있습니다")

    action.status = "VERIFIED"
    action.verified_by = current_user.user_id
    action.verified_date = date.today()
    action.updated_at = datetime.now(timezone.utc)

    # 해당 발견사항의 모든 시정조치가 VERIFIED이면 발견사항도 VERIFIED로 변경
    finding = db.query(QmsAuditFinding).filter(QmsAuditFinding.finding_id == action.finding_id).first()
    if finding:
        all_actions = db.query(QmsCorrectiveAction).filter(
            QmsCorrectiveAction.finding_id == action.finding_id,
            QmsCorrectiveAction.action_id != action_id,
        ).all()
        all_verified = all(a.status == "VERIFIED" for a in all_actions)
        if all_verified:
            finding.status = "VERIFIED"
            finding.updated_at = datetime.now(timezone.utc)

    log_update(db, current_user.user_id, "qms_corrective_action", action.action_no, "status", "COMPLETED", "VERIFIED")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(action)
    resp = CorrectiveActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no if finding else None
    resp.is_overdue = False
    return resp


# ============================================================
# 연간 요약
# ============================================================

@router.get("/summary/{audit_year}", response_model=AuditSummaryResponse)
def audit_summary(
    audit_year: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    plans = db.query(QmsAuditPlan).filter(QmsAuditPlan.audit_year == audit_year).all()
    total_plans = len(plans)
    completed_plans = sum(1 for p in plans if p.status == "COMPLETED")

    plan_ids = [p.plan_id for p in plans]
    findings = []
    if plan_ids:
        findings = db.query(QmsAuditFinding).filter(QmsAuditFinding.plan_id.in_(plan_ids)).all()

    total_findings = len(findings)
    major_nc = sum(1 for f in findings if f.finding_type == "MAJOR_NC")
    minor_nc = sum(1 for f in findings if f.finding_type == "MINOR_NC")
    observation = sum(1 for f in findings if f.finding_type == "OBSERVATION")
    ofi = sum(1 for f in findings if f.finding_type == "OFI")

    finding_ids = [f.finding_id for f in findings]
    actions = []
    if finding_ids:
        actions = db.query(QmsCorrectiveAction).filter(QmsCorrectiveAction.finding_id.in_(finding_ids)).all()

    total_actions = len(actions)
    completed_actions = sum(1 for a in actions if a.status in ("COMPLETED", "VERIFIED"))
    overdue_actions = sum(
        1 for a in actions
        if a.target_date and a.status not in ("COMPLETED", "VERIFIED") and a.target_date < date.today()
    )

    return AuditSummaryResponse(
        audit_year=audit_year,
        total_plans=total_plans,
        completed_plans=completed_plans,
        total_findings=total_findings,
        major_nc_count=major_nc,
        minor_nc_count=minor_nc,
        observation_count=observation,
        ofi_count=ofi,
        total_actions=total_actions,
        completed_actions=completed_actions,
        overdue_actions=overdue_actions,
    )
