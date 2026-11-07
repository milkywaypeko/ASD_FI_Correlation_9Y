"""Insurance premium totals and *observed* household denominators.

Never divide by population, patients, or assumed persons per household: doing so
would change the estimand. The optional household-count CSV is required for
premium-per-household regression and is documented in Statistics/README.md.
"""
from __future__ import annotations
import csv
import math
import re
from collections import defaultdict
from pathlib import Path
from expanded_analysis import PROVINCES, province_name, district_name, number, YEARS, _parent_city

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
