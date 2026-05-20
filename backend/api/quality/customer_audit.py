"""
고객심사관리 API 라우터
- 고객심사, 발견사항, 시정조치 CRUD
- 연간 요약 대시보드
"""

import logging
from datetime import datetime, timezone, date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from api.deps import get_db, get_current_user
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser
from models.iatf import (
    QmsCustomerAudit, QmsCustomerAuditFinding, QmsCustomerAuditAction,
)
from schemas.customer_audit import (
    CustomerAuditCreate, CustomerAuditUpdate, CustomerAuditResponse,
    CustomerAuditFindingCreate, CustomerAuditFindingUpdate, CustomerAuditFindingResponse,
    CustomerAuditActionCreate, CustomerAuditActionUpdate, CustomerAuditActionResponse,
    CustomerAuditSummaryResponse,
)
from schemas.common import PagedResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/customer-audit", tags=["고객심사관리"])


# ============================================================
# 고객심사
# ============================================================

@router.get("/", response_model=PagedResponse[CustomerAuditResponse])
def list_audits(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    customer_id: Optional[str] = None,
    audit_type: Optional[str] = None,
    status: Optional[str] = None,
    result: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsCustomerAudit)
    if customer_id:
        query = query.filter(QmsCustomerAudit.customer_id == customer_id)
    if audit_type:
        query = query.filter(QmsCustomerAudit.audit_type == audit_type)
    if status:
        query = query.filter(QmsCustomerAudit.status == status)
    if result:
        query = query.filter(QmsCustomerAudit.result == result)

    total = query.count()
    audits = query.order_by(QmsCustomerAudit.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # batch load finding counts
    audit_ids = [a.cust_audit_id for a in audits]
    finding_counts = {}
    if audit_ids:
        fc = db.query(
            QmsCustomerAuditFinding.cust_audit_id,
            func.count(QmsCustomerAuditFinding.cust_finding_id),
        ).filter(
            QmsCustomerAuditFinding.cust_audit_id.in_(audit_ids)
        ).group_by(QmsCustomerAuditFinding.cust_audit_id).all()
        finding_counts = {aid: cnt for aid, cnt in fc}

    items = []
    for a in audits:
        resp = CustomerAuditResponse.model_validate(a)
        resp.finding_count = finding_counts.get(a.cust_audit_id, 0)
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=CustomerAuditResponse)
def create_audit(
    data: CustomerAuditCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.audit_no == data.audit_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"고객심사 번호 '{data.audit_no}'가 이미 존재합니다")

    audit = QmsCustomerAudit(
        audit_no=data.audit_no, customer_id=data.customer_id, audit_type=data.audit_type,
        audit_date=data.audit_date, audit_end_date=data.audit_end_date,
        auditor_name=data.auditor_name, scope=data.scope,
        result=data.result, score=data.score, status=data.status,
        remarks=data.remarks,
    )
    db.add(audit)
    log_create(db, current_user.user_id, "qms_customer_audit", data.audit_no, "고객심사 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(audit)
    resp = CustomerAuditResponse.model_validate(audit)
    resp.finding_count = 0
    return resp


@router.get("/{cust_audit_id}", response_model=CustomerAuditResponse)
def get_audit(cust_audit_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    audit = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id == cust_audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="고객심사를 찾을 수 없습니다")
    fc = db.query(func.count(QmsCustomerAuditFinding.cust_finding_id)).filter(
        QmsCustomerAuditFinding.cust_audit_id == cust_audit_id
    ).scalar()
    resp = CustomerAuditResponse.model_validate(audit)
    resp.finding_count = fc
    return resp


@router.put("/{cust_audit_id}", response_model=CustomerAuditResponse)
def update_audit(
    cust_audit_id: int, data: CustomerAuditUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    audit = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id == cust_audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="고객심사를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(audit, key)
        setattr(audit, key, value)
        log_update(db, current_user.user_id, "qms_customer_audit", audit.audit_no, key, old_value, value)

    audit.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(audit)
    fc = db.query(func.count(QmsCustomerAuditFinding.cust_finding_id)).filter(
        QmsCustomerAuditFinding.cust_audit_id == cust_audit_id
    ).scalar()
    resp = CustomerAuditResponse.model_validate(audit)
    resp.finding_count = fc
    return resp


@router.delete("/{cust_audit_id}")
def delete_audit(cust_audit_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    audit = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id == cust_audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="고객심사를 찾을 수 없습니다")

    # 하위 시정조치 → 발견사항 삭제
    findings = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_audit_id == cust_audit_id).all()
    for f in findings:
        db.query(QmsCustomerAuditAction).filter(QmsCustomerAuditAction.cust_finding_id == f.cust_finding_id).delete()
    db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_audit_id == cust_audit_id).delete()

    log_delete(db, current_user.user_id, "qms_customer_audit", audit.audit_no, "고객심사 삭제")
    db.delete(audit)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "고객심사가 삭제되었습니다"}


