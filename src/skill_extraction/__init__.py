"""Skill extraction module for professional profiles."""

from .extractor import (
    SkillExtractor,
    SkillExtractionResult,
    COMMON_TECHNICAL_SKILLS,
    COMMON_SOFT_SKILLS,
)

__all__ = [
    "SkillExtractor",
    "SkillExtractionResult",
    "COMMON_TECHNICAL_SKILLS",
    "COMMON_SOFT_SKILLS",
]
