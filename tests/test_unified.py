"""Regression contract: six covariates, honest samples, exact index/detail ties."""
from pathlib import Path
import math
import unittest

from unified_analysis import SPECS, HEALTH_YEARS, LABELS, _fit

ROOT = Path(__file__).resolve().parents[1]


class TestUnifiedRegression(unittest.TestCase):
    def test_all_healthcare_models_exclude_2014(self):
        self.assertEqual(HEALTH_YEARS, tuple(range(2015, 2023)))
        for name in ("six", "medical", "premium"):
            self.assertEqual(SPECS[name]["years"], HEALTH_YEARS)
        for name in ("age65", "under15", "fertility", "fiscal"):
            self.assertEqual(SPECS[name]["years"][0], 2014)
        self.assertEqual(len(SPECS["six"]["fields"]), 5)
        self.assertTrue(SPECS["six"]["fiscal"])
        self.assertEqual(len(SPECS), 7)

    def test_exact_six_coefficients_and_observation_consistency(self):
        fields=("after","age65_percent","under15_percent","fertility",
                "medical_10k_per_person","premium_10k_per_household")
        rows=[]
        expected=[2.0,0.1,-0.05,0.2,0.003,-0.008]
        for i in range(1,38):
            x=[0.1 + 0.001*i,
               5+(7*i % 23),8+(11*i % 19),
               0.3+(13*i % 29)*0.04,
               40+(17*i % 31),
               55+(19*i % 37)]
            y=1.2 + sum(beta*value for beta,value in zip(expected,x))
            rows.append(dict(year=2015,province="서울특별시",district=f"지역{i}",
                             rates={"전체":y,"지체":y*0.1},
                             **dict(zip(fields,x))))
        rows.append(dict(year=2014,province="서울특별시",district="2014년",
                         rates={"전체":99999}, **dict(zip(fields,[1]*6))))
        # Calling the fit on 2015 rows is the builder's period-scoped contract.
        selected=[r for r in rows if r["year"]==2015]
        item, detail=_fit(selected,"전체",fields,"municipal","전국",2015,"after")
        self.assertEqual(item["n"],37)
        self.assertEqual(item["year"],2015)
        self.assertEqual(item["coefficients"].__len__(),6)
        self.assertEqual(len(detail["observations"]),item["n"])
        self.assertIn("OLS Regression Results",detail["model"]["raw"])
        self.assertIn("Durbin-Watson",detail["model"]["raw"])
        for coef,expected_value in zip(item["coefficients"],expected):
            self.assertAlmostEqual(coef,expected_value,places=7)
        for obs in detail["observations"]:
            self.assertAlmostEqual(obs[-2]+obs[-1],obs[3],places=8)
        self.assertEqual(item["r2"],detail["model"]["r2"])
        self.assertEqual(item["adj_r2"],detail["model"]["adj_r2"])
        self.assertEqual(item["p_model"],detail["model"]["p_model"])

    def test_missing_type_and_predictors_are_never_zero_imputed(self):
        fields=("after","age65_percent","under15_percent","fertility",
                "medical_10k_per_person","premium_10k_per_household")
        rows=[dict(year=2022,province="경기도",district=f"지역{i}",rates={
            "전체":i,"청각·언어":i*0.1 if i<5 else None
        }, **dict(zip(fields,[i,i**2,i**3,i**4,i**5,i**6])))
              for i in range(1,13)]
        item, detail=_fit(rows,"청각·언어",fields,"municipal","경기도",2022,"after")
        self.assertEqual(item["n"],4)
        self.assertIsNone(item["intercept"])
        self.assertIsNotNone(item["warning"])
        self.assertEqual(len(detail["observations"]),4)
        rows[0]["premium_10k_per_household"]=None
        item, detail=_fit(rows,"전체",fields,"municipal","경기도",2022,"after")
        self.assertEqual(item["n"],11)
        self.assertFalse(any(r[2]=="지역1" for r in detail["observations"]))

    def test_province_type_completeness_and_ui_hooks(self):
        rows=[dict(year=2022,province="경기도",district="경기도",rates={
            "전체":1,"청각":0.1
        },age65_percent=10,complete_types=["전체"])]
        item,_=_fit(rows,"청각",("age65_percent",),"provincial","전국",2022,None)
        self.assertEqual(item["n"],0)
        self.assertIsNotNone(item["warning"])
        html=(ROOT/"site"/"unified.html").read_text(encoding="utf-8")
        js=(ROOT/"site"/"assets"/"js"/"unified.js").read_text(encoding="utf-8")
        for term in ("u-index-export","u-search","u-index-scope",
                     "u-prev","u-next","u-all-types","u-all-regions"):
            self.assertIn('id="'+term+'"',html)
        self.assertIn("state.model",js)
        self.assertIn("item.shard",js)
        self.assertIn("otherMean",js)
        self.assertIn("spanGaps:false",js)
        self.assertNotIn("원본 보간",js)


if __name__=="__main__":
    unittest.main()
