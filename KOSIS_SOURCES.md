# KOSIS 통계 출처와 인용 표준

**조사/열람일: 2026-11-08 (KOSIS 공개 통계목록 및 지표 설명 확인).**
이 프로젝트의 모든 원본 CSV는 연구자가 KOSIS 국가통계포털에서 다운로드한 자료입니다.
**KOSIS는 제공·열람 플랫폼**이며 통계를 작성하는 기관은
행정안전부·보건복지부·국가데이터처(당시 통계청)·국민건강보험공단 등
통계표마다 다릅니다. 출처를 단순히 '통계청'이라고 통일하지 않습니다.

KOSIS 공식 출처 기재 안내:
https://stat.kosis.kr/nsistN/kosisUseGuide.do

KOSIS는 출처를 명시할 때 **작성기관·조사명·통계표명·작성시점·참조일자·상세 URL**
을 권장합니다. 과거 CSV의 최초 내려받은 날짜는 저장소에 없으므로 임의로 추정하지
않고 **'원본 다운로드일 미기록'**으로 표시합니다. 아래 열람일은 이번 문서 검증일로
과거 CSV 취득일이나 통계 작성일을 의미하지 않습니다.

## 사용자 제공 KOSIS 인용문·직접 URL·저장 CSV 대응표 (2026.11.08)

아래 **30개 항목은 2026.11.08에 사용자가 제공한 인용문 및 KOSIS 직접 통계표 URL**을 저장소의 실제 CSV 경로와 대조해 기록한 것입니다. 링크의 현재 개설 여부, 원표 화면의 최신 작성기관 표기 및 인용문의 통계 기준연도는 별도 전수 검증되지 않았습니다. **인용문의 2026년·2024년 등 시점은 본 연구의 분석기간(2014–2022년)과 다르며**, CSV 원본의 최초 다운로드일을 의미하지 않습니다. 사용자 인용문상의 ‘전남광주통합특별시’ 표기는 그대로 보존했지만, 해당 CSV는 각각 광주광역시·전라남도 원표명으로 구분됩니다. 연앙인구 작성기관/통계명 역시 사용자 표기를 보존했으며 이전 문서의 기재와 차이가 있어 최종 논문 인용 전 원표 확인이 필요합니다.

### 기초 통계 (5개)

| 제공된 인용문 | KOSIS 직접 URL | 저장소의 원본 CSV 경로 |
| --- | --- | --- |
| 행정안전부,「주민등록인구현황」, 2026.10, 2026.11.08, 행정구역(시군구)별, 성별 인구수 | [DT_1B040A3](https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B040A3&conn_path=I2) | [`Statistics/인구/Resident population.csv`](Statistics/%EC%9D%B8%EA%B5%AC/Resident%20population.csv) |
| 국가데이터처,「국내인구이동통계」, 2023, 2026.11.08, 시군구/성/연령(5세)별 주민등록연앙인구 | [DT_1B040M5](https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B040M5&conn_path=I2) | [`Statistics/인구/연령(5세)별 주민등록연앙인구.csv`](Statistics/%EC%9D%B8%EA%B5%AC/%EC%97%B0%EB%A0%B9(5%EC%84%B8)%EB%B3%84%20%EC%A3%BC%EB%AF%BC%EB%93%B1%EB%A1%9D%EC%97%B0%EC%95%99%EC%9D%B8%EA%B5%AC.csv) |
| 행정안전부,「주민등록인구현황」, 2026.10, 2026.11.08, 행정구역(시군구)별 주민등록세대수 | [DT_1B040B3](https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1B040B3&conn_path=I2) | [`Statistics/인구/행정구역(시군구)별 주민등록세대수.csv`](Statistics/%EC%9D%B8%EA%B5%AC/%ED%96%89%EC%A0%95%EA%B5%AC%EC%97%AD(%EC%8B%9C%EA%B5%B0%EA%B5%AC)%EB%B3%84%20%EC%A3%BC%EB%AF%BC%EB%93%B1%EB%A1%9D%EC%84%B8%EB%8C%80%EC%88%98.csv) |
| 행정안전부(재정정책과), 2026, 2026.11.08, 재정자립도(시도/시/군/구) | [DT_1YL20921](https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1YL20921&conn_path=I2) | [`Statistics/재정/Financial Independence.csv`](Statistics/%EC%9E%AC%EC%A0%95/Financial%20Independence.csv) |
| 국가데이터처,「인구동향조사」, 2025, 2026.11.08, 합계출산율(시도/시/군/구) | [INH_1B81A17](https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=INH_1B81A17&conn_path=I2) | [`Statistics/출산율/Birth rate.csv`](Statistics/%EC%B6%9C%EC%82%B0%EC%9C%A8/Birth%20rate.csv) |

