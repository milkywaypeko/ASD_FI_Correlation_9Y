"""National basic-municipality OLS view, citation and chart theme contracts."""
from pathlib import Path
import gzip
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ACTIVE_PAGES = ("index.html", "unified.html", "multivariate.html",
                "fiscal-birth.html", "results.html", "quality.html")


def test_nationwide_ols_only_filter_is_based_on_existing_fitted_scope():
    html = (SITE / "unified.html").read_text(encoding="utf-8")
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    assert 'value="national_municipal"' in html
    assert 'id="u-index-definition"' in html
    assert "state.indexScope === 'national_municipal'" in js
    assert "item.scope !== 'municipal' || item.region !== '전국'" in js
    assert "if (!nationwide && !state.allRegions" in js
    assert "filtered = index.filter(scoped)" in js
    assert "...filtered.map(item=>" in js
    assert "button.onclick=()=>{select(item)" in js
    assert "item.shard" in js


def test_every_model_has_a_precomputed_nationwide_municipal_fit():
    manifest=json.loads((SITE / "data/unified_manifest.json").read_text(encoding="utf-8"))
    for model, spec in manifest["models"].items():
        path = SITE / "data" / f"unified_index_{model}.json.gz"
        rows=json.loads(gzip.decompress(path.read_bytes()))
        nationwide=[r for r in rows
                    if r["scope"]=="municipal" and r["region"]=="전국"]
        assert nationwide, model
        # Each year and type should contain a nationwide result, regardless of
        # whether the actual model could be fitted for sparse disability types.
        assert any(r["year"]==spec["years"][-1] and r["type"]=="전체"
                   and r["intercept"] is not None for r in nationwide), model
        if model in ("six", "medical", "premium"):
            assert all(r["year"]!=2014 for r in nationwide)
        if model=="six":
            assert all(len(r["coefficients"])==6 for r in nationwide)


def test_chart_theme_loaded_once_before_page_graph_scripts():
    script=(SITE / "assets/js/chart-theme.js").read_text(encoding="utf-8")
    for key in ("observationFill", "prediction", "series", "tooltip",
                "Chart", "window.ResearchChartTheme", "palette.grid"):
        assert key in script
    for name in ACTIVE_PAGES:
        html=(SITE / name).read_text(encoding="utf-8")
        assert html.count('assets/js/chart-theme.js')==1, name
        assert html.count('assets/js/sidebar.js')==1, name
    root=(ROOT / "index.html").read_text(encoding="utf-8")
    assert root.replace('<base href="./site/">', '', 1) == (
        SITE / "unified.html").read_text(encoding="utf-8")
    for name in ("unified.js", "dashboard.js", "multivariate.js",
                 "fiscal-birth.js", "birth-ols.js", "common.js"):
        js=(SITE / "assets/js" / name).read_text(encoding="utf-8")
        assert "ResearchChartTheme" in js, name


def test_kosis_citations_do_not_invent_unverified_download_table_ids():
    sources=(ROOT / "KOSIS_SOURCES.md").read_text(encoding="utf-8")
    readme=(ROOT / "README.md").read_text(encoding="utf-8")
    methods=(SITE / "quality.html").read_text(encoding="utf-8")
    definitions=(ROOT / "Statistics/README.md").read_text(encoding="utf-8")
    assert "DT_1B040M5" in sources
    assert "미확인" in sources
    assert "원본 다운로드일 미기록" in sources
    assert sources.count("https://kosis.kr/")>=8
    assert "KOSIS_SOURCES.md" in readme
    assert "REPRODUCIBILITY.md" in readme
    assert "KOSIS" in methods and "2026.11.08" in methods
    assert "KOSIS_SOURCES.md" in definitions


def test_reproducibility_not_to_delete_source_folders():
    text=(ROOT / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
    for term in ("Statistics/", "2014", "site/data", "site/raw",
                 "__pycache__", ".pytest_cache", "site/ 폴더 전체",
                 "python build.py", "requirements.txt", ".github/"):
        assert term in text, term
