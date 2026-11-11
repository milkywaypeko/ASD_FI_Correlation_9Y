"""Q1 density and source-provenance contracts for ASD-related facility OLS."""
from pathlib import Path
import json
import bz2
import math
import pytest

from facility_analysis import (
    FACILITY_MODELS, SOURCE_REL, attach_facility_densities,
    read_facility_counts, _parse_count, _local_name,
)

ROOT = Path(__file__).resolve().parents[1]


def test_source_is_original_numeric_selection_and_q1_only():
    source = ROOT / 'Statistics' / SOURCE_REL
    text = bz2.decompress(source.read_bytes()).decode('cp949')
    assert '2014.1/4' in text and '2022.1/4' in text
    assert '2026.2/4' not in text
    for name in ('상급종합병원', '종합병원', '병원', '의원', '정신병원', '보건소'):
        assert name in text
    assert '요양병원' in text  # Full original also retains unrelated categories.
    assert '요양병원' not in FACILITY_MODELS


def test_2021_psychiatric_introduced_never_backfilled():
    local, provinces = read_facility_counts(ROOT / 'Statistics' / SOURCE_REL)
    assert (2020, '서울특별시', '강남구', 'facility_psychiatric') not in local
    assert (2021, '서울특별시', '강남구', 'facility_psychiatric') in local
    assert (2022, '서울특별시', '강남구', 'facility_clinic') in local
    assert local[(2022, '서울특별시', '강남구', 'facility_clinic')] == 1801
    assert provinces[(2022, '서울특별시', 'facility_clinic')] == 9264


def test_duplicate_district_names_keep_parent_province_and_rename():
    local, _ = read_facility_counts(ROOT / 'Statistics' / SOURCE_REL)
    assert (2022, '서울특별시', '중구', 'facility_clinic') in local
    assert (2022, '부산광역시', '중구', 'facility_clinic') in local
    assert (2014, '인천광역시', '미추홀구', 'facility_clinic') in local
    assert _local_name('부산광역시', '진구') == '부산진구'
    assert _parse_count('0') == 0
    assert _parse_count('') is None
    with pytest.raises(ValueError):
        _parse_count('-2')


def test_population_denominator_not_100k_or_total_count():
    # Use all exact raw source keys to pass the source coverage audit.
    raw, _ = read_facility_counts(ROOT / 'Statistics' / SOURCE_REL)
    districts = sorted({(prov,dist) for year,prov,dist,model in raw if year==2022 and model=='facility_clinic'})
    local = [{'year':2022,'province':prov,'district':dist,'population':100_000 if (prov,dist)==('서울특별시','강남구') else 200_000}
             for prov,dist in districts]
    gangnam = next(r for r in local if r['province']=='서울특별시' and r['district']=='강남구')
    provincial = [{'year':2022,'province':'서울특별시','district':'서울특별시','population':10_000_000}]
    audit = attach_facility_densities(ROOT/'Statistics', local, provincial)
    assert gangnam['facility_clinic_count_q1'] == 1801
    assert gangnam['facility_clinic_per_100k'] == pytest.approx(1801.0)
    assert provincial[0]['facility_clinic_count_q1'] == 9264
    assert provincial[0]['facility_clinic_per_100k'] == pytest.approx(92.64)
    local.append({'year':2022, 'province':'서울특별시','district':'없는시군구','population':100_000})
    attach_facility_densities(ROOT/'Statistics', local, provincial)
    assert local[-1]['facility_clinic_per_100k'] is None  # not zero-imputed
    assert audit['normalization'].endswith('× 100000')


def test_ui_raw_disclosures_and_kosis_source():
    html=(ROOT/'site/facilities.html').read_text(encoding='utf-8')
    script=(ROOT/'site/assets/js/facilities.js').read_text(encoding='utf-8')
    for marker in ('f-ols-details','f-scipy-details'):
        assert 'id="'+marker+'" open' in html
    assert 'id="f-observations-details"' in html
    assert 'id="f-observations-details" open' not in html
    assert 'DT_HIRA4B' in html
    assert '인구 10만 명당' in html
    assert "$('f-observations-details').open=false" in script
    assert 'detail.observations.slice(0,150)' in script
    assert 'data/facility_index_' in script
    assert 'new Blob(' in script


def test_ols_and_scipy_use_same_population_normalized_pairs():
    from build import _fit
    raw, _ = read_facility_counts(ROOT / 'Statistics' / SOURCE_REL)
    rows = []
    for (year,prov,dist,model),count in raw.items():
        if year != 2022 or model != 'facility_clinic':
            continue
        # Synthetic Y is deterministic but based on actual Q1 facility values.
        # X must be density rather than the raw counts.
        pop = 100_000 + (len(dist) % 7) * 100_000
        x = count / pop * 100_000
        rows.append({'year':2022,'province':prov,'district':dist,'population':pop,
                     'rates':{'자폐성':0.1+0.005*x+0.00002*(len(dist)%4)},
                     'facility_clinic_per_100k':x})
    item,detail=_fit(rows,'자폐성',('facility_clinic_per_100k',),
                     'municipal','전국',2022,None)
    assert item['n'] > 180
    assert item['intercept'] is not None
    assert item['coefficients'][0] == pytest.approx(0.005,abs=0.00001)
    assert detail['correlations']['scipy']['facility_clinic_per_100k']['raw'].startswith('PearsonRResult(')
    assert all(abs(row[-2]+row[-1]-row[3])<1e-9 for row in detail['observations'])
