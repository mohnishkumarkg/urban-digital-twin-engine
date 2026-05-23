from __future__ import annotations
import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "config.json"

def load_config(path: str | Path = _CONFIG_PATH) -> dict:
    with open(path) as f:
        return json.load(f)

def get_zones(config: dict) -> list[str]:
    n = input(f"How many zones? (default {config['num_zones']}): ").strip()
    n = int(n) if n else config["num_zones"]
    zones = [input(f"Zone {i+1} name: ").strip() for i in range(n)]
    return zones