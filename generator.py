"""
core/generator.py
=================
Synthetic data generation for the Urban Digital Twin & Decision Intelligence Engine.

Generates realistic city data: population per zone, hourly traffic, and daily weather.
Uses only NumPy and Pandas. All functions accept a `seed` for reproducibility.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Optional


# ---------------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------------

def generate_population(
    zones: List[str],
    mean: float = 50_000,
    std: float = 10_000,
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """
    Generate a population estimate for each urban zone.

    Parameters
    ----------
    zones : list[str]
        Zone identifiers (e.g. ['North', 'South', 'East']).
    mean : float
        Mean population per zone.
    std : float
        Standard deviation of population across zones.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Columns: ['zone', 'population']

    Edge cases
    ----------
    - Empty zones list  → returns empty DataFrame with correct columns.
    - Negative samples  → clipped to 0.
    """
    if not zones:
        return pd.DataFrame(columns=["zone", "population"])

    rng = np.random.default_rng(seed)
    populations = rng.normal(loc=mean, scale=std, size=len(zones))
    populations = np.clip(populations, 0, None).astype(int)

    return pd.DataFrame({"zone": zones, "population": populations})


# ---------------------------------------------------------------------------
# Traffic
# ---------------------------------------------------------------------------

def generate_traffic(
    zones: List[str],
    days: int = 30,
    base_volume: float = 500.0,
    noise_std: float = 20.0,
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """
    Simulate hourly traffic for each zone over `days` days.

    Pattern applied (fully vectorised, no Python loops):
      - Daily cycle  : sinusoidal 24-hour curve (rush-hour peaks at 08:00 & 18:00)
      - Weekly cycle : 20 % reduction on weekends
      - Gaussian noise

    Parameters
    ----------
    zones : list[str]
        Zone identifiers.
    days : int
        Number of days to simulate.
    base_volume : float
        Baseline vehicles per hour per zone.
    noise_std : float
        Standard deviation of Gaussian noise added to traffic.
    seed : int or None
        Random seed.

    Returns
    -------
    pd.DataFrame
        Columns: ['datetime', 'zone', 'traffic']
        'datetime' is an hourly DatetimeIndex repeated for each zone.

    Edge cases
    ----------
    - days == 0 → returns empty DataFrame with correct columns.
    - Negative traffic values are clipped to 0.
    """
    if days == 0 or not zones:
        return pd.DataFrame(columns=["datetime", "zone", "traffic"])

    rng = np.random.default_rng(seed)
    n_hours = days * 24

    # Build hourly time index
    dt_index = pd.date_range(start="2024-01-01", periods=n_hours, freq="h")

    # --- Vectorised pattern construction ---
    hours_of_day = dt_index.hour.to_numpy()           # shape (n_hours,)
    day_of_week  = dt_index.dayofweek.to_numpy()      # 0=Mon … 6=Sun

    # Dual-peak daily pattern: morning (08:00) and evening (18:00) rush hours
    morning_peak = np.exp(-0.5 * ((hours_of_day - 8)  / 2.5) ** 2)
    evening_peak = np.exp(-0.5 * ((hours_of_day - 18) / 2.5) ** 2)
    daily_pattern = 1.0 + 0.8 * (morning_peak + evening_peak)   # shape (n_hours,)

    # Weekend reduction (Sat=5, Sun=6)
    is_weekend = (day_of_week >= 5).astype(float)
    weekly_pattern = 1.0 - 0.20 * is_weekend                    # shape (n_hours,)

    # Combined base signal, broadcast across zones
    # base shape: (n_hours,) → repeat for each zone
    base_signal = base_volume * daily_pattern * weekly_pattern   # (n_hours,)

    # Stack zones: shape (n_zones, n_hours)
    n_zones = len(zones)
    traffic_matrix = np.tile(base_signal, (n_zones, 1))

    # Add per-zone Gaussian noise
    noise = rng.normal(loc=0, scale=noise_std, size=traffic_matrix.shape)
    traffic_matrix += noise
    traffic_matrix = np.clip(traffic_matrix, 0, None)

    # Flatten into long-format DataFrame
    zone_col = np.repeat(zones, n_hours)
    dt_col   = np.tile(dt_index, n_zones)
    traffic_col = traffic_matrix.ravel()

    df = pd.DataFrame({"datetime": dt_col, "zone": zone_col, "traffic": traffic_col})
    df["zone"] = df["zone"].astype("category")
    return df


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------

def generate_weather(
    days: int = 365,
    base_temp: float = 25.0,
    temp_amplitude: float = 10.0,
    base_humidity: float = 60.0,
    seed: Optional[int] = 42,
) -> pd.DataFrame:
    """
    Generate daily temperature (°C) and humidity (%) for one year.

    Uses a sinusoidal annual cycle plus Gaussian noise.

    Parameters
    ----------
    days : int
        Number of days to generate.
    base_temp : float
        Mean annual temperature (°C).
    temp_amplitude : float
        Seasonal swing (°C) above/below the mean.
    base_humidity : float
        Mean annual humidity (%).
    seed : int or None
        Random seed.

    Returns
    -------
    pd.DataFrame
        Columns: ['date', 'temperature', 'humidity']

    Edge cases
    ----------
    - days == 0 → returns empty DataFrame with correct columns.
    - Humidity is clipped to [0, 100].
    """
    if days == 0:
        return pd.DataFrame(columns=["date", "temperature", "humidity"])

    rng = np.random.default_rng(seed)
    day_idx = np.arange(days)
    date_index = pd.date_range(start="2024-01-01", periods=days, freq="D")

    # Annual sinusoidal cycle (peak in mid-summer ~day 172)
    seasonal_cycle = np.sin(2 * np.pi * (day_idx - 80) / 365)

    temperature = (
        base_temp
        + temp_amplitude * seasonal_cycle
        + rng.normal(0, 1.5, size=days)
    )

    # Humidity is inversely correlated with temperature (hot days → drier)
    humidity = (
        base_humidity
        - 0.4 * temp_amplitude * seasonal_cycle
        + rng.normal(0, 3.0, size=days)
    )
    humidity = np.clip(humidity, 0, 100)

    return pd.DataFrame({
        "date":        date_index,
        "temperature": np.round(temperature, 2),
        "humidity":    np.round(humidity, 2),
    })
