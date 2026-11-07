"""Household denominators must be real source data, never per-person substitutes."""
import csv
import tempfile
import unittest
from pathlib import Path

from insurance_premiums import (
    PREMIUM_FIELD, household_premium_10k, parse_household_counts,
    parse_insurance_premiums,
)
from expanded_analysis import fit_extended_ols

BASE = Path(__file__).resolve().parents[1]


class TestHouseholdPremiums(unittest.TestCase):
    def test_raw_four_premium_sources_and_accounting_identity(self):
        values, invalid = parse_insurance_premiums(BASE/'Statistics'/'국가건강정보'/'보험료')
        self.assertGreater(len(values), 2000)
        self.assertNotIn((2014,'서울특별시','서울특별시'),values)
        self.assertIn((2015,'서울특별시','서울특별시'),values)
        self.assertEqual(len(invalid), 101)  # 2014 Seoul/Incheon/Gyeonggi/Gangwon
        self.assertEqual({x['year'] for x in invalid},{2014})
        self.assertIn((2022,'제주특별자치도','제주특별자치도'),values)

    def test_real_household_source_and_parent_city_not_duplicated(self):
        counts = parse_household_counts(BASE/'Statistics'/'인구'/'행정구역(시군구)별 주민등록세대수.csv')
        self.assertEqual(len(counts), 9 * 243)
        self.assertEqual(counts[(2022, '서울특별시', '서울특별시')], 4446296)
        self.assertEqual(counts[(2022, '경기도', '부천시')], 344135)
        # Duplicate city-subward labels in the source should not be separate model units.
        self.assertNotIn((2022, '경기도', '오정구'), counts)
        self.assertEqual(counts[(2022, '충청북도', '청주시')], 393697)

    def test_real_2022_insurance_household_value(self):
        counts = parse_household_counts(BASE/'Statistics'/'인구'/'행정구역(시군구)별 주민등록세대수.csv')
        premiums, invalid = parse_insurance_premiums(BASE/'Statistics'/'국가건강정보'/'보험료')
        key = (2022,'서울특별시','종로구')
        self.assertEqual(counts[key], 72524)
        self.assertEqual(premiums[key], 298391378)
        self.assertAlmostEqual(household_premium_10k(premiums[key], counts[key]), 411.438114279411)
        self.assertNotIn((2014,'서울특별시','종로구'), premiums)
        self.assertTrue(invalid)

    def test_household_premium_unit_and_missingness(self):
        # 50,000 thousand KRW = 50 million KRW / 25 households = 200 ten-thousands.
        self.assertEqual(household_premium_10k(50_000,25),200)
        self.assertIsNone(household_premium_10k(50_000,0))
        self.assertIsNone(household_premium_10k(50_000,None))
        self.assertIsNone(household_premium_10k(None,25))

    def test_household_long_csv_and_province_normalization(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'house.csv'
            path.write_text('연도,시도,시군구,세대수\n'
                            '2022,서울,종로구,72500\n'
                            '2022,경기,수원시,550000\n'
                            '2022,인천,남구,250000\n'
                            '2022,서울,중구,-1\n',encoding='utf-8')
            d=parse_household_counts(path)
            self.assertEqual(d[(2022,'서울특별시','종로구')],72500)
            self.assertEqual(d[(2022,'경기도','수원시')],550000)
            self.assertEqual(d[(2022,'인천광역시','미추홀구')],250000)
            self.assertNotIn((2022,'서울특별시','중구'),d)

    def test_household_wide_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'house.csv'
            with path.open('w',encoding='utf-8',newline='') as f:
                w=csv.writer(f)
                w.writerow(['행정구역별','2014','2015','2022'])
                w.writerow(['서울특별시',4000000,4100000,4400000])
                w.writerow(['종로구',60000,61000,70000])
                w.writerow(['중구',55000,55000,60000])
            d=parse_household_counts(path)
            self.assertEqual(d[(2014,'서울특별시','서울특별시')],4000000)
            self.assertEqual(d[(2022,'서울특별시','종로구')],70000)

    def test_ols_per_household_uses_only_observed_denominators(self):
        rows=[]
        for i in range(1,15):
            amount=20000 + i*3000
            denom=120+i*8
            price=household_premium_10k(amount,denom)
            rows.append({PREMIUM_FIELD:price,'rates':{'전체':1+0.01*price,'지체':0.5+0.02*price}})
        rows.append({PREMIUM_FIELD:None,'rates':{'지체':99}})
        fitted=fit_extended_ols(rows,(PREMIUM_FIELD,),'municipal','전국',2022,dtype='지체')
        self.assertEqual(fitted['n'],14)
        self.assertAlmostEqual(fitted['coefficients'][PREMIUM_FIELD]['coef'],0.02,places=7)
        self.assertIn('OLS Regression Results',fitted['raw'])

    def test_documented_units_and_page_explanations(self):
        readme=(BASE/'README.md').read_text(encoding='utf-8')
        self.assertIn('## 최종 6변수 회귀모형',readme)
        self.assertIn('만원/세대/년',readme)
        self.assertIn('주민등록세대수',readme)
        page=(BASE/'site'/'unified.html').read_text(encoding='utf-8')
        self.assertIn('만원/세대/년',page)
        self.assertIn('만원/인/년',page)
        self.assertIn('u-year',page)
        self.assertIn('u-adjr2',page)
        self.assertIn('u-r2',page)

    def test_new_pages_and_no_five_variable_toggle(self):
        for path,model in [('age-medical-multi.html','six'),
                           ('household-premium-ols.html','premium')]:
            html=(BASE/'site'/path).read_text(encoding='utf-8')
            self.assertIn('unified.html?model='+model,html)
        main=(BASE/'site'/'unified.html').read_text(encoding='utf-8')
        script=(BASE/'site'/'assets'/'js'/'unified.js').read_text(encoding='utf-8')
        self.assertNotIn('an-premium-model',main)
        self.assertIn('premium_10k_per_household',(
            BASE/'unified_analysis.py').read_text(encoding='utf-8'))
        self.assertIn('state.model',script)


if __name__=='__main__':
    unittest.main()
