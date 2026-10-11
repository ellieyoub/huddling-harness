# S1 메인 — 계산기 키패드 + 오늘의 테이프 (P2 설계, 시도 1)

- 프레임: `S1-concept` / `S1-final`, 390×844 세로
- 서체: Pretendard(기본·한글), JetBrains Mono(시각·금액·키 숫자·TOTAL). 이 2종 외 사용 금지
- 색·모서리·간격: docs/design.md YAML의 `colors` / `rounded` / `spacing` 토큰만 사용 (간격은 토큰 값 또는 0)

## 대상 유저스토리
- **U1** (주): 사용자가 계산기 화면에서 물품명과 금액을 입력해 지출을 기록한다 — 물품명 → 금액 → `=` 로 끝
- **U2** (보조): 사용자가 마감 전에 남긴 기록을 수정하거나 삭제한다 — 오늘의 테이프 행을 탭하면 같은 표시창에서 바로 고침 (인터랙션 메모로만 표현, 아래 "인터랙션 메모" 참고)

## 구성 요소
레이어 이름은 harness/artifacts.md 규칙을 따른다. `input/*` 레이어는 정확히 2개(`input/item`, `input/amount`)만 둔다. 키는 `input/` 아래에 두지 않는다.
`modal`, `popup`, `sheet`, `select`, `dropdown` 조각이 들어간 레이어 이름은 하나도 쓰지 않는다.

| 레이어 이름 | 종류 | 내용 |
|---|---|---|
| `S1-concept` / `S1-final` | 프레임 390×844 | 배경 `canvas` |
| `header` | 오토레이아웃(가로) | 좌: 워드마크 `cally`, 우: 오늘 날짜 |
| `header/logo` | 텍스트 | `cally` — Pretendard 22px/600, `primary` |
| `header/date` | 텍스트 | `2026.10.11 SUN` — JetBrains Mono 13px, `muted` |
| `tape` | 오토레이아웃(세로) | 오늘의 테이프 (감열지 띠). 배경 `canvas-soft`, 테두리 1px `hairline`, 모서리 `rounded.lg` |
| `tape/title` | 텍스트 | `오늘의 테이프` — Pretendard 13px, `muted` |
| `tape/row-1` … `tape/row-5` | 오토레이아웃(가로) | 한 행 = [시각 · 물품명 · 금액]. 시각 좌측, 물품명 가운데(채움), 금액 우측 정렬 |
| └ `time` / `name` / `price` | 텍스트(행 자식) | 시각: JetBrains Mono 13px `muted` / 물품명: Pretendard 14px `body` / 금액: JetBrains Mono 14px `ink`, 우측 정렬 |
| `tape/divider` | 선(점선) | 1px `hairline-strong`, 점선 — 행과 합계 구분 |
| `tape/total` | 오토레이아웃(가로) | 좌: `5건`(Pretendard 13px `muted`) + `TOTAL`(JetBrains Mono 13px/600 `ink`), 우: `₩35,650`(JetBrains Mono 18px/600 `ink`, 우측 정렬). 테이프 맨 끝에 고정 |
| `display` | 오토레이아웃(세로) | 계산기 표시창. 배경 `surface-card`, 테두리 1px `hairline`, 모서리 `rounded.lg` |
| `input/item` | 오토레이아웃(가로) | 물품명 입력. 텍스트 `붕어빵`(Pretendard 16px `ink`), 비었을 때 플레이스홀더 `물품명`(`muted-soft`). 하단 1px `hairline` 구분선 |
| `input/amount` | 오토레이아웃(가로) | 금액 입력. `₩3,000` — JetBrains Mono 36px/400 `ink`, **우측 정렬**. 비었을 때 `₩0`(`muted-soft`) |
| `keypad` | 오토레이아웃(가로) | 숫자 3열 그리드(`keypad/digits`) + 기능 1열(`keypad/func`). 프레임 가운데 정렬 |
| `keypad/digits` | 오토레이아웃(세로, 행 4개) | 행: `7 8 9` / `4 5 6` / `1 2 3` / `00 0 000` |
| `key/0` … `key/9` | 원형 키 72×72 | 배경 `surface-card`, 테두리 1px `hairline-strong`, 숫자 JetBrains Mono 22px `ink`, cornerRadius 9999 (`rounded.full`) |
| `key/00`, `key/000` | 원형 키 72×72 | `key/0`과 같은 스타일 |
| `keypad/func` | 오토레이아웃(세로) | 위에서부터 `key/C`, `key/back`, `key/=` |
| `key/C` | 원형 키 72×72 | 배경 `surface-strong`, 글자 `C` JetBrains Mono 22px `ink`, cornerRadius 9999 |
| `key/back` | 원형 키 72×72 | 배경 `surface-strong`, 글자 `⌫` `ink`, cornerRadius 9999 (한 자리 지우기) |
| `key/=` | 세로 알약형 키 72×160 (2행 높이) | 배경 `primary`, 글자 `=` JetBrains Mono 28px `on-primary`, cornerRadius 9999. 누르면 기록 완료 |

