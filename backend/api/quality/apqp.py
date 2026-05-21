"""
APQP (사전품질계획) API 라우터
- APQP 프로젝트 CRUD
- 5단계 게이트 리뷰
- Gantt 차트 데이터
"""

import logging
from datetime import datetime, date, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user, require_role
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser, Product, Customer
from models.iatf import QmsApqpProject, QmsApqpPhase, QmsApqpDeliverable
from schemas.apqp import (
    ApqpProjectCreate, ApqpProjectUpdate, ApqpProjectResponse,
    ApqpPhaseCreate, ApqpPhaseUpdate, ApqpPhaseResponse,
    ApqpDeliverableCreate, ApqpDeliverableUpdate, ApqpDeliverableResponse,
    GanttItem,
)
from schemas.common import PagedResponse
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/apqp", tags=["APQP"])

# APQP 5단계 정의
APQP_5_PHASES = [
    (1, "계획 및 정의 (Plan and Define)"),
    (2, "제품 설계 및 개발 (Product Design & Development)"),
    (3, "공정 설계 및 개발 (Process Design & Development)"),
    (4, "제품 및 공정 유효성 확인 (Product & Process Validation)"),
    (5, "양산 (Production)"),
]


# ── APQP 프로젝트 ──

@router.get("/", response_model=PagedResponse[ApqpProjectResponse])
def list_apqp_projects(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    status: Optional[str] = None,
    product_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 프로젝트 목록 조회"""
    query = db.query(QmsApqpProject)
    if status:
        query = query.filter(QmsApqpProject.status == status)
    if product_id:
        query = query.filter(QmsApqpProject.product_id == product_id)

    total = query.count()
    projects = query.order_by(QmsApqpProject.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # Batch load related data
    product_ids = list(set(p.product_id for p in projects if p.product_id))
    products_map = {}
    if product_ids:
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        products_map = {p.product_id: p for p in products}

    customer_ids = list(set(p.customer_id for p in projects if p.customer_id))
    customers_map = {}
    if customer_ids:
        custs = db.query(Customer).filter(Customer.customer_id.in_(customer_ids)).all()
        customers_map = {c.customer_id: c for c in custs}

    apqp_ids = [p.apqp_id for p in projects]
    phase_counts = {}
    if apqp_ids:
        counts = db.query(QmsApqpPhase.apqp_id, func.count(QmsApqpPhase.phase_id)).filter(
            QmsApqpPhase.apqp_id.in_(apqp_ids)
        ).group_by(QmsApqpPhase.apqp_id).all()
        phase_counts = {apqp_id: cnt for apqp_id, cnt in counts}

    items = []
    for p in projects:
        product = products_map.get(p.product_id)
        customer = customers_map.get(p.customer_id)
        items.append(ApqpProjectResponse(
            apqp_id=p.apqp_id,
            product_id=p.product_id,
            customer_id=p.customer_id,
            project_name=p.project_name,
            project_no=p.project_no,
            current_phase=p.current_phase,
            sop_date=p.sop_date,
            team_leader=p.team_leader,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
            product_name=product.product_name if product else None,
            customer_name=customer.customer_name if customer else None,
            phase_count=phase_counts.get(p.apqp_id, 0),
        ))

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=ApqpProjectResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_apqp_project(
    data: ApqpProjectCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 프로젝트 생성 (5단계 자동 초기화)"""
    if data.project_no:
        existing = db.query(QmsApqpProject).filter(QmsApqpProject.project_no == data.project_no).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"프로젝트 번호 '{data.project_no}'가 이미 존재합니다")

    project = QmsApqpProject(
        product_id=data.product_id,
        customer_id=data.customer_id,
        project_name=data.project_name,
        project_no=data.project_no,
        current_phase=data.current_phase,
        sop_date=data.sop_date,
        team_leader=data.team_leader or current_user.user_id,
        status=data.status,
    )
    db.add(project)
    db.flush()  # apqp_id 확보

    # 5단계 자동 생성
    for phase_no, phase_name in APQP_5_PHASES:
        phase = QmsApqpPhase(
            apqp_id=project.apqp_id,
            phase_no=phase_no,
            phase_name=phase_name,
            status="NOT_STARTED",
        )
        db.add(phase)

    log_create(db, current_user.user_id, "qms_apqp_project", data.project_no or str(project.apqp_id),
               "APQP 프로젝트 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(project)

    product = db.query(Product).filter(Product.product_id == project.product_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == project.customer_id).first() if project.customer_id else None

    return ApqpProjectResponse(
        apqp_id=project.apqp_id,
        product_id=project.product_id,
        customer_id=project.customer_id,
        project_name=project.project_name,
        project_no=project.project_no,
        current_phase=project.current_phase,
        sop_date=project.sop_date,
        team_leader=project.team_leader,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        product_name=product.product_name if product else None,
        customer_name=customer.customer_name if customer else None,
        phase_count=5,
    )


@router.get("/{apqp_id}", response_model=ApqpProjectResponse)
def get_apqp_project(
    apqp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 프로젝트 상세 조회"""
    project = db.query(QmsApqpProject).filter(QmsApqpProject.apqp_id == apqp_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="APQP 프로젝트를 찾을 수 없습니다")

    product = db.query(Product).filter(Product.product_id == project.product_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == project.customer_id).first() if project.customer_id else None
    phase_count = db.query(func.count(QmsApqpPhase.phase_id)).filter(
        QmsApqpPhase.apqp_id == apqp_id
    ).scalar()

    return ApqpProjectResponse(
        apqp_id=project.apqp_id,
        product_id=project.product_id,
        customer_id=project.customer_id,
        project_name=project.project_name,
        project_no=project.project_no,
        current_phase=project.current_phase,
        sop_date=project.sop_date,
        team_leader=project.team_leader,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        product_name=product.product_name if product else None,
        customer_name=customer.customer_name if customer else None,
        phase_count=phase_count,
    )


@router.put("/{apqp_id}", response_model=ApqpProjectResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_apqp_project(
    apqp_id: int,
    data: ApqpProjectUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 프로젝트 수정"""
    project = db.query(QmsApqpProject).filter(QmsApqpProject.apqp_id == apqp_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="APQP 프로젝트를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(project, key, None)
        setattr(project, key, value)
        log_update(db, current_user.user_id, "qms_apqp_project",
                   project.project_no or str(apqp_id), key, old_value, value)

    project.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(project)

    # Build response directly from already-loaded object
    product = db.query(Product).filter(Product.product_id == project.product_id).first()
    customer = db.query(Customer).filter(Customer.customer_id == project.customer_id).first() if project.customer_id else None
    phase_count = db.query(func.count(QmsApqpPhase.phase_id)).filter(
        QmsApqpPhase.apqp_id == apqp_id
    ).scalar()

    return ApqpProjectResponse(
        apqp_id=project.apqp_id,
        product_id=project.product_id,
        customer_id=project.customer_id,
        project_name=project.project_name,
        project_no=project.project_no,
        current_phase=project.current_phase,
        sop_date=project.sop_date,
        team_leader=project.team_leader,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        product_name=product.product_name if product else None,
        customer_name=customer.customer_name if customer else None,
        phase_count=phase_count,
    )


@router.delete("/{apqp_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_apqp_project(
    apqp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 프로젝트 삭제"""
    project = db.query(QmsApqpProject).filter(QmsApqpProject.apqp_id == apqp_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="APQP 프로젝트를 찾을 수 없습니다")

    # 산출물 -> 단계 -> 프로젝트 순서로 삭제
    phases = db.query(QmsApqpPhase).filter(QmsApqpPhase.apqp_id == apqp_id).all()
    for phase in phases:
        db.query(QmsApqpDeliverable).filter(QmsApqpDeliverable.phase_id == phase.phase_id).delete()
    db.query(QmsApqpPhase).filter(QmsApqpPhase.apqp_id == apqp_id).delete()

    log_delete(db, current_user.user_id, "qms_apqp_project",
               project.project_no or str(apqp_id), "APQP 프로젝트 삭제")
    db.delete(project)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "APQP 프로젝트가 삭제되었습니다"}


# ── APQP 단계 ──

@router.get("/{apqp_id}/phases", response_model=List[ApqpPhaseResponse])
def list_phases(
    apqp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 단계 목록 조회"""
    project = db.query(QmsApqpProject).filter(QmsApqpProject.apqp_id == apqp_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="APQP 프로젝트를 찾을 수 없습니다")

    phases = db.query(QmsApqpPhase).filter(
        QmsApqpPhase.apqp_id == apqp_id
    ).order_by(QmsApqpPhase.phase_no).all()

    # Batch load deliverable counts to avoid N+1
    phase_ids = [p.phase_id for p in phases]
    count_map = {}
    if phase_ids:
        counts = db.query(
            QmsApqpDeliverable.phase_id,
            func.count(QmsApqpDeliverable.deliverable_id).label("cnt")
        ).filter(QmsApqpDeliverable.phase_id.in_(phase_ids)).group_by(QmsApqpDeliverable.phase_id).all()
        count_map = {c[0]: c[1] for c in counts}

    items = []
    for phase in phases:
        del_count = count_map.get(phase.phase_id, 0)

        items.append(ApqpPhaseResponse(
            phase_id=phase.phase_id,
            apqp_id=phase.apqp_id,
            phase_no=phase.phase_no,
            phase_name=phase.phase_name,
            plan_start=phase.plan_start,
            plan_end=phase.plan_end,
            actual_start=phase.actual_start,
            actual_end=phase.actual_end,
            status=phase.status,
            gate_review=phase.gate_review,
            deliverable_count=del_count,
        ))

    return items


@router.put("/phases/{phase_id}", response_model=ApqpPhaseResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_phase(
    phase_id: int,
    data: ApqpPhaseUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 단계 수정 (게이트 리뷰 포함)"""
    phase = db.query(QmsApqpPhase).filter(QmsApqpPhase.phase_id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="APQP 단계를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(phase, key, value)

    log_update(db, current_user.user_id, "qms_apqp_phase", str(phase_id), "update", None, None, "APQP 단계 수정")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(phase)

    del_count = db.query(func.count(QmsApqpDeliverable.deliverable_id)).filter(
        QmsApqpDeliverable.phase_id == phase_id
    ).scalar()

    return ApqpPhaseResponse(
        phase_id=phase.phase_id,
        apqp_id=phase.apqp_id,
        phase_no=phase.phase_no,
        phase_name=phase.phase_name,
        plan_start=phase.plan_start,
        plan_end=phase.plan_end,
        actual_start=phase.actual_start,
        actual_end=phase.actual_end,
        status=phase.status,
        gate_review=phase.gate_review,
        deliverable_count=del_count,
    )


# ── APQP 산출물 ──

@router.get("/phases/{phase_id}/deliverables", response_model=List[ApqpDeliverableResponse])
def list_deliverables(
    phase_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 산출물 목록 조회"""
    deliverables = db.query(QmsApqpDeliverable).filter(
        QmsApqpDeliverable.phase_id == phase_id
    ).order_by(QmsApqpDeliverable.deliverable_id).all()

    return [ApqpDeliverableResponse.model_validate(d) for d in deliverables]


@router.post("/phases/{phase_id}/deliverables", response_model=ApqpDeliverableResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_deliverable(
    phase_id: int,
    data: ApqpDeliverableCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 산출물 추가"""
    phase = db.query(QmsApqpPhase).filter(QmsApqpPhase.phase_id == phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="APQP 단계를 찾을 수 없습니다")

    deliverable = QmsApqpDeliverable(
        phase_id=phase_id,
        item_name=data.item_name,
        responsible=data.responsible,
        due_date=data.due_date,
        status=data.status,
        completion_date=data.completion_date,
    )
    db.add(deliverable)
    log_create(db, current_user.user_id, "qms_apqp_deliverable", str(phase_id), f"산출물 추가: {data.item_name}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(deliverable)

    return ApqpDeliverableResponse.model_validate(deliverable)


@router.put("/deliverables/{deliverable_id}", response_model=ApqpDeliverableResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_deliverable(
    deliverable_id: int,
    data: ApqpDeliverableUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP 산출물 수정"""
    deliverable = db.query(QmsApqpDeliverable).filter(
        QmsApqpDeliverable.deliverable_id == deliverable_id
    ).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="산출물을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(deliverable, key, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(deliverable)

    return ApqpDeliverableResponse.model_validate(deliverable)


# ── Gantt 차트 데이터 ──

@router.get("/{apqp_id}/gantt", response_model=List[GanttItem])
def get_gantt_data(
    apqp_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """APQP Gantt 차트 데이터"""
    project = db.query(QmsApqpProject).filter(QmsApqpProject.apqp_id == apqp_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="APQP 프로젝트를 찾을 수 없습니다")

    phases = db.query(QmsApqpPhase).filter(
        QmsApqpPhase.apqp_id == apqp_id
    ).order_by(QmsApqpPhase.phase_no).all()

    # Batch load total and completed counts per phase to avoid N+1
    gantt_phase_ids = [p.phase_id for p in phases]
    total_count_map = {}
    completed_count_map = {}
    if gantt_phase_ids:
        total_counts = db.query(
            QmsApqpDeliverable.phase_id,
            func.count(QmsApqpDeliverable.deliverable_id).label("cnt")
        ).filter(QmsApqpDeliverable.phase_id.in_(gantt_phase_ids)).group_by(QmsApqpDeliverable.phase_id).all()
        total_count_map = {c[0]: c[1] for c in total_counts}

        completed_counts = db.query(
            QmsApqpDeliverable.phase_id,
            func.count(QmsApqpDeliverable.deliverable_id).label("cnt")
        ).filter(
            QmsApqpDeliverable.phase_id.in_(gantt_phase_ids),
            QmsApqpDeliverable.status == "COMPLETED",
        ).group_by(QmsApqpDeliverable.phase_id).all()
        completed_count_map = {c[0]: c[1] for c in completed_counts}

    items = []
    for phase in phases:
        # 진행률 계산 (산출물 기준)
        total_del = total_count_map.get(phase.phase_id, 0)
        completed_del = completed_count_map.get(phase.phase_id, 0)

        progress = round(completed_del / total_del * 100, 1) if total_del > 0 else 0.0
        if phase.status == "COMPLETED":
            progress = 100.0

        items.append(GanttItem(
            phase_no=phase.phase_no,
            phase_name=phase.phase_name,
            plan_start=phase.plan_start,
            plan_end=phase.plan_end,
            actual_start=phase.actual_start,
            actual_end=phase.actual_end,
            status=phase.status,
            progress_pct=progress,
        ))

    return items
