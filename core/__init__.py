# core/__init__.py

from .generator import generate_population
from .generator import generate_traffic
from .generator import generate_weather

__version__ = "1.0.0"
__all__ = [
    "generate_population",
    "generate_traffic",
    "generate_weather",
]