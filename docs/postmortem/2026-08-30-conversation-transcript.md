# Portfolio Optimizer KR: 대화 작업 기록

작성일: 2026-08-30

## 기록 범위

이 문서는 이 작업방에서 사용자에게 보인 요청과 그에 따른 작업 결과를 시간순으로 보존한 공개용 대화 기록이다. 시스템/개발자 지시, 비공개 내부 추론, 인증 정보, 도구의 내부 상세 출력은 포함하지 않는다. 원문 대화 내보내기 기능이 저장소에 없으므로, 접근 가능한 사용자 대화와 작업 상태를 기반으로 재구성하였다.

## 대화 및 작업 경과

1. 사용자는 다음 AI Share 문서를 읽고 대화를 이어가도록 요청했다.

   - `ai-share/agent-to-agent.md`
   - `ai-share/llm-to-llm.md`

2. 사용자는 `docs/specification.md`와 AI Share의 LLM-to-Agent 문서를 확인하고, LLM이 만든 뼈대 코드를 바탕으로 후속 개발 및 필요한 작업을 수행하도록 요청했다.

3. 사용자는 GitHub의 최신 내용을 내려받아 전체 저장소를 현실화한 뒤 LLM-to-Agent 내용을 확인하도록 요청했다. 이어서 LLM-to-Codex 요청 사항을 확인하고 실행하도록 요청했다.

4. 소스 충돌 여부에 대한 질문 뒤, 사용자는 동기화 기준을 다음과 같이 지정했다.

   ```text
   GitHub main
     + 최신 research/interactions layer
     + parity contract test

   로컬에서 보존
     + run_pv_target_vol_parity.py 보강 구현
     + 재생성된 parity.json
     + 재생성된 moment_parity.csv
     + 재생성된 solver_parity.csv
   ```

5. 사용자는 전체 소스 동기화 완료 여부를 확인했고, 커밋/푸시 및 이후 LLM 요건 확인 시 로컬이 아니라 GitHub의 해당 문서를 먼저 pull하여 확인하라는 규칙을 요구했다. 이 규칙은 `ai-share/PROTOCOL.md`에 반영되어 GitHub 기준 inbound 동기화 절차로 관리된다.

6. 사용자는 반복적으로 LLM-to-Agent 요청을 확인·실행하고, LLM이 전달한 변경 사항을 반영하도록 요청했다.

7. 사용자는 다음 Portfolio Visualizer 페이지를 외부 비교 기준(golden source)으로 제시하고, 로컬 보고서와 실제 페이지를 비교해 차이와 개선 사항을 찾도록 요청했다.

   - PV: <https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg>
   - 로컬 보고서(당시): `runs/20260829-0001/report.html`

   사용자가 먼저 발견한 차이는 소수점 표기이며, 소수점 이하 2자리 반올림이 필요하다고 명시했다.

8. 사용자는 실제 PV 페이지 접속 가능 여부를 확인한 뒤, 실제 PV 페이지와 `report.html`을 비교하여 차이점 및 개선 사항을 `ai-share/agent-to-llm.md`에 보고하도록 요청했다.

9. 사용자는 특히 다음 UI 문제도 보고되었는지 확인했다.

   - 차트 눈금 표기 차이
   - Active Return Contribution 그래프가 톱니바퀴처럼 보이는 문제

   또한 검증 중 생성한 HTML/CSV 원본을 GitHub에 올리고, 로컬/원격 경로를 사용자 및 LLM에 전달하도록 요청했다.

10. 사용자는 LLM 명령을 수행하고 결과 HTML을 GitHub에 업로드한 뒤 파일명과 위치를 알려 달라고 요청했다. 이어서 해당 HTML의 GitHub 위치를 `agent-to-llm.md`에도 추가하도록 요청했다.

11. LLM 요청 사항을 확인·실행한 뒤, 사용자 질문에 따라 작업 완료 및 HTML 업로드 여부를 점검했다. 이후 현재까지의 완료 내용과 검증 내용을 LLM에 보고하고, 실행 결과 HTML을 업로드해 경로까지 보고하도록 요청받았다.

12. 최신 LLM 요청(`20260829T093500+0900-llm`)에 대한 P0 수정/검증 작업이 진행되었다. 요청의 핵심은 다음과 같았다.

   - Efficient frontier 선은 실제 frontier 점만 연결하고 landmark는 marker로만 표시
   - Ex-ante landmark 좌표의 출처를 historical performance가 아니라 투자 가정 기반으로 교정
   - Up/Down capture를 실제 월별 산점도와 통계로 제시하고 단순 막대그래프를 대체
   - Up/Down 수익률, contribution, rolling active return의 단위/tooltip/결측값 표현을 교정
   - Transition map hover를 행 인덱스가 아니라 실제 가장 가까운 변동성 값 기준으로 교정
   - Growth of $10k 표시를 올바른 기준값으로 정규화
   - 관련 테스트, 브라우저 검증, 새 실행 산출물 및 시각 비교 기록을 제공

13. 현재까지 완료된 일부 P0 결과는 다음과 같다.

   - Frontier 곡선 데이터에서 landmark를 제외하도록 `site/report-template.html`의 렌더링을 보강했다.
   - 관련 contract 테스트 11개와 전체 테스트 87개가 통과했다.
   - 부분 검증 실행 결과를 `runs/20260829-0002/`에 저장하고 GitHub에 올렸다.
   - 보고서 URL: <https://github.com/comus93/portfolio-optimizer-kr/blob/main/runs/20260829-0002/report.html>
   - 이 결과는 전체 P0 종료가 아니라 부분 검증임을 `ai-share/agent-to-llm.md`에 명시했다.

14. 남아 있는 P0 항목은 ex-ante landmark 좌표, 실제 월별 Up/Down 산점도와 단위, contribution/rolling tooltip과 결측값 처리, transition hover, Growth 표시 등이다. 따라서 현재 상태를 전체 P0 완료로 선언하지 않았다.

15. 현재 사용자 요청: 이 작업방의 대화 내용을 GitHub 저장소의 `docs/postmortem/` 아래 텍스트 파일로 만들고 push한다.

## 관련 저장소 산출물

- 부분 P0 실행: `runs/20260829-0002/`
- 초기/비교 실행 이력: `runs/20260829-0001/`, `runs/20260829-0004/`
- LLM 전달 결과: `ai-share/agent-to-llm.md`
- LLM 요청: `ai-share/llm-to-agent.md`
- 협업 규약: `ai-share/PROTOCOL.md`

## 주의 사항

- Portfolio Visualizer는 외부 참고/조사 기준이며, 프로젝트의 규범적 계산 및 UI 의미는 `docs/specification.md`와 `docs/report-ui-specification.md`가 우선한다.
- AI Share 파일은 최신 메시지 하나만 유지하며, 전체 대화 보관 용도가 아니다. 이 문서가 별도의 postmortem 보관 위치다.
- 실행 중 새로 생성된 미추적 validation 산출물은 이 문서 커밋에 포함하지 않는다.
