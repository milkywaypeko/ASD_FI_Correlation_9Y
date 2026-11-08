"""Data integrity regression checks for source aggregation."""

from pathlib import Path
import pytest
import build


def test_disability_duplicate_conflict_fails(tmp_path):
    folder = tmp_path / "Disability"
    folder.mkdir()
    (folder / "Population of the disabled in Busan.csv").write_text(
        "지역,유형,시군구,2022\n"
        "x,지체,중구,2\n"
        "x,지체,중구,3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="중복 충돌"):
        build.parse_disability(folder)


def test_published_total_not_double_counted(tmp_path):
    folder = tmp_path / "Disability"
    folder.mkdir()
    (folder / "Population of the disabled in Busan.csv").write_text(
        "지역,유형,시군구,2022\n"
        "x,지체,중구,2\n"
        "x,전체,중구,2\n", encoding="utf-8")
    records, _, _ = build.parse_disability(folder)
    assert records[(2022, "부산광역시", "중구")] == {"지체": 2}
