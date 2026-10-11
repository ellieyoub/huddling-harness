# huddling-harness
Hundding 클럽의 4번째 실험으로 harness를 구축하는 연습을 합니다.

이 저장소는 사람이 손으로 하던 **앱 화면 디자인 작업**을 Claude Code **하네스**(작업 에이전트 + 게이트 + 판정 스크립트)로 옮긴 결과물입니다.
대상 서비스는 빈티지 계산기 모습의 지출 기록 앱 **cally**이고, 하네스는 cally의 Figma 시안 3개(S1~S3)를 만듭니다.

---

## 하네스란

| 구성 | 역할 |
|---|---|
| **작업 에이전트** | 단계별로 실제 일을 한다 (리서치, 설계, Figma 작업, 값 추출) |
| **게이트** | 다음 단계로 넘어가도 되는지 기계가 판정한다. 실패하면 정해진 단계로 되돌아간다 |
| **판정 스크립트** | 게이트의 통과 조건을 숫자로 센다. 합격·불합격은 스크립트만 정한다 |
| **오케스트레이터** | 메인 Claude. 순서 관리, 에이전트 호출, 게이트 실행만 하고 디자인은 직접 하지 않는다 |

"그린 사람"과 "넘겨도 된다고 판단하는 사람"을 분리하는 것이 핵심입니다.

---

## 폴더 구조

```
.
├── CLAUDE.md                 오케스트레이터 지시서 (Claude Code가 자동으로 읽음)
├── .claude/
│   ├── agents/               작업 에이전트 정의 4개
│   │   ├── researcher.md
│   │   ├── planner.md
│   │   ├── designer.md
│   │   └── reviewer.md
│   └── settings.json         docs/ · harness/ · CLAUDE.md · .claude/ 편집 차단
├── docs/                     서비스 기준 — "무엇을 만드나"
│   ├── prd.md                서비스 정의
│   ├── design.md             색·모서리·간격 SSOT (getdesign `cursor`, 수정 금지)
│   ├── story-service.md      유저스토리 U1~U5, 어기면 안 되는 것 N1·N2
│   ├── story-work.md         손으로 하던 작업 흐름 (하네스 설계의 재료)
│   └── reference/            시안 참고 이미지
├── harness/                  하네스 정의 — "어떻게 만드나"
│   ├── goal.md               목적, 입력, 완료 기준
│   ├── pipeline.md           단계, 게이트, 복귀 규칙
│   ├── artifacts.md          파일명, Figma·레이어 이름 규칙
│   ├── rules.yaml            ★ 규칙 SSOT (게이트 숫자, N1·N2 판정 방식, 서체 예외)
│   ├── roles.md              에이전트별 편집 범위, 자연어 트리거
│   ├── verify.md             하네스 시험 방법
│   ├── scripts/
│   │   ├── gate.py           G1·G2·G3·G5 판정
│   │   ├── figma_dump.js     Figma 노드 값 읽기 전용 추출
│   │   └── run_fixtures.py   게이트 시험 실행
│   └── fixtures/             통과·실패 시험 데이터 16개
└── work/                     실행 결과 (화면별 폴더)
```

---

## 설계 과정

하네스는 바로 만들지 않고, 인터뷰 라운드를 거쳐 한 라운드에 파일 1개씩 확정했습니다.

| 라운드 | 정한 것 | 산출물 |
|---|---|---|
| R0 | 준비물 확인 | — |
| R1-A | 서비스 맥락: 유저스토리, 어기면 안 되는 것 | `docs/story-service.md` |
| R1-B | 손으로 하던 작업 흐름: 산출물(명사) / 멈칫(게이트) / 넘김(에이전트 경계) | `docs/story-work.md` |
| R2 | 목적: 매번 달라지는 입력, 사용자, 완료 기준 | `harness/goal.md` |
| R3 | 파이프라인: 단계 분할, 입출력, 되돌아가는 지점 | `harness/pipeline.md` |
| R4 | 산출물: 파일명, 규칙 SSOT, 재개 가능 여부 | `harness/artifacts.md` |
| R5 | 게이트: 기계가 셀 수 있는 통과 조건 | `harness/rules.yaml` |
| R6 | 역할: 편집 범위, 읽기 전용 판정자, 트리거 | `harness/roles.md` |
| R7 | 오케스트레이터 | `CLAUDE.md` |
| R8 | 검증과 리뷰 | `harness/verify.md` |

