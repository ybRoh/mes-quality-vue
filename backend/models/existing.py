"""
기존 MES 테이블 읽기 전용 ORM 매핑
- ExistingBase 사용 (절대 create_all 하지 않음)
- 관계(relationship) 정의 없음 (FK 자동생성 방지)
- 기존 mes-streamlit 앱의 38개 테이블 전체 매핑
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, DateTime,
    PrimaryKeyConstraint,
)
from models.base import ExistingBase


# ============================================================
# 1. 마스터 데이터
# ============================================================

class Factory(ExistingBase):
    """공장"""
    __tablename__ = "factory"

    factory_id = Column(Text, primary_key=True)
    factory_name = Column(Text, nullable=False)
    address = Column(Text)
    is_active = Column(Integer, default=1)


class Line(ExistingBase):
    """생산라인"""
    __tablename__ = "line"

    line_id = Column(Text, primary_key=True)
    factory_id = Column(Text)
    line_name = Column(Text, nullable=False)
    process_type = Column(Text, nullable=False)
    is_active = Column(Integer, default=1)


class Machine(ExistingBase):
    """설비"""
    __tablename__ = "machine"

    machine_id = Column(Text, primary_key=True)
    line_id = Column(Text)
    machine_name = Column(Text, nullable=False)
    process_type = Column(Text, nullable=False)
    maker = Column(Text)
    model = Column(Text)
    serial_no = Column(Text)
    install_date = Column(Date)
    is_active = Column(Integer, default=1)


class MachineSpecMaster(ExistingBase):
    """설비 스펙 항목 정의"""
    __tablename__ = "machine_spec_master"

    spec_code = Column(Text, primary_key=True)
    process_type = Column(Text, nullable=False)
    spec_name = Column(Text, nullable=False)
    spec_type = Column(Text, default="NUMBER")
    unit = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Integer, default=1)


class MachineSpec(ExistingBase):
    """설비별 실제 스펙 값"""
    __tablename__ = "machine_spec"

    machine_spec_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Text)
    spec_code = Column(Text)
    spec_value = Column(Text, nullable=False)


class Product(ExistingBase):
    """품번 마스터"""
    __tablename__ = "product"

    product_id = Column(Text, primary_key=True)
    product_name = Column(Text, nullable=False)
    customer_id = Column(Text)
    customer_part_no = Column(Text)
    process_type = Column(Text, nullable=False)
    material_type = Column(Text)
    cavity = Column(Integer)
    cycle_time = Column(Float)
    unit_weight = Column(Float)
    drawing_no = Column(Text)
    is_active = Column(Integer, default=1)


class Material(ExistingBase):
    """원자재 마스터"""
    __tablename__ = "material"

    material_id = Column(Text, primary_key=True)
    material_name = Column(Text, nullable=False)
    material_type = Column(Text)
    supplier_id = Column(Text)
    unit = Column(Text, default="KG")
    safety_stock = Column(Float, default=0)
    is_active = Column(Integer, default=1)


class BOM(ExistingBase):
    """BOM (원자재 -> 완제품)"""
    __tablename__ = "bom"

    bom_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Text)
    material_id = Column(Text)
    qty_per = Column(Float, nullable=False)
    loss_rate = Column(Float, default=0)
    unit = Column(Text, default="EA")


class Customer(ExistingBase):
    """거래선 (납품처)"""
    __tablename__ = "customer"

    customer_id = Column(Text, primary_key=True)
    customer_name = Column(Text, nullable=False)
    customer_type = Column(Text)
    contact_name = Column(Text)
    contact_phone = Column(Text)
    is_active = Column(Integer, default=1)


class Supplier(ExistingBase):
    """공급처"""
    __tablename__ = "supplier"

    supplier_id = Column(Text, primary_key=True)
    supplier_name = Column(Text, nullable=False)
    contact_name = Column(Text)
    contact_phone = Column(Text)
    is_active = Column(Integer, default=1)


class Worker(ExistingBase):
    """작업자"""
    __tablename__ = "worker"

    worker_id = Column(Text, primary_key=True)
    worker_name = Column(Text, nullable=False)
    department = Column(Text)
    shift = Column(Text)
    skill_level = Column(Text)
    phone = Column(Text)
    is_active = Column(Integer, default=1)


class Mold(ExistingBase):
    """금형"""
    __tablename__ = "mold"

    mold_id = Column(Text, primary_key=True)
    mold_name = Column(Text, nullable=False)
    mold_type = Column(Text)
    product_id = Column(Text)
    total_shots = Column(Integer, default=0)
    max_shots = Column(Integer)
    pm_cycle_shots = Column(Integer)
    last_pm_date = Column(Date)
    last_pm_shots = Column(Integer, default=0)
    cleaning_cycle_shots = Column(Integer)
    last_cleaning_shots = Column(Integer, default=0)
    last_cleaning_date = Column(Date)
    status = Column(Text, default="READY")
    location = Column(Text)
    maker = Column(Text)


class Tool(ExistingBase):
    """공구 (CNC용)"""
    __tablename__ = "tool"

    tool_id = Column(Text, primary_key=True)
    tool_name = Column(Text, nullable=False)
    tool_type = Column(Text)
    spec = Column(Text)
    max_life = Column(Integer)
    life_unit = Column(Text, default="COUNT")
    current_life = Column(Integer, default=0)
    status = Column(Text, default="NEW")


class CodeMaster(ExistingBase):
    """공통 코드"""
    __tablename__ = "code_master"

    code_group = Column(Text, nullable=False)
    code_value = Column(Text, nullable=False)
    code_name = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Integer, default=1)

    __table_args__ = (
        PrimaryKeyConstraint("code_group", "code_value"),
    )


class SysUser(ExistingBase):
    """사용자 계정"""
    __tablename__ = "sys_user"

    user_id = Column(Text, primary_key=True)
    user_name = Column(Text, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, default="WORKER")
    department = Column(Text)
    is_active = Column(Integer, default=1)


class ProcessItemMaster(ExistingBase):
    """공정별 작업일보 항목 정의"""
    __tablename__ = "process_item_master"

    item_code = Column(Text, primary_key=True)
    process_type = Column(Text, nullable=False)
    item_name = Column(Text, nullable=False)
    item_type = Column(Text, default="NUMBER")
    unit = Column(Text)
    is_required = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    select_options = Column(Text)
    is_active = Column(Integer, default=1)


# ============================================================
# 2. 생산 관리
# ============================================================

class WorkOrder(ExistingBase):
    """작업지시"""
    __tablename__ = "work_order"

    wo_id = Column(Text, primary_key=True)
    order_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    product_id = Column(Text)
    line_id = Column(Text)
    machine_id = Column(Text)
    mold_id = Column(Text)
    plan_qty = Column(Integer, nullable=False)
    actual_qty = Column(Integer, default=0)
    status = Column(Text, default="PLANNED")
    priority = Column(Integer, default=5)
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Production(ExistingBase):
    """생산실적"""
    __tablename__ = "production"

    prod_id = Column(Integer, primary_key=True, autoincrement=True)
    wo_id = Column(Text)
    lot_no = Column(Text, nullable=False)
    product_id = Column(Text)
    machine_id = Column(Text)
    mold_id = Column(Text)
    worker_id = Column(Text)
    shift = Column(Text)
    work_date = Column(Date, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    plan_qty = Column(Integer)
    good_qty = Column(Integer, default=0)
    ng_qty = Column(Integer, default=0)
    rework_qty = Column(Integer, default=0)
    cycle_time_avg = Column(Float)
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class ProductionDetail(ExistingBase):
    """생산실적 상세 (공정별 고유 데이터)"""
    __tablename__ = "production_detail"

    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    prod_id = Column(Integer)
    item_code = Column(Text)
    item_value = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class NgDetail(ExistingBase):
    """불량 상세"""
    __tablename__ = "ng_detail"

    ng_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    prod_id = Column(Integer)
    ng_type = Column(Text, nullable=False)
    ng_qty = Column(Integer, nullable=False)
    remark = Column(Text)


# ============================================================
# 3. 품질 관리
# ============================================================

class InspectionSpec(ExistingBase):
    """검사 기준"""
    __tablename__ = "inspection_spec"

    spec_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Text)
    insp_item = Column(Text, nullable=False)
    insp_type = Column(Text)
    spec_nominal = Column(Float)
    spec_usl = Column(Float)
    spec_lsl = Column(Float)
    unit = Column(Text)
    method = Column(Text)
    frequency = Column(Text)
    is_critical = Column(Integer, default=0)


class Inspection(ExistingBase):
    """검사 실적"""
    __tablename__ = "inspection"

    insp_id = Column(Integer, primary_key=True, autoincrement=True)
    lot_no = Column(Text, nullable=False)
    product_id = Column(Text)
    insp_stage = Column(Text, nullable=False)
    inspector_id = Column(Text)
    insp_date = Column(Date, nullable=False)
    insp_time = Column(DateTime)
    result = Column(Text, default="PASS")
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class InspectionValue(ExistingBase):
    """검사 측정값"""
    __tablename__ = "inspection_value"

    value_id = Column(Integer, primary_key=True, autoincrement=True)
    insp_id = Column(Integer)
    spec_id = Column(Integer)
    measured_value = Column(Float)
    judgment = Column(Text, default="OK")
    sample_no = Column(Integer, default=1)


class Claim(ExistingBase):
    """고객 클레임 (8D 프로세스)"""
    __tablename__ = "claim"

    claim_id = Column(Text, primary_key=True)
    customer_id = Column(Text)
    product_id = Column(Text)
    lot_no = Column(Text)
    claim_date = Column(Date, nullable=False)
    claim_qty = Column(Integer)
    defect_type = Column(Text)
    description = Column(Text)
    cause = Column(Text)
    countermeasure = Column(Text)
    status = Column(Text, default="OPEN")
    due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.now)

    # D1: 팀 구성
    team_members = Column(Text)

    # D2: 문제 정의
    defect_source = Column(Text)
    problem_definition = Column(Text)

    # D3: 즉각 조치
    immediate_action = Column(Text)
    immediate_action_date = Column(Date)

    # D4: 원인 분석 (4M + 5Why)
    cause_man = Column(Text)
    cause_machine = Column(Text)
    cause_material = Column(Text)
    cause_method = Column(Text)
    why1 = Column(Text)
    why2 = Column(Text)
    why3 = Column(Text)
    why4 = Column(Text)
    why5 = Column(Text)
    root_cause = Column(Text)

    # D5: 시정 조치
    corrective_action_date = Column(Date)

    # D6: 유효성 검증
    verification_result = Column(Text)
    verification_date = Column(Date)
    verification_by = Column(Text)

    # D7: 수평 전개
    deployment_targets = Column(Text)
    deployment_action = Column(Text)
    deployment_date = Column(Date)

    # D8: 완료
    close_date = Column(Date)
    close_approver = Column(Text)
    lessons_learned = Column(Text)


class SortingHistory(ExistingBase):
    """선별이력"""
    __tablename__ = "sorting_history"

    sorting_id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(Text)
    product_id = Column(Text)
    lot_no = Column(Text)
    sorting_date = Column(Date, nullable=False)
    total_qty = Column(Integer, nullable=False)
    ok_qty = Column(Integer, default=0)
    ng_qty = Column(Integer, default=0)
    rework_qty = Column(Integer, default=0)
    worker_count = Column(Integer, default=1)
    work_hours = Column(Float, default=0)
    cost_per_hour = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class LotTrace(ExistingBase):
    """LOT 추적"""
    __tablename__ = "lot_trace"

    trace_id = Column(Integer, primary_key=True, autoincrement=True)
    prod_lot_no = Column(Text, nullable=False)
    material_id = Column(Text)
    material_lot_no = Column(Text, nullable=False)
    qty_used = Column(Float)
    prod_id = Column(Integer)
    bom_id = Column(Integer)
    inventory_id = Column(Integer)
    source = Column(Text, default="AUTO")
    created_at = Column(DateTime, default=datetime.now)


# ============================================================
# 4. 설비/금형 보전
# ============================================================

class PmPlan(ExistingBase):
    """보전 계획"""
    __tablename__ = "pm_plan"

    pm_plan_id = Column(Integer, primary_key=True, autoincrement=True)
    target_type = Column(Text, nullable=False)
    target_id = Column(Text, nullable=False)
    pm_type = Column(Text)
    pm_items = Column(Text)
    cycle_days = Column(Integer)
    cycle_shots = Column(Integer)
    next_due_date = Column(Date)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)


class PmHistory(ExistingBase):
    """보전 이력"""
    __tablename__ = "pm_history"

    pm_history_id = Column(Integer, primary_key=True, autoincrement=True)
    target_type = Column(Text, nullable=False)
    target_id = Column(Text, nullable=False)
    pm_type = Column(Text)
    work_date = Column(Date, nullable=False)
    worker_name = Column(Text)
    description = Column(Text)
    parts_used = Column(Text)
    cost = Column(Float, default=0)
    downtime_hours = Column(Float, default=0)
    shots_at_pm = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class DowntimeRecord(ExistingBase):
    """설비 비가동 이력"""
    __tablename__ = "downtime_record"

    downtime_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Text, nullable=False)
    downtime_reason = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    downtime_hours = Column(Float, default=0)
    description = Column(Text)
    action_taken = Column(Text)
    worker_name = Column(Text)
    is_resolved = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


# ============================================================
# 5. 자재/재고
# ============================================================

class MaterialReceive(ExistingBase):
    """자재 입고"""
    __tablename__ = "material_receive"

    receive_id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(Text)
    supplier_id = Column(Text)
    receive_date = Column(Date, nullable=False)
    lot_no = Column(Text, nullable=False)
    qty = Column(Float, nullable=False)
    unit = Column(Text)
    insp_result = Column(Text, default="PENDING")
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Inventory(ExistingBase):
    """재고 현황"""
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(Text, nullable=False)
    item_id = Column(Text, nullable=False)
    lot_no = Column(Text)
    location = Column(Text)
    qty = Column(Float, nullable=False)
    unit = Column(Text)
    updated_at = Column(DateTime, default=datetime.now)


class Shipment(ExistingBase):
    """출하"""
    __tablename__ = "shipment"

    shipment_id = Column(Text, primary_key=True)
    customer_id = Column(Text)
    ship_date = Column(Date, nullable=False)
    product_id = Column(Text)
    lot_no = Column(Text, nullable=False)
    qty = Column(Integer, nullable=False)
    delivery_no = Column(Text)
    invoice_no = Column(Text)
    status = Column(Text, default="READY")
    created_at = Column(DateTime, default=datetime.now)


# ============================================================
# 6. 공통/시스템
# ============================================================

class ChangeHistory(ExistingBase):
    """4M 변경 이력"""
    __tablename__ = "change_history"

    change_id = Column(Integer, primary_key=True, autoincrement=True)
    change_date = Column(Date, nullable=False)
    change_type = Column(Text, nullable=False)
    target = Column(Text)
    before_value = Column(Text)
    after_value = Column(Text)
    reason = Column(Text)
    approver = Column(Text)
    product_id = Column(Text)
    line_id = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class AuditLog(ExistingBase):
    """감사 추적"""
    __tablename__ = "audit_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    user_id = Column(Text)
    action = Column(Text, nullable=False)
    table_name = Column(Text, nullable=False)
    record_id = Column(Text)
    field_name = Column(Text)
    old_value = Column(Text)
    new_value = Column(Text)
    description = Column(Text)


class LoginLog(ExistingBase):
    """접속 로그"""
    __tablename__ = "login_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50))
    action = Column(String(20))
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.now)
    detail = Column(Text)


class ShipmentInspection(ExistingBase):
    """출하검사"""
    __tablename__ = "shipment_inspection"

    ship_insp_id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(Text)
    product_id = Column(Text)
    inspector_id = Column(Text)
    insp_date = Column(Date, nullable=False)
    result = Column(Text, default="PENDING")
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class ShipmentInspValue(ExistingBase):
    """출하검사 측정값"""
    __tablename__ = "shipment_insp_value"

    value_id = Column(Integer, primary_key=True, autoincrement=True)
    ship_insp_id = Column(Integer)
    spec_id = Column(Integer)
    measured_value = Column(Float)
    judgment = Column(Text, default="OK")
    sample_no = Column(Integer, default=1)


class MaterialInspection(ExistingBase):
    """수입검사"""
    __tablename__ = "material_inspection"

    mat_insp_id = Column(Integer, primary_key=True, autoincrement=True)
    receive_id = Column(Integer)
    inspector_id = Column(Text)
    insp_date = Column(Date, nullable=False)
    result = Column(Text, default="PENDING")
    remark = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class MaterialInspValue(ExistingBase):
    """수입검사 측정값"""
    __tablename__ = "material_insp_value"

    value_id = Column(Integer, primary_key=True, autoincrement=True)
    mat_insp_id = Column(Integer)
    insp_item = Column(Text, nullable=False)
    spec_value = Column(Text)
    measured_value = Column(Text)
    judgment = Column(Text, default="OK")
