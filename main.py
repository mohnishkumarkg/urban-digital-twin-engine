from config import load_config, get_zones

from datetime import datetime

from core import (
    generate_population,
    generate_traffic,
    generate_weather
)

from intelligence import run_intelligence

from reports.report_builder import (
    build_full_report
)


# ===================================================
# SYSTEM BANNER
# ===================================================

print("=" * 60)
print("URBAN DIGITAL TWIN & DECISION INTELLIGENCE ENGINE")
print("=" * 60)

start_time = datetime.now()


# ===================================================
# LOAD CONFIG
# ===================================================

print("\nLoading configuration...")

config = load_config()

ZONES = get_zones(config)

print(f"Loaded {len(ZONES)} zones.")


# ===================================================
# GENERATE DATA
# ===================================================

print("\n[1/5] Generating population data...")

population_df = generate_population(
    ZONES,
    **config["population"]
)

print("[2/5] Generating traffic simulation...")

traffic_df = generate_traffic(
    ZONES,
    **config["traffic"]
)

print("[3/5] Generating weather simulation...")

weather_df = generate_weather(
    **config["weather"]
)


# ===================================================
# SAVE RAW DATASETS
# ===================================================

print("\nSaving raw datasets...")

population_df.to_csv(
    "outputs/raw_population.csv",
    index=False
)

traffic_df.to_csv(
    "outputs/raw_traffic.csv",
    index=False
)

weather_df.to_csv(
    "outputs/raw_weather.csv",
    index=False
)


# ===================================================
# SCENARIO SELECTION
# ===================================================

print("\nAvailable Scenarios:")
print("1. Baseline")
print("2. Heatwave")
print("3. Festival")

choice = input("\nChoose scenario: ").strip()

scenario_map = {
    "1": "Baseline",
    "2": "Heatwave",
    "3": "Festival"
}

scenario = scenario_map.get(choice, "Baseline")

print(f"\nRunning scenario: {scenario}")


# ===================================================
# RUN INTELLIGENCE ENGINE
# ===================================================

print("[4/5] Running intelligence engine...")

result = run_intelligence(
    scenario,
    ZONES,
    traffic_df,
    weather_df,
    population_df
)


# ===================================================
# BUILD REPORTS
# ===================================================

print("[5/5] Building analytical reports...")

report = build_full_report(
    result["population"],
    result["traffic"],
    result["weather"],
    result["recommendations"],
    city=config["default_city"],
    scenario=scenario,
    output_dir=config["output_dir"]
)


# ===================================================
# CONSOLE OUTPUT
# ===================================================

print("\n")
print(report)

print("\nSystem executed successfully.")


# ===================================================
# EXECUTION SUMMARY
# ===================================================

print("\nExecution Summary")
print("-" * 40)

print(f"Zones simulated      : {len(ZONES)}")

print(f"Population records   : {len(population_df)}")

print(f"Traffic records      : {len(traffic_df):,}")

print(f"Weather records      : {len(weather_df)}")

print("-" * 40)


# ===================================================
# RUNTIME METADATA
# ===================================================

end_time = datetime.now()

print(f"\nStarted  : {start_time}")

print(f"Finished : {end_time}")

print(f"Runtime  : {end_time - start_time}")