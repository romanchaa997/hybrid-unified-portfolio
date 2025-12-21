"""Core embeddings module for vector representation of professional profiles."""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    embedding_dim: int = 768
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 32
    normalize: bool = True


class EmbeddingGenerator:
    """Generate vector embeddings for professional content."""

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """Initialize embedding generator.
        
        Args:
            config: Configuration for embeddings.
        """
        self.config = config or EmbeddingConfig()
        self.model = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.config.model_name)
            logger.info(f"Loaded model: {self.config.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using fallback embeddings.")
            self.model = None

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into vector embeddings.
        
        Args:
            texts: List of text strings to encode.
            
        Returns:
            numpy array of shape (len(texts), embedding_dim).
        """
        if self.model is None:
            return self._fallback_encode(texts)
        
        embeddings = self.model.encode(
            texts,
            batch_size=self.config.batch_size,
            normalize_embeddings=self.config.normalize
        )
        return embeddings

    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Fallback encoding using simple approach.
        
        Args:
            texts: List of text strings.
            
        Returns:
            numpy array of embeddings.
        """
        embeddings = []
        for text in texts:
            hash_val = hash(text) % (2**32)
            np.random.seed(hash_val)
            embedding = np.random.randn(self.config.embedding_dim)
            if self.config.normalize:
                embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        return np.array(embeddings)

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings.
        
        Args:
            embedding1: First embedding vector.
            embedding2: Second embedding vector.
            
        Returns:
            Cosine similarity score.
        """
        if len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0
        
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))

    def batch_similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """Calculate pairwise cosine similarities.
        
        Args:
            embeddings1: Array of shape (n, embedding_dim).
            embeddings2: Array of shape (m, embedding_dim).
            
        Returns:
            Similarity matrix of shape (n, m).
        """
        norm1 = np.linalg.norm(embeddings1, axis=1, keepdims=True)
        norm2 = np.linalg.norm(embeddings2, axis=1, keepdims=True)
        
        norm1 = np.where(norm1 == 0, 1, norm1)
        norm2 = np.where(norm2 == 0, 1, norm2)
        
        embeddings1_norm = embeddings1 / norm1
        embeddings2_norm = embeddings2 / norm2
        
        return np.dot(embeddings1_norm, embeddings2_norm.T)


class ProfileEmbedder:
    """Embed professional profile data into vectors."""

    def __init__(self, embedding_generator: Optional[EmbeddingGenerator] = None):
        """Initialize profile embedder.
        
        Args:
            embedding_generator: Embedding generator instance.
        """
        self.generator = embedding_generator or EmbeddingGenerator()

    def embed_skills(self, skills: List[str]) -> np.ndarray:
        """Embed a list of skills.
        
        Args:
            skills: List of skill names.
            
        Returns:
            Embedding vectors for skills.
        """
        if not skills:
            return np.array([])
        return self.generator.encode(skills)

    def embed_experience(self, experiences: List[Dict[str, str]]) -> np.ndarray:
        """Embed professional experience descriptions.
        
        Args:
            experiences: List of experience dictionaries.
            
        Returns:
            Embedding vectors for experiences.
        """
        descriptions = [
            f"{exp.get('title', '')} {exp.get('description', '')}".strip()
            for exp in experiences
        ]
        if not descriptions:
            return np.array([])
        return self.generator.encode(descriptions)

    def embed_profile(self, profile: Dict) -> Dict[str, np.ndarray]:
        """Embed entire profile data.
        
        Args:
            profile: Dictionary with profile fields.
            
        Returns:
            Dictionary with embeddings for each component.
        """
        embeddings = {}
        
        if 'skills' in profile:
            embeddings['skills'] = self.embed_skills(profile['skills'])
        
        if 'experience' in profile:
            embeddings['experience'] = self.embed_experience(profile['experience'])
        
        if 'summary' in profile:
            embeddings['summary'] = self.generator.encode([profile['summary']])[0]
        
        return embeddings
