"""
SPC (통계적 공정관리) API 라우터
- 관리도 (Xbar-R/S chart)
- 공정능력 (Cp/Cpk/Pp/Ppk)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.existing import InspectionSpec, InspectionValue, Inspection
from services.spc_service import calculate_xbar_r_chart, calculate_capability

router = APIRouter(prefix="/api/quality/spc", tags=["SPC"])


@router.get("/control-chart/{spec_id}")
def get_control_chart(
    spec_id: int,
    n: int = Query(25, description="최근 N개 데이터"),
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
    n: int = Query(25, description="최근 N개 데이터"),
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
