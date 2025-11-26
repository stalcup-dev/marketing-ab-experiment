"""
Utility functions for the marketing Ad vs PSA experiment.

Exposes:
- get_experiment_df (data_access)
- core statistical helpers (stats)
- plotting helpers (viz)
"""

from .data_access import get_experiment_df
from . import stats  # so you can do ab_experiment.stats.compute_conversion_lift

