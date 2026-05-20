"""
SPC (통계적 공정관리) API 라우터
- 제품/규격 목록 조회
- 관리도 (Xbar-R/S chart)
- 공정능력 (Cp/Cpk/Pp/Ppk)
"""

from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.existing import InspectionSpec, InspectionValue, Inspection, Product
from services.spc_service import calculate_xbar_r_chart, calculate_capability

router = APIRouter(prefix="/api/quality/spc", tags=["SPC"])


@router.get("/products")
def get_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """SPC 분석 가능한 제품 목록 (측정값이 있는 규격을 가진 제품)"""
    results = (
        db.query(
            Product.product_id,
            Product.product_name,
            func.count(func.distinct(InspectionSpec.spec_id)).label("spec_count"),
        )
        .join(InspectionSpec, Product.product_id == InspectionSpec.product_id)
        .join(InspectionValue, InspectionSpec.spec_id == InspectionValue.spec_id)
        .filter(InspectionValue.measured_value.isnot(None))
        .group_by(Product.product_id, Product.product_name)
        .order_by(Product.product_name)
        .all()
    )
    return [
        {"id": r.product_id, "name": r.product_name, "spec_count": r.spec_count}
        for r in results
    ]


@router.get("/specs/{product_id}")
def get_specs(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """제품의 검사 규격 목록 (수치 측정 가능한 것만)"""
    results = (
        db.query(InspectionSpec)
        .filter(
            InspectionSpec.product_id == product_id,
            InspectionSpec.spec_usl.isnot(None),
            InspectionSpec.spec_lsl.isnot(None),
        )
        .order_by(InspectionSpec.spec_id)
        .all()
    )
    return [
        {
            "id": s.spec_id,
            "name": s.insp_item,
            "usl": s.spec_usl,
            "lsl": s.spec_lsl,
            "nominal": s.spec_nominal,
        }
        for s in results
    ]


@router.get("/data")
def get_spc_data(
    spec_id: int = Query(..., description="검사 규격 ID"),
    sample_count: int = Query(25, ge=5, le=500, description="샘플 수"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """SPC 관리도 데이터 조회 (control-chart 동일)"""
    spec = db.query(InspectionSpec).filter(InspectionSpec.spec_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="검사 규격을 찾을 수 없습니다")

    results = (
        db.query(InspectionValue.measured_value, Inspection.lot_no)
        .join(Inspection, InspectionValue.insp_id == Inspection.insp_id)
        .filter(
            InspectionValue.spec_id == spec_id,
            InspectionValue.measured_value.isnot(None),
        )
        .order_by(Inspection.insp_date.desc(), InspectionValue.value_id.desc())
        .limit(sample_count)
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="측정 데이터가 없습니다")

    results.reverse()
    values = [float(r.measured_value) for r in results]
    chart_data = calculate_xbar_r_chart(values)

    return {
        "spec_id": spec_id,
        "insp_item": spec.insp_item,
        "product_id": spec.product_id,
        "values": chart_data["values"],
        "mean": chart_data["mean"],
        "ucl": chart_data["ucl"],
        "lcl": chart_data["lcl"],
        "std": chart_data["std"],
        "count": chart_data["count"],
        "usl": spec.spec_usl,
        "lsl": spec.spec_lsl,
        "nominal": spec.spec_nominal,
    }


@router.get("/control-chart/{spec_id}")
def get_control_chart(
    spec_id: int,
    n: int = Query(25, ge=5, le=500, description="최근 N개 데이터"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Xbar-R/S 관리도 데이터 조회"""
    # 검사 규격 조회
    spec = db.query(InspectionSpec).filter(InspectionSpec.spec_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="검사 규격을 찾을 수 없습니다")

    # 최근 N개 측정값 조회 (최신순 정렬 후 역순)
    results = (
        db.query(
            InspectionValue.measured_value,
            Inspection.lot_no,
        )
        .join(Inspection, InspectionValue.insp_id == Inspection.insp_id)
        .filter(
            InspectionValue.spec_id == spec_id,
            InspectionValue.measured_value.isnot(None),
        )
        .order_by(Inspection.insp_date.desc(), InspectionValue.value_id.desc())
        .limit(n)
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="측정 데이터가 없습니다")

    # 시간순 정렬
    results.reverse()
    values = [float(r.measured_value) for r in results]
    lot_nos = [r.lot_no for r in results]

    # 관리도 계산
    chart_data = calculate_xbar_r_chart(values)

    return {
        "spec_id": spec_id,
        "insp_item": spec.insp_item,
        "product_id": spec.product_id,
        "values": chart_data["values"],
        "mean": chart_data["mean"],
        "ucl": chart_data["ucl"],
        "lcl": chart_data["lcl"],
        "std": chart_data["std"],
        "count": chart_data["count"],
        "usl": spec.spec_usl,
        "lsl": spec.spec_lsl,
        "nominal": spec.spec_nominal,
        "lot_nos": lot_nos,
    }


@router.get("/capability/{spec_id}")
def get_capability(
    spec_id: int,
    n: int = Query(25, alias="sample_count", description="최근 N개 데이터"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Cp/Cpk/Pp/Ppk 공정능력 계산"""
    # 검사 규격 조회
    spec = db.query(InspectionSpec).filter(InspectionSpec.spec_id == spec_id).first()
    if not spec:
        raise HTTPException(status_code=404, detail="검사 규격을 찾을 수 없습니다")

    if spec.spec_usl is None or spec.spec_lsl is None:
        raise HTTPException(status_code=400, detail="규격 상한/하한이 설정되지 않았습니다")

    # 최근 N개 측정값 조회
    results = (
        db.query(InspectionValue.measured_value)
        .join(Inspection, InspectionValue.insp_id == Inspection.insp_id)
        .filter(
            InspectionValue.spec_id == spec_id,
            InspectionValue.measured_value.isnot(None),
        )
        .order_by(Inspection.insp_date.desc(), InspectionValue.value_id.desc())
        .limit(n)
        .all()
    )

    if len(results) < 2:
        raise HTTPException(status_code=400, detail="공정능력 계산에 최소 2개 이상의 데이터가 필요합니다")

    values = [float(r.measured_value) for r in results]

    # 공정능력 계산
    cap_data = calculate_capability(values, spec.spec_usl, spec.spec_lsl)
    if "error" in cap_data:
        raise HTTPException(status_code=400, detail=cap_data["error"])

    return {
        "spec_id": spec_id,
        "insp_item": spec.insp_item,
        "product_id": spec.product_id,
        "mean": cap_data["mean"],
        "std_within": cap_data["std_within"],
        "std_overall": cap_data["std_overall"],
        "cp": cap_data["cp"],
        "cpk": cap_data["cpk"],
        "pp": cap_data["pp"],
        "ppk": cap_data["ppk"],
        "cpu": cap_data["cpu"],
        "cpl": cap_data["cpl"],
        "count": cap_data["count"],
        "min_val": cap_data["min"],
        "max_val": cap_data["max"],
        "usl": spec.spec_usl,
        "lsl": spec.spec_lsl,
        "nominal": spec.spec_nominal,
    }