# ============================================================
# 발견사항 (Findings)
# ============================================================

@router.get("/{cust_audit_id}/findings", response_model=List[CustomerAuditFindingResponse])
def list_audit_findings(
    cust_audit_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    audit = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id == cust_audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="고객심사를 찾을 수 없습니다")

    findings = db.query(QmsCustomerAuditFinding).filter(
        QmsCustomerAuditFinding.cust_audit_id == cust_audit_id
    ).order_by(QmsCustomerAuditFinding.cust_finding_id).all()

    result = []
    for f in findings:
        ac = db.query(func.count(QmsCustomerAuditAction.cust_action_id)).filter(
            QmsCustomerAuditAction.cust_finding_id == f.cust_finding_id
        ).scalar()
        resp = CustomerAuditFindingResponse.model_validate(f)
        resp.action_count = ac
        resp.audit_no = audit.audit_no
        result.append(resp)
    return result


@router.post("/{cust_audit_id}/findings", response_model=CustomerAuditFindingResponse)
def create_finding(
    cust_audit_id: int, data: CustomerAuditFindingCreate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    audit = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id == cust_audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="고객심사를 찾을 수 없습니다")

    existing = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.finding_no == data.finding_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"발견사항 번호 '{data.finding_no}'가 이미 존재합니다")

    finding = QmsCustomerAuditFinding(
        cust_audit_id=cust_audit_id, finding_no=data.finding_no, finding_type=data.finding_type,
        clause_ref=data.clause_ref, description=data.description, evidence=data.evidence,
        status=data.status,
    )
    db.add(finding)
    log_create(db, current_user.user_id, "qms_customer_audit_finding", data.finding_no, "고객심사 발견사항 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(finding)
    resp = CustomerAuditFindingResponse.model_validate(finding)
    resp.action_count = 0
    resp.audit_no = audit.audit_no
    return resp


@router.get("/findings", response_model=PagedResponse[CustomerAuditFindingResponse])
def list_all_findings(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    finding_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsCustomerAuditFinding)
    if finding_type:
        query = query.filter(QmsCustomerAuditFinding.finding_type == finding_type)
    if status:
        query = query.filter(QmsCustomerAuditFinding.status == status)

    total = query.count()
    findings = query.order_by(QmsCustomerAuditFinding.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # batch load counts and audit_no
    finding_ids = [f.cust_finding_id for f in findings]
    audit_ids = list(set(f.cust_audit_id for f in findings))
    action_counts = {}
    audit_map = {}

    if finding_ids:
        ac = db.query(
            QmsCustomerAuditAction.cust_finding_id,
            func.count(QmsCustomerAuditAction.cust_action_id),
        ).filter(
            QmsCustomerAuditAction.cust_finding_id.in_(finding_ids)
        ).group_by(QmsCustomerAuditAction.cust_finding_id).all()
        action_counts = {fid: cnt for fid, cnt in ac}

    if audit_ids:
        audits = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id.in_(audit_ids)).all()
        audit_map = {a.cust_audit_id: a.audit_no for a in audits}

    items = []
    for f in findings:
        resp = CustomerAuditFindingResponse.model_validate(f)
        resp.action_count = action_counts.get(f.cust_finding_id, 0)
        resp.audit_no = audit_map.get(f.cust_audit_id)
        items.append(resp)

    pages_count = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages_count)


@router.get("/findings/{cust_finding_id}", response_model=CustomerAuditFindingResponse)
def get_finding(cust_finding_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == cust_finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")
    ac = db.query(func.count(QmsCustomerAuditAction.cust_action_id)).filter(
        QmsCustomerAuditAction.cust_finding_id == cust_finding_id
    ).scalar()
    audit = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id == finding.cust_audit_id).first()
    resp = CustomerAuditFindingResponse.model_validate(finding)
    resp.action_count = ac
    resp.audit_no = audit.audit_no if audit else None
    return resp


