from config import load_config, get_zones

from core import (
    generate_population,
    generate_traffic,
    generate_weather
)

from intelligence import run_intelligence

from reports.report_builder import (
    build_full_report
)


# ---------------------------------------------------
# Load Config
# ---------------------------------------------------

config = load_config()

ZONES = get_zones(config)


# ---------------------------------------------------
# Generate Data
# ---------------------------------------------------

population_df = generate_population(
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


# ---------------------------------------------------
# Run Intelligence Engine
# ---------------------------------------------------

result = run_intelligence(
    "Baseline",
    ZONES,
    traffic_df,
    weather_df,
    population_df
)


# ---------------------------------------------------
# Build Reports
# ---------------------------------------------------

report = build_full_report(
    result["population"],
    result["traffic"],
    result["weather"],
    result["recommendations"],
    city=config["default_city"],
    scenario="Baseline",
    output_dir=config["output_dir"]
)


# ---------------------------------------------------
# Console Output
# ---------------------------------------------------

print(report)

print("\nSystem executed successfully.")