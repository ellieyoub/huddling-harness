# artifacts — 산출물

## 단계별 파일
실행 1회 = 화면 1개 = 폴더 1개. 게이트가 읽는 파일은 JSON, 사람이 읽는 파일은 md.

```
work/
├── log.md              화면 완료마다 1줄 (오케스트레이터)
└── {S1|S2|S3}/
    ├── state.json          current_stage, 게이트별 실패 횟수      — 오케스트레이터
    ├── p1-references.json  [{url, app, memo}] ≥ 5개               — researcher
    ├── p1-items.json       [{source_url, story, kind, content}] ≥ 3 — researcher
    ├── p2-spec.md          화면 설계 문서                          — planner
    ├── p3-concept.json     Figma 파일 키, 키스크린 노드 ID          — designer
    ├── p3-approval.json    {approved, date, comment, utterance}    — 오케스트레이터 (사용자 발화 시)
    ├── p4-build.json       토큰·컴포넌트·완성 화면 노드 ID          — designer
    ├── p5-figma-dump.json  S{n}-final 노드 정보 원본 (해석 없음)    — reviewer
    ├── p5-review.json      위반 목록 [{rule, node_id, value}], 복귀 단계 — gate.py
    └── _archive/{시도번호}/  복귀 시 옮겨둔 이전 파일
```

## 규칙 SSOT
- `harness/rules.yaml` 1개
- 게이트 숫자, N1·N2 판정 방식, 서체 예외를 여기에 둔다
- design.md 값(색·모서리·간격)은 복사하지 않고 경로만 참조: `tokens_from: docs/design.md`
- design.md는 수정하지 않는다

## 재개
- 가능. `state.json`의 `current_stage`부터 다시 시작
- 통과한 단계의 파일은 덮어쓰지 않는다. 복귀 시에는 pipeline.md의 "복귀할 때 파일 처리"를 따른다

## Figma 규칙
- 파일 1개: `cally-design`
- 페이지: `P3-concept`, `P4-tokens`, `P4-components`, `P4-screens`, (시험용) `TEST`
- 프레임 이름: `S{n}-concept`, `S{n}-final`. 크기 390×844
- 이름 규칙과 다른 프레임은 게이트 판정 대상이 아니다 (`--page TEST` 시험 제외)

## 레이어 이름 규칙 (N1·N2 판정용)
| 레이어 | 이름 |
|---|---|
| 물품명 입력 | `input/item` |
| 금액 입력 | `input/amount` |
| 계산기 키 | `key/0` … `key/9`, `key/=` 등 (`input/` 아래에 두지 않음) |
| 원형 키 | cornerRadius 9999 (`rounded.full`) |
| 영수증 화면(S2·S3) | `edit`, `delete` 단어가 들어간 레이어 이름 사용 금지 |
