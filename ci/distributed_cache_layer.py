"""Distributed Cache Layer for multi-node high-performance caching."""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    ttl: Optional[int] = None  # Time to live in seconds
    hit_count: int = 0
    access_count: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return (datetime.now() - self.created_at).seconds > self.ttl


class DistributedCacheNode:
    """A single cache node in the distributed system."""

    def __init__(self, node_id: str, max_size: int = 10000):
        self.node_id = node_id
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            entry.last_accessed = datetime.now()
            entry.hit_count += 1
            self.stats["hits"] += 1
            return entry.value
        self.stats["misses"] += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in cache."""
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        entry = CacheEntry(key=key, value=value, ttl=ttl)
        self.cache[key] = entry
        self.cache.move_to_end(key)
        return True

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self.cache:
            lru_key = next(iter(self.cache))
            del self.cache[lru_key]
            self.stats["evictions"] += 1

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        return {
            "node_id": self.node_id,
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
            **self.stats
        }


class DistributedCacheLayer:
    """Distributed caching layer with multi-node support."""

    def __init__(self, name: str = "DistCache-001", num_nodes: int = 4):
        self.name = name
        self.nodes: Dict[str, DistributedCacheNode] = {}
        self.replication_factor = 2
        self.consistency_level = "eventual"  # or "strong"
        self._create_nodes(num_nodes)
        logger.info(f"Initialized {self.name} with {num_nodes} nodes")

    def _create_nodes(self, num_nodes: int) -> None:
        """Create cache nodes."""
        for i in range(num_nodes):
            node_id = f"cache-node-{i}"
            self.nodes[node_id] = DistributedCacheNode(node_id)

    def _get_node_for_key(self, key: str) -> str:
        """Determine which node stores the key using consistent hashing."""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        node_index = hash_value % len(self.nodes)
        return list(self.nodes.keys())[node_index]

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from distributed cache."""
        node_id = self._get_node_for_key(key)
        node = self.nodes[node_id]
        return await node.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in distributed cache with replication."""
        node_id = self._get_node_for_key(key)
        node = self.nodes[node_id]
        await node.set(key, value, ttl)
        
        # Replicate to other nodes
        for i in range(1, self.replication_factor):
            replica_index = (list(self.nodes.keys()).index(node_id) + i) % len(self.nodes)
            replica_node = list(self.nodes.values())[replica_index]
            await replica_node.set(key, value, ttl)
        
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from distributed cache."""
        node_id = self._get_node_for_key(key)
        if key in self.nodes[node_id].cache:
            del self.nodes[node_id].cache[key]
        return True

    async def bulk_set(self, items: Dict[str, Any], ttl: Optional[int] = None) -> int:
        """Set multiple items in cache."""
        count = 0
        for key, value in items.items():
            if await self.set(key, value, ttl):
                count += 1
        return count

    async def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        import re
        regex = re.compile(pattern)
        count = 0
        for node in self.nodes.values():
            keys_to_delete = [k for k in node.cache.keys() if regex.match(k)]
            for key in keys_to_delete:
                del node.cache[key]
                count += 1
        return count

    def get_cluster_stats(self) -> Dict:
        """Get statistics for the entire cache cluster."""
        node_stats = [node.get_stats() for node in self.nodes.values()]
        total_hits = sum(s["hits"] for s in node_stats)
        total_misses = sum(s["misses"] for s in node_stats)
        total_size = sum(s["size"] for s in node_stats)
        
        return {
            "cluster_name": self.name,
            "nodes": len(self.nodes),
            "total_size": total_size,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "cluster_hit_rate": total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0,
            "node_stats": node_stats
        }


if __name__ == "__main__":
    async def main():
        cache = DistributedCacheLayer("MainCache", 4)
        
        # Set values
        await cache.set("user:1", {"name": "Alice", "role": "admin"}, ttl=3600)
        await cache.set("user:2", {"name": "Bob", "role": "user"}, ttl=3600)
        
        # Get values
        user1 = await cache.get("user:1")
        print(f"User 1: {user1}")
        
        # Get stats
        stats = cache.get_cluster_stats()
        print(f"Cache Stats: {stats}")
    
    asyncio.run(main())
