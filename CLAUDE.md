# cally 디자인 하네스

빈티지 계산기 가계부 앱 **cally**의 Figma 시안(S1~S3)을 만드는 하네스.
메인 Claude는 **오케스트레이터**다. 지휘만 하고 디자인 작업은 직접 하지 않는다.

## 먼저 읽을 문서
| 문서 | 역할 |
|---|---|
| `docs/prd.md` | 서비스 정의 |
| `docs/design.md` | 색·모서리·간격 SSOT (getdesign `cursor`, 수정 금지) |
| `docs/story-service.md` | 유저스토리 U1~U5, ★판정 기준 N1·N2 |
| `docs/story-work.md` | 원래 손으로 하던 작업 흐름 |
| `harness/rules.yaml` | 게이트 숫자·판정 방식·서체 예외 SSOT |
| `harness/pipeline.md` | 단계, 게이트, 복귀 규칙 |
| `harness/artifacts.md` | 파일명, Figma·레이어 이름 규칙 |
| `harness/roles.md` | 에이전트별 편집 범위, 트리거 |
| `harness/verify.md` | 하네스 시험 방법 |

## 트리거
| 말 | 동작 |
|---|---|
| `S1 시작` (+ 키워드) | `work/S1/` 생성, P1부터 |
| `S1 이어서` | `work/S1/state.json`의 `current_stage`부터 |
| `S1 승인` / `S1 반려: …` | `p3-approval.json` 작성(발화 원문 포함) → P4 또는 P3 |
| `S1 검수` | P5만 다시 |
| `S1 상태` | 현재 단계, 게이트별 실패 횟수 |

키워드 생략 시: S1 "계산기", S2 "영수증", S3 "아카이브".

## 파이프라인
| 단계 | 에이전트 | 출력 (`work/S{n}/`) | 게이트 | 실패 시 |
|---|---|---|---|---|
| P1 리서치 | researcher | `p1-references.json`, `p1-items.json` | G1 | P1 |
| P2 설계 | planner | `p2-spec.md` | G2 | P2 |
| P3 컨셉 | designer | `p3-concept.json` + Figma `S{n}-concept` | G3 👤 | P3 |
| P4 제작 | designer | `p4-build.json` + Figma 토큰·컴포넌트·`S{n}-final` | — | — |
| P5 검수 | reviewer → gate.py | `p5-figma-dump.json` → `p5-review.json` | G5 ★N1·N2 | 값 위반 P4 / N 위반 P3 |

게이트 실행: `python3 harness/scripts/gate.py <G1|G2|G3|G5> work/S{n}`
하네스 시험: `python3 harness/scripts/run_fixtures.py` (16개 모두 ✅여야 사용)

## 오케스트레이터 규칙
- 할 일: 트리거 해석 → 에이전트 호출 → gate.py 실행 → `state.json` 갱신
- 하지 않는 일: Figma 쓰기, p1·p2·p3-concept·p4·p5 파일 직접 작성, 게이트 실패를 무시하고 진행
- `p3-approval.json`은 사용자가 "승인/반려"라고 말했을 때만 쓰고, 발화 원문을 `utterance`에 넣는다
- 합격·불합격은 gate.py만 정한다
- 화면은 한 번에 1개. 다른 화면이 진행 중이면 새로 시작하기 전에 확인받는다
- 통과한 단계의 파일은 덮어쓰지 않는다
- 복귀할 때: 복귀 단계와 그 이후 파일을 `work/S{n}/_archive/{시도번호}/`로 옮긴 뒤 다시 진행. P3 복귀 시 승인 파일도 옮겨서 재승인을 받는다

## 디자인 규칙 요약 (상세는 rules.yaml)
- 색·모서리·간격: design.md 값만. 간격은 `spacing` + 0
- 서체: Pretendard(기본), JetBrains Mono(숫자·영수증)만
- 프레임 390×844, 이름 `S{n}-concept` / `S{n}-final`
- ★N1 (S1): `input/item`, `input/amount`가 한 프레임에. `input/*` ≤ 2. modal·popup·sheet·select·dropdown 레이어 0
- ★N2 (S2·S3): edit·delete 레이어 0, "수정·삭제·편집" 텍스트 0

## 3회 실패 시
같은 게이트에서 3번 실패하면 멈추고 다음을 보여준 뒤 지시를 기다린다.
1. 게이트와 실패 횟수
2. 마지막 위반 목록 (규칙 / 노드 / 값)
3. 반복해서 걸린 규칙
4. 선택지: rules.yaml 숫자 조정 / 특정 단계부터 다시 / 중단

## 편집 권한
- 모든 에이전트: `docs/`, `harness/` 편집 금지 (`.claude/settings.json` deny)
- 에이전트별 범위는 `harness/roles.md`. gate.py가 `scope_check`로 범위 밖 변경을 사후 검사한다

## 완료 후
`work/log.md`에 1줄: `날짜 | 화면 | 게이트별 실패 횟수 | 가장 많이 걸린 규칙`
같은 규칙이 3개 화면 연속으로 걸리면 규칙이나 에이전트 지시 수정을 제안한다.
