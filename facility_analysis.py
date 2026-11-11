"""Q1 healthcare-facility density vs registered-disability rate (static OLS).

Input is a full byte-preserved CP949 original of the user-provided
KOSIS DT_HIRA4B CSV. Missing cells stay missing, not zero. The source's 2014–22
first-quarter counts are paired to the corresponding calendar-year population
and administrative disability-registration rate; the dates are not identical.
"""
from __future__ import annotations

import bz2
import csv
import gzip
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_REL = Path('국가건강정보/요양기관/KOSIS_DT_HIRA4B_original_2014_2022_Q1_cp949.csv.bz2')
SOURCE_URL = 'https://kosis.kr/statHtml/statHtml.do?orgId=354&tblId=DT_HIRA4B&conn_path=I2'
SOURCE_CITATION = '국민건강보험공단·건강보험심사평가원, 「건강보험통계」, 시군구별 종별 요양기관 현황, KOSIS (2026.11.11 열람; 다운로드 자료는 2014–2022년 각 1분기)'
# Institution types are capacity/access PROXIES, not ASD-specialist facility counts.
FACILITY_MODELS = {
    'facility_tertiary': ('상급종합병원', '상급종합병원'),
    'facility_general': ('종합병원', '종합병원'),
    'facility_hospital': ('병원', '병원'),
    'facility_clinic': ('의원', '의원'),
    'facility_psychiatric': ('정신병원', '정신병원'),
    'facility_public_health': ('보건소', '보건소'),
}
PROVINCES = {
    '서울': '서울특별시', '부산': '부산광역시', '대구': '대구광역시',
    '인천': '인천광역시', '광주': '광주광역시', '대전': '대전광역시',
    '울산': '울산광역시', '세종': '세종특별자치시', '경기': '경기도',
    '강원': '강원특별자치도', '충북': '충청북도', '충남': '충청남도',
    '전북': '전북특별자치도', '전남': '전라남도', '경북': '경상북도',
    '경남': '경상남도', '제주': '제주특별자치도',
}
SPECIAL = {'세종특별자치시', '제주특별자치도'}
START_YEAR, END_YEAR = 2014, 2022


def _parse_count(cell: str) -> int | None:
    value = (cell or '').strip().replace(',', '')
    if value in ('', '-', '…', 'X'):
        return None
    if not value.isdecimal():
        raise ValueError(f'요양기관 수가 유효한 정수가 아닙니다: {cell!r}')
    return int(value)


def _local_name(province: str, name: str) -> str:
    name = name.strip()
    if province == '인천광역시' and name == '남구':
        return '미추홀구'
    if province == '부산광역시' and name == '진구':
        return '부산진구'
    for prefix in ('경기 ', '충북 ', '충남 ', '강원 ', '전북 ', '전남 ', '경북 ', '경남 '):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return province if province in SPECIAL else name


def read_facility_counts(path: Path):
    """Return count maps keyed by (year,province,district,model) and province.

    The first column is hierarchical: province rows change the context for
    subsequent *unqualified* district names (e.g. 서울 중구 vs 부산 중구).
    Subdistrict rows under a parent city are retained in the source map but
    never added to a parent city's count. Only exact disability keys are joined.
    """
    with bz2.open(path, 'rt', encoding='cp949', newline='') as stream:
        rows = list(csv.DictReader(stream))
    cols = [f'{y}.1/4' for y in range(START_YEAR, END_YEAR + 1)]
    required = {'시군구별', '요양기관종별', *cols}
    if not rows or not required.issubset(rows[0]):
        raise ValueError('KOSIS 요양기관 원본 필수 컬럼 누락')
    by_name = {name: code for code, (name, _) in FACILITY_MODELS.items()}
    provincial = {}
    local = {}
    current_province = None
    duplicate_conflicts = []
    for row in rows:
        name = row['시군구별'].strip()
        category = row['요양기관종별'].strip()
        if name == '전체':
            current_province = None
            continue
        if name in PROVINCES:
            current_province = PROVINCES[name]
            is_province = True
        else:
            is_province = False
        if current_province is None:
            raise ValueError(f'상위 시도 없이 기초지자체가 등장: {name}')
        if category not in by_name:
            continue
        model = by_name[category]
        district = _local_name(current_province, name)
        for year in range(START_YEAR, END_YEAR + 1):
            count = _parse_count(row[f'{year}.1/4'])
            if count is None:
                continue
            # Explicit province counts used for province-level density.
            if is_province:
                key = (year, current_province, model)
                if key in provincial and provincial[key] != count:
                    duplicate_conflicts.append(('province', key))
                provincial[key] = count
            # Sejong and Jeju are single province-as-local observations in the
            # original disability/population analysis, not their child cities.
            if is_province and current_province in SPECIAL:
                key = (year, current_province, current_province, model)
            elif is_province:
                continue
            elif current_province in SPECIAL:
                continue
            else:
                key = (year, current_province, district, model)
            if key in local and local[key] != count:
                duplicate_conflicts.append(('municipal', key))
            local[key] = count
    if duplicate_conflicts:
        raise ValueError(f'충돌하는 요양기관 원본 중복: {duplicate_conflicts[:5]}')
    return local, provincial


