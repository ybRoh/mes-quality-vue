"""
생산분석 서비스
- 기간별, 유형별, 설비별, 품번별 분석 SQL 쿼리 함수
"""

from datetime import date
from typing import List, Optional
from sqlalchemy import func, case, extract
from sqlalchemy.orm import Session

from models.existing import Production, Product, Machine, Customer


def get_daily_production(db: Session, target_date: date) -> List[dict]:
    """일별 생산실적 조회"""
    results = (
        db.query(
            Production.product_id,
            Product.product_name,
            Production.machine_id,
            Machine.machine_name,
            func.sum(Production.plan_qty).label("plan_qty"),
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
        )
        .outerjoin(Product, Production.product_id == Product.product_id)
        .outerjoin(Machine, Production.machine_id == Machine.machine_id)
        .filter(Production.work_date == target_date)
        .group_by(
            Production.product_id, Product.product_name,
            Production.machine_id, Machine.machine_name,
        )
        .all()
    )

    items = []
    for r in results:
        total = r.total_qty or 0
        good = r.good_qty or 0
        ng = r.ng_qty or 0
        plan = r.plan_qty or 0
        items.append({
            "product_id": r.product_id,
            "product_name": r.product_name,
            "machine_id": r.machine_id,
            "machine_name": r.machine_name,
            "plan_qty": plan,
            "good_qty": good,
            "ng_qty": ng,
            "total_qty": total,
            "ng_rate": round(ng / total * 100, 2) if total > 0 else 0.0,
            "achievement_rate": round(good / plan * 100, 2) if plan > 0 else 0.0,
        })
    return items


def get_monthly_production(db: Session, year: int, month: int) -> List[dict]:
    """월별 생산실적 (일자별 집계)"""
    results = (
        db.query(
            Production.work_date,
            func.sum(Production.plan_qty).label("plan_qty"),
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
            func.count(Production.prod_id).label("production_count"),
        )
        .filter(
            extract("year", Production.work_date) == year,
            extract("month", Production.work_date) == month,
        )
        .group_by(Production.work_date)
        .order_by(Production.work_date)
        .all()
    )

    items = []
    for r in results:
        total = r.total_qty or 0
        good = r.good_qty or 0
        ng = r.ng_qty or 0
        plan = r.plan_qty or 0
        items.append({
            "work_date": r.work_date,
            "plan_qty": plan,
            "good_qty": good,
            "ng_qty": ng,
            "total_qty": total,
            "ng_rate": round(ng / total * 100, 2) if total > 0 else 0.0,
            "achievement_rate": round(good / plan * 100, 2) if plan > 0 else 0.0,
            "production_count": r.production_count,
        })
    return items


def get_yearly_production(db: Session, year: int) -> List[dict]:
    """연별 생산실적 (월별 집계)"""
    results = (
        db.query(
            extract("month", Production.work_date).label("month"),
            func.sum(Production.plan_qty).label("plan_qty"),
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
            func.count(Production.prod_id).label("production_count"),
        )
        .filter(extract("year", Production.work_date) == year)
        .group_by(extract("month", Production.work_date))
        .order_by(extract("month", Production.work_date))
        .all()
    )

    items = []
    for r in results:
        total = r.total_qty or 0
        ng = r.ng_qty or 0
        items.append({
            "month": int(r.month),
            "plan_qty": r.plan_qty or 0,
            "good_qty": r.good_qty or 0,
            "ng_qty": ng,
            "total_qty": total,
            "ng_rate": round(ng / total * 100, 2) if total > 0 else 0.0,
            "production_count": r.production_count,
        })
    return items


