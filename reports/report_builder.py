"""
reports/report_builder.py
Generates text summary reports and CSV exports
for the Urban Digital Twin Engine.
"""

from __future__ import annotations

import os
import pandas as pd

from datetime import datetime

from analytics import (
    population_summary,
    top_zone_population,
    bottom_zone_population,

    traffic_summary,
    peak_traffic_hour,
    busiest_zone,
    quietest_zone,
    weekend_vs_weekday,

    weather_summary,
    hottest_day,
    coldest_day,
    days_above_temp,
    days_below_temp,
)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _ensure_dir(path: str) -> None:
    """
    Creates output directory if missing.
    """

    os.makedirs(path, exist_ok=True)


def _header(
    title: str,
    city: str,
    scenario: str
) -> str:

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return (
        f"{'=' * 60}\n"
        f"  {title}\n"
        f"  City     : {city}\n"
        f"  Scenario : {scenario}\n"
        f"  Generated: {now}\n"
        f"{'=' * 60}\n"
    )


def _footer() -> str:

    return (
        f"\n{'=' * 60}\n"
        f"  End of Report\n"
        f"{'=' * 60}\n"
    )


# ---------------------------------------------------------------------------
# POPULATION REPORT
# ---------------------------------------------------------------------------

def build_population_report(
    pop_df: pd.DataFrame,
    city: str = "Metropolis",
    scenario: str = "Baseline",
    output_dir: str = "outputs",
) -> str:

    """
    Generates population report.
    """

    _ensure_dir(output_dir)

    summary = population_summary(pop_df)

    top = top_zone_population(pop_df)

    bottom = bottom_zone_population(pop_df)

    lines = [
        _header("POPULATION REPORT", city, scenario),

        f"  Total Population   : {summary['total_population'][0]:,}",
        f"  Average per Zone   : {summary['average_population'][0]:,.0f}",
        f"  Max Population     : {summary['max_population'][0]:,}",
        f"  Min Population     : {summary['min_population'][0]:,}",

        f"\n  Highest Zone : {top['Zone']} ({top['Population']:,})",
        f"  Lowest Zone  : {bottom['Zone']} ({bottom['Population']:,})",

        f"\n  Zone Breakdown:",
        f"  {'-' * 40}",
    ]

    for _, row in pop_df.iterrows():

        lines.append(
            f"  {row['Zone']:<20} "
            f"{row['Population']:>10,}"
        )

    lines.append(_footer())

    report = "\n".join(lines)

    # Save CSV
    csv_path = os.path.join(
        output_dir,
        "population_report.csv"
    )

    pop_df.to_csv(csv_path, index=False)

    # Save TXT
    txt_path = os.path.join(
        output_dir,
        "population_report.txt"
    )

    with open(
        txt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report


# ---------------------------------------------------------------------------
# TRAFFIC REPORT
# ---------------------------------------------------------------------------

def build_traffic_report(
    traffic_df: pd.DataFrame,
    city: str = "Metropolis",
    scenario: str = "Baseline",
    output_dir: str = "outputs",
) -> str:

    """
    Generates traffic report.
    """

    _ensure_dir(output_dir)

    t_summary = traffic_summary(traffic_df)

    peak_h = peak_traffic_hour(traffic_df)

    busy = busiest_zone(traffic_df)

    quiet = quietest_zone(traffic_df)

    ww = weekend_vs_weekday(traffic_df)

    lines = [
        _header("TRAFFIC REPORT", city, scenario),

        f"  Busiest Zone   : {busy}",
        f"  Quietest Zone  : {quiet}",

        f"\n  Average Traffic per Zone:",
        f"  {'-' * 40}",
    ]

    for _, row in t_summary.iterrows():

        lines.append(
            f"  {row['Zone']:<20} "
            f"avg: {row['avg_traffic']:>8.2f}  "
            f"max: {row['max_traffic']:>8.2f}  "
            f"min: {row['min_traffic']:>8.2f}"
        )

    lines.append("\n  Peak Traffic Hour per Zone:")
    lines.append(f"  {'-' * 40}")

    for _, row in peak_h.iterrows():

        lines.append(
            f"  {row['Zone']:<20} "
            f"peak hour: {int(row['peak_hour']):02d}:00  "
            f"avg traffic: {row['peak_avg_traffic']:>8.2f}"
        )

    lines.append("\n  Weekend vs Weekday Traffic:")
    lines.append(f"  {'-' * 40}")

    for _, row in ww.iterrows():

        lines.append(
            f"  {row['Zone']:<20} "
            f"weekday: {row['weekday_avg']:>8.2f}  "
            f"weekend: {row['weekend_avg']:>8.2f}"
        )

    lines.append(_footer())

    report = "\n".join(lines)

    # Save CSV
    csv_path = os.path.join(
        output_dir,
        "traffic_report.csv"
    )

    t_summary.to_csv(csv_path, index=False)

    # Save TXT
    txt_path = os.path.join(
        output_dir,
        "traffic_report.txt"
    )

    with open(
        txt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report


# ---------------------------------------------------------------------------
# WEATHER REPORT
# ---------------------------------------------------------------------------

def build_weather_report(
    weather_df: pd.DataFrame,
    city: str = "Metropolis",
    scenario: str = "Baseline",
    output_dir: str = "outputs",
) -> str:

    """
    Generates weather report.
    """

    _ensure_dir(output_dir)

    w_summary = weather_summary(weather_df)

    hot = hottest_day(weather_df)

    cold = coldest_day(weather_df)

    above30 = days_above_temp(weather_df, 30.0)

    below5 = days_below_temp(weather_df, 5.0)

    lines = [
        _header("WEATHER REPORT", city, scenario),

        f"  Average Temperature : {w_summary['avg_temperature'][0]}°C",
        f"  Max Temperature     : {w_summary['max_temperature'][0]}°C",
        f"  Min Temperature     : {w_summary['min_temperature'][0]}°C",

        f"  Average Humidity    : {w_summary['avg_humidity'][0]}%",
        f"  Max Humidity        : {w_summary['max_humidity'][0]}%",
        f"  Min Humidity        : {w_summary['min_humidity'][0]}%",

        f"\n  Hottest Day : "
        f"{str(hot['date'])[:10]}  →  "
        f"{hot['temperature']}°C",

        f"  Coldest Day : "
        f"{str(cold['date'])[:10]}  →  "
        f"{cold['temperature']}°C",

        f"\n  Days Above 30°C : {above30}",
        f"  Days Below  5°C : {below5}",

        _footer(),
    ]

    report = "\n".join(lines)

    # Save CSV
    csv_path = os.path.join(
        output_dir,
        "weather_report.csv"
    )

    weather_df.to_csv(csv_path, index=False)

    # Save TXT
    txt_path = os.path.join(
        output_dir,
        "weather_report.txt"
    )

    with open(
        txt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report


# ---------------------------------------------------------------------------
# RECOMMENDATIONS REPORT
# ---------------------------------------------------------------------------

def build_recommendations_report(
    recs_df: pd.DataFrame,
    city: str = "Metropolis",
    scenario: str = "Baseline",
    output_dir: str = "outputs",
) -> str:

    """
    Generates recommendations report.
    """

    _ensure_dir(output_dir)

    critical = len(
        recs_df[
            recs_df["severity"].str.contains("Critical")
        ]
    )

    warning = len(
        recs_df[
            recs_df["severity"].str.contains("Warning")
        ]
    )

    normal = len(
        recs_df[
            recs_df["severity"].str.contains("Normal")
        ]
    )

    lines = [
        _header("RECOMMENDATIONS REPORT", city, scenario),

        f"  Total Recommendations : {len(recs_df)}",
        f"  🔴 Critical           : {critical}",
        f"  🟡 Warning            : {warning}",
        f"  🟢 Normal             : {normal}",

        f"\n  {'-' * 56}",
    ]

    for _, row in recs_df.iterrows():

        lines.append(
            f"\n  [{row['severity']}]  "
            f"{row['category']} — {row['zone']}\n"
            f"  {row['recommendation']}"
        )

        lines.append(f"  {'-' * 56}")

    lines.append(_footer())

    report = "\n".join(lines)

    # Save CSV
    csv_path = os.path.join(
        output_dir,
        "recommendations_report.csv"
    )

    recs_df.to_csv(csv_path, index=False)

    # Save TXT
    txt_path = os.path.join(
        output_dir,
        "recommendations_report.txt"
    )

    with open(
        txt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    return report


# ---------------------------------------------------------------------------
# FULL REPORT
# ---------------------------------------------------------------------------

def build_full_report(
    pop_df: pd.DataFrame,
    traffic_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    recs_df: pd.DataFrame,
    city: str = "Metropolis",
    scenario: str = "Baseline",
    output_dir: str = "outputs",
) -> str:

    """
    Builds complete system report.
    """

    pop_report = build_population_report(
        pop_df,
        city,
        scenario,
        output_dir
    )

    traf_report = build_traffic_report(
        traffic_df,
        city,
        scenario,
        output_dir
    )

    weat_report = build_weather_report(
        weather_df,
        city,
        scenario,
        output_dir
    )

    recs_report = build_recommendations_report(
        recs_df,
        city,
        scenario,
        output_dir
    )

    full = "\n\n".join([
        pop_report,
        traf_report,
        weat_report,
        recs_report
    ])

    txt_path = os.path.join(
        output_dir,
        "full_report.txt"
    )

    with open(
        txt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(full)

    return full