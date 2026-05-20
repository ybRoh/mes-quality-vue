"""
SPC (통계적 공정관리) 서비스
- I-MR / Xbar-R 관리도 계산
- Cp/Cpk/Pp/Ppk 공정능력 계산
- SPC 상수표 (d2, D3, D4, A2, E2)
"""

import numpy as np
from typing import List, Dict, Any

# ── SPC 상수표 ──
# d2: 부분군 크기(n)에 따른 이동범위/범위 → 표준편차 변환 상수
D2_TABLE = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}

# A2: Xbar 관리도 상수 (UCL = X̄̄ + A2*R̄)
A2_TABLE = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}

# D3, D4: R 관리도 상수 (UCL_R = D4*R̄, LCL_R = D3*R̄)
D3_TABLE = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
D4_TABLE = {2: 3.267, 3: 2.575, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}

# E2: 개별 관리도 상수 (n=2 이동범위 기준, E2 = 3/d2 = 2.660)
E2 = 3.0 / D2_TABLE[2]  # 2.6596


def _moving_range(values: np.ndarray) -> np.ndarray:
    """연속 관측치 간 이동범위(MR) 계산"""
    return np.abs(np.diff(values))


def calculate_xbar_r_chart(values: List[float], subgroup_size: int = 1) -> Dict[str, Any]:
    """Xbar-R / I-MR 관리도 계산

    Args:
        values: 측정값 리스트
        subgroup_size: 부분군 크기 (1 = 개별 I-MR 관리도)

    Returns:
        관리도 데이터 (평균, UCL, LCL, R̄, 표준편차 등)
    """
    arr = np.array(values, dtype=float)
    n = len(arr)

    if subgroup_size <= 1:
        # ── I-MR (개별-이동범위) 관리도 ──
        x_bar = float(np.mean(arr))
        mr = _moving_range(arr)
        mr_bar = float(np.mean(mr)) if len(mr) > 0 else 0.0

        # 군내 표준편차 추정: σ̂ = MR̄ / d2 (n=2)
        sigma_within = mr_bar / D2_TABLE[2] if mr_bar > 0 else 0.0

        # I 관리도: UCL = X̄ + E2 * MR̄ = X̄ + 3σ̂
        ucl = x_bar + E2 * mr_bar
        lcl = x_bar - E2 * mr_bar

        return {
            "values": values,
            "mean": round(x_bar, 4),
            "ucl": round(ucl, 4),
            "lcl": round(lcl, 4),
            "std": round(sigma_within, 4),
            "r_bar": round(mr_bar, 4),
            "count": n,
            "chart_type": "I-MR",
        }
    else:
        # ── Xbar-R 관리도 ──
        # 부분군으로 나누기 (마지막 불완전 부분군 제외)
        num_subgroups = n // subgroup_size
        if num_subgroups < 2:
            # 부분군이 부족하면 I-MR로 폴백
            return calculate_xbar_r_chart(values, subgroup_size=1)

        trimmed = arr[:num_subgroups * subgroup_size]
        subgroups = trimmed.reshape(num_subgroups, subgroup_size)

        # 각 부분군의 평균과 범위
        xbars = np.mean(subgroups, axis=1)
        ranges = np.ptp(subgroups, axis=1)  # max - min per subgroup

        x_bar_bar = float(np.mean(xbars))   # 총평균
        r_bar = float(np.mean(ranges))       # 평균범위

        a2 = A2_TABLE.get(subgroup_size, 3.0 / (subgroup_size ** 0.5))

        # Xbar 관리도: UCL = X̄̄ + A2 * R̄
        ucl = x_bar_bar + a2 * r_bar
        lcl = x_bar_bar - a2 * r_bar

        # 군내 표준편차 추정: σ̂ = R̄ / d2
        d2 = D2_TABLE.get(subgroup_size, 1.128)
        sigma_within = r_bar / d2 if r_bar > 0 else 0.0

        return {
            "values": values,
            "xbar_values": [round(v, 4) for v in xbars.tolist()],
            "range_values": [round(v, 4) for v in ranges.tolist()],
            "mean": round(x_bar_bar, 4),
            "ucl": round(ucl, 4),
            "lcl": round(lcl, 4),
            "std": round(sigma_within, 4),
            "r_bar": round(r_bar, 4),
            "r_ucl": round(D4_TABLE.get(subgroup_size, 3.267) * r_bar, 4),
            "r_lcl": round(D3_TABLE.get(subgroup_size, 0) * r_bar, 4),
            "count": n,
            "subgroup_size": subgroup_size,
            "num_subgroups": num_subgroups,
            "chart_type": "Xbar-R",
        }