def attach_facility_densities(statistics_root: Path, local_rows: list[dict],
                              provincial_rows: list[dict]):
    source = statistics_root / SOURCE_REL
    local_counts, province_counts = read_facility_counts(source)
    matched = Counter()
    missing = Counter()
    for rows, is_province in ((local_rows, False), (provincial_rows, True)):
        for row in rows:
            population = row.get('population')
            if not population or not math.isfinite(float(population)) or population <= 0:
                raise ValueError('유효하지 않은 인구 분모: ' + str(row))
            for model in FACILITY_MODELS:
                field = model + '_per_100k'
                if is_province:
                    count = province_counts.get((row['year'], row['province'], model))
                else:
                    count = local_counts.get((row['year'], row['province'], row['district'], model))
                row[model + '_count_q1'] = count
                row[field] = count * 100_000 / population if count is not None else None
                ident = ('provincial' if is_province else 'municipal', model, row['year'])
                (matched if count is not None else missing)[ident] += 1
    # A source file without usable district values must fail loudly, not quietly
    # generate a dashboard full of empty regressions.
    if matched[('municipal', 'facility_clinic', 2022)] < 180:
        raise ValueError('2022년 의원 원본·시군구 결합 실패: ' + str(matched[('municipal', 'facility_clinic', 2022)]))
    return {
        'citation': SOURCE_CITATION,
        'url': SOURCE_URL,
        'source_path': 'Statistics/' + SOURCE_REL.as_posix(),
        'period': '2014–2022년 각 1분기 (연도별 등록률·연도별 주민등록인구와 결합)',
        'normalization': '해당 1분기 요양기관 수 / 같은 연도·지역 주민등록인구 × 100000',
        'interpretation': '요양기관 종별 시설 수는 자폐성 전문진료 또는 실제 서비스 제공능력을 직접 측정하지 않습니다.',
        'classification_change': '정신병원은 2021년 이후 분류 신설; 이전 연도는 0이 아닌 결측',
        'matched': {str(k): v for k, v in sorted(matched.items())},
        'missing': {str(k): v for k, v in sorted(missing.items())},
    }


def _save_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).encode('utf-8')
    if path.suffix == '.gz':
        path.write_bytes(gzip.compress(data, compresslevel=6, mtime=0))
    else:
        path.write_bytes(data)


def build_facility_models(statistics_root: Path, output: Path,
                          local_rows: list[dict], provincial_rows: list[dict],
                          disability_types: list[str], fit):
    """Build year-specific and pooled cross-regional simple OLS from real rows.

    Deliberately omits local-history regression: at most 9 Q1 observations and
    administrative time trends make naive significance especially misleading.
    """
    audit = attach_facility_densities(statistics_root, local_rows, provincial_rows)
    groups = defaultdict(list)
    for row in local_rows:
        groups[row['province']].append(row)
    years = list(range(START_YEAR, END_YEAR + 1))
    meta = {
        'types': disability_types,
        'models': {},
        'provinces': list(PROVINCES.values()),
        'source_url': SOURCE_URL,
        'citation': SOURCE_CITATION,
        'normalization': audit['normalization'],
        'limitations': [
            '2014–2022년 기관 통계는 각 연도 1분기 스냅샷이며 등록률은 같은 연도의 연간 행정등록 통계입니다.',
            '단순회귀는 연령, 재정, 진단·등록 접근성 등을 통제하지 않으며 인과효과가 아닙니다.',
            '요양기관 종별은 자폐성 전문진료 기관 여부를 구별하지 않습니다.',
            '모형의 일부 기간 통합 분석은 반복관측과 연도 효과를 통제하지 않습니다.',
            '정신병원 분류는 2021년에 신설되어 2021–2022년만 분석합니다.',
        ],
    }
    for model, (category, label) in FACILITY_MODELS.items():
        field = model + '_per_100k'
        model_years = [2021, 2022] if model == 'facility_psychiatric' else years
        meta['models'][model] = {
            'label': label + ' (인구 10만 명당)',
            'category': category,
            'field': field,
            'years': model_years,
            'unit': '개소/인구 10만 명',
        }
        allowed = set(model_years)
        index = []
        for type_index, dtype in enumerate(disability_types):
            path = f'data/facility_detail/{model}/{type_index:02d}.json.gz'
            details = {}
            for period in (*model_years, '전기간'):
                subsets = []
                if period == '전기간':
                    all_local = [r for r in local_rows if r['year'] in allowed]
                    all_province = [r for r in provincial_rows if r['year'] in allowed]
                    subsets.append(('municipal', '전국', all_local))
                    for name in PROVINCES.values():
                        subsets.append(('municipal', name, [r for r in groups[name] if r['year'] in allowed]))
                    subsets.append(('provincial', '전국', all_province))
                else:
                    all_local = [r for r in local_rows if r['year'] == period]
                    all_province = [r for r in provincial_rows if r['year'] == period]
                    subsets.append(('municipal', '전국', all_local))
                    for name in PROVINCES.values():
                        subsets.append(('municipal', name, [r for r in groups[name] if r['year'] == period]))
                    subsets.append(('provincial', '전국', all_province))
                for scope, region, selected in subsets:
                    item, detail = fit(selected, dtype, (field,), scope, region, period, None)
                    ident = str(len(index))
                    item.update(id=ident, shard=path)
                    # Show the raw facility count and original population next
                    # to the derived density for independent audit and CSV.
                    rows_by_key = {(r['year'], r['province'], r['district']): r for r in selected}
                    detail['columns'] += ['facility_count_q1', 'population']
                    for obs in detail['observations']:
                        original = rows_by_key[(obs[0], obs[1], obs[2])]
                        obs.extend([original[model + '_count_q1'], original['population']])
                    detail['notes']['facility_density'] = audit['normalization']
                    detail['notes']['facility_source'] = SOURCE_URL
                    index.append(item)
                    details[ident] = detail
            _save_json(output / path, details)
        _save_json(output / 'data' / f'facility_index_{model}.json.gz', index)
        meta['models'][model]['index_count'] = len(index)
        meta['models'][model]['fitted_count'] = sum(i['intercept'] is not None for i in index)
    _save_json(output / 'data/facility_manifest.json', meta)
    _save_json(output / 'data/facility_quality.json', audit)
    return audit
