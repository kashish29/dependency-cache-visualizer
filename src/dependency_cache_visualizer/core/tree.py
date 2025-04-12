import asyncio
import logging
from typing import Any, List, Optional

from .node import DependencyNode

log = logging.getLogger(__name__)

class DependencyTree:
    """
    Manages the overall dependency cache tree structure.

    Provides methods to add, retrieve, and invalidate nodes within the tree
    using paths (lists of identifiers). Handles concurrency using an asyncio Lock.
    """

    def __init__(self):
        """Initializes the DependencyTree with a root node."""
        self.root: DependencyNode = DependencyNode("root")
        self._lock: asyncio.Lock = asyncio.Lock()
        log.info("DependencyTree initialized with root node.")

    async def add_or_update_node(self, path: List[str], data: Any) -> Optional[DependencyNode]:
        """
        Adds or updates a node at the specified path with the given data.

        Creates intermediate nodes if they don't exist. Acquires a lock
        to ensure thread-safe modification of the tree.

        Args:
            path: A list of string identifiers representing the path from the root.
            data: The data to store at the target node.

        Returns:
            The node that was added or updated, or None if the path was empty.
        """
        if not path:
            log.warning("Attempted to add/update node with empty path.")
            return None

        async with self._lock:
            log.debug(f"Acquired lock to add/update node at path: {path}")
            current_node = self.root
            for identifier in path:
                child = await current_node.get_child(identifier)
                if child is None:
                    log.debug(f"Creating new node '{identifier}' under '{current_node.identifier}'.")
                    new_node = DependencyNode(identifier=identifier, parent=current_node)
                    await current_node.add_child(new_node)
                    current_node = new_node
                else:
                    current_node = child

            # Now current_node is the target node
            log.info(f"Setting data for node at path: {path}")
            current_node.data = data # Setter handles hash and timestamp
            log.info(f"Data SET for node '{current_node.identifier}' at path {path}. Data type: {type(current_node.data)}, Data is None: {current_node.data is None}")
            log.debug(f"Node object after data set: {current_node}")
            log.debug(f"Releasing lock after add/update at path: {path}")
            return current_node


    async def _get_node_unsafe(self, path: List[str]) -> Optional[DependencyNode]:
        """
        Retrieves a node from the specified path WITHOUT acquiring the lock.

        Assumes the caller holds the lock. Used internally by methods that
        already manage the lock.

        Args:
            path: A list of string identifiers representing the path from the root.

        Returns:
            The DependencyNode at the specified path if found, otherwise None.
        """
        if not path:
            return self.root # Return root if path is empty

        current_node = self.root
        for identifier in path:
            # Use direct dictionary access assuming lock is held
            child = current_node.children.get(identifier)
            if child is None:
                log.debug(f"Node not found at path segment '{identifier}' within path {path} (unsafe get).")
                return None
            current_node = child
        log.debug(f"Node found at path {path} (unsafe get).")
        return current_node

    async def get_node(self, path: List[str]) -> Optional[DependencyNode]:
        """
        Retrieves a node from the specified path.

        Acquires a lock for safe concurrent access.

        Args:
            path: A list of string identifiers representing the path from the root.

        Returns:
            The DependencyNode at the specified path if found, otherwise None.
        """
        async with self._lock:
            log.debug(f"Acquired lock to get node at path: {path}")
            node = await self._get_node_unsafe(path)
            log.debug(f"Releasing lock after get node at path: {path}")
            return node

    async def invalidate(self, path: List[str]) -> None:
        """
        Invalidates a node and its entire subtree at the specified path.

        Acquires a lock to ensure safe modification during invalidation.
        If the path does not exist, this operation does nothing.

        Args:
            path: A list of string identifiers representing the path to the node
                  to invalidate.
        """
        if not path:
            log.warning("Attempted to invalidate with empty path. Invalidating root is not typical, skipping.")
            # Or potentially invalidate the whole tree if desired: await self.root.invalidate_tree()
            return

        async with self._lock:
            log.debug(f"Acquired lock to invalidate node at path: {path}")
            node_to_invalidate = await self._get_node_unsafe(path)
            if node_to_invalidate:
                log.info(f"Invalidating subtree starting at path: {path}")
                await node_to_invalidate.invalidate_tree()
                # Optional: Remove the invalidated node itself from its parent?
                # if node_to_invalidate.parent:
                #     await node_to_invalidate.parent.remove_child(node_to_invalidate.identifier)
            else:
                log.warning(f"Attempted to invalidate non-existent path: {path}")
            log.debug(f"Releasing lock after invalidate at path: {path}")


    async def get_data(self, path: List[str]) -> Any:
        """
        Convenience method to get data directly from a node at the specified path.

        Acquires a lock for safe concurrent access.

        Args:
            path: A list of string identifiers representing the path from the root.

        Returns:
            The data stored at the node if the node exists and has data, otherwise None.
        """
        node = await self.get_node(path)
        return node.data if node else None

    def __repr__(self) -> str:
        """Provides a string representation of the DependencyTree."""
        # Accessing root.children might need care if tree is modified without lock,
        # but repr is usually for debugging, so direct access might be acceptable.
        # For safety, could acquire lock, but might be overkill for repr.
        return f"DependencyTree(root_children={len(self.root.children)})"

    async def get_subtree_nodes(self, start_path: List[str] = None) -> List[DependencyNode]:
        """
        Retrieves all nodes in the subtree starting from the given path (or root).

        Uses a breadth-first search approach. Acquires lock for safety.

        Args:
            start_path: The path to the root of the subtree. If None or empty, starts from the tree root.

        Returns:
            A list of all DependencyNode objects in the specified subtree.
        """
        nodes = []
        queue = asyncio.Queue()

        async with self._lock:
            start_node = await self._get_node_unsafe(start_path or [])
            if start_node:
                await queue.put(start_node)

            while not queue.empty():
                current_node = await queue.get()
                nodes.append(current_node)
                for child in current_node.children.values():
                    await queue.put(child)

        return nodes