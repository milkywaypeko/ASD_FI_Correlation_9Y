"""Additional 2014–2022 demographic and medical-expense OLS models.

The source statistics are read-only. All municipality joins use a full
(year, province, district) key; ward totals are combined only when a city
total is absent, and missing covariates are never imputed.
"""
from __future__ import annotations

import csv
import json
import math
import re
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import statsmodels.api as sm

YEARS = tuple(range(2014, 2023))
MODES = ("before", "after")
PROVINCES = (
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
    "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도",
    "충청북도", "충청남도", "전북특별자치도", "전라남도", "경상북도",
    "경상남도", "제주특별자치도",
)
ALIASES = {
    "서울": "서울특별시", "부산": "부산광역시", "대구": "대구광역시",
    "인천": "인천광역시", "광주": "광주광역시", "대전": "대전광역시",
    "울산": "울산광역시", "세종": "세종특별자치시", "경기": "경기도",
    "강원": "강원특별자치도", "충북": "충청북도", "충남": "충청남도",
    "전북": "전북특별자치도", "전남": "전라남도", "경북": "경상북도",
    "경남": "경상남도", "제주": "제주특별자치도",
    "강원도": "강원특별자치도", "전라북도": "전북특별자치도",
}
SPECIAL = {"세종특별자치시", "제주특별자치도"}
AGE_VARIABLES = ("age65_percent", "under15_percent")
MEDICAL = "medical_10k_per_person"
LABELS = {
    "before": "재정자립도(개편 전, 0~1)", "after": "재정자립도(개편 후, 0~1)",
    "age65_percent": "65세 이상 인구비율(%)",
    "under15_percent": "0~14세 인구비율(%)",
    "fertility": "합계출산율(명/여성)",
    MEDICAL: "1인당 진료비(만원)",
}
SIMPLE = {
    "age65": "age65_percent",
    "under15": "under15_percent",
    "medical": MEDICAL,
}


def read_csv(path: Path) -> list[list[str]]:
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            with path.open(encoding=encoding, newline="") as handle:
                return list(csv.reader(handle))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"CSV 인코딩을 읽을 수 없습니다: {path}")


def number(value: str) -> float | None:
    text = str(value or "").strip().replace(",", "")
    if text in ("", "-", "…", "X", "x", "N/A"):
        return None
    try:
        parsed = float(text)
        return parsed if math.isfinite(parsed) else None
    except ValueError:
        return None


def province_name(text: str) -> str:
    name = text.strip()
    return ALIASES.get(name, name)


def district_name(province: str, value: str) -> str:
    name = re.sub(r"\s*\([^)]*변동[^)]*\)\s*$", "", value.strip())
    for prefix in ("충북 ", "경기 "):
        if name.startswith(prefix):
            name = name[len(prefix):]
    if province == "인천광역시" and name == "남구":
        return "미추홀구"
    return province if province in SPECIAL else name


def year_columns(headers: list[str]) -> list[tuple[int, int]]:
    found = []
    for index, header in enumerate(headers):
        match = re.match(r"^\s*(20\d{2})\s*(?:년)?\s*$", header)
        if match and int(match.group(1)) in YEARS:
            found.append((index, int(match.group(1))))
    return found


def _parent_city(district: str) -> str | None:
    """Identify city wards such as '청주시 상당구' without pooling ordinary 구."""
    match = re.fullmatch(r"(\S+시)\s+\S+구", district)
    return match.group(1) if match else None


