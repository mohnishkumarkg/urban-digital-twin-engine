import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.loader import load_config
from core         import generate_population, generate_traffic, generate_weather
from analytics    import (
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
    /* Main background */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
 
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #1c1f26;
        border: 1px solid #2e3140;
        border-radius: 10px;
        padding: 16px;
    }
 
    /* Section headers */
    h2 { color: #4fc3f7; border-bottom: 1px solid #2e3140; padding-bottom: 8px; }
    h3 { color: #81d4fa; }
 
    /* Severity badges */
    .badge-critical { color: #ff5252; font-weight: bold; }
    .badge-warning  { color: #ffd740; font-weight: bold; }
    .badge-normal   { color: #69f0ae; font-weight: bold; }
 
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #13161e; }
</style>
""", unsafe_allow_html=True)
 
# ---------------------------------------------------------------------------
# SIDEBAR — INPUTS
# ---------------------------------------------------------------------------
 
st.sidebar.image("https://img.icons8.com/fluency/96/city.png", width=60)
st.sidebar.title("🏙️ Urban Digital Twin")
st.sidebar.markdown("---")
 
config = load_config()
 
st.sidebar.header("🗺️ Zone Configuration")
n = st.sidebar.number_input(
    "Number of Zones",
    min_value=1, max_value=20,
    value=config["num_zones"]
)
ZONES = [
    st.sidebar.text_input(f"Zone {i+1}", value=f"Zone {i+1}")
    for i in range(n)
]
 
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Simulation Settings")
days = st.sidebar.slider(
    "Simulation Days",
    min_value=1, max_value=365,
    value=config["simulation_days"]
)
 
st.sidebar.markdown("---")
st.sidebar.header("🎭 Scenario")
scenario = st.sidebar.selectbox(
    "Choose Scenario",
    options=config["default_scenarios"]
)
 
festival_zones = None
if scenario == "Festival":
    festival_zones = st.sidebar.multiselect(
        "Festival Zones",
        options=ZONES,
        default=[ZONES[0]] if ZONES else []
    )
 
st.sidebar.markdown("---")
run = st.sidebar.button("▶ Run Simulation", use_container_width=True)
 
# ---------------------------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------------------------
 
st.title("🏙️ Urban Digital Twin & Decision Intelligence Engine")
st.caption(f"City: **{config['default_city']}**  |  Scenario: **{scenario}**  |  Days: **{days}**")
st.markdown("---")
 
if not run:
    st.info("👈 Configure your simulation in the sidebar and click **Run Simulation** to begin.")
    st.stop()
 
# ---------------------------------------------------------------------------
# GENERATE DATA
# ---------------------------------------------------------------------------
 
with st.spinner("Generating city data..."):
    pop_df     = generate_population(ZONES, **config["population"])
    traffic_df = generate_traffic(ZONES, days=days, **config["traffic"])
    weather_df = generate_weather(days=days,         **config["weather"])
 
    result     = run_intelligence(
        scenario, ZONES, traffic_df, weather_df, pop_df, festival_zones
    )
 
    mod_traffic = result["traffic"]
    mod_weather = result["weather"]
    mod_pop     = result["population"]
    recs        = result["recommendations"]
 
# ---------------------------------------------------------------------------
# SCENARIO BANNER
# ---------------------------------------------------------------------------
 
scenario_colors = {
    "Baseline": "#69f0ae",
    "Heatwave": "#ff5252",
    "Festival": "#ffd740",
}
color = scenario_colors.get(scenario, "#4fc3f7")
st.markdown(
    f"""<div style='background:{color}22; border-left:4px solid {color};
    padding:12px 20px; border-radius:6px; margin-bottom:20px;'>
    <b style='color:{color};'>{scenario} Scenario Active</b><br>
    <span style='color:#ccc;'>{result['description']}</span>
    </div>""",
    unsafe_allow_html=True
)
 
# ---------------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------------
 
tab1, tab2, tab3, tab4 = st.tabs([
    "👥 Population",
    "🚗 Traffic",
    "🌤️ Weather",
    "🧠 Recommendations",
])
 
 
# ── TAB 1 — POPULATION ──────────────────────────────────────────────────────
 
with tab1:
    st.header("Population Overview")
 
    summary = population_summary(mod_pop)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Population",   f"{summary['total_population'][0]:,}")
    c2.metric("Average per Zone",   f"{summary['average_population'][0]:,.0f}")
    c3.metric("Highest Zone",       f"{top_zone_population(mod_pop)['Zone']} — {top_zone_population(mod_pop)['Population']:,}")
    c4.metric("Lowest Zone",        f"{bottom_zone_population(mod_pop)['Zone']} — {bottom_zone_population(mod_pop)['Population']:,}")
 
    st.markdown("---")
    col1, col2 = st.columns(2)
 
    with col1:
        st.subheader("Population per Zone")
        fig = px.bar(
            mod_pop.sort_values("Population", ascending=True),
            x="Population", y="Zone",
            orientation="h",
            color="Population",
            color_continuous_scale="Blues",
            template="plotly_dark",
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
 
    with col2:
        st.subheader("Population Share")
        fig = px.pie(
            mod_pop, values="Population", names="Zone",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            template="plotly_dark",
            hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Raw Data")
    st.dataframe(mod_pop, use_container_width=True)
 
 
# ── TAB 2 — TRAFFIC ─────────────────────────────────────────────────────────
 
with tab2:
    st.header("Traffic Analysis")
 
    t_summary = traffic_summary(mod_traffic)
    peak_h    = peak_traffic_hour(mod_traffic)
    busy      = busiest_zone(mod_traffic)
    quiet     = quietest_zone(mod_traffic)
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Busiest Zone",  busy)
    c2.metric("Quietest Zone", quiet)
    c3.metric("Zones Tracked", len(ZONES))
 
    st.markdown("---")
    col1, col2 = st.columns(2)
 
    with col1:
        st.subheader("Average Traffic per Zone")
        fig = px.bar(
            t_summary.sort_values("avg_traffic", ascending=True),
            x="avg_traffic", y="Zone",
            orientation="h",
            color="avg_traffic",
            color_continuous_scale="Oranges",
            template="plotly_dark",
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
 
    with col2:
        st.subheader("Peak Traffic Hour per Zone")
        fig = px.bar(
            peak_h,
            x="Zone", y="peak_hour",
            color="peak_avg_traffic",
            color_continuous_scale="Reds",
            template="plotly_dark",
            labels={"peak_hour": "Hour of Day"},
        )
        st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Hourly Traffic Over Time")
    zone_filter = st.multiselect(
        "Filter Zones", options=ZONES, default=ZONES[:2]
    )
    filtered = mod_traffic[mod_traffic["Zone"].isin(zone_filter)]
    fig = px.line(
        filtered, x="datetime", y="traffic", color="Zone",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Weekend vs Weekday Traffic")
    ww = weekend_vs_weekday(mod_traffic)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Weekday", x=ww["Zone"], y=ww["weekday_avg"], marker_color="#4fc3f7"))
    fig.add_trace(go.Bar(name="Weekend", x=ww["Zone"], y=ww["weekend_avg"], marker_color="#ff8a65"))
    fig.update_layout(barmode="group", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
 
 
# ── TAB 3 — WEATHER ─────────────────────────────────────────────────────────
 
with tab3:
    st.header("Weather Analysis")
 
    w_summary = weather_summary(mod_weather)
    hot       = hottest_day(mod_weather)
    cold      = coldest_day(mod_weather)
    above30   = days_above_temp(mod_weather, 30.0)
    below5    = days_below_temp(mod_weather, 5.0)
 
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Temperature",  f"{w_summary['avg_temperature'][0]}°C")
    c2.metric("Hottest Day",      f"{hot['temperature']}°C",  str(hot['date'])[:10])
    c3.metric("Coldest Day",      f"{cold['temperature']}°C", str(cold['date'])[:10])
    c4.metric("Days Above 30°C",  above30)
 
    st.markdown("---")
    col1, col2 = st.columns(2)
 
    with col1:
        st.subheader("Temperature Over Time")
        fig = px.line(
            mod_weather, x="date", y="temperature",
            template="plotly_dark",
            color_discrete_sequence=["#ff7043"],
        )
        fig.add_hline(y=30, line_dash="dash", line_color="#ff5252",
                      annotation_text="Heat threshold")
        st.plotly_chart(fig, use_container_width=True)
 
    with col2:
        st.subheader("Humidity Over Time")
        fig = px.line(
            mod_weather, x="date", y="humidity",
            template="plotly_dark",
            color_discrete_sequence=["#4fc3f7"],
        )
        fig.add_hline(y=80, line_dash="dash", line_color="#ffd740",
                      annotation_text="Humidity threshold")
        st.plotly_chart(fig, use_container_width=True)
 
    st.subheader("Temperature vs Humidity")
    fig = px.scatter(
        mod_weather, x="temperature", y="humidity",
        color="temperature",
        color_continuous_scale="RdBu_r",
        template="plotly_dark",
        hover_data=["date"],
    )
    st.plotly_chart(fig, use_container_width=True)
 
 
# ── TAB 4 — RECOMMENDATIONS ─────────────────────────────────────────────────
 
with tab4:
    st.header("Decision Intelligence Recommendations")
 
    # Summary counts
    critical = len(recs[recs["severity"].str.contains("Critical")])
    warning  = len(recs[recs["severity"].str.contains("Warning")])
    normal   = len(recs[recs["severity"].str.contains("Normal")])
 
    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 Critical", critical)
    c2.metric("🟡 Warning",  warning)
    c3.metric("🟢 Normal",   normal)
 
    st.markdown("---")
 
    # Filter by category
    categories = ["All"] + list(recs["category"].unique())
    cat_filter = st.selectbox("Filter by Category", options=categories)
 
    filtered_recs = recs if cat_filter == "All" else recs[recs["category"] == cat_filter]
 
    # Display each recommendation as a card
    for _, row in filtered_recs.iterrows():
        sev = row["severity"]
        if "Critical" in sev:
            color = "#ff5252"
        elif "Warning" in sev:
            color = "#ffd740"
        else:
            color = "#69f0ae"
 
        st.markdown(
            f"""<div style='background:#1c1f26; border-left:4px solid {color};
            padding:14px 20px; border-radius:6px; margin-bottom:10px;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                <span style='color:#888; font-size:0.8em;'>
                    {row['category']} — {row['zone']}
                </span>
                <span style='color:{color}; font-size:0.85em; font-weight:bold;'>
                    {row['severity']}
                </span>
            </div>
            <span style='color:#e0e0e0;'>{row['recommendation']}</span>
            </div>""",
            unsafe_allow_html=True
        )
 
    st.markdown("---")
    st.subheader("Recommendations Breakdown")
    fig = px.histogram(
        recs, x="category", color="severity",
        color_discrete_map={
            "🔴 Critical": "#ff5252",
            "🟡 Warning":  "#ffd740",
            "🟢 Normal":   "#69f0ae",
        },
        template="plotly_dark",
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)
