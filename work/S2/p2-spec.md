# S2 하루 마감 영수증 (P2 설계, 시도 1)

- 프레임: `S2-concept` / `S2-final`, 390×844 세로
- 콘셉트: S1에서 승인·제작된 빈티지 인쇄 계산기와 **같은 물건**이다. 00:00에 그날의 테이프가 끝까지 인쇄되어 계산기 상단 출력구에서 한 장의 감열지 영수증으로 나온 장면. 화면 위쪽에 계산기 본체의 윗부분(브랜드 띠 + 작은 표시창 + 출력구)만 잘라 보여주고, 그 출력구 아래로 흰 영수증이 길게 내려온다
- 서체: Pretendard(한글 물품명·안내 문구), JetBrains Mono(로고 인쇄·날짜·시각·금액·건수·TOTAL·영문 라벨). 이 2종 외 사용 금지
- 색·모서리·간격: docs/design.md YAML의 `colors` / `rounded` / `spacing` 토큰만 사용 (간격은 토큰 값 또는 0)
- 영수증 전체(앱 이름 ~ 절취선)가 스크롤 없이 390×844 안에 모두 보이게 한다

## 대상 유저스토리
- **U3** (주): 사용자가 하루 마감 시각에 그날 기록을 영수증 1장으로 확인한다 — F3 기본 00:00 자동 마감, 수동 출력 없음
- **U4** (연결): 사용자가 아카이브에서 지난 날짜의 영수증을 본다 — 이 화면에서는 아카이브(S3)로 가는 이동 요소 `nav/archive` 1개만 둔다. 아카이브 화면 자체는 S3 범위

## 구성 요소
레이어 이름은 harness/artifacts.md 규칙을 따른다. 영수증 요소는 모두 `receipt/` 접두어.
`edit`, `delete` 조각이 들어간 레이어 이름 0개, `modal`·`popup`·`sheet`·`select`·`dropdown` 조각 0개. 이 화면에는 `input/*` 레이어를 두지 않는다.

**PRD §8 영수증 필수 항목 대응**

| §8 항목 | 레이어 |
|---|---|
| 상단 앱 이름 cally | `receipt/header` (`receipt/logo`) |
| 날짜 | `receipt/date` |
| 건별 [시각 · 물품명 · 금액] | `receipt/row-1` … `receipt/row-6` |
| 건수 | `receipt/count` |
| TOTAL | `receipt/total` |
| 하단 절취선(점선) | `receipt/cut-line` |

**레이어 목록**