키 개수: 숫자 10 + `00`·`000` 2 + `C`·`back`·`=` 3 = 15개. 키 레이어는 모두 `key/` 접두어.

## 레이아웃
390×844 기준 대략적인 y 범위 (좌우 바깥 여백 `spacing.lg` 24px, 콘텐츠 폭 342px).

| 영역 | y 범위 | 메모 |
|---|---|---|
| 상태바 여백 | 0–48 | 비워둠 (프레임 상단 padding `spacing.xxl` 48) |
| `header` | 48–80 | 높이 약 32, 좌우 space-between |
| (간격) | 80–96 | `spacing.base` 16 |
| `tape` | 96–356 | 안쪽 padding `spacing.base` 16, 행 간격 `spacing.xs` 8. title + 5행 + divider + total. 행이 늘면 테이프 안에서 위로 스크롤, `tape/total`은 바닥 고정 |
| (간격) | 356–372 | `spacing.base` 16 |
| `display` | 372–460 | 안쪽 padding `spacing.base` 16, 두 입력 사이 `spacing.xs` 8. `input/item` 위, `input/amount` 아래 |
| (간격) | 460–476 | `spacing.base` 16 |
| `keypad` | 476–812 | 키 72, 키 사이 가로·세로 gap `spacing.base` 16 → 4열 폭 336 × 4행 높이 336. `keypad`는 가로 가운데 정렬(좌우 padding 값 대신 정렬로 중앙 배치) |
| 하단 여백 | 812–844 | `spacing.xl` 32 (홈 인디케이터) |

- 구조는 계산기 본체처럼 상단 표시부(테이프 + 표시창) / 하단 키패드 상하 2분할
- `key/=`는 `keypad/func` 열의 3–4행을 세로로 차지 (72 + 16 + 72 = 160)
- 그림자 없음. 깊이는 1px 테두리와 `canvas` ↔ `surface-card` 대비로만

## 토큰 사용
| 요소 | 색 (colors) | 모서리 (rounded) | 간격 (spacing) |
|---|---|---|---|
| 프레임 배경 | `canvas` | — | 상 `xxl` 48, 좌우 `lg` 24, 하 `xl` 32, 섹션 사이 `base` 16 |
| `header/logo` | `primary` | — | — |
| `header/date`, `tape/title`, 행 시각, 건수 | `muted` | — | — |
| `tape` | 배경 `canvas-soft`, 테두리 `hairline` | `lg` | padding `base` 16, gap `xs` 8 |
| 행 물품명 | `body` | — | 행 안 gap `sm` 12 |
| 행 금액, TOTAL, 합계 금액 | `ink` | — | — |
| `tape/divider` | `hairline-strong` (점선) | — | — |
| `display` | 배경 `surface-card`, 테두리 `hairline` | `lg` | padding `base` 16, gap `xs` 8 |
| `input/item` 하단선 | `hairline` | — | padding 하 `xs` 8 |
| 입력 텍스트 / 플레이스홀더 | `ink` / `muted-soft` | — | — |
| 숫자 키, `00`, `000` | 배경 `surface-card`, 테두리 `hairline-strong`, 글자 `ink` | `full` (9999) | — |
| `key/C`, `key/back` | 배경 `surface-strong`, 글자 `ink` | `full` (9999) | — |
| `key/=` | 배경 `primary`, 글자 `on-primary` (눌림 상태는 `primary-active`) | `full` (9999) | — |
| `keypad` 행·열 | — | — | gap `base` 16 |

