# S3 영수증 아카이브 (P2 설계, 시도 1)

- 프레임: `S3-concept` / `S3-final`, 390×844 세로
- 콘셉트: S1·S2와 **같은 빈티지 인쇄 계산기**다. 화면 위에 계산기 본체 윗부분(잉크색 브랜드 띠 + 민트 VFD 표시창)을 작게 두고, 그 아래에 보관된 감열지 영수증을 기간 단위로 묶어 보여준다. 영수증 하루치 1장은 한 줄 종이 띠로 접혀 쌓이고, 기간 합계는 S2 영수증의 TOTAL 줄과 같은 모양으로 목록 위에 놓인다
- 그리는 상태: **주별 보기 1장** (2026.10.05 월 – 10.11 일). 일별·월별 보기는 인터랙션 메모로만 적는다
- 서체: Pretendard(한글 탭 라벨·안내 문구), JetBrains Mono(날짜·건수·금액·TOTAL·영문 라벨·로고). 이 2종 외 사용 금지
- 색·모서리·간격: docs/design.md YAML의 `colors` / `rounded` / `spacing` 토큰만 사용 (간격은 토큰 값 또는 0)
- 화면 전체가 스크롤 없이 390×844 안에 보이게 그린다 (주별은 최대 7줄이므로 항상 한 화면에 들어간다)

## 대상 유저스토리
- **U4** (주): 사용자가 아카이브에서 지난 날짜의 영수증을 본다 — 주별 목록의 하루 줄 7개로 지난 날짜 영수증을 찾고, 줄을 누르면 그날 영수증(S2와 같은 읽기 전용 감열지)을 연다
- **U5** (주): 사용자가 아카이브에서 영수증을 주별·월별로 묶어 사용 합계를 확인한다 — 일별·주별·월별 탭 전환(F5), 주는 월요일 시작(월~일), 기간 요약의 TOTAL로 기간 사용 합계를 보여준다

## 구성 요소
레이어 이름은 harness/artifacts.md 규칙을 따른다.
- 이름 조각(`/`·`-`·`_` 기준)에 `edit`, `delete` 0개
- 이름 조각에 `modal`, `popup`, `sheet`, `select`, `dropdown` 0개 — 보기 전환은 `tabs` / `tab/*`로 부른다 (`selected`·`selector` 같은 파생어도 쓰지 않는다. 활성 상태는 레이어 이름이 아니라 채움 색으로만 구분)
- 이 화면에는 `input/*` 레이어를 두지 않는다

**PRD §8 영수증 필수 항목 대응**
S3는 영수증 여러 장을 보관하는 화면이므로, §8 항목을 "기간 묶음 영수증" 형태로 모두 갖춘다. 하루 영수증 원본(건별 줄 포함)은 줄을 눌러 여는 S2와 같은 영수증에서 그대로 보인다.

| §8 항목 | 이 화면의 레이어 | 비고 |
|---|---|---|
| 상단 앱 이름 cally | `printer/brand` 안 `cally` 글자 | S1·S2와 같은 브랜드 표기 |
| 날짜 | `period/label` (기간), `archive/row-n` 안 `date` (하루) | |
| 건별 [시각 · 물품명 · 금액] | 일별 보기 / 줄을 눌러 여는 하루 영수증의 `receipt/row-n` | 주별 화면에서는 하루를 [날짜 · 건수 · 금액] 1줄로 접는다 (p1 항목 4) |
| 건수 | `summary/count` (기간), `archive/row-n` 안 `count` (하루) | |
| TOTAL | `summary/total` | |
| 하단 절취선(점선) | `archive/cut-line` | |

**레이어 목록**

