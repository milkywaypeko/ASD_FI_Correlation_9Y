"""Same-sample Pearson r calculations and unified UI wiring."""
import math
from pathlib import Path

import pytest
from scipy.stats import pearsonr

from unified_analysis import _pearson_correlation, _scipy_pearson_result, _fit, SPECS

ROOT = Path(__file__).resolve().parents[1]


def test_exact_positive_negative_and_uncorrelated_pearson():
    xs = [1., 2., 3., 4., 5.]
    assert _pearson_correlation(xs, [3*x+5 for x in xs]) == pytest.approx(1)
    assert _pearson_correlation(xs, [-2*x+10 for x in xs]) == pytest.approx(-1)
    assert _pearson_correlation(xs, [2., -1., 0., -1., 2.]) == pytest.approx(0)


def test_undefined_pearson_never_zero_imputed():
    assert _pearson_correlation([], []) is None
    assert _pearson_correlation([1.], [2.]) is None
    assert _pearson_correlation([4., 4., 4.], [1., 2., 3.]) is None
    assert _pearson_correlation([1., 2., 3.], [7., 7., 7.]) is None


def test_simple_ols_pearson_matches_r_squared_and_observations():
    rows = [dict(year=2022, province="서울특별시", district=f"구{i}",
                 fertility=float(i), rates={"전체": 7.-2.*i})
            for i in range(1, 12)]
    rows.append(dict(year=2022, province="서울특별시", district="누락",
                     fertility=None, rates={"전체": 999.}))
    row, detail = _fit(rows, "전체", ("fertility",),
                       "municipal", "전국", 2022, None)
    assert row["n"] == 11
    assert row["correlations"] == pytest.approx([-1.0])
    assert detail["correlations"]["sample_n"] == row["n"]
    assert detail["correlations"]["method"] == "pearson"
    assert detail["correlations"]["library"] == "scipy.stats.pearsonr"
    scipy_result = detail["correlations"]["scipy"]["fertility"]
    assert scipy_result["raw"].startswith("PearsonRResult(")
    assert scipy_result["raw_confidence_interval"].startswith("ConfidenceInterval(")
    assert scipy_result["alternative"] == "two-sided"
    assert scipy_result["pvalue"] == pytest.approx(pearsonr(
        [row[4] for row in detail["observations"]],
        [row[3] for row in detail["observations"]]
    ).pvalue)
    assert row["correlation_pvalues"] == pytest.approx([scipy_result["pvalue"]])
    assert detail["correlations"]["predictors"]["fertility"] == pytest.approx(-1)
    assert row["r2"] == pytest.approx(row["correlations"][0]**2)
    assert len(detail["observations"]) == row["n"]


def test_multivariable_r_is_marginal_not_a_partial_slope():
    # X1 and X2 move together, while both enter the regression. Pearson r
    # should be computed from actual X/Y, not by converting model betas.
    fields = ("age65_percent", "under15_percent")
    rows = []
    for i in range(1, 21):
        a = float(i)
        b = float((i * 7) % 13)
        y = 2 + a * .3 - b * .75
        rows.append(dict(year=2022, province="서울특별시", district=f"구{i}",
                         age65_percent=a, under15_percent=b,
                         rates={"전체": y, "지체": y*.1}))
    rows.append(dict(year=2022, province="서울특별시", district="누락",
                     age65_percent=999., under15_percent=None,
                     rates={"전체": 99999.}))
    item, detail = _fit(rows, "전체", fields,
                        "municipal", "전국", 2022, None)
    assert item["n"] == 20
    assert len(item["correlations"]) == 2
    assert len(detail["observations"]) == item["n"]
    for index, field in enumerate(fields):
        observed = detail["observations"]
        xs = [o[4+index] for o in observed]
        ys = [o[3] for o in observed]
        expected = _pearson_correlation(xs, ys)
        assert item["correlations"][index] == pytest.approx(expected)
        assert detail["correlations"]["predictors"][field] == pytest.approx(expected)
    assert item["coefficients"][0] == pytest.approx(.3)
    assert item["coefficients"][1] == pytest.approx(-.75)
    # β is measured in percentage points per X unit and cannot equal r generally.
    assert item["correlations"][0] != pytest.approx(item["coefficients"][0])


def test_undefined_on_sparse_disability_type_and_collinear_ols():
    fields = ("age65_percent", "under15_percent")
    rows = [
        dict(year=2022, province="경기도", district=f"구{i}",
             age65_percent=float(i),
             under15_percent=float(i)*2,  # exactly collinear
             rates={"전체": float(i)*3,
                    **({"청각": 2.*i} if i in (1,2,3) else {})})
        for i in range(1, 12)
    ]
    item, detail = _fit(rows, "전체", fields,
                        "municipal", "전국", 2022, None)
    assert item["intercept"] is None
    assert item["correlations"] == pytest.approx([1., 1.])
    sparse, details = _fit(rows[:1], "청각", fields,
                           "municipal", "전국", 2022, None)
    assert sparse["intercept"] is None
    assert sparse["correlations"] == [None, None]
    assert details["correlations"]["sample_n"] == 1
    assert details["correlations"]["scipy"][fields[0]]["raw"] is None
    assert "표본" in details["correlations"]["scipy"][fields[0]]["reason"]


