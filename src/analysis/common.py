"""Shared helpers for Phase 2 financial metric calculations."""

from __future__ import annotations

import logging
from collections.abc import Iterable

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


def prepare_financials(financials: pd.DataFrame, required_columns: Iterable[str], *, module_name: str) -> pd.DataFrame:
    """Return a sorted dataframe with missing required columns added as NaN."""

    prepared = financials.copy()
    for column in required_columns:
        if column not in prepared.columns:
            LOGGER.warning("%s is missing required column '%s'; filling with NaN.", module_name, column)
            prepared[column] = np.nan
    return prepared.sort_values("fiscal_year").reset_index(drop=True)


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide two series while avoiding infinite results."""

    result = numerator.div(denominator)
    return result.replace([np.inf, -np.inf], np.nan)


def average_with_prior(series: pd.Series) -> pd.Series:
    """Average a series with its prior-year value, defaulting to the current value."""

    prior = series.shift(1)
    return (series + prior.fillna(series)) / 2


def cagr(series: pd.Series, fiscal_years: pd.Series, periods: int) -> pd.Series:
    """Compute CAGR only when a matching prior fiscal year exists."""

    prior_values = series.shift(periods)
    prior_years = fiscal_years.shift(periods)
    valid_gap = fiscal_years - prior_years == periods
    positive_values = (series > 0) & (prior_values > 0)
    result = pd.Series(np.nan, index=series.index, dtype=float)
    mask = valid_gap & positive_values
    result.loc[mask] = (series.loc[mask] / prior_values.loc[mask]) ** (1 / periods) - 1
    return result
