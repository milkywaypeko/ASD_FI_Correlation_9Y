"""Simple OLS displays slope and Pearson r; six-X OLS displays only OLS statistics."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def test_model_specific_cards_and_panels():
    html = (SITE / "unified.html").read_text(encoding="utf-8")
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    css = (SITE / "assets/css/style.css").read_text(encoding="utf-8")
    for id_ in ("u-slope-card", "u-slope", "u-slope-variable",
                "u-corr-card", "u-corr", "u-trend-corr-wrap",
                "u-scipy-section", "u-coeff-title", "u-coeff-explanation"):
        assert f'id="{id_}"' in html, id_
    assert "const isSimple = () => state.model !== 'six'" in js
    for id_ in ("u-slope-card", "u-corr-card", "u-trend-corr-wrap", "u-scipy-section"):
        assert f"'{id_}'" in js
        assert f"#{id_}[hidden]" in css
    assert "el.hidden = !simple" in js
    assert "updateRegressionPresentation();" in js


def test_simple_regression_slope_and_pearson_are_separate_cards():
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    assert "text('u-slope',fmt(item.coefficients?.[0], 9))" in js
    assert "text('u-corr',fmt(item.correlations?.[0], 9))" in js
    assert "text('u-slope-variable','· '+label(modelFields(item)[0]))" in js
    assert "showSciPyRaw(detail, item, modelFields(item)[0])" in js
    assert "scipy_pearson_pairs_" in js


def test_multivariable_ols_omits_correlation_ui_and_csv_columns():
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    assert "for (const [i, field] of modelFields(item).entries())" in js
    assert "if (isSimple()) values.push(fmt(item?.correlations?.[i], 9))" in js
    assert "if (isSimple()) values.push(fmt(item?.correlation_pvalues?.[i], 9))" in js
    assert "if (isSimple()) configs.push(['corr'" in js
    assert "if (isSimple()) modelFields(item).forEach" in js
    assert "...(isSimple()?[item.correlations?.[i]??null" in js
    assert "isSimple()?['피어슨 r (Y–X)','SciPy r p값(양측)']" in js
    assert "item.coefficients.flatMap((beta,i)=>[" in js
    assert "detail.model.raw" in js
    assert "u-observation-export" in js


def test_github_pages_root_matches_unified():
    html = (SITE / "unified.html").read_text(encoding="utf-8")
    root = (ROOT / "index.html").read_text(encoding="utf-8")
    assert root.replace('<base href="./site/">', '', 1) == html