### 보험료 (4개)

| 제공된 인용문 | KOSIS 직접 URL | 저장소의 원본 CSV 경로 |
| --- | --- | --- |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(서울,인천,경기,강원)별 보험료 현황 | [TX_35003_A021](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A021&conn_path=I2) | [`Statistics/국가건강정보/보험료/시군구(서울,인천,경기,강원)별 보험료 현황.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EB%B3%B4%ED%97%98%EB%A3%8C/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EC%84%9C%EC%9A%B8,%EC%9D%B8%EC%B2%9C,%EA%B2%BD%EA%B8%B0,%EA%B0%95%EC%9B%90)%EB%B3%84%20%EB%B3%B4%ED%97%98%EB%A3%8C%20%ED%98%84%ED%99%A9.csv) |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(대전,세종,충북,충남)별 보험료 현황 | [TX_35003_A050](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A050&conn_path=I2) | [`Statistics/국가건강정보/보험료/시군구(대전,세종,충북,충남)별 보험료 현황.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EB%B3%B4%ED%97%98%EB%A3%8C/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EB%8C%80%EC%A0%84,%EC%84%B8%EC%A2%85,%EC%B6%A9%EB%B6%81,%EC%B6%A9%EB%82%A8)%EB%B3%84%20%EB%B3%B4%ED%97%98%EB%A3%8C%20%ED%98%84%ED%99%A9.csv) |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(광주,전북,전남,제주)별 보험료 현황 | [TX_35003_A079](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A079&conn_path=I2) | [`Statistics/국가건강정보/보험료/시군구(광주,전북,전남,제주)별 보험료 현황.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EB%B3%B4%ED%97%98%EB%A3%8C/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EA%B4%91%EC%A3%BC,%EC%A0%84%EB%B6%81,%EC%A0%84%EB%82%A8,%EC%A0%9C%EC%A3%BC)%EB%B3%84%20%EB%B3%B4%ED%97%98%EB%A3%8C%20%ED%98%84%ED%99%A9.csv) |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(부산,대구,울산,경북,경남)별 보험료 현황 | [TX_35003_A108](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A108&conn_path=I2) | [`Statistics/국가건강정보/보험료/시군구(부산,대구,울산,경북,경남)별 보험료 현황.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EB%B3%B4%ED%97%98%EB%A3%8C/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EB%B6%80%EC%82%B0,%EB%8C%80%EA%B5%AC,%EC%9A%B8%EC%82%B0,%EA%B2%BD%EB%B6%81,%EA%B2%BD%EB%82%A8)%EB%B3%84%20%EB%B3%B4%ED%97%98%EB%A3%8C%20%ED%98%84%ED%99%A9.csv) |

### 진료비 (4개)