def parse_age_population(path: Path):
    """Return age-band statistics from official 5-year mid-year counts.

    Uses '계' sex only; 0–14 is 0–4 + 5–9 + 10–14 and 65+
    is 65–69, 70–74, 75–79, 80–84, and 85+.
    """
    rows = read_csv(path)
    columns = year_columns(rows[0])
    if set(y for _, y in columns) != set(YEARS):
        raise ValueError("5세별 연앙인구 파일의 2014~2022 열이 불완전합니다.")
    bands = defaultdict(dict)
    province = None
    for row in rows[1:]:
        if len(row) < 5 or row[1].strip() != "계":
            continue
        area = province_name(row[0])
        if area == "전국":
            continue
        if area in PROVINCES:
            province = area
            district = area
        elif province:
            if province in SPECIAL:
                continue
            district = district_name(province, row[0])
        else:
            continue
        age_text = re.sub(r"\s+", "", row[2])
        if age_text == "계":
            age = "total"
        else:
            match = re.fullmatch(r"(\d+)-(\d+)세", age_text)
            if match and int(match.group(2)) - int(match.group(1)) == 4:
                age = int(match.group(1))
            elif re.fullmatch(r"85세이상", age_text):
                age = 85
            else:
                continue
        if age != "total" and age not in (*range(0, 85, 5), 85):
            continue
        for index, year in columns:
            val = number(row[index] if index < len(row) else "")
            if val is not None and val >= 0:
                bands[(year, province, district)][age] = val

    # For sources that only list city wards, construct the parent from disjoint wards.
    parts = defaultdict(list)
    for (year, prov, district), vals in bands.items():
        parent = _parent_city(district)
        if parent is not None:
            parts[(year, prov, parent)].append(vals)
    for key, members in parts.items():
        if key in bands:
            continue
        combined = {}
        for field in ("total", 0, 5, 10, 65, 70, 75, 80, 85):
            if all(field in member for member in members):
                combined[field] = sum(member[field] for member in members)
        bands[key] = combined

    result = {}
    for key, values in bands.items():
        population = values.get("total")
        young = (sum(values[v] for v in (0, 5, 10))
                 if all(v in values for v in (0, 5, 10)) else None)
        elderly = (sum(values[v] for v in (65, 70, 75, 80, 85))
                   if all(v in values for v in (65, 70, 75, 80, 85)) else None)
        result[key] = {
            "age_population": population,
            "under15_percent": young / population * 100 if population and young is not None else None,
            "age65_percent": elderly / population * 100 if population and elderly is not None else None,
        }
    return result


def parse_medical_expenses(folder: Path):
    """Read three long-form and one multiheader wide-form treatment tables.

    Each selected value is '진료비 (천원)' for age '합계', not benefit cost
    (급여비) and not cost per treated person (진료실인원수).
    """
    direct = {}
    duplicates = []
    paths = sorted(folder.glob("시군구*연령별 진료현황-전체.csv"))
    if len(paths) != 4:
        raise ValueError(f"의료비 통계 파일 4개가 필요합니다. 발견: {len(paths)}")
    for path in paths:
        rows = read_csv(path)
        wide = len(rows) > 2 and rows[0][1].startswith("시군구별(2)")
        if wide:
            cols = [(index, year) for index, year in year_columns(rows[0])
                    if rows[1][index].strip() == "합계"
                    and "진료비" in rows[2][index].replace(" ", "")
                    and "급여비" not in rows[2][index]]
            if len(cols) != len(YEARS):
                raise ValueError(f"의료비 가로형 CSV 열 매핑 오류: {path}")
            candidates = []
            for row in rows[3:]:
                if len(row) < 2:
                    continue
                province = province_name(row[0])
                if province not in PROVINCES:
                    continue
                district = province if row[1].strip() in ("소계", "합계") else district_name(province, row[1])
                candidates.extend(((year, province, district), number(row[index]))
                                  for index, year in cols if index < len(row))
        else:
            cols = year_columns(rows[0])
            if len(cols) != len(YEARS):
                raise ValueError(f"의료비 세로형 CSV 열 매핑 오류: {path}")
            candidates = []
            province = None
            for row in rows[1:]:
                if len(row) < 4 or row[1].strip() != "합계" or "진료비" not in row[2] or "급여비" in row[2]:
                    continue
                area = province_name(row[0])
                if area in PROVINCES:
                    province = area
                    district = area
                elif province:
                    if province in SPECIAL:
                        continue
                    district = district_name(province, row[0])
                else:
                    continue
                candidates.extend(((year, province, district), number(row[index]))
                                  for index, year in cols if index < len(row))
        for key, value in candidates:
            if value is None or value < 0:
                continue
            if key in direct and not math.isclose(direct[key], value):
                duplicates.append({"key": list(key), "first": direct[key], "next": value})
                continue
            direct[key] = value

    # Parent municipality entries take precedence; ward costs are summed only
    # when the parent city is absent. This avoids double-counting city totals.
    parts = defaultdict(list)
    for (year, prov, district), cost in direct.items():
        parent = _parent_city(district)
        if parent:
            parts[(year, prov, parent)].append(cost)
    for key, values in parts.items():
        if key not in direct:
            direct[key] = sum(values)
    return direct, duplicates


