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

## 통계별 인용문 및 링크

| 저장된 CSV | 보고서에 넣을 인용 정보(작성기관, 조사, 통계표) | 공식 확인 링크 / 검증 범위 |
| --- | --- | --- |
| `인구/Resident population.csv` | **행정안전부, 「주민등록인구현황」, 「행정구역(시군구)별, 성별 인구수」, KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 주민등록인구 지표](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=A&statJipyoId=3647&vStatJipyoId=4887) — 작성기관 및 원표 제목 확인 |
| `인구/연령(5세)별 주민등록연앙인구.csv` | **행정안전부, 「주민등록인구현황」, 「시군구/성/연령(5세)별 주민등록연앙인구」, KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 5세별 주민등록연앙인구 대량통계목록](https://kosis.kr/statisticsList/mass/mass_list.jsp?list_id=&org_id=101&process=statHtml&tbl_id=DT_1B040M5&vw_cd=MT_Z) — 표 식별자 **기관 101 / DT_1B040M5** 및 2014–2022년 파일 확인 |
| `인구/행정구역(시군구)별 주민등록세대수.csv` | **행정안전부, 「주민등록인구현황」, 「행정구역(시군구)별 주민등록세대수」, KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 주민등록세대수 지표](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=A&statJipyoId=3639&vStatJipyoId=4852) — 작성기관, 통계표명, 단위 확인 |
| `재정/Financial Independence.csv` | **행정안전부, 재정자립도(세입과목 개편 전·후), KOSIS e-지방지표, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 재정자립도 지역지표](https://kosis.kr/metroindex/detailMetroIdct.do?graphTy=L&idctId=5&page=all) — 지표 정의, 세입과목 2014년 변경 및 작성기관 확인. **이 CSV에 정확히 대응하는 통계표 고유 ID는 미확인** |
| `출산율/Birth rate.csv` | **국가데이터처(과거 통계청), 「인구동향조사」, 합계출산율(시군구 자료), KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 합계출산율](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=A&statJipyoId=3643&vStatJipyoId=4854) 및 [KOSIS 시군구 출생아수·합계출산율 연결 안내](https://kosis.kr/edu/visualStats/detail.do?ixId=1123&menuId=M_05). **이 CSV의 세부 표 ID는 미확인** |
| `장애인등록/Disability/` 시도별 원본 17개 | **보건복지부, 「장애인현황」, 장애유형별 등록장애인수(시도·시군구 관련 원본), KOSIS, 2014–2022년 자료 사용, 2026.11.08 열람.** | [KOSIS 장애인인구 지표](https://kosis.kr/visual/nsportalStats/detailContents.do?listId=D&statJipyoId=3672&vStatJipyoId=4839) — 작성기관·시도별 표명 확인. **CSV 17개의 개별 시군구 통계표 ID는 미확인** |
| `국가건강정보/진료비/` 원본 4개 | **국민건강보험공단, 지역별·연령별 진료현황, KOSIS에서 추출한 연도별 지역 자료, 연구에 2015–2022년 사용, 2026.11.08 출처 목록 열람.** | [KOSIS 공식 통계목록](https://kosis.kr/statisticsList/statisticsListIndex.do?menuId=M_01&outLink=Y). **정확한 작성 통계명·표 ID는 아직 독립 확인 불가**; 원본 CSV 파일명과 작성기관은 본 연구의 기록 기준 |
| `국가건강정보/보험료/` 원본 4개 | **국민건강보험공단, 「지역별 의료이용통계」, 「시군구별 보험료 현황」, KOSIS, 연구에 2015–2022년 사용, 2026.11.08 열람.** | 공식 KOSIS 통계표 중 **3개 지역군 표 ID 직접 확인**: 서울·인천·경기·강원 `TX_35003_A021`, 대전·세종·충북·충남 `TX_35003_A050`, 광주·전북·전남·제주 `TX_35003_A079`. 부산·대구·울산·경북·경남의 표 ID는 미확인. 아래 공식 목록 링크 참조. |

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

> 출처: 보건복지부, 「장애인현황」, 「시도별, 장애유형별, 성별 등록장애인수」,
> KOSIS 국가통계포털(https://kosis.kr/), 연구 적용기간 2014–2022년,
> 출처 정보 2026.11.08 열람. *(세부 시군구 파일의 정확한 KOSIS 표 ID는 별도 확인 필요)*

보건복지부·행정안전부·국민건강보험공단이 **생산한 통계를 KOSIS를 통해
열람/취득**했다는 사실과 통계의 실제 단위 및 해석을 분리해 적습니다.
해당 공식 통계 원표의 집계액을 재가공하여 만든 장애인 등록률, 인구구조 비율,
1인당 진료비 및 가구당 보험료는 **이 연구의 파생변수**이지
원본 KOSIS가 직접 산출한 수치라고 인용하지 않습니다.

분모·기간·결측·2014년 건강보험 분석 배제는 [`Statistics/README.md`](Statistics/README.md),
삭제 가능한 생성물은 [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)와
메인 [`README.md`](README.md)에서 함께 확인할 수 있습니다.