| 레이어 이름 | 종류 | 내용 |
|---|---|---|
| `S3-concept` / `S3-final` | 프레임 390×844 | 배경 `canvas` |
| `printer` | 오토레이아웃(세로) | 계산기 본체 윗부분. 폭 342. 자식 `printer/brand`, `printer/case` |
| `printer/brand` | 오토레이아웃(가로) | 배경 `ink`, 위 두 모서리 `rounded.xl`, 아래 0. 좌: `cally`(Pretendard 16px/600, `primary`), 우: `RECEIPT ARCHIVE`(JetBrains Mono 11px, `muted-soft`). space-between. S2 `printer/brand`와 같은 모양 |
| `printer/case` | 오토레이아웃(가로) | 배경 `surface-strong`, 위 0 · 아래 두 모서리 `rounded.xl`. 자식 `printer/display` 1개 |
| `printer/display` | 오토레이아웃(가로) | 배경 `ink`, 모서리 `rounded.sm`, 폭 채움. 텍스트 `ARCHIVE · WEEK`(JetBrains Mono 11px, `timeline-grep` — S1·S2 VFD 민트 글자) |
| `tabs` | 오토레이아웃(가로) | 보기 단위 전환 알약형 세그먼트. 배경 `surface-strong`, 모서리 `rounded.pill`, padding `spacing.xxs` 4, gap `spacing.xxs` 4. 자식 3개 폭 균등 채움 |
| `tab/day` | 버튼(알약) | `일별` — Pretendard 14px/500 `muted`. 채움 없음, 모서리 `rounded.pill`, 높이 32 |
| `tab/week` | 버튼(알약, 활성) | `주별` — Pretendard 14px/600 `on-primary`. 배경 `ink`, 모서리 `rounded.pill`, 높이 32. **이 시안의 활성 탭** |
| `tab/month` | 버튼(알약) | `월별` — Pretendard 14px/500 `muted`. 채움 없음, 모서리 `rounded.pill`, 높이 32 |
| `period` | 오토레이아웃(가로, 가운데 정렬) | ◀ 기간 ▶. space-between, 높이 32 |
| `period/prev` | 버튼(원형) | 32×32, 배경 `surface-card`, 테두리 1px `hairline-strong`, 모서리 `rounded.full`. 글자 `◀` JetBrains Mono 11px `ink` (글리프가 없으면 같은 크기 삼각형 벡터, 채움 `ink`) |
| `period/label` | 텍스트 | `10.05 월 – 10.11 일` — JetBrains Mono 15px/600 `ink`, 가운데. 바로 위에 `period/year` |
| `period/year` | 텍스트 | `2026` — JetBrains Mono 11px `muted`, 가운데. `period/label`과 세로로 묶음(`period/title`, gap 0) |
| `period/title` | 오토레이아웃(세로) | `period/year` + `period/label` |
| `period/next` | 버튼(원형, 비활성) | 32×32, 채움 없음, 테두리 1px `hairline`, 모서리 `rounded.full`. 글자 `▶` JetBrains Mono 11px `muted-soft` — 더 최근 영수증이 없어 비활성 (가정 3) |
| `summary` | 오토레이아웃(세로) | 기간 요약 = 묶음 영수증의 합계부. 감열지 띠: 배경 `surface-card`, 테두리 1px `hairline`, 모서리 `rounded.none`, 그림자 없음. padding 상하 `spacing.base` 16 · 좌우 `spacing.lg` 24 |
| `summary/name` | 오토레이아웃(가로) | 좌: `WEEKLY RECEIPT`(JetBrains Mono 11px/600, 자간 넓게, `muted`), 우: `MON – SUN`(JetBrains Mono 11px, `muted-soft`, 우측 정렬). 기간 이름 |
| `summary/count` | 오토레이아웃(가로) | 좌: `영수증`(Pretendard 13px `muted`), 우: `6장 · 27건`(JetBrains Mono 13px `ink`, **우측 정렬**) |
| `summary/divider` | 선(실선) | 1px `ink`. S2 `receipt/divider-total`과 같은 역할 |
| `summary/total` | 오토레이아웃(가로, 아래 정렬) | 좌: `TOTAL`(JetBrains Mono 16px/700 `ink`), 우: `₩174,200`(JetBrains Mono 24px/700 `ink`, **우측 정렬**) |
| `archive` | 오토레이아웃(세로) | 하루 영수증을 한 줄씩 접어 쌓은 긴 감열지. 배경 `surface-card`, 테두리 1px `hairline`, 모서리 `rounded.none`. padding 상 `spacing.base` 16 · 좌우 `spacing.lg` 24 · 하 `spacing.base` 16 |
| `archive/columns` | 오토레이아웃(가로) | 열 머리 `DATE` / `COUNT` / `AMOUNT` — JetBrains Mono 11px `muted-soft`. `AMOUNT`는 우측 정렬(오른쪽 끝에서 `chevron` 폭 12 + gap 12만큼 안쪽) |
| `archive/divider-top` | 선(점선) | 1px `hairline-strong`, 점선(대시 4·간격 4) |
| `archive/rows` | 오토레이아웃(세로) | 줄 7개 + 줄 사이 점선 6개, gap 0 |
| `archive/row-1` … `archive/row-7` | 오토레이아웃(가로) | 하루 1줄 = [날짜 · 건수 · 금액 · ›]. padding 상하 `spacing.xs` 8, 좌우 0, gap `spacing.sm` 12, 높이 36. 배경 없음(종이 위 인쇄 줄) |
| └ `date` | 텍스트 | `10.11 일` — JetBrains Mono 13px `ink`, 고정폭 72 |
| └ `count` | 텍스트 | `6건` — JetBrains Mono 13px `muted`, 고정폭 40 |
| └ `price` | 텍스트 | `₩38,650` — JetBrains Mono 13px `ink`, 폭 채움, **우측 정렬** |
| └ `chevron` | 텍스트 | `›` — JetBrains Mono 13px `muted-soft`, 고정폭 12. 이 줄을 누르면 그날 영수증이 열린다는 표시 |
| `archive/row-4` (0건인 날) | 오토레이아웃(가로) | 같은 구조지만 `date`·`count`·`price` 모두 `muted-soft`(흐린 줄), `chevron` 대신 같은 폭 12의 빈 프레임 `chevron-space`(채움 없음). 누름 반응 없음 (가정 2) |
| `archive/divider-1` … `archive/divider-6` | 선(점선) | 줄 사이 1px `hairline`, 점선(대시 2·간격 2). 영수증 품목 줄처럼 가볍게 |
| `archive/cut-line` | 선(점선) | 하단 절취선. 1px `hairline-strong`, 점선(대시 4·간격 4), 종이 전체 폭 |
| `caption` | 텍스트 | `날짜를 누르면 그날 영수증을 볼 수 있어요` — Pretendard 13px `muted`, 가운데 |
| `nav` | 오토레이아웃(가로) | 하단 이동 버튼 1개, 폭 채움 |
| `nav/home` | 버튼 | `계산기로` — Pretendard 15px/600 `on-primary`. 배경 `ink`, 모서리 `rounded.lg`, 높이 48, padding 좌우 `spacing.base` 16. S1로 이동 (S2 `nav/archive`와 같은 primary 모양) |