def _finite(value):
    return round(float(value), 12) if value is not None and math.isfinite(float(value)) else None


def fit_extended_ols(rows: list[dict], predictors: tuple[str, ...],
                     scope: str, region: str, year: int | str, mode: str | None = None,
                     dtype: str = "전체"):
    """Complete-case OLS with a constant, rank check, and explicit warnings."""
    valid = [r for r in rows if r.get("rates", {}).get(dtype) is not None
             and all(r.get(field) is not None and math.isfinite(float(r[field])) for field in predictors)]
    k = len(predictors)
    result = {
        "scope": scope, "region": region, "year": year, "mode": mode,
        "type": dtype, "n": len(valid), "predictors": list(predictors),
        "intercept": None, "coefficients": {}, "r2": None, "adj_r2": None,
        "p_model": None, "warning": None, "raw": None,
    }
    if len(valid) < k + 2:
        result["warning"] = f"회귀에 필요한 완전 관측치가 부족합니다 (최소 {k + 2}개)."
        return result
    x = np.asarray([[float(r[field]) for field in predictors] for r in valid])
    y = np.asarray([float(r["rates"][dtype]) for r in valid])
    if not np.isfinite(y).all():
        result["warning"] = "종속변수에 유효하지 않은 수치가 있습니다."
        return result
    design = sm.add_constant(x, has_constant="add")
    if np.linalg.matrix_rank(design) != k + 1:
        result["warning"] = "독립변수에 상수 또는 완전한 선형종속이 존재합니다."
        return result
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = sm.OLS(y, design).fit()
            raw = str(model.summary(xname=["const"] + [field.replace("before","fiscal_before").replace("after","fiscal_after") for field in predictors]))
        ci = model.conf_int(alpha=.05)
        coefficients = {
            field: {
                "coef": _finite(model.params[i + 1]),
                "p": float(model.pvalues[i + 1]) if math.isfinite(float(model.pvalues[i + 1])) else None,
                "ci": [_finite(ci[i + 1, 0]), _finite(ci[i + 1, 1])],
                "se": _finite(model.bse[i + 1]),
            }
            for i, field in enumerate(predictors)
        }
        result.update(intercept=_finite(model.params[0]),
                      coefficients=coefficients, r2=_finite(model.rsquared),
                      adj_r2=_finite(model.rsquared_adj),
                      p_model=float(model.f_pvalue) if math.isfinite(float(model.f_pvalue)) else None,
                      raw=raw)
    except (ValueError, np.linalg.LinAlgError) as exc:
        result["warning"] = f"OLS 계산 실패: {exc}"
    return result


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False), encoding="utf-8")


def _emit_models(out: Path, prefix: str, detail: list[dict], provinces: list[dict],
                 predictors: tuple[str, ...], fiscal_mode: bool):
    """Create the same annual / pooled / local-history scopes as the existing UI."""
    def models(rows, prov_rows, year, mode=None):
        output = [fit_extended_ols(rows, predictors_for(mode), "municipal", "전국", year, mode)]
        for province in PROVINCES:
            subset = [r for r in rows if r["province"] == province]
            output.append(fit_extended_ols(subset, predictors_for(mode), "municipal", province, year, mode))
        output.append(fit_extended_ols(prov_rows, predictors_for(mode), "provincial", "전국", year, mode))
        return output

    def predictors_for(mode):
        return ((mode,) + predictors) if fiscal_mode else predictors

    by_local = defaultdict(list)
    for row in detail:
        by_local[(row["province"], row["district"])].append(row)
    total = 0
    for year in YEARS:
        rows = [r for r in detail if r["year"] == year]
        prov_rows = [r for r in provinces if r["year"] == year]
        for mode in (MODES if fiscal_mode else (None,)):
            group = models(rows, prov_rows, year, mode)
            suffix = f"_{mode}" if mode else ""
            _write_json(out / "data" / f"{prefix}_{year}{suffix}.json", group)
            total += len(group)

    pooled, history = [], []
    for mode in (MODES if fiscal_mode else (None,)):
        pooled.extend(models(detail, provinces, "전기간", mode))
        for (prov, district), rows in sorted(by_local.items()):
            history.append(fit_extended_ols(rows, predictors_for(mode),
                                            "local_history", prov + "|" + district,
                                            "전기간", mode))
    _write_json(out / "data" / f"{prefix}_pooled.json", pooled)
    _write_json(out / "data" / f"{prefix}_local_history.json", history)
    return {"yearly_models": total, "pooled_models": len(pooled),
            "local_history_models": len(history),
            "estimated_models": sum(m["intercept"] is not None for m in pooled + history)}



