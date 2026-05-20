"""
MSA (측정시스템분석) API 라우터
- MSA 연구 CRUD
- 측정 데이터 입력
- GR&R 계산
"""

from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import get_db, get_current_user
from core.audit import log_create, log_update, log_delete
from models.existing import SysUser, Product
from models.iatf import QmsMsaStudy, QmsMsaMeasurement
from schemas.msa import (
    MsaStudyCreate, MsaStudyUpdate, MsaStudyResponse,
    MsaMeasurementCreate, MsaMeasurementBulkCreate, MsaMeasurementResponse,
    GrrResultResponse,
)
from schemas.common import PagedResponse
from config import settings
from services.msa_service import calculate_grr

router = APIRouter(prefix="/api/quality/msa", tags=["MSA"])


def _build_msa_response(study: QmsMsaStudy, db: Session, products_map: dict = None) -> MsaStudyResponse:
    """MsaStudy → MsaStudyResponse 변환 헬퍼"""
    if products_map is not None:
        product = products_map.get(study.product_id)
    else:
        product = db.query(Product).filter(Product.product_id == study.product_id).first()

    meas_count = db.query(func.count(QmsMsaMeasurement.measurement_id)).filter(
        QmsMsaMeasurement.msa_id == study.msa_id
    ).scalar()

    return MsaStudyResponse(
        msa_id=study.msa_id,
        msa_no=study.msa_no,
        product_id=study.product_id,
        spec_id=study.spec_id,
        study_type=study.study_type,
        gage_name=study.gage_name,
        gage_id=study.gage_id,
        num_operators=study.num_operators,
        num_parts=study.num_parts,
        num_trials=study.num_trials,
        tolerance=study.tolerance,
        result_grr_pct=study.result_grr_pct,
        result_ndc=study.result_ndc,
        judgment=study.judgment,
        created_at=study.created_at,
        updated_at=study.updated_at,
        product_name=product.product_name if product else None,
        measurement_count=meas_count,
    )


# ── MSA 연구 ──

