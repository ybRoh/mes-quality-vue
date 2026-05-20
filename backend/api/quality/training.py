"""
교육/자격관리 API 라우터
- 교육과정, 교육이수, 자격, 역량매트릭스, 자격심사 CRUD
- 재교육 알림, 만료예정, Gap 분석
"""

import logging
from datetime import datetime, timezone, date, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user, require_role
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser
from models.iatf import (
    QmsTrainingCourse, QmsTrainingRecord, QmsQualification,
    QmsCompetencyMatrix, QmsQualAudit,
)
from schemas.training import (
    TrainingCourseCreate, TrainingCourseUpdate, TrainingCourseResponse,
    TrainingRecordCreate, TrainingRecordBulkCreate, TrainingRecordUpdate, TrainingRecordResponse,
    QualificationCreate, QualificationUpdate, QualificationResponse,
    CompetencyMatrixCreate, CompetencyMatrixUpdate, CompetencyMatrixResponse,
    GapAnalysisResponse,
    QualAuditCreate, QualAuditUpdate, QualAuditResponse,
)
from schemas.common import PagedResponse
from config import settings
from api.quality.utils import escape_like

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality/training", tags=["교육/자격관리"])


# ============================================================
# 교육과정 마스터
# ============================================================

@router.get("/courses", response_model=PagedResponse[TrainingCourseResponse])
def list_courses(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    category: Optional[str] = None,
    training_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsTrainingCourse)
    if category:
        query = query.filter(QmsTrainingCourse.category == category)
    if training_type:
        query = query.filter(QmsTrainingCourse.training_type == training_type)
    if is_active is not None:
        query = query.filter(QmsTrainingCourse.is_active == is_active)

    total = query.count()
    courses = query.order_by(QmsTrainingCourse.course_no).offset((page - 1) * size).limit(size).all()

    course_ids = [c.course_id for c in courses]
    record_counts = {}
    if course_ids:
        rc = db.query(QmsTrainingRecord.course_id, func.count(QmsTrainingRecord.record_id)).filter(
            QmsTrainingRecord.course_id.in_(course_ids)
        ).group_by(QmsTrainingRecord.course_id).all()
        record_counts = {cid: cnt for cid, cnt in rc}

    items = []
    for c in courses:
        resp = TrainingCourseResponse.model_validate(c)
        resp.record_count = record_counts.get(c.course_id, 0)
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/courses", response_model=TrainingCourseResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_course(
    data: TrainingCourseCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_no == data.course_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"교육과정 번호 '{data.course_no}'가 이미 존재합니다")

    course = QmsTrainingCourse(
        course_no=data.course_no, course_name=data.course_name, category=data.category,
        duration_hours=data.duration_hours, training_type=data.training_type,
        recurrence_months=data.recurrence_months, is_active=data.is_active,
    )
    db.add(course)
    log_create(db, current_user.user_id, "qms_training_course", data.course_no, "교육과정 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(course)
    resp = TrainingCourseResponse.model_validate(course)
    resp.record_count = 0
    return resp


@router.get("/courses/{course_id}", response_model=TrainingCourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    course = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="교육과정을 찾을 수 없습니다")
    rc = db.query(func.count(QmsTrainingRecord.record_id)).filter(
        QmsTrainingRecord.course_id == course_id
    ).scalar()
    resp = TrainingCourseResponse.model_validate(course)
    resp.record_count = rc
    return resp


@router.put("/courses/{course_id}", response_model=TrainingCourseResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_course(
    course_id: int, data: TrainingCourseUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    course = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="교육과정을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(course, key)
        setattr(course, key, value)
        log_update(db, current_user.user_id, "qms_training_course", course.course_no, key, old_value, value)

    course.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(course)
    rc = db.query(func.count(QmsTrainingRecord.record_id)).filter(
        QmsTrainingRecord.course_id == course_id
    ).scalar()
    resp = TrainingCourseResponse.model_validate(course)
    resp.record_count = rc
    return resp


@router.delete("/courses/{course_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    course = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="교육과정을 찾을 수 없습니다")
    db.query(QmsTrainingRecord).filter(QmsTrainingRecord.course_id == course_id).delete()
    log_delete(db, current_user.user_id, "qms_training_course", course.course_no, "교육과정 삭제")
    db.delete(course)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "교육과정이 삭제되었습니다"}


# ============================================================
# 교육이수 기록
# ============================================================

@router.get("/records", response_model=PagedResponse[TrainingRecordResponse])
def list_records(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    course_id: Optional[int] = None,
    trainee_id: Optional[str] = None,
    result: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsTrainingRecord)
    if course_id:
        query = query.filter(QmsTrainingRecord.course_id == course_id)
    if trainee_id:
        query = query.filter(QmsTrainingRecord.trainee_id == trainee_id)
    if result:
        query = query.filter(QmsTrainingRecord.result == result)

    total = query.count()
    records = query.order_by(QmsTrainingRecord.training_date.desc()).offset((page - 1) * size).limit(size).all()

    # batch load course info
    c_ids = list(set(r.course_id for r in records))
    course_map = {}
    if c_ids:
        courses = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id.in_(c_ids)).all()
        course_map = {c.course_id: c for c in courses}

    items = []
    for r in records:
        resp = TrainingRecordResponse.model_validate(r)
        course = course_map.get(r.course_id)
        resp.course_name = course.course_name if course else None
        resp.course_no = course.course_no if course else None
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/records", response_model=TrainingRecordResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_record(
    data: TrainingRecordCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    course = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="교육과정을 찾을 수 없습니다")

    # 재교육 예정일 자동 계산
    next_due = data.next_due_date
    if not next_due and course.recurrence_months:
        next_due = data.training_date + timedelta(days=course.recurrence_months * 30)

    record = QmsTrainingRecord(
        course_id=data.course_id, trainee_id=data.trainee_id, training_date=data.training_date,
        score=data.score, result=data.result, next_due_date=next_due,
    )
    db.add(record)
    log_create(db, current_user.user_id, "qms_training_record", str(data.course_id),
               f"교육이수 기록: {data.trainee_id}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(record)
    resp = TrainingRecordResponse.model_validate(record)
    resp.course_name = course.course_name
    resp.course_no = course.course_no
    return resp


@router.post("/records/bulk", response_model=List[TrainingRecordResponse], dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def bulk_create_records(
    data: TrainingRecordBulkCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """교육이수 일괄 등록"""
    course = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id == data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="교육과정을 찾을 수 없습니다")

    next_due = None
    if course.recurrence_months:
        next_due = data.training_date + timedelta(days=course.recurrence_months * 30)

    records = []
    for tid in data.trainee_ids:
        record = QmsTrainingRecord(
            course_id=data.course_id, trainee_id=tid, training_date=data.training_date,
            score=data.score, result=data.result, next_due_date=next_due,
        )
        db.add(record)
        records.append(record)

    log_create(db, current_user.user_id, "qms_training_record", str(data.course_id),
               f"일괄 교육이수 등록: {len(data.trainee_ids)}명")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")

    result = []
    for r in records:
        db.refresh(r)
        resp = TrainingRecordResponse.model_validate(r)
        resp.course_name = course.course_name
        resp.course_no = course.course_no
        result.append(resp)
    return result


@router.put("/records/{record_id}", response_model=TrainingRecordResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_record(
    record_id: int, data: TrainingRecordUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    record = db.query(QmsTrainingRecord).filter(QmsTrainingRecord.record_id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="교육이수 기록을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(record, key)
        setattr(record, key, value)
        log_update(db, current_user.user_id, "qms_training_record", str(record_id), key, old_value, value)

    record.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(record)
    course = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id == record.course_id).first()
    resp = TrainingRecordResponse.model_validate(record)
    resp.course_name = course.course_name if course else None
    resp.course_no = course.course_no if course else None
    return resp


@router.delete("/records/{record_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_record(record_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    record = db.query(QmsTrainingRecord).filter(QmsTrainingRecord.record_id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="교육이수 기록을 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_training_record", str(record_id), "교육이수 기록 삭제")
    db.delete(record)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "교육이수 기록이 삭제되었습니다"}


@router.get("/records/due-soon", response_model=PagedResponse[TrainingRecordResponse])
def due_soon_records(
    days: int = Query(90, ge=1),
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """재교육 예정 알림 (기본 90일 이내)"""
    cutoff = date.today() + timedelta(days=days)
    query = db.query(QmsTrainingRecord).filter(
        QmsTrainingRecord.next_due_date <= cutoff,
        QmsTrainingRecord.next_due_date >= date.today(),
    ).order_by(QmsTrainingRecord.next_due_date)

    total = query.count()
    records = query.offset((page - 1) * size).limit(size).all()

    c_ids = list(set(r.course_id for r in records))
    course_map = {}
    if c_ids:
        courses = db.query(QmsTrainingCourse).filter(QmsTrainingCourse.course_id.in_(c_ids)).all()
        course_map = {c.course_id: c for c in courses}

    items = []
    for r in records:
        resp = TrainingRecordResponse.model_validate(r)
        course = course_map.get(r.course_id)
        resp.course_name = course.course_name if course else None
        resp.course_no = course.course_no if course else None
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


# ============================================================
# 자격/인증
# ============================================================

@router.get("/qualifications", response_model=PagedResponse[QualificationResponse])
def list_qualifications(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    qual_type: Optional[str] = None,
    holder_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsQualification)
    if qual_type:
        query = query.filter(QmsQualification.qual_type == qual_type)
    if holder_id:
        query = query.filter(QmsQualification.holder_id == holder_id)
    if status:
        query = query.filter(QmsQualification.status == status)

    total = query.count()
    quals = query.order_by(QmsQualification.created_at.desc()).offset((page - 1) * size).limit(size).all()

    qual_ids = [q.qual_id for q in quals]
    audit_counts = {}
    if qual_ids:
        ac = db.query(QmsQualAudit.qual_id, func.count(QmsQualAudit.qual_audit_id)).filter(
            QmsQualAudit.qual_id.in_(qual_ids)
        ).group_by(QmsQualAudit.qual_id).all()
        audit_counts = {qid: cnt for qid, cnt in ac}

    items = []
    for q in quals:
        resp = QualificationResponse.model_validate(q)
        resp.audit_count = audit_counts.get(q.qual_id, 0)
        if q.expiry_date:
            resp.days_until_expiry = (q.expiry_date - date.today()).days
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/qualifications", response_model=QualificationResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_qualification(
    data: QualificationCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    qual = QmsQualification(
        qual_type=data.qual_type, qual_name=data.qual_name, holder_id=data.holder_id,
        issuing_body=data.issuing_body, certificate_no=data.certificate_no,
        issue_date=data.issue_date, expiry_date=data.expiry_date, status=data.status,
    )
    db.add(qual)
    log_create(db, current_user.user_id, "qms_qualification", data.qual_name,
               f"자격 등록: {data.holder_id}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(qual)
    resp = QualificationResponse.model_validate(qual)
    resp.audit_count = 0
    if qual.expiry_date:
        resp.days_until_expiry = (qual.expiry_date - date.today()).days
    return resp


@router.get("/qualifications/{qual_id}", response_model=QualificationResponse)
def get_qualification(qual_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    qual = db.query(QmsQualification).filter(QmsQualification.qual_id == qual_id).first()
    if not qual:
        raise HTTPException(status_code=404, detail="자격을 찾을 수 없습니다")
    ac = db.query(func.count(QmsQualAudit.qual_audit_id)).filter(QmsQualAudit.qual_id == qual_id).scalar()
    resp = QualificationResponse.model_validate(qual)
    resp.audit_count = ac
    if qual.expiry_date:
        resp.days_until_expiry = (qual.expiry_date - date.today()).days
    return resp


@router.put("/qualifications/{qual_id}", response_model=QualificationResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_qualification(
    qual_id: int, data: QualificationUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    qual = db.query(QmsQualification).filter(QmsQualification.qual_id == qual_id).first()
    if not qual:
        raise HTTPException(status_code=404, detail="자격을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(qual, key)
        setattr(qual, key, value)
        log_update(db, current_user.user_id, "qms_qualification", str(qual_id), key, old_value, value)

    qual.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(qual)
    ac = db.query(func.count(QmsQualAudit.qual_audit_id)).filter(QmsQualAudit.qual_id == qual_id).scalar()
    resp = QualificationResponse.model_validate(qual)
    resp.audit_count = ac
    if qual.expiry_date:
        resp.days_until_expiry = (qual.expiry_date - date.today()).days
    return resp


@router.delete("/qualifications/{qual_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_qualification(qual_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    qual = db.query(QmsQualification).filter(QmsQualification.qual_id == qual_id).first()
    if not qual:
        raise HTTPException(status_code=404, detail="자격을 찾을 수 없습니다")
    db.query(QmsQualAudit).filter(QmsQualAudit.qual_id == qual_id).delete()
    log_delete(db, current_user.user_id, "qms_qualification", str(qual_id), "자격 삭제")
    db.delete(qual)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "자격이 삭제되었습니다"}


@router.get("/qualifications/expiring", response_model=PagedResponse[QualificationResponse])
def expiring_qualifications(
    days: int = Query(90, ge=1),
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """만료 예정 자격 (기본 90일 이내)"""
    cutoff = date.today() + timedelta(days=days)
    query = db.query(QmsQualification).filter(
        QmsQualification.expiry_date <= cutoff,
        QmsQualification.expiry_date >= date.today(),
        QmsQualification.status == "ACTIVE",
    ).order_by(QmsQualification.expiry_date)

    total = query.count()
    quals = query.offset((page - 1) * size).limit(size).all()

    items = []
    for q in quals:
        resp = QualificationResponse.model_validate(q)
        resp.days_until_expiry = (q.expiry_date - date.today()).days
        resp.audit_count = 0
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


# ============================================================
# 역량 매트릭스
# ============================================================

@router.get("/competency", response_model=PagedResponse[CompetencyMatrixResponse])
def list_competency(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    employee_id: Optional[str] = None,
    skill_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsCompetencyMatrix)
    if employee_id:
        query = query.filter(QmsCompetencyMatrix.employee_id == employee_id)
    if skill_name:
        query = query.filter(QmsCompetencyMatrix.skill_name.ilike(f"%{escape_like(skill_name)}%"))

    total = query.count()
    items = query.order_by(QmsCompetencyMatrix.employee_id, QmsCompetencyMatrix.skill_name).offset(
        (page - 1) * size
    ).limit(size).all()

    pages = (total + size - 1) // size
    return PagedResponse(
        items=[CompetencyMatrixResponse.model_validate(m) for m in items],
        total=total, page=page, size=size, pages=pages,
    )


@router.post("/competency", response_model=CompetencyMatrixResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_competency(
    data: CompetencyMatrixCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    existing = db.query(QmsCompetencyMatrix).filter(
        QmsCompetencyMatrix.employee_id == data.employee_id,
        QmsCompetencyMatrix.skill_name == data.skill_name,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 동일한 직원-스킬 조합이 존재합니다")

    gap = data.required_level - data.current_level
    matrix = QmsCompetencyMatrix(
        employee_id=data.employee_id, skill_name=data.skill_name,
        required_level=data.required_level, current_level=data.current_level,
        gap=gap, evaluation_date=data.evaluation_date, evaluator=data.evaluator,
    )
    db.add(matrix)
    log_create(db, current_user.user_id, "qms_competency_matrix", data.employee_id,
               f"역량 등록: {data.skill_name}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(matrix)
    return CompetencyMatrixResponse.model_validate(matrix)


@router.put("/competency/{matrix_id}", response_model=CompetencyMatrixResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_competency(
    matrix_id: int, data: CompetencyMatrixUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    matrix = db.query(QmsCompetencyMatrix).filter(QmsCompetencyMatrix.matrix_id == matrix_id).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="역량 데이터를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(matrix, key)
        setattr(matrix, key, value)
        log_update(db, current_user.user_id, "qms_competency_matrix", str(matrix_id), key, old_value, value)

    # gap 재계산
    matrix.gap = matrix.required_level - matrix.current_level
    matrix.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(matrix)
    return CompetencyMatrixResponse.model_validate(matrix)


@router.delete("/competency/{matrix_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_competency(matrix_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    matrix = db.query(QmsCompetencyMatrix).filter(QmsCompetencyMatrix.matrix_id == matrix_id).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="역량 데이터를 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_competency_matrix", str(matrix_id), "역량 데이터 삭제")
    db.delete(matrix)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "역량 데이터가 삭제되었습니다"}


@router.get("/competency/gap-analysis", response_model=PagedResponse[GapAnalysisResponse])
def gap_analysis(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """직원별 Gap 분석"""
    # Load all competency matrix rows in a single query and group in Python
    all_rows = db.query(QmsCompetencyMatrix).all()
    from collections import defaultdict
    grouped = defaultdict(list)
    for row in all_rows:
        grouped[row.employee_id].append(row)

    all_results = []
    for emp_id in sorted(grouped.keys()):
        rows = grouped[emp_id]
        total_skills = len(rows)
        gaps = [r.gap or 0 for r in rows]
        avg_gap = sum(gaps) / total_skills if total_skills else 0
        max_gap = max(gaps) if gaps else 0
        skills_with_gap = sum(1 for g in gaps if g > 0)
        skills_met = sum(1 for g in gaps if g <= 0)

        all_results.append(GapAnalysisResponse(
            employee_id=emp_id,
            total_skills=total_skills,
            avg_gap=round(avg_gap, 1),
            max_gap=max_gap,
            skills_with_gap=skills_with_gap,
            skills_met=skills_met,
        ))

    total = len(all_results)
    items = all_results[(page - 1) * size : page * size]
    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


# ============================================================
# 자격심사 기록
# ============================================================

@router.get("/qual-audits", response_model=PagedResponse[QualAuditResponse])
def list_qual_audits(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    qual_id: Optional[int] = None,
    result_filter: Optional[str] = Query(None, alias="result"),
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    query = db.query(QmsQualAudit)
    if qual_id:
        query = query.filter(QmsQualAudit.qual_id == qual_id)
    if result_filter:
        query = query.filter(QmsQualAudit.result == result_filter)

    total = query.count()
    audits = query.order_by(QmsQualAudit.audit_date.desc()).offset((page - 1) * size).limit(size).all()

    q_ids = list(set(a.qual_id for a in audits))
    qual_map = {}
    if q_ids:
        quals = db.query(QmsQualification).filter(QmsQualification.qual_id.in_(q_ids)).all()
        qual_map = {q.qual_id: q for q in quals}

    items = []
    for a in audits:
        resp = QualAuditResponse.model_validate(a)
        qual = qual_map.get(a.qual_id)
        resp.qual_name = qual.qual_name if qual else None
        resp.holder_id = qual.holder_id if qual else None
        items.append(resp)

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/qual-audits", response_model=QualAuditResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def create_qual_audit(
    data: QualAuditCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    qual = db.query(QmsQualification).filter(QmsQualification.qual_id == data.qual_id).first()
    if not qual:
        raise HTTPException(status_code=404, detail="자격을 찾을 수 없습니다")

    audit = QmsQualAudit(
        qual_id=data.qual_id, audit_date=data.audit_date, auditor=data.auditor or current_user.user_id,
        result=data.result, score=data.score, next_audit_date=data.next_audit_date,
        remarks=data.remarks,
    )
    db.add(audit)
    log_create(db, current_user.user_id, "qms_qual_audit", str(data.qual_id), "자격심사 기록 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(audit)
    resp = QualAuditResponse.model_validate(audit)
    resp.qual_name = qual.qual_name
    resp.holder_id = qual.holder_id
    return resp


@router.put("/qual-audits/{qual_audit_id}", response_model=QualAuditResponse, dependencies=[Depends(require_role("ADMIN", "MANAGER", "QA_ENGINEER"))])
def update_qual_audit(
    qual_audit_id: int, data: QualAuditUpdate,
    db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user),
):
    audit = db.query(QmsQualAudit).filter(QmsQualAudit.qual_audit_id == qual_audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="자격심사 기록을 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(audit, key)
        setattr(audit, key, value)
        log_update(db, current_user.user_id, "qms_qual_audit", str(qual_audit_id), key, old_value, value)

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(audit)
    qual = db.query(QmsQualification).filter(QmsQualification.qual_id == audit.qual_id).first()
    resp = QualAuditResponse.model_validate(audit)
    resp.qual_name = qual.qual_name if qual else None
    resp.holder_id = qual.holder_id if qual else None
    return resp


@router.delete("/qual-audits/{qual_audit_id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
def delete_qual_audit(qual_audit_id: int, db: Session = Depends(get_db), current_user: SysUser = Depends(get_current_user)):
    audit = db.query(QmsQualAudit).filter(QmsQualAudit.qual_audit_id == qual_audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="자격심사 기록을 찾을 수 없습니다")
    log_delete(db, current_user.user_id, "qms_qual_audit", str(qual_audit_id), "자격심사 기록 삭제")
    db.delete(audit)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed")
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "자격심사 기록이 삭제되었습니다"}
