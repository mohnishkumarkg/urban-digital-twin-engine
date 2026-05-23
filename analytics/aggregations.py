
from __future__ import annotations
import pandas as pd
 
 
# ---------------------------------------------------------------------------
# POPULATION AGGREGATIONS
# ---------------------------------------------------------------------------
 
def population_summary(pop_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns total, average, max and min population across all zones.
    """
    return pd.DataFrame({
        "total_population":   [pop_df["Population"].sum()],
        "average_population": [pop_df["Population"].mean().round(2)],
        "max_population":     [pop_df["Population"].max()],
        "min_population":     [pop_df["Population"].min()],
    })
 
 
def top_zone_population(pop_df: pd.DataFrame) -> pd.Series:
    """
    Returns the zone with the highest population.
    """
    idx = pop_df["Population"].idxmax()
    return pop_df.loc[idx]
 
 
def bottom_zone_population(pop_df: pd.DataFrame) -> pd.Series:
    """
    Returns the zone with the lowest population.
    """
    idx = pop_df["Population"].idxmin()
    return pop_df.loc[idx]
 
 
# ---------------------------------------------------------------------------
# TRAFFIC AGGREGATIONS
# ---------------------------------------------------------------------------
 
def traffic_summary(traffic_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns average, max and min traffic per zone.
    """
    return (
        traffic_df
        .groupby("Zone")["traffic"]
        .agg(
            avg_traffic="mean",
            max_traffic="max",
            min_traffic="min",
        )
        .round(2)
        .reset_index()
    )
 
 
def peak_traffic_hour(traffic_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns the hour of day with highest average traffic per zone.
    """
    df = traffic_df.copy()
    df["hour"] = pd.to_datetime(df["datetime"]).dt.hour
 
    return (
        df
        .groupby(["Zone", "hour"])["traffic"]
        .mean()
        .round(2)
        .reset_index()
        .sort_values("traffic", ascending=False)
        .groupby("Zone")
        .first()
        .reset_index()
        .rename(columns={
            "traffic": "peak_avg_traffic",
            "hour":    "peak_hour"
        })
    )
 
 
def busiest_zone(traffic_df: pd.DataFrame) -> str:
    """
    Returns the name of the zone with the highest average traffic.
    """
    summary = traffic_summary(traffic_df)
    idx     = summary["avg_traffic"].idxmax()
    return summary.loc[idx, "Zone"]
 
 
def quietest_zone(traffic_df: pd.DataFrame) -> str:
    """
    Returns the name of the zone with the lowest average traffic.
    """
    summary = traffic_summary(traffic_df)
    idx     = summary["avg_traffic"].idxmin()
    return summary.loc[idx, "Zone"]
 
 
def weekend_vs_weekday(traffic_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compares average weekend vs weekday traffic per zone.
    """
    df              = traffic_df.copy()
    df["datetime"]  = pd.to_datetime(df["datetime"])
    df["is_weekend"] = df["datetime"].dt.dayofweek >= 5
 
    weekday = (
        df[df["is_weekend"] == False]
        .groupby("Zone")["traffic"]
        .mean()
        .round(2)
        .rename("weekday_avg")
    )
    weekend = (
        df[df["is_weekend"] == True]
        .groupby("Zone")["traffic"]
        .mean()
        .round(2)
        .rename("weekend_avg")
    )
    return pd.concat([weekday, weekend], axis=1).reset_index()
 
 
# ---------------------------------------------------------------------------
# WEATHER AGGREGATIONS
# ---------------------------------------------------------------------------
 
def weather_summary(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns average, max and min temperature and humidity.
    """
    return pd.DataFrame({
        "avg_temperature": [weather_df["temperature"].mean().round(2)],
        "max_temperature": [weather_df["temperature"].max()],
        "min_temperature": [weather_df["temperature"].min()],
        "avg_humidity":    [weather_df["humidity"].mean().round(2)],
        "max_humidity":    [weather_df["humidity"].max()],
        "min_humidity":    [weather_df["humidity"].min()],
    })
 
 
def hottest_day(weather_df: pd.DataFrame) -> pd.Series:
    """
    Returns the row with the highest temperature.
 """
    idx = weather_df["temperature"].idxmax()
    return weather_df.loc[idx]
 
 
def coldest_day(weather_df: pd.DataFrame) -> pd.Series:
    """
    Returns the row with the lowest temperature.
    """
    idx = weather_df["temperature"].idxmin()
    return weather_df.loc[idx]
 
 
def days_above_temp(weather_df: pd.DataFrame, threshold: float = 30.0) -> int:
    """
    Returns number of days where temperature exceeded the threshold.
    """
    return int((weather_df["temperature"] > threshold).sum())
 
 
def days_below_temp(weather_df: pd.DataFrame, threshold: float = 5.0) -> int:
    """
    Returns number of days where temperature fell below the threshold.
    """
    return int((weather_df["temperature"] < threshold).sum())
 
 
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
 
    print("\n=== Population Summary ===")
    print(population_summary(pop_df).to_string(index=False))
 
    print("\n=== Top Zone (Population) ===")
    print(top_zone_population(pop_df))
 
    print("\n=== Bottom Zone (Population) ===")
    print(bottom_zone_population(pop_df))
 
    print("\n=== Traffic Summary ===")
    print(traffic_summary(traffic_df).to_string(index=False))
 
    print("\n=== Peak Traffic Hour per Zone ===")
    print(peak_traffic_hour(traffic_df).to_string(index=False))
 
    print("\n=== Busiest Zone ===")
    print(busiest_zone(traffic_df))
 
    print("\n=== Quietest Zone ===")
    print(quietest_zone(traffic_df))
 
    print("\n=== Weekend vs Weekday Traffic ===")
    print(weekend_vs_weekday(traffic_df).to_string(index=False))
 
    print("\n=== Weather Summary ===")
    print(weather_summary(weather_df).to_string(index=False))
 
    print("\n=== Hottest Day ===")
    print(hottest_day(weather_df))
 
    print("\n=== Coldest Day ===")
    print(coldest_day(weather_df))
 
    print(f"\n=== Days Above 30°C : {days_above_temp(weather_df, 30.0)} ===")
    print(f"=== Days Below  5°C : {days_below_temp(weather_df,  5.0)} ===")