- `primary` 오렌지는 `printer/brand`의 `cally` 글자에만 쓴다. 종이 위(`summary`, `archive`)는 감열지처럼 `ink`/`muted`/`muted-soft`만
- 민트(`timeline-grep`)는 `printer/display` 글자에만 쓴다

## 레이아웃
390×844 기준. 좌우 여백 `spacing.lg` 24 → 내용 폭 342 (x 24–366). `summary`·`archive` 안쪽 padding 좌우 24 → 내용 폭 294.

| 영역 | y 범위 | 메모 |
|---|---|---|
| 상태바 여백 | 0–48 | 프레임 상단 padding `spacing.xxl` 48 |
| `printer/brand` | 48–80 | 높이 32, padding 좌우 `spacing.base` 16 |
| `printer/case` | 80–116 | padding 상하 `spacing.xs` 8 · 좌우 `spacing.base` 16 |
| └ `printer/display` | 88–108 | 높이 20, padding 좌우 `spacing.xs` 8 |
| (간격) | 116–140 | `spacing.lg` 24 |
| `tabs` | 140–180 | 높이 40 (padding 4 + 탭 32 + 4). 탭 폭 각 약 108.7 |
| (간격) | 180–196 | `spacing.base` 16 |
| `period` | 196–228 | `period/prev` x 24–56, `period/title` 가운데(year 196–210, label 210–228), `period/next` x 334–366 |
| (간격) | 228–244 | `spacing.base` 16 |
| `summary` | 244–381 | padding 상하 16 |
| └ `summary/name` | 260–276 | |
| └ (간격) | 276–288 | `spacing.sm` 12 |
| └ `summary/count` | 288–308 | |
| └ (간격) | 308–320 | `spacing.sm` 12 |
| └ `summary/divider` | 320–321 | 실선 `ink` |
| └ (간격) | 321–333 | `spacing.sm` 12 |
| └ `summary/total` | 333–365 | 높이 32 |
| (간격) | 381–397 | `spacing.base` 16 |
| `archive` | 397–725 | padding 상 16 · 하 16 |
| └ `archive/columns` | 413–429 | |
| └ (간격) | 429–437 | `spacing.xs` 8 |
| └ `archive/divider-top` | 437–438 | 점선 |
| └ `archive/rows` | 438–696 | 줄 36 × 7 + 점선 1 × 6 = 258 |
| └ └ `archive/row-1` | 438–474 | 10.11 일 |
| └ └ `archive/row-2` | 475–511 | 10.10 토 |
| └ └ `archive/row-3` | 512–548 | 10.09 금 |
| └ └ `archive/row-4` | 549–585 | 10.08 목 (0건, 흐린 줄) |
| └ └ `archive/row-5` | 586–622 | 10.07 수 |
| └ └ `archive/row-6` | 623–659 | 10.06 화 |
| └ └ `archive/row-7` | 660–696 | 10.05 월 |
| └ (간격) | 696–708 | `spacing.sm` 12 |
| └ `archive/cut-line` | 708–709 | 점선, 아래 padding 16 뒤 종이 끝(725) |
| (간격) | 725–733 | `spacing.xs` 8 |
| `caption` | 733–751 | |
| (빈 공간) | 751–764 | 캔버스 여백 |
| `nav` | 764–812 | `nav/home` 높이 48, x 24–366 |
| 하단 여백 | 812–844 | `spacing.xl` 32 (홈 인디케이터) |

