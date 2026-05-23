"""
core/simulator.py
=================
Time-series simulation engine for UDT-DIE.

Applies temporal patterns (daily cycles, seasonality, lag effects) to a base
DataFrame produced by core/generator.py.  All operations are fully vectorised.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional


# ---------------------------------------------------------------------------
# Daily pattern
# ---------------------------------------------------------------------------

def apply_daily_pattern(df: pd.DataFrame, traffic_col: str = "traffic") -> pd.DataFrame:
    """
    """
    df = df.copy()

    # Resolve the hour-of-day from either a column or the index
    if "datetime" in df.columns:
        hours = pd.to_datetime(df["datetime"]).dt.hour.to_numpy()
    elif isinstance(df.index, pd.DatetimeIndex):
        hours = df.index.hour.to_numpy()
    else:
        raise ValueError("DataFrame must have a 'datetime' column or DatetimeIndex.")

    # Dual-peak rush-hour modifier (purely additive sine blend)
    morning = np.exp(-0.5 * ((hours - 8)  / 2.5) ** 2)
    evening = np.exp(-0.5 * ((hours - 18) / 2.5) ** 2)
    modifier = 1.0 + 0.3 * (morning + evening)   # gentle second pass

    df[traffic_col] = (df[traffic_col].to_numpy() * modifier).clip(min=0)
    return df


# ---------------------------------------------------------------------------
# Seasonality
# ---------------------------------------------------------------------------

def apply_seasonality(
    df: pd.DataFrame,
    value_col: str,
    amplitude: float = 0.15,
    date_col: Optional[str] = "date",
) -> pd.DataFrame:
    """
    Scale a time-series column by an annual sinusoidal seasonality factor.


    """
    df = df.copy()

    if date_col and date_col in df.columns:
        dates = pd.to_datetime(df[date_col])
    elif isinstance(df.index, pd.DatetimeIndex):
        dates = df.index
    else:
        raise ValueError("Provide a valid date_col or a DatetimeIndex.")

    day_of_year = dates.day_of_year.to_numpy()
    seasonal_factor = 1.0 + amplitude * np.sin(2 * np.pi * (day_of_year - 80) / 365)

    df[value_col] = (df[value_col].to_numpy() * seasonal_factor).clip(min=0)
    return df


# ---------------------------------------------------------------------------
# Lag features
# ---------------------------------------------------------------------------

def add_lagged_features(
    df: pd.DataFrame,
    col: str,
    lag: int = 24,
    fill_value: float = np.nan,
) -> pd.DataFrame:
    """
    Create a lagged copy of `col` using np.roll, then optionally fill the
    wrap-around positions.

    """
    df = df.copy()
    values = df[col].to_numpy(dtype=float)
    rolled = np.roll(values, shift=lag)

    # Replace the wrap-around tail/head with fill_value
    if lag > 0:
        rolled[:lag] = fill_value
    elif lag < 0:
        rolled[lag:] = fill_value

    df[f"{col}_lag{lag}"] = rolled
    return df


# ---------------------------------------------------------------------------
# Weekly cycle helper
# ---------------------------------------------------------------------------

def apply_weekly_pattern(
    df: pd.DataFrame,
    traffic_col: str = "traffic",
    weekend_factor: float = 0.80,
) -> pd.DataFrame:
    """
    Reduce traffic on weekends by `weekend_factor`.

   
    """
    df = df.copy()

    if "datetime" in df.columns:
        dow = pd.to_datetime(df["datetime"]).dt.dayofweek.to_numpy()
    elif isinstance(df.index, pd.DatetimeIndex):
        dow = df.index.dayofweek.to_numpy()
    else:
        raise ValueError("DataFrame must have a 'datetime' column or DatetimeIndex.")

    is_weekend = (dow >= 5).astype(float)
    factor = 1.0 - (1.0 - weekend_factor) * is_weekend
    df[traffic_col] = (df[traffic_col].to_numpy() * factor).clip(min=0)
    return df
