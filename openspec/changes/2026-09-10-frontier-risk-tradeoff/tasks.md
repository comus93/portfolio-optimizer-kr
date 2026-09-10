# Tasks

- [x] 변경 전 기준선 `baseline-20260910-pre-pain-metrics` tag 생성 및 target SHA 검증
- [x] Pain Area / Pain Index / TUW / Maximum Underwater Months formula와 unit contract 정의
- [x] Frontier persisted weights와 monthly return series를 사용하는 prototype analyzer 구현
- [x] 기존 100-point real run에서 prototype 계산 비용 확인
- [x] Pain Ratio와 Schwager-style Monthly Gain-to-Pain 계산 구현 및 synthetic tests
- [x] point별 realized CAGR / Pain Ratio / Monthly Gain-to-Pain을 frontier overlay artifact에 추가
- [x] compact `frontier_interactive.json` artifact 생성 및 JSON safety test
- [x] 정적 `report.html`에 synchronized frontier metric dashboard와 point selection 추가
- [x] selected point weights / drawdown curve browser-side 재생성 로직 및 unit-level contract 검증
- [x] GitHub Actions validation 통과
- [x] 실제 100-point research run으로 JSON size / report size / analyzer elapsed time 확인
- [x] GitHub Pages publish workflow 성공 확인
- [ ] 실제 browser에서 point click / synchronized redraw visual acceptance 확인
- [ ] 기존 Efficient Frontier numerical regression을 baseline tag와 별도 비교 검증
- [x] Sweet spot 자동 판정은 이번 change에 포함하지 않고 실제 curve 검토 이후 별도 결정