- 그림자 없음. 깊이는 `canvas` ↔ `surface-card`(종이) ↔ `surface-strong`/`ink`(본체) 대비와 1px 테두리로만 (S2와 동일)
- `summary`와 `archive`는 별개의 종이 두 장처럼 16 간격을 두고 놓는다. 둘 다 모서리 0(잘린 종이)

## 토큰 사용
| 요소 | 색 (colors) | 모서리 (rounded) | 간격 (spacing) |
|---|---|---|---|
| 프레임 배경 | `canvas` | — | 상 `xxl` 48, 좌우 `lg` 24, 하 `xl` 32 |
| `printer/brand` 배경 / `cally` / `RECEIPT ARCHIVE` | `ink` / `primary` / `muted-soft` | 위 `xl` 16, 아래 `none` 0 | padding 좌우 `base` 16 |
| `printer/case` | `surface-strong` | 위 `none` 0, 아래 `xl` 16 | padding `xs` 8 · `base` 16 |
| `printer/display` 배경 / 글자 | `ink` / `timeline-grep` | `sm` 6 | padding 좌우 `xs` 8 |
| `tabs` 바탕 | `surface-strong` | `pill` 9999 | padding `xxs` 4, gap `xxs` 4 |
| `tab/week`(활성) 배경 / 글자 | `ink` / `on-primary` | `pill` 9999 | padding 0 (가운데 정렬) |
| `tab/day`, `tab/month` 글자 | `muted` (채움 없음) | `pill` 9999 | padding 0 |
| `period/prev` 배경 / 테두리 / 글자 | `surface-card` / `hairline-strong` / `ink` | `full` 9999 | — |
| `period/next`(비활성) 테두리 / 글자 | `hairline` / `muted-soft` (채움 없음) | `full` 9999 | — |
| `period/label` / `period/year` | `ink` / `muted` | — | `period/title` gap 0 |
| `summary`, `archive` 종이 / 테두리 | `surface-card` / `hairline` | `none` 0 | padding `base` 16 · `lg` 24 |
| `summary/name` 좌 / 우 | `muted` / `muted-soft` | — | — |
| `summary/count` 라벨 / 값 | `muted` / `ink` | — | 요약 내부 gap `sm` 12 |
| `summary/divider` (실선) | `ink` | — | — |
| `summary/total` (TOTAL, 금액) | `ink` | — | — |
| `archive/columns` | `muted-soft` | — | 아래 gap `xs` 8 |
| `archive/divider-top`, `archive/cut-line` (점선) | `hairline-strong` | — | cut-line 위 gap `sm` 12 |
| `archive/divider-1`~`6` (점선) | `hairline` | — | — |
| 줄 `date` / `count` / `price` / `chevron` | `ink` / `muted` / `ink` / `muted-soft` | — | 줄 padding 상하 `xs` 8, gap `sm` 12 |
| 0건 줄 글자 전체 | `muted-soft` | — | 같음 |
| `caption` | `muted` | — | 위 gap `xs` 8 |
| `nav/home` 배경 / 글자 | `ink` / `on-primary` | `lg` 12 | padding 좌우 `base` 16 |