def get_by_equipment(
    db: Session, from_date: date, to_date: date, machine_id: Optional[str] = None,
) -> List[dict]:
    """설비별 생산실적 분석"""
    query = (
        db.query(
            Production.machine_id,
            Machine.machine_name,
            Machine.process_type,
            func.sum(Production.plan_qty).label("plan_qty"),
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
        )
        .outerjoin(Machine, Production.machine_id == Machine.machine_id)
        .filter(Production.work_date.between(from_date, to_date))
    )
    if machine_id:
        query = query.filter(Production.machine_id == machine_id)

    results = query.group_by(
        Production.machine_id, Machine.machine_name, Machine.process_type,
    ).all()

    items = []
    for r in results:
        total = r.total_qty or 0
        good = r.good_qty or 0
        ng = r.ng_qty or 0
        plan = r.plan_qty or 0
        items.append({
            "machine_id": r.machine_id,
            "machine_name": r.machine_name,
            "process_type": r.process_type,
            "plan_qty": plan,
            "good_qty": good,
            "ng_qty": ng,
            "total_qty": total,
            "ng_rate": round(ng / total * 100, 2) if total > 0 else 0.0,
            "achievement_rate": round(good / plan * 100, 2) if plan > 0 else 0.0,
        })
    return items


def get_by_spec(
    db: Session, from_date: date, to_date: date, product_id: Optional[str] = None,
) -> List[dict]:
    """품번별 생산실적 분석"""
    query = (
        db.query(
            Production.product_id,
            Product.product_name,
            Product.process_type,
            func.sum(Production.plan_qty).label("plan_qty"),
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
        )
        .outerjoin(Product, Production.product_id == Product.product_id)
        .filter(Production.work_date.between(from_date, to_date))
    )
    if product_id:
        query = query.filter(Production.product_id == product_id)

    results = query.group_by(
        Production.product_id, Product.product_name, Product.process_type,
    ).all()

    items = []
    for r in results:
        total = r.total_qty or 0
        good = r.good_qty or 0
        ng = r.ng_qty or 0
        plan = r.plan_qty or 0
        items.append({
            "product_id": r.product_id,
            "product_name": r.product_name,
            "process_type": r.process_type,
            "plan_qty": plan,
            "good_qty": good,
            "ng_qty": ng,
            "total_qty": total,
            "ng_rate": round(ng / total * 100, 2) if total > 0 else 0.0,
            "achievement_rate": round(good / plan * 100, 2) if plan > 0 else 0.0,
        })
    return items


def get_monthly_trend(db: Session, from_date: date, to_date: date) -> List[dict]:
    """월별 추이 분석"""
    # PostgreSQL: to_char 사용
    year_month_expr = func.to_char(Production.work_date, "YYYY-MM")

    results = (
        db.query(
            year_month_expr.label("year_month"),
            func.sum(Production.plan_qty).label("plan_qty"),
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
            func.count(Production.prod_id).label("production_count"),
        )
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(year_month_expr)
        .order_by(year_month_expr)
        .all()
    )

    items = []
    for r in results:
        good = r.good_qty or 0
        ng = r.ng_qty or 0
        total = good + ng
        items.append({
            "year_month": r.year_month,
            "plan_qty": r.plan_qty or 0,
            "good_qty": good,
            "ng_qty": ng,
            "ng_rate": round(ng / total * 100, 2) if total > 0 else 0.0,
            "production_count": r.production_count,
        })
    return items


