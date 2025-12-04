# Metric Framework: Ad vs PSA Experiment (Stakeholder-Ready)

## Goal (1 sentence)
Decide whether showing a **product Ad** instead of a **PSA** increases conversions without harming user experience or business constraints.

---

## Primary metric (the one the experiment is powered for)
**Conversion Rate (CR)**  
> % of eligible users who convert within the measurement window.

**Definition**
- Numerator: number of users with `converted = 1`
- Denominator: number of eligible users exposed/assigned in the experiment

**Why it’s primary**
- Directly matches the business question (“maximize purchases/conversions”)
- Interpretable in absolute lift (pp) and incremental conversions per 1M exposures

**Decision quantity**
- Absolute lift (pp): CR_treatment − CR_control
- Always report uncertainty (CI) alongside lift

---

## Secondary metrics (useful context; not the ship gate by themselves)
Pick 2–5 that matter for your org. Examples:
- Click-through rate (CTR) on the ad unit
- Add-to-cart rate
- Revenue per user (RPU) / average order value (AOV)
- Down-funnel conversion (e.g., purchase completion)
- Return rate / cancellations (if relevant)

**Why they matter**
They help you understand *mechanism* (did we drive better traffic or just different traffic?) and *business quality* (did we increase junk conversions?).

---

## Guardrails (must NOT get worse)
Guardrails protect the product and trust. Examples:
- Page performance: latency / error rate (ads can slow pages)
- Bounce rate / session depth (ads can annoy users)
- Spam/complaints/unsubscribes (for email-like surfaces)
- Customer support contact rate
- Ad policy / compliance constraints
- Cost guardrail: incremental cost per incremental conversion (if paid media inventory)

**Guardrail policy (simple)**
- If any guardrail regression is “material,” the result is **no-ship** even if CR improves.

---

## Segmentation plan (what slices we monitor)
Segmentation is for **diagnosis and risk**, not fishing for significance.

Recommended slices:
- **Time**: day-of-week, hour-of-day (captures seasonality / batch effects)
- **User type**: new vs returning
- **Device**: mobile vs desktop (ads can behave differently)
- **Geo**: country/region (where applicable)
- **Traffic source**: organic / paid / referrals (major confounder if imbalanced)
- **Exposure intensity**: users with high vs low ad exposure (if applicable)

What to look for:
- Lift stability: does the lift stay roughly consistent, or does it only “work” in one slice?
- SRM / allocation drift by slice: is the experiment truly randomized within slices?

---

## Common failure modes (what breaks trust in results)
### Design / allocation failures
- **SRM / split mismatch**: actual traffic split differs from intended due to bugs or targeting rules
- **Sample pollution**: users see both variants (non-persistent assignment)
- **Interference**: users influence each other (sharing links, network effects)

### Measurement failures
- Logging bugs (missing conversion events in one variant)
- Bot traffic or invalid users unevenly distributed
- Delayed conversions not captured consistently

### Confounding (especially in marketing)
- Different traffic sources in different variants
- Campaign timing and holiday effects
- Creative fatigue / novelty effects

---

## Ship / no-ship decision policy (clear and enforceable)

### Ship
Ship the Ad if:
1. Primary metric improves: lift > 0
2. Evidence is strong at the planned horizon: CI excludes 0 in the positive direction (or p < alpha)
3. Guardrails pass (no material regressions)
4. Lift is reasonably stable across key segments (no major red flags)

### No-ship
No-ship if:
- Lift is negative or indistinguishable from 0 at the horizon
- Guardrails regress materially
- SRM / instrumentation issues invalidate the comparison

### “Investigate” (don’t ship, don’t discard)
Investigate if:
- Overall lift is positive but concentrated in one segment with clear confounding risk
- Allocation drift or logging issues are suspected
- The test ended early or was repeatedly peeked (invalidates fixed-horizon inference)

---

## Reporting standard (what we publish in the decision memo)
Minimum:
- CR_control, CR_treatment, lift(pp), CI
- Total N and runtime window
- SRM result + top QA checks
- Guardrail deltas
- 2–3 key segment reads (time/device/source)
- A plain-English ship/no-ship recommendation
