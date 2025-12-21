"""Semantic search engine for portfolio discovery."""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

from ..embeddings import EmbeddingGenerator, ProfileEmbedder

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with score and metadata."""
    profile_id: str
    similarity_score: float
    profile_data: Dict
    
    def __lt__(self, other):
        return self.similarity_score < other.similarity_score


class SemanticSearchEngine:
    """Search engine for finding similar profiles."""

    def __init__(self, embedding_generator: Optional[EmbeddingGenerator] = None):
        """Initialize search engine.
        
        Args:
            embedding_generator: Embedding generator instance.
        """
        self.embeddings = EmbeddingGenerator() if embedding_generator is None else embedding_generator
        self.embedder = ProfileEmbedder(self.embeddings)
        self.profile_store = {}  # Dict to store profiles by ID
        self.embedding_store = {}  # Dict to store embeddings by profile ID

    def add_profile(self, profile_id: str, profile: Dict) -> None:
        """Add a profile to the search engine.
        
        Args:
            profile_id: Unique identifier for profile.
            profile: Dictionary containing profile data.
        """
        self.profile_store[profile_id] = profile
        # Combine all text from profile
        profile_text = self._combine_profile_text(profile)
        self.embedding_store[profile_id] = self.embeddings.encode([profile_text])[0]
        logger.info(f"Added profile {profile_id} to search engine")

    def search(self, query: str, top_k: int = 10, threshold: float = 0.0) -> List[SearchResult]:
        """Search for similar profiles.
        
        Args:
            query: Search query text.
            top_k: Number of top results to return.
            threshold: Minimum similarity score threshold.
            
        Returns:
            List of SearchResult objects, sorted by similarity.
        """
        query_embedding = self.embeddings.encode([query])[0]
        results = []
        
        for profile_id, stored_embedding in self.embedding_store.items():
            score = self.embeddings.similarity(query_embedding, stored_embedding)
            
            if score >= threshold:
                results.append(SearchResult(
                    profile_id=profile_id,
                    similarity_score=float(score),
                    profile_data=self.profile_store[profile_id]
                ))
        
        # Sort by similarity score descending
        results.sort(reverse=True, key=lambda x: x.similarity_score)
        return results[:top_k]

    def search_by_skill(self, skill: str, top_k: int = 10) -> List[SearchResult]:
        """Search profiles by specific skill.
        
        Args:
            skill: Skill to search for.
            top_k: Number of results to return.
            
        Returns:
            List of profiles containing the skill.
        """
        query = f"expert in {skill}"
        return self.search(query, top_k=top_k)

    def batch_search(self, queries: List[str], top_k: int = 10) -> Dict[str, List[SearchResult]]:
        """Perform multiple searches.
        
        Args:
            queries: List of search queries.
            top_k: Number of top results per query.
            
        Returns:
            Dictionary mapping queries to results.
        """
        results = {}
        for query in queries:
            results[query] = self.search(query, top_k=top_k)
        return results

    def recommend_matches(self, profile_id: str, top_k: int = 5) -> List[SearchResult]:
        """Find profiles similar to a given profile.
        
        Args:
            profile_id: Profile to find matches for.
            top_k: Number of matches to return.
            
        Returns:
            List of similar profiles.
        """
        if profile_id not in self.profile_store:
            logger.warning(f"Profile {profile_id} not found")
            return []
        
        profile_embedding = self.embedding_store[profile_id]
        results = []
        
        for other_id, stored_embedding in self.embedding_store.items():
            if other_id != profile_id:
                score = self.embeddings.similarity(profile_embedding, stored_embedding)
                results.append(SearchResult(
                    profile_id=other_id,
                    similarity_score=float(score),
                    profile_data=self.profile_store[other_id]
                ))
        
        results.sort(reverse=True, key=lambda x: x.similarity_score)
        return results[:top_k]

    def _combine_profile_text(self, profile: Dict) -> str:
        """Combine all text fields from profile.
        
        Args:
            profile: Profile dictionary.
            
        Returns:
            Combined text.
        """
        texts = []
        for key in ['summary', 'headline', 'title', 'description']:
            if key in profile:
                value = profile[key]
                if isinstance(value, str):
                    texts.append(value)
                elif isinstance(value, list):
                    texts.extend(str(v) for v in value)
        
        return ' '.join(texts) if texts else ''

    def clear(self) -> None:
        """Clear all stored profiles and embeddings."""
        self.profile_store.clear()
        self.embedding_store.clear()
        logger.info("Cleared search engine")

    def get_statistics(self) -> Dict[str, int]:
        """Get search engine statistics.
        
        Returns:
            Dictionary with statistics.
        """
        return {
            'num_profiles': len(self.profile_store),
            'num_embeddings': len(self.embedding_store),
        }
