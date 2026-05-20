"""
QMS 샘플 데이터 시드 스크립트
모든 모듈에 데모용 샘플 데이터를 삽입합니다.
실행: cd backend && python3 seed_data.py
"""

from datetime import date, datetime, timezone, timedelta
from database import SessionLocal
from models.iatf import (
    QmsFmea, QmsFmeaItem,
    QmsControlPlan, QmsControlPlanItem,
    QmsMsaStudy, QmsMsaMeasurement,
    QmsPpap, QmsPpapElement,
    QmsApqpProject, QmsApqpPhase, QmsApqpDeliverable,
    QmsDocument, QmsDocumentRevision,
    QmsAuditRequirement, QmsAuditPlan, QmsAuditFinding, QmsCorrectiveAction,
    QmsTrainingCourse, QmsTrainingRecord, QmsQualification, QmsCompetencyMatrix, QmsQualAudit,
    QmsSpecification, QmsDrawingRevision, QmsSiFaq, QmsCsr,
    QmsCustomerAudit, QmsCustomerAuditFinding, QmsCustomerAuditAction,
    QmsKpiDefinition, QmsKpiData, QmsProcessMonitor, QmsRiskIssue,
)

now = datetime.now(timezone.utc)


def seed():
    db = SessionLocal()
    try:
        # ── 1. FMEA ──
        fmea1 = QmsFmea(
            fmea_no="FMEA-2026-001", product_id="P001", fmea_type="PROCESS",
            revision=1, status="APPROVED", prepared_by="김품질", approved_by="이부장",
            created_at=now, updated_at=now,
        )
        fmea2 = QmsFmea(
            fmea_no="FMEA-2026-002", product_id="P002", fmea_type="DESIGN",
            revision=1, status="DRAFT", prepared_by="박설계", approved_by=None,
            created_at=now, updated_at=now,
        )
        db.add_all([fmea1, fmea2])
        db.flush()

        fmea_items = [
            QmsFmeaItem(
                fmea_id=fmea1.fmea_id, process_step="사출 성형",
                function_requirement="외관 규격 충족", failure_mode="버(Burr) 발생",
                failure_effect="고객 클레임", severity=8, failure_cause="금형 마모",
                occurrence=4, current_control_prevent="금형 점검 주기 관리",
                current_control_detect="외관 전수검사", detection=3, rpn=96, ap="M",
                recommended_action="금형 예방보전 주기 단축", responsible="정금형",
                target_date=date(2026, 6, 30),
            ),
            QmsFmeaItem(
                fmea_id=fmea1.fmea_id, process_step="조립",
                function_requirement="체결 토크 5±0.5 Nm", failure_mode="토크 부족",
                failure_effect="체결 풀림 → 안전 사고", severity=9, failure_cause="토크렌치 교정 불량",
                occurrence=3, current_control_prevent="교정 주기 관리",
                current_control_detect="토크 모니터링", detection=4, rpn=108, ap="H",
                recommended_action="자동 토크 제어 시스템 도입", responsible="최조립",
                target_date=date(2026, 7, 15),
                action_taken="자동 토크건 도입 완료", new_severity=9, new_occurrence=2,
                new_detection=2, new_rpn=36,
            ),
            QmsFmeaItem(
                fmea_id=fmea1.fmea_id, process_step="도장",
                function_requirement="도막 두께 25~35μm", failure_mode="도막 두께 부족",
                failure_effect="내식성 저하", severity=7, failure_cause="스프레이 노즐 막힘",
                occurrence=5, current_control_prevent="노즐 청소 SOP",
                current_control_detect="도막 두께 측정", detection=3, rpn=105, ap="H",
                recommended_action="노즐 교체 주기 설정", responsible="한도장",
                target_date=date(2026, 8, 1),
            ),
            QmsFmeaItem(
                fmea_id=fmea2.fmea_id, process_step="설계 검증",
                function_requirement="내열성 150°C 이상", failure_mode="소재 변형",
                failure_effect="제품 기능 상실", severity=9, failure_cause="소재 선정 오류",
                occurrence=2, current_control_prevent="소재 DB 참조",
                current_control_detect="시뮬레이션", detection=5, rpn=90, ap="M",
                recommended_action="실물 열변형 시험 추가", responsible="박설계",
                target_date=date(2026, 9, 1),
            ),
        ]
        db.add_all(fmea_items)

        # ── 2. Control Plan ──
        cp1 = QmsControlPlan(
            cp_no="CP-2026-001", product_id="P001", fmea_id=None,
            cp_type="PRODUCTION", revision=2, status="APPROVED",
            prepared_by="김품질", approved_by="이부장",
            created_at=now, updated_at=now,
        )
        cp2 = QmsControlPlan(
            cp_no="CP-2026-002", product_id="P002", fmea_id=None,
            cp_type="PRE_LAUNCH", revision=1, status="IN_REVIEW",
            prepared_by="박설계", approved_by=None,
            created_at=now, updated_at=now,
        )
        db.add_all([cp1, cp2])
        db.flush()

        cp_items = [
            QmsControlPlanItem(
                cp_id=cp1.cp_id, process_no="10", process_name="사출 성형",
                machine_id="M001", characteristic_name="외관 (버)",
                characteristic_class="CTQ", evaluation_method="육안 검사",
                sample_size="5EA", sample_frequency="매 2시간",
                control_method="한도 견본 비교", reaction_plan="즉시 라인 정지 후 금형 점검",
            ),
            QmsControlPlanItem(
                cp_id=cp1.cp_id, process_no="20", process_name="조립",
                machine_id="M003", characteristic_name="체결 토크",
                characteristic_class="CTQ", evaluation_method="토크렌치",
                sample_size="전수", sample_frequency="매 제품",
                control_method="Xbar-R 관리도", reaction_plan="토크렌치 재교정 및 재작업",
            ),
            QmsControlPlanItem(
                cp_id=cp1.cp_id, process_no="30", process_name="도장",
                machine_id="M005", characteristic_name="도막 두께",
                characteristic_class="MAJOR", evaluation_method="도막 두께계",
                sample_size="3EA", sample_frequency="매 로트",
                control_method="규격 확인", reaction_plan="도장 조건 재설정",
            ),
        ]
        db.add_all(cp_items)

        # ── 3. MSA Study ──
        msa1 = QmsMsaStudy(
            msa_no="MSA-2026-001", product_id="P001", spec_id=None,
            study_type="GRR", gage_name="마이크로미터 #12", gage_id="GAG-012",
            num_operators=3, num_parts=10, num_trials=3, tolerance=0.05,
            result_grr_pct=8.5, result_ndc=12, judgment="ACCEPTABLE",
            created_at=now, updated_at=now,
        )
        msa2 = QmsMsaStudy(
            msa_no="MSA-2026-002", product_id="P002", spec_id=None,
            study_type="GRR", gage_name="캘리퍼스 #03", gage_id="GAG-003",
            num_operators=2, num_parts=10, num_trials=3, tolerance=0.1,
            result_grr_pct=22.3, result_ndc=4, judgment="MARGINAL",
            created_at=now, updated_at=now,
        )
        db.add_all([msa1, msa2])
        db.flush()

        import random
        random.seed(42)
        measurements = []
        operators = ["김측정", "이측정", "박측정"]
        for op_idx, op_name in enumerate(operators):
            for part in range(1, 11):
                base_val = 10.0 + part * 0.01
                for trial in range(1, 4):
                    val = base_val + random.gauss(0, 0.002) + op_idx * 0.001
                    measurements.append(QmsMsaMeasurement(
                        msa_id=msa1.msa_id, operator_name=op_name,
                        part_no=part, trial_no=trial, measured_value=round(val, 4),
                    ))
        db.add_all(measurements)

        # ── 4. PPAP ──
        ppap1 = QmsPpap(
            ppap_no="PPAP-2026-001", product_id="P001", customer_id="C001",
            submission_level=3, reason="신규 양산 승인",
            status="APPROVED", created_at=now, updated_at=now,
        )
        ppap2 = QmsPpap(
            ppap_no="PPAP-2026-002", product_id="P002", customer_id="C002",
            submission_level=3, reason="설계 변경 후 재승인",
            status="IN_PROGRESS", created_at=now, updated_at=now,
        )
        db.add_all([ppap1, ppap2])
        db.flush()

        ppap_element_names = [
            "설계 기록", "승인된 기술변경 문서", "고객 기술승인", "Design FMEA",
            "공정 흐름도", "Process FMEA", "관리계획서", "MSA",
            "치수 검사 결과", "재료/성능 시험", "초기 공정 능력 조사", "공인시험실 문서",
            "외관 승인 보고서(AAR)", "양산 시료", "마스터 샘플", "검사 보조구",
            "고객 특별요구사항", "부품 제출 보증서(PSW)",
        ]
        for ppap_obj in [ppap1, ppap2]:
            for i, name in enumerate(ppap_element_names, 1):
                st = "COMPLETED" if ppap_obj == ppap1 else ("COMPLETED" if i <= 10 else "IN_PROGRESS")
                db.add(QmsPpapElement(
                    ppap_id=ppap_obj.ppap_id, element_no=i, element_name=name,
                    is_required=1, status=st, document_ref=f"DOC-{i:02d}" if st == "COMPLETED" else None,
                ))

        # ── 5. APQP ──
        apqp1 = QmsApqpProject(
            product_id="P001", customer_id="C001", project_name="P001 신규 양산 프로젝트",
            project_no="APQP-2026-001", current_phase=4, sop_date=date(2026, 9, 1),
            team_leader="이프로", status="IN_PROGRESS",
            created_at=now, updated_at=now,
        )
        db.add(apqp1)
        db.flush()

        phase_names = [
            "계획 및 정의", "제품 설계/개발", "공정 설계/개발",
            "제품 및 공정 유효성 확인", "피드백/시정조치/지속개선",
        ]
        phases = []
        for i, pname in enumerate(phase_names, 1):
            st = "COMPLETED" if i < 4 else ("IN_PROGRESS" if i == 4 else "NOT_STARTED")
            p = QmsApqpPhase(
                apqp_id=apqp1.apqp_id, phase_no=i, phase_name=pname,
                plan_start=date(2026, i, 1), plan_end=date(2026, i + 1, 28),
                actual_start=date(2026, i, 1) if i <= 4 else None,
                actual_end=date(2026, i + 1, 20) if i < 4 else None,
                status=st,
            )
            phases.append(p)
        db.add_all(phases)
        db.flush()

        deliverables_data = [
            (phases[0].phase_id, "고객 VOC 수집", "COMPLETED"),
            (phases[0].phase_id, "품질 목표 설정", "COMPLETED"),
            (phases[1].phase_id, "Design FMEA 작성", "COMPLETED"),
            (phases[1].phase_id, "도면 발행", "COMPLETED"),
            (phases[2].phase_id, "공정 흐름도", "COMPLETED"),
            (phases[2].phase_id, "Process FMEA 작성", "COMPLETED"),
            (phases[2].phase_id, "관리계획서 작성", "COMPLETED"),
            (phases[3].phase_id, "MSA 실시", "IN_PROGRESS"),
            (phases[3].phase_id, "초기 공정 능력 조사", "IN_PROGRESS"),
            (phases[3].phase_id, "PPAP 제출", "NOT_STARTED"),
            (phases[4].phase_id, "양산 후 품질 모니터링", "NOT_STARTED"),
        ]
        for pid, item_name, st in deliverables_data:
            db.add(QmsApqpDeliverable(
                phase_id=pid, item_name=item_name, responsible="이프로",
                due_date=date(2026, 6, 30), status=st,
                completion_date=date(2026, 5, 15) if st == "COMPLETED" else None,
            ))

        # ── 6. Document ──
        docs = [
            QmsDocument(
                doc_no="QM-001", doc_type="MANUAL", title="품질 매뉴얼 (IATF 16949)",
                department="품질보증팀", revision=3, status="APPROVED",
                prepared_by="김품질", reviewed_by="이부장", approved_by="최이사",
                effective_date=date(2026, 1, 1), created_at=now, updated_at=now,
            ),
            QmsDocument(
                doc_no="QP-001", doc_type="PROCESS", title="부적합품 관리 프로세스",
                department="품질보증팀", revision=2, status="APPROVED",
                prepared_by="김품질", reviewed_by="이부장", approved_by="최이사",
                effective_date=date(2025, 6, 1), created_at=now, updated_at=now,
            ),
            QmsDocument(
                doc_no="QP-002", doc_type="PROCESS", title="시정조치 프로세스",
                department="품질보증팀", revision=1, status="APPROVED",
                prepared_by="김품질", reviewed_by="이부장", approved_by="최이사",
                effective_date=date(2025, 3, 1), created_at=now, updated_at=now,
            ),
            QmsDocument(
                doc_no="QR-001", doc_type="REGULATION", title="검사 규정",
                department="검사팀", revision=4, status="APPROVED",
                prepared_by="박검사", reviewed_by="김품질", approved_by="이부장",
                effective_date=date(2026, 2, 1), created_at=now, updated_at=now,
            ),
            QmsDocument(
                doc_no="QF-001", doc_type="FORM", title="부적합 보고서 양식",
                department="품질보증팀", revision=2, status="APPROVED",
                prepared_by="김품질", reviewed_by=None, approved_by="이부장",
                effective_date=date(2025, 9, 1), created_at=now, updated_at=now,
            ),
            QmsDocument(
                doc_no="QP-003", doc_type="PROCESS", title="내부심사 프로세스",
                department="품질보증팀", revision=1, status="DRAFT",
                prepared_by="김품질", reviewed_by=None, approved_by=None,
                effective_date=None, created_at=now, updated_at=now,
            ),
        ]
        db.add_all(docs)
        db.flush()

        db.add(QmsDocumentRevision(
            doc_id=docs[0].doc_id, revision_no=3,
            change_summary="IATF 16949:2016 SI 반영", changed_by="김품질",
            previous_status="APPROVED", new_status="APPROVED", created_at=now,
        ))

        # ── 7. Audit ──
        reqs = [
            QmsAuditRequirement(
                req_no="REQ-001", clause_ref="4.1", category="Context",
                description="조직의 이해관계자 요구사항 파악 및 모니터링",
                audit_criteria="이해관계자 목록 및 요구사항 매트릭스 확인", is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsAuditRequirement(
                req_no="REQ-002", clause_ref="7.1.5", category="자원관리",
                description="모니터링 및 측정 자원의 적합성 보장",
                audit_criteria="교정 기록 및 MSA 결과 확인", is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsAuditRequirement(
                req_no="REQ-003", clause_ref="8.5.1", category="생산",
                description="생산 및 서비스 제공의 관리",
                audit_criteria="작업표준서, 관리계획서 현장 이행 확인", is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsAuditRequirement(
                req_no="REQ-004", clause_ref="9.1.1", category="성과평가",
                description="품질 목표 모니터링 및 분석",
                audit_criteria="KPI 추이, 경영 검토 기록 확인", is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsAuditRequirement(
                req_no="REQ-005", clause_ref="10.2", category="개선",
                description="부적합 및 시정조치 관리",
                audit_criteria="부적합 보고서, 시정조치 유효성 확인", is_active=True,
                created_at=now, updated_at=now,
            ),
        ]
        db.add_all(reqs)

        plan1 = QmsAuditPlan(
            plan_no="AUD-2026-001", audit_year=2026, audit_type="INTERNAL",
            title="2026년 상반기 내부심사", scope="전 부서 IATF 16949 적합성",
            department="전사", lead_auditor="김심사",
            plan_start=date(2026, 3, 1), plan_end=date(2026, 3, 15),
            actual_start=date(2026, 3, 3), actual_end=date(2026, 3, 14),
            status="COMPLETED", created_at=now, updated_at=now,
        )
        plan2 = QmsAuditPlan(
            plan_no="AUD-2026-002", audit_year=2026, audit_type="INTERNAL",
            title="2026년 하반기 내부심사", scope="생산부, 품질부",
            department="생산/품질", lead_auditor="김심사",
            plan_start=date(2026, 9, 1), plan_end=date(2026, 9, 15),
            status="PLANNED", created_at=now, updated_at=now,
        )
        db.add_all([plan1, plan2])
        db.flush()

        f1 = QmsAuditFinding(
            plan_id=plan1.plan_id, finding_no="F-2026-001", finding_type="MINOR_NC",
            clause_ref="7.1.5", description="마이크로미터 #05 교정 기한 초과 (2개월)",
            evidence="교정 대장 확인 결과 2026-01-15 만료", status="CLOSED",
            created_at=now, updated_at=now,
        )
        f2 = QmsAuditFinding(
            plan_id=plan1.plan_id, finding_no="F-2026-002", finding_type="OBSERVATION",
            clause_ref="8.5.1", description="도장 공정 작업표준서 최신본 미게시",
            evidence="현장 게시판 Rev.1 확인, 최신은 Rev.3", status="CLOSED",
            created_at=now, updated_at=now,
        )
        f3 = QmsAuditFinding(
            plan_id=plan1.plan_id, finding_no="F-2026-003", finding_type="OFI",
            clause_ref="9.1.1", description="KPI 대시보드에 추이 그래프 추가 권고",
            evidence="현재 수치만 표시", status="VERIFIED",
            created_at=now, updated_at=now,
        )
        db.add_all([f1, f2, f3])
        db.flush()

        ca1 = QmsCorrectiveAction(
            finding_id=f1.finding_id, action_no="CA-2026-001",
            root_cause="교정 관리 대장 알림 시스템 미비",
            containment_action="해당 마이크로미터 즉시 사용 중지 및 교정 의뢰",
            corrective_action="교정 기한 30일 전 자동 알림 시스템 구축",
            preventive_action="전사 측정기 교정 관리 시스템 전산화",
            responsible="이측정", target_date=date(2026, 4, 30),
            completion_date=date(2026, 4, 15), status="VERIFIED",
            verified_by="김심사", verified_date=date(2026, 4, 20),
            created_at=now, updated_at=now,
        )
        db.add(ca1)

        # ── 8. Training ──
        courses = [
            QmsTrainingCourse(
                course_no="TR-001", course_name="IATF 16949 인식교육",
                category="품질시스템", duration_hours=8.0,
                training_type="INTERNAL", recurrence_months=12, is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsTrainingCourse(
                course_no="TR-002", course_name="내부심사원 양성과정",
                category="심사", duration_hours=24.0,
                training_type="EXTERNAL", recurrence_months=36, is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsTrainingCourse(
                course_no="TR-003", course_name="SPC 실무교육",
                category="통계적품질관리", duration_hours=16.0,
                training_type="INTERNAL", recurrence_months=24, is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsTrainingCourse(
                course_no="TR-004", course_name="사출 성형 OJT",
                category="생산기술", duration_hours=40.0,
                training_type="OJT", recurrence_months=None, is_active=True,
                created_at=now, updated_at=now,
            ),
        ]
        db.add_all(courses)
        db.flush()

        trainees = ["W001", "W002", "W003", "W004", "W005"]
        records = []
        for c in courses[:3]:
            for tid in trainees:
                records.append(QmsTrainingRecord(
                    course_id=c.course_id, trainee_id=tid,
                    training_date=date(2026, 2, 15), score=random.uniform(75, 100),
                    result="PASS", next_due_date=date(2027, 2, 15) if c.recurrence_months else None,
                    created_at=now, updated_at=now,
                ))
        # One FAIL record
        records.append(QmsTrainingRecord(
            course_id=courses[2].course_id, trainee_id="W006",
            training_date=date(2026, 2, 15), score=58.0,
            result="FAIL", next_due_date=None,
            created_at=now, updated_at=now,
        ))
        db.add_all(records)

        # ── 9. Qualification ──
        quals = [
            QmsQualification(
                qual_type="INTERNAL_AUDITOR", qual_name="IATF 16949 내부심사원",
                holder_id="W001", issuing_body="한국인정원",
                certificate_no="IA-2024-0512", issue_date=date(2024, 5, 12),
                expiry_date=date(2027, 5, 11), status="ACTIVE",
                created_at=now, updated_at=now,
            ),
            QmsQualification(
                qual_type="INTERNAL_AUDITOR", qual_name="IATF 16949 내부심사원",
                holder_id="W002", issuing_body="한국인정원",
                certificate_no="IA-2023-0301", issue_date=date(2023, 3, 1),
                expiry_date=date(2026, 2, 28), status="EXPIRED",
                created_at=now, updated_at=now,
            ),
            QmsQualification(
                qual_type="WELDER", qual_name="용접기능사",
                holder_id="W003", issuing_body="한국산업인력공단",
                certificate_no="WD-2025-1234", issue_date=date(2025, 8, 20),
                expiry_date=date(2028, 8, 19), status="ACTIVE",
                created_at=now, updated_at=now,
            ),
        ]
        db.add_all(quals)
        db.flush()

        db.add(QmsQualAudit(
            qual_id=quals[0].qual_id, audit_date=date(2026, 3, 10),
            auditor="이부장", result="PASS", score=92.0,
            next_audit_date=date(2027, 3, 10), remarks="적합",
            created_at=now,
        ))

        # ── 10. Competency Matrix ──
        skills = ["SPC 분석", "MSA 수행", "FMEA 작성", "내부심사", "8D 보고서"]
        for emp_id in ["W001", "W002", "W003"]:
            for skill in skills:
                req = random.randint(3, 5)
                cur = random.randint(1, 5)
                db.add(QmsCompetencyMatrix(
                    employee_id=emp_id, skill_name=skill,
                    required_level=req, current_level=cur, gap=max(req - cur, 0),
                    evaluation_date=date(2026, 4, 1), evaluator="이부장",
                    created_at=now, updated_at=now,
                ))

        # ── 11. Specification ──
        specs = [
            QmsSpecification(
                spec_no="SPEC-001", spec_type="CUSTOMER", customer_id="C001",
                product_id="P001", title="현대자동차 도면 규격 HMC-SP-001",
                revision=3, status="ACTIVE", effective_date=date(2025, 6, 1),
                expiry_date=None, source="현대자동차", remarks="연 1회 개정 검토",
                created_at=now, updated_at=now,
            ),
            QmsSpecification(
                spec_no="SPEC-002", spec_type="LEGAL", customer_id=None,
                product_id=None, title="KS B 0401 치수 공차",
                revision=1, status="ACTIVE", effective_date=date(2020, 1, 1),
                expiry_date=None, source="한국산업표준", remarks=None,
                created_at=now, updated_at=now,
            ),
            QmsSpecification(
                spec_no="SPEC-003", spec_type="INTERNAL", customer_id=None,
                product_id="P002", title="내부 검사 기준서 QS-003",
                revision=2, status="ACTIVE", effective_date=date(2026, 1, 15),
                expiry_date=None, source="품질보증팀", remarks=None,
                created_at=now, updated_at=now,
            ),
            QmsSpecification(
                spec_no="SPEC-004", spec_type="DRAWING", customer_id="C002",
                product_id="P002", title="기아 도면 KIA-DW-2025-088",
                revision=1, status="SUPERSEDED", effective_date=date(2025, 3, 1),
                expiry_date=date(2026, 1, 1), source="기아자동차", remarks="신규 Rev.2 발행됨",
                created_at=now, updated_at=now,
            ),
        ]
        db.add_all(specs)
        db.flush()

        db.add_all([
            QmsDrawingRevision(
                spec_mgmt_id=specs[0].spec_mgmt_id, drawing_no="HMC-SP-001",
                revision_no=3, change_summary="치수 공차 변경 (±0.1 → ±0.05)",
                changed_by="현대 설계팀", change_date=date(2025, 5, 20),
                file_path="/docs/HMC-SP-001_Rev3.pdf", created_at=now,
            ),
            QmsDrawingRevision(
                spec_mgmt_id=specs[0].spec_mgmt_id, drawing_no="HMC-SP-001",
                revision_no=2, change_summary="소재 변경 (SUS304 → SUS316)",
                changed_by="현대 설계팀", change_date=date(2024, 8, 10),
                file_path="/docs/HMC-SP-001_Rev2.pdf", created_at=now,
            ),
        ])

        # ── 12. SI FAQ ──
        faqs = [
            QmsSiFaq(
                customer_id="C001", category="검사", question="수입검사 시 AQL 기준은?",
                answer="일반 항목 AQL 0.65, 외관 항목 AQL 1.0 적용 (KS Q ISO 2859-1)",
                reference_spec_id=None, is_active=True, created_at=now, updated_at=now,
            ),
            QmsSiFaq(
                customer_id="C001", category="포장", question="납품 시 라벨 부착 위치는?",
                answer="박스 우측 상단, AIAG 바코드 라벨 규격 준수",
                reference_spec_id=None, is_active=True, created_at=now, updated_at=now,
            ),
            QmsSiFaq(
                customer_id="C002", category="품질", question="PPAP 제출 레벨은?",
                answer="Level 3 기본, 설계변경 시 Level 4 요구 가능",
                reference_spec_id=None, is_active=True, created_at=now, updated_at=now,
            ),
        ]
        db.add_all(faqs)

        # ── 13. CSR ──
        csrs = [
            QmsCsr(
                csr_no="CSR-001", customer_id="C001",
                requirement="초도품 검사 시 Cpk 1.67 이상 달성 필수",
                category="품질", iatf_clause="8.3.4.4",
                compliance_status="COMPLIANT", responsible="김품질",
                target_date=date(2026, 3, 31), completion_date=date(2026, 3, 15),
                evidence="Cpk 보고서 제출 완료 (Cpk=1.89)",
                created_at=now, updated_at=now,
            ),
            QmsCsr(
                csr_no="CSR-002", customer_id="C001",
                requirement="납품 포장재 100% 재활용 가능 소재 사용",
                category="환경", iatf_clause=None,
                compliance_status="PENDING", responsible="한포장",
                target_date=date(2026, 12, 31), completion_date=None,
                evidence=None, created_at=now, updated_at=now,
            ),
            QmsCsr(
                csr_no="CSR-003", customer_id="C002",
                requirement="S/W 업데이트 시 사전 고객 승인 필수",
                category="품질", iatf_clause="8.5.6",
                compliance_status="COMPLIANT", responsible="정소프트",
                target_date=date(2026, 6, 30), completion_date=date(2026, 5, 10),
                evidence="변경관리 프로세스 내 고객승인 절차 반영",
                created_at=now, updated_at=now,
            ),
            QmsCsr(
                csr_no="CSR-004", customer_id="C002",
                requirement="클레임 발생 시 48시간 내 8D 보고서 제출",
                category="품질", iatf_clause="10.2.3",
                compliance_status="NON_COMPLIANT", responsible="김품질",
                target_date=date(2026, 4, 30), completion_date=None,
                evidence=None, created_at=now, updated_at=now,
            ),
        ]
        db.add_all(csrs)

        # ── 14. Customer Audit ──
        ca_audit1 = QmsCustomerAudit(
            audit_no="CA-2026-001", customer_id="C001", audit_type="SQ",
            audit_date=date(2026, 2, 10), audit_end_date=date(2026, 2, 12),
            auditor_name="현대 SQ팀 박차장", scope="사출 및 조립 공정",
            result="CONDITIONAL", score=82.5, status="COMPLETED",
            remarks="조건부 합격 - 시정조치 1건", created_at=now, updated_at=now,
        )
        ca_audit2 = QmsCustomerAudit(
            audit_no="CA-2026-002", customer_id="C002", audit_type="PROCESS",
            audit_date=date(2026, 4, 20), audit_end_date=date(2026, 4, 20),
            auditor_name="기아 품질팀 이과장", scope="도장 공정",
            result="PASS", score=91.0, status="CLOSED",
            remarks=None, created_at=now, updated_at=now,
        )
        ca_audit3 = QmsCustomerAudit(
            audit_no="CA-2026-003", customer_id="C001", audit_type="SYSTEM",
            audit_date=date(2026, 8, 15), audit_end_date=date(2026, 8, 17),
            auditor_name="현대 SQ팀", scope="품질시스템 전반",
            result="PENDING", score=None, status="SCHEDULED",
            remarks="하반기 정기 심사", created_at=now, updated_at=now,
        )
        db.add_all([ca_audit1, ca_audit2, ca_audit3])
        db.flush()

        cf1 = QmsCustomerAuditFinding(
            cust_audit_id=ca_audit1.cust_audit_id, finding_no="CF-2026-001",
            finding_type="MINOR_NC", clause_ref="8.5.1.1",
            description="사출 공정 파라미터 변경 이력 관리 미흡",
            evidence="파라미터 변경 로그 3건 누락 확인",
            status="CLOSED", created_at=now, updated_at=now,
        )
        cf2 = QmsCustomerAuditFinding(
            cust_audit_id=ca_audit1.cust_audit_id, finding_no="CF-2026-002",
            finding_type="OBSERVATION", clause_ref="7.1.5.1",
            description="측정기 관리 대장 양식 개선 권고",
            evidence="현행 양식에 교정 주기 필드 누락",
            status="VERIFIED", created_at=now, updated_at=now,
        )
        db.add_all([cf1, cf2])
        db.flush()

        caa1 = QmsCustomerAuditAction(
            cust_finding_id=cf1.cust_finding_id, action_no="CAA-2026-001",
            root_cause="파라미터 변경 절차서 내 기록 의무 조항 부재",
            containment_action="누락 건 소급 기록 완료",
            corrective_action="파라미터 변경 시 자동 로그 시스템 구축",
            preventive_action="변경관리 프로세스 개정 및 교육",
            responsible="최사출", target_date=date(2026, 3, 31),
            completion_date=date(2026, 3, 20), status="VERIFIED",
            verified_by="현대 SQ팀 박차장", verified_date=date(2026, 4, 5),
            customer_feedback="시정조치 적합 확인",
            created_at=now, updated_at=now,
        )
        db.add(caa1)

        # ── 15. KPI Definition & Data ──
        kpis = [
            QmsKpiDefinition(
                kpi_no="KPI-001", kpi_name="공정 불량률",
                process_name="사출", category="품질", unit="ppm",
                target_value=500, target_direction="LOWER",
                threshold_yellow=800, threshold_red=1200,
                measurement_frequency="MONTHLY", responsible="김품질",
                formula="(불량수 / 생산수) × 1,000,000", is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsKpiDefinition(
                kpi_no="KPI-002", kpi_name="고객 클레임 건수",
                process_name="전사", category="품질", unit="건",
                target_value=2, target_direction="LOWER",
                threshold_yellow=3, threshold_red=5,
                measurement_frequency="MONTHLY", responsible="김품질",
                formula="월간 고객 클레임 접수 건수", is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsKpiDefinition(
                kpi_no="KPI-003", kpi_name="납기 준수율",
                process_name="물류", category="납기", unit="%",
                target_value=98.0, target_direction="HIGHER",
                threshold_yellow=95.0, threshold_red=90.0,
                measurement_frequency="MONTHLY", responsible="한물류",
                formula="(정시 납품 건수 / 총 납품 건수) × 100", is_active=True,
                created_at=now, updated_at=now,
            ),
            QmsKpiDefinition(
                kpi_no="KPI-004", kpi_name="Cpk (핵심 공정)",
                process_name="사출", category="품질", unit="",
                target_value=1.67, target_direction="HIGHER",
                threshold_yellow=1.33, threshold_red=1.0,
                measurement_frequency="MONTHLY", responsible="김품질",
                formula="핵심 치수 공정능력지수", is_active=True,
                created_at=now, updated_at=now,
            ),
        ]
        db.add_all(kpis)
        db.flush()

        kpi_data_values = {
            kpis[0].kpi_id: [  # 공정 불량률 (ppm, LOWER)
                ("2026-01", 650, "YELLOW"), ("2026-02", 520, "YELLOW"),
                ("2026-03", 480, "GREEN"), ("2026-04", 420, "GREEN"),
                ("2026-05", 390, "GREEN"),
            ],
            kpis[1].kpi_id: [  # 클레임 건수 (LOWER)
                ("2026-01", 3, "YELLOW"), ("2026-02", 1, "GREEN"),
                ("2026-03", 2, "GREEN"), ("2026-04", 0, "GREEN"),
                ("2026-05", 1, "GREEN"),
            ],
            kpis[2].kpi_id: [  # 납기준수율 (%, HIGHER)
                ("2026-01", 96.5, "YELLOW"), ("2026-02", 97.2, "YELLOW"),
                ("2026-03", 98.1, "GREEN"), ("2026-04", 99.0, "GREEN"),
                ("2026-05", 98.5, "GREEN"),
            ],
            kpis[3].kpi_id: [  # Cpk (HIGHER)
                ("2026-01", 1.25, "YELLOW"), ("2026-02", 1.38, "YELLOW"),
                ("2026-03", 1.52, "GREEN"), ("2026-04", 1.71, "GREEN"),
                ("2026-05", 1.68, "GREEN"),
            ],
        }
        for kpi_id, data_list in kpi_data_values.items():
            for period, val, st in data_list:
                db.add(QmsKpiData(
                    kpi_id=kpi_id, period=period, actual_value=val, status=st,
                    collected_by="시스템", collected_at=now,
                    created_at=now, updated_at=now,
                ))

        # ── 16. Process Monitor ──
        monitors = [
            QmsProcessMonitor(
                process_name="사출 성형", monitor_date=date(2026, 5, 5),
                monitor_type="ROUTINE", auditor="김현장",
                result="OK", score=95.0,
                findings="이상 없음", actions_required=None, status="CLOSED",
                created_at=now, updated_at=now,
            ),
            QmsProcessMonitor(
                process_name="조립", monitor_date=date(2026, 5, 5),
                monitor_type="ROUTINE", auditor="김현장",
                result="NG", score=72.0,
                findings="토크렌치 사용법 미숙지 작업자 1명 발견",
                actions_required="해당 작업자 OJT 재교육", status="OPEN",
                created_at=now, updated_at=now,
            ),
            QmsProcessMonitor(
                process_name="도장", monitor_date=date(2026, 5, 12),
                monitor_type="LAYERED", auditor="이부장",
                result="OK", score=88.0,
                findings="온습도 관리 기록 일부 누락", actions_required="기록 관리 재교육",
                status="CLOSED", created_at=now, updated_at=now,
            ),
            QmsProcessMonitor(
                process_name="사출 성형", monitor_date=date(2026, 4, 10),
                monitor_type="SPECIAL", auditor="김품질",
                result="OK", score=90.0,
                findings="클레임 후 특별 점검 - 이상 없음",
                actions_required=None, status="CLOSED",
                created_at=now, updated_at=now,
            ),
        ]
        db.add_all(monitors)

        # ── 17. Risk/Issue ──
        risks = [
            QmsRiskIssue(
                issue_no="RISK-001", issue_type="RISK", category="공급망",
                process_name="구매", description="핵심 원자재 단일 공급처 의존 (SUS316 소재)",
                severity=4, likelihood=3, risk_score=12,
                mitigation_plan="대체 공급처 2곳 발굴 및 인증 진행",
                responsible="구매팀 김대리", target_date=date(2026, 9, 30),
                status="MITIGATING", created_at=now, updated_at=now,
            ),
            QmsRiskIssue(
                issue_no="RISK-002", issue_type="RISK", category="설비",
                process_name="사출", description="사출기 #3 노후화 (10년 경과)",
                severity=3, likelihood=4, risk_score=12,
                mitigation_plan="예방보전 주기 단축 및 교체 예산 확보",
                responsible="설비팀 박과장", target_date=date(2026, 12, 31),
                status="IDENTIFIED", created_at=now, updated_at=now,
            ),
            QmsRiskIssue(
                issue_no="RISK-003", issue_type="OPPORTUNITY", category="기술",
                process_name="검사", description="AI 비전 검사 시스템 도입으로 검출율 향상 가능",
                severity=2, likelihood=4, risk_score=8,
                mitigation_plan="PoC 진행 후 투자 검토",
                responsible="기술팀 정차장", target_date=date(2026, 6, 30),
                status="MITIGATING", created_at=now, updated_at=now,
            ),
            QmsRiskIssue(
                issue_no="ISSUE-001", issue_type="ISSUE", category="인력",
                process_name="품질보증", description="내부심사원 자격 보유자 부족 (현 2명, 필요 4명)",
                severity=3, likelihood=5, risk_score=15,
                mitigation_plan="2026년 상반기 2명 추가 양성 교육 등록",
                responsible="김품질", target_date=date(2026, 6, 30),
                status="MITIGATING", created_at=now, updated_at=now,
            ),
            QmsRiskIssue(
                issue_no="RISK-004", issue_type="RISK", category="규제",
                process_name="전사", description="EU REACH 규제 강화에 따른 소재 전환 필요",
                severity=5, likelihood=2, risk_score=10,
                mitigation_plan="소재 분석 및 대체 소재 테스트",
                responsible="기술팀", target_date=date(2027, 3, 31),
                status="IDENTIFIED", created_at=now, updated_at=now,
            ),
        ]
        db.add_all(risks)

        db.commit()
        print("✅ 샘플 데이터 삽입 완료!")
        print("  - FMEA: 2건 (아이템 4건)")
        print("  - 관리계획서: 2건 (아이템 3건)")
        print("  - MSA: 2건 (측정데이터 90건)")
        print("  - PPAP: 2건 (요소 36건)")
        print("  - APQP: 1건 (5개 단계, 11개 산출물)")
        print("  - 표준문서: 6건")
        print("  - 심사요구사항: 5건")
        print("  - 내부심사: 2건 (발견사항 3건, 시정조치 1건)")
        print("  - 교육과정: 4건 (이수기록 16건)")
        print("  - 자격: 3건 (자격심사 1건)")
        print("  - 역량매트릭스: 15건")
        print("  - 규격: 4건 (도면이력 2건)")
        print("  - SI FAQ: 3건")
        print("  - CSR: 4건")
        print("  - 고객심사: 3건 (발견사항 2건, 시정조치 1건)")
        print("  - KPI: 4건 (데이터 20건)")
        print("  - 공정모니터링: 4건")
        print("  - 리스크/이슈: 5건")

    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
