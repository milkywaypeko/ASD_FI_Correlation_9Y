"""Age distribution, medical expense integration and new OLS regression tests."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from expanded_analysis import (
    parse_age_population, parse_medical_expenses, fit_extended_ols,
    build_expanded_analysis, MEDICAL,
)

ROOT = Path(__file__).resolve().parents[1]
STATS = ROOT / "Statistics"


class TestAgeMedicalRegressions(unittest.TestCase):
    def test_age_uses_correct_five_year_bands(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "age.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["행정구역(시군구)별", "성별", "연령별", "항목", "단위"] + [str(y) + " 년" for y in range(2014, 2023)])
                for age, population in [
                    ("계", 100), ("0 - 4세", 5), ("5 - 9세", 6), ("10 - 14세", 7),
                    ("65 - 69세", 8), ("70 - 74세", 9), ("75 - 79세", 10),
                    ("80 - 84세", 11), ("85세 이상", 12),
                ]:
                    writer.writerow(["서울특별시", "계", age, "주민등록연앙인구[명]", "명"] + [population] * 9)
            parsed = parse_age_population(path)
            self.assertEqual(parsed[(2022, "서울특별시", "서울특별시")]["under15_percent"], 18)
            self.assertEqual(parsed[(2014, "서울특별시", "서울특별시")]["age65_percent"], 50)

    def test_real_age_and_medical_files_are_readable(self):
        age = parse_age_population(STATS / "연령(5세)별 주민등록연앙인구.csv")
        costs, duplicates = parse_medical_expenses(STATS)
        self.assertGreater(len(age), 1000)
        self.assertGreater(len(costs), 1000)
        self.assertIn((2022, "서울특별시", "서울특별시"), costs)
        self.assertIn((2022, "서울특별시", "서울특별시"), age)
        self.assertGreater(age[(2022, "서울특별시", "서울특별시")]["age65_percent"], 0)
        self.assertGreater(costs[(2022, "서울특별시", "서울특별시")], 0)
        self.assertEqual(duplicates, [])

    def test_multivariable_exact_coefficients(self):
        rows = []
        for i in range(24):
            fiscal = 0.10 + .019 * i
            elderly = 7 + (i * 7 % 19)
            young = 11 + (i * 11 % 17)
            birth = 0.5 + (i * 13 % 23) / 24
            medical = 22 + (i * 17 % 29)
            y = 3 + 2*fiscal + .15*elderly - .06*young + .08*birth + .02*medical
            rows.append({"after":fiscal,"age65_percent":elderly,"under15_percent":young,
                         "fertility":birth, MEDICAL:medical,"rates":{"전체":y}})
        predictors = ("after","age65_percent","under15_percent","fertility",MEDICAL)
        fit = fit_extended_ols(rows,predictors,"municipal","전국",2022,"after")
        self.assertIsNone(fit["warning"])
        self.assertEqual(fit["n"],24)
        self.assertAlmostEqual(fit["intercept"],3,places=8)
        self.assertAlmostEqual(fit["coefficients"]["after"]["coef"],2,places=8)
        self.assertAlmostEqual(fit["coefficients"]["age65_percent"]["coef"],.15,places=8)
        self.assertAlmostEqual(fit["coefficients"]["under15_percent"]["coef"],-.06,places=8)
        self.assertAlmostEqual(fit["coefficients"]["fertility"]["coef"],.08,places=8)
        self.assertAlmostEqual(fit["coefficients"][MEDICAL]["coef"],.02,places=8)

    def test_missing_and_collinear_not_imputed(self):
        base = [{"age65_percent":i+2,"rates":{"전체":2*i+1}} for i in range(8)]
        fit=fit_extended_ols(base,("age65_percent",),"municipal","전국",2022)
        self.assertEqual(fit["n"],8)
        self.assertAlmostEqual(fit["coefficients"]["age65_percent"]["coef"],2)
        base.append({"age65_percent":None,"rates":{"전체":99}})
        fit=fit_extended_ols(base,("age65_percent",),"municipal","전국",2022)
        self.assertEqual(fit["n"],8)
        singular = [dict(age65_percent=10,under15_percent=10,rates={"전체":j}) for j in range(10)]
        self.assertIsNotNone(fit_extended_ols(singular,("age65_percent","under15_percent"),"municipal","전국",2022)["warning"])

    def test_four_html_pages_exist(self):
        for page in ("age-medical-multi.html","age65-ols.html","under15-ols.html","medical-ols.html"):
            html=(ROOT/"site"/page).read_text(encoding="utf-8")
            self.assertIn('id="an-chart"',html)
            self.assertIn("assets/js/age-medical.js",html)
            self.assertIn('id="an-coefficients"',html)
            self.assertIn('id="an-export"',html)
        self.assertIn("age65-ols.html",(ROOT/"site"/"index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