@router.get("/", response_model=PagedResponse[MsaStudyResponse])
def list_msa_studies(
    page: int = Query(1, ge=1),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    product_id: Optional[str] = None,
    study_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """MSA 연구 목록 조회"""
    query = db.query(QmsMsaStudy)
    if product_id:
        query = query.filter(QmsMsaStudy.product_id == product_id)
    if study_type:
        query = query.filter(QmsMsaStudy.study_type == study_type)

    total = query.count()
    studies = query.order_by(QmsMsaStudy.created_at.desc()).offset((page - 1) * size).limit(size).all()

    # Batch load related data
    product_ids = list(set(s.product_id for s in studies if s.product_id))
    products_map = {}
    if product_ids:
        products = db.query(Product).filter(Product.product_id.in_(product_ids)).all()
        products_map = {p.product_id: p for p in products}

    msa_ids = [s.msa_id for s in studies]
    meas_counts = {}
    if msa_ids:
        counts = db.query(QmsMsaMeasurement.msa_id, func.count(QmsMsaMeasurement.measurement_id)).filter(
            QmsMsaMeasurement.msa_id.in_(msa_ids)
        ).group_by(QmsMsaMeasurement.msa_id).all()
        meas_counts = {msa_id: cnt for msa_id, cnt in counts}

    items = []
    for s in studies:
        product = products_map.get(s.product_id)
        items.append(MsaStudyResponse(
            msa_id=s.msa_id,
            msa_no=s.msa_no,
            product_id=s.product_id,
            spec_id=s.spec_id,
            study_type=s.study_type,
            gage_name=s.gage_name,
            gage_id=s.gage_id,
            num_operators=s.num_operators,
            num_parts=s.num_parts,
            num_trials=s.num_trials,
            tolerance=s.tolerance,
            result_grr_pct=s.result_grr_pct,
            result_ndc=s.result_ndc,
            judgment=s.judgment,
            created_at=s.created_at,
            updated_at=s.updated_at,
            product_name=product.product_name if product else None,
            measurement_count=meas_counts.get(s.msa_id, 0),
        ))

    pages = (total + size - 1) // size
    return PagedResponse(items=items, total=total, page=page, size=size, pages=pages)


@router.post("/", response_model=MsaStudyResponse)
def create_msa_study(
    data: MsaStudyCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """MSA 연구 생성"""
    existing = db.query(QmsMsaStudy).filter(QmsMsaStudy.msa_no == data.msa_no).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"MSA 번호 '{data.msa_no}'가 이미 존재합니다")

    study = QmsMsaStudy(
        msa_no=data.msa_no,
        product_id=data.product_id,
        spec_id=data.spec_id,
        study_type=data.study_type,
        gage_name=data.gage_name,
        gage_id=data.gage_id,
        num_operators=data.num_operators,
        num_parts=data.num_parts,
        num_trials=data.num_trials,
        tolerance=data.tolerance,
    )
    db.add(study)
    log_create(db, current_user.user_id, "qms_msa_study", data.msa_no, "MSA 연구 생성")
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(study)

    return _build_msa_response(study, db)


@router.get("/{msa_id}", response_model=MsaStudyResponse)
def get_msa_study(
    msa_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """MSA 연구 상세 조회"""
    study = db.query(QmsMsaStudy).filter(QmsMsaStudy.msa_id == msa_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA 연구를 찾을 수 없습니다")

    return _build_msa_response(study, db)


@router.put("/{msa_id}", response_model=MsaStudyResponse)
def update_msa_study(
    msa_id: int,
    data: MsaStudyUpdate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """MSA 연구 수정"""
    study = db.query(QmsMsaStudy).filter(QmsMsaStudy.msa_id == msa_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA 연구를 찾을 수 없습니다")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(study, key)
        setattr(study, key, value)
        log_update(db, current_user.user_id, "qms_msa_study", study.msa_no, key, old_value, value)

    study.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    db.refresh(study)

    return _build_msa_response(study, db)


@router.delete("/{msa_id}")
def delete_msa_study(
    msa_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """MSA 연구 삭제"""
    study = db.query(QmsMsaStudy).filter(QmsMsaStudy.msa_id == msa_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA 연구를 찾을 수 없습니다")

    db.query(QmsMsaMeasurement).filter(QmsMsaMeasurement.msa_id == msa_id).delete()
    log_delete(db, current_user.user_id, "qms_msa_study", study.msa_no, "MSA 연구 삭제")
    db.delete(study)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    return {"message": "MSA 연구가 삭제되었습니다"}


# ── 측정 데이터 ──

@router.get("/{msa_id}/measurements", response_model=List[MsaMeasurementResponse])
def list_measurements(
    msa_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """MSA 측정 데이터 목록 조회"""
    measurements = db.query(QmsMsaMeasurement).filter(
        QmsMsaMeasurement.msa_id == msa_id
    ).order_by(
        QmsMsaMeasurement.operator_name,
        QmsMsaMeasurement.part_no,
        QmsMsaMeasurement.trial_no,
    ).all()
    return [MsaMeasurementResponse.model_validate(m) for m in measurements]


@router.post("/{msa_id}/measurements", response_model=List[MsaMeasurementResponse])
def add_measurements(
    msa_id: int,
    data: MsaMeasurementBulkCreate,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """MSA 측정 데이터 일괄 입력"""
    study = db.query(QmsMsaStudy).filter(QmsMsaStudy.msa_id == msa_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA 연구를 찾을 수 없습니다")

    created = []
    for m in data.measurements:
        measurement = QmsMsaMeasurement(
            msa_id=msa_id,
            operator_name=m.operator_name,
            part_no=m.part_no,
            trial_no=m.trial_no,
            measured_value=m.measured_value,
        )
        db.add(measurement)
        created.append(measurement)

    log_create(db, current_user.user_id, "qms_msa_measurement", str(msa_id),
               f"측정 데이터 {len(data.measurements)}건 입력")
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")
    for m in created:
        db.refresh(m)

    return [MsaMeasurementResponse.model_validate(m) for m in created]


# ── GR&R 계산 ──

@router.get("/{msa_id}/calculate", response_model=GrrResultResponse)
def calculate_msa(
    msa_id: int,
    db: Session = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """ANOVA 기반 GR&R 계산"""
    study = db.query(QmsMsaStudy).filter(QmsMsaStudy.msa_id == msa_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="MSA 연구를 찾을 수 없습니다")

    # 측정 데이터 조회
    measurements = db.query(QmsMsaMeasurement).filter(
        QmsMsaMeasurement.msa_id == msa_id
    ).all()

    expected_count = study.num_operators * study.num_parts * study.num_trials
    if len(measurements) < expected_count:
        raise HTTPException(
            status_code=400,
            detail=f"측정 데이터 부족: {len(measurements)}/{expected_count}건"
        )

    # GR&R 계산
    meas_data = [
        {
            "operator_name": m.operator_name,
            "part_no": m.part_no,
            "trial_no": m.trial_no,
            "measured_value": m.measured_value,
        }
        for m in measurements
    ]

    result = calculate_grr(
        measurements=meas_data,
        num_operators=study.num_operators,
        num_parts=study.num_parts,
        num_trials=study.num_trials,
        tolerance=study.tolerance,
    )

    # 결과를 MSA 연구에 저장
    study.result_grr_pct = result["grr_pct"]
    study.result_ndc = result["ndc"]
    study.judgment = result["judgment"]
    study.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터 저장 중 오류가 발생했습니다")

    return GrrResultResponse(
        msa_id=msa_id,
        ev=result["ev"],
        av=result["av"],
        grr=result["grr"],
        pv=result["pv"],
        tv=result["tv"],
        grr_pct=result["grr_pct"],
        ndc=result["ndc"],
        ev_pct=result["ev_pct"],
        av_pct=result["av_pct"],
        pv_pct=result["pv_pct"],
        judgment=result["judgment"],
    )