| 레이어 이름 | 종류 | 내용 |
|---|---|---|
| `S2-concept` / `S2-final` | 프레임 390×844 | 배경 `canvas` |
| `printer` | 오토레이아웃(세로) | 계산기 본체 윗부분(부분 노출). 배경 `surface-strong`, 위쪽 두 모서리 `rounded.xl`, 아래쪽 모서리 0. S1 케이스와 같은 재질 |
| `printer/brand` | 오토레이아웃(가로) | S1과 같은 브랜드 띠. 배경 `ink`. 좌: `cally`(Pretendard 16px/600, `primary`), 우: `ELECTRONIC LEDGER`(JetBrains Mono 11px, `muted-soft`). space-between |
| `printer/display` | 오토레이아웃(가로) | S1 표시창의 축소판. 배경 `ink`, 모서리 `rounded.sm`. 텍스트 `END OF DAY  00:00`(JetBrains Mono 11px, `timeline-grep` — S1 VFD 민트 글자) |
| `printer/slot` | 사각형 | 출력구. 배경 `ink`, 높이 8, 모서리 `rounded.xs`. 영수증 종이가 이 아래에서 나온다 |
| `receipt` | 오토레이아웃(세로) | 감열지 영수증 본체. 배경 `surface-card`(흰 종이), 테두리 1px `hairline`, 모서리 0(`rounded.none`, 잘린 종이), 그림자 없음. 위쪽 끝은 `printer/slot` 바로 아래에 붙여 출력구에서 나온 것처럼 보이게 한다 |
| `receipt/header` | 오토레이아웃(세로, 가운데 정렬) | 영수증 머리. 자식: `receipt/logo`, `receipt/subtitle` |
| `receipt/logo` | 텍스트 | `cally` — JetBrains Mono 28px/700, `ink`, 가운데 정렬 (감열 인쇄된 로고) |
| `receipt/subtitle` | 텍스트 | `DAILY RECEIPT` — JetBrains Mono 11px/600, 자간 넓게, `muted`, 가운데 |
| `receipt/date` | 텍스트 | `2026.10.11 SUN` — JetBrains Mono 13px, `ink`, 가운데 |
| `receipt/closed-at` | 텍스트 | `CLOSED 00:00 · AUTO PRINT` — JetBrains Mono 11px, `muted`, 가운데 |
| `receipt/divider-top` | 선(점선) | 1px `hairline-strong`, 점선. 머리와 품목 구분 |
| `receipt/columns` | 오토레이아웃(가로) | 열 머리. `TIME` / `ITEM` / `AMOUNT` — JetBrains Mono 11px, `muted-soft`. `AMOUNT`는 우측 정렬 |
| `receipt/rows` | 오토레이아웃(세로) | 건별 행 묶음, 행 간격 `spacing.xs` 8 |
| `receipt/row-1` … `receipt/row-6` | 오토레이아웃(가로) | 한 행 = [시각 · 물품명 · 금액]. 시각 좌측 고정폭, 물품명 채움, 금액 우측 정렬. 행 안 gap `spacing.sm` 12. 탭 반응 없음(정적 인쇄물) |
| └ `time` / `name` / `price` | 텍스트(행 자식) | 시각: JetBrains Mono 12px `muted` / 물품명: Pretendard 13px `body` / 금액: JetBrains Mono 13px `ink`, **우측 정렬** |
| `receipt/divider-items` | 선(점선) | 1px `hairline-strong`, 점선. 품목과 요약 구분 |
| `receipt/count` | 오토레이아웃(가로) | 좌: `건수`(Pretendard 13px `muted`), 우: `6건`(JetBrains Mono 13px `ink`, 우측 정렬) |
| `receipt/divider-total` | 선(실선) | 1px `ink`. TOTAL을 위 줄과 분리 |
| `receipt/total` | 오토레이아웃(가로, 아래 정렬) | 좌: `TOTAL`(JetBrains Mono 16px/700 `ink`), 우: `₩38,650`(JetBrains Mono 24px/700 `ink`, **우측 정렬**) |
| `receipt/footer` | 텍스트 | `PRINTED · 출력 완료` — `PRINTED`는 JetBrains Mono, `· 출력 완료`는 Pretendard, 11px, `muted`, 가운데. 확정·보관된 인쇄물임을 표시 |
| `receipt/cut-line` | 선(점선) | 하단 절취선. 1px `hairline-strong`, 점선(대시 4·간격 4). 영수증 전체 폭을 가로지르고 종이는 이 선 아래 짧은 여백 뒤에서 끝난다 |
| `caption` | 텍스트 | `00:00에 자동 마감되어 아카이브에 보관됐어요` — Pretendard 13px, `muted`, 가운데 |
| `nav` | 오토레이아웃(가로) | 하단 이동 버튼 2개, gap `spacing.sm` 12, 각 버튼 폭 채움 |
| `nav/home` | 버튼 | `계산기로` — Pretendard 15px/600 `ink`. 배경 `surface-card`, 테두리 1px `hairline-strong`, 모서리 `rounded.lg`, 높이 48. 새 날의 S1로 이동 |
| `nav/archive` | 버튼 | `아카이브 보기` — Pretendard 15px/600 `on-primary`. 배경 `ink`, 모서리 `rounded.lg`, 높이 48. S3로 이동 |

- 버튼 모서리는 S1의 둥근 사각 키와 같은 계열(`rounded.lg`)로 맞춘다
- `primary` 오렌지는 `printer/brand`의 `cally` 글자에만 쓴다 (S1과 동일한 브랜드 표기). 영수증 종이 위는 감열지처럼 `ink`/`muted` 계열만

