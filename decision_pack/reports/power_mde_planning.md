# Power + MDE Planning
This planning note sizes a 2-arm conversion experiment using a normal-approx two-proportion z-test.
## Inputs
- Baseline conversion rate: **1.79%**
- Desired lift (absolute): **0.77 pp**
- Alpha: **0.050** (two-sided)
- Power: **0.80**
- Traffic split (treatment share): **0.50**
- Daily eligible traffic: **10,000 users/day**

## Assumptions (explicit)
- Binary outcome per user (converted = 0/1), independent users.
- Stable baseline rate during the test window.
- Fixed-horizon analysis (no repeated peeking); otherwise alpha inflates.
- Z-test normal approximation is acceptable given expected counts.

## Output: required sample size
- Control N: **5,633**
- Treatment N: **5,633**
- Total N: **11,266**

## Estimated runtime (given daily traffic)
- Estimated runtime: **1.13 days** (~27.0 hours)

## Sanity check: implied MDE at this N
- With these sample sizes, the MDE is **0.77 pp** (should be ~equal to the target lift, up to rounding/approximation).

## Example run
```bash
cd decision_pack/src
python -m abpack.run_power \
  --baseline 0.0179 \
  --lift-pp 0.77 \
  --alpha 0.05 \
  --power 0.80 \
  --daily-traffic 10000 \
  --treat-share 0.50
```