- design.md 컴포넌트의 개별 padding(10px 18px 등)은 쓰지 않는다
- `timeline-grep` 외 `timeline-*`, `semantic-*` 색은 쓰지 않는다. 특히 `timeline-edit`은 변수 이름 노출을 피하려 바인딩하지 않는다

## 상태 예시 데이터
시안 상태: S2에서 `아카이브 보기`를 눌러 들어온 직후. 주별 탭, 가장 최근 영수증(2026.10.11 일)이 들어 있는 주 **2026.10.05 월 – 10.11 일**. 최신 날짜가 위(가정 1).

| 레이어 | date | count | price | 비고 |
|---|---|---|---|---|
| `archive/row-1` | 10.11 일 | 6건 | ₩38,650 | S2 영수증과 같은 값 |
| `archive/row-2` | 10.10 토 | 4건 | ₩52,300 | |
| `archive/row-3` | 10.09 금 | 5건 | ₩27,400 | |
| `archive/row-4` | 10.08 목 | 0건 | ₩0 | 기록 0건 — 흐린 줄, 누름 반응 없음 |
| `archive/row-5` | 10.07 수 | 3건 | ₩14,800 | |
| `archive/row-6` | 10.06 화 | 4건 | ₩21,350 | |
| `archive/row-7` | 10.05 월 | 5건 | ₩19,700 | |

- 요일 확인: 2026.10.11은 일요일 → 10.05 월, 10.06 화, 10.07 수, 10.08 목, 10.09 금, 10.10 토 (월요일 시작 주, F5)
- 금액 검산: 38,650 + 52,300 = 90,950 → + 27,400 = 118,350 → + 0 = 118,350 → + 14,800 = 133,150 → + 21,350 = 154,500 → + 19,700 = **174,200**
- 건수 검산: 6 + 4 + 5 + 0 + 3 + 4 + 5 = **27건**
- 영수증 장수: 기록이 있는 날 6일 = **6장** (0건인 10.08은 영수증 없음, 가정 2)
- `summary/name`: `WEEKLY RECEIPT` / `MON – SUN`
- `summary/count`: `영수증` / `6장 · 27건`
- `summary/total`: `TOTAL` / `₩174,200`
- `period/year` `2026`, `period/label` `10.05 월 – 10.11 일`
- `printer/display`: `ARCHIVE · WEEK`
- 모든 금액은 ₩ + 천 단위 콤마, JetBrains Mono, 우측 정렬로 끝자리를 맞춘다

## 반영 항목
p1-items.json 5개 모두 반영한다.

1. **[U5 · 아카이브]** "주별·월별 보기에서 목록 위에 기간 요약 영역을 고정해 기간 이름, 영수증 장수, TOTAL 합계(₩, JetBrains Mono, 우측 정렬)를 영수증 하단 합계 줄처럼 보여준다."
   → `summary`: `summary/name`(기간 이름 `WEEKLY RECEIPT`) · `summary/count`(`6장 · 27건`) · `summary/divider`(ink 실선) · `summary/total`(`TOTAL` / `₩174,200`, JetBrains Mono 24px/700 우측 정렬). S2 `receipt/count` → `receipt/divider-total` → `receipt/total` 순서를 그대로 따른다.
2. **[U5 · 레이아웃]** "화면 상단에 '일·주·월' 알약형 세그먼트 탭 3개를 가로로 두고 선택된 탭만 채워 표시해, 시트나 팝업 없이 같은 화면에서 보기 단위를 전환한다."
   → `tabs`(`rounded.pill`, `surface-strong`) 안 `tab/day` · `tab/week` · `tab/month`. 활성 `tab/week`만 `ink` 채움. 같은 화면 안에서 아래 내용만 바뀐다.