## 레이아웃
390×844 기준 대략적인 y 범위. `printer`는 좌우 여백 `spacing.lg` 24(폭 342, x 24–366), `receipt`는 좌우 여백 `spacing.xxl` 48 대신 위치로 x 40–350(폭 310)에 가운데 정렬 — 본체보다 좁아 출력구에서 나온 종이처럼 보인다. 영수증 안쪽 padding 좌우 `spacing.lg` 24 → 내용 폭 262.

| 영역 | y 범위 | 메모 |
|---|---|---|
| 상태바 여백 | 0–48 | 비워둠 (프레임 상단 padding `spacing.xxl` 48) |
| `printer/brand` | 48–80 | 높이 32, 좌우 padding `spacing.base` 16 |
| `printer` 케이스 부분 | 80–124 | padding 상하 `spacing.xs` 8, 좌우 `spacing.base` 16, 자식 gap `spacing.xs` 8 |
| └ `printer/display` | 88–108 | 높이 20, padding 좌우 `spacing.xs` 8 |
| └ `printer/slot` | 116–124 | 높이 8, 케이스 폭 거의 전체 |
| `receipt` | 124–652 | 출력구 바로 아래에서 시작. padding 상 `spacing.lg` 24, 좌우 `spacing.lg` 24, 하 `spacing.base` 16 |
| └ `receipt/header` | 148–196 | logo 36 + subtitle 12 (gap 0) |
| └ (간격) | 196–208 | `spacing.sm` 12 |
| └ `receipt/date` | 208–226 | |
| └ `receipt/closed-at` | 230–244 | date와 gap `spacing.xxs` 4 |
| └ (간격) | 244–260 | `spacing.base` 16 |
| └ `receipt/divider-top` | 260–261 | 점선 |
| └ (간격) | 261–273 | `spacing.sm` 12 |
| └ `receipt/columns` | 273–289 | |
| └ (간격) | 289–297 | `spacing.xs` 8 |
| └ `receipt/rows` (6행) | 297–457 | 행 높이 20 × 6 + 간격 8 × 5 = 160 |
| └ (간격) | 457–469 | `spacing.sm` 12 |
| └ `receipt/divider-items` | 469–470 | 점선 |
| └ (간격) | 470–482 | `spacing.sm` 12 |
| └ `receipt/count` | 482–502 | |
| └ (간격) | 502–514 | `spacing.sm` 12 |
| └ `receipt/divider-total` | 514–515 | 실선 `ink` |
| └ (간격) | 515–527 | `spacing.sm` 12 |
| └ `receipt/total` | 527–559 | 높이 32 |
| └ (간격) | 559–583 | `spacing.lg` 24 |
| └ `receipt/footer` | 583–599 | |
| └ (간격) | 599–635 | `spacing.lg` 24 + 여유 |
| └ `receipt/cut-line` | 635–636 | 점선. 아래 `spacing.base` 16 뒤 종이 끝(652) |
| (간격) | 652–676 | `spacing.lg` 24 |
| `caption` | 676–694 | |
| (빈 공간) | 694–764 | 캔버스 여백 (영수증 행이 늘어날 때의 여유분) |
| `nav` | 764–812 | 높이 48, x 24–366 |
| 하단 여백 | 812–844 | `spacing.xl` 32 (홈 인디케이터) |

- 그림자 없음. 깊이는 `canvas`(바탕) ↔ `surface-card`(종이) ↔ `surface-strong`/`ink`(본체) 대비와 1px 테두리로만
- 기록이 많은 날은 `receipt/rows`가 길어져 영수증이 아래로 늘어나고 화면은 세로 스크롤된다. 시안은 6건 기준으로 한 화면 안에 전체가 보이게 그린다

