# Tasks

- [x] 변경 전 기준선 `baseline-20260910-pre-pain-metrics` tag 생성 및 target SHA 검증
- [x] Pain Area / Pain Index / TUW / Maximum Underwater Months formula와 unit contract 정의
- [x] Frontier persisted weights와 monthly return series를 사용하는 prototype analyzer 구현
- [x] 기존 100-point real run에서 prototype 계산 비용 확인
- [ ] Pain Ratio와 Schwager-style Monthly Gain-to-Pain 계산 구현 및 synthetic tests
- [ ] point별 realized CAGR / Pain Ratio / Monthly Gain-to-Pain을 frontier overlay artifact에 추가
- [ ] compact `frontier_interactive.json` artifact 생성 및 JSON safety test
- [ ] 정적 `report.html`에 synchronized frontier metric dashboard와 point selection 추가
- [ ] selected point weights / drawdown curve browser-side 재생성 검증
- [ ] 기존 Efficient Frontier values가 변경되지 않음을 회귀 검증
- [ ] GitHub Actions validation 통과
- [ ] 실제 100-point research run으로 JSON size / report size / analyzer elapsed time 확인
- [ ] GitHub Pages 게시 후 interactive visual acceptance 확인
- [ ] Sweet spot 자동 판정은 실제 curve 검토 이후 별도 결정
