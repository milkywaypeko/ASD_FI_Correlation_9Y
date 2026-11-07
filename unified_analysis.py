"""Unified, reproducible statsmodels OLS index and lazy details.

The same fitted model supplies index statistics, its unabridged summary(),
and exact complete-case observations with predictions and residuals.
Original Statistics CSV files are never modified.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import gzip
import json
import math
import shutil

from expanded_analysis import PROVINCES, fit_extended_ols

HEALTH_YEARS = tuple(range(2015, 2023))
ALL_YEARS = tuple(range(2014, 2023))
LABELS = {
    "before": "재정자립도(개편 전, 0~1)",
    "after": "재정자립도(개편 후, 0~1)",
    "age65_percent": "65세 이상 주민등록연앙인구 비율(%)",
    "under15_percent": "0~14세 주민등록연앙인구 비율(%)",
    "fertility": "합계출산율(명/여성)",
    "medical_10k_per_person": "1인당 진료비(만원/인/년)",
    "premium_10k_per_household": "가구당 건강보험료(만원/세대/년)",
}
# The fiscal explanatory variable is selected from the two published series.
SPECS = {
    "six": {"fields": ("age65_percent", "under15_percent", "fertility",
                       "medical_10k_per_person", "premium_10k_per_household"),
            "fiscal": True, "years": HEALTH_YEARS, "label": "최종 6변수 다중회귀"},
    "age65": {"fields": ("age65_percent",), "fiscal": False,
              "years": ALL_YEARS, "label": "65세 이상 인구비율 단순회귀"},
    "under15": {"fields": ("under15_percent",), "fiscal": False,
                "years": ALL_YEARS, "label": "0~14세 인구비율 단순회귀"},
    "medical": {"fields": ("medical_10k_per_person",), "fiscal": False,
                "years": HEALTH_YEARS, "label": "1인당 진료비 단순회귀"},
    "premium": {"fields": ("premium_10k_per_household",), "fiscal": False,
                "years": HEALTH_YEARS, "label": "가구당 건강보험료 단순회귀"},
    "fertility": {"fields": ("fertility",), "fiscal": False,
                  "years": ALL_YEARS, "label": "합계출산율 단순회귀"},
    "fiscal": {"fields": (), "fiscal": True,
               "years": ALL_YEARS, "label": "재정자립도 단순회귀"},
}


def _save(path: Path, value):
    """Byte-preserving compact JSON or deterministic gzip (no statistical rounding)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")
    if path.suffix == ".gz":
        path.write_bytes(gzip.compress(data, compresslevel=6, mtime=0))
    else:
        path.write_bytes(data)


def _finite(value):
    return value is not None and math.isfinite(float(value))


def _complete_cases(rows, dtype, fields):
    return [
        row for row in rows
        if _finite(row.get("rates", {}).get(dtype))
        and all(_finite(row.get(field)) for field in fields)
    ]