- design.md 컴포넌트의 개별 padding(10px 18px, 12px 16px 등)은 쓰지 않는다
- `timeline-*` 파스텔, `semantic-*` 색은 이 화면에서 쓰지 않는다

## 상태 예시 데이터
시안은 "오늘 5건을 기록했고, 6번째 지출을 금액까지 입력한 직후(`=` 누르기 직전)" 상태로 그린다.

오늘의 테이프 (2026.10.11 일요일)

| 레이어 | 시각 | 물품명 | 금액 |
|---|---|---|---|
| `tape/row-1` | 08:41 | 지하철 | ₩1,550 |
| `tape/row-2` | 12:20 | 김치찌개 | ₩9,000 |
| `tape/row-3` | 13:05 | 편의점 생수 | ₩1,200 |
| `tape/row-4` | 15:47 | 다이소 수납함 | ₩5,000 |
| `tape/row-5` | 19:32 | 올리브영 선크림 | ₩18,900 |
| `tape/total` | — | 5건 TOTAL | ₩35,650 |

표시창
- `input/item`: `붕어빵`
- `input/amount`: `₩3,000`

`=`를 누르면 `tape/row-6`(현재 시각 · 붕어빵 · ₩3,000)이 테이프 맨 아래에 추가되고 TOTAL은 `6건 ₩38,650`이 되며, 표시창은 빈 상태(`물품명` / `₩0`)로 돌아간다. 이 결과 상태는 시안에 따로 그리지 않는다.

## 반영 항목
p1-items.json에서 5개 모두 반영한다.

1. **[U1 · 입력 방식]** "하단 고정 3열 숫자 키패드의 '완료' 자리를 강조색 원형 '=' 키로 바꿔, 금액을 누르고 '='를 치면 별도 확인 없이 바로 기록되게 한다"
   → 숫자 3열 + 기능 1열 키패드를 하단에 고정, `key/=`를 `primary` 알약형 키로 두고 누르면 확인 단계 없이 바로 기록.
2. **[U1 · 레이아웃]** "화면을 상단 표시부(오늘의 테이프 + 입력 중인 물품명·금액 표시창)와 하단 절반 키패드로 나누는 상하 2분할 구조를 계산기 본체 형태로 채택한다"
   → y 96–460 상단 표시부(`tape` + `display`), y 476–812 하단 `keypad`.
3. **[U1 · 입력 방식]** "물품명 필드와 금액 표시를 한 화면 표시창에 위아래로 함께 두어, 물품명 입력 후 화면 전환·팝업 없이 곧바로 키패드 금액 입력으로 이어지게 한다"
   → `display` 안에 `input/item`(위)과 `input/amount`(아래)를 함께 둠. 물품명 입력 뒤 키보드의 완료/다음을 누르거나 키패드 숫자를 누르면 바로 `input/amount`로 포커스가 이동.
4. **[U1 · 영수증 표현]** "품목명·가격 한 줄 리스트와 하단 고정 합계 바처럼, 오늘의 테이프를 [물품명 · 우측 정렬 금액] 행으로 쌓고 테이프 끝에 오늘 TOTAL을 모노스페이스로 고정 표시한다"
   → `tape/row-n` 한 줄 행 + 금액 우측 정렬, `tape/total`을 테이프 바닥에 고정하고 JetBrains Mono로 표시.
