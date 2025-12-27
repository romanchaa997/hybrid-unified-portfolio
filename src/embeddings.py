"""Vector embeddings module for skill and portfolio representation.

This module provides functions for generating semantic embeddings of skills,
experience descriptions, and portfolio items using state-of-the-art models.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    batch_size: int = 32
    normalize: bool = True
    device: str = "cpu"


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        pass

    @abstractmethod
    def embed_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        pass


class TransformerEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using transformer models (SentenceTransformers)."""

    def __init__(self, config: EmbeddingConfig):
        """Initialize transformer embedding provider."""
        self.config = config
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(config.model_name, device=config.device)
            logger.info(f"Loaded embedding model: {config.model_name}")
        except ImportError:
            logger.error("sentence-transformers not installed")
            raise

    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        if not texts:
            return np.array([])

        embeddings = self.model.encode(
            texts,
            batch_size=self.config.batch_size,
            normalize_embeddings=self.config.normalize,
            show_progress_bar=False
        )
        return np.array(embeddings, dtype=np.float32)

    def embed_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        if not text or not text.strip():
            return np.zeros(self.config.embedding_dim, dtype=np.float32)

        embedding = self.model.encode(
            text,
            normalize_embeddings=self.config.normalize
        )
        return np.array(embedding, dtype=np.float32)


class SkillEmbedder:
    """Generates skill embeddings with semantic understanding."""

    def __init__(self, provider: EmbeddingProvider):
        """Initialize skill embedder."""
        self.provider = provider

    def embed_skills(self, skills: List[str]) -> Dict[str, np.ndarray]:
        """Generate embeddings for multiple skills."""
        embeddings = self.provider.embed(skills)
        return {skill: emb for skill, emb in zip(skills, embeddings)}

    def embed_skill_groups(self, groups: Dict[str, List[str]]) -> Dict[str, Dict]:
        """Generate embeddings for skill groups with hierarchy."""
        result = {}
        for group_name, skills in groups.items():
            embeddings = self.provider.embed(skills)
            result[group_name] = {
                'skills': skills,
                'embeddings': embeddings,
                'group_embedding': np.mean(embeddings, axis=0)
            }
        return result


class ExperienceEmbedder:
    """Generates experience and project embeddings."""

    def __init__(self, provider: EmbeddingProvider):
        """Initialize experience embedder."""
        self.provider = provider

    def embed_projects(self, projects: List[Dict[str, str]]) -> List[Dict]:
        """Generate embeddings for project descriptions."""
        descriptions = [p.get('description', '') for p in projects]
        embeddings = self.provider.embed(descriptions)

        result = []
        for project, embedding in zip(projects, embeddings):
            result.append({
                'id': project.get('id'),
                'title': project.get('title'),
                'description': project.get('description'),
                'embedding': embedding,
                'metadata': project.get('metadata', {})
            })
        return result

    def embed_experience(self, experiences: List[Dict[str, str]]) -> List[Dict]:
        """Generate embeddings for work experience descriptions."""
        descriptions = [
            f"{e.get('title', '')} at {e.get('company', '')}. {e.get('description', '')}"
            for e in experiences
        ]
        embeddings = self.provider.embed(descriptions)

        result = []
        for experience, embedding in zip(experiences, embeddings):
            result.append({
                'id': experience.get('id'),
                'title': experience.get('title'),
                'company': experience.get('company'),
                'description': experience.get('description'),
                'embedding': embedding,
                'duration': experience.get('duration')
            })
        return result


class SimilarityMatcher:
    """Matches embeddings based on similarity metrics."""

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        if v1.size == 0 or v2.size == 0:
            return 0.0
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10))

    @staticmethod
    def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate Euclidean distance between two vectors."""
        return float(np.linalg.norm(v1 - v2))

    @classmethod
    def find_similar(cls, query: np.ndarray, corpus: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        """Find top-k most similar items in corpus to query."""
        similarities = np.array([cls.cosine_similarity(query, item) for item in corpus])
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(idx, float(similarities[idx])) for idx in top_indices]



# ============== OPTIMIZATIONS ==============

from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

class CachedEmbeddingProvider:
    """Caching wrapper for embedding providers to optimize repeated requests."""
    
    def __init__(self, provider: EmbeddingProvider, cache_size: int = 128):
        """Initialize cached embedding provider."""
        self.provider = provider
        self.cache_size = cache_size
        self._embed_cache = {}
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings with caching."""
        uncached_texts = []
        uncached_indices = []
        results = [None] * len(texts)
        
        # Check cache first
        for idx, text in enumerate(texts):
            text_hash = hash(text)
            if text_hash in self._embed_cache:
                results[idx] = self._embed_cache[text_hash]
            else:
                uncached_texts.append(text)
                uncached_indices.append(idx)
        
        # Embed uncached texts
        if uncached_texts:
            embeddings = self.provider.embed(uncached_texts)
            for idx, emb in zip(uncached_indices, embeddings):
                text_hash = hash(uncached_texts[uncached_indices.index(idx)])
                self._embed_cache[text_hash] = emb
                results[idx] = emb
                
                # Limit cache size
                if len(self._embed_cache) > self.cache_size:
                    self._embed_cache.pop(next(iter(self._embed_cache)))
        
        return np.array(results)


class AsyncEmbeddingProvider:
    """Async wrapper for embedding providers."""
    
    def __init__(self, provider: EmbeddingProvider, max_workers: int = 4):
        """Initialize async embedding provider."""
        self.provider = provider
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def embed_async(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.provider.embed, texts)
    
    async def embed_batch_async(self, text_batches: List[List[str]], batch_size: int = 32) -> List[np.ndarray]:
        """Process multiple batches asynchronously."""
        tasks = [self.embed_async(batch) for batch in text_batches]
        return await asyncio.gather(*tasks)


def batch_embeddings(texts: List[str], batch_size: int = 32) -> List[List[str]]:
    """Split texts into batches for efficient processing."""
    return [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
