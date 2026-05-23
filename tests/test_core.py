from __future__ import annotations

import pandas as pd

from core.generator import (
    generate_population,
    generate_traffic,
    generate_weather,
)


# ---------------------------------------------------------
# Population Tests
# ---------------------------------------------------------

def test_generate_population():

    zones = ["North", "South", "East"]

    df = generate_population(zones)

    assert not df.empty
    assert "population" in df.columns
    assert len(df) == 3


# ---------------------------------------------------------
# Traffic Tests
# ---------------------------------------------------------

def test_generate_traffic():

    zones = ["North", "South"]

    df = generate_traffic(
        zones=zones,
        days=2
    )

    assert not df.empty
    assert "traffic" in df.columns

    expected_rows = 2 * 24 * len(zones)

    assert len(df) == expected_rows


# ---------------------------------------------------------
# Weather Tests
# ---------------------------------------------------------

def test_generate_weather():

    df = generate_weather(days=10)

    assert not df.empty
    assert "temperature" in df.columns
    assert "humidity" in df.columns

    assert len(df) == 10