| 제공된 인용문 | KOSIS 직접 URL | 저장소의 원본 CSV 경로 |
| --- | --- | --- |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(서울,인천,경기,강원)별 연령별 진료현황-전체 | [TX_35003_A035](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A035&conn_path=I2) | [`Statistics/국가건강정보/진료비/시군구(서울,인천,경기,강원)별 연령별 진료현황-전체.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EC%A7%84%EB%A3%8C%EB%B9%84/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EC%84%9C%EC%9A%B8,%EC%9D%B8%EC%B2%9C,%EA%B2%BD%EA%B8%B0,%EA%B0%95%EC%9B%90)%EB%B3%84%20%EC%97%B0%EB%A0%B9%EB%B3%84%20%EC%A7%84%EB%A3%8C%ED%98%84%ED%99%A9-%EC%A0%84%EC%B2%B4.csv) |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(대전,세종,충북,충남)별 연령별 진료현황-전체 | [TX_35003_A064](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A064&conn_path=I2) | [`Statistics/국가건강정보/진료비/시군구(대전,세종,충북,충남)별 연령별 진료현황-전체.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EC%A7%84%EB%A3%8C%EB%B9%84/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EB%8C%80%EC%A0%84,%EC%84%B8%EC%A2%85,%EC%B6%A9%EB%B6%81,%EC%B6%A9%EB%82%A8)%EB%B3%84%20%EC%97%B0%EB%A0%B9%EB%B3%84%20%EC%A7%84%EB%A3%8C%ED%98%84%ED%99%A9-%EC%A0%84%EC%B2%B4.csv) |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(광주,전북,전남,제주)별 연령별 진료현황-전체 | [TX_35003_A093](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A093&conn_path=I2) | [`Statistics/국가건강정보/진료비/시군구(광주,전북,전남,제주)별 연령별 진료현황-전체.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EC%A7%84%EB%A3%8C%EB%B9%84/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EA%B4%91%EC%A3%BC,%EC%A0%84%EB%B6%81,%EC%A0%84%EB%82%A8,%EC%A0%9C%EC%A3%BC)%EB%B3%84%20%EC%97%B0%EB%A0%B9%EB%B3%84%20%EC%A7%84%EB%A3%8C%ED%98%84%ED%99%A9-%EC%A0%84%EC%B2%B4.csv) |
| 국민건강보험공단,「지역별의료이용통계」, 2024, 2026.11.08, 시군구(부산,대구,울산,경북,경남)별 연령별 진료현황-전체 | [TX_35003_A122](https://kosis.kr/statHtml/statHtml.do?orgId=350&tblId=TX_35003_A122&conn_path=I2) | [`Statistics/국가건강정보/진료비/시군구(부산,대구,울산,경북,경남)별 연령별 진료현황-전체.csv`](Statistics/%EA%B5%AD%EA%B0%80%EA%B1%B4%EA%B0%95%EC%A0%95%EB%B3%B4/%EC%A7%84%EB%A3%8C%EB%B9%84/%EC%8B%9C%EA%B5%B0%EA%B5%AC(%EB%B6%80%EC%82%B0,%EB%8C%80%EA%B5%AC,%EC%9A%B8%EC%82%B0,%EA%B2%BD%EB%B6%81,%EA%B2%BD%EB%82%A8)%EB%B3%84%20%EC%97%B0%EB%A0%B9%EB%B3%84%20%EC%A7%84%EB%A3%8C%ED%98%84%ED%99%A9-%EC%A0%84%EC%B2%B4.csv) |

### 장애인등록 (17개)

| 제공된 인용문 | KOSIS 직접 URL | 저장소의 원본 CSV 경로 |
| --- | --- | --- |
| 서울특별시,「서울특별시기본통계」, 2024, 2026.11.08, 장애인 현황(장애유형별) | [DT_201004_O110044](https://kosis.kr/statHtml/statHtml.do?orgId=201&tblId=DT_201004_O110044&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Seoul.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Seoul.csv) |
| 부산광역시,「부산광역시기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_1137](https://kosis.kr/statHtml/statHtml.do?orgId=202&tblId=DT_1137&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Busan.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Busan.csv) |
| 대구광역시,「대구광역시기본통계」, 2024, 2026.11.08, 장애인등록현황 | [DT_K2E001](https://kosis.kr/statHtml/statHtml.do?orgId=203&tblId=DT_K2E001&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Daegu.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Daegu.csv) |
| 인천광역시,「인천광역시기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_20402_K000042](https://kosis.kr/statHtml/statHtml.do?orgId=204&tblId=DT_20402_K000042&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Incheon.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Incheon.csv) |
| 전남광주통합특별시,「광주광역시기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_20503_K001036](https://kosis.kr/statHtml/statHtml.do?orgId=205&tblId=DT_20503_K001036&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Gwangju.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Gwangju.csv) |
| 대전광역시,「대전광역시기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_20603_K001036](https://kosis.kr/statHtml/statHtml.do?orgId=206&tblId=DT_20603_K001036&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Daejeon.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Daejeon.csv) |
| 울산광역시,「울산광역시기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_2071K36](https://kosis.kr/statHtml/statHtml.do?orgId=207&tblId=DT_2071K36&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Ulsan.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Ulsan.csv) |
| 세종특별자치시,「세종특별자치시기본통계」, 2023, 2026.11.08, 장애인 등록현황 | [DT_20802N_200](https://kosis.kr/statHtml/statHtml.do?orgId=208&tblId=DT_20802N_200&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Sejong.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Sejong.csv) |
| 경기도,「경기도기본통계」, 2023, 2026.11.08, 장애인 등록현황 | [DT_21002_K033](https://kosis.kr/statHtml/statHtml.do?orgId=210&tblId=DT_21002_K033&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Gyeonggi-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Gyeonggi-do.csv) |
| 강원특별자치도,「강원특별자치도기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_211002_K030](https://kosis.kr/statHtml/statHtml.do?orgId=211&tblId=DT_211002_K030&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Gangwon-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Gangwon-do.csv) |
| 충청북도,「충청북도기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_T28](https://kosis.kr/statHtml/statHtml.do?orgId=212&tblId=DT_T28&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Chungcheongbuk-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Chungcheongbuk-do.csv) |
| 충청남도,「충청남도기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_21303_K000086](https://kosis.kr/statHtml/statHtml.do?orgId=213&tblId=DT_21303_K000086&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Chungcheongnam-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Chungcheongnam-do.csv) |
| 전북특별자치도,「전북특별자치도기본통계」, 2022, 2026.11.08, 장애인 등록현황 | [DT_214N_Z00026](https://kosis.kr/statHtml/statHtml.do?orgId=214&tblId=DT_214N_Z00026&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Jeollabuk-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Jeollabuk-do.csv) |
| 전남광주통합특별시,「전라남도기본통계」, 2022, 2026.11.08, 장애인 등록현황 | [DT_K037](https://kosis.kr/statHtml/statHtml.do?orgId=215&tblId=DT_K037&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Jeollanam-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Jeollanam-do.csv) |
| 경상북도,「경상북도기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_21603_K001036](https://kosis.kr/statHtml/statHtml.do?orgId=216&tblId=DT_21603_K001036&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Gyeongsangbuk-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Gyeongsangbuk-do.csv) |
| 경상남도,「경상남도기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_217003N_K036](https://kosis.kr/statHtml/statHtml.do?orgId=217&tblId=DT_217003N_K036&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Gyeongsangnam-do.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Gyeongsangnam-do.csv) |
| 제주특별자치도,「제주특별자치도기본통계」, 2024, 2026.11.08, 장애인 등록현황 | [DT_21802_K001036](https://kosis.kr/statHtml/statHtml.do?orgId=218&tblId=DT_21802_K001036&conn_path=I2) | [`Statistics/장애인등록/Disability/Population of the disabled in Jeju.csv`](Statistics/%EC%9E%A5%EC%95%A0%EC%9D%B8%EB%93%B1%EB%A1%9D/Disability/Population%20of%20the%20disabled%20in%20Jeju.csv) |

---

## 통계별 인용문 및 링크

| 저장된 CSV | 보고서에 넣을 인용 정보(작성기관, 조사, 통계표) | 공식 확인 링크 / 검증 범위 |
| --- | --- | --- |
| `인구/Resident population.csv` | **행정안전부, 「주민등록인구현황」, 「행정구역(시군구)별, 성별 인구수」, KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 주민등록인구 지표](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=A&statJipyoId=3647&vStatJipyoId=4887) — 작성기관 및 원표 제목 확인 |
| `인구/연령(5세)별 주민등록연앙인구.csv` | **행정안전부, 「주민등록인구현황」, 「시군구/성/연령(5세)별 주민등록연앙인구」, KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 5세별 주민등록연앙인구 대량통계목록](https://kosis.kr/statisticsList/mass/mass_list.jsp?list_id=&org_id=101&process=statHtml&tbl_id=DT_1B040M5&vw_cd=MT_Z) — 표 식별자 **기관 101 / DT_1B040M5** 및 2014–2022년 파일 확인 |
| `인구/행정구역(시군구)별 주민등록세대수.csv` | **행정안전부, 「주민등록인구현황」, 「행정구역(시군구)별 주민등록세대수」, KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 주민등록세대수 지표](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=A&statJipyoId=3639&vStatJipyoId=4852) — 작성기관, 통계표명, 단위 확인 |
| `재정/Financial Independence.csv` | **행정안전부, 재정자립도(세입과목 개편 전·후), KOSIS e-지방지표, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 재정자립도 지역지표](https://kosis.kr/metroindex/detailMetroIdct.do?graphTy=L&idctId=5&page=all) — 지표 정의, 세입과목 2014년 변경 및 작성기관 확인. **이 CSV에 정확히 대응하는 통계표 고유 ID는 미확인** |
| `출산율/Birth rate.csv` | **국가데이터처(과거 통계청), 「인구동향조사」, 합계출산율(시군구 자료), KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 합계출산율](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=A&statJipyoId=3643&vStatJipyoId=4854) 및 [KOSIS 시군구 출생아수·합계출산율 연결 안내](https://kosis.kr/edu/visualStats/detail.do?ixId=1123&menuId=M_05). **이 CSV의 세부 표 ID는 미확인** |
| `장애인등록/Disability/` 시도별 원본 17개 | **시도별 작성기관(서울특별시~제주특별자치도), 각 「○○기본통계」의 장애인 등록 현황, KOSIS.** [이전 ASD_FI_Correlation 연구](https://github.com/milkywaypeko/ASD_FI_Correlation)의 **같은 17개 통계표**에서 이번에는 2014–2022년 연도 열을 활용. | **원표 KOSIS orgId/tblId 17개 확보**. 아래 「시도별 장애인등록 KOSIS 원표」 표 참조. 보건복지부 「장애인현황」 지표는 별도 참고자료이며 이 17개 파일의 원표와 동일하다고 단정하지 않음. |
| `국가건강정보/진료비/` 원본 4개 | **국민건강보험공단, 지역별·연령별 진료현황, KOSIS에서 추출한 연도별 지역 자료, 연구에 2015–2022년 사용, 2026.11.08 출처 목록 열람.** | [KOSIS 공식 통계목록](https://kosis.kr/statisticsList/statisticsListIndex.do?menuId=M_01&outLink=Y). **정확한 작성 통계명·표 ID는 아직 독립 확인 불가**; 원본 CSV 파일명과 작성기관은 본 연구의 기록 기준 |
| `국가건강정보/보험료/` 원본 4개 | **국민건강보험공단, 「지역별 의료이용통계」, 「시군구별 보험료 현황」, KOSIS, 연구에 2015–2022년 사용, 2026.11.08 열람.** | 공식 KOSIS 통계표 중 **3개 지역군 표 ID 직접 확인**: 서울·인천·경기·강원 `TX_35003_A021`, 대전·세종·충북·충남 `TX_35003_A050`, 광주·전북·전남·제주 `TX_35003_A079`. 부산·대구·울산·경북·경남의 표 ID는 미확인. 아래 공식 목록 링크 참조. |


## 시도별 장애인등록 KOSIS 원표 17개 · 이전 연구에서 이어진 자료 계보

[기존 연구 `milkywaypeko/ASD_FI_Correlation`](https://github.com/milkywaypeko/ASD_FI_Correlation)의
[원래 README `Data Source → Link`](https://github.com/milkywaypeko/ASD_FI_Correlation/blob/main/README.md#link)에
시도별 **「시도 기본통계」의 장애인 등록 표 링크 17개**와 해당 시점의 인용문이 이미
기록되어 있었습니다. 사용자가 확인한 대로 이번 연구의
`Statistics/장애인등록/Disability/` 파일은 **같은 KOSIS 통계표에서 연도 범위를
2014–2022년으로 바꿔 추출한 다년 원본**입니다.
이전 저장소는 지역별로 2016·2019·2020년 단일 연도 표를 이용했고,
본 프로젝트는 2014–2022년을 회귀 분석에 사용합니다.
따라서 **과거 저장소의 수치와 새 CSV 전체 파일이 바이트 단위로 같다는 뜻이 아닙니다.**

기존 README의 원표 출처 표기는 **2023.04.20**, 현재의 링크 계보 확인은
**2026.11.08**입니다. **이번 프로젝트의 최초 다운로드 날짜는 기록돼 있지 않습니다.**
링크는 이전 연구가 보존한 KOSIS `orgId`/`tblId`이며, 2026년 현재의
각 표 최신 화면/표명 변경·중단 여부까지 전부 검증했다는 의미는 아닙니다.

| 시도·자료 작성기관 | 기존 연구 선택 연도 | KOSIS `orgId / tblId` | 원래 연구에서 기록한 직접 출처 |
| --- | ---: | --- | --- |
| 서울특별시 | 2019년 | `201` / `DT_201_00018_2014` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=201&tblId=DT_201_00018_2014&conn_path=I2) |
| 부산광역시 | 2020년 | `202` / `DT_1137` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=202&tblId=DT_1137&conn_path=I2) |
| 대구광역시 | 2020년 | `203` / `DT_K2E001` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=203&tblId=DT_K2E001&conn_path=I2) |
| 인천광역시 | 2016년 | `204` / `DT_20402_K000042` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=204&tblId=DT_20402_K000042&conn_path=I2) |
| 광주광역시 | 2020년 | `205` / `DT_20503_K001036` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=205&tblId=DT_20503_K001036&conn_path=I2) |
| 대전광역시 | 2020년 | `206` / `DT_20603_K001036` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=206&tblId=DT_20603_K001036&conn_path=I2) |
| 울산광역시 | 2020년 | `207` / `DT_2071K36` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=207&tblId=DT_2071K36&conn_path=I2) |
| 세종특별자치시 | 2019년 | `208` / `DT_20802N_200` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=208&tblId=DT_20802N_200&conn_path=I2) |
| 경기도 | 2019년 | `210` / `DT_21002_K033` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=210&tblId=DT_21002_K033&conn_path=I2) |
| 강원도(현 강원특별자치도) | 2020년 | `211` / `DT_211002_K030` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=211&tblId=DT_211002_K030&conn_path=I2) |
| 충청북도 | 2020년 | `212` / `DT_T28` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=212&tblId=DT_T28&conn_path=I2) |
| 충청남도 | 2020년 | `213` / `DT_21303_K000086` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=213&tblId=DT_21303_K000086&conn_path=I2) |
| 전라북도(현 전북특별자치도) | 2019년 | `214` / `DT_214N_Z00026` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=214&tblId=DT_214N_Z00026&conn_path=I2) |
| 전라남도 | 2019년 | `215` / `DT_K037` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=215&tblId=DT_K037&conn_path=I2) |
| 경상북도 | 2020년 | `216` / `DT_21603_K001036` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=216&tblId=DT_21603_K001036&conn_path=I2) |
| 경상남도 | 2020년 | `217` / `DT_217003N_K036` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=217&tblId=DT_217003N_K036&conn_path=I2) |
| 제주특별자치도 | 2020년 | `218` / `DT_21802_K001036` | [KOSIS 시도별 기본통계 장애인 등록표](https://kosis.kr/statHtml/statHtml.do?orgId=218&tblId=DT_21802_K001036&conn_path=I2) |

**교차검증 예시:** 과거의 단일 연도 장애인 집계 CSV와 현재의 다년 KOSIS CSV에서
같은 연도·지역·지체장애 건수를 직접 비교한 결과,
서울 종로구(2019, 2,661명), 인천 중구(2016, 2,912명),
경기 수원시(2019, 20,258명), 부산 중구(2020, 1,173명)가 일치했습니다.
이는 **선택한 사례의 원자료 계보를 확인한 결과**이지, 17개 파일 모든
숫자와 기준 연도가 전수 일치한다는 검증은 아닙니다.
CSV의 2023~2024년 등 다른 연도 열이 존재해도 본 연구의 회귀는
2014–2022년(건강보험 관련 모형은 2015–2022년)만 사용합니다.

### 시도별 기본통계 인용문 권장 형식

> 출처: [시도 작성기관], 「[시도명]기본통계」,
> 장애인 등록 현황(장애유형·시군구별), KOSIS 국가통계포털,
> [원표의 orgId/tblId 및 직접 URL],
> 본 연구 분석기간 2014–2022년,
> KOSIS 표 URL 계보: 기존 ASD_FI_Correlation 저장소의 2023.04.20 기록 참조,
> 2026.11.08 출처 정보 점검.

표명은 시도별로 조금씩 다를 수 있으므로 실제 인용 시
원표 제목을 우선합니다. **장애인 등록률(%)은 본 연구에서 등록인원을
주민등록인구로 나누어 계산한 파생변수**로, 이 원본 표의 등록인원과 구분합니다.


### 국민건강보험공단 「시군구별 보험료 현황」 공식 통계표

- [KOSIS 지역편(서울·인천·경기·강원) 일반현황](https://stat.kosis.kr/nsieu/view/tree.do?hOrg=350&id=350_35003_2_1%2AMT_OTITLE&task=branchView): **TX_35003_A021**.
- [KOSIS 지역편(대전·세종·충북·충남) 일반현황](https://stat.kosis.kr/nsieu/view/tree.do?hOrg=350&id=350_35003_3_1%2AMT_OTITLE&task=branchView): **TX_35003_A050**.
- [KOSIS 지역편(광주·전북·전남·제주) 일반현황](https://stat.kosis.kr/nsieu/view/tree.do?hOrg=350&id=350_35003_4_1%2AMT_OTITLE&task=branchView): **TX_35003_A079**.
- [KOSIS의 보험료 기준·원본 이상값 공식 답변](https://kosis.kr/civilComplaint/qnaDetail.do?boardIdx=23305): 시군구별 보험료 현황은 직장 고지보험료(정산포함)와 지역 부과보험료의 **연간 합계**입니다. KOSIS는 문의된 특정 오류값을 인정하고 수정 예정이라고 답변했습니다. 연구의 2014년 보험료 분석 제외와 원본 보존 기록에 대한 참고자료이며, 현재 표에 반영된 정정 여부를 단정하지 않습니다.

**중요한 구분:** KOSIS 100대지표 화면은 공식 지표의 출처·작성기관·통계표명을
확인하는 **검증 가능한 안내 링크**입니다. 연구자가 내려받은 시군구 단위 CSV의
원본 화면과 반드시 동일하다는 뜻은 아닙니다. 확인되지 않은 `orgId`/`tblId`나
다운로드일을 임의로 만들지 않습니다. KOSIS 원본 다운로드 당시 표 URL이
확보되면 해당 항목을 고유 링크로 갱신하는 것이 가장 정확합니다.

## 출처를 인용할 때의 예

> 출처: 행정안전부, 「주민등록인구현황」, 「행정구역(시군구)별 주민등록세대수」,
> KOSIS 국가통계포털(https://kosis.kr/), 연구 적용기간 2014–2022년,
> 출처 정보 2026.11.08 열람.

> 출처: 서울특별시, 「서울특별시기본통계」, 장애인 등록 현황(시군구·장애유형별),
> KOSIS 국가통계포털, orgId=201, tblId=DT_201_00018_2014,
> https://kosis.kr/statHtml/statHtml.do?orgId=201&tblId=DT_201_00018_2014&conn_path=I2,
> 본 연구의 적용기간 2014–2022년. (링크는 이전 연구의 2023.04.20 기록을 승계)

보건복지부·행정안전부·국민건강보험공단이 **생산한 통계를 KOSIS를 통해
열람/취득**했다는 사실과 통계의 실제 단위 및 해석을 분리해 적습니다.
해당 공식 통계 원표의 집계액을 재가공하여 만든 장애인 등록률, 인구구조 비율,
1인당 진료비 및 가구당 보험료는 **이 연구의 파생변수**이지
원본 KOSIS가 직접 산출한 수치라고 인용하지 않습니다.

분모·기간·결측·2014년 건강보험 분석 배제는 [`Statistics/README.md`](Statistics/README.md),
삭제 가능한 생성물은 [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)와
메인 [`README.md`](README.md)에서 함께 확인할 수 있습니다.

## 추가 통계표 — 요양기관 밀도와 장애인 등록률

- **제공된 인용문:** 국민건강보험공단, 건강보험심사평가원, 「건강보험통계」, 2026 2/4, 2026.11.11, 「시군구별 종별 요양기관 현황」.
- **KOSIS 원표 URL:** https://kosis.kr/statHtml/statHtml.do?orgId=354&tblId=DT_HIRA4B&conn_path=I2
- **원표 식별자:** orgId 354; tblId DT_HIRA4B.
- **실제 분석 범위:** 업로드 CSV의 2014~2022년 **1분기** 시설 현황. 2026 2/4는 인용에 포함된 기간이지만 제출된 CSV의 관측열에는 해당하지 않습니다.
- **저장된 발췌본:** `Statistics/국가건강정보/요양기관/ASD_facility_categories_2014_2022_Q1.csv.bz2` (원본 CP949→UTF-8, 여섯 기관 종별 행의 수치 변경 없는 발췌·압축 파일; 전체 원본은 별도 보관 대상).
- **기관 분류:** 상급종합병원, 종합병원, 병원, 의원, 정신병원, 보건소. 이들은 자폐 전문기관으로 검증된 목록이 아닙니다.
- **X 단위:** 해당 지역 요양기관 수 / 해당 연도 주민등록인구 × 100,000 (개소/인구 10만 명). **Y 단위:** 동일 지역·연도 장애유형 등록률(%).
- **주의:** 1분기 스냅샷과 연간 등록통계의 시점 차이, 정신병원 2021년 이전 결측, 집계 행정구역 및 환자 이동 가능성을 명시합니다.
