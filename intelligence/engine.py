"""
intelligence/engine.py
Scenario simulation and recommendations engine for the Urban Digital Twin Engine.

Scenarios:
    Baseline   →  normal city conditions
    Heatwave   →  temperature spike, humidity rise, traffic drop
    Festival   →  traffic surge in selected zones

Recommendations:
    Combines traffic, weather and population data to generate
    actionable city management decisions.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import List, Optional


# ---------------------------------------------------------------------------
# SCENARIO SIMULATION
# ---------------------------------------------------------------------------

def run_scenario(
    scenario: str,
    zones: List[str],
    traffic_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    pop_df: pd.DataFrame,
    festival_zones: Optional[List[str]] = None,
) -> dict:
    scenario = scenario.strip().title()

    # Always work on copies — never modify original data
    traffic    = traffic_df.copy()
    weather    = weather_df.copy()
    population = pop_df.copy()

    if scenario == "Baseline":
        description = (
            "Normal city conditions. "
            "No modifiers applied. "
            "Traffic, weather and population reflect standard patterns."
        )

    elif scenario == "Heatwave":
        weather["temperature"] = (weather["temperature"] + 10.0).round(2)
        weather["humidity"]    = np.clip(weather["humidity"] + 15.0, 0, 100).round(2)
        traffic["traffic"]     = (traffic["traffic"] * 0.80).round(2)
        description = (
            "Heatwave conditions active. "
            "Temperature raised by +10°C, humidity by +15%. "
            "Traffic reduced by 20% as residents stay indoors."
        )

    elif scenario == "Festival":
        if not festival_zones:
            festival_zones = [zones[0]]
        mask = traffic["Zone"].isin(festival_zones)
        traffic.loc[mask, "traffic"] = (
            traffic.loc[mask, "traffic"] * 3.0
        ).round(2)
        description = (
            f"Festival scenario active in zones: {', '.join(festival_zones)}. "
            f"Traffic surged by 3x in affected zones."
        )

    else:
        raise ValueError(
            f"Unknown scenario '{scenario}'. "
            f"Choose from: Baseline, Heatwave, Festival."
        )

    return {
        "scenario":    scenario,
        "description": description,
        "traffic":     traffic,
        "weather":     weather,
        "population":  population,
    }


# ---------------------------------------------------------------------------
# RECOMMENDATIONS ENGINE
# ---------------------------------------------------------------------------

def generate_recommendations(
    scenario_result: dict,
    traffic_threshold: float  = 800.0,
    temp_threshold: float     = 35.0,
    humidity_threshold: float = 80.0,
    pop_threshold: int        = 60_000,
) -> pd.DataFrame:
    traffic    = scenario_result["traffic"]
    weather    = scenario_result["weather"]
    population = scenario_result["population"]
    scenario   = scenario_result["scenario"]

    recommendations = []

    # ── Traffic ──────────────────────────────────────────────
    avg_traffic = traffic.groupby("Zone")["traffic"].mean().round(2)

    for zone, avg in avg_traffic.items():
        if avg > traffic_threshold * 1.5:
            recommendations.append({
                "category":       "Traffic",
                "zone":           zone,
                "recommendation": f"Critical traffic congestion detected. Deploy emergency traffic control and reroute vehicles away from {zone}.",
                "severity":       "🔴 Critical",
            })
        elif avg > traffic_threshold:
            recommendations.append({
                "category":       "Traffic",
                "zone":           zone,
                "recommendation": f"High traffic volume in {zone}. Increase public transport frequency and open overflow parking.",
                "severity":       "🟡 Warning",
            })
        else:
            recommendations.append({
                "category":       "Traffic",
                "zone":           zone,
                "recommendation": f"Traffic in {zone} is within normal range. No action required.",
                "severity":       "🟢 Normal",
            })

    # ── Weather ──────────────────────────────────────────────
    avg_temp   = weather["temperature"].mean().round(2)
    hot_days   = int((weather["temperature"] > temp_threshold).sum())
    humid_days = int((weather["humidity"] > humidity_threshold).sum())

    if avg_temp > temp_threshold:
        recommendations.append({
            "category":       "Weather",
            "zone":           "City-wide",
            "recommendation": f"Average temperature is {avg_temp}°C — above threshold. Open cooling centres, issue public heat advisory and increase water supply.",
            "severity":       "🔴 Critical",
        })
    elif hot_days > 5:
        recommendations.append({
            "category":       "Weather",
            "zone":           "City-wide",
            "recommendation": f"{hot_days} days exceeded {temp_threshold}°C. Prepare cooling centres and monitor vulnerable populations.",
            "severity":       "🟡 Warning",
        })
    else:
        recommendations.append({
            "category":       "Weather",
            "zone":           "City-wide",
            "recommendation": f"Temperature averaging {avg_temp}°C. Conditions are normal.",
            "severity":       "🟢 Normal",
        })

    if humid_days > 5:
        recommendations.append({
            "category":       "Weather",
            "zone":           "City-wide",
            "recommendation": f"{humid_days} days exceeded {humidity_threshold}% humidity. Monitor air quality and issue comfort advisories.",
            "severity":       "🟡 Warning",
        })

    # ── Population ───────────────────────────────────────────
    for _, row in population.iterrows():
        if row["Population"] > pop_threshold:
            recommendations.append({
                "category":       "Population",
                "zone":           row["Zone"],
                "recommendation": f"{row['Zone']} has a high population of {row['Population']:,}. Prioritise infrastructure investment and emergency service coverage.",
                "severity":       "🟡 Warning",
            })
        else:
            recommendations.append({
                "category":       "Population",
                "zone":           row["Zone"],
                "recommendation": f"Population in {row['Zone']} is {row['Population']:,}. Within manageable range.",
                "severity":       "🟢 Normal",
            })

    # ── Scenario specific ────────────────────────────────────
    if scenario == "Heatwave":
        recommendations.append({
            "category":       "Scenario",
            "zone":           "City-wide",
            "recommendation": "Heatwave protocol active. Restrict outdoor events, increase hospital readiness and issue citywide emergency alert.",
            "severity":       "🔴 Critical",
        })
    elif scenario == "Festival":
        recommendations.append({
            "category":       "Scenario",
            "zone":           "City-wide",
            "recommendation": "Festival scenario active. Coordinate with event management, deploy extra policing and prepare medical response teams.",
            "severity":       "🟡 Warning",
        })

    return pd.DataFrame(recommendations)


# ---------------------------------------------------------------------------
# COMBINED RUNNER
# ---------------------------------------------------------------------------

def run_intelligence(
    scenario: str,
    zones: List[str],
    traffic_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    pop_df: pd.DataFrame,
    festival_zones: Optional[List[str]] = None,
) -> dict:
    result                    = run_scenario(scenario, zones, traffic_df, weather_df, pop_df, festival_zones)
    result["recommendations"] = generate_recommendations(result)
    return result


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from config import load_config, get_zones
    from core   import generate_population, generate_traffic, generate_weather

    config = load_config()
    ZONES  = get_zones(config)

    pop_df     = generate_population(ZONES, **config["population"])
    traffic_df = generate_traffic(ZONES,    **config["traffic"])
    weather_df = generate_weather(          **config["weather"])

    print("\nAvailable scenarios: Baseline, Heatwave, Festival")
    scenario = input("Choose scenario: ").strip()

    festival_zones = None
    if scenario.title() == "Festival":
        fest = input(f"Which zones are affected? (comma separated, e.g. {ZONES[0]}): ")
        festival_zones = [z.strip() for z in fest.split(",")]

    result = run_intelligence(scenario, ZONES, traffic_df, weather_df, pop_df, festival_zones)

    print(f"\n=== Scenario: {result['scenario']} ===")
    print(result["description"])

    print("\n=== Modified Traffic (first 12 rows) ===")
    print(result["traffic"].head(12).to_string(index=False))

    print("\n=== Modified Weather (first 7 days) ===")
    print(result["weather"].head(7).to_string(index=False))

    print("\n=== Recommendations ===")
    print(result["recommendations"].to_string(index=False))