## 토큰 사용
| 요소 | 색 (colors) | 모서리 (rounded) | 간격 (spacing) |
|---|---|---|---|
| 프레임 배경 | `canvas` | — | 상 `xxl` 48, 좌우 `lg` 24, 하 `xl` 32 |
| `printer` 케이스 | `surface-strong` | 위 `xl` 16 / 아래 `none` 0 | padding `xs` 8 · `base` 16, gap `xs` 8 |
| `printer/brand` 배경 / `cally` / `ELECTRONIC LEDGER` | `ink` / `primary` / `muted-soft` | 위 `xl` 16 | padding 좌우 `base` 16 |
| `printer/display` 배경 / 글자 | `ink` / `timeline-grep` | `sm` 6 | padding 좌우 `xs` 8 |
| `printer/slot` | `ink` | `xs` 4 | — |
| `receipt` 종이 / 테두리 | `surface-card` / `hairline` | `none` 0 | padding `lg` 24 (하 `base` 16) |
| `receipt/logo`, `receipt/date`, 행 금액, 건수 값, TOTAL, 합계 금액 | `ink` | — | — |
| `receipt/subtitle`, `receipt/closed-at`, 행 시각, `건수` 라벨, `receipt/footer` | `muted` | — | — |
| `receipt/columns` | `muted-soft` | — | — |
| 행 물품명 | `body` | — | 행 안 gap `sm` 12, 행 사이 `xs` 8 |
| `receipt/divider-top`, `receipt/divider-items`, `receipt/cut-line` (점선) | `hairline-strong` | — | — |
| `receipt/divider-total` (실선) | `ink` | — | — |
| `caption` | `muted` | — | — |
| `nav` | — | — | gap `sm` 12 |
| `nav/home` | 배경 `surface-card`, 테두리 `hairline-strong`, 글자 `ink` | `lg` 12 | padding 좌우 `base` 16 |
| `nav/archive` | 배경 `ink`, 글자 `on-primary` | `lg` 12 | padding 좌우 `base` 16 |

- design.md 컴포넌트의 개별 padding(10px 18px 등)은 쓰지 않는다
- `timeline-grep` 외 `timeline-*`, `semantic-*` 색은 쓰지 않는다. 특히 `timeline-edit`(라벤더)은 이름 때문에 혼동을 피하려 사용하지 않는다 (색 이름은 레이어 이름이 아니지만, 변수 바인딩 이름으로 노출될 여지를 없앤다)

## 상태 예시 데이터
시안은 "2026.10.11(일) 기록이 00:00에 자동 마감되어 영수증이 막 출력된" 상태로 그린다. S1 시안과 같은 날이며, S1에서 입력 중이던 붕어빵이 `=`로 기록된 뒤 마감된 결과다.

| 레이어 | 시각 | 물품명 | 금액 |
|---|---|---|---|
| `receipt/row-1` | 08:41 | 지하철 | ₩1,550 |
| `receipt/row-2` | 12:20 | 김치찌개 | ₩9,000 |
| `receipt/row-3` | 13:05 | 편의점 생수 | ₩1,200 |
| `receipt/row-4` | 15:47 | 다이소 수납함 | ₩5,000 |
| `receipt/row-5` | 19:32 | 올리브영 선크림 | ₩18,900 |
| `receipt/row-6` | 20:15 | 붕어빵 | ₩3,000 |
| `receipt/count` | — | 건수 | 6건 |
| `receipt/total` | — | TOTAL | ₩38,650 |

- 검산: 1,550 + 9,000 + 1,200 + 5,000 + 18,900 + 3,000 = 38,650
- 헤더: `cally` / `DAILY RECEIPT` / `2026.10.11 SUN` / `CLOSED 00:00 · AUTO PRINT`
- `printer/display`: `END OF DAY  00:00`
- 모든 금액은 ₩ + 천 단위 콤마, JetBrains Mono, 우측 정렬로 끝자리를 맞춘다

## 반영 항목
p1-items.json 5개 모두 반영한다.

1. **[U3 · 영수증 표현]** "영수증 상단에 앱 이름 'cally'를 로고처럼 중앙 크게 찍고 그 아래 날짜를 작은 글씨로 두는 POS 영수증 헤더 순서를 S2 감열지 영수증 상단에 그대로 적용한다"
   → `receipt/logo`(`cally` 28px/700 가운데) → `receipt/subtitle` → `receipt/date`(13px) → `receipt/closed-at`(11px) 순서.
2. **[U3 · 레이아웃]** "건별 행을 [시각(좌) · 물품명(가운데) · 금액(우측 정렬)] 3열 한 줄로 구성하고 금액 열을 모노스페이스 우측 정렬로 맞춰 영수증 품목 줄처럼 보이게 한다"
   → `receipt/row-n` = `time`(좌) · `name`(채움) · `price`(JetBrains Mono 우측 정렬), 위에 `receipt/columns` 열 머리.
