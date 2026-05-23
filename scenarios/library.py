from __future__ import annotations

import pandas as pd
import numpy as np


# -------------------------------------------------------------------
# Rainstorm Scenario
# -------------------------------------------------------------------

def simulate_rainstorm(
    traffic_df: pd.DataFrame,
    reduction_factor: float = 0.30
) -> pd.DataFrame:

    """
    Simulate traffic reduction during heavy rain.

    """

    modified_df = traffic_df.copy()

    modified_df["traffic"] = (
        modified_df["traffic"] * (1 - reduction_factor)
    )

    return modified_df


# -------------------------------------------------------------------
# Heatwave Scenario
# -------------------------------------------------------------------

def simulate_heatwave(
    weather_df: pd.DataFrame,
    temperature_increase: float = 5.0
) -> pd.DataFrame:

    """
    Increase city temperature during heatwave.
    """

    modified_df = weather_df.copy()

    modified_df["temperature"] += temperature_increase

    return modified_df


# -------------------------------------------------------------------
# Festival Traffic Surge
# -------------------------------------------------------------------

def simulate_festival_traffic(
    traffic_df: pd.DataFrame,
    surge_factor: float = 0.40
) -> pd.DataFrame:

    """
    Simulate increased traffic during festivals/events.
    """

    modified_df = traffic_df.copy()

    modified_df["traffic"] = (
        modified_df["traffic"] * (1 + surge_factor)
    )

    return modified_df