def test_year_policy_and_static_ui_correlation_contract():
    for key in ("six", "medical", "premium"):
        assert 2014 not in SPECS[key]["years"]
    html = (ROOT/"site"/"unified.html").read_text(encoding="utf-8")
    js = (ROOT/"site"/"assets"/"js"/"unified.js").read_text(encoding="utf-8")
    for id_ in ("u-corr", "u-corr-variable", "u-trend-corr",
                "u-detail-corr", "u-coefficients", "u-index-export",
                "u-scipy-raw", "u-scipy-variable", "u-scipy-export",
                "u-scipy-observation-body"):
        assert f'id="{id_}"' in html
    for fragment in ("result.correlations.sample_n !== item.n",
                     "item.correlations?.[i]", "['corr',",
                     "m?.correlations?.[i]", "item.correlations?.[i]??null",
                     "result.correlations.scipy?.[field]?.pvalue",
                     "item.correlation_pvalues?.[i]",
                     "result.raw_confidence_interval",
                     "scipy_pearson_pairs_"):
        assert fragment in js
    root = (ROOT/"index.html").read_text(encoding="utf-8")
    assert root.replace('<base href="./site/">', '', 1) == html


def test_scipy_pearson_raw_ci_and_two_sided_pvalue():
    xs = [3.0, 7.0, 11.0, 18.0, 21.0, 24.0, 29.0, 32.0]
    ys = [0.2, 1.1, 0.5, 1.8, 1.3, 3.1, 2.7, 3.4]
    scipy = pearsonr(xs, ys, alternative="two-sided")
    stored = _scipy_pearson_result(xs, ys)
    assert stored["method"] == "scipy.stats.pearsonr"
    assert stored["n"] == len(xs)
    assert stored["statistic"] == pytest.approx(scipy.statistic)
    assert stored["pvalue"] == pytest.approx(scipy.pvalue)
    expected_ci = scipy.confidence_interval(confidence_level=0.95)
    assert stored["confidence_interval"]["low"] == pytest.approx(expected_ci.low)
    assert stored["confidence_interval"]["high"] == pytest.approx(expected_ci.high)
    assert stored["raw"] == repr(scipy)
    assert stored["raw_confidence_interval"] == repr(expected_ci)
    assert stored["reason"] is None


def test_scipy_undefined_inputs_record_reason_not_zero():
    for xs, ys, hint in [
        ([], [], "표본"),
        ([1.], [2.], "표본"),
        ([3., 3., 3.], [1., 2., 3.], "상수"),
        ([1., 2., 3.], [5., 5., 5.], "상수")
    ]:
        result = _scipy_pearson_result(xs, ys)
        assert result["statistic"] is None
        assert result["pvalue"] is None
        assert result["confidence_interval"] == {"low": None, "high": None}
        assert hint in result["reason"]
        assert result["raw"] is None
        assert result["n"] == len(xs)


def test_scipy_and_statsmodels_are_distinct_in_documentation_and_requirements():
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    quality = (ROOT / "site/quality.html").read_text(encoding="utf-8")
    assert "scipy>=" in req
    assert "statsmodels>=" in req
    assert "scipy.stats.pearsonr" in readme
    assert "scipy.stats.pearsonr" in quality
    assert "PearsonRResult" in readme
    assert "ConfidenceInterval" in readme


def test_simple_regression_top_cards_and_six_variable_correlation_hidden():
    """Display policy must not modify underlying SciPy/OLS source data."""
    html = (ROOT / "site/unified.html").read_text(encoding="utf-8")
    js = (ROOT / "site/assets/js/unified.js").read_text(encoding="utf-8")
    for name in ("u-slope-card", "u-slope", "u-slope-variable", "u-corr-card",
                 "u-corr", "u-trend-corr-wrap", "u-scipy-detail"):
        assert f'id="{name}"' in html
    assert html.count("data-simple-only") >= 6
    assert "const isSimple = () => state.model !== 'six'" in js
    assert "element.style.display = isSimple() ? '' : 'none'" in js
    assert "text('u-slope',fmt(item.coefficients?.[0], 9))" in js
    assert "fmt(item.correlations?.[0], 9)" in js
    assert "if (isSimple()) configs.push(['corr'" in js
    assert "if (isSimple()) {" in js
    assert "if (!isSimple()) {" in js
    assert "if (isSimple()) headers.push('SciPy 피어슨 r'" in js
    assert "if (isSimple()) values.push(item.correlations?.[i]" in js
    assert "if (isSimple()) values.push(m?.correlations?.[i]" in js
    assert "if (!isSimple()) {" in js and "detail.model.raw" in js
    assert (ROOT / "index.html").read_text(encoding="utf-8").replace(
        '<base href="./site/">', '', 1) == html