3. **[U4 · 영수증 표현]** 일별 보기는 왼쪽 세로선에 날짜 라벨을 달고 그 오른쪽에 S2와 같은 감열지 영수증(cally·날짜·건별 줄·TOTAL·절취선)을 날짜순으로 한 장씩 쌓아 읽기 전용으로 보여준다.
   → 이 시안은 주별 상태라 그리지 않고, 인터랙션 메모의 일별 보기 설명과 줄 → 하루 영수증 열기에 반영한다.
4. **[U4 · 아카이브]** "주별·월별 보기의 목록은 하루 영수증 1장을 한 줄로 접어 '10.06 월 · 5건 · ₩금액(우측 정렬)' 형태의 날짜·건수·금액 3열 행으로 나열한다."
   → `archive/row-1`~`7` = `date`(`10.11 일`) · `count`(`6건`) · `price`(`₩38,650`, 우측 정렬) + `chevron`. 위에 `archive/columns` 열 머리.
5. **[U5 · 레이아웃]** "탭 아래 중앙에 ◀ 기간 ▶ 화살표 이동을 두고 주별은 월요일 시작 범위('10.06 월 – 10.12 일'), 월별은 '2026년 10월'로 표기해 이전·다음 기간으로 넘긴다."
   → `period/prev` ◀ · `period/title`(`2026` / `10.05 월 – 10.11 일`) · `period/next` ▶. 2026년 기준 월요일 시작 주는 10.05–10.11이므로 실제 날짜에 맞춰 표기한다. 월별 표기는 인터랙션 메모 참고.

## 인터랙션 메모
- **진입**: S2 `nav/archive` → 이 화면(주별, 최근 영수증이 든 주). 다른 진입 경로는 이번 시안 범위 밖
- **탭 전환**(`tab/*`): 같은 화면에서 `period`·`summary`·`archive` 내용만 바뀐다. 시트·팝업·화면 전환 없음
  - **일별** (`tab/day`): `period/label`이 `2026.10.11 일` 하루로 바뀌고, ◀ ▶는 하루씩 이동. `summary`는 숨기고(F5: 합계는 주별·월별에만), 그 자리에 S2와 같은 감열지 영수증 1장(`receipt/*`: cally · 날짜 · 건별 [시각 · 물품명 · 금액] · 건수 · TOTAL · 절취선)을 왼쪽 날짜 라벨과 함께 보여준다. 0건인 날은 영수증 대신 `0건 · ₩0` 흐린 한 줄
  - **주별** (`tab/week`): 이 시안. ◀ ▶는 한 주(월~일)씩 이동
  - **월별** (`tab/month`): `period/label`이 `2026년 10월`, `summary/name`이 `MONTHLY RECEIPT`, `archive/rows`가 그달 날짜 수만큼 같은 줄 형식으로 늘어나 화면이 세로 스크롤된다. `summary`는 목록 위에 고정
- **줄 누름**(`archive/row-n`): 그날 영수증을 S2와 같은 모양의 읽기 전용 영수증 화면으로 연다. 열린 영수증에도 조작 요소 없음(N2). 0건 줄은 반응 없음
- **기간 이동**(`period/prev`, `period/next`): 이전·다음 기간으로 넘긴다. 더 최근 영수증이 없으면 `period/next` 비활성
- `summary`, `archive` 종이는 길게 누르기·스와이프 반응 없음
- `nav/home` → S1 계산기
- 공유·저장·검색·카테고리·통계·차트·예산·수입 등 PRD에 없는 요소는 넣지 않는다

