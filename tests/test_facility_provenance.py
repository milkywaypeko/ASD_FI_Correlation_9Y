"""KOSIS source citation and full-provider model regression contracts."""
from pathlib import Path
import bz2
import hashlib
import html

from facility_analysis import FACILITY_MODELS, SOURCE_CITATION, SOURCE_REL, SOURCE_URL

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "국민건강보험공단, 건강보험심사평가원,「건강보험통계」, 2026 2/4, 2026.11.11, 시군구별 종별 요양기관 현황"


def test_citation_is_identical_across_main_source_surfaces():
    assert SOURCE_CITATION == EXPECTED
    for filename in ("README.md", "Statistics/README.md", "KOSIS_SOURCES.md",
                     "site/quality.html", "site/facilities.html"):
        content = (ROOT / filename).read_text(encoding="utf-8")
        assert EXPECTED in content, filename
        assert SOURCE_URL in html.unescape(content), filename
    assert "DT_HIRA4B" in (ROOT / "KOSIS_SOURCES.md").read_text(encoding="utf-8")


def test_original_full_kosis_csv_is_byte_preserved():
    original = bz2.decompress((ROOT / "Statistics" / SOURCE_REL).read_bytes())
    assert hashlib.sha256(original).hexdigest() == (
        "52eecc3f3ebd598f552d154262314ed7524b0f89a244a07b9753bd583e0f03db"
    )


def test_full_institution_type_is_distinct_from_six_subcategories():
    assert len(FACILITY_MODELS) == 7
    assert FACILITY_MODELS["facility_total"][0] == "계"
    assert set(FACILITY_MODELS) == {
        "facility_total", "facility_tertiary", "facility_general",
        "facility_hospital", "facility_clinic", "facility_psychiatric",
        "facility_public_health",
    }


def test_both_ci_paths_rebuild_when_facility_analysis_changes():
    verify = (ROOT / ".github/workflows/verify-unified.yml").read_text(encoding="utf-8")
    refresh = (ROOT / ".github/workflows/refresh-published-data.yml").read_text(encoding="utf-8")
    assert "facility_analysis\\.py$" in verify
    assert "facility_analysis.py" in refresh
    assert "== 7 * 17" in verify


def test_existing_thirty_sources_remain_and_new_one_is_additional():
    register = (ROOT / "KOSIS_SOURCES.md").read_text(encoding="utf-8")
    assert "기존 30건" in register
    assert "기존 30개 KOSIS 원표" not in register or "유지" in register
    assert "추가 1건" in register
    assert "전체 요양기관(계)" in register
    assert "부분 발췌" not in register.split("## 추가 통계표 — 요양기관 밀도와 장애인 등록률", 1)[1]
