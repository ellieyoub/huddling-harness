# verify — 검증과 리뷰

## 1. gate.py 시험 (fixtures)
실행: `python3 harness/scripts/run_fixtures.py`
`harness/fixtures/`에 가짜 work 폴더를 두고, 게이트마다 통과 1개 + 실패 1개를 돌린다.
12개 + 시나리오 2개가 모두 예상대로 나와야 하네스를 사용한다.

| 게이트 | 실패 fixture | 기대 결과 |
|---|---|---|
| G1 | 레퍼런스 4장 | 실패 → P1 |
| G2 | `## 금지 확인` 제목 없음 | 실패 → P2 |
| G3 | p3-approval.json 없음 / `utterance` 비어 있음 | 실패 → P3 |
| G5 값 | design.md에 없는 `#123456`, 또는 Inter 서체 | 실패 → P4 |
| ★ N1 | S1-final에 `input/popup` 레이어 | 실패 → P3 |
| ★ N2 | S2-final에 "삭제" 텍스트 | 실패 → P3 |

추가 시나리오
- S2 실행에서 N1이 적용되지 않는지 (applies_to)
- P3 복귀 후 이전 승인 파일이 `_archive/`로 옮겨져 G3가 다시 실패하는지

## 2. Figma 연결 시험
1. designer가 `cally-design`에 `TEST` 페이지를 만들고 규칙을 어긴 프레임 1개를 그린다
2. reviewer가 dump → `gate.py G5 <fixture> --page TEST`가 위반을 잡는지 확인
3. 확인 후 designer가 `TEST` 페이지 삭제

## 3. 문서 교차 리뷰
CLAUDE.md 확정 전, 읽기 전용 리뷰 에이전트 1개가 `docs/`·`harness/` 전체를 검사한다.
- 파일명, 게이트 이름, 경로, 단계 번호가 문서마다 같은가
- N1·N2가 최소 1개 게이트에 연결되어 있는가
- 불일치 목록만 보고. 수정은 본인 승인 후

## 4. 운영 개선
화면 1개가 끝날 때마다 오케스트레이터가 `work/log.md`에 1줄:
`날짜 | 화면 | 게이트별 실패 횟수 | 가장 많이 걸린 규칙`
같은 규칙이 3개 화면 연속으로 걸리면 rules.yaml 또는 에이전트 지시 수정을 제안한다.
