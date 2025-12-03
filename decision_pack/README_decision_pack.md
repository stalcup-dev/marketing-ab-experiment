## Experimentation Decision Pack (Integrity + Decision Memo)

This repo includes a lightweight **decision-pack** pipeline that generates three stakeholder-ready artifacts:

- **Integrity report** — SRM diagnostics (50/50 reference + holdout reference), timing distribution checks, and basic data QA  
- **Estimation report** — conversion rates, lift (pp), confidence interval, and significance  
- **1-page decision memo** — an executive-ready recommendation with risks, caveats, and next steps

**Important context:** This dataset’s allocation is consistent with a **treatment-heavy holdout (~96% Ad / ~4% PSA)** rather than a balanced 50/50 experiment. Results are presented as **directional evidence**, and are **potentially causal only if** randomized holdout assignment and stability over time are confirmed.

**Outputs:**
- `decision_pack/reports/integrity_report.md`
- `decision_pack/reports/estimation_report.md`
- `decision_pack/reports/decision_memo_1pager.md`