def get_production_share(db: Session, from_date: date, to_date: date) -> List[dict]:
    """제품별 생산 점유율"""
    results = (
        db.query(
            Production.product_id,
            Product.product_name,
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
        )
        .outerjoin(Product, Production.product_id == Product.product_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(Production.product_id, Product.product_name)
        .order_by(func.sum(Production.good_qty + Production.ng_qty).desc())
        .all()
    )

    grand_total = sum(r.total_qty or 0 for r in results)
    items = []
    for r in results:
        total = r.total_qty or 0
        items.append({
            "product_id": r.product_id,
            "product_name": r.product_name,
            "total_qty": total,
            "share_pct": round(total / grand_total * 100, 2) if grand_total > 0 else 0.0,
        })
    return items


def get_parts_composition(db: Session, from_date: date, to_date: date) -> List[dict]:
    """부품 구성비"""
    results = (
        db.query(
            Production.product_id,
            Product.product_name,
            Product.process_type,
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
        )
        .outerjoin(Product, Production.product_id == Product.product_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(Production.product_id, Product.product_name, Product.process_type)
        .order_by(func.sum(Production.good_qty + Production.ng_qty).desc())
        .all()
    )

    grand_total = sum(r.total_qty or 0 for r in results)
    items = []
    for r in results:
        total = r.total_qty or 0
        items.append({
            "product_id": r.product_id,
            "product_name": r.product_name,
            "process_type": r.process_type,
            "good_qty": r.good_qty or 0,
            "ng_qty": r.ng_qty or 0,
            "total_qty": total,
            "composition_pct": round(total / grand_total * 100, 2) if grand_total > 0 else 0.0,
        })
    return items


def get_by_customer(db: Session, from_date: date, to_date: date) -> List[dict]:
    """고객유형별 생산 분석"""
    results = (
        db.query(
            Customer.customer_id,
            Customer.customer_name,
            Customer.customer_type,
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
            func.sum(Production.good_qty).label("good_qty"),
            func.sum(Production.ng_qty).label("ng_qty"),
        )
        .outerjoin(Product, Production.product_id == Product.product_id)
        .outerjoin(Customer, Product.customer_id == Customer.customer_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(Customer.customer_id, Customer.customer_name, Customer.customer_type)
        .order_by(func.sum(Production.good_qty + Production.ng_qty).desc())
        .all()
    )

    grand_total = sum(r.total_qty or 0 for r in results)
    items = []
    for r in results:
        total = r.total_qty or 0
        items.append({
            "customer_id": r.customer_id,
            "customer_name": r.customer_name,
            "customer_type": r.customer_type,
            "total_qty": total,
            "good_qty": r.good_qty or 0,
            "ng_qty": r.ng_qty or 0,
            "share_pct": round(total / grand_total * 100, 2) if grand_total > 0 else 0.0,
        })
    return items


def get_equipment_capacity(db: Session, from_date: date, to_date: date) -> List[dict]:
    """설비 가동능력 분석"""
    results = (
        db.query(
            Production.machine_id,
            Machine.machine_name,
            Machine.process_type,
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
            func.avg(Production.cycle_time_avg).label("avg_cycle_time"),
        )
        .outerjoin(Machine, Production.machine_id == Machine.machine_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(Production.machine_id, Machine.machine_name, Machine.process_type)
        .all()
    )

    items = []
    for r in results:
        total = r.total_qty or 0
        avg_ct = r.avg_cycle_time
        # 가동시간 추정 (총생산량 x 평균 사이클타임 / 3600)
        operating_hours = round(total * (avg_ct or 0) / 3600, 2) if avg_ct else 0.0
        items.append({
            "machine_id": r.machine_id,
            "machine_name": r.machine_name,
            "process_type": r.process_type,
            "total_qty": total,
            "operating_hours": operating_hours,
            "capacity_rate": 0.0,  # 이론 가동능력 대비 비율 (추가 데이터 필요)
            "avg_cycle_time": round(float(avg_ct), 2) if avg_ct else None,
        })
    return items


def get_st_achievement(db: Session, from_date: date, to_date: date) -> List[dict]:
    """표준시간(ST) 달성률"""
    results = (
        db.query(
            Production.machine_id,
            Machine.machine_name,
            Production.product_id,
            Product.product_name,
            Product.cycle_time.label("std_cycle_time"),
            func.avg(Production.cycle_time_avg).label("avg_cycle_time"),
            func.count(Production.prod_id).label("production_count"),
        )
        .outerjoin(Machine, Production.machine_id == Machine.machine_id)
        .outerjoin(Product, Production.product_id == Product.product_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(
            Production.machine_id, Machine.machine_name,
            Production.product_id, Product.product_name,
            Product.cycle_time,
        )
        .all()
    )

    items = []
    for r in results:
        std_ct = r.std_cycle_time
        avg_ct = r.avg_cycle_time
        st_ach = round(std_ct / float(avg_ct) * 100, 2) if std_ct and avg_ct and float(avg_ct) > 0 else 0.0
        items.append({
            "machine_id": r.machine_id,
            "machine_name": r.machine_name,
            "product_id": r.product_id,
            "product_name": r.product_name,
            "std_cycle_time": std_ct,
            "avg_cycle_time": round(float(avg_ct), 2) if avg_ct else None,
            "st_achievement": st_ach,
            "production_count": r.production_count,
        })
    return items


def get_type_share(db: Session, from_date: date, to_date: date) -> List[dict]:
    """공정유형 점유율"""
    # 공정유형명 매핑
    process_names = {
        "INJECTION": "사출",
        "PRESS": "프레스",
        "CNC": "CNC가공",
        "POLISH": "연마",
    }

    results = (
        db.query(
            Machine.process_type,
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
            func.count(func.distinct(Production.machine_id)).label("machine_count"),
        )
        .outerjoin(Machine, Production.machine_id == Machine.machine_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(Machine.process_type)
        .order_by(func.sum(Production.good_qty + Production.ng_qty).desc())
        .all()
    )

    grand_total = sum(r.total_qty or 0 for r in results)
    items = []
    for r in results:
        total = r.total_qty or 0
        items.append({
            "process_type": r.process_type or "UNKNOWN",
            "process_name": process_names.get(r.process_type, r.process_type),
            "total_qty": total,
            "share_pct": round(total / grand_total * 100, 2) if grand_total > 0 else 0.0,
            "machine_count": r.machine_count,
        })
    return items


def get_spec_production_time(db: Session, from_date: date, to_date: date) -> List[dict]:
    """품번별 생산시간 분석"""
    results = (
        db.query(
            Production.product_id,
            Product.product_name,
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
            func.avg(Production.cycle_time_avg).label("avg_cycle_time"),
            Product.cycle_time.label("std_cycle_time"),
        )
        .outerjoin(Product, Production.product_id == Product.product_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(Production.product_id, Product.product_name, Product.cycle_time)
        .all()
    )

    items = []
    for r in results:
        total = r.total_qty or 0
        avg_ct = r.avg_cycle_time
        operating_hours = round(total * (float(avg_ct) if avg_ct else 0) / 3600, 2)
        items.append({
            "product_id": r.product_id,
            "product_name": r.product_name,
            "total_qty": total,
            "operating_hours": operating_hours,
            "avg_cycle_time": round(float(avg_ct), 2) if avg_ct else None,
            "std_cycle_time": r.std_cycle_time,
        })
    return items


def get_spec_st_achievement(db: Session, from_date: date, to_date: date) -> List[dict]:
    """품번별 ST 달성률"""
    results = (
        db.query(
            Production.product_id,
            Product.product_name,
            Product.cycle_time.label("std_cycle_time"),
            func.avg(Production.cycle_time_avg).label("avg_cycle_time"),
            func.sum(Production.good_qty + Production.ng_qty).label("total_qty"),
        )
        .outerjoin(Product, Production.product_id == Product.product_id)
        .filter(Production.work_date.between(from_date, to_date))
        .group_by(Production.product_id, Product.product_name, Product.cycle_time)
        .all()
    )

    items = []
    for r in results:
        std_ct = r.std_cycle_time
        avg_ct = r.avg_cycle_time
        st_ach = round(std_ct / float(avg_ct) * 100, 2) if std_ct and avg_ct and float(avg_ct) > 0 else 0.0
        items.append({
            "product_id": r.product_id,
            "product_name": r.product_name,
            "std_cycle_time": std_ct,
            "avg_cycle_time": round(float(avg_ct), 2) if avg_ct else None,
            "st_achievement": st_ach,
            "total_qty": r.total_qty or 0,
        })
    return items


def get_spec_detail(
    db: Session, from_date: date, to_date: date, product_id: str,
) -> List[dict]:
    """품번 상세 생산실적"""
    results = (
        db.query(
            Production.work_date,
            Production.machine_id,
            Machine.machine_name,
            Production.lot_no,
            Production.plan_qty,
            Production.good_qty,
            Production.ng_qty,
            Production.cycle_time_avg,
            Production.worker_id,
        )
        .outerjoin(Machine, Production.machine_id == Machine.machine_id)
        .filter(
            Production.work_date.between(from_date, to_date),
            Production.product_id == product_id,
        )
        .order_by(Production.work_date, Production.machine_id)
        .all()
    )

    items = []
    for r in results:
        items.append({
            "work_date": r.work_date,
            "machine_id": r.machine_id,
            "machine_name": r.machine_name,
            "lot_no": r.lot_no,
            "plan_qty": r.plan_qty or 0,
            "good_qty": r.good_qty or 0,
            "ng_qty": r.ng_qty or 0,
            "cycle_time_avg": r.cycle_time_avg,
            "worker_id": r.worker_id,
        })
    return items