def _emit_disability_type_models(out: Path, detail: list[dict], provinces: list[dict],
                                 types: list[str]):
    """Precompute all 4 regressions per disability type in lazily fetched files.

    Models retain annual, nationwide/provincial, pooled, and locality histories;
    the full statsmodels OLS Regression Results are preserved for every fit.
    All source category missingness is preserved, never converted to zero.
    """
    yearly = {y: [r for r in detail if r["year"] == y] for y in YEARS}
    province_yearly = {y: [r for r in provinces if r["year"] == y] for y in YEARS}
    history = defaultdict(list)
    for r in detail:
        history[(r["province"], r["district"])].append(r)
    configurations = {
        "demographic_multi_models": (("age65_percent", "under15_percent", "fertility", MEDICAL), True),
        "age65_ols_models": (("age65_percent",), False),
        "under15_ols_models": (("under15_percent",), False),
        "medical_ols_models": ((MEDICAL,), False),
    }
    summary = {}
    for index, dtype in enumerate(types):
        if dtype == "전체":
            continue  # Existing 53 files retain the default '전체' models.
        counts = {}
        for prefix, (predictors, is_multi) in configurations.items():
            models = []
            modes = MODES if is_multi else (None,)
            for period in (*YEARS, "전기간"):
                subset = yearly[period] if isinstance(period, int) else detail
                prov_subset = province_yearly[period] if isinstance(period, int) else provinces
                grouped = {prov: [r for r in subset if r["province"] == prov] for prov in PROVINCES}
                # Only a province with complete district-type reporting yields an
                # aggregate type rate. Partial totals must never masquerade as full.
                complete_prov = [r for r in prov_subset if dtype in r.get("complete_types", [])]
                for fiscal in modes:
                    names = ((fiscal,) + predictors) if fiscal else predictors
                    def fit(rows, scope, region, p=period):
                        return fit_extended_ols(rows, names, scope, region, p,
                                                fiscal, dtype)
                    models.append(fit(subset, "municipal", "전국"))
                    models.extend(fit(grouped[prov], "municipal", prov) for prov in PROVINCES)
                    models.append(fit(complete_prov, "provincial", "전국"))
            for fiscal in modes:
                names = ((fiscal,) + predictors) if fiscal else predictors
                for (prov, district), rows in sorted(history.items()):
                    models.append(fit_extended_ols(
                        rows, names, "local_history", prov + "|" + district,
                        "전기간", fiscal, dtype))
            filename = f"{prefix}_type_{index:02d}.json"
            _write_json(out / "data" / filename, {"type": dtype, "models": models})
            counts[prefix] = {
                "models": len(models),
                "fitted": sum(m["intercept"] is not None for m in models),
                "annual_2022_national_n": next(
                    (m["n"] for m in models if m["scope"] == "municipal"
                     and m["region"] == "전국" and m["year"] == 2022), 0),
            }
        summary[dtype] = counts
    return summary


