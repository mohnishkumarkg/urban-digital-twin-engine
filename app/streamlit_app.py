import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.loader import load_config
from core import generate_population, generate_traffic, generate_weather
from analytics import (
    population_summary, top_zone_population, bottom_zone_population,
    traffic_summary, peak_traffic_hour, busiest_zone, quietest_zone,
    weekend_vs_weekday, weather_summary, hottest_day, coldest_day,
    days_above_temp, days_below_temp,
)
from intelligence import run_intelligence

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Urban Digital Twin",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# STYLING
# ---------------------------------------------------------------------------

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #e0e0e0; }

div[data-testid="metric-container"] {
    background: #1c1f26;
    border: 1px solid #2e3140;
    border-radius: 10px;
    padding: 16px;
}

h2 { color: #4fc3f7; border-bottom: 1px solid #2e3140; padding-bottom: 8px; }
h3 { color: #81d4fa; }

section[data-testid="stSidebar"] { background-color: #13161e; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------

st.sidebar.title("🏙️ Urban Digital Twin")

config = load_config()

n = st.sidebar.number_input("Number of Zones", 1, 20, config["num_zones"])

ZONES = [
    st.sidebar.text_input(f"Zone {i+1}", f"Zone {i+1}")
    for i in range(n)
]

days = st.sidebar.slider("Simulation Days", 1, 365, config["simulation_days"])

scenario = st.sidebar.selectbox("Scenario", config["default_scenarios"])

run = st.sidebar.button("▶ Run Simulation", use_container_width=True)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------

st.title("🏙️ Urban Digital Twin & Decision Intelligence Engine")
st.caption(f"City: {config['default_city']} | Scenario: {scenario} | Days: {days}")

if not run:
    st.info("Configure sidebar and run simulation.")
    st.stop()

# ---------------------------------------------------------------------------
# DATA GENERATION
# ---------------------------------------------------------------------------

with st.spinner("Generating data..."):
    pop_df = generate_population(ZONES, **config["population"])
    traffic_df = generate_traffic(ZONES, days=days, **config["traffic"])
    weather_df = generate_weather(days=days, **config["weather"])

    result = run_intelligence(
        scenario, ZONES, traffic_df, weather_df, pop_df, None
    )

    mod_pop = result["population"]
    mod_traffic = result["traffic"]
    mod_weather = result["weather"]
    recs = result["recommendations"]

# ---------------------------------------------------------------------------
# CITY HEALTH SCORE (NEW UPGRADE)
# ---------------------------------------------------------------------------

traffic_risk = mod_traffic["traffic"].mean()
weather_risk = mod_weather["temperature"].std()

city_health = max(0, 100 - (traffic_risk * 0.05 + weather_risk * 2))

colA, colB, colC = st.columns(3)

colA.metric("🏙️ City Health Score", f"{city_health:.1f}/100")
colB.metric("🚗 Avg Traffic Load", f"{traffic_risk:.2f}")
colC.metric("🌡️ Weather Volatility", f"{weather_risk:.2f}")

st.markdown("---")

# ---------------------------------------------------------------------------
# INSIGHTS (ONLY ONCE - FIXED)
# ---------------------------------------------------------------------------

st.subheader("🧠 System Insights")
st.info("🚨 Traffic peaks mostly occur in evening hours across zones.")
st.info("🌡️ Weather volatility increases traffic instability.")

st.markdown("---")

# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Population",
    "🚗 Traffic",
    "🌤️ Weather",
    "🧠 Recommendations",
])

# ---------------------------------------------------------------------------
# TAB 1 - POPULATION
# ---------------------------------------------------------------------------

with tab1:
    st.header("Population Overview")

    summary = population_summary(mod_pop)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Population", f"{summary['total_population'][0]:,}")
    c2.metric("Avg per Zone", f"{summary['average_population'][0]:,.0f}")
    c3.metric("Highest Zone", f"{top_zone_population(mod_pop)['Zone']}")
    c4.metric("Lowest Zone", f"{bottom_zone_population(mod_pop)['Zone']}")

    fig = px.bar(
        mod_pop,
        x="Population",
        y="Zone",
        orientation="h",
        template="plotly_dark",
        color="Population"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 2 - TRAFFIC (FIXED DUPLICATE + CLEAN UI)
# ---------------------------------------------------------------------------

with tab2:
    st.header("Traffic Analysis")

    busy = busiest_zone(mod_traffic)
    quiet = quietest_zone(mod_traffic)

    c1, c2, c3 = st.columns(3)
    c1.metric("Busiest Zone", busy)
    c2.metric("Quietest Zone", quiet)
    c3.metric("Zones", len(ZONES))

    zone_filter = st.multiselect(
        "Select Zones",
        ZONES,
        default=ZONES[:2] if len(ZONES) >= 2 else ZONES,
        key="traffic_filter"
    )

    filtered = mod_traffic[mod_traffic["Zone"].isin(zone_filter)]

    fig = px.line(
        filtered,
        x="datetime",
        y="traffic",
        color="Zone",
        markers=True,
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    peak_h = peak_traffic_hour(mod_traffic)

    fig2 = px.bar(
        peak_h,
        x="Zone",
        y="peak_hour",
        template="plotly_dark"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 3 - WEATHER
# ---------------------------------------------------------------------------

with tab3:
    st.header("Weather Analysis")

    hot = hottest_day(mod_weather)
    cold = coldest_day(mod_weather)

    c1, c2 = st.columns(2)
    c1.metric("Hottest", f"{hot['temperature']}°C")
    c2.metric("Coldest", f"{cold['temperature']}°C")

    fig = px.line(
        mod_weather,
        x="date",
        y="temperature",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 4 - RECOMMENDATIONS
# ---------------------------------------------------------------------------

with tab4:
    st.header("Recommendations")

    for _, row in recs.iterrows():
        st.markdown(
            f"""
            <div style='background:#1c1f26;padding:12px;border-radius:8px;
            margin-bottom:10px;border-left:4px solid #4fc3f7'>
            <b>{row['category']} - {row['zone']}</b><br>
            {row['recommendation']}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Distribution")
    fig = px.histogram(recs, x="category", color="severity", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