3. **[U3 · 영수증 표현]** "품목 목록 아래에 '건수 N건'을 좌측, 금액 합을 우측에 두는 요약 한 줄을 넣어 TOTAL 직전 건수를 표기한다"
   → `receipt/count`: 좌 `건수`, 우 `6건`. TOTAL 바로 위 줄. (금액 합은 바로 아래 `receipt/total`에서 강조 표기하므로 건수 줄 우측에는 건수 값을 둔다)
4. **[U3 · 영수증 표현]** "건수 줄 아래 구분선을 두고 'TOTAL'과 합계 금액을 품목보다 크고 굵은 모노스페이스로 표기해 영수증의 최종 합계로 분리한다"
   → `receipt/divider-total`(1px `ink` 실선) 아래 `receipt/total`: `TOTAL` 16px/700, `₩38,650` 24px/700 JetBrains Mono (품목 13px보다 크고 굵게).
5. **[U3 · 아카이브]** "출력된 영수증은 읽기 전용 문서처럼 라벨–값 행과 합계만 보여주고 수정·삭제 컨트롤을 두지 않으며, 하단은 점선 절취선으로 마무리해 '확정·보관됨'을 표현한다"
   → 영수증 안에는 행·합계·라벨만 있고 조작 요소 0개. 맨 아래 `receipt/cut-line` 점선, `receipt/footer` `PRINTED · 출력 완료`와 `caption`으로 보관됨을 표현.

## 인터랙션 메모
- 진입: 00:00 자동 마감(F3) 뒤 처음 앱을 열면 이 화면이 뜬다. 수동 출력 버튼 없음
- `receipt/*`는 탭·길게 누르기·스와이프 반응 없음 (정적 인쇄물)
- `nav/home` → 새 날의 S1(빈 테이프), `nav/archive` → S3 아카이브(이 날짜 영수증이 맨 위에 보관된 상태)
- 공유·저장·카테고리·통계 등 PRD에 없는 기능 요소는 넣지 않는다

## 금지 확인
**N2 — 출력된 영수증 변경 불가 (S2 적용, ★)**
- 영수증 화면에 변경 관련 UI 요소 0개: 행 탭 반응, 스와이프 액션, 더보기 메뉴, 연필·휴지통 아이콘, 체크박스 모두 없음
- 레이어 이름 조각(`/`·`-`·`_` 기준)에 `edit`, `delete` 0개. 사용한 이름: `printer/*`, `receipt/*`(header, logo, subtitle, date, closed-at, divider-top, columns, rows, row-1~6, time, name, price, divider-items, count, divider-total, total, footer, cut-line), `caption`, `nav`, `nav/home`, `nav/archive` — 모두 해당 없음. `credit`처럼 조각 안에 섞이는 이름도 쓰지 않는다
- 화면의 모든 텍스트에 금지 문자열 3개(수정·삭제·편집에 해당하는 한글 단어) 0개. 불변성은 `PRINTED · 출력 완료`, `CLOSED 00:00 · AUTO PRINT`, `아카이브에 보관됐어요`로만 표현한다. 디자이너는 안내 문구·레이어 설명·컴포넌트 설명에도 이 세 단어를 넣지 않는다
- `timeline-edit` 색 변수를 이 화면 노드에 바인딩하지 않는다

**N1 — 기록까지 입력 단계 ≤ 2 (S1 전용)**
- S2는 판정 대상 아님. 이 화면에는 입력 요소가 없고 `input/*` 레이어 0개
- 그래도 레이어 이름 조각에 `modal`, `popup`, `sheet`, `select`, `dropdown` 0개 — 영수증은 오버레이가 아니라 화면 자체에 놓인다 (`selected` 같은 파생어도 피한다)

**기타**
- 색은 design.md `colors` HEX만, 모서리는 `rounded` 값만, 간격은 `spacing` 값 또는 0만
- 서체는 Pretendard, JetBrains Mono 2종만
- PRD Non-goals(수입, 카테고리, 예산, 통계·차트, 연동, 로그인, 설정 화면, 다크모드) 요소를 넣지 않는다
