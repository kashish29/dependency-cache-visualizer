import asyncio
import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Set up basic logging
log = logging.getLogger(__name__)

class DependencyNode:
    """
    Represents a node in the dependency cache tree.

    Each node holds optional data, tracks its children, parent, timestamp,
    and a hash of its data for change detection.
    """

    def __init__(
        self,
        identifier: str,
        data: Any = None,
        parent: Optional['DependencyNode'] = None
    ):
        """
        Initializes a DependencyNode.

        Args:
            identifier: A string identifier for this node within its parent's children.
            data: The data payload to cache at this node (optional).
            parent: A reference to the parent node (optional, None for root).
        """
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("Node identifier must be a non-empty string.")

        self.identifier: str = identifier
        self._data: Any = data
        self.parent: Optional['DependencyNode'] = parent
        self.children: Dict[str, 'DependencyNode'] = {}
        self.timestamp: datetime = datetime.now()
        self._data_hash: Optional[str] = self._generate_hash(data) if data is not None else None
        log.debug(f"Node '{self.identifier}' created.")

    @property
    def data(self) -> Any:
        """Gets the data stored in this node."""
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        """Sets the data for this node and updates the hash and timestamp."""
        self._data = value
        self._data_hash = self._generate_hash(value) if value is not None else None
        self.timestamp = datetime.now()
        log.debug(f"Data set for node '{self.identifier}', hash: {self._data_hash}")

    @property
    def data_hash(self) -> Optional[str]:
        """Gets the hash of the data stored in this node."""
        return self._data_hash

    def _generate_hash(self, data_to_hash: Any) -> str:
        """
        Generates a stable MD5 hash for the node's data.

        Uses JSON serialization with a fallback to repr() for complex types.
        Note: This is a basic implementation. For complex objects like DataFrames
        or custom classes without stable repr, a more robust hashing strategy
        (e.g., considering specific attributes, using pickle with care, or
        custom serializers) might be needed.

        Args:
            data_to_hash: The data to generate a hash for.

        Returns:
            A string representing the MD5 hash.
        """
        try:
            # Use default=str for common non-serializable types like datetime
            data_str = json.dumps(data_to_hash, sort_keys=True, default=str)
        except (TypeError, OverflowError):
            # Fallback for types JSON can't handle directly
            data_str = repr(data_to_hash)
            log.warning(
                f"Using repr() for hashing data of type {type(data_to_hash)} "
                f"in node '{self.identifier}'. Ensure repr is stable."
            )
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    async def add_child(self, child_node: 'DependencyNode') -> None:
        """
        Adds a child node to this node.

        Sets the child's parent reference.

        Args:
            child_node: The DependencyNode instance to add as a child.
        """
        if not isinstance(child_node, DependencyNode):
            raise TypeError("Child must be an instance of DependencyNode.")
        if child_node.identifier in self.children:
            log.warning(f"Overwriting existing child with identifier '{child_node.identifier}' in node '{self.identifier}'.")

        child_node.parent = self
        self.children[child_node.identifier] = child_node
        log.debug(f"Child node '{child_node.identifier}' added to parent '{self.identifier}'.")

    async def get_child(self, identifier: str) -> Optional['DependencyNode']:
        """
        Gets a child node by its identifier.

        Args:
            identifier: The string identifier of the child node.

        Returns:
            The child DependencyNode if found, otherwise None.
        """
        return self.children.get(identifier)

    async def remove_child(self, identifier: str) -> None:
        """
        Removes a child node by its identifier.

        The removed child node and its descendants are not automatically invalidated;
        call invalidate_tree on the child first if needed.

        Args:
            identifier: The string identifier of the child node to remove.
        """
        if identifier in self.children:
            child_to_remove = self.children.pop(identifier)
            child_to_remove.parent = None # Dereference parent
            log.debug(f"Child node '{identifier}' removed from parent '{self.identifier}'.")
        else:
            log.warning(f"Attempted to remove non-existent child '{identifier}' from node '{self.identifier}'.")

    async def clear_children(self) -> None:
        """
        Removes all child nodes from this node.

        This method recursively invalidates the entire subtree rooted at each child
        before removing the child reference.
        """
        children_to_clear = list(self.children.values())
        self.children.clear()
        log.debug(f"Clearing {len(children_to_clear)} children from node '{self.identifier}'.")
        # Invalidate children *after* clearing the dictionary to avoid potential
        # modification during iteration issues if invalidation triggers other actions.
        await asyncio.gather(*(child.invalidate_tree() for child in children_to_clear))
        log.debug(f"Finished invalidating children of node '{self.identifier}'.")


    async def invalidate_tree(self) -> None:
        """
        Invalidates this node and recursively invalidates all its descendants.

        Invalidation means setting the node's data and hash to None and updating
        its timestamp. It then clears all children, triggering their invalidation.
        """
        log.debug(f"Invalidating node '{self.identifier}' and its descendants.")
        self._data = None
        self._data_hash = None
        self.timestamp = datetime.now()
        # Clear children, which will recursively call invalidate_tree on them
        await self.clear_children()
        log.debug(f"Node '{self.identifier}' invalidation complete.")


    def __repr__(self) -> str:
        """Provides a string representation of the node."""
        parent_id = f"'{self.parent.identifier}'" if self.parent else "None"
        return (
            f"DependencyNode(identifier='{self.identifier}', "
            f"has_data={self._data is not None}, "
            f"hash='{self._data_hash[:7] if self._data_hash else None}...', "
            f"children={len(self.children)}, "
            f"parent={parent_id})"
        )

    def get_path(self) -> List[str]:
        """Returns the list of identifiers from the root to this node."""
        path = []
        current = self
        while current is not None and current.identifier != "root": # Stop at root
            path.append(current.identifier)
            current = current.parent
        return path[::-1] # Reverse to get root -> node order