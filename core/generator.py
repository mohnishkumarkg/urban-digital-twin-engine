# Synthetic data generation for the Urban Digital Twin & Decision Intelligence Engine.

# Generates realistic city data:
# - Population per zone
# - Hourly traffic
# - Daily weather

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Optional


# ---------------------------------------------------------------------------
# POPULATION GENERATION
# ---------------------------------------------------------------------------

def generate_population(
    Zones: List[str],
    mean: float = 50_000,
    std: float = 10_000,
    seed: Optional[int] = 42,
) -> pd.DataFrame:

    """
    Generate population data for city zones.
    """

    if not Zones:
        return pd.DataFrame(columns=["Zone", "Population"])

    rng = np.random.default_rng(seed)

    populations = rng.normal(
        loc=mean,
        scale=std,
        size=len(Zones)
    )

    populations = np.clip(populations, 0, None).astype(int)

    return pd.DataFrame({
        "Zone": Zones,
        "Population": populations
    })


# ---------------------------------------------------------------------------
# TRAFFIC GENERATION
# ---------------------------------------------------------------------------

def generate_traffic(
    zones: List[str],
    days: int = 30,
    base_volume: float = 500.0,
    noise_std: float = 20.0,
    seed: Optional[int] = 42,
) -> pd.DataFrame:

    """
    Generate hourly traffic simulation.
    """

    if days == 0 or not zones:
        return pd.DataFrame(
            columns=["Zone", "datetime", "traffic"]
        )

    rng = np.random.default_rng(seed)

    n_hours = days * 24

    # Create hourly timestamps
    dt_index = pd.date_range(
        start="2026-05-14",
        periods=n_hours,
        freq="h"
    )

    # Extract hour values
    hours_of_day = dt_index.hour.to_numpy()

    # Monday = 0, Sunday = 6
    day_of_week = dt_index.dayofweek.to_numpy()

    # Gaussian rush-hour peaks
    morning_peak = np.exp(
        -0.5 * ((hours_of_day - 8) / 2.5) ** 2
    )

    evening_peak = np.exp(
        -0.5 * ((hours_of_day - 18) / 2.5) ** 2
    )

    # Daily traffic pattern
    daily_pattern = (
        1.0 +
        0.8 * (morning_peak + evening_peak)
    )

    # Weekend reduction
    weekly_pattern = np.where(
        day_of_week < 5,
        1.0,
        0.8
    )

    records = []

    for zone in zones:

        # Random fluctuations
        noise = rng.normal(
            0,
            noise_std,
            size=n_hours
        )

        traffic = (
            base_volume *
            daily_pattern *
            weekly_pattern +
            noise
        )

        traffic = np.clip(
            traffic,
            0,
            None
        )

        for i, ts in enumerate(dt_index):

            records.append({
                "Zone": zone,
                "datetime": ts,
                "traffic": round(traffic[i], 2)
            })

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# WEATHER GENERATION
# ---------------------------------------------------------------------------

def generate_weather(
    days: int = 365,
    base_temp: float = 25.0,
    temp_amplitude: float = 10.0,
    base_humidity: float = 60.0,
    seed: Optional[int] = 42,
) -> pd.DataFrame:

    """
    Generate daily weather simulation.
    """

    if days == 0:
        return pd.DataFrame(
            columns=["date", "temperature", "humidity"]
        )

    rng = np.random.default_rng(seed)

    # Day numbers
    day_idx = np.arange(days)

    date_index = pd.date_range(
        start="2024-01-01",
        periods=days,
        freq="D"
    )

    # Seasonal sine-wave cycle
    seasonal_cycle = np.sin(
        2 * np.pi * (day_idx - 80) / 365
    )

    # Temperature generation
    temperature = (
        base_temp +
        temp_amplitude * seasonal_cycle +
        rng.normal(0, 1.5, size=days)
    )

    # Humidity generation
    humidity = (
        base_humidity -
        0.4 * temp_amplitude * seasonal_cycle +
        rng.normal(0, 3.0, size=days)
    )

    humidity = np.clip(
        humidity,
        0,
        100
    )

    return pd.DataFrame({
        "date": date_index,
        "temperature": np.round(temperature, 2),
        "humidity": np.round(humidity, 2),
    })


# ---------------------------------------------------------------------------
# TEST EXECUTION
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    from config import load_config, get_zones

    config = load_config()

    ZONES = get_zones(config)

    pop_df = generate_population(
        ZONES,
        **config["population"]
    )

    traffic_df = generate_traffic(
        ZONES,
        **config["traffic"]
    )

    weather_df = generate_weather(
        **config["weather"]
    )

    print("\n=== Population ===")
    print(pop_df.to_string(index=False))

    print("\n=== Traffic (first 12 rows) ===")
    print(traffic_df.head(12).to_string(index=False))

    print("\n=== Weather (first 7 days) ===")
    print(weather_df.head(7).to_string(index=False))