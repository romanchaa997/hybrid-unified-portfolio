"""Skill extraction module for analyzing professional profiles."""

import re
from typing import List, Set, Dict, Optional
from dataclasses import dataclass
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# Common technical skills database
COMMON_TECHNICAL_SKILLS = {
    # Languages
    'python', 'javascript', 'java', 'c++', 'c#', 'typescript', 'golang', 'rust',
    'ruby', 'php', 'kotlin', 'swift', 'objective-c', 'scala', 'r', 'matlab',
    # Web frameworks
    'react', 'angular', 'vue', 'express', 'django', 'flask', 'fastapi',
    'spring', 'asp.net', 'nextjs', 'nuxtjs', 'laravel', 'rails',
    # Databases
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
    'dynamodb', 'firestore', 'oracle', 'sql', 'nosql', 'sqlite',
    # Cloud
    'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'terraform',
    # Data science
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
    'spark', 'hadoop', 'tableau', 'powerbi',
    # Other tools
    'git', 'linux', 'windows', 'macos', 'ci/cd', 'jenkins', 'gitlab',
    'github', 'bitbucket', 'jira', 'rest', 'graphql', 'grpc'
}

# Common soft skills
COMMON_SOFT_SKILLS = {
    'communication', 'leadership', 'teamwork', 'problem-solving',
    'critical thinking', 'collaboration', 'time management',
    'project management', 'negotiation', 'presentation', 'analysis',
    'strategic thinking', 'creativity', 'adaptability'
}


@dataclass
class SkillExtractionResult:
    """Result of skill extraction."""
    technical_skills: Set[str]
    soft_skills: Set[str]
    all_skills: Set[str]
    skill_frequencies: Dict[str, int]


class SkillExtractor:
    """Extract skills from professional text."""

    def __init__(self):
        """Initialize skill extractor."""
        self.technical_skills = COMMON_TECHNICAL_SKILLS
        self.soft_skills = COMMON_SOFT_SKILLS

    def extract(self, text: str) -> SkillExtractionResult:
        """Extract skills from text.
        
        Args:
            text: Text to analyze for skills.
            
        Returns:
            SkillExtractionResult with extracted skills.
        """
        text_lower = text.lower()
        
        # Extract technical skills
        technical = self._find_technical_skills(text_lower)
        
        # Extract soft skills
        soft = self._find_soft_skills(text_lower)
        
        # Combine all skills
        all_skills = technical | soft
        
        # Calculate frequencies
        frequencies = self._calculate_frequencies(text_lower, all_skills)
        
        return SkillExtractionResult(
            technical_skills=technical,
            soft_skills=soft,
            all_skills=all_skills,
            skill_frequencies=frequencies
        )

    def _find_technical_skills(self, text: str) -> Set[str]:
        """Find technical skills in text.
        
        Args:
            text: Lowercased text to search.
            
        Returns:
            Set of found technical skills.
        """
        found = set()
        for skill in self.technical_skills:
            if self._skill_in_text(text, skill):
                found.add(skill)
        return found

    def _find_soft_skills(self, text: str) -> Set[str]:
        """Find soft skills in text.
        
        Args:
            text: Lowercased text to search.
            
        Returns:
            Set of found soft skills.
        """
        found = set()
        for skill in self.soft_skills:
            if self._skill_in_text(text, skill):
                found.add(skill)
        return found

    def _skill_in_text(self, text: str, skill: str) -> bool:
        """Check if skill exists in text with word boundaries.
        
        Args:
            text: Text to search.
            skill: Skill to look for.
            
        Returns:
            True if skill found with proper boundaries.
        """
        # Handle special cases with slashes
        if '/' in skill:
            pattern = skill.replace('/', r'\s*/?\s*')
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
        
        return bool(re.search(pattern, text, re.IGNORECASE))

    def _calculate_frequencies(self, text: str, skills: Set[str]) -> Dict[str, int]:
        """Calculate skill mention frequencies.
        
        Args:
            text: Text to search.
            skills: Skills to count.
            
        Returns:
            Dictionary of skill frequencies.
        """
        frequencies = {}
        for skill in skills:
            pattern = skill.replace('/', r'\s*/?\s*') if '/' in skill else skill
            matches = len(re.findall(r'\b' + re.escape(pattern) + r'\b', text, re.IGNORECASE))
            if matches > 0:
                frequencies[skill] = matches
        
        return frequencies

    def add_custom_skill(self, skill: str, skill_type: str = 'technical') -> None:
        """Add custom skill to the database.
        
        Args:
            skill: Skill to add.
            skill_type: 'technical' or 'soft'.
        """
        skill_lower = skill.lower()
        if skill_type == 'technical':
            self.technical_skills.add(skill_lower)
        elif skill_type == 'soft':
            self.soft_skills.add(skill_lower)

    def extract_from_profile(self, profile: Dict) -> Dict[str, SkillExtractionResult]:
        """Extract skills from entire profile.
        
        Args:
            profile: Dictionary with profile text fields.
            
        Returns:
            Dictionary with extraction results for each field.
        """
        results = {}
        for field in ['summary', 'experience', 'education']:
            if field in profile:
                text = profile[field] if isinstance(profile[field], str) else ' '.join(str(x) for x in profile[field])
                results[field] = self.extract(text)
        
        return results
