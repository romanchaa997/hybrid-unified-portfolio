"""Hybrid search engine for portfolio discovery.

Combines vector semantic search with keyword/BM25 search for comprehensive
portfolio matching and discovery.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from .embeddings import SimilarityMatcher

logger = logging.getLogger(__name__)


class SearchMode(str, Enum):
    """Search mode enumeration."""
    VECTOR = "vector"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


@dataclass
class SearchResult:
    """Search result item."""
    item_id: str
    title: str
    description: str
    score: float
    match_type: str
    metadata: Dict = None


class KeywordSearchEngine:
    """Keyword-based search using BM25 scoring."""

    def __init__(self, documents: List[Dict] = None):
        """Initialize keyword search engine."""
        self.documents = documents or []
        self.index = {}
        self._build_index()

    def _build_index(self):
        """Build inverted index from documents."""
        self.index = {}
        for doc_id, doc in enumerate(self.documents):
            text = f"{doc.get('title', '')} {doc.get('description', '')}".lower()
            words = text.split()
            for word in set(words):
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append(doc_id)

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search documents using keyword matching."""
        query_words = query.lower().split()
        scores = {}

        for word in query_words:
            if word in self.index:
                for doc_id in self.index[word]:
                    scores[doc_id] = scores.get(doc_id, 0) + 1

        if not scores:
            return []

        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = []

        for doc_id, score in sorted_docs:
            doc = self.documents[doc_id]
            results.append(SearchResult(
                item_id=doc.get('id', str(doc_id)),
                title=doc.get('title', ''),
                description=doc.get('description', ''),
                score=float(score) / len(query_words),
                match_type="keyword",
                metadata=doc.get('metadata')
            ))

        return results


class VectorSearchEngine:
    """Vector-based semantic search engine."""

    def __init__(self, embeddings: np.ndarray = None, documents: List[Dict] = None):
        """Initialize vector search engine."""
        self.embeddings = embeddings or np.array([])
        self.documents = documents or []
        self.matcher = SimilarityMatcher()

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """Search documents using vector similarity."""
        if self.embeddings.size == 0:
            return []

        similarities = self.matcher.find_similar(query_embedding, self.embeddings, top_k)
        results = []

        for idx, score in similarities:
            doc = self.documents[idx]
            results.append(SearchResult(
                item_id=doc.get('id', str(idx)),
                title=doc.get('title', ''),
                description=doc.get('description', ''),
                score=float(score),
                match_type="vector",
                metadata=doc.get('metadata')
            ))

        return results


class HybridSearchEngine:
    """Hybrid search combining vector and keyword search."""

    def __init__(self, documents: List[Dict], embeddings: np.ndarray = None):
        """Initialize hybrid search engine."""
        self.documents = documents
        self.keyword_engine = KeywordSearchEngine(documents)
        self.vector_engine = VectorSearchEngine(embeddings, documents) if embeddings is not None else None

    def search(
        self,
        query: str,
        query_embedding: np.ndarray = None,
        mode: SearchMode = SearchMode.HYBRID,
        top_k: int = 5,
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4
    ) -> List[SearchResult]:
        """Perform hybrid search combining multiple strategies."""
        results = []

        if mode in [SearchMode.VECTOR, SearchMode.HYBRID] and query_embedding is not None:
            vector_results = self.vector_engine.search(query_embedding, top_k)
            results.extend(vector_results)

        if mode in [SearchMode.KEYWORD, SearchMode.HYBRID]:
            keyword_results = self.keyword_engine.search(query, top_k)
            results.extend(keyword_results)

        if mode == SearchMode.HYBRID and query_embedding is not None:
            return self._merge_results(results, vector_weight, keyword_weight, top_k)

        return results[:top_k]

    def _merge_results(
        self,
        results: List[SearchResult],
        vector_weight: float,
        keyword_weight: float,
        top_k: int
    ) -> List[SearchResult]:
        """Merge and re-rank hybrid search results."""
        score_map = {}

        for result in results:
            if result.item_id not in score_map:
                score_map[result.item_id] = {"result": result, "scores": []}
            score_map[result.item_id]["scores"].append((result.match_type, result.score))

        merged_results = []
        for item_id, data in score_map.items():
            base_result = data["result"]
            final_score = 0.0

            for match_type, score in data["scores"]:
                if match_type == "vector":
                    final_score += score * vector_weight
                elif match_type == "keyword":
                    final_score += score * keyword_weight

            base_result.score = final_score
            merged_results.append(base_result)

        return sorted(merged_results, key=lambda x: x.score, reverse=True)[:top_k]


class PortfolioSearchService:
    """High-level portfolio search service."""

    def __init__(self, documents: List[Dict], embeddings: np.ndarray = None):
        """Initialize portfolio search service."""
        self.engine = HybridSearchEngine(documents, embeddings)

    def search_portfolios(
        self,
        query: str,
        query_embedding: np.ndarray = None,
        search_mode: str = "hybrid",
        top_k: int = 10
    ) -> List[SearchResult]:
        """Search portfolios with given query."""
        try:
            mode = SearchMode(search_mode)
            return self.engine.search(
                query,
                query_embedding,
                mode,
                top_k
            )
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
