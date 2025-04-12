"""
Dependency Cache Visualizer Package.

Provides core caching classes and a development visualizer tool.
"""

__version__ = "0.1.0" # Match pyproject.toml

# Import key components for easier access
from .core import DataCache, DependencyNode, DependencyTree
from .path_utils import (
    hash_params,
    build_raw_data_path,
    build_transformed_data_path,
    build_indicator_path,
    build_portfolio_analysis_path,
    build_portfolio_metric_path,
    build_portfolio_benchmark_metric_path,
)

# Import the main entry point function for the visualizer
# This relies on the visualizer module being structured correctly later
try:
    from .visualizer import start_visualizer
except ImportError:
    # Define a placeholder if visualizer isn't implemented yet,
    # so importing the package doesn't fail.
    import warnings
    warnings.warn(
        "Visualizer component not fully implemented yet. "
        "'start_visualizer' is a placeholder."
    )
    async def start_visualizer(*args, **kwargs):
        print(
            "Placeholder start_visualizer called. "
            "Implement the real one in visualizer/__init__.py!"
        )
        import asyncio
        await asyncio.sleep(0)


__all__ = [
    # Core classes
    "DataCache",
    "DependencyNode",
    "DependencyTree",
    # Path building utilities
    "hash_params",
    "build_raw_data_path",
    "build_transformed_data_path",
    "build_indicator_path",
    "build_portfolio_analysis_path",
    "build_portfolio_metric_path",
    "build_portfolio_benchmark_metric_path",
    # Visualizer entry point
    "start_visualizer",
]