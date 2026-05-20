"""
성과지표관리 API 라우터
- KPI 정의/데이터 CRUD, 대시보드
- 공정 모니터링 CRUD
- 리스크/이슈 CRUD, 리스크 매트릭스
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from api.deps import get_db, get_current_user, require_role
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser
from models.iatf import QmsKpiDefinition, QmsKpiData, QmsProcessMonitor, QmsRiskIssue
from schemas.kpi import (
    KpiDefinitionCreate, KpiDefinitionUpdate, KpiDefinitionResponse,
    KpiDataCreate, KpiDataResponse,
    KpiDashboardItem,
    ProcessMonitorCreate, ProcessMonitorUpdate, ProcessMonitorResponse,
    RiskIssueCreate, RiskIssueUpdate, RiskIssueResponse,
)
from schemas.common import PagedResponse
from config import settings
from api.quality.utils import escape_like

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/kpi", tags=["성과지표관리"])


# ── KPI 상태 자동 계산 ──

def _calc_kpi_status(actual, target, direction, yellow_threshold, red_threshold):
    """KPI 실적값을 기반으로 GREEN/YELLOW/RED 상태 자동 계산"""
    if target is None:
        return "GREEN"
    if direction == "HIGHER":
        if red_threshold is not None and actual <= red_threshold:
            return "RED"
        if yellow_threshold is not None and actual <= yellow_threshold:
            return "YELLOW"
        return "GREEN"
    else:  # LOWER
        if red_threshold is not None and actual >= red_threshold:
            return "RED"
        if yellow_threshold is not None and actual >= yellow_threshold:
            return "YELLOW"
        return "GREEN"


# ============================================================
# KPI 정의 (Definitions)
# ============================================================

@router.get("/definitions", response_model=PagedResponse[KpiDefinitionResponse])
def list_definitions(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsKpiDefinition)
    if category:
        query = query.filter(QmsKpiDefinition.category == category)
    if is_active is not None:
        query = query.filter(QmsKpiDefinition.is_active == is_active)

    total = query.count()
    definitions = query.order_by(QmsKpiDefinition.kpi_no).offset((page - 1) * size).limit(size).all()

    # Batch load latest data for each KPI
    kpi_ids = [d.kpi_id for d in definitions]
    latest_map = {}
    if kpi_ids:
        # Subquery to get the max data_id (latest record) per kpi_id
        sub = db.query(
            QmsKpiData.kpi_id,
            func.max(QmsKpiData.data_id).label("max_id"),
        ).filter(QmsKpiData.kpi_id.in_(kpi_ids)).group_by(QmsKpiData.kpi_id).subquery()

        latest_rows = db.query(QmsKpiData).join(
            sub, QmsKpiData.data_id == sub.c.max_id
        ).all()
        for row in latest_rows:
            latest_map[row.kpi_id] = row

    items = []
    for d in definitions:
        resp = KpiDefinitionResponse.model_validate(d)
        latest = latest_map.get(d.kpi_id)
        if latest:
            resp.latest_value = latest.actual_value
            resp.latest_status = latest.status
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/definitions", response_model=KpiDefinitionResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_definition(
    data: KpiDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsKpiDefinition).filter(QmsKpiDefinition.kpi_no == data.kpi_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"KPI 번호 '{data.kpi_no}'가 이미 존재합니다")

    kpi = QmsKpiDefinition(
        kpi_no=data.kpi_no, kpi_name=data.kpi_name, process_name=data.process_name,
        category=data.category, unit=data.unit, target_value=data.target_value,
        target_direction=data.target_direction, threshold_yellow=data.threshold_yellow,
        threshold_red=data.threshold_red, measurement_frequency=data.measurement_frequency,
        responsible=data.responsible, formula=data.formula, is_active=data.is_active,
    )
    db.add(kpi)
    log_create(db, current_user.user_id, "qms_kpi_definition", data.kpi_no, "KPI 정의 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(kpi)
    return KpiDefinitionResponse.model_validate(kpi)


@router.get("/definitions/{kpi_id}", response_model=KpiDefinitionResponse)
def get_definition(kpi_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    kpi = db.query(QmsKpiDefinition).filter(QmsKpiDefinition.kpi_id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI 정의를 찾을 수 없습니다")

    # Load latest data
    latest = db.query(QmsKpiData).filter(
        QmsKpiData.kpi_id == kpi_id
    ).order_by(QmsKpiData.data_id.desc()).first()

    resp = KpiDefinitionResponse.model_validate(kpi)
    if latest:
        resp.latest_value = latest.actual_value
        resp.latest_status = latest.status
    return resp


@router.put("/definitions/{kpi_id}", response_model=KpiDefinitionResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_definition(
    kpi_id: int, data: KpiDefinitionUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    kpi = db.query(QmsKpiDefinition).filter(QmsKpiDefinition.kpi_id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI 정의를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(kpi, key)
        setattr(kpi, key, value)
        log_update(db, current_user.user_id, "qms_kpi_definition", kpi.kpi_no, key, old_value, value)

    kpi.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(kpi)

    latest = db.query(QmsKpiData).filter(
        QmsKpiData.kpi_id == kpi_id
    ).order_by(QmsKpiData.data_id.desc()).first()

    resp = KpiDefinitionResponse.model_validate(kpi)
    if latest:
        resp.latest_value = latest.actual_value
        resp.latest_status = latest.status
    return resp


@router.delete("/definitions/{kpi_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_definition(kpi_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    kpi = db.query(QmsKpiDefinition).filter(QmsKpiDefinition.kpi_id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI 정의를 찾을 수 없습니다")

    # 하위 KPI 데이터 삭제
    db.query(QmsKpiData).filter(QmsKpiData.kpi_id == kpi_id).delete()

    log_delete(db, current_user.user_id, "qms_kpi_definition", kpi.kpi_no, "KPI 정의 삭제")
    db.delete(kpi)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "KPI 정의가 삭제되었습니다"}


# ============================================================
# KPI 데이터 (Data)
# ============================================================

@router.get("/definitions/{kpi_id}/data", response_model=List[KpiDataResponse])
def list_kpi_data(
    kpi_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    kpi = db.query(QmsKpiDefinition).filter(QmsKpiDefinition.kpi_id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI 정의를 찾을 수 없습니다")

    data_rows = db.query(QmsKpiData).filter(
        QmsKpiData.kpi_id == kpi_id
    ).order_by(QmsKpiData.period.desc()).all()

    result = []
    for row in data_rows:
        resp = KpiDataResponse.model_validate(row)
        resp.kpi_name = kpi.kpi_name
        result.append(resp)
    return result


@router.post("/definitions/{kpi_id}/data", response_model=KpiDataResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_kpi_data(
    kpi_id: int, data: KpiDataCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    kpi = db.query(QmsKpiDefinition).filter(QmsKpiDefinition.kpi_id == kpi_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI 정의를 찾을 수 없습니다")

    # Auto-calculate status
    status = _calc_kpi_status(
        data.actual_value, kpi.target_value, kpi.target_direction,
        kpi.threshold_yellow, kpi.threshold_red,
    )

    kpi_data = QmsKpiData(
        kpi_id=kpi_id, period=data.period, actual_value=data.actual_value,
        status=status, remarks=data.remarks, collected_by=data.collected_by,
        collected_at=datetime.now(timezone.utc),
    )
    db.add(kpi_data)
    log_create(db, current_user.user_id, "qms_kpi_data", f"{kpi.kpi_no}/{data.period}", "KPI 데이터 등록")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(kpi_data)
    resp = KpiDataResponse.model_validate(kpi_data)
    resp.kpi_name = kpi.kpi_name
    return resp


# ============================================================
# KPI 대시보드
# ============================================================

@router.get("/dashboard", response_model=List[KpiDashboardItem])
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """활성 KPI 목록 + 최신값 + 최근 6개 데이터 트렌드"""
    kpis = db.query(QmsKpiDefinition).filter(
        QmsKpiDefinition.is_active == True
    ).order_by(QmsKpiDefinition.kpi_no).all()

    kpi_ids = [k.kpi_id for k in kpis]

    # Batch load latest value per KPI
    latest_map = {}
    if kpi_ids:
        sub = db.query(
            QmsKpiData.kpi_id,
            func.max(QmsKpiData.data_id).label("max_id"),
        ).filter(QmsKpiData.kpi_id.in_(kpi_ids)).group_by(QmsKpiData.kpi_id).subquery()

        latest_rows = db.query(QmsKpiData).join(
            sub, QmsKpiData.data_id == sub.c.max_id
        ).all()
        for row in latest_rows:
            latest_map[row.kpi_id] = row

    # Batch load last 6 data points per KPI for trend
    trend_map: dict = {kid: [] for kid in kpi_ids}
    if kpi_ids:
        all_data = db.query(QmsKpiData).filter(
            QmsKpiData.kpi_id.in_(kpi_ids)
        ).order_by(QmsKpiData.kpi_id, QmsKpiData.period.desc()).all()

        # Group by kpi_id
        grouped = defaultdict(list)
        for row in all_data:
            grouped[row.kpi_id].append(row)

        for kid, rows in grouped.items():
            # Take last 6, reverse to chronological order
            last_6 = rows[:6]
            last_6.reverse()
            trend_map[kid] = [r.actual_value for r in last_6]

    result = []
    for k in kpis:
        latest = latest_map.get(k.kpi_id)
        item = KpiDashboardItem(
            kpi_id=k.kpi_id,
            kpi_no=k.kpi_no,
            kpi_name=k.kpi_name,
            category=k.category,
            unit=k.unit,
            target_value=k.target_value,
            target_direction=k.target_direction,
            latest_value=latest.actual_value if latest else None,
            latest_status=latest.status if latest else None,
            trend=trend_map.get(k.kpi_id, []),
        )
        result.append(item)
    return result


# ============================================================
# 공정 모니터링 (Process Monitor)
# ============================================================

@router.get("/monitors", response_model=PagedResponse[ProcessMonitorResponse])
def list_monitors(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    process_name: Optional[str] = None,
    monitor_type: Optional[str] = None,
    result: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsProcessMonitor)
    if process_name:
        query = query.filter(QmsProcessMonitor.process_name.ilike(f"%{escape_like(process_name)}%"))
    if monitor_type:
        query = query.filter(QmsProcessMonitor.monitor_type == monitor_type)
    if result:
        query = query.filter(QmsProcessMonitor.result == result)
    if status:
        query = query.filter(QmsProcessMonitor.status == status)

    total = query.count()
    monitors = query.order_by(QmsProcessMonitor.monitor_date.desc()).offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size

    items = [ProcessMonitorResponse.model_validate(m) for m in monitors]
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/monitors", response_model=ProcessMonitorResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_monitor(
    data: ProcessMonitorCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    monitor = QmsProcessMonitor(
        process_name=data.process_name, monitor_date=data.monitor_date,
        monitor_type=data.monitor_type, auditor=data.auditor,
        result=data.result, score=data.score, findings=data.findings,
        actions_required=data.actions_required, status=data.status,
    )
    db.add(monitor)
    log_create(db, current_user.user_id, "qms_process_monitor", data.process_name, "공정 모니터링 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(monitor)
    return ProcessMonitorResponse.model_validate(monitor)


@router.get("/monitors/{monitor_id}", response_model=ProcessMonitorResponse)
def get_monitor(monitor_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    monitor = db.query(QmsProcessMonitor).filter(QmsProcessMonitor.monitor_id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="공정 모니터링을 찾을 수 없습니다")
    return ProcessMonitorResponse.model_validate(monitor)


@router.put("/monitors/{monitor_id}", response_model=ProcessMonitorResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_monitor(
    monitor_id: int, data: ProcessMonitorUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    monitor = db.query(QmsProcessMonitor).filter(QmsProcessMonitor.monitor_id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="공정 모니터링을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(monitor, key)
        setattr(monitor, key, value)
        log_update(db, current_user.user_id, "qms_process_monitor", monitor.process_name, key, old_value, value)

    monitor.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(monitor)
    return ProcessMonitorResponse.model_validate(monitor)


@router.delete("/monitors/{monitor_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_monitor(monitor_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    monitor = db.query(QmsProcessMonitor).filter(QmsProcessMonitor.monitor_id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="공정 모니터링을 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_process_monitor", monitor.process_name, "공정 모니터링 삭제")
    db.delete(monitor)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "공정 모니터링이 삭제되었습니다"}


# ============================================================
# 리스크/이슈 (Risk/Issue)
# ============================================================

@router.get("/risks", response_model=PagedResponse[RiskIssueResponse])
def list_risks(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    issue_type: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsRiskIssue)
    if issue_type:
        query = query.filter(QmsRiskIssue.issue_type == issue_type)
    if status:
        query = query.filter(QmsRiskIssue.status == status)
    if category:
        query = query.filter(QmsRiskIssue.category.ilike(f"%{escape_like(category)}%"))

    total = query.count()
    risks = query.order_by(QmsRiskIssue.created_at.desc()).offset((page - 1) * size).limit(size).all()
    pages = (total + size - 1) // size

    items = [RiskIssueResponse.model_validate(r) for r in risks]
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/risks", response_model=RiskIssueResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_risk(
    data: RiskIssueCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsRiskIssue).filter(QmsRiskIssue.issue_no == data.issue_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"이슈 번호 '{data.issue_no}'가 이미 존재합니다")

    risk_score = data.severity * data.likelihood

    risk = QmsRiskIssue(
        issue_no=data.issue_no, issue_type=data.issue_type, category=data.category,
        process_name=data.process_name, description=data.description,
        severity=data.severity, likelihood=data.likelihood, risk_score=risk_score,
        mitigation_plan=data.mitigation_plan, responsible=data.responsible,
        target_date=data.target_date, status=data.status,
    )
    db.add(risk)
    log_create(db, current_user.user_id, "qms_risk_issue", data.issue_no, "리스크/이슈 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(risk)
    return RiskIssueResponse.model_validate(risk)


@router.get("/risks/matrix")
def get_risk_matrix(
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """5x5 리스크 매트릭스 데이터 (severity x likelihood grid with counts)"""
    risks = db.query(QmsRiskIssue).filter(
        QmsRiskIssue.issue_type == "RISK",
        QmsRiskIssue.status != "CLOSED",
    ).all()

    # Build 5x5 matrix: matrix[severity][likelihood] = count
    matrix = {}
    for s in range(1, 6):
        matrix[s] = {}
        for l in range(1, 6):
            matrix[s][l] = 0

    for r in risks:
        sev = min(max(r.severity, 1), 5)
        lik = min(max(r.likelihood, 1), 5)
        matrix[sev][lik] += 1

    return {"matrix": matrix, "total_risks": len(risks)}


@router.get("/risks/{issue_id}", response_model=RiskIssueResponse)
def get_risk(issue_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    risk = db.query(QmsRiskIssue).filter(QmsRiskIssue.issue_id == issue_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="리스크/이슈를 찾을 수 없습니다")
    return RiskIssueResponse.model_validate(risk)


@router.put("/risks/{issue_id}", response_model=RiskIssueResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_risk(
    issue_id: int, data: RiskIssueUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    risk = db.query(QmsRiskIssue).filter(QmsRiskIssue.issue_id == issue_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="리스크/이슈를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(risk, key)
        setattr(risk, key, value)
        log_update(db, current_user.user_id, "qms_risk_issue", risk.issue_no, key, old_value, value)

    # Recalculate risk_score if severity or likelihood changed
    risk.risk_score = risk.severity * risk.likelihood

    risk.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(risk)
    return RiskIssueResponse.model_validate(risk)


@router.delete("/risks/{issue_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_risk(issue_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    risk = db.query(QmsRiskIssue).filter(QmsRiskIssue.issue_id == issue_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="리스크/이슈를 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_risk_issue", risk.issue_no, "리스크/이슈 삭제")
    db.delete(risk)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "리스크/이슈가 삭제되었습니다"}