원칙
- **"어기면 안 되는 것"(N1·N2)은 판정 기준이지, 작업 흐름의 재료가 아니다.** 둘을 섞지 않는다.
- **규칙은 스크립트가 셀 수 있는 형태로 바꾼다.** 예: "깔끔하게" → "모서리는 design.md `rounded` 값만 허용"
- 손으로 하던 흐름에서 **멈칫한 지점은 게이트**, **다른 사람·도구로 넘긴 지점은 에이전트 경계**가 된다.

---

## 파이프라인

```
"S1 시작"
  P1 리서치 ──G1──▶ P2 설계 ──G2──▶ P3 컨셉 ──G3 👤──▶ P4 제작 ──▶ P5 검수 ──G5──▶ 완료
     ▲  │              ▲  │            ▲   │                ▲            │
     └──┘              └──┘            └───┘                └── 값 위반 ──┤
   (키워드 바꿔 재수집)              (반려 시 다시)          P3 ◀── N1·N2 위반 ┘
```

| 단계 | 에이전트 | 출력 (`work/S{n}/`) | 게이트 | 실패 시 |
|---|---|---|---|---|
| P1 리서치 | researcher | `p1-references.json`, `p1-items.json` | G1 | P1 |
| P2 설계 | planner | `p2-spec.md` | G2 | P2 |
| P3 컨셉 | designer | `p3-concept.json` + Figma `S{n}-concept` | G3 👤 | P3 |
| P4 제작 | designer | `p4-build.json` + Figma 토큰·컴포넌트·`S{n}-final` | — | — |
| P5 검수 | reviewer → gate.py | `p5-figma-dump.json` → `p5-review.json` | G5 ★ | 값 위반 P4 / N 위반 P3 |

- 실행 1회 = 화면 1개 (S1 메인 계산기 / S2 하루 마감 영수증 / S3 영수증 아카이브)
- 같은 게이트에서 **3번 실패하면 멈추고** 사용자에게 묻는다
- 되돌아갈 때는 그 단계와 이후 파일을 `work/S{n}/_archive/{시도번호}/`로 옮긴다. P3로 돌아가면 **승인도 다시** 받아야 한다
- `state.json`의 `current_stage`부터 **이어서 실행**할 수 있다

---

## 게이트

모든 숫자는 `harness/rules.yaml` 한 곳에서 관리합니다.

| 게이트 | 통과 조건 |
|---|---|
| **G1** 리서치 | 레퍼런스 5개 이상(모두 uibowl URL), 반영 항목 3개 이상. 항목마다 출처 URL · 유저스토리(U1~U5) · 종류 · 내용이 모두 있음 |
| **G2** 설계 | `p2-spec.md`에 `## 대상 유저스토리` `## 구성 요소` `## 반영 항목` `## 금지 확인` 제목이 모두 있음 |
| **G3** 승인 👤 | 사용자가 "승인"이라고 말했고, 그 발화 원문이 `utterance`에 기록됨. **사람이 판단하는 유일한 지점** |
| **G5** 검수 | `S{n}-final` 안의 모든 노드가 아래 규칙을 지킴. 위반 0건 |

**G5 디자인 값 규칙**
- 색: design.md `colors` 값만 (그라데이션 금지)
- 모서리: design.md `rounded` 값만
- auto-layout 간격·패딩: design.md `spacing` 값 또는 0
- 서체: Pretendard(기본), JetBrains Mono(숫자·영수증)만 — design.md 서체에 한글이 없어 예외로 고정
- 프레임 크기 390×844

**★ 어기면 안 되는 것 (서비스 규칙을 게이트로 옮긴 것)**

| 규칙 | 서비스 의미 | 적용 화면 | 기계가 세는 방법 |
|---|---|---|---|
| **N1** | 기록까지 입력 단계 ≤ 2 | S1 | `input/item`, `input/amount`가 한 프레임에 있음 · `input/*` 2개 이하 · modal·popup·sheet·select·dropdown 이름 0개 |
| **N2** | 출력된 영수증은 변경 불가 | S2, S3 | `edit`·`delete` 이름 0개 · "수정·삭제·편집" 텍스트 0개 |

정적 시안에서는 "단계"나 "수정 버튼"을 기계가 알아볼 수 없어서, **레이어 이름 규칙**으로 셉니다. 자세한 이름 규칙은 `harness/artifacts.md`에 있습니다.

**범위 검사**: 게이트마다 `state.json`의 단계 시작 시각 이후에 바뀐 파일이 그 단계 에이전트의 범위 안인지 사후 검사합니다. 범위 밖 파일이 바뀌었으면 그 게이트는 실패합니다.

---

## 역할과 권한

