"""
reports — Text summary and CSV report generation
for the Urban Digital Twin Engine.

Provides:
    build_population_report      →  population summary + CSV
    build_traffic_report         →  traffic summary + CSV
    build_weather_report         →  weather summary + CSV
    build_recommendations_report →  recommendations summary + CSV
    build_full_report            →  all four in one call
"""

from .report_builder import (
    build_population_report,
    build_traffic_report,
    build_weather_report,
    build_recommendations_report,
    build_full_report,
)

__all__ = [
    "build_population_report",
    "build_traffic_report",
    "build_weather_report",
    "build_recommendations_report",
    "build_full_report",
]