def _pearson_correlation(xs, ys):
    """Pearson r on the *same* model complete cases; undefined => None.

    Unweighted descriptive correlation, not a multivariate/partial
    regression coefficient. Never fill missing values or hide zero variance.
    """
    if len(xs) < 2:
        return None
    mean_x = math.fsum(xs) / len(xs)
    mean_y = math.fsum(ys) / len(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    sx = math.fsum(a * a for a in dx)
    sy = math.fsum(b * b for b in dy)
    if sx <= 0.0 or sy <= 0.0:
        return None
    value = math.fsum(a * b for a, b in zip(dx, dy)) / math.sqrt(sx * sy)
    return max(-1.0, min(1.0, value)) if math.isfinite(value) else None


def _fit(rows, dtype, fields, scope, region, period, fiscal_mode):
    # Provincial disability totals are valid only if every component locality
    # reported that type. Unreported categories must never become zero.
    if scope == "provincial":
        rows = [r for r in rows if dtype in r.get("complete_types", [])]
    complete = _complete_cases(rows, dtype, fields)
    model = fit_extended_ols(
        rows, fields, scope, region, period, fiscal_mode, dtype
    )
    if model["n"] != len(complete):
        raise AssertionError("OLS complete-case count does not match audit rows")
    # Marginal X-Y Pearson r for each predictor, evaluated on exactly the
    # same complete cases as the corresponding six-variable or simple OLS.
    # These are NOT partial correlations and are not inferred from R².
    y_values = [float(row["rates"][dtype]) for row in complete]
    correlations = [
        _pearson_correlation(
            [float(row[field]) for row in complete], y_values
        ) for field in fields
    ]
    observations = []
    for row in complete:
        actual = float(row["rates"][dtype])
        xs = [float(row[field]) for field in fields]
        fitted = (
            float(model["intercept"]) +
            sum(float(model["coefficients"][field]["coef"]) * x
                for field, x in zip(fields, xs))
            if model["intercept"] is not None else None
        )
        residual = actual - fitted if fitted is not None else None
        observations.append([row["year"], row["province"], row["district"],
                             actual, *xs, fitted, residual])
    record = {
        "scope": scope, "region": region, "year": period,
        "type": dtype, "mode": fiscal_mode, "n": model["n"],
        "intercept": model["intercept"], "r2": model["r2"],
        "adj_r2": model["adj_r2"], "p_model": model["p_model"],
        "coefficients": [model["coefficients"].get(f, {}).get("coef") for f in fields],
        "pvalues": [model["coefficients"].get(f, {}).get("p") for f in fields],
        "correlations": correlations,
        "warning": model["warning"],
    }
    detail = {
        "model": model,
        "correlations": {
            "method": "pearson",
            "sample_n": len(complete),
            "predictors": dict(zip(fields, correlations)),
        },
        "columns": ["year", "province", "district", "registered_rate_percent",
                    *fields, "prediction_percent", "residual_percentage_points"],
        "observations": observations,
        "notes": {
            "outcome": "해당 장애유형 등록인원 ÷ 해당 연도·지역 주민등록인구 × 100 (%)",
            "prediction": "동일 statsmodels OLS 모형으로 계산한 관측치별 적합값",
            "inference": "통계적 연관성만 분석하며 인과관계를 입증하지 않습니다.",
            "correlation": "피어슨 r은 모형에 사용된 동일 완전관측치의 Y와 각 X 간 비가중 이변량 상관계수입니다. 다른 X를 통제한 편상관이나 다중회귀 β가 아닙니다. n<2 또는 어느 변수든 분산이 0이면 null로 기록합니다.",
        },
    }
    return record, detail


def build_unified_analysis(out: Path, detail: list[dict],
                           provinces: list[dict], types: list[str]):
    """Emit seven regressions, all types/scopes, light indexes and lazy details."""
    results = {}
    # Build to a reproducible site even when the prior uncompressed 1,258
    # shards are present. Never touch Statistics/ raw CSVs.
    data_dir = out / "data"
    shutil.rmtree(data_dir / "unified_detail", ignore_errors=True)
    for old in data_dir.glob("unified_index_*.json*"):
        old.unlink()
    province_groups = defaultdict(list)
    local_groups = defaultdict(list)
    province_aggregate_groups = defaultdict(list)
    for row in detail:
        province_groups[row["province"]].append(row)
        local_groups[(row["province"], row["district"])].append(row)
    for row in provinces:
        province_aggregate_groups[row["province"]].append(row)

    for key, spec in SPECS.items():
        allowed = set(spec["years"])
        annual = {y: [r for r in detail if r["year"] == y] for y in spec["years"]}
        annual_prov = {y: [r for r in provinces if r["year"] == y] for y in spec["years"]}
        pooled = [r for r in detail if r["year"] in allowed]
        pooled_prov = [r for r in provinces if r["year"] in allowed]
        history = {region: [r for r in rows if r["year"] in allowed]
                   for region, rows in local_groups.items()}
        index = []
        total_fitted = 0
        for type_index, dtype in enumerate(types):
            # Group one disability type into a single compressed asset.
            # 119 files replace 1,258 tiny per-period JSON documents; detail
            # stays lazy and all original statsmodels summaries remain exact.
            shard = f"data/unified_detail/{key}/{type_index:02d}.json.gz"
            payload = {}
            for period in (*spec["years"], "pooled", "history"):
                if period == "history":
                    scopes = [("local_history", prov + "|" + dist, rows)
                              for (prov, dist), rows in sorted(history.items())]
                    model_period = "전기간"
                else:
                    subset = pooled if period == "pooled" else annual[period]
                    subset_prov = pooled_prov if period == "pooled" else annual_prov[period]
                    scopes = [("municipal", "전국", subset)]
                    scopes.extend(("municipal", province,
                                   [r for r in subset if r["province"] == province])
                                  for province in PROVINCES)
                    scopes.append(("provincial", "전국", subset_prov))
                    model_period = "전기간" if period == "pooled" else period
                for mode in (("before", "after") if spec["fiscal"] else (None,)):
                    fields = ((mode,) + spec["fields"] if mode else spec["fields"])
                    for scope, region, rows in scopes:
                        item, full = _fit(
                            rows, dtype, fields, scope, region, model_period, mode
                        )
                        ident = str(len(index))
                        item.update(id=ident, shard=shard)
                        index.append(item)
                        payload[ident] = full
                        if item["intercept"] is not None:
                            total_fitted += 1
            _save(out / shard, payload)
        _save(out / "data" / f"unified_index_{key}.json.gz", index)
        results[key] = {
            "models": len(index), "fitted": total_fitted,
            "years": list(spec["years"]), "label": spec["label"],
        }
        print("통합 OLS", key, results[key], flush=True)

    _save(out / "data" / "unified_manifest.json", {
        "types": types, "provinces": PROVINCES,
        "labels": LABELS,
        "models": {
            key: {"label": cfg["label"], "years": list(cfg["years"]),
                  "fiscal": cfg["fiscal"], "fields": list(cfg["fields"])}
            for key, cfg in SPECS.items()
        },
        "limitations": [
            "피어슨 r은 동일 완전관측치에서 계산된 각 X와 등록률 Y의 이변량 상관이며, 다중회귀 β 또는 편상관이 아닙니다.",
            "r의 절댓값이 1에 가까우면 선형 연관성이 크지만 인과관계를 입증하지 않습니다.",
            "상수열이나 표본 부족으로 계산되지 않는 r은 결측으로 기록하며 0으로 대체하지 않습니다.",
            "지역별 회귀계수는 통계적 연관성이며 인과효과가 아닙니다.",
            "단순회귀는 다른 변수를 통제하지 않으며, 다중회귀 계수는 다른 다섯 변수를 일정하게 둔 조건부 연관성입니다.",
            "연도 통합 OLS는 지자체 반복관측과 연도효과를 따로 통제하지 않습니다.",
            "인구구조, 보험료, 진료비, 재정자립도 사이에 상관 및 다중공선성이 존재할 수 있습니다.",
            "진료비·보험료는 고령화와 질병부담의 결과일 수도 있습니다.",
            "원본 자료의 결측, 행정구역 개편, 집계 기준 차이로 표본 수가 변합니다.",
            "건강보험 관련 회귀는 2014년을 배제하여 2015~2022년만 사용합니다.",
            "2014년 원본 CSV는 변경하거나 삭제하지 않습니다.",
        ],
        "index_summary": results,
    })
    return results