| 누가 | 하는 일 | 쓸 수 있는 것 | Figma |
|---|---|---|---|
| 오케스트레이터 | 지휘, 게이트 실행, 상태 기록 | `state.json`, `p3-approval.json`(사용자 발화 시만), `_archive/`, `work/log.md` | ❌ |
| researcher | uibowl에서 레퍼런스 수집·분석 | `p1-*` | ❌ |
| planner | 화면 설계 문서 | `p2-*` | ❌ |
| designer | 키스크린, 토큰·컴포넌트·완성 화면 | `p3-concept.json`, `p4-*` | 쓰기 |
| reviewer | `figma_dump.js`로 값 추출만 | `p5-figma-dump.json` | 읽기 |
| gate.py | 판정 | `p5-review.json` | ❌ |
| 사용자 | 컨셉 승인·반려, 규칙 수정 | `docs/`, `harness/` | — |

권한은 두 겹으로 막습니다.
1. `.claude/settings.json`: `docs/`, `harness/`, `CLAUDE.md`, `.claude/` 편집 차단
2. `gate.py`의 범위 검사: 에이전트별 파일 범위를 사후 검사

reviewer는 Figma 값을 **해석하지 않고 그대로 저장**하고, 합격·불합격은 `gate.py`만 정합니다.

---

## 사용법

### 준비
- Claude Code
- Figma MCP, uibowl MCP 연결
- Python 3 (외부 패키지 없이 동작)

### 1. 하네스 시험
```bash
python3 harness/scripts/run_fixtures.py
```
16개가 모두 ✅여야 사용합니다. 게이트별 통과·실패 사례와 시나리오(S3에서 N1 미적용, P3 복귀 후 재승인, 범위 위반, Figma TEST 페이지)를 포함합니다.

### 2. Figma 연결 시험 (`harness/verify.md` §2)
designer가 `TEST` 페이지에 규칙 위반 프레임을 그리고 → reviewer가 추출하고 → `gate.py G5 <폴더> --page TEST`가 위반을 잡는지 확인한 뒤 → TEST 페이지를 지웁니다.

### 3. 실행 (Claude Code에서 말하기)

| 말 | 동작 |
|---|---|
| `S1 시작` (+ 키워드) | `work/S1/` 생성, P1부터 진행 |
| `S1 이어서` | 멈춘 단계부터 다시 진행 |
| `S1 승인` / `S1 반려: 코멘트` | G3 기록 → P4 또는 P3 |
| `S1 검수` | P5만 다시 실행 |
| `S1 상태` | 현재 단계, 게이트별 실패 횟수 |

키워드를 생략하면 S1 "계산기", S2 "영수증", S3 "아카이브"를 씁니다.

### 게이트 직접 실행
```bash
python3 harness/scripts/gate.py <G1|G2|G3|G5> work/S{n}
```
결과는 JSON으로 출력되고, 통과하면 exit 0, 실패하면 exit 1입니다.

---

## 규칙을 바꾸려면

| 바꾸고 싶은 것 | 고칠 파일 |
|---|---|
| 게이트 숫자 (레퍼런스 개수, 반복 제한 등), N1·N2 판정, 허용 서체 | `harness/rules.yaml` |
| 색·모서리·간격 값 | `docs/design.md` (현재는 수정하지 않는 원칙) |
| 에이전트 행동 | `.claude/agents/*.md` |
| 오케스트레이터 규칙 | `CLAUDE.md` |

모두 에이전트 편집이 차단된 파일이라 사용자가 직접 수정합니다. 수정한 뒤에는 `run_fixtures.py`를 다시 돌립니다.
화면이 끝날 때마다 `work/log.md`에 게이트별 실패 횟수가 쌓입니다. 같은 규칙이 3개 화면 연속으로 걸리면 규칙이나 에이전트 지시를 고칠 때입니다.

---

## 알려진 한계

- **정적 시안만 판정합니다.** N1의 "화면 전환"처럼 흐름에 관한 규칙은 레이어 이름으로 근사합니다.
- **게이트가 보지 않는 PRD 항목이 있습니다.** 영수증 필수 항목, ₩ 표기, 금액 정렬 등은 G2 설계 문서와 G3 사람 승인에서 확인합니다.
- **편집 차단은 Edit/Write 도구에만 걸립니다.** Bash로 쓰는 것은 범위 검사가 사후에 잡습니다.
- **하위 에이전트의 승인 파일 작성은 권한으로 완전히 막지 못합니다.** 대신 `utterance`(사용자 발화 원문)가 필수입니다.
- **reviewer가 Figma 응답을 파일로 옮기는 과정이 수작업일 수 있습니다.** 옮기는 중에 값이 틀어질 위험이 있습니다.
