import logging
import asyncio
from typing import Optional

import uvicorn

from ..core import DataCache # Import from parent core module
from .app import create_app, app_state # Import factory and state management

log = logging.getLogger(__name__)

# Define the public function to start the visualizer
async def start_visualizer(
    cache_instance: DataCache,
    host: str = "127.0.0.1",
    port: int = 8001,
    log_level: str = "info",
    reload: bool = False # Typically False when run programmatically
):
    """
    Starts the Dependency Cache Visualizer backend server.

    Args:
        cache_instance: The live instance of DataCache to visualize.
        host: The network interface to bind the server to.
        port: The port to run the server on.
        log_level: Logging level for the Uvicorn server.
        reload: Enable auto-reload (usually for development of the visualizer itself).
    """
    if not isinstance(cache_instance, DataCache):
        raise TypeError("cache_instance must be an instance of DataCache")

    log.info(f"Preparing to start visualizer server on {host}:{port}")
    log.info(f"Visualizing DataCache instance: {cache_instance}")

    # --- Crucial Step: Pass the cache instance to the app ---
    # Set the instance in the shared state *before* creating/running the app
    app_state["cache_instance"] = cache_instance
    log.debug(f"Set cache_instance in app_state: {app_state['cache_instance']}")

    app = create_app()

    # Configure Uvicorn
    config = uvicorn.Config(
        app=app, # Pass the FastAPI app instance
        host=host,
        port=port,
        log_level=log_level.lower(),
        reload=reload,
        # Use lifespan='on' to ensure lifespan events are handled
        lifespan='on'
    )

    server = uvicorn.Server(config)

    log.info("Starting Uvicorn server for visualizer...")
    try:
        await server.serve()
    except asyncio.CancelledError:
        log.info("Visualizer server task cancelled.")
    except Exception as e:
        log.exception(f"Visualizer server encountered an error: {e}")
    finally:
        log.info("Visualizer server stopped.")
        if app_state.get("cache_instance") is not None:
             log.warning("Cleaning up cache_instance reference after server stop.")
             app_state["cache_instance"] = None


__all__ = ["start_visualizer"]