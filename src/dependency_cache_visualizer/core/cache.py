import collections
import logging
from typing import Any, List, Dict, Optional

from .tree import DependencyTree

log = logging.getLogger(__name__)

class DataCache:
    """
    Provides a user-friendly facade for interacting with the DependencyTree cache.

    Manages cache statistics (hits, misses, adds, invalidations) both globally
    and per cache path. Handles path conversion for stats tracking.
    """
    def __init__(self):
        """
        Initializes the DataCache with a DependencyTree instance and statistics counters.
        """
        self.dependency_tree = DependencyTree()
        self._stats: Dict[str, Any] = self._init_stats()
        log.info("DataCache initialized.")

    def _init_stats(self) -> Dict[str, Any]:
        """Initializes or resets the statistics dictionary."""
        return {
            "gets": 0,
            "hits": 0,
            "misses": 0,
            "adds": 0,
            "invalidations": 0,
            # Using defaultdict for easier updates
            "paths_checked": collections.defaultdict(int),
            "paths_hit": collections.defaultdict(int),
            "paths_missed": collections.defaultdict(int),
            "paths_added": collections.defaultdict(int),
            "paths_invalidated": collections.defaultdict(int)
        }

    def _path_to_key(self, path: List[str]) -> str:
        """
        Converts a list path to a single string key suitable for stats dictionaries.

        Args:
            path: A list of strings representing the path in the dependency tree.

        Returns:
            A single string key (e.g., "raw_data/nse/symbol"). Returns "ROOT" for empty path.
        """
        return "/".join(path) if path else "ROOT"

    async def get_data(self, path: List[str]) -> Any:
        """
        Retrieves cached data for a specific path from the DependencyTree, updating stats.

        Args:
            path: A list of strings representing the path in the dependency tree.

        Returns:
            The cached data if found and not None, otherwise None.
        """
        path_key = self._path_to_key(path)
        log.debug(f"Attempting to get data for path: {path} (key: {path_key})")
        self._stats["gets"] += 1
        self._stats["paths_checked"][path_key] += 1

        try:
            data = await self.dependency_tree.get_data(path)
            if data is not None:
                self._stats["hits"] += 1
                self._stats["paths_hit"][path_key] += 1
                log.info(f"Cache HIT for path: {path}")
                return data
            else:
                self._stats["misses"] += 1
                self._stats["paths_missed"][path_key] += 1
                log.info(f"Cache MISS for path: {path}")
                return None
        except Exception as e:
            # Log unexpected errors during retrieval
            log.exception(f"Error retrieving data from cache for path {path}: {e}")
            self._stats["misses"] += 1 # Count as miss if error occurs
            self._stats["paths_missed"][path_key] += 1
            return None

    async def add_or_update_data(self, path: List[str], data: Any) -> None:
        """
        Adds or updates cached data at a specific path in the DependencyTree, updating stats.

        Args:
            path: A list of strings representing the path in the dependency tree.
            data: The data artifact to cache.
        """
        path_key = self._path_to_key(path)
        log.debug(f"Attempting to add/update data for path: {path} (key: {path_key})")
        self._stats["adds"] += 1
        self._stats["paths_added"][path_key] += 1

        try:
            await self.dependency_tree.add_or_update_node(path, data)
            log.info(f"Data added/updated successfully for path: {path}")
        except Exception as e:
            # Log unexpected errors during add/update
            log.exception(f"Error adding/updating data in cache for path {path}: {e}")
            # Decrement add count if it failed? Or leave as an attempted add?
            # Let's leave it, as the intent was to add.

    async def invalidate(self, path: List[str]) -> None:
        """
        Invalidates cached data at a specific path and its descendants, updating stats.

        Args:
            path: A list of strings representing the path to invalidate.
        """
        path_key = self._path_to_key(path)
        log.debug(f"Attempting to invalidate path: {path} (key: {path_key})")
        self._stats["invalidations"] += 1
        self._stats["paths_invalidated"][path_key] += 1

        try:
            await self.dependency_tree.invalidate(path)
            log.info(f"Cache invalidated successfully for path: {path}")
        except Exception as e:
            # Log unexpected errors during invalidation
            log.exception(f"Error invalidating cache for path {path}: {e}")
            # Decrement invalidation count? Let's leave it.

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns a copy of the current cache statistics.

        Converts defaultdicts to regular dicts for easier JSON serialization if needed.

        Returns:
            A dictionary containing cache statistics.
        """
        # Create a deep copy to avoid external modification? For stats, shallow might be ok.
        stats_copy = self._stats.copy()
        # Convert defaultdicts to regular dicts for cleaner output/serialization
        for key in [
            "paths_checked", "paths_hit", "paths_missed",
            "paths_added", "paths_invalidated"
        ]:
            stats_copy[key] = dict(stats_copy[key])
        return stats_copy

    def reset_stats(self) -> None:
        """
        Resets all cache statistics to their initial state.
        """
        log.info("Resetting cache statistics.")
        self._stats = self._init_stats()

    def __repr__(self) -> str:
        """Provides a string representation of the DataCache."""
        return f"DataCache(stats={{gets: {self._stats['gets']}, hits: {self._stats['hits']}, ...}})"