def build_expanded_analysis(stats: Path, out: Path, detail: list[dict],
                            province_rows: list[dict], disability_types: list[str] | None = None):
    """Enrich observation rows in-place and write all four requested model sets.

    Run after build_multivariate(), so its fertility field has already joined.
    Must run before municipalities.json and provinces.json are written.
    """
    age = parse_age_population(stats / "연령(5세)별 주민등록연앙인구.csv")
    costs, duplicates = parse_medical_expenses(stats)
    all_rows = detail + province_rows
    for row in all_rows:
        key = (row["year"], row["province"], row["district"])
        age_values = age.get(key, {})
        for field in ("age_population", "age65_percent", "under15_percent"):
            row[field] = _finite(age_values.get(field))
        medical_cost = costs.get(key)
        population = age_values.get("age_population")
        row["medical_total_thousand_krw"] = medical_cost
        row[MEDICAL] = _finite(medical_cost / (10.0 * population)) if (
            medical_cost is not None and population is not None and population > 0) else None

    # Keep partial provincial disability aggregations from being treated as
    # complete observations in the new type-filtered models and plots.
    disability_types = disability_types or ["전체"]
    municipalities_by_province = defaultdict(list)
    for row in detail:
        municipalities_by_province[(row["year"], row["province"])].append(row)
    for row in province_rows:
        members = municipalities_by_province[(row["year"], row["province"])]
        row["complete_types"] = [dtype for dtype in disability_types
                                 if members and all(dtype in m["rates"] for m in members)]

    checks = ("age65_percent", "under15_percent", "fertility", MEDICAL)
    audit = {
        "years": list(YEARS),
        "sources": ["Statistics/연령(5세)별 주민등록연앙인구.csv",
                    "Statistics/시군구(...)별 연령별 진료현황-전체.csv"],
        "denominators": "0~14세·65세 이상 비율의 분모와 의료비 1인당 분모는 해당 연도 주민등록연앙인구(계).",
        "medical_definition": "전체 연령 진료비(천원) × 1000 ÷ 주민등록연앙인구 ÷ 10000 = 만원/인. 급여비·진료인원수 아님.",
        "outcome": "등록 장애인 총수 / 해당 연도 기존 주민등록인구 × 100 (%)",
        "caveat": "동시기 지역 수준의 탐색적 OLS로 인과효과를 의미하지 않음. 연도 통합은 지역 반복측정과 연도효과를 통제하지 않음. 진료비에 비급여가 전부 포함된다는 뜻이 아님.",
        "source_duplicates": duplicates[:50],
        "municipal_total": len(detail),
        "province_total": len(province_rows),
        "municipal_by_variable": {field: sum(r.get(field) is not None for r in detail) for field in checks},
        "province_by_variable": {field: sum(r.get(field) is not None for r in province_rows) for field in checks},
        "municipal_complete_cases": {mode: sum(
            all(r.get(field) is not None for field in (mode, *checks)) for r in detail) for mode in MODES},
        "province_complete_cases": {mode: sum(
            all(r.get(field) is not None for field in (mode, *checks)) for r in province_rows) for mode in MODES},
        "missing_municipal_sample": [
            {"year": r["year"], "province": r["province"], "district": r["district"],
             "fields": [field for field in checks if r.get(field) is None]}
            for r in detail if any(r.get(field) is None for field in checks)
        ][:100],
    }
    audit["multi"] = _emit_models(out, "demographic_multi_models", detail, province_rows,
                                  ("age65_percent", "under15_percent", "fertility", MEDICAL), True)
    for label, field in SIMPLE.items():
        audit[label] = _emit_models(out, f"{label}_ols_models", detail, province_rows, (field,), False)
    if len(disability_types) > 1:
        audit["disability_type_regressions"] = _emit_disability_type_models(
            out, detail, province_rows, disability_types)
        audit["type_regression_note"] = (
            "청각·언어는 경기도 2014~2017년 통합 집계만 사용; "
            "청각/언어로 분리하거나 결측을 0으로 대체하지 않음. "
            "광역 장애유형별 등록률은 하위 지역의 모든 유형 자료가 있는 경우만 사용.")
    _write_json(out / "data" / "age_medical_quality.json", audit)
    print("인구구조·의료비 추가 분석:", json.dumps(
        {key: audit[key] for key in ("municipal_by_variable", "municipal_complete_cases", "multi", "age65", "under15", "medical")}, ensure_ascii=False), flush=True)
    return audit