## 금지 확인
**N2 — 출력된 영수증 변경 불가 (S3 적용, ★)**
- 아카이브 화면과 줄을 눌러 여는 하루 영수증 어디에도 변경 관련 UI 요소 0개: 행 스와이프 액션, 더보기(⋮) 메뉴, 연필·휴지통 아이콘, 체크박스, 다중 선택 모드 모두 없음. 레퍼런스(페이워크 우상단 버튼, Kia ⋮ 메뉴)의 해당 요소는 가져오지 않았다
- 줄의 유일한 반응은 "그날 영수증 열기(읽기 전용)"이며 `chevron` `›`만 둔다
- 레이어 이름 조각에 `edit`, `delete` 0개. 사용한 이름: `printer/*`(brand, case, display), `tabs`, `tab/day`·`tab/week`·`tab/month`, `period/*`(prev, title, year, label, next), `summary/*`(name, count, divider, total), `archive/*`(columns, divider-top, rows, row-1~7, divider-1~6, cut-line), 줄 자식 `date`·`count`·`price`·`chevron`·`chevron-space`, `caption`, `nav`, `nav/home` — 모두 해당 없음. `credit` 같은 섞인 이름도 쓰지 않는다
- 화면의 모든 텍스트에 rules.yaml `N2.forbidden_text`의 한글 단어 3개 0개. 화면 텍스트 전체: `cally`, `RECEIPT ARCHIVE`, `ARCHIVE · WEEK`, `일별`, `주별`, `월별`, `◀`, `▶`, `2026`, `10.05 월 – 10.11 일`, `WEEKLY RECEIPT`, `MON – SUN`, `영수증`, `6장 · 27건`, `TOTAL`, `₩174,200`, `DATE`, `COUNT`, `AMOUNT`, 줄 7개의 날짜·건수·금액, `›`, `날짜를 누르면 그날 영수증을 볼 수 있어요`, `계산기로`. 디자이너는 레이어 설명·컴포넌트 설명에도 이 세 단어를 넣지 않는다
- `timeline-edit` 색 변수를 이 화면 노드에 바인딩하지 않는다

**N1 — 기록까지 입력 단계 ≤ 2 (S1 전용)**
- S3는 판정 대상 아님. 입력 요소 없음, `input/*` 레이어 0개
- 그래도 레이어 이름 조각에 `modal`, `popup`, `sheet`, `select`, `dropdown` 0개. 보기 전환은 오버레이가 아니라 화면에 놓인 `tabs`로 하고, 이름에 `select` 계열 단어를 쓰지 않는다

**기타**
- 색은 design.md `colors` HEX만, 모서리는 `rounded` 값만, 간격은 `spacing` 값 또는 0만
- 서체는 Pretendard, JetBrains Mono 2종만
- PRD Non-goals(수입, 카테고리, 예산, 통계·차트·카테고리 분석, 연동, 로그인·동기화, 월간 분석 화면, 설정 화면, 다크모드) 요소 0개. 기간 합계는 숫자 TOTAL 한 줄뿐이며 그래프·비율·평균 같은 분석 표시는 넣지 않는다

## 가정 (사용자 확인 필요)
PRD §11 미정 사항과 명시되지 않은 동작에 대해 아래처럼 가정했다. 승인 단계(G3)에서 확인 부탁드린다.

1. **정렬 순서 (§11)**: 최신 날짜가 위. 주별·월별 목록, 일별 영수증 쌓기 모두 최신 → 과거 순
2. **기록 0건인 날 (§11)**: 마감 시 영수증을 출력하지 않는다. 목록에는 날짜 줄을 빼지 않고 `0건 · ₩0` 흐린 줄(`muted-soft`)로 남겨 주의 7일이 모두 보이게 한다. 누름 반응 없음, 영수증 장수에 넣지 않음(이 주: 7일 중 6장)
3. **`period/next` 비활성**: 더 최근에 마감된 영수증이 없는 기간이면 ▶를 비활성(테두리 `hairline`, 글자 `muted-soft`)으로 둔다. 아직 마감 전인 오늘 기록은 아카이브에 나타나지 않는다
4. **진입 시 기본 보기**: S2에서 들어오면 주별 탭, 가장 최근 영수증이 든 주를 연다 (이 시안 상태)
5. **기간 요약 건수**: `summary/count`에 영수증 장수와 함께 기간의 총 기록 건수(`6장 · 27건`)를 같이 적는다. 장수만 원하면 `6장`으로 줄인다
6. **일별 보기의 합계**: F5에 따라 일별 보기에는 기간 요약(`summary`)을 두지 않고, 하루 영수증 자체의 TOTAL만 보인다
