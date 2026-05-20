"""
MSA (측정시스템분석) 서비스
- ANOVA 기반 GR&R 계산
- EV (Equipment Variation), AV (Appraiser Variation)
- %GR&R, ndc (구별범주수)
"""

import numpy as np
from typing import List, Dict, Any, Tuple


def calculate_grr(
    measurements: List[Dict[str, Any]],
    num_operators: int,
    num_parts: int,
    num_trials: int,
    tolerance: float = None,
) -> Dict[str, Any]:
    """ANOVA 기반 GR&R 계산

    Args:
        measurements: 측정 데이터 리스트 [{operator_name, part_no, trial_no, measured_value}, ...]
        num_operators: 작업자 수
        num_parts: 부품 수
        num_trials: 반복 횟수
        tolerance: 공차 (USL - LSL), None이면 5.15*sigma 기준 사용

    Returns:
        GR&R 분석 결과
    """
    # 데이터를 3차원 배열로 변환: [작업자][부품][반복]
    operators = sorted(set(m["operator_name"] for m in measurements))
    parts = sorted(set(m["part_no"] for m in measurements))

    k = len(operators)   # 작업자 수
    n = len(parts)       # 부품 수
    r = num_trials       # 반복 수

    # 데이터 행렬 구성
    data = np.zeros((k, n, r))
    for m in measurements:
        i = operators.index(m["operator_name"])
        j = parts.index(m["part_no"])
        t = m["trial_no"] - 1
        if 0 <= t < r:
            data[i, j, t] = m["measured_value"]

    # 전체 평균
    x_bar = np.mean(data)

    # ── 반복성 (EV: Equipment Variation) ──
    # 각 작업자-부품 조합의 범위(range) 계산
    ranges = np.max(data, axis=2) - np.min(data, axis=2)  # (k, n)
    r_bar = np.mean(ranges)

    # d2 상수표 (반복 횟수별)
    d2_table = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534}
    d2 = d2_table.get(r, 1.128)

    ev = r_bar / d2  # 반복성 표준편차

    # ── 재현성 (AV: Appraiser Variation) ──
    # 작업자별 평균
    x_bar_operator = np.mean(data, axis=(1, 2))  # (k,)
    x_diff = np.max(x_bar_operator) - np.min(x_bar_operator)

    # d2* 상수표 (작업자 수별)
    d2_star_table = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326}
    d2_star = d2_star_table.get(k, 1.128)

    av_squared = (x_diff / d2_star) ** 2 - (ev ** 2 / (n * r))
    av = np.sqrt(max(av_squared, 0))  # 재현성 표준편차

    # ── GR&R ──
    grr = np.sqrt(ev ** 2 + av ** 2)

    # ── 부품 변동 (PV: Part Variation) ──
    x_bar_part = np.mean(data, axis=(0, 2))  # (n,)
    rp = np.max(x_bar_part) - np.min(x_bar_part)

    d2_part_table = {
        2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
        6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078,
    }
    d2_part = d2_part_table.get(n, 3.078)

    pv = rp / d2_part  # 부품 변동 표준편차

    # ── 총 변동 (TV: Total Variation) ──
    tv = np.sqrt(grr ** 2 + pv ** 2)

    # ── 비율 계산 ──
    if tv > 0:
        ev_pct = round(ev / tv * 100, 2)
        av_pct = round(av / tv * 100, 2)
        grr_pct = round(grr / tv * 100, 2)
        pv_pct = round(pv / tv * 100, 2)
    else:
        ev_pct = av_pct = grr_pct = pv_pct = 0.0

    # 공차 기준 %GR&R (tolerance가 주어진 경우)
    if tolerance and tolerance > 0:
        grr_pct_tolerance = round(5.15 * grr / tolerance * 100, 2)
    else:
        grr_pct_tolerance = grr_pct

    # ── ndc (구별범주수) ──
    ndc = int(1.41 * (pv / grr)) if grr > 0 else 0

    # ── 판정 ──
    if grr_pct_tolerance < 10:
        judgment = "ACCEPTABLE"
    elif grr_pct_tolerance < 30:
        judgment = "MARGINAL"
    else:
        judgment = "UNACCEPTABLE"

    return {
        "ev": round(float(ev), 4),
        "av": round(float(av), 4),
        "grr": round(float(grr), 4),
        "pv": round(float(pv), 4),
        "tv": round(float(tv), 4),
        "ev_pct": ev_pct,
        "av_pct": av_pct,
        "grr_pct": round(grr_pct_tolerance, 2),
        "pv_pct": pv_pct,
        "ndc": ndc,
        "judgment": judgment,
    }
