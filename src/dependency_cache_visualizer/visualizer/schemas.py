from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- Request Models ---

class PathRequest(BaseModel):
    """Request model containing just a path list."""
    path: List[str] = Field(..., description="List of strings representing the node path.")

class PathDataRequest(BaseModel):
    """Request model containing a path list and optional data."""
    path: List[str] = Field(..., description="List of strings representing the node path.")
    data: Optional[Any] = Field(None, description="Data payload to add/update.")

# --- Response Models ---

class MessageResponse(BaseModel):
    """Generic success message response."""
    message: str

class GetDataResponse(BaseModel):
    """Response model for retrieving data from a path."""
    path: List[str]
    data: Optional[Any] = None
    data_hash: Optional[str] = None
    timestamp: Optional[datetime] = None
    node_exists: bool

class TreeNode(BaseModel):
    """Serializable representation of a DependencyNode for the API."""
    identifier: str
    has_data: bool
    data_hash: Optional[str] = None
    timestamp: Optional[datetime] = None
    children: Dict[str, 'TreeNode'] = {} # Recursive definition

# Allow recursive model reference resolution
# TreeNode.update_forward_refs() # For older Pydantic v1
# For Pydantic v2, this is usually handled automatically if type hints are correct.

class TreeResponse(TreeNode):
    """The root response for the entire tree structure."""
    # Inherits structure from TreeNode, represents the root
    pass

class StatsResponse(BaseModel):
    """Response model for cache statistics."""
    gets: int
    hits: int
    misses: int
    adds: int
    invalidations: int
    paths_checked: Dict[str, int]
    paths_hit: Dict[str, int]
    paths_missed: Dict[str, int]
    paths_added: Dict[str, int]
    paths_invalidated: Dict[str, int]

    # Add calculated stats for convenience
    hit_ratio: Optional[float] = None

    # Pydantic v2 validator example (or use root_validator in v1)
    # @model_validator(mode='after') # Pydantic v2
    # def calculate_hit_ratio(self) -> 'StatsResponse':
    #     if self.gets > 0:
    #         self.hit_ratio = (self.hits / self.gets) * 100.0
    #     else:
    #         self.hit_ratio = None # Or 0.0?
    #     return self

    # Pydantic v1 validator example
    # from pydantic import root_validator
    # @root_validator
    # def calculate_hit_ratio(cls, values):
    #     gets = values.get('gets', 0)
    #     hits = values.get('hits', 0)
    #     if gets > 0:
    #         values['hit_ratio'] = (hits / gets) * 100.0
    #     else:
    #         values['hit_ratio'] = None
    #     return values

# --- Data Preview (Optional Enhancement) ---
class DataPreviewResponse(BaseModel):
    """Response model for data preview."""
    path: List[str]
    data_type: str
    preview: Any # Could be string summary, dict subset, list slice etc.
    full_data_hash: Optional[str] = None
    timestamp: Optional[datetime] = None
    node_exists: bool