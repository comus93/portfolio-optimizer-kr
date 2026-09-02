# Verification

이 repository의 agent verification은 `verification/profile.yaml`을 기준으로 최소 단계부터 수행한다.

```text
Test
→ Real Run
→ Result Verification
→ Browser Verification (if applicable)
→ Fix
→ Re-verify
```

## Command entrypoint

Targeted + affected regression:

```bash
python scripts/verify.py
```

OpenSpec strict validation 포함:

```bash
python scripts/verify.py --openspec
```

Full pytest까지 포함:

```bash
python scripts/verify.py --openspec --full
```

`verify.py`는 command-based validation만 수행한다. 실제 market-data를 사용하는 real run과 browser semantic verification은 Agent가 `verification/profile.yaml`의 `real_run` / `browser` 항목에 따라 별도로 수행하고 evidence를 남긴다.

## Rules

- 실패를 통과시키기 위해 requirement, acceptance criterion, finance formula, test를 임의로 약화·삭제·skip하지 않는다.
- 구현 수정 후에는 영향을 받은 단계부터 다시 검증한다.
- shared capability 변경은 영향을 받는 기존 Optimization regression을 포함한다.
- report/viewer 변경은 실제 served browser context에서 semantic/interaction을 확인한다.
- PV pixel parity는 acceptance criterion이 아니다.
- Human visual review는 material layout/interaction change에만 completion gate로 사용한다.
