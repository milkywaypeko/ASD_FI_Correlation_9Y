"""Homepage/build and README contracts for the current six-variable research site."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_root_is_final_six_variable_explorer_and_build_is_reproducible():
    root=(ROOT/"index.html").read_text(encoding="utf-8")
    unified=(ROOT/"site"/"unified.html").read_text(encoding="utf-8")
    old=(ROOT/"site"/"index.html").read_text(encoding="utf-8")
    build=(ROOT/"build.py").read_text(encoding="utf-8")
    assert root.replace('<base href="./site/">', '', 1)==unified
    assert root.count('<base href="./site/">')==1
    assert 'assets/js/unified.js' in root
    assert 'assets/js/dashboard.js' not in root
    assert 'assets/js/dashboard.js' in old
    assert 'source = out / "unified.html"' in build
    assert '(base / "index.html").write_text(html' in build


def test_readme_matches_current_navigation_model_and_units():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    for required in (
        "최종 6변수", "site/unified.html?model=six", "site/index.html",
        "2014", "2015", "2022", "만원/인/년", "만원/세대/년",
        "statsmodels", "DecompressionStream", "python build.py",
        "R²", "수정 R²", "청각·언어", "지자체 반복관측",
    ):
        assert required in readme, required
    assert "5변수/보험료 포함 6변수 선택" not in readme
    assert "site/index.html`은 데이터 탐색 화면" in readme