5. **[U2 · 레이아웃]** "건별 카드에 날짜·이름·금액을 묶어 보여주는 방식을 참고해, 테이프 각 행을 [시각 · 물품명 · 금액] 한 줄 단위로 만들고 행을 탭하면 마감 전 수정·삭제가 가능하게 한다"
   → 행 구성 [시각 · 물품명 · 금액]은 정적 시안에 그대로 반영. 탭해서 수정·삭제는 레이어를 추가하지 않고 아래 "인터랙션 메모"로만 기술한다 (N1 레이어 규칙 유지).

## 인터랙션 메모
- **기록(U1)**: `input/item`에 물품명 입력 → 키패드로 금액 입력 → `key/=` → 테이프에 한 줄 추가. 기록 시각은 자동 저장(F1). 사이에 확인 창·선택 단계 없음
- **수정·삭제(U2, F2, 마감 전 기록만)**: `tape/row-n`을 탭하면 그 행의 물품명·금액이 같은 `display`의 `input/item`·`input/amount`에 채워지고, 그 행은 테이프에서 강조(테두리 `primary`)된다. 값을 고쳐 `key/=`를 누르면 그 행이 바뀐다. 이 상태에서 `input/amount`를 `key/C`로 비우고 `key/=`를 누르면 그 행이 삭제된다. 별도 창·시트·선택 목록을 띄우지 않으며 새 `input/*` 레이어도 만들지 않는다
- 수정·삭제는 기록 흐름(물품명 → 금액) 사이에 끼어드는 필수 단계가 아니다. 테이프를 건드리지 않으면 등장하지 않는다
- 이 편집 상태는 정적 시안에 그리지 않는다 (S1 시안은 기본 입력 상태 1장)
- 마감(F3)은 00:00 자동. 이 화면에 수동 출력 버튼을 두지 않는다

## 금지 확인
**N1 — 기록까지 입력 단계 ≤ 2 (S1 적용)**
- 물품명(`input/item`) → 금액(`input/amount`) → `key/=` 로 끝난다. 두 입력이 한 표시창에 함께 있어 사이에 화면 전환 0개
- 팝업·모달·시트·드롭다운·필수 선택 0개. 카테고리·결제수단 등 선택 항목 없음 (PRD Non-goals 준수)
- `must_have_layers`: `input/item`, `input/amount` 둘 다 존재
- `input/*` 패턴 레이어 정확히 2개. 키(`key/*`), 테이프(`tape/*`), 표시창(`display`) 등은 `input/` 아래에 두지 않으며, 입력 내부 텍스트 자식 레이어 이름도 `input/`으로 시작하지 않게 한다
- 레이어 이름 조각(`/`·`-`·`_` 기준)에 `modal`, `popup`, `sheet`, `select`, `dropdown` 0개 (`selected` 같은 파생어도 피한다)
- U2 수정·삭제는 같은 표시창을 재사용하는 인터랙션 메모로만 두고, 이를 위한 별도 레이어를 만들지 않는다

**N2 — 출력된 영수증 변경 불가 (S2·S3 적용)**
- S1은 영수증 화면이 아니므로 판정 대상 아님. 다만 S1 테이프는 마감 전 기록이고, 마감 뒤 출력된 영수증(S2·S3)으로 넘어간 기록은 S1에서 고칠 수 없다 (F2 "마감 전 기록만")

**기타**
- 색은 design.md `colors` HEX만, 모서리는 `rounded` 값만(키는 9999), 간격은 `spacing` 값 또는 0만
- 서체는 Pretendard, JetBrains Mono 2종만
- PRD Non-goals(수입, 카테고리, 예산, 통계·차트, 연동, 로그인, 설정 화면, 다크모드) 요소를 넣지 않는다
