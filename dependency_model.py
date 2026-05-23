"""
core/dependency_model.py
========================
Dependency (inter-variable) equations for UDT-DIE.

Models the realistic relationships between urban variables:
  - Traffic  →  Pollution (PM2.5)
  - Temperature + Population  →  Energy consumption
  - Traffic  →  Public transport usage (inverse)

All functions operate on NumPy arrays for maximum vectorisation speed.
"""

from __future__ import annotations

import numpy as np
from typing import Optional


# ---------------------------------------------------------------------------
# Pollution model
# ---------------------------------------------------------------------------

def pollution_model(
    traffic: np.ndarray,
    base: float = 5.0,
    coef: float = 0.06,
    noise_std: float = 1.5,
    seed: Optional[int] = 42,
) -> np.ndarray:
    """
    Compute PM2.5 pollution from traffic volume.

    Formula
    -------
        pollution = base + coef * traffic + noise

    Parameters
    ----------
    traffic : np.ndarray
        Traffic values (vehicles / hour).
    base : float
        Background pollution level (µg/m³).
    coef : float
        Marginal pollution per unit of traffic.
    noise_std : float
        Standard deviation of Gaussian noise.
    seed : int or None
        Random seed.

    Returns
    -------
    np.ndarray
        Pollution values (µg/m³), clipped ≥ 0.

    Edge cases
    ----------
    - Zero traffic → output ≈ base.
    - Negative inputs → treated as 0 before computation.
    """
    rng = np.random.default_rng(seed)
    traffic = np.clip(np.asarray(traffic, dtype=float), 0, None)
    noise = rng.normal(0, noise_std, size=traffic.shape)
    pollution = base + coef * traffic + noise
    return np.clip(pollution, 0, None)


# ---------------------------------------------------------------------------
# Lagged pollution model (traffic from previous period drives current pollution)
# ---------------------------------------------------------------------------

def pollution_with_lag(
    traffic: np.ndarray,
    lag: int = 24,
    base: float = 5.0,
    coef_current: float = 0.06,
    coef_lag: float = 0.03,
    noise_std: float = 1.5,
    seed: Optional[int] = 42,
) -> np.ndarray:
    """
    Pollution depends on current AND lagged traffic (simulates atmospheric delay).

    Formula
    -------
        traffic_lag = np.roll(traffic, lag)   [wrap-around positions set to 0]
        pollution   = base
                    + coef_current * traffic
                    + coef_lag     * traffic_lag
                    + noise

    Returns
    -------
    np.ndarray, clipped ≥ 0.
    """
    rng = np.random.default_rng(seed)
    traffic = np.clip(np.asarray(traffic, dtype=float), 0, None)
    traffic_lag = np.roll(traffic, lag)
    traffic_lag[:lag] = 0.0          # no wrap-around bleed

    noise = rng.normal(0, noise_std, size=traffic.shape)
    pollution = base + coef_current * traffic + coef_lag * traffic_lag + noise
    return np.clip(pollution, 0, None)


# ---------------------------------------------------------------------------
# Energy model
# ---------------------------------------------------------------------------

def energy_model(
    temperature: np.ndarray,
    population: np.ndarray,
    a: float = 0.10,
    b: float = 0.50,
    avg_temp: float = 20.0,
    noise_std: float = 50.0,
    seed: Optional[int] = 42,
) -> np.ndarray:
    """
    Compute energy consumption (MWh) from population and temperature deviation.

    Formula
    -------
        energy = a * population + b * |temperature - avg_temp| * (population / 1000)
               + noise

    Rationale: colder or hotter than average → more heating/cooling demand,
    scaled by population density.

    Parameters
    ----------
    temperature : np.ndarray
        Daily temperature values (°C).
    population : np.ndarray
        Population of zone (scalar or array matching `temperature`).
    a : float
        Base energy per person (MWh per capita).
    b : float
        Temperature-sensitivity coefficient.
    avg_temp : float
        Comfort (baseline) temperature (°C).
    noise_std : float
        Noise standard deviation (MWh).
    seed : int or None
        Random seed.

    Returns
    -------
    np.ndarray
        Energy consumption (MWh), clipped ≥ 0.

    Edge cases
    ----------
    - Extreme temperatures (heat waves, cold snaps) produce higher consumption.
    - population array is broadcast if scalar.
    """
    rng = np.random.default_rng(seed)
    temperature = np.asarray(temperature, dtype=float)
    population  = np.asarray(population,  dtype=float)

    temp_dev = np.abs(temperature - avg_temp)
    energy = a * population + b * temp_dev * (population / 1_000)
    noise  = rng.normal(0, noise_std, size=energy.shape)
    return np.clip(energy + noise, 0, None)


# ---------------------------------------------------------------------------
# Public transport usage model
# ---------------------------------------------------------------------------

def public_transport_model(
    traffic: np.ndarray,
    max_capacity: float = 800.0,
    sensitivity: float = 0.4,
    noise_std: float = 10.0,
    seed: Optional[int] = 42,
) -> np.ndarray:
    """
    Model public transport ridership as inversely related to private traffic.

    Formula
    -------
        transit = max_capacity - sensitivity * traffic + noise
        (clipped to [0, max_capacity])

    When roads are congested, some commuters switch to public transport,
    so the relationship is not purely inverse but tapers off.

    Returns
    -------
    np.ndarray
        Public transport usage (passengers / hour), clipped to [0, max_capacity].
    """
    rng = np.random.default_rng(seed)
    traffic = np.clip(np.asarray(traffic, dtype=float), 0, None)
    noise   = rng.normal(0, noise_std, size=traffic.shape)
    transit = max_capacity - sensitivity * traffic + noise
    return np.clip(transit, 0, max_capacity)


# ---------------------------------------------------------------------------
# Correlation check helper (returns covariance matrix for diagnostics)
# ---------------------------------------------------------------------------

def compute_dependency_covariance(*arrays: np.ndarray) -> np.ndarray:
    """
    Return the covariance matrix for a set of 1-D arrays of equal length.

    Useful for verifying that the modelled variables have the expected
    inter-variable relationships (e.g. traffic and pollution positively correlated).

    Parameters
    ----------
    *arrays : np.ndarray
        Variable-length positional arguments, each a 1-D NumPy array.

    Returns
    -------
    np.ndarray
        Shape (n_vars, n_vars) covariance matrix.
    """
    stacked = np.vstack([np.asarray(a, dtype=float) for a in arrays])
    return np.cov(stacked)
