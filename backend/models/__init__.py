"""
QMS 모델 패키지
- 기존 테이블 매핑 (ExistingBase)
- 신규 IATF 16949 테이블 (QmsBase)
"""

# 베이스 클래스
from models.base import ExistingBase, QmsBase

# 열거형
from models.enums import (
    FmeaStatus, CpType, MsaStudyType, MsaJudgment,
    PpapStatus, ApqpPhase, ApqpStatus, ActionPriority,
    CharacteristicClass,
)

# 기존 테이블 매핑
from models.existing import (
    Factory, Line, Machine, MachineSpecMaster, MachineSpec,
    Product, Material, BOM, Customer, Supplier, Worker, Mold, Tool,
    CodeMaster, SysUser, ProcessItemMaster,
    WorkOrder, Production, ProductionDetail, NgDetail,
    InspectionSpec, Inspection, InspectionValue,
    Claim, SortingHistory, LotTrace,
    PmPlan, PmHistory, DowntimeRecord,
    MaterialReceive, Inventory, Shipment,
    ChangeHistory, AuditLog, LoginLog,
    ShipmentInspection, ShipmentInspValue,
    MaterialInspection, MaterialInspValue,
)

# 신규 IATF 테이블
from models.iatf import (
    QmsFmea, QmsFmeaItem,
    QmsControlPlan, QmsControlPlanItem,
    QmsMsaStudy, QmsMsaMeasurement,
    QmsPpap, QmsPpapElement,
    QmsApqpProject, QmsApqpPhase, QmsApqpDeliverable,
)
