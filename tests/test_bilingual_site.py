"""Static bilingual UI contract. This feature must never recalculate OLS data."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def test_every_dashboard_has_korean_english_switch():
    pages = sorted(SITE.glob("*.html"))
    assert len(pages) >= 12
    for page in pages:
        content = page.read_text(encoding="utf-8")
        assert 'assets/js/i18n.js' in content, page.name
        assert 'lang="ko"' in content, page.name


def test_root_dashboard_matches_unified_and_has_language_switch():
    root = (ROOT / "index.html").read_text(encoding="utf-8")
    unified = (SITE / "unified.html").read_text(encoding="utf-8")
    assert root.replace('<base href="./site/">', '', 1) == unified
    assert 'assets/js/i18n.js' in root


def test_language_toggle_is_persistent_accessible_and_presentation_only():
    js = (SITE / "assets/js/i18n.js").read_text(encoding="utf-8")
    for expected in [
        "public-data-lab-language",
        "localStorage.getItem",
        "localStorage.setItem",
        "new URLSearchParams(location.search).get('lang')",
        "['ko','한국어']",
        "['en','English']",
        "aria-pressed",
        "document.documentElement.lang=code",
        "MutationObserver",
        "NodeFilter.SHOW_TEXT",
        "window.SiteLanguage",
        "data-no-translate",
        "'SCRIPT','STYLE','NOSCRIPT','TEXTAREA','PRE','CODE'",
    ]:
        assert expected in js
    # The i18n code must not edit numeric results, CSV payloads, regression
    # coefficients, observations, or source JSON.
    for forbidden in ["pearsonr(", "fetch(", "JSON.stringify(", "new Blob(", "download("]:
        assert forbidden not in js


def test_english_dictionary_covers_main_analysis_ui():
    js = (SITE / "assets/js/i18n.js").read_text(encoding="utf-8")
    for term in [
        "Final six-variable regression",
        "Simple linear regressions",
        "OLS slope β₁ p-value",
        "SciPy Pearson r",
        "Download trend CSV",
        "Regression results by year and region",
        "Data quality & methodology",
        "Select a model from the comparison table.",
    ]:
        assert term in js


def test_ci_skips_full_ols_for_presentation_only_changes():
    workflow = (ROOT / ".github/workflows/verify-unified.yml").read_text(encoding="utf-8")
    assert "Determine whether statistical data needs regeneration" in workflow
    assert "git diff --name-only" in workflow
    assert "full_build=false" in workflow
    assert "full_build=true" in workflow
    assert workflow.count("if: steps.changes.outputs.full_build == 'true'") == 3
    assert "cache: 'pip'" in workflow


def test_single_build_file_preserves_regression_helpers_and_timing():
    build = (ROOT / "build.py").read_text(encoding="utf-8")
    for name in ("def fit_extended_ols(", "def build_unified_analysis(", "def parse_insurance_premiums(",
                 "grouped_periods[period]", "history_scopes", "time.perf_counter()"):
        assert name in build
    for old in ("expanded_analysis.py", "unified_analysis.py", "insurance_premiums.py"):
        assert not (ROOT / old).exists()


def test_retired_duplicate_disability_ols_generator_is_removed():
    """Unified analysis owns the per-type shards; no unused second generator."""
    build = (ROOT / "build.py").read_text(encoding="utf-8")
    assert "def _emit_disability_type_models(" not in build
    assert "def build_unified_analysis(" in build
    assert "def _emit_models(" in build  # still needed by legacy analysis pages


def test_ols_warning_capture_and_statistical_caveats():
    build = (ROOT / "build.py").read_text(encoding="utf-8")
    assert 'warnings.simplefilter("ignore")' not in build
    assert "def _report_ols_warnings(" in build
    assert build.count("_report_ols_warnings(caught_ols_warnings)") == 5
    assert "province_population = num(row[i])" in build
    assert "district_population = num(row[i])" in build
    for page in ("index.html", "site/unified.html"):
        html = (ROOT / page).read_text(encoding="utf-8")
        assert "생태학적 오류" in html
        assert "다중공선성" in html
