"""Hybrid Unified Portfolio System - Core modules."""

__version__ = "0.1.0"
__author__ = "Roman Chaa"
__email__ = "romanchaa997@gmail.com"

from . import embeddings
from . import skill_extraction

__all__ = [
    "embeddings",
    "skill_extraction",
    "__version__",
    "__author__",
    "__email__",
]
