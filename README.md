# UDT-DIE Urban Decision Support Platform

This project is a synthetic city decision-support platform built with Python, NumPy, Pandas, and Streamlit. It simulates urban systems including transportation, environment, energy, demographics, and infrastructure to evaluate policy scenarios and generate actionable recommendations.

## Features
- Synthetic multi-city generation with zone-level attributes
- Scenario library for natural events, human events, and policy interventions
- Time-series simulation engine for comparing baseline and intervention outcomes
- Composite risk scoring combining pollution, congestion, and energy stress
- Zone stability and volatility analysis
- Investment prioritization and recommendation generation
- Multi-city benchmarking and policy tradeoff analysis
- Streamlit dashboard with scenario comparison, heatmaps, and CSV export
- Professional outputs: datasets, pivot tables, correlation matrices, executive summaries

## Installation
1. Create or activate a Python environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run main.py
```

Or

```bash
python main.py
```

## Structure
- `core/` - Core simulation logic (data generation, simulation)
- `scenarios/` - Scenario definitions and modifiers
- `analytics/` - Risk scoring, stability, ranking
- `intelligence/` - Advanced analytics (benchmarking, tradeoffs, business questions)
- `reports/` - Output utilities (CSV export, summaries, heatmaps)
- `app/` - Streamlit application
- `config/` - Configuration files (JSON)
- `tests/` - Unit tests
- `outputs/` - Generated files and reports
- `main.py` - Entry point

## Configuration
Edit `config/config.json` to set defaults for city, scenarios, simulation days, etc.

## Testing
Run tests with:

```bash
python -m unittest tests/test_core.py
```

## Deployment
Deploy to Streamlit Community Cloud by pushing to GitHub and connecting the repo.

## Business Questions Answered
- How will a new metro corridor affect congestion and pollution?
- Which neighborhoods are most vulnerable during heatwaves?
- What is the trade-off between energy savings and public comfort?
- Which zones should receive investment first?
- How stable is each zone under repeated stress events?
- Which zones should receive the first ₹100 crore of infrastructure investment?
- Which policy yields the largest pollution reduction per unit cost?
- Which zones remain unstable despite intervention?
- What are the top three recommendations for the next quarter?

This platform aligns with digital twin initiatives from NASA, Siemens, IBM, and World Bank, providing a virtual laboratory for urban planning and policy analysis.