@router.put("/findings/{cust_finding_id}", response_model=CustomerAuditFindingResponse)
def update_finding(
    cust_finding_id: int, data: CustomerAuditFindingUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == cust_finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(finding, key)
        setattr(finding, key, value)
        log_update(db, current_user.user_id, "qms_customer_audit_finding", finding.finding_no, key, old_value, value)

    finding.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(finding)
    ac = db.query(func.count(QmsCustomerAuditAction.cust_action_id)).filter(
        QmsCustomerAuditAction.cust_finding_id == cust_finding_id
    ).scalar()
    audit = db.query(QmsCustomerAudit).filter(QmsCustomerAudit.cust_audit_id == finding.cust_audit_id).first()
    resp = CustomerAuditFindingResponse.model_validate(finding)
    resp.action_count = ac
    resp.audit_no = audit.audit_no if audit else None
    return resp


@router.delete("/findings/{cust_finding_id}")
def delete_finding(cust_finding_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == cust_finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")
    db.query(QmsCustomerAuditAction).filter(QmsCustomerAuditAction.cust_finding_id == cust_finding_id).delete()
    log_delete(db, current_user.user_id, "qms_customer_audit_finding", finding.finding_no, "고객심사 발견사항 삭제")
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

@router.get("/findings/{cust_finding_id}/actions", response_model=List[CustomerAuditActionResponse])
def list_finding_actions(
    cust_finding_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == cust_finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")

    actions = db.query(QmsCustomerAuditAction).filter(
        QmsCustomerAuditAction.cust_finding_id == cust_finding_id
    ).order_by(QmsCustomerAuditAction.cust_action_id).all()

    result = []
    for a in actions:
        resp = CustomerAuditActionResponse.model_validate(a)
        resp.finding_no = finding.finding_no
        resp.is_overdue = (
            a.target_date is not None
            and a.status not in ("COMPLETED", "VERIFIED")
            and a.target_date < date.today()
        )
        result.append(resp)
    return result


@router.post("/findings/{cust_finding_id}/actions", response_model=CustomerAuditActionResponse)
def create_action(
    cust_finding_id: int, data: CustomerAuditActionCreate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == cust_finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="발견사항을 찾을 수 없습니다")

    existing = db.query(QmsCustomerAuditAction).filter(QmsCustomerAuditAction.action_no == data.action_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"시정조치 번호 '{data.action_no}'가 이미 존재합니다")

    action = QmsCustomerAuditAction(
        cust_finding_id=cust_finding_id, action_no=data.action_no, root_cause=data.root_cause,
        containment_action=data.containment_action, corrective_action=data.corrective_action,
        preventive_action=data.preventive_action, responsible=data.responsible,
        target_date=data.target_date, status=data.status,
    )
    db.add(action)

    # 발견사항 상태를 ACTION_REQUIRED로 변경
    if finding.status == "OPEN":
        finding.status = "ACTION_REQUIRED"
        finding.updated_at = datetime.now(timezone.utc)

    log_create(db, current_user.user_id, "qms_customer_audit_action", data.action_no, "고객심사 시정조치 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(action)
    resp = CustomerAuditActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no
    resp.is_overdue = False
    return resp


@router.get("/actions", response_model=PagedResponse[CustomerAuditActionResponse])
def list_all_actions(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    overdue_only: bool = False,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsCustomerAuditAction)
    if status:
        query = query.filter(QmsCustomerAuditAction.status == status)
    if overdue_only:
        query = query.filter(
            QmsCustomerAuditAction.target_date < date.today(),
            QmsCustomerAuditAction.status.notin_(["COMPLETED", "VERIFIED"]),
        )

    total = query.count()
    actions = query.order_by(QmsCustomerAuditAction.created_at.desc()).offset((page - 1) * size).limit(size).all()

    finding_ids = list(set(a.cust_finding_id for a in actions))
    finding_map = {}
    if finding_ids:
        findings = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id.in_(finding_ids)).all()
        finding_map = {f.cust_finding_id: f.finding_no for f in findings}

    items = []
    for a in actions:
        resp = CustomerAuditActionResponse.model_validate(a)
        resp.finding_no = finding_map.get(a.cust_finding_id)
        resp.is_overdue = (
            a.target_date is not None
            and a.status not in ("COMPLETED", "VERIFIED")
            and a.target_date < date.today()
        )
        items.append(resp)

    pages_count = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages_count)


@router.get("/actions/{cust_action_id}", response_model=CustomerAuditActionResponse)
def get_action(cust_action_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    action = db.query(QmsCustomerAuditAction).filter(QmsCustomerAuditAction.cust_action_id == cust_action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == action.cust_finding_id).first()
    resp = CustomerAuditActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no if finding else None
    resp.is_overdue = (
        action.target_date is not None
        and action.status not in ("COMPLETED", "VERIFIED")
        and action.target_date < date.today()
    )
    return resp


@router.put("/actions/{cust_action_id}", response_model=CustomerAuditActionResponse)
def update_action(
    cust_action_id: int, data: CustomerAuditActionUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    action = db.query(QmsCustomerAuditAction).filter(QmsCustomerAuditAction.cust_action_id == cust_action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(action, key)
        setattr(action, key, value)
        log_update(db, current_user.user_id, "qms_customer_audit_action", action.action_no, key, old_value, value)

    action.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(action)
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == action.cust_finding_id).first()
    resp = CustomerAuditActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no if finding else None
    resp.is_overdue = (
        action.target_date is not None
        and action.status not in ("COMPLETED", "VERIFIED")
        and action.target_date < date.today()
    )
    return resp


@router.delete("/actions/{cust_action_id}")
def delete_action(cust_action_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    action = db.query(QmsCustomerAuditAction).filter(QmsCustomerAuditAction.cust_action_id == cust_action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_customer_audit_action", action.action_no, "고객심사 시정조치 삭제")
    db.delete(action)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "시정조치가 삭제되었습니다"}


@router.put("/actions/{cust_action_id}/verify", response_model=CustomerAuditActionResponse)
def verify_action(
    cust_action_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """고객심사 시정조치 검증"""
    action = db.query(QmsCustomerAuditAction).filter(QmsCustomerAuditAction.cust_action_id == cust_action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="시정조치를 찾을 수 없습니다")

    if action.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="완료 상태인 시정조치만 검증할 수 있습니다")

    action.status = "VERIFIED"
    action.verified_by = current_user.user_id
    action.verified_date = date.today()
    action.updated_at = datetime.now(timezone.utc)

    # 해당 발견사항의 모든 시정조치가 VERIFIED이면 발견사항도 VERIFIED로 변경
    finding = db.query(QmsCustomerAuditFinding).filter(QmsCustomerAuditFinding.cust_finding_id == action.cust_finding_id).first()
    if finding:
        all_actions = db.query(QmsCustomerAuditAction).filter(
            QmsCustomerAuditAction.cust_finding_id == action.cust_finding_id,
            QmsCustomerAuditAction.cust_action_id != cust_action_id,
        ).all()
        all_verified = all(a.status == "VERIFIED" for a in all_actions)
        if all_verified:
            finding.status = "VERIFIED"
            finding.updated_at = datetime.now(timezone.utc)

    log_update(db, current_user.user_id, "qms_customer_audit_action", action.action_no, "status", "COMPLETED", "VERIFIED")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(action)
    resp = CustomerAuditActionResponse.model_validate(action)
    resp.finding_no = finding.finding_no if finding else None
    resp.is_overdue = False
    return resp


# ============================================================
# 연간 요약
# ============================================================

@router.get("/summary/{audit_year}", response_model=CustomerAuditSummaryResponse)
def customer_audit_summary(
    audit_year: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    audits = db.query(QmsCustomerAudit).filter(
        extract("year", QmsCustomerAudit.audit_date) == audit_year
    ).all()

    total_audits = len(audits)
    pass_count = sum(1 for a in audits if a.result == "PASS")
    conditional_count = sum(1 for a in audits if a.result == "CONDITIONAL")
    fail_count = sum(1 for a in audits if a.result == "FAIL")

    audit_ids = [a.cust_audit_id for a in audits]
    findings = []
    if audit_ids:
        findings = db.query(QmsCustomerAuditFinding).filter(
            QmsCustomerAuditFinding.cust_audit_id.in_(audit_ids)
        ).all()

    total_findings = len(findings)
    major_nc = sum(1 for f in findings if f.finding_type == "MAJOR_NC")
    minor_nc = sum(1 for f in findings if f.finding_type == "MINOR_NC")
    observation = sum(1 for f in findings if f.finding_type == "OBSERVATION")

    finding_ids = [f.cust_finding_id for f in findings]
    actions = []
    if finding_ids:
        actions = db.query(QmsCustomerAuditAction).filter(
            QmsCustomerAuditAction.cust_finding_id.in_(finding_ids)
        ).all()

    total_actions = len(actions)
    completed_actions = sum(1 for a in actions if a.status in ("COMPLETED", "VERIFIED"))
    overdue_actions = sum(
        1 for a in actions
        if a.target_date and a.status not in ("COMPLETED", "VERIFIED") and a.target_date < date.today()
    )

    return CustomerAuditSummaryResponse(
        audit_year=audit_year,
        total_audits=total_audits,
        pass_count=pass_count,
        conditional_count=conditional_count,
        fail_count=fail_count,
        total_findings=total_findings,
        major_nc_count=major_nc,
        minor_nc_count=minor_nc,
        observation_count=observation,
        total_actions=total_actions,
        completed_actions=completed_actions,
        overdue_actions=overdue_actions,
    )
