# roles — 역할

## 에이전트와 편집 범위
| 누가 | 단계 | 편집 가능 | Figma |
|---|---|---|---|
| 오케스트레이터 (메인 Claude) | 전체 | `work/*/state.json`, `work/*/p3-approval.json`(사용자 발화 시), `work/*/_archive/`, `work/log.md` | ❌ |
| researcher | P1 | `work/*/p1-*` | ❌ (uibowl만) |
| planner | P2 | `work/*/p2-*` | ❌ |
| designer | P3, P4, 시험 | `work/*/p3-concept.json`, `work/*/p4-*` | 쓰기 (`TEST` 페이지 포함) |
| reviewer | P5 | `work/*/p5-figma-dump.json` | 읽기만 |
| gate.py | 모든 게이트 | `work/*/p5-review.json` | ❌ |

공통 금지: `docs/`, `harness/` 편집 불가 (본인만 수정).
권한은 두 겹으로 막는다.
1. `.claude/settings.json` deny: `docs/**`, `harness/**` 쓰기
2. gate.py가 `rules.yaml`의 `scope_check`로 단계마다 범위 밖 파일 변경을 사후 검사 → 있으면 그 게이트 실패

## 판정자 (읽기 전용)
1. reviewer가 `harness/scripts/figma_dump.js`(읽기 전용 고정 스크립트)를 use_figma로 실행해 `S{n}-final` 노드 정보를 `p5-figma-dump.json`에 그대로 저장
2. `harness/scripts/gate.py`가 dump + `harness/rules.yaml` + `docs/design.md`를 비교해 `p5-review.json` 작성
3. 합격·불합격은 스크립트만 정한다. reviewer는 결과를 바꿀 수 없다
- G1·G2·G3·G5 모두 gate.py로 판정

## 사람 승인 (G3)
- 본인이 "S1 승인" / "S1 반려: 코멘트"라고 말하면 오케스트레이터가 `p3-approval.json`을 쓴다
- 발화 원문을 `utterance` 필드에 그대로 기록한다. 비어 있으면 G3 실패
- 하위 에이전트는 이 파일을 쓸 수 없다

## 자연어 트리거
| 말 | 동작 |
|---|---|
| `S1 시작` (+ 키워드 선택) | `work/S1/` 생성, P1부터 진행 |
| `S1 이어서` | `state.json`의 `current_stage`부터 진행 |
| `S1 승인` / `S1 반려: …` | G3 기록 → P4 또는 P3 |
| `S1 검수` | P5만 다시 실행 |
| `S1 상태` | 현재 단계, 게이트별 실패 횟수 표시 |
