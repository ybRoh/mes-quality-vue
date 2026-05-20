"""
QMS 테스트용 샘플 데이터 시드 스크립트
- FMEA, Control Plan, MSA, PPAP, APQP 전체 모듈 데이터 생성
- 기존 product, customer, machine, inspection_spec 테이블 참조
"""

import random
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import text

from database import SessionLocal
from models.iatf import (
    QmsApqpDeliverable,
    QmsApqpPhase,
    QmsApqpProject,
    QmsControlPlan,
    QmsControlPlanItem,
    QmsFmea,
    QmsFmeaItem,
    QmsMsaMeasurement,
    QmsMsaStudy,
    QmsPpap,
    QmsPpapElement,
)

random.seed(42)
now = datetime.now(timezone.utc)


def seed():
    db = SessionLocal()
    try:
        # 기존 QMS 데이터 삭제 (재실행 가능하도록)
        for tbl in [
            "qms_apqp_deliverable", "qms_apqp_phase", "qms_apqp_project",
            "qms_ppap_element", "qms_ppap",
            "qms_msa_measurement", "qms_msa_study",
            "qms_control_plan_item", "qms_control_plan",
            "qms_fmea_item", "qms_fmea",
        ]:
            db.execute(text(f"DELETE FROM {tbl}"))
        db.commit()

        # =============================================================
        # 1. FMEA 데이터
        # =============================================================
        fmea_data = [
            {
                "fmea_no": "FMEA-INJ-001",
                "product_id": "P-INJ-001",
                "fmea_type": "PROCESS",
                "status": "APPROVED",
                "prepared_by": "admin",
                "approved_by": "admin",
                "items": [
                    {
                        "process_step": "사출 성형",
                        "function_requirement": "규격 내 치수 충족",
                        "failure_mode": "미성형 (Short Shot)",
                        "failure_effect": "제품 기능 불량, 고객 반품",
                        "severity": 8,
                        "failure_cause": "수지 충전량 부족, 사출 압력 낮음",
                        "occurrence": 4,
                        "current_control_prevent": "사출 압력/속도 모니터링",
                        "current_control_detect": "초중종 외관검사",
                        "detection": 5,
                        "recommended_action": "사출 조건 최적화 및 모니터링 강화",
                        "responsible": "김사출",
                        "target_date": date(2025, 6, 30),
                        "action_taken": "사출 조건 파라미터 범위 재설정 완료",
                        "new_severity": 8,
                        "new_occurrence": 2,
                        "new_detection": 3,
                    },
                    {
                        "process_step": "사출 성형",
                        "function_requirement": "외관 품질 확보",
                        "failure_mode": "플래시 (Flash/Burr)",
                        "failure_effect": "외관 불량, 후공정 작업성 저하",
                        "severity": 6,
                        "failure_cause": "금형 마모, 형체력 부족",
                        "occurrence": 5,
                        "current_control_prevent": "금형 PM 주기 관리",
                        "current_control_detect": "전수 외관검사",
                        "detection": 3,
                        "recommended_action": "금형 PM 주기 단축, 형체력 점검 강화",
                        "responsible": "이사출",
                        "target_date": date(2025, 7, 15),
                        "action_taken": "금형 PM 주기 5000shot→3000shot 변경",
                        "new_severity": 6,
                        "new_occurrence": 3,
                        "new_detection": 3,
                    },
                    {
                        "process_step": "냉각",
                        "function_requirement": "치수 안정성 확보",
                        "failure_mode": "변형 (Warpage)",
                        "failure_effect": "조립 불가, 고객 라인 정지 위험",
                        "severity": 9,
                        "failure_cause": "냉각 불균일, 냉각시간 부족",
                        "occurrence": 3,
                        "current_control_prevent": "냉각수 온도/유량 관리",
                        "current_control_detect": "3차원 측정",
                        "detection": 4,
                        "recommended_action": "냉각 채널 시뮬레이션 및 금형 수정",
                        "responsible": "김사출",
                        "target_date": date(2025, 8, 1),
                    },
                    {
                        "process_step": "포장",
                        "function_requirement": "운송 중 파손 방지",
                        "failure_mode": "포장 불량",
                        "failure_effect": "운송 중 스크래치, 파손",
                        "severity": 5,
                        "failure_cause": "포장재 부적합, 적재 방법 미준수",
                        "occurrence": 2,
                        "current_control_prevent": "포장 사양서 배포",
                        "current_control_detect": "출하 전 포장 상태 확인",
                        "detection": 4,
                    },
                ],
            },
            {
                "fmea_no": "FMEA-PRS-001",
                "product_id": "P-PRS-001",
                "fmea_type": "PROCESS",
                "status": "IN_REVIEW",
                "prepared_by": "admin",
                "items": [
                    {
                        "process_step": "블랭킹",
                        "function_requirement": "소재 정밀 절단",
                        "failure_mode": "버(Burr) 과다",
                        "failure_effect": "후공정 불량, 작업자 부상 위험",
                        "severity": 7,
                        "failure_cause": "금형 클리어런스 부적합, 펀치 마모",
                        "occurrence": 4,
                        "current_control_prevent": "펀치 교체 주기 관리",
                        "current_control_detect": "초중종 버 높이 측정",
                        "detection": 4,
                        "recommended_action": "클리어런스 재설정, 자동 측정 도입",
                        "responsible": "박프레스",
                        "target_date": date(2025, 7, 1),
                    },
                    {
                        "process_step": "벤딩",
                        "function_requirement": "정확한 절곡 각도",
                        "failure_mode": "스프링백으로 각도 불량",
                        "failure_effect": "조립 불가",
                        "severity": 8,
                        "failure_cause": "소재 LOT별 항복강도 편차",
                        "occurrence": 3,
                        "current_control_prevent": "입고검사 시 인장시험",
                        "current_control_detect": "각도 게이지 검사",
                        "detection": 3,
                    },
                    {
                        "process_step": "피어싱",
                        "function_requirement": "홀 위치/크기 정확도",
                        "failure_mode": "홀 위치 편차",
                        "failure_effect": "볼트 체결 불가",
                        "severity": 9,
                        "failure_cause": "소재 피딩 오차, 파일럿 핀 마모",
                        "occurrence": 2,
                        "current_control_prevent": "파일럿 핀 마모 점검",
                        "current_control_detect": "CMM 측정",
                        "detection": 3,
                    },
                ],
            },
            {
                "fmea_no": "FMEA-CNC-001",
                "product_id": "P-CNC-001",
                "fmea_type": "PROCESS",
                "status": "DRAFT",
                "prepared_by": "admin",
                "items": [
                    {
                        "process_step": "황삭",
                        "function_requirement": "형상 가공",
                        "failure_mode": "채터마크 발생",
                        "failure_effect": "표면품질 불량, 후공정 추가",
                        "severity": 6,
                        "failure_cause": "공구 마모, 절삭조건 부적합",
                        "occurrence": 3,
                        "current_control_prevent": "공구 수명 관리",
                        "current_control_detect": "표면조도 측정",
                        "detection": 4,
                    },
                    {
                        "process_step": "정삭",
                        "function_requirement": "치수 및 표면조도 달성",
                        "failure_mode": "치수 공차 이탈",
                        "failure_effect": "조립 불가, 전수선별 필요",
                        "severity": 8,
                        "failure_cause": "열변위, 공구 보정 오류",
                        "occurrence": 3,
                        "current_control_prevent": "열변위 보정, 공구 오프셋 관리",
                        "current_control_detect": "인라인 자동측정",
                        "detection": 2,
                    },
                ],
            },
        ]

        fmea_ids = {}
        for fd in fmea_data:
            fmea = QmsFmea(
                fmea_no=fd["fmea_no"],
                product_id=fd["product_id"],
                fmea_type=fd["fmea_type"],
                status=fd["status"],
                prepared_by=fd.get("prepared_by"),
                approved_by=fd.get("approved_by"),
                created_at=now,
                updated_at=now,
            )
            db.add(fmea)
            db.flush()
            fmea_ids[fd["fmea_no"]] = fmea.fmea_id

            for item_data in fd["items"]:
                s = item_data.get("severity", 1)
                o = item_data.get("occurrence", 1)
                d = item_data.get("detection", 1)
                rpn = s * o * d
                ap = "H" if rpn >= 200 else ("M" if rpn >= 80 else "L")

                ns = item_data.get("new_severity")
                no = item_data.get("new_occurrence")
                nd = item_data.get("new_detection")
                new_rpn = (ns * no * nd) if (ns and no and nd) else None

                item = QmsFmeaItem(
                    fmea_id=fmea.fmea_id,
                    process_step=item_data["process_step"],
                    function_requirement=item_data.get("function_requirement"),
                    failure_mode=item_data["failure_mode"],
                    failure_effect=item_data.get("failure_effect"),
                    severity=s,
                    failure_cause=item_data.get("failure_cause"),
                    occurrence=o,
                    current_control_prevent=item_data.get("current_control_prevent"),
                    current_control_detect=item_data.get("current_control_detect"),
                    detection=d,
                    rpn=rpn,
                    ap=ap,
                    recommended_action=item_data.get("recommended_action"),
                    responsible=item_data.get("responsible"),
                    target_date=item_data.get("target_date"),
                    action_taken=item_data.get("action_taken"),
                    new_severity=ns,
                    new_occurrence=no,
                    new_detection=nd,
                    new_rpn=new_rpn,
                )
                db.add(item)

        db.flush()
        print(f"FMEA: {len(fmea_data)} headers, items inserted")

        # =============================================================
        # 2. Control Plan 데이터
        # =============================================================
        cp_data = [
            {
                "cp_no": "CP-INJ-001",
                "product_id": "P-INJ-001",
                "fmea_id": fmea_ids["FMEA-INJ-001"],
                "cp_type": "PRODUCTION",
                "status": "APPROVED",
                "prepared_by": "admin",
                "approved_by": "admin",
                "items": [
                    {
                        "process_no": "10",
                        "process_name": "수지 건조",
                        "machine_id": "INJ-M01",
                        "characteristic_name": "건조 온도",
                        "characteristic_class": "MAJOR",
                        "evaluation_method": "온도 센서 모니터링",
                        "sample_size": "연속",
                        "sample_frequency": "매 LOT",
                        "control_method": "X-bar R 관리도",
                        "reaction_plan": "건조기 온도 재설정, 수지 재건조",
                    },
                    {
                        "process_no": "20",
                        "process_name": "사출 성형",
                        "machine_id": "INJ-M01",
                        "characteristic_name": "주요치수 A",
                        "characteristic_class": "CTQ",
                        "spec_id": 2,
                        "evaluation_method": "마이크로미터 측정",
                        "sample_size": "5EA",
                        "sample_frequency": "매 2시간",
                        "control_method": "X-bar R 관리도, Cpk≥1.33",
                        "reaction_plan": "사출 조건 조정, 금형 점검",
                    },
                    {
                        "process_no": "20",
                        "process_name": "사출 성형",
                        "machine_id": "INJ-M01",
                        "characteristic_name": "주요치수 B",
                        "characteristic_class": "CTQ",
                        "spec_id": 3,
                        "evaluation_method": "마이크로미터 측정",
                        "sample_size": "5EA",
                        "sample_frequency": "매 2시간",
                        "control_method": "X-bar R 관리도, Cpk≥1.33",
                        "reaction_plan": "사출 조건 조정, 금형 점검",
                    },
                    {
                        "process_no": "30",
                        "process_name": "외관검사",
                        "characteristic_name": "외관 (미성형, 플래시, 변색)",
                        "characteristic_class": "MAJOR",
                        "spec_id": 1,
                        "evaluation_method": "목시검사 (한도 견본 비교)",
                        "sample_size": "전수",
                        "sample_frequency": "매 제품",
                        "control_method": "합부판정",
                        "reaction_plan": "불량품 격리, 원인 분석 후 재작업",
                    },
                    {
                        "process_no": "40",
                        "process_name": "중량 검사",
                        "machine_id": "INJ-M01",
                        "characteristic_name": "제품 중량",
                        "characteristic_class": "MINOR",
                        "spec_id": 4,
                        "evaluation_method": "전자저울 측정",
                        "sample_size": "5EA",
                        "sample_frequency": "매 4시간",
                        "control_method": "I-MR 관리도",
                        "reaction_plan": "수지 LOT 확인, 사출 조건 점검",
                    },
                ],
            },
            {
                "cp_no": "CP-PRS-001",
                "product_id": "P-PRS-001",
                "fmea_id": fmea_ids["FMEA-PRS-001"],
                "cp_type": "PRODUCTION",
                "status": "IN_REVIEW",
                "prepared_by": "admin",
                "items": [
                    {
                        "process_no": "10",
                        "process_name": "블랭킹",
                        "machine_id": "PRS-M01",
                        "characteristic_name": "블랭크 치수",
                        "characteristic_class": "CTQ",
                        "spec_id": 14,
                        "evaluation_method": "버니어 캘리퍼스",
                        "sample_size": "5EA",
                        "sample_frequency": "매 1시간",
                        "control_method": "X-bar R 관리도",
                        "reaction_plan": "금형 점검, 펀치 교체",
                    },
                    {
                        "process_no": "20",
                        "process_name": "벤딩",
                        "machine_id": "PRS-M01",
                        "characteristic_name": "벤딩 각도",
                        "characteristic_class": "CTQ",
                        "evaluation_method": "각도 게이지",
                        "sample_size": "3EA",
                        "sample_frequency": "매 2시간",
                        "control_method": "기록표",
                        "reaction_plan": "금형 조정, 스프링백 보정",
                    },
                    {
                        "process_no": "30",
                        "process_name": "버 제거",
                        "machine_id": "PRS-M01",
                        "characteristic_name": "버 높이",
                        "characteristic_class": "MAJOR",
                        "spec_id": 15,
                        "evaluation_method": "버 높이 게이지",
                        "sample_size": "5EA",
                        "sample_frequency": "매 1시간",
                        "control_method": "체크시트",
                        "reaction_plan": "디버링 재작업",
                    },
                ],
            },
        ]

        cp_ids = {}
        for cpd in cp_data:
            cp = QmsControlPlan(
                cp_no=cpd["cp_no"],
                product_id=cpd["product_id"],
                fmea_id=cpd.get("fmea_id"),
                cp_type=cpd["cp_type"],
                status=cpd["status"],
                prepared_by=cpd.get("prepared_by"),
                approved_by=cpd.get("approved_by"),
                created_at=now,
                updated_at=now,
            )
            db.add(cp)
            db.flush()
            cp_ids[cpd["cp_no"]] = cp.cp_id

            for ci in cpd["items"]:
                item = QmsControlPlanItem(
                    cp_id=cp.cp_id,
                    process_no=ci["process_no"],
                    process_name=ci["process_name"],
                    machine_id=ci.get("machine_id"),
                    characteristic_name=ci["characteristic_name"],
                    characteristic_class=ci.get("characteristic_class"),
                    spec_id=ci.get("spec_id"),
                    evaluation_method=ci.get("evaluation_method"),
                    sample_size=ci.get("sample_size"),
                    sample_frequency=ci.get("sample_frequency"),
                    control_method=ci.get("control_method"),
                    reaction_plan=ci.get("reaction_plan"),
                )
                db.add(item)

        db.flush()
        print(f"Control Plan: {len(cp_data)} headers inserted")

        # =============================================================
        # 3. MSA 데이터 (GR&R 연구)
        # =============================================================
        msa_studies = [
            {
                "msa_no": "MSA-INJ001-DIM-A",
                "product_id": "P-INJ-001",
                "spec_id": 2,  # 주요치수 A (45.0 ±0.15)
                "gage_name": "마이크로미터 #M-001",
                "gage_id": "M-001",
                "num_operators": 3,
                "num_parts": 10,
                "num_trials": 3,
                "tolerance": 0.30,  # 45.15 - 44.85
                "nominal": 45.0,
                "spread": 0.10,  # 부품 간 변동
                "ev_noise": 0.008,  # 반복성 노이즈
                "av_bias": {"김사출": -0.005, "이사출": 0.003, "W003": 0.001},
            },
            {
                "msa_no": "MSA-CNC001-DIM-A",
                "product_id": "P-CNC-001",
                "spec_id": 19,  # 치수 A (20.0 ±0.02)
                "gage_name": "다이얼게이지 #D-002",
                "gage_id": "D-002",
                "num_operators": 3,
                "num_parts": 10,
                "num_trials": 3,
                "tolerance": 0.04,  # 20.02 - 19.98
                "nominal": 20.0,
                "spread": 0.015,
                "ev_noise": 0.002,
                "av_bias": {"정CNC": -0.001, "W006": 0.002, "W007": 0.000},
            },
            {
                "msa_no": "MSA-PRS001-DIM",
                "product_id": "P-PRS-001",
                "spec_id": 14,  # 치수 (60.0 ±0.1)
                "gage_name": "버니어 캘리퍼스 #V-003",
                "gage_id": "V-003",
                "num_operators": 3,
                "num_parts": 10,
                "num_trials": 3,
                "tolerance": 0.20,  # 60.1 - 59.9
                "nominal": 60.0,
                "spread": 0.08,
                "ev_noise": 0.010,
                "av_bias": {"박프레스": 0.005, "최프레스": -0.003, "W005": 0.002},
            },
        ]

        msa_ids = {}
        for msd in msa_studies:
            msa = QmsMsaStudy(
                msa_no=msd["msa_no"],
                product_id=msd["product_id"],
                spec_id=msd["spec_id"],
                study_type="GRR",
                gage_name=msd["gage_name"],
                gage_id=msd["gage_id"],
                num_operators=msd["num_operators"],
                num_parts=msd["num_parts"],
                num_trials=msd["num_trials"],
                tolerance=msd["tolerance"],
                created_at=now,
                updated_at=now,
            )
            db.add(msa)
            db.flush()
            msa_ids[msd["msa_no"]] = msa.msa_id

            # 부품별 참값 생성
            part_values = []
            for p in range(1, msd["num_parts"] + 1):
                pv = msd["nominal"] + random.uniform(-msd["spread"] / 2, msd["spread"] / 2)
                part_values.append(pv)

            # 측정값 생성
            operators = list(msd["av_bias"].keys())
            for op in operators:
                bias = msd["av_bias"][op]
                for p_idx, pv in enumerate(part_values, 1):
                    for t in range(1, msd["num_trials"] + 1):
                        noise = random.gauss(0, msd["ev_noise"])
                        measured = round(pv + bias + noise, 4)
                        m = QmsMsaMeasurement(
                            msa_id=msa.msa_id,
                            operator_name=op,
                            part_no=p_idx,
                            trial_no=t,
                            measured_value=measured,
                        )
                        db.add(m)

        db.flush()
        print(f"MSA: {len(msa_studies)} studies with measurement data inserted")

        # =============================================================
        # 4. PPAP 데이터
        # =============================================================
        ppap_elements_18 = [
            (1, "설계 기록 (Design Records)"),
            (2, "승인된 기술변경문서 (Authorized Engineering Change Documents)"),
            (3, "고객 기술 승인 (Customer Engineering Approval)"),
            (4, "설계 FMEA (Design FMEA)"),
            (5, "공정 흐름도 (Process Flow Diagram)"),
            (6, "공정 FMEA (Process FMEA)"),
            (7, "관리계획서 (Control Plan)"),
            (8, "측정시스템분석 (MSA)"),
            (9, "치수 측정 결과 (Dimensional Results)"),
            (10, "재료/성능 시험 결과 (Material/Performance Test Results)"),
            (11, "초기 공정 연구 (Initial Process Study - SPC)"),
            (12, "공인시험실 서류 (Qualified Laboratory Documentation)"),
            (13, "외관 승인 보고서 (AAR)"),
            (14, "양산 시료 (Sample Production Parts)"),
            (15, "마스터 시료 (Master Sample)"),
            (16, "검사 보조기구 (Checking Aids)"),
            (17, "고객 고유 요구사항 (Customer-Specific Requirements)"),
            (18, "부품 제출 보증서 (PSW)"),
        ]

        ppap_data = [
            {
                "ppap_no": "PPAP-INJ-001",
                "product_id": "P-INJ-001",
                "customer_id": "C-HMC",
                "submission_level": 3,
                "reason": "신규 부품 양산 승인",
                "status": "APPROVED",
                "fmea_id": fmea_ids["FMEA-INJ-001"],
                "cp_id": cp_ids["CP-INJ-001"],
                "msa_id": msa_ids["MSA-INJ001-DIM-A"],
                "element_statuses": {
                    i: "COMPLETED" for i in range(1, 19)
                },
            },
            {
                "ppap_no": "PPAP-PRS-001",
                "product_id": "P-PRS-001",
                "customer_id": "C-HMC",
                "submission_level": 3,
                "reason": "신규 부품 양산 승인",
                "status": "IN_PROGRESS",
                "fmea_id": fmea_ids["FMEA-PRS-001"],
                "cp_id": cp_ids["CP-PRS-001"],
                "msa_id": msa_ids["MSA-PRS001-DIM"],
                "element_statuses": {
                    1: "COMPLETED", 2: "COMPLETED", 3: "NOT_STARTED",
                    4: "COMPLETED", 5: "COMPLETED", 6: "COMPLETED",
                    7: "IN_PROGRESS", 8: "COMPLETED", 9: "IN_PROGRESS",
                    10: "NOT_STARTED", 11: "IN_PROGRESS", 12: "NOT_STARTED",
                    13: "NOT_STARTED", 14: "NOT_STARTED", 15: "NOT_STARTED",
                    16: "NOT_STARTED", 17: "NOT_STARTED", 18: "NOT_STARTED",
                },
            },
            {
                "ppap_no": "PPAP-CNC-001",
                "product_id": "P-CNC-001",
                "customer_id": "C-MOBIS",
                "submission_level": 4,
                "reason": "기술 변경 (도면 Rev.B)",
                "status": "PLANNING",
                "fmea_id": fmea_ids["FMEA-CNC-001"],
                "element_statuses": {
                    1: "IN_PROGRESS", 2: "NOT_STARTED", 3: "NOT_STARTED",
                    4: "NOT_STARTED", 5: "IN_PROGRESS", 6: "IN_PROGRESS",
                    7: "NOT_STARTED", 8: "NOT_STARTED", 9: "NOT_STARTED",
                    10: "NOT_STARTED", 11: "NOT_STARTED", 12: "NOT_STARTED",
                    13: "NOT_STARTED", 14: "NOT_STARTED", 15: "NOT_STARTED",
                    16: "NOT_STARTED", 17: "NOT_STARTED", 18: "NOT_STARTED",
                },
            },
        ]

        ppap_ids = {}
        for pd in ppap_data:
            ppap = QmsPpap(
                ppap_no=pd["ppap_no"],
                product_id=pd["product_id"],
                customer_id=pd["customer_id"],
                submission_level=pd["submission_level"],
                reason=pd["reason"],
                status=pd["status"],
                fmea_id=pd.get("fmea_id"),
                cp_id=pd.get("cp_id"),
                msa_id=pd.get("msa_id"),
                created_at=now,
                updated_at=now,
            )
            db.add(ppap)
            db.flush()
            ppap_ids[pd["ppap_no"]] = ppap.ppap_id

            for eno, ename in ppap_elements_18:
                elem = QmsPpapElement(
                    ppap_id=ppap.ppap_id,
                    element_no=eno,
                    element_name=ename,
                    is_required=1 if pd["submission_level"] >= 3 or eno in (1, 5, 6, 7, 9, 18) else 0,
                    status=pd["element_statuses"].get(eno, "NOT_STARTED"),
                )
                db.add(elem)

        db.flush()
        print(f"PPAP: {len(ppap_data)} submissions with 18 elements each inserted")

        # =============================================================
        # 5. APQP 데이터
        # =============================================================
        apqp_phases_def = [
            (1, "계획 및 정의 (Plan and Define)", [
                "품질 목표 설정",
                "신뢰성 목표",
                "예비 BOM 작성",
                "예비 공정흐름도",
                "특별특성 목록 (초안)",
                "제품 보증 계획",
            ]),
            (2, "제품 설계 및 개발 (Product Design & Development)", [
                "설계 FMEA",
                "제조성 및 조립성 검토 (DFM/DFA)",
                "설계 검증 (DVP&R)",
                "도면 완성",
                "기술 사양서",
                "시작품 관리계획서",
            ]),
            (3, "공정 설계 및 개발 (Process Design & Development)", [
                "공정 흐름도",
                "공정 FMEA",
                "양산 관리계획서",
                "포장 기준서",
                "MSA 계획",
                "공정능력 연구 계획 (Cpk)",
            ]),
            (4, "제품 및 공정 유효성 확인 (Validation)", [
                "양산 시험 가동 (Run@Rate)",
                "MSA 실시",
                "초기 공정능력 연구 (Ppk)",
                "PPAP 제출",
                "양산 관리계획서 확정",
                "품질 계획 승인",
            ]),
            (5, "피드백 및 시정조치 (Feedback & Corrective Action)", [
                "산포 저감 활동",
                "고객 만족도 평가",
                "납입 및 서비스 모니터링",
                "교훈 (Lessons Learned) 정리",
            ]),
        ]

        apqp_data = [
            {
                "product_id": "P-INJ-001",
                "customer_id": "C-HMC",
                "project_name": "엔진마운트 브라켓 양산 개발",
                "project_no": "APQP-INJ-001",
                "current_phase": 4,
                "sop_date": date(2025, 9, 1),
                "team_leader": "admin",
                "status": "IN_PROGRESS",
                "phase_statuses": ["COMPLETED", "COMPLETED", "COMPLETED", "IN_PROGRESS", "NOT_STARTED"],
                "phase_dates": [
                    (date(2025, 1, 6), date(2025, 2, 28), date(2025, 1, 6), date(2025, 2, 25)),
                    (date(2025, 3, 3), date(2025, 4, 30), date(2025, 3, 3), date(2025, 4, 28)),
                    (date(2025, 5, 1), date(2025, 6, 30), date(2025, 5, 1), date(2025, 6, 27)),
                    (date(2025, 7, 1), date(2025, 8, 31), date(2025, 7, 1), None),
                    (date(2025, 9, 1), date(2025, 12, 31), None, None),
                ],
            },
            {
                "product_id": "P-CNC-001",
                "customer_id": "C-MOBIS",
                "project_name": "변속기 샤프트 Rev.B 개발",
                "project_no": "APQP-CNC-001",
                "current_phase": 2,
                "sop_date": date(2026, 1, 15),
                "team_leader": "admin",
                "status": "IN_PROGRESS",
                "phase_statuses": ["COMPLETED", "IN_PROGRESS", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"],
                "phase_dates": [
                    (date(2025, 4, 1), date(2025, 5, 31), date(2025, 4, 1), date(2025, 5, 28)),
                    (date(2025, 6, 1), date(2025, 8, 31), date(2025, 6, 2), None),
                    (date(2025, 9, 1), date(2025, 11, 30), None, None),
                    (date(2025, 12, 1), date(2026, 1, 14), None, None),
                    (date(2026, 1, 15), date(2026, 6, 30), None, None),
                ],
            },
            {
                "product_id": "P-INJ-003",
                "customer_id": "C-MOBIS",
                "project_name": "센서 하우징 신규 개발",
                "project_no": "APQP-INJ-003",
                "current_phase": 1,
                "sop_date": date(2026, 6, 1),
                "team_leader": "admin",
                "status": "NOT_STARTED",
                "phase_statuses": ["IN_PROGRESS", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED", "NOT_STARTED"],
                "phase_dates": [
                    (date(2025, 7, 1), date(2025, 9, 30), date(2025, 7, 1), None),
                    (date(2025, 10, 1), date(2026, 1, 31), None, None),
                    (date(2026, 2, 1), date(2026, 3, 31), None, None),
                    (date(2026, 4, 1), date(2026, 5, 31), None, None),
                    (date(2026, 6, 1), date(2026, 12, 31), None, None),
                ],
            },
        ]

        for apd in apqp_data:
            project = QmsApqpProject(
                product_id=apd["product_id"],
                customer_id=apd["customer_id"],
                project_name=apd["project_name"],
                project_no=apd["project_no"],
                current_phase=apd["current_phase"],
                sop_date=apd["sop_date"],
                team_leader=apd["team_leader"],
                status=apd["status"],
                created_at=now,
                updated_at=now,
            )
            db.add(project)
            db.flush()

            for i, (phase_no, phase_name, deliverable_names) in enumerate(apqp_phases_def):
                ps, pe, acs, ace = apd["phase_dates"][i]
                phase = QmsApqpPhase(
                    apqp_id=project.apqp_id,
                    phase_no=phase_no,
                    phase_name=phase_name,
                    plan_start=ps,
                    plan_end=pe,
                    actual_start=acs,
                    actual_end=ace,
                    status=apd["phase_statuses"][i],
                )
                db.add(phase)
                db.flush()

                for d_idx, d_name in enumerate(deliverable_names):
                    phase_status = apd["phase_statuses"][i]
                    if phase_status == "COMPLETED":
                        d_status = "COMPLETED"
                        d_completion = pe - timedelta(days=random.randint(1, 10))
                    elif phase_status == "IN_PROGRESS":
                        d_status = random.choice(["COMPLETED", "IN_PROGRESS", "NOT_STARTED"])
                        d_completion = (
                            date.today() - timedelta(days=random.randint(1, 20))
                            if d_status == "COMPLETED"
                            else None
                        )
                    else:
                        d_status = "NOT_STARTED"
                        d_completion = None

                    due = ps + timedelta(days=(d_idx + 1) * ((pe - ps).days // (len(deliverable_names) + 1)))
                    deliverable = QmsApqpDeliverable(
                        phase_id=phase.phase_id,
                        item_name=d_name,
                        responsible="admin",
                        due_date=due,
                        status=d_status,
                        completion_date=d_completion,
                    )
                    db.add(deliverable)

        db.flush()
        print(f"APQP: {len(apqp_data)} projects with 5 phases each inserted")

        db.commit()
        print("\n=== 샘플 데이터 입력 완료 ===")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
