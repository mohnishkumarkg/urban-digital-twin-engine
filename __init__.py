"""
core/__init__.py
================
Public API for the UDT-DIE core package.

Usage
-----
    from core import generate_traffic, generate_weather, generate_population
    from core import apply_seasonality, add_lagged_features
    from core import pollution_model, energy_model
"""

from core.generator import (
    generate_population,
    generate_traffic,
    generate_weather,
)

from core.simulator import (
    apply_daily_pattern,
    apply_seasonality,
    apply_weekly_pattern,
    add_lagged_features,
)

from core.dependency_model import (
    pollution_model,
    pollution_with_lag,
    energy_model,
    public_transport_model,
    compute_dependency_covariance,
)

__all__ = [
    # generator
    "generate_population",
    "generate_traffic",
    "generate_weather",
    # simulator
    "apply_daily_pattern",
    "apply_seasonality",
    "apply_weekly_pattern",
    "add_lagged_features",
    # dependency model
    "pollution_model",
    "pollution_with_lag",
    "energy_model",
    "public_transport_model",
    "compute_dependency_covariance",
]