def calculate_capability(values: List[float], usl: float, lsl: float, subgroup_size: int = 1) -> Dict[str, Any]:
    """Cp/Cpk/Pp/Ppk 공정능력 계산

    Cp/Cpk: 군내 변동 기반 (단기 공정능력)
      - 개별 데이터(subgroup_size=1): σ̂_within = MR̄ / d2
      - 부분군 데이터: σ̂_within = R̄ / d2

    Pp/Ppk: 전체 변동 기반 (장기 공정성능)
      - σ̂_overall = s (표본표준편차, ddof=1)

    Args:
        values: 측정값 리스트
        usl: 규격 상한 (Upper Specification Limit)
        lsl: 규격 하한 (Lower Specification Limit)
        subgroup_size: 부분군 크기 (기본 1 = 개별 데이터)

    Returns:
        공정능력 지수 (Cp, Cpk, Pp, Ppk 등)
    """
    arr = np.array(values, dtype=float)
    n = len(arr)
    mean = float(np.mean(arr))

    # ── 전체 표준편차 (장기, Pp/Ppk용) ──
    std_overall = float(np.std(arr, ddof=1))

    # ── 군내 표준편차 (단기, Cp/Cpk용) ──
    if subgroup_size <= 1:
        # 개별 데이터: 이동범위(MR) 기반 σ̂ = MR̄ / d2
        mr = _moving_range(arr)
        mr_bar = float(np.mean(mr)) if len(mr) > 0 else 0.0
        std_within = mr_bar / D2_TABLE[2] if mr_bar > 0 else 0.0
    else:
        # 부분군 데이터: R̄ / d2
        num_subgroups = n // subgroup_size
        if num_subgroups >= 2:
            trimmed = arr[:num_subgroups * subgroup_size]
            subgroups = trimmed.reshape(num_subgroups, subgroup_size)
            ranges = np.ptp(subgroups, axis=1)
            r_bar = float(np.mean(ranges))
            d2 = D2_TABLE.get(subgroup_size, 1.128)
            std_within = r_bar / d2 if r_bar > 0 else 0.0
        else:
            # 부분군 부족 시 이동범위 방식 사용
            mr = _moving_range(arr)
            mr_bar = float(np.mean(mr)) if len(mr) > 0 else 0.0
            std_within = mr_bar / D2_TABLE[2] if mr_bar > 0 else 0.0

    if std_within == 0 or std_overall == 0:
        return {"error": "표준편차가 0입니다. 데이터를 확인하세요."}

    # ── 군내 기반: Cp/Cpk (단기 공정능력) ──
    cp = (usl - lsl) / (6 * std_within)
    cpu = (usl - mean) / (3 * std_within)
    cpl = (mean - lsl) / (3 * std_within)
    cpk = min(cpu, cpl)

    # ── 전체 기반: Pp/Ppk (장기 공정성능) ──
    pp = (usl - lsl) / (6 * std_overall)
    ppu = (usl - mean) / (3 * std_overall)
    ppl = (mean - lsl) / (3 * std_overall)
    ppk = min(ppu, ppl)

    return {
        "mean": round(mean, 4),
        "std_within": round(std_within, 4),
        "std_overall": round(std_overall, 4),
        "cp": round(cp, 3),
        "cpk": round(cpk, 3),
        "pp": round(pp, 3),
        "ppk": round(ppk, 3),
        "cpu": round(cpu, 3),
        "cpl": round(cpl, 3),
        "count": n,
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
    }
