# Copilot Instructions for AI Coding Agents

## Project Overview
This repository analyzes Ad vs PSA performance using the Kaggle `marketing_AB` dataset. It demonstrates a production-style workflow for experiment integrity, estimation, robustness, and decision reporting. The codebase is organized for reproducible analytics and clear separation of directional vs causal claims.

## Architecture & Key Components
- **decision_pack/**: Core pipeline for integrity audit and estimation. 
  - `src/abpack/`: Python modules for data loading (`io.py`), integrity checks (`checks.py`), reporting (`run.py`, `run_estimation.py`), and statistical analysis.
  - `reports/`: Markdown outputs (integrity, estimation, decision memo).
  - `data/`: Place the Kaggle CSV here locally (not committed).
  - `tests/fixtures/`: Small sample for CI.
- **dbt_marketing_ab/**: dbt project for data modeling (staging → intermediate → marts).
- **notebooks/**: Exploratory analysis, diagnostics, estimation, and recommendations.
- **src/ab_experiment/**: Standalone Python module for data access and stats utilities.
- **visuals/**: Output figures for reports and notebooks.

## Developer Workflows
- **Run integrity and estimation pipeline:**
  ```powershell
  cd decision_pack/src
  python -m abpack.run
  python -m abpack.run_estimation
  ```
  Outputs are written to `decision_pack/reports/`.
- **Notebooks:** Use Jupyter for EDA, diagnostics, and reporting. See `notebooks/` for workflow order.
- **dbt:** Build models in `dbt_marketing_ab/models/` for staged, intermediate, and mart tables.
- **Testing:** Use sample data in `decision_pack/tests/fixtures/` for CI and smoke tests.

## Project-Specific Patterns & Conventions
- **Directional vs Causal:** Integrity checks are required before interpreting lift as causal. Reports and code clearly distinguish between directional evidence and causal claims.
- **SRM & QA:** Always run SRM and timing diagnostics before estimation. See `checks.py` and `integrity_report.md`.
- **Data location:** Large datasets are not committed; use local `decision_pack/data/marketing_ab.csv`.
- **Reporting:** All key findings are written to markdown in `decision_pack/reports/` for stakeholder communication.
- **Reproducibility:** All analysis steps are modularized for rerun and auditability.

## Integration Points
- **Python:** pandas, numpy, scipy for analysis.
- **dbt:** SQL models for data transformation.
- **Jupyter:** Notebooks for interactive analysis and documentation.

## Examples
- To run a full integrity audit and estimation:
  ```powershell
  cd decision_pack/src
  python -m abpack.run
  python -m abpack.run_estimation
  ```
- To view results, check `decision_pack/reports/integrity_report.md` and `decision_pack/reports/estimation_report.md`.
- For EDA and diagnostics, open `notebooks/01_eda_and_integrity_diagnostics.ipynb`.

## References
- See `README.md` for business context, workflow, and roadmap.
- See `decision_pack/docs/experiment_design_spec.md` for experiment design details.

---

If any section is unclear or missing, please provide feedback to improve these instructions for future AI agents.
