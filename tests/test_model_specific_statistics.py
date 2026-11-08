"""Simple OLS displays slope and Pearson r; six-X OLS displays only OLS statistics."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def test_model_specific_cards_and_panels():
    html = (SITE / "unified.html").read_text(encoding="utf-8")
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    css = (SITE / "assets/css/style.css").read_text(encoding="utf-8")
    for id_ in ("u-slope-card", "u-slope", "u-slope-variable",
                "u-corr-card", "u-corr", "u-slope-p-card", "u-slope-p", "u-trend-corr-wrap",
                "u-scipy-section", "u-coeff-title", "u-coeff-explanation"):
        assert f'id="{id_}"' in html, id_
    assert "const isSimple = () => state.model !== 'six'" in js
    for id_ in ("u-slope-card", "u-corr-card", "u-slope-p-card", "u-trend-corr-wrap", "u-scipy-section"):
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
    assert "if (isSimple()) values.push(fmtP(item?.correlation_pvalues?.[i], 9))" in js
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


def test_simple_ols_slope_pvalue_and_scientific_notation():
    html = (SITE / "unified.html").read_text(encoding="utf-8")
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    assert 'id="u-slope-p-card"' in html
    assert 'id="u-slope-p"' in html
    assert "text('u-slope-p',fmtP(item.pvalues?.[0], 9))" in js
    assert "text('u-pmodel',fmtP(item.p_model,9))" in js
    assert "const fmtP = (x, digits = 9) =>" in js
    assert "if (Math.abs(p) < 10 ** (-digits)) return p.toExponential(3)" in js
    assert "if (p === 0) return '< 1e-323 (정밀도 한계)'" in js
    assert "values.push(fmtP(c.p, 9))" in js
    assert "values.push(fmtP(item?.correlation_pvalues?.[i], 9))" in js
    assert "fmtP(scipy?.pvalue, 10)" in js
    assert "fmtP(value, 8)" in js
    assert "fmtP(c.raw.y,10)" in js


def test_simple_regression_index_shows_coefficient_pvalue_next_to_slope():
    """The per-year/province/municipality table must expose the OLS slope test,
    distinct from the Pearson correlation test, without recomputing statistics."""
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    assert "columns.push(col('beta'+i,isSimple() ? 'OLS β₁ 기울기' : 'β'+(i+1),false))" in js
    assert "columns.push(col('p'+i,isSimple() ? 'OLS β₁ p값 (양측)' : 'β'+(i+1)+' p값',false))" in js
    assert js.index("columns.push(col('beta'+i,isSimple()") < js.index("columns.push(col('p'+i,isSimple()") < js.index("columns.push(col('corr'+i")
    assert "if(/^p\\d+$/.test(column.key))value=item.pvalues[Number(column.key.slice(1))]" in js
    assert "? fmtP(value, 8) : fmt(value, 8)" in js
    assert "columns.push(col('rp'+i,'r'+(i+1)+' SciPy p값',false))" in js


def test_ols_pvalue_index_columns_use_scientific_formatter():
    """OLS p0, p1, ... must be detected by the p-value formatting branch."""
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    # A doubled backslash in the JS regex matches a literal backslash followed
    # by d, and silently routes all coefficient p-values to the generic fmt.
    assert r"/^p\d+$/.test(column.key)" in js
    assert r"/^p\\d+$/.test(column.key)" not in js
    assert "column.key==='p_model' || column.key.startsWith('rp')" in js
    assert "? fmtP(value, 8) : fmt(value, 8)" in js
    assert "if (p === 0) return '< 1e-323 (정밀도 한계)'" in js
    assert "return p.toExponential(3)" in js


def test_analysis_filters_support_all_provinces_and_districts():
    js = (SITE / "assets/js/unified.js").read_text(encoding="utf-8")
    assert "opt($('u-province'),'전국','전체 (전국)')" in js
    assert "opt(control, '전체', '전체')" in js
    assert "const allDistricts = () => state.scope === 'local_history' && state.district === '전체'" in js
    assert "const findSelected = () => allDistricts() ? null :" in js
    assert "state.province !== '전국' && !item.region.startsWith(state.province + '|')" in js
    assert "state.district !== '전체' && item.region !== state.province + '|' + state.district" in js
    assert "전체 선택은 각 기초지자체의 기존 회귀 결과를 비교합니다." in js
    assert "state.province=manifest.provinces[0]" not in js
