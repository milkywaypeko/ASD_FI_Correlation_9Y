#!/usr/bin/env python3
"""Korean municipal disability/fiscal OLS static GitHub Pages builder (2014-2022)."""
from __future__ import annotations
import argparse
import csv
import json
import math
import re
import warnings
import shutil
import gzip
import scipy
from scipy.stats import pearsonr
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import statsmodels.api as sm


# Report each distinct numerical warning once rather than hiding fit diagnostics.
_REPORTED_OLS_WARNINGS = set()

def _report_ols_warnings(captured):
    for item in captured:
        signature = (item.category.__name__, str(item.message))
        if signature not in _REPORTED_OLS_WARNINGS:
            _REPORTED_OLS_WARNINGS.add(signature)
            print(f"[OLS warning] {signature[0]}: {signature[1]}", flush=True)


# ===== Embedded former expanded_analysis.py =====
def _namespace_expanded_analysis():
    """Additional 2014–2022 demographic and medical-expense OLS models.
    
    The source statistics are read-only. All municipality joins use a full
    (year, province, district) key; ward totals are combined only when a city
    total is absent, and missing covariates are never imputed.
    """
    
    
    
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
            with warnings.catch_warnings(record=True) as caught_ols_warnings:
                warnings.simplefilter("always")
                model = sm.OLS(y, design).fit()
                raw = str(model.summary(xname=["const"] + [field.replace("before","fiscal_before").replace("after","fiscal_after") for field in predictors]))
            _report_ols_warnings(caught_ols_warnings)
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
    
        analysis_years = (tuple(range(2015, 2023))
                          if prefix in ("medical_ols_models", "household_premium_ols_models")
                          else YEARS)
        permitted = set(analysis_years)
        by_local = defaultdict(list)
        for row in detail:
            if row["year"] in permitted:
                by_local[(row["province"], row["district"])].append(row)
        total = 0
        for year in analysis_years:
            rows = [r for r in detail if r["year"] == year]
            prov_rows = [r for r in provinces if r["year"] == year]
            for mode in (MODES if fiscal_mode else (None,)):
                group = models(rows, prov_rows, year, mode)
                suffix = f"_{mode}" if mode else ""
                _write_json(out / "data" / f"{prefix}_{year}{suffix}.json", group)
                total += len(group)
    
        pooled, history = [], []
        for mode in (MODES if fiscal_mode else (None,)):
            pooled.extend(models([r for r in detail if r["year"] in permitted],
                                 [r for r in provinces if r["year"] in permitted],
                                 "전기간", mode))
            for (prov, district), rows in sorted(by_local.items()):
                history.append(fit_extended_ols(rows, predictors_for(mode),
                                                "local_history", prov + "|" + district,
                                                "전기간", mode))
        _write_json(out / "data" / f"{prefix}_pooled.json", pooled)
        _write_json(out / "data" / f"{prefix}_local_history.json", history)
        return {"yearly_models": total, "pooled_models": len(pooled),
                "local_history_models": len(history),
                "estimated_models": sum(m["intercept"] is not None for m in pooled + history)}
    
    
    
    # Retired per-disability shard generator removed: unified_analysis now
    # creates the sole active per-type regression index and detail files.

    def build_expanded_analysis(stats: Path, out: Path, detail: list[dict],
                                province_rows: list[dict], disability_types: list[str] | None = None):
        """Enrich observation rows in-place and write requested model sets.
    
        Run after build_multivariate(), so its fertility field has already joined.
        Must run before municipalities.json and provinces.json are written.
        """
        age = parse_age_population(stats / "인구" / "연령(5세)별 주민등록연앙인구.csv")
        costs, duplicates = parse_medical_expenses(stats / "국가건강정보" / "진료비")
        premiums, premium_invalid = parse_insurance_premiums(stats / "국가건강정보" / "보험료")
        household_file = stats / HOUSEHOLD_FILE
        households = parse_household_counts(household_file)
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
            premium = premiums.get(key)
            household_count = households.get(key)
            row["premium_total_thousand_krw"] = premium
            row["households"] = household_count
            row[PREMIUM_FIELD] = household_premium_10k(premium, household_count)
    
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
    
        checks = ("age65_percent", "under15_percent", "fertility", MEDICAL, PREMIUM_FIELD)
        audit = {
            "years": list(YEARS),
            "sources": ["Statistics/인구/연령(5세)별 주민등록연앙인구.csv",
                        "Statistics/국가건강정보/진료비/시군구(...)별 연령별 진료현황-전체.csv",
                        "Statistics/국가건강정보/보험료/시군구(...)별 보험료 현황.csv"],
            "denominators": "0~14세·65세 이상 비율의 분모와 의료비 1인당 분모는 해당 연도 주민등록연앙인구(계).",
            "medical_definition": "전체 연령 진료비(천원) × 1000 ÷ 주민등록연앙인구 ÷ 10000 = 만원/인. 급여비·진료인원수 아님.",
            "outcome": "등록 장애인 총수 / 해당 연도 기존 주민등록인구 × 100 (%)",
            "caveat": "동시기 지역 수준의 탐색적 OLS로 인과효과를 의미하지 않음. 연도 통합은 지역 반복측정과 연도효과를 통제하지 않음. 진료비에 비급여가 전부 포함된다는 뜻이 아님.",
            "source_duplicates": duplicates[:50],
            "premium_source_invalid": premium_invalid[:300],
            "premium_source_invalid_count": len(premium_invalid),
            "premium_sources_2014_invalid_note": "2014년 서울·인천·경기·강원 표의 보험료 5항목 합계 불일치 자료는 진료비 혼입으로 판단하여 제외. 원본은 보존함.",
            "premium_total_available": len(premiums),
            "household_file": str(HOUSEHOLD_FILE),
            "household_available": len(households),
            "premium_definition": "연간 건강보험료 총액(천원) ÷ 주민등록세대수 ÷ 10 = 만원/세대/년. 직장+지역 전체(가입자 및 사용자 부담 포함 가능). 보험가입 세대별 실제 고지액이 아님.",
            "premium_missing_households_warning": (None if households else
                "주민등록세대수.csv가 없어 모든 가구당 보험료 회귀가 추정 불가입니다. 수치를 임의 추정하지 않습니다."),
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
        # Legacy five-variable and duplicate six-variable generations are retired.
        # The seven current models (all disability types) share the unified builder.
        for label, field in SIMPLE.items():
            audit[label] = _emit_models(out, f"{label}_ols_models", detail, province_rows, (field,), False)
        audit["household_premium_ols"] = _emit_models(
            out, "household_premium_ols_models", detail, province_rows,
            (PREMIUM_FIELD,), False)
        audit["type_regression_note"] = (
            "청각·언어는 경기도 2014~2017년 통합 집계만 사용; "
            "청각/언어로 분리하거나 결측을 0으로 대체하지 않음. "
            "광역 장애유형별 등록률은 모든 하위 지역의 유형 자료가 있을 때만 사용.")
        _write_json(out / "data" / "age_medical_quality.json", audit)
        print("인구구조·의료비 추가 분석:", json.dumps(
            {key: audit[key] for key in ("municipal_by_variable", "municipal_complete_cases", "age65", "under15", "medical")}, ensure_ascii=False), flush=True)
        return audit
    return locals()

_expanded_analysis = _namespace_expanded_analysis()

# Export the expanded helpers for downstream sections and unit tests.
globals().update({key: value for key, value in _expanded_analysis.items() if not key.startswith('__')})

# ===== Embedded former insurance_premiums.py =====
def _namespace_insurance_premiums():
    PROVINCES = _expanded_analysis['PROVINCES']
    province_name = _expanded_analysis['province_name']
    district_name = _expanded_analysis['district_name']
    number = _expanded_analysis['number']
    YEARS = _expanded_analysis['YEARS']
    _parent_city = _expanded_analysis['_parent_city']
    """Insurance premium totals and *observed* household denominators.
    
    Never divide by population, patients, or assumed persons per household: doing so
    would change the estimand. The optional household-count CSV is required for
    premium-per-household regression and is documented in Statistics/README.md.
    """
    
    PREMIUM_FIELD = "premium_10k_per_household"
    PREMIUM_FILE_PATTERN = "시군구*별 보험료 현황.csv"
    HOUSEHOLD_FILE = Path("인구/행정구역(시군구)별 주민등록세대수.csv")
    
    
    def _rows(path: Path):
        for encoding in ("utf-8-sig", "cp949", "euc-kr"):
            try:
                with path.open(newline="", encoding=encoding) as f:
                    return list(csv.reader(f))
            except UnicodeDecodeError:
                continue
        raise ValueError(f"잘못된 CSV 인코딩: {path}")
    
    
    def _year_header_index(row: list[str]):
        return [(i, int(match.group(1))) for i, value in enumerate(row)
                if (match := re.fullmatch(r"\s*(20\d{2})\s*(?:년)?\s*", value))
                and int(match.group(1)) in YEARS]
    
    
    def _comparable(a: float, b: float) -> bool:
        # Source values can be rounded to the nearest thousand KRW.
        return abs(a - b) <= max(3.0, 1e-8 * max(abs(a), abs(b)))
    
    
    def parse_insurance_premiums(folder: Path):
        """Read four NHIS annual total-premium files (unit: *thousand KRW*).
    
        A 5-column block for a given year represents total, workplace total,
        employee, public/teacher and regional total, respectively. Check the
        accounting identities before trusting any row. This catches the user-
        supplied Seoul/Incheon/Gyeonggi/Gangwon 2014 block, which is mis-sourced.
        """
        values = {}
        invalid = []
        paths = sorted(folder.glob(PREMIUM_FILE_PATTERN))
        if len(paths) != 4:
            raise ValueError(f"가구 건강보험료 CSV 4개가 필요합니다: 발견 {len(paths)} ({folder})")
        for path in paths:
            rows = _rows(path)
            if len(rows) < 4 or len(rows[0]) != len(rows[1]) or len(rows[1]) != len(rows[2]):
                raise ValueError(f"건강보험료 CSV 표 머리글 오류: {path}")
            blocks = []
            for year in YEARS:
                cols = [i for i, y in _year_header_index(rows[0]) if y == year]
                expected = [("합계", "소계"), ("직장", "소계"),
                            ("직장", "근로자"), ("직장", "공·교"), ("지역", "소계")]
                if len(cols) != 5 or [(rows[1][i].strip(), rows[2][i].strip()) for i in cols] != expected:
                    raise ValueError(f"건강보험료 헤더 연도별 5개 항목 불일치: {path} {year}")
                blocks.append((year, cols))
            for row in rows[3:]:
                if not row or len(row) < len(rows[0]):
                    continue
                prov = province_name(row[0])
                if prov not in PROVINCES:
                    continue
                # Jeju/Sejong parent subtotal is the dashboard's only comparable unit.
                # Do not duplicate that subtotal with the administrative city rows.
                if prov in ("제주특별자치도", "세종특별자치시") and row[1].strip() not in ("소계", "합계"):
                    continue
                district = prov if row[1].strip() in ("소계", "합계") else district_name(prov, row[1])
                for year, cols in blocks:
                    nums = [number(row[i]) for i in cols]
                    if any(x is None or x < 0 for x in nums):
                        continue
                    total, workplace, employee, public, regional = nums
                    if (not _comparable(total, workplace + regional) or
                        not _comparable(workplace, employee + public)):
                        invalid.append({"year": year, "province": prov, "district": district,
                                        "source": path.name, "reason": "보험료 합계 ≠ 직장+지역 / 직장 ≠ 근로자+공·교"})
                        continue
                    key = (year, prov, district)
                    if key in values and not _comparable(values[key], total):
                        invalid.append({"year": year, "province": prov, "district": district,
                                        "source": path.name, "reason": "중복 관측치 불일치"})
                        continue
                    values[key] = total
        # If a city total exists, never add its wards on top. Otherwise combine wards.
        wards = defaultdict(list)
        for (year, prov, district), amount in values.items():
            parent = _parent_city(district)
            if parent:
                wards[(year, prov, parent)].append(amount)
        for key, amounts in wards.items():
            if key not in values:
                values[key] = sum(amounts)
        return values, invalid
    
    
    def parse_household_counts(path: Path):
        """Parse positive registered household counts; supports long and KOSIS-wide CSV.
    
        Accepted long columns: 연도,시도,시군구,세대수 (exact values, NOT household size).
        Accepted wide: region then 2014..2022 columns, optional year-metric header.
        A missing file produces no households and no insurance estimates.
        """
        if not path.exists():
            return {}
        rows = _rows(path)
        if not rows:
            return {}
        header = [x.strip().lstrip("\ufeff") for x in rows[0]]
        out = {}
        if {"연도", "시도", "시군구", "세대수"} <= set(header):
            fields = {name: header.index(name) for name in ("연도", "시도", "시군구", "세대수")}
            source = [{name: row[idx] for name, idx in fields.items()} for row in rows[1:]
                      if len(row) > max(fields.values())]
            for row in source:
                if not row["연도"].strip().isdigit():
                    continue
                year = int(row["연도"].strip())
                if year not in YEARS:
                    continue
                prov = province_name(row["시도"])
                if prov not in PROVINCES:
                    continue
                raw_district = row["시군구"].strip()
                district = (prov if raw_district in ("전체", "계", "합계", "소계", prov)
                            else district_name(prov, raw_district))
                val = number(row["세대수"])
                if val is None or val <= 0 or not val.is_integer():
                    continue
                key = (year, prov, district)
                if key in out and out[key] != int(val):
                    raise ValueError(f"주민등록세대수 중복 충돌: {key}")
                out[key] = int(val)
        else:
            years = _year_header_index(header)
            if not years:
                raise ValueError("세대수 CSV 형식이 잘못되었습니다. 연도,시도,시군구,세대수 열이 필요합니다.")
            province = None
            parent_city = None  # Source sometimes lists ward rows directly after a city subtotal.
            start = 1
            two_locations = len(header)>1 and ("별(2)" in header[1] or header[1] in ("시군구", "행정구역(2)"))
            if len(rows) > 1 and any("세대" in x for x in rows[1][1:]):
                # Multiple KOSIS measures per year: use only explicit household counts.
                years = [(i, y) for i, y in years if i < len(rows[1])
                         and ("세대수" in rows[1][i] or "총세대" in rows[1][i])]
                if not years:
                    raise ValueError("세대수에 해당하는 연도별 열이 없습니다.")
                start = 2
            for row in rows[start:]:
                if not row:
                    continue
                area = province_name(row[0])
                if area == "전국":
                    continue
                if two_locations:
                    if area not in PROVINCES or len(row) < 2:
                        continue
                    province = area
                    local = row[1].strip()
                    if province in ("세종특별자치시", "제주특별자치도") and local not in ("소계", "합계", "계", "전체"):
                        continue
                    district = (province if local in ("소계", "합계", "계", "전체")
                                else district_name(province, local))
                elif area in PROVINCES:
                    province = area
                    district = area
                    parent_city = None
                elif province:
                    if province in ("세종특별자치시", "제주특별자치도"):
                        continue
                    district = district_name(province, row[0])
                    if district.endswith("시"):
                        # City total already exists; its following ward rows are not
                        # separate municipality observations and must not be pooled.
                        parent_city = district
                    elif district.endswith("군"):
                        parent_city = None
                    elif district.endswith("구") and parent_city is not None:
                        # E.g. Bucheon lists its wards (including duplicated 오정구).
                        # City-level household count above is authoritative.
                        continue
                else:
                    continue
                for index, year in years:
                    val = number(row[index] if index < len(row) else "")
                    if val is not None and val > 0 and val.is_integer():
                        key = (year, province, district)
                        if key in out and out[key] != int(val):
                            raise ValueError(f"주민등록세대수 중복 충돌: {key}")
                        out[key] = int(val)
        # Aggregate child wards only when the source lacks its city-level count.
        wards = defaultdict(list)
        for (year, prov, district), n in out.items():
            parent = _parent_city(district)
            if parent:
                wards[(year, prov, parent)].append(n)
        for key, vals in wards.items():
            if key not in out:
                out[key] = sum(vals)
        return out
    
    
    def household_premium_10k(total_thousand_krw, households):
        """Annual insurance premium in units 10,000 KRW per *registered household*."""
        if total_thousand_krw is None or households is None or households <= 0:
            return None
        return round(total_thousand_krw / (10 * households), 12)
    return locals()

_insurance_premiums = _namespace_insurance_premiums()

globals().update({key: value for key, value in _insurance_premiums.items() if not key.startswith('__')})

# ===== Embedded former unified_analysis.py =====
def _namespace_unified_analysis():
    PROVINCES = _expanded_analysis['PROVINCES']
    fit_extended_ols = _expanded_analysis['fit_extended_ols']
    """Unified, reproducible statsmodels OLS index and lazy details.
    
    The same fitted model supplies index statistics, its unabridged summary(),
    and exact complete-case observations with predictions and residuals.
    Original Statistics CSV files are never modified.
    """
    
    
    
    
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
    
    
    
    def _number_or_none(value):
        """Convert numeric SciPy values to JSON-safe numbers, never impute zero."""
        try:
            converted = float(value)
            return converted if math.isfinite(converted) else None
        except (TypeError, ValueError):
            return None
    
    
    def _scipy_pearson_result(xs, ys):
        """Actual two-sided scipy.stats.pearsonr and its raw return object.
    
        Inputs are the *identical* model complete-case sample used by OLS.
        A undefined r, p or interval stays null; observed pairs are retained
        separately in detail["observations"] and are never modified.
        """
        n = len(xs)
        result = {
            "method": "scipy.stats.pearsonr",
            "n": n,
            "alternative": "two-sided",
            "statistic": None,
            "pvalue": None,
            "confidence_level": 0.95,
            "confidence_interval": {"low": None, "high": None},
            "raw": None,
            "raw_confidence_interval": None,
            "warnings": [],
            "reason": None,
        }
        if n != len(ys):
            raise AssertionError("SciPy X/Y paired sample lengths differ")
        if n < 2:
            result["reason"] = "표본 n<2: 피어슨 상관계수 계산 불가"
            return result
        if all(x == xs[0] for x in xs) or all(y == ys[0] for y in ys):
            result["reason"] = "X 또는 Y가 상수: 피어슨 상관계수 정의되지 않음"
            return result
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            raw = pearsonr(xs, ys, alternative="two-sided")
            interval = raw.confidence_interval(confidence_level=0.95)
        result["raw"] = repr(raw)
        result["raw_confidence_interval"] = repr(interval)
        result["statistic"] = _number_or_none(raw.statistic)
        result["pvalue"] = _number_or_none(raw.pvalue)
        result["confidence_interval"] = {
            "low": _number_or_none(interval.low),
            "high": _number_or_none(interval.high),
        }
        result["warnings"] = [str(item.message) for item in caught]
        if result["statistic"] is None:
            result["reason"] = "SciPy가 정의되지 않은 r을 반환함"
        elif result["pvalue"] is None:
            result["reason"] = "SciPy가 유효하지 않은 p값을 반환함"
        if result["confidence_interval"]["low"] is None:
            result["warnings"].append("표본이 작아 95% 신뢰구간을 계산할 수 없음")
        return result
    
    
    def _pearson_correlation(xs, ys):
        """Compatibility wrapper; the statistic now comes only from SciPy."""
        return _scipy_pearson_result(xs, ys)["statistic"]
    
    
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
        scipy_results = [
            _scipy_pearson_result(
                [float(row[field]) for row in complete], y_values
            ) for field in fields
        ]
        correlations = [entry["statistic"] for entry in scipy_results]
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
            "correlation_pvalues": [entry["pvalue"] for entry in scipy_results],
            "warning": model["warning"],
        }
        detail = {
            "model": model,
            "correlations": {
                "method": "pearson",
                "library": "scipy.stats.pearsonr",
                "scipy_version": scipy.__version__,
                "alternative": "two-sided",
                "sample_n": len(complete),
                "predictors": dict(zip(fields, correlations)),
                "scipy": dict(zip(fields, scipy_results)),
            },
            "columns": ["year", "province", "district", "registered_rate_percent",
                        *fields, "prediction_percent", "residual_percentage_points"],
            "observations": observations,
            "notes": {
                "outcome": "해당 장애유형 등록인원 ÷ 해당 연도·지역 주민등록인구 × 100 (%)",
                "prediction": "동일 statsmodels OLS 모형으로 계산한 관측치별 적합값",
                "inference": "통계적 연관성만 분석하며 인과관계를 입증하지 않습니다.",
                "correlation": "피어슨 r, 양측 p값, 95% Fisher 신뢰구간은 scipy.stats.pearsonr에서 반환됩니다. 모형에 사용된 동일 완전관측치의 Y와 각 X 간 비가중 이변량 상관이며 편상관이나 다중회귀 β가 아닙니다. n<2 또는 상수 변수인 경우 null; 표본 n<=3이면 신뢰구간이 정의되지 않을 수 있습니다.",
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
    
        import time
        for key, spec in SPECS.items():
            started = time.perf_counter()
            allowed = set(spec["years"])
            annual = {y: [r for r in detail if r["year"] == y] for y in spec["years"]}
            annual_prov = {y: [r for r in provinces if r["year"] == y] for y in spec["years"]}
            pooled = [r for r in detail if r["year"] in allowed]
            pooled_prov = [r for r in provinces if r["year"] in allowed]
            history = {region: [r for r in rows if r["year"] in allowed]
                       for region, rows in local_groups.items()}
            grouped_periods = {}
            for period in (*spec["years"], "pooled"):
                subset = pooled if period == "pooled" else annual[period]
                grouped = defaultdict(list)
                for row in subset:
                    grouped[row["province"]].append(row)
                grouped_periods[period] = grouped
            history_scopes = [("local_history", prov + "|" + dist, rows)
                              for (prov, dist), rows in sorted(history.items())]
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
                        scopes = history_scopes
                        model_period = "전기간"
                    else:
                        subset = pooled if period == "pooled" else annual[period]
                        subset_prov = pooled_prov if period == "pooled" else annual_prov[period]
                        # Build province partitions once per period rather than
                        # rescanning all rows for every disability type.
                        groups = grouped_periods[period]
                        scopes = [("municipal", "전국", subset)]
                        scopes.extend(("municipal", province, groups[province])
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
            print("통합 OLS", key, results[key], f"elapsed={time.perf_counter()-started:.1f}s", flush=True)
    
        _save(out / "data" / "unified_manifest.json", {
            "types": types, "provinces": PROVINCES,
            "labels": LABELS,
            "models": {
                key: {"label": cfg["label"], "years": list(cfg["years"]),
                      "fiscal": cfg["fiscal"], "fields": list(cfg["fields"])}
                for key, cfg in SPECS.items()
            },
            "limitations": [
                "피어슨 r, 양측검정 p값, 95% 신뢰구간은 scipy.stats.pearsonr로 동일 완전관측치에서 계산하며, 다중회귀 β 또는 편상관이 아닙니다.",
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
    return locals()

_unified_analysis = _namespace_unified_analysis()

globals().update({key: value for key, value in _unified_analysis.items() if not key.startswith('__')})

YEARS = tuple(range(2014, 2023))
MODES = ("before", "after")
TYPES = ["전체", "지체", "뇌병변", "시각", "청각", "언어", "청각·언어", "지적", "자폐성", "정신", "신장", "심장", "호흡기", "간", "안면", "장루·요루", "뇌전증"]
FILE_TO_PROVINCE = {
    "Seoul": "서울특별시", "Busan": "부산광역시", "Daegu": "대구광역시", "Incheon": "인천광역시",
    "Gwangju": "광주광역시", "Daejeon": "대전광역시", "Ulsan": "울산광역시", "Sejong": "세종특별자치시",
    "Gyeonggi-do": "경기도", "Gangwon-do": "강원특별자치도", "Chungcheongbuk-do": "충청북도",
    "Chungcheongnam-do": "충청남도", "Jeollabuk-do": "전북특별자치도", "Jeollanam-do": "전라남도",
    "Gyeongsangbuk-do": "경상북도", "Gyeongsangnam-do": "경상남도", "Jeju": "제주특별자치도",
}
SPECIAL = {"세종특별자치시", "제주특별자치도"}
PROVINCES = list(FILE_TO_PROVINCE.values())
PROVINCE_ALIASES = {"강원도": "강원특별자치도", "전라북도": "전북특별자치도"}


def read_rows(path: Path) -> list[list[str]]:
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            with path.open("r", encoding=encoding, newline="") as f:
                return list(csv.reader(f))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"인코딩을 읽을 수 없습니다: {path}")


def num(v: str) -> float | None:
    v = (v or "").strip().replace(",", "")
    if v in ("", "-", "…", "X", "x", "N/A"):
        return None
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except ValueError:
        return None


def clean_province(s: str) -> str:
    return PROVINCE_ALIASES.get(s.strip(), s.strip())


def clean_district(province: str, district: str) -> str:
    district = district.strip()
    if province in SPECIAL:
        return province
    if district.startswith("충북 "):
        district = district.removeprefix("충북 ")
    if district.startswith("경기 "):
        district = district.removeprefix("경기 ")
    if province == "인천광역시" and district == "남구":
        district = "미추홀구"
    return district


def clean_disability_type(name: str) -> str:
    name = re.sub(r"\s+", "", name.strip()).replace("장애", "")
    if "장루" in name and "요루" in name:
        return "장루·요루"
    name = name.replace("청각,언어", "청각·언어")
    return name


def parse_population(path: Path):
    rows = read_rows(path)
    year_cols = [(i, int(h)) for i, h in enumerate(rows[0]) if h.isdigit() and int(h) in YEARS]
    province = None
    local = {}
    total = {}
    errors = []
    for row in rows[2:]:
        if not row or not row[0].strip() or row[0] == "전국":
            continue
        name = clean_province(row[0])
        if name in PROVINCES:
            province = name
            for i, y in year_cols:
                province_population = num(row[i])
                if province_population is not None and province_population > 0:
                    total[(y, province)] = int(province_population)
            continue
        if province is None:
            continue
        if province in SPECIAL:
            # The province total is already present. Jeju has two administrative
            # cities and Sejong repeats a city total: do not treat child rows as
            # separate values or flag their expected differences as duplicates.
            continue
        district = clean_district(province, row[0])
        # Skip child administrative districts / field offices because the source also
        # provides a parent city total. Only merge keys that exist in the disability source.
        for i, y in year_cols:
            district_population = num(row[i])
            if district_population is not None and district_population > 0:
                key = (y, province, district)
                if key in local and local[key] != int(district_population):
                    errors.append(f"인구 중복: {key} {local[key]} vs {district_population}")
                local[key] = int(district_population)
    for (y, province), value in total.items():
        if province in SPECIAL:
            local[(y, province, province)] = value
    return local, total, errors


def parse_fiscal(path: Path):
    rows = read_rows(path)
    columns = [(i, int(y), "after" if "개편후" in rows[1][i] else "before")
               for i, y in enumerate(rows[0]) if y.isdigit() and int(y) in YEARS]
    local = {}
    totals = {}
    duplicates = []
    for row in rows[2:]:
        if len(row) < 2:
            continue
        province, district = clean_province(row[0]), row[1].strip()
        if province not in PROVINCES:
            continue
        for i, year, mode in columns:
            value = num(row[i])
            if value is None:
                continue
            if not 0 <= value <= 100:
                raise ValueError(f"재정자립도가 0~100 밖입니다: {year} {province} {district} {mode}: {value}")
            # 원본 CSV의 백분율(0~100)은 변경하지 않고, 빌드 시 (0~1)로 변환.
            value = round(value / 100.0, 12)
            if district == "소계":
                totals[(year, province, mode)] = value
            else:
                district = clean_district(province, row[1])
                key = (year, province, district, mode)
                if key in local and local[key] != value:
                    duplicates.append(f"재정자립도 중복: {key}: {local[key]} vs {value}")
                local[key] = value
    for (year, prov, mode), value in totals.items():
        if prov in SPECIAL:
            local[(year, prov, prov, mode)] = value
    return local, totals, duplicates


def parse_disability(folder: Path):
    records = defaultdict(dict)
    unknown = Counter()
    duplicated = []
    for file in sorted(folder.glob("Population of the disabled in *.csv")):
        name = file.stem[len("Population of the disabled in "):]
        if name not in FILE_TO_PROVINCE:
            raise ValueError(f"알 수 없는 광역시도 파일: {file.name}")
        prov = FILE_TO_PROVINCE[name]
        rows = read_rows(file)
        year_cols = [(i, int(h)) for i, h in enumerate(rows[0]) if h.isdigit() and int(h) in YEARS]
        if not year_cols:
            raise ValueError(f"2014-2022 연도를 발견하지 못했습니다: {file.name}")
        year_start = min(i for i, _ in year_cols)
        # Gyeonggi: '남부/북부' then city; Seoul: '서울시' then gu.
        # All others use their third field. Jeju/Sejong use a single '합계' row.
        district_col = 3 if name in ("Gyeonggi-do", "Seoul") else 2
        data_start = 2 if name == "Seoul" else 1
        for row in rows[data_start:]:
            if len(row) <= max(i for i, _ in year_cols):
                continue
            dtype = clean_disability_type(row[1])
            if dtype not in TYPES:
                unknown[(name, dtype)] += 1
                continue
            district = clean_district(prov, row[district_col])
            if district in ("소계", "합계", "총계") and prov not in SPECIAL:
                continue
            if prov in SPECIAL:
                district = prov
            for idx, year in year_cols:
                val = num(row[idx])
                if val is None:
                    continue
                key = (year, prov, district)
                if dtype in records[key] and records[key][dtype] != int(val):
                    duplicated.append(f"장애유형 중복: {key} {dtype}")
                records[key][dtype] = int(val)
    return records, dict(unknown), duplicated


def finite(value):
    if value is None:
        return None
    value = float(value)
    return round(value, 12) if math.isfinite(value) else None


def finite_probability(value):
    """Preserve small p-values: rounding to 12 decimal places would turn 1e-40 into 0."""
    v = float(value)
    return v if math.isfinite(v) else None


def fit_model(obs: list[dict], scope: str, region: str, year: str | int,
              dtype: str, mode: str, raw_group: list[str]):
    valid = []
    for r in obs:
        x = r.get(mode)
        y = r.get("rates", {}).get(dtype)
        if x is not None and y is not None and math.isfinite(x) and math.isfinite(y):
            valid.append((float(x), float(y)))
    n = len(valid)
    result = {"scope": scope, "region": region, "year": year, "type": dtype,
              "mode": mode, "n": n, "slope": None, "intercept": None,
              "r2": None, "p": None, "warning": None, "raw": None}
    if n < 3:
        result["warning"] = "유효 관측치가 3개 미만입니다."
        return result
    xs, ys = np.array(valid, dtype=float).T
    if np.ptp(xs) < 1e-12:
        result["warning"] = "재정자립도 값이 모두 같아 회귀할 수 없습니다."
        return result
    X = sm.add_constant(xs, has_constant="add")
    model = sm.OLS(ys, X).fit()
    result.update(intercept=finite(model.params[0]), slope=finite(model.params[1]),
                  r2=finite(model.rsquared), p=finite_probability(model.pvalues[1]))
    with warnings.catch_warnings(record=True) as caught_ols_warnings:
        warnings.simplefilter("always")
        result["raw"] = str(model.summary())
    _report_ols_warnings(caught_ols_warnings)
    raw_group.append(f"\n{'=' * 78}\nscope={scope}, region={region}, year={year}, type={dtype}, mode={mode}, n={n}\n" + result["raw"] + "\n")
    return result



def parse_birth_rate(path: Path):
    """KOSIS-style TFR CSV: province headings followed by districts.

    Child wards in incorporated cities are ignored at integration time: only
    exact (year, province, municipality) keys from the disability dataset join.
    Historical district aliases are resolved BEFORE data matching; missing
    values (e.g. pre-2018 미추홀구) never replace valid data.
    """
    rows = read_rows(path)
    if not rows or rows[0][0].strip('\ufeff') != "시군구별":
        raise ValueError(f"출산율 헤더가 예상과 다릅니다: {path}")
    year_cols = [(i, int(s)) for i, s in enumerate(rows[0]) if s.isdigit() and int(s) in YEARS]
    if {y for _, y in year_cols} != set(YEARS):
        raise ValueError("Birth rate.csv에 2014~2022년 열이 모두 필요합니다.")
    local, totals, duplicates = {}, {}, []
    province = None
    for row in rows[2:]:
        if not row or not row[0].strip():
            continue
        name = clean_province(row[0])
        if name in PROVINCES:
            province = name
            for i, y in year_cols:
                val = num(row[i] if i < len(row) else "")
                if val is not None:
                    totals[(y, province)] = val
            continue
        if province is None or province in SPECIAL:
            continue
        # e.g. '남구(변동전)', '군위군(변동전)'
        district = re.sub(r"\s*\([^()]*변동[^()]*\)\s*$", "", row[0]).strip()
        district = clean_district(province, district)
        for i, y in year_cols:
            value = num(row[i] if i < len(row) else "")
            if value is None:
                continue
            key = (y, province, district)
            if key in local and abs(local[key] - value) > 1e-10:
                duplicates.append(f"합계출산율 중복: {key}: {local[key]} vs {value}")
            local[key] = value
    for (y, prov), val in totals.items():
        if prov in SPECIAL:
            local[(y, prov, prov)] = val
    return local, totals, duplicates


def fit_multivariate(obs: list[dict], scope: str, region: str,
                     year: str | int, mode: str, raw_group: list[str], dtype: str = "자폐성"):
    """Selected disability registration rate (%) ~ fiscal fraction [0,1] + TFR."""
    valid = [r for r in obs if r.get(mode) is not None
             and r.get("fertility") is not None
             and r.get("rates", {}).get(dtype) is not None]
    result = {"scope": scope, "region": region, "year": year, "mode": mode, "type": dtype,
              "n": len(valid), "intercept": None, "fiscal_coef": None,
              "fertility_coef": None, "r2": None, "adj_r2": None,
              "p_fiscal": None, "p_fertility": None, "p_model": None,
              "fiscal_ci": None, "fertility_ci": None, "se_fiscal": None,
              "se_fertility": None, "vif": None, "warning": None, "raw": None}
    if len(valid) < 4:
        result["warning"] = "절편과 두 독립변수 추정에는 4개 이상의 유효 관측치가 필요합니다."
        return result
    z = np.asarray([[r[mode], r["fertility"], r["rates"][dtype]] for r in valid], dtype=float)
    if not np.isfinite(z).all():
        result["warning"] = "유효하지 않은 수치가 포함되었습니다."
        return result
    x = sm.add_constant(z[:, :2], has_constant="add")
    if np.linalg.matrix_rank(x) != 3:
        result["warning"] = "독립변수 중 상수 또는 완전 선형종속 항목이 있어 추정할 수 없습니다."
        return result
    try:
        with warnings.catch_warnings(record=True) as caught_ols_warnings:
            warnings.simplefilter("always")
            model = sm.OLS(z[:, 2], x).fit()
            raw = str(model.summary(xname=["const", "fiscal_independence_0to1", "total_fertility_rate"]))
        _report_ols_warnings(caught_ols_warnings)
    except (ValueError, np.linalg.LinAlgError) as ex:
        result["warning"] = f"회귀계산 오류: {ex}"
        return result
    ci = model.conf_int(alpha=.05)
    c = np.corrcoef(z[:, 0], z[:, 1])[0, 1]
    vif = (1 / (1 - c*c)) if math.isfinite(c) and abs(c) < 1 else None
    result.update(intercept=finite(model.params[0]),
                  fiscal_coef=finite(model.params[1]), fertility_coef=finite(model.params[2]),
                  r2=finite(model.rsquared), adj_r2=finite(model.rsquared_adj),
                  p_fiscal=finite_probability(model.pvalues[1]),
                  p_fertility=finite_probability(model.pvalues[2]),
                  p_model=finite_probability(model.f_pvalue),
                  fiscal_ci=[finite(ci[1, 0]), finite(ci[1, 1])],
                  fertility_ci=[finite(ci[2, 0]), finite(ci[2, 1])],
                  se_fiscal=finite(model.bse[1]), se_fertility=finite(model.bse[2]),
                  vif=finite(vif), raw=raw)
    raw_group.append(f"\n{'=' * 80}\nscope={scope}, region={region}, year={year}, type={dtype}, mode={mode}, n={len(valid)}\n" + raw + "\n")
    return result


def build_multivariate(stats: Path, out: Path, detail: list[dict], province_rows: list[dict]):
    birth, totals, duplicates = parse_birth_rate(stats / "출산율" / "Birth rate.csv")
    missing_local = []
    for r in detail:
        r["fertility"] = birth.get((r["year"], r["province"], r["district"]))
        if r["fertility"] is None:
            missing_local.append({"year": r["year"], "province": r["province"], "district": r["district"]})
    missing_province = []
    for r in province_rows:
        # Provincial fertility is ALWAYS the published province subtotal, not
        # an unweighted average of municipal TFR figures.
        r["fertility"] = totals.get((r["year"], r["province"]))
        if r["fertility"] is None:
            missing_province.append({"year": r["year"], "province": r["province"]})
    # Every disability category is modeled independently. Missing source categories
    # remain missing: e.g. hearing+language combined in Gyeonggi until 2017.
    for year in YEARS:
        yr = [r for r in detail if r["year"] == year]
        yr_prov = [r for r in province_rows if r["year"] == year]
        by_prov = {prov: [r for r in yr if r["province"] == prov] for prov in PROVINCES}
        for mode in MODES:
            models, dumps = [], []
            for dtype in TYPES:
                models.append(fit_multivariate(yr, "municipal", "전국", year, mode, dumps, dtype))
                for province in PROVINCES:
                    models.append(fit_multivariate(by_prov[province], "municipal", province,
                                                   year, mode, dumps, dtype))
                models.append(fit_multivariate(yr_prov, "provincial", "전국", year, mode, dumps, dtype))
            write_json(out / "data" / f"multi_models_{year}_{mode}.json", models)
            (out / "raw" / f"MULTI_{year}_{mode}.txt").write_text("".join(dumps), encoding="utf-8")
            print(f"  다중회귀 {year} {mode}: {len(models)} models", flush=True)
    pooled, history = [], []
    grouped = defaultdict(list)
    for r in detail:
        grouped[(r["province"], r["district"])].append(r)
    for mode in MODES:
        dumps = []
        for dtype in TYPES:
            pooled.append(fit_multivariate(detail, "municipal", "전국", "전기간", mode, dumps, dtype))
            for province in PROVINCES:
                subset = [r for r in detail if r["province"] == province]
                pooled.append(fit_multivariate(subset, "municipal", province,
                                               "전기간", mode, dumps, dtype))
            pooled.append(fit_multivariate(province_rows, "provincial", "전국", "전기간", mode, dumps, dtype))
        (out / "raw" / f"MULTI_pooled_{mode}.txt").write_text("".join(dumps), encoding="utf-8")
        dumps = []
        for (province, district), rlist in sorted(grouped.items()):
            for dtype in TYPES:
                history.append(fit_multivariate(rlist, "local_history",
                                                province + "|" + district,
                                                "전기간", mode, dumps, dtype))
        (out / "raw" / f"MULTI_local_history_{mode}.txt").write_text("".join(dumps), encoding="utf-8")
    write_json(out / "data" / "multi_models_pooled.json", pooled)
    write_json(out / "data" / "multi_models_local_history.json", history)
    autism_complete = [r for r in detail if r.get("rates", {}).get("자폐성") is not None
                       and r.get("fertility") is not None]
    autism_missing = [{"year": r["year"], "province": r["province"], "district": r["district"]}
                      for r in detail if r.get("rates", {}).get("자폐성") is None]
    audit = {"source": "Statistics/Birth rate.csv", "indicator": "합계출산율 (여성 1명당 출생아 수)",
             "autism_usable_municipal": len(autism_complete), "autism_missing_municipal": autism_missing,
             "municipal_matched": len(detail) - len(missing_local), "municipal_total": len(detail),
             "province_matched": len(province_rows) - len(missing_province),
             "province_total": len(province_rows),
             "unmatched_municipal": missing_local, "unmatched_province": missing_province,
             "duplicate_birth_rows": duplicates,
             "model": "선택 장애유형 등록률(전체 주민등록인구 대비 %) = 절편 + β재정 × 재정자립도(0~1) + β출산 × 합계출산율(명/여성)",
             "types": TYPES, "models_yearly": len(YEARS)*len(MODES)*(len(PROVINCES)+2)*len(TYPES),
             "models_pooled": len(pooled), "models_local_history": len(history),
             "note": "연도별 또는 시점 통합 OLS. 같은 해 합계출산율은 전체 연령의 장애등록자와 출생 코호트가 달라 인과효과를 의미하지 않음. 통합모형은 지역 반복관측, 연도효과, 지역 고정효과를 통제하지 않음."}
    write_json(out / "data" / "multi_quality.json", audit)
    print(f"  다중회귀: 기초 출산율 결합 {audit['municipal_matched']}/{len(detail)}, "
          f"광역 {audit['province_matched']}/{len(province_rows)}, "
          f"연도별 모형 {len(YEARS)*len(MODES)*(len(PROVINCES)+2)*len(TYPES)}건, "
          f"통합 {len(pooled)}건, 개별 시계열 {len(history)}건", flush=True)
    return audit

def fit_birth_ols(obs: list[dict], scope: str, region: str,
                  year: str | int, raw_group: list[str], dtype: str = "자폐성"):
    """Simple OLS: selected disability registration (%) = b0 + b1 * TFR.

    Fiscal independence does not enter this model. Records with a missing
    disability rate or TFR are excluded, never imputed as zero.
    """
    valid = [(float(r["fertility"]), float(r["rates"][dtype])) for r in obs
             if r.get("fertility") is not None and r.get("rates", {}).get(dtype) is not None
             and math.isfinite(float(r["fertility"]))
             and math.isfinite(float(r["rates"][dtype]))]
    n = len(valid)
    model_result = {"scope": scope, "region": region, "year": year, "type": dtype,
                    "n": n, "slope": None, "intercept": None, "r2": None,
                    "adj_r2": None, "p": None, "slope_ci": None,
                    "warning": None, "raw": None}
    if n < 3:
        model_result["warning"] = "유효 관측치가 3개 미만이어서 OLS를 적합할 수 없습니다."
        return model_result
    x, y = np.asarray(valid, dtype=float).T
    if np.ptp(x) < 1e-12:
        model_result["warning"] = "합계출산율 관측값이 모두 같아 기울기를 추정할 수 없습니다."
        return model_result
    with warnings.catch_warnings(record=True) as caught_ols_warnings:
        warnings.simplefilter("always")
        result = sm.OLS(y, sm.add_constant(x, has_constant="add")).fit()
        raw = str(result.summary(xname=["const", "total_fertility_rate"]))
    _report_ols_warnings(caught_ols_warnings)
    ci = result.conf_int(alpha=0.05)
    model_result.update(intercept=finite(result.params[0]), slope=finite(result.params[1]),
                        r2=finite(result.rsquared), adj_r2=finite(result.rsquared_adj),
                        p=finite_probability(result.pvalues[1]),
                        slope_ci=[finite(ci[1, 0]), finite(ci[1, 1])], raw=raw)
    raw_group.append(f"\n{'=' * 80}\nscope={scope}, region={region}, year={year}, type={dtype}, n={n}\n" + raw + "\n")
    return model_result


def build_birth_ols(out: Path, detail: list[dict], province_rows: list[dict]):
    """Persist year, pooled, and single-district time-series OLS outputs."""
    model_count = 0
    for year in YEARS:
        year_rows = [r for r in detail if r["year"] == year]
        year_provinces = [r for r in province_rows if r["year"] == year]
        by_prov = {prov: [r for r in year_rows if r["province"] == prov] for prov in PROVINCES}
        models, dumps = [], []
        for dtype in TYPES:
            models.append(fit_birth_ols(year_rows, "municipal", "전국", year, dumps, dtype))
            for province in PROVINCES:
                models.append(fit_birth_ols(by_prov[province], "municipal", province,
                                            year, dumps, dtype))
            models.append(fit_birth_ols(year_provinces, "provincial", "전국", year, dumps, dtype))
        write_json(out / "data" / f"birth_ols_models_{year}.json", models)
        (out / "raw" / f"BIRTH_OLS_{year}.txt").write_text("".join(dumps), encoding="utf-8")
        model_count += len(models)
        print(f"  출산율 OLS {year}: {len(models)} models", flush=True)
    pooled, history = [], []
    dumps = []
    for dtype in TYPES:
        pooled.append(fit_birth_ols(detail, "municipal", "전국", "전기간", dumps, dtype))
        for province in PROVINCES:
            pooled.append(fit_birth_ols([r for r in detail if r["province"] == province],
                                        "municipal", province, "전기간", dumps, dtype))
        pooled.append(fit_birth_ols(province_rows, "provincial", "전국", "전기간", dumps, dtype))
    (out / "raw" / "BIRTH_OLS_pooled.txt").write_text("".join(dumps), encoding="utf-8")
    groups = defaultdict(list)
    for r in detail:
        groups[(r["province"], r["district"])].append(r)
    dumps = []
    for (province, district), obs in sorted(groups.items()):
        for dtype in TYPES:
            history.append(fit_birth_ols(obs, "local_history", province + "|" + district,
                                         "전기간", dumps, dtype))
    (out / "raw" / "BIRTH_OLS_local_history.txt").write_text("".join(dumps), encoding="utf-8")
    write_json(out / "data" / "birth_ols_models_pooled.json", pooled)
    write_json(out / "data" / "birth_ols_models_local_history.json", history)
    audit = {
        "model": "선택 장애유형 등록률(%) = 절편 + 기울기 × 합계출산율(명/여성)",
        "types": TYPES,
        "x": "합계출산율(명/여성)", "y": "주민등록인구 대비 선택한 장애유형 등록률(%)",
        "year_models": model_count, "pooled_models": len(pooled),
        "local_history_models": len(history),
        "usable_municipal": sum(r.get("fertility") is not None and
                               r.get("rates", {}).get("자폐성") is not None for r in detail),
        "usable_by_type": {t: sum(r.get("fertility") is not None and
                                 r.get("rates", {}).get(t) is not None for r in detail)
                           for t in TYPES},
        "caveat": "동일 연도의 합계출산율과 전체 연령층 장애유형별 등록률 간 탐색적 연관성입니다. "
                  "출생 코호트·지역 반복 관측·시간 추세를 통제하지 않으며 인과관계를 뜻하지 않습니다."
    }
    write_json(out / "data" / "birth_ols_quality.json", audit)
    print(f"  출산율 단순 OLS: 연도별 {model_count}건, 통합 {len(pooled)}건, "
          f"개별 지역 시계열 {len(history)}건", flush=True)
    return audit


def fit_fiscal_birth_ols(obs: list[dict], scope: str, region: str,
                         year: str | int, mode: str, raw_group: list[str]):
    """Fit fertility (births/woman) ~ fiscal-independence fraction (0..1).

    Both sides must exist.  Do not modify the source CSV or replace missing values
    with zero.  Province observations use published totals rather than averages.
    """
    valid = [(float(r[mode]), float(r["fertility"])) for r in obs
             if r.get(mode) is not None and r.get("fertility") is not None
             and math.isfinite(float(r[mode])) and math.isfinite(float(r["fertility"]))]
    result = {"scope": scope, "region": region, "year": year, "mode": mode,
              "n": len(valid), "slope": None, "intercept": None,
              "r2": None, "adj_r2": None, "p": None, "slope_ci": None,
              "warning": None, "raw": None}
    if len(valid) < 3:
        result["warning"] = "유효 관측치가 3개 미만이어서 OLS를 적합할 수 없습니다."
        return result
    xs, ys = np.asarray(valid, dtype=float).T
    if np.ptp(xs) < 1e-12:
        result["warning"] = "재정자립도가 모두 같아서 기울기를 추정할 수 없습니다."
        return result
    try:
        with warnings.catch_warnings(record=True) as caught_ols_warnings:
            warnings.simplefilter("always")
            model = sm.OLS(ys, sm.add_constant(xs, has_constant="add")).fit()
            raw = str(model.summary(xname=["const", "fiscal_independence_0to1"]))
        _report_ols_warnings(caught_ols_warnings)
        ci = model.conf_int(alpha=.05)
        result.update(intercept=finite(model.params[0]), slope=finite(model.params[1]),
                      r2=finite(model.rsquared), adj_r2=finite(model.rsquared_adj),
                      p=finite_probability(model.pvalues[1]),
                      slope_ci=[finite(ci[1, 0]), finite(ci[1, 1])], raw=raw)
        raw_group.append(f"\n{'=' * 80}\nscope={scope}, region={region}, year={year}, mode={mode}, n={len(valid)}\n"+raw+"\n")
    except (ValueError, np.linalg.LinAlgError) as ex:
        result["warning"] = f"회귀 계산 오류: {ex}"
    return result


def build_fiscal_birth_ols(out: Path, detail: list[dict], province_rows: list[dict]):
    """Static files for year-by-year, pooled and district 2014-22 fertility/fiscal OLS."""
    yearly_count = 0
    for year in YEARS:
        year_local = [r for r in detail if r["year"] == year]
        year_prov = [r for r in province_rows if r["year"] == year]
        groups = {prov: [r for r in year_local if r["province"] == prov]
                  for prov in PROVINCES}
        for mode in MODES:
            models, raws = [], []
            models.append(fit_fiscal_birth_ols(year_local, "municipal", "전국", year, mode, raws))
            for prov in PROVINCES:
                models.append(fit_fiscal_birth_ols(groups[prov], "municipal", prov, year, mode, raws))
            models.append(fit_fiscal_birth_ols(year_prov, "provincial", "전국", year, mode, raws))
            write_json(out / "data" / f"fiscal_birth_models_{year}_{mode}.json", models)
            (out / "raw" / f"FISCAL_BIRTH_{year}_{mode}.txt").write_text("".join(raws), encoding="utf-8")
            yearly_count += len(models)
    pooled, history = [], []
    groups = defaultdict(list)
    for r in detail:
        groups[(r["province"], r["district"])].append(r)
    for mode in MODES:
        raws = []
        pooled.append(fit_fiscal_birth_ols(detail, "municipal", "전국", "전기간", mode, raws))
        for prov in PROVINCES:
            pooled.append(fit_fiscal_birth_ols([r for r in detail if r["province"] == prov],
                                                "municipal", prov, "전기간", mode, raws))
        pooled.append(fit_fiscal_birth_ols(province_rows, "provincial", "전국", "전기간", mode, raws))
        (out / "raw" / f"FISCAL_BIRTH_pooled_{mode}.txt").write_text("".join(raws), encoding="utf-8")
        raws = []
        for (prov, district), records in sorted(groups.items()):
            history.append(fit_fiscal_birth_ols(records, "local_history", prov + "|" + district,
                                                 "전기간", mode, raws))
        (out / "raw" / f"FISCAL_BIRTH_local_history_{mode}.txt").write_text("".join(raws), encoding="utf-8")
    write_json(out / "data" / "fiscal_birth_models_pooled.json", pooled)
    write_json(out / "data" / "fiscal_birth_models_local_history.json", history)
    audit = {
        "model": "합계출산율(명/여성) = β₀ + β₁ × 재정자립도(0~1) + ε",
        "source": ["Statistics/Financial Independence.csv", "Statistics/Birth rate.csv"],
        "yearly_models": yearly_count, "pooled_models": len(pooled),
        "local_history_models": len(history),
        "municipal_complete": {mode: sum(r.get(mode) is not None and r.get("fertility") is not None
                                         for r in detail) for mode in MODES},
        "provincial_complete": {mode: sum(r.get(mode) is not None and r.get("fertility") is not None
                                          for r in province_rows) for mode in MODES},
        "caveat": "같은 지역의 같은 연도 자료를 이용한 단순 OLS입니다. 지역 간 차이·동시기 연관성을 기술하며 인과효과는 아닙니다. 전체 기간 통합은 연도·지역 고정효과 및 반복관측을 보정하지 않습니다.",
    }
    write_json(out / "data" / "fiscal_birth_quality.json", audit)
    print(f"  재정자립도 × 합계출산율 OLS: 연도별 {yearly_count}건, 통합 {len(pooled)}건, 기초 시계열 {len(history)}건", flush=True)
    return audit


def write_project_root_entrypoint(base: Path, out: Path):
    """Publish the current final six-variable explorer at the Pages root.

    Keep site/index.html as the original fiscal-independence data explorer.
    The root entrypoint is the full site/unified.html, not a redirect: <base>
    resolves JS, styles, links, and data fetches inside ./site/. Regenerate
    it on every build so a manual edit cannot revert to the legacy homepage.
    """
    if out.resolve() != (base / "site").resolve():
        return
    source = out / "unified.html"
    html = source.read_text(encoding="utf-8")
    if "<head>" not in html:
        raise ValueError("사이트 unified.html에 <head>가 없습니다.")
    html = html.replace("<head>", '<head><base href="./site/">', 1)
    (base / "index.html").write_text(html, encoding="utf-8")
    (base / ".nojekyll").write_text("", encoding="utf-8")


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def build(base: Path, out: Path):
    stats = base / "Statistics"
    pop, pop_totals, pe = parse_population(stats / "인구" / "Resident population.csv")
    fisc, fiscal_totals, fe = parse_fiscal(stats / "재정" / "Financial Independence.csv")
    disabilities, unknown, de = parse_disability(stats / "장애인등록" / "Disability")

    detail = []
    unmatched = []
    missing_types_report = []
    missing_count = Counter()
    for (year, province, district), counts in sorted(disabilities.items()):
        denom = pop.get((year, province, district))
        before = fisc.get((year, province, district, "before"))
        after = fisc.get((year, province, district, "after"))
        if denom is None:
            unmatched.append({"year": year, "province": province, "district": district,
                              "cause": "인구자료 없음", "disability": sum(counts.values())})
            missing_count["population"] += 1
            continue
        if before is None and after is None:
            unmatched.append({"year": year, "province": province, "district": district,
                              "cause": "재정자립도 개편 전/후 모두 없음", "disability": sum(counts.values())})
            missing_count["fiscal_both"] += 1
        if before is None: missing_count["fiscal_before"] += 1
        if after is None: missing_count["fiscal_after"] += 1
        # Mutually exclusive source categories: separate 2014-17 Gyeonggi hearing/language
        # combined records must not be split or copied into two individual categories.
        expected_types = set(TYPES) - {"전체", "청각·언어"}
        if province == "경기도" and year <= 2017:
            expected_types -= {"청각", "언어"}
            expected_types.add("청각·언어")
        missing_types = sorted(expected_types - set(counts))
        if missing_types:
            missing_types_report.append({"year": year, "province": province, "district": district,
                                         "missing_types": missing_types})
        total_disabled = sum(counts.values())
        if total_disabled > denom:
            unmatched.append({"year": year, "province": province, "district": district,
                              "cause": "유형 합계가 주민등록인구보다 큼", "disability": total_disabled, "population": denom})
            missing_count["over_population"] += 1
        ratios = {t: round(cnt / denom * 100, 10) for t, cnt in counts.items()}
        ratios["전체"] = round(total_disabled / denom * 100, 10)
        detail.append({"year": year, "province": province, "district": district,
                       "population": denom, "disabled": total_disabled,
                       "counts": counts, "rates": ratios, "before": before, "after": after,
                       "missing_types": missing_types})

    # Use published metropolitan total population, sum published municipality disabled
    # counts. Province 'before/after' is its official subtotal, never a mean of counties.
    by_province = defaultdict(list)
    for r in detail: by_province[(r["year"], r["province"])].append(r)
    province_rows = []
    for (year, province), rows in sorted(by_province.items()):
        population = pop_totals.get((year, province))
        if not population:
            continue
        counts = defaultdict(int)
        for r in rows:
            for t, n in r["counts"].items(): counts[t] += n
        disabled = sum(counts.values())
        rates = {t: round(n / population * 100, 10) for t, n in counts.items()}
        rates["전체"] = round(disabled / population * 100, 10)
        province_rows.append({"year": year, "province": province, "district": province,
                              "population": population, "disabled": disabled,
                              "counts": dict(counts), "rates": rates,
                              "before": fiscal_totals.get((year, province, "before")),
                              "after": fiscal_totals.get((year, province, "after"))})

    out.mkdir(parents=True, exist_ok=True)
    template = Path(__file__).resolve().parent / "site"
    if out.resolve() != template.resolve():
        # --output must produce a complete deployable site, not only JSON files.
        shutil.copytree(template, out, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("data", "raw"))
    (out / "raw").mkdir(exist_ok=True)
    # Models are grouped into separate data files so a basic dashboard only needs its
    # selected year's model file. Text dumps are additionally saved by block.
    for year in YEARS:
        year_data = [r for r in detail if r["year"] == year]
        prov_data = [r for r in province_rows if r["year"] == year]
        for mode in MODES:
            models = []
            dumps = []
            for dtype in TYPES:
                models.append(fit_model(year_data, "municipal", "전국", year, dtype, mode, dumps))
                for province in PROVINCES:
                    relevant = [r for r in year_data if r["province"] == province]
                    models.append(fit_model(relevant, "municipal", province, year, dtype, mode, dumps))
                models.append(fit_model(prov_data, "provincial", "전국", year, dtype, mode, dumps))
            write_json(out / "data" / f"models_{year}_{mode}.json", models)
            (out / "raw" / f"OLS_{year}_{mode}.txt").write_text("".join(dumps), encoding="utf-8")
            print(f"  {year} {mode}: {len(models)} models / {len(dumps)} fits", flush=True)

    all_models = []
    hist_models = []
    for mode in MODES:
        dumps = []
        for dtype in TYPES:
            all_models.append(fit_model(detail, "municipal", "전국", "전기간", dtype, mode, dumps))
            for province in PROVINCES:
                relevant = [r for r in detail if r["province"] == province]
                all_models.append(fit_model(relevant, "municipal", province, "전기간", dtype, mode, dumps))
            all_models.append(fit_model(province_rows, "provincial", "전국", "전기간", dtype, mode, dumps))
        (out / "raw" / f"OLS_pooled_{mode}.txt").write_text("".join(dumps), encoding="utf-8")
        dumps = []
        grouping = defaultdict(list)
        for r in detail: grouping[(r["province"], r["district"])].append(r)
        for (province, district), records in sorted(grouping.items()):
            for dtype in TYPES:
                hist_models.append(fit_model(records, "local_history", province + "|" + district,
                                             "전기간", dtype, mode, dumps))
        (out / "raw" / f"OLS_local_history_{mode}.txt").write_text("".join(dumps), encoding="utf-8")
        print(f"  pooled {mode}: {len(all_models)}; local history {len(hist_models)}", flush=True)
    write_json(out / "data" / "models_pooled.json", all_models)
    write_json(out / "data" / "models_local_history.json", hist_models)
    import time
    analysis_started = time.perf_counter()
    birth_audit = build_multivariate(stats, out, detail, province_rows)
    birth_ols_audit = build_birth_ols(out, detail, province_rows)
    fiscal_birth_audit = build_fiscal_birth_ols(out, detail, province_rows)
    expanded_audit = build_expanded_analysis(stats, out, detail, province_rows, TYPES)
    print(f"기존 분석 생성 소요: {time.perf_counter()-analysis_started:.1f}s", flush=True)
    unified_started = time.perf_counter()
    unified_audit = build_unified_analysis(out, detail, province_rows, TYPES)
    print(f"통합 회귀 생성 소요: {time.perf_counter()-unified_started:.1f}s", flush=True)
    # Do not publish superseded five-variable or duplicate six-variable JSON.
    for obsolete_prefix in ("demographic_multi_models_", "household_premium_multi_models_"):
        for obsolete in (out / "data").glob(obsolete_prefix + "*.json"):
            obsolete.unlink()
    # Retired type shards included historical 2014 healthcare regressions;
    # the new unified shards replace them and cannot contain health 2014.
    for obsolete in (out / "data").glob("*_models_type_??.json"):
        obsolete.unlink()
    for obsolete in ("medical_ols_models_2014.json", "household_premium_ols_models_2014.json"):
        (out / "data" / obsolete).unlink(missing_ok=True)
    write_json(out / "data" / "municipalities.json", detail)
    write_json(out / "data" / "provinces.json", province_rows)

    regions = {p: sorted({r["district"] for r in detail if r["province"] == p}) for p in PROVINCES}
    meta = {"years": list(YEARS), "types": TYPES, "provinces": PROVINCES,
            "districts": regions, "modes": {"before": "세입과목 개편 전", "after": "세입과목 개편 후"},
            "units": {"fiscal": "ratio_0to1", "disability": "percent", "fertility": "births_per_woman"},
            "fiscal_transformation": "재정자립도 원본(0~100) / 100. 원본 CSV 비수정.",
            "new_analysis": "합계출산율(명/여성) ~ 재정자립도(0~1), 개편 전후"}
    write_json(out / "data" / "meta.json", meta)
    quality = {"observations": len(detail), "province_observations": len(province_rows),
               "partially_reported_types": missing_types_report,
               "unmatched": unmatched, "missing": dict(missing_count),
               "unknown_types": {str(k): v for k, v in unknown.items()},
               "duplicate_records": pe + fe + de,
               "type_note": "경기도 2014-2017 청각·언어는 통합 유형이며 청각/언어로 강제 분리하지 않음. 일부 지역-연도의 특정 유형은 원본 공란이므로 전체 등록인원 합계는 제공된 유형의 합산값이며 소폭 과소계상 가능.",
               "special_note": "세종/제주는 광역합계 관측치를 기초 단일 관측치로 사용. 다른 시군구와 완전히 동일한 행정계층은 아님.",
               "multivariate": birth_audit, "birth_ols": birth_ols_audit,
               "fiscal_birth_ols": fiscal_birth_audit, "age_medical": expanded_audit,
                "unified": unified_audit,
               "fiscal_unit_note": "원본 재정자립도(0~100)를 Python 빌드시 100으로 나눠 0~1로 계산하며 CSV 원본은 수정하지 않음.",
               "method_note": "단순 OLS(상수항 포함); 연도 통합분석은 반복 측정과 연도 교란을 보정하지 않으므로 인과관계로 해석하지 말 것."}
    write_json(out / "data" / "quality.json", quality)
    print("다중회귀 출산율 결합 완료")
    print("완료:", len(detail), "기초-연도 관측치,", len(province_rows), "광역-연도 관측치")
    print("누락:", dict(missing_count), "분석 제외 목록:", len(unmatched),
          "장애유형 일부 결측:", len(missing_types_report), "중복:", len(pe + fe + de))
    if unmatched: print("예시:", unmatched[:10])
    write_project_root_entrypoint(base, out)
    return quality


def main():
    parser = argparse.ArgumentParser(description="2014~2022 장애등록률/재정자립도/출산율 OLS · GitHub Pages 루트 페이지 생성")
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parent,
                        help="Statistics/ (Disability/ 포함)을 가진 프로젝트 디렉터리")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "site",
                        help="GitHub Pages 출력 폴더 (기본값: ./site)")
    args = parser.parse_args()
    build(args.input.resolve(), args.output.resolve())

if __name__ == "__main__":
    main()
