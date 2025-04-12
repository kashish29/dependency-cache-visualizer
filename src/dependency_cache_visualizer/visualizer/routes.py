import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Body

from ..core import DataCache, DependencyNode # Import from parent core module
from .schemas import (
    TreeNode, TreeResponse, StatsResponse, MessageResponse,
    PathRequest, PathDataRequest, GetDataResponse,
    # DataPreviewResponse # Uncomment if implementing preview
)

log = logging.getLogger(__name__)

# This function will be used for dependency injection to get the cache instance
# It will be set up in app.py or __init__.py
async def get_cache_instance() -> DataCache:
    # This is a placeholder implementation.
    # The actual implementation will depend on how the instance is passed.
    # See app.py / __init__.py for the setup.
    raise NotImplementedError("Cache instance dependency not configured")

# Create API router
router = APIRouter()

# --- Helper Function to Serialize Tree ---
async def serialize_node(node: DependencyNode) -> TreeNode:
    """Recursively convert a DependencyNode to a serializable TreeNode."""
    if node is None:
        return None # Should not happen for root, but good practice

    children_data = {}
    # Directly iterate over children dictionary items
    for child_id, child_node in node.children.items():
         children_data[child_id] = await serialize_node(child_node)

    # --- Logging added for debugging ---
    current_path_for_log = []
    temp_node = node
    while temp_node and temp_node.parent: # Traverse up to the node just below root
        current_path_for_log.insert(0, temp_node.identifier)
        temp_node = temp_node.parent
    path_str_for_log = "/".join(current_path_for_log)

    log.debug(f"Serializing node: {node.identifier}, Path: {path_str_for_log}, Has Data according to node.data: {node.data is not None}")
    # Check specifically for the problematic path if possible
    if "interval_day" == node.identifier: # Check if the current node is an interval_day node
         log.warning(f"CHECKING interval_day node during serialization: {node.identifier}, Path: {path_str_for_log}, node.data is None: {node.data is None}")
    # --- End of added logging ---

    return TreeNode(
        identifier=node.identifier,
        has_data=node.data is not None,
        data_hash=node.data_hash,
        timestamp=node.timestamp,
        children=children_data
    )

# --- API Endpoints ---

@router.get("/tree", response_model=TreeResponse, summary="Get Cache Tree Structure")
async def get_tree(
    cache: DataCache = Depends(get_cache_instance)
):
    """
    Retrieves the entire dependency cache tree structure starting from the root.
    """
    log.debug("Received request for /tree")
    try:
        # Serialize the tree structure starting from the actual root node
        # The TreeResponse schema matches the TreeNode structure
        tree_data = await serialize_node(cache.dependency_tree.root)
        if tree_data is None: # Should ideally not happen unless root is corrupt
             raise HTTPException(status_code=500, detail="Failed to serialize root node.")
        return tree_data
    except Exception as e:
        log.exception("Error getting tree structure: %s", e)
        raise HTTPException(status_code=500, detail=f"Error getting tree: {str(e)}")

@router.get("/stats", response_model=StatsResponse, summary="Get Cache Statistics")
async def get_stats(
    cache: DataCache = Depends(get_cache_instance)
):
    """
    Retrieves the current statistics for the cache instance.
    """
    log.debug("Received request for /stats")
    try:
        stats = cache.get_stats()
        # Calculate hit ratio here if not done in Pydantic model
        gets = stats.get('gets', 0)
        hits = stats.get('hits', 0)
        if gets > 0:
            stats['hit_ratio'] = (hits / gets) * 100.0
        else:
            stats['hit_ratio'] = None
        return StatsResponse(**stats)
    except Exception as e:
        log.exception("Error getting stats: %s", e)
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.post("/reset-stats", response_model=MessageResponse, summary="Reset Cache Statistics")
async def reset_stats(
    cache: DataCache = Depends(get_cache_instance)
):
    """
    Resets all cache statistics to their initial zeroed state.
    """
    log.info("Received request to reset stats")
    try:
        cache.reset_stats()
        return MessageResponse(message="Statistics reset successfully")
    except Exception as e:
        log.exception("Error resetting stats: %s", e)
        raise HTTPException(status_code=500, detail=f"Error resetting stats: {str(e)}")

@router.post("/get-data", response_model=GetDataResponse, summary="Get Data from Path")
async def get_data(
    request: PathRequest, # Use the simple PathRequest model
    cache: DataCache = Depends(get_cache_instance)
):
    """
    Retrieves data and metadata for a specific node path.
    """
    log.debug(f"Received request for /get-data for path: {request.path}")
    try:
        # Use get_node to get metadata even if data is None
        node = await cache.dependency_tree.get_node(request.path)
        if node:
            return GetDataResponse(
                path=request.path,
                data=node.data,
                data_hash=node.data_hash,
                timestamp=node.timestamp,
                node_exists=True
            )
        else:
            return GetDataResponse(
                path=request.path,
                data=None,
                data_hash=None,
                timestamp=None,
                node_exists=False
            )
    except Exception as e:
        log.exception("Error getting data for path %s: %s", request.path, e)
        raise HTTPException(status_code=500, detail=f"Error getting data: {str(e)}")

@router.post("/add-data", response_model=MessageResponse, summary="Add or Update Data")
async def add_data(
    request: PathDataRequest, # Use model with path and data
    cache: DataCache = Depends(get_cache_instance)
):
    """
    Adds or updates data at a specific node path. Creates nodes if they don't exist.
    """
    log.info(f"Received request for /add-data for path: {request.path}")
    if not request.path:
         raise HTTPException(status_code=400, detail="Path cannot be empty for add-data.")
    try:
        await cache.add_or_update_data(request.path, request.data)
        return MessageResponse(message="Data added/updated successfully")
    except Exception as e:
        log.exception("Error adding/updating data for path %s: %s", request.path, e)
        raise HTTPException(status_code=500, detail=f"Error adding data: {str(e)}")

@router.post("/invalidate", response_model=MessageResponse, summary="Invalidate Path Subtree")
async def invalidate(
    request: PathRequest, # Use the simple PathRequest model
    cache: DataCache = Depends(get_cache_instance)
):
    """
    Invalidates the node at the specified path and its entire subtree.
    """
    log.info(f"Received request for /invalidate for path: {request.path}")
    if not request.path:
         raise HTTPException(status_code=400, detail="Path cannot be empty for invalidate.")
    try:
        await cache.invalidate(request.path)
        return MessageResponse(message="Cache path invalidated successfully")
    except Exception as e:
        log.exception("Error invalidating path %s: %s", request.path, e)
        raise HTTPException(status_code=500, detail=f"Error invalidating cache: {str(e)}")
