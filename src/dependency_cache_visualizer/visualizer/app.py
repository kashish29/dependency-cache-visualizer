import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from ..core import DataCache # Import from parent core module
from .routes import router as api_router, get_cache_instance # Import router and dependency function

log = logging.getLogger(__name__)

# --- State Management for Cache Instance ---
# This dictionary will hold the state accessible by the lifespan manager
app_state = {"cache_instance": None}

# --- Dependency Override ---
# This function will replace the placeholder in routes.py
async def get_live_cache_instance() -> DataCache:
    """Dependency function to provide the live cache instance."""
    instance = app_state.get("cache_instance")
    if instance is None:
        # This should not happen if lifespan is used correctly
        log.error("Cache instance not found in app state!")
        raise RuntimeError("Cache instance has not been initialized.")
    return instance

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown.
    Crucially, this is where we expect the cache instance to be set.
    """
    log.info("Visualizer FastAPI app starting up...")
    # The cache instance should be set in app_state *before* uvicorn starts
    # (see start_visualizer in __init__.py)
    if app_state.get("cache_instance") is None:
         log.warning("Cache instance is None during startup. Ensure it's set before running uvicorn.")
         # Optionally raise an error here if it's critical
         # raise RuntimeError("Cache instance must be set before application startup")
    else:
         log.info(f"Cache instance type during startup: {type(app_state['cache_instance'])}")

    yield # Application runs here

    # --- Shutdown logic ---
    log.info("Visualizer FastAPI app shutting down...")
    app_state["cache_instance"] = None # Clear the reference on shutdown


# --- FastAPI App Creation ---
def create_app() -> FastAPI:
    """Creates and configures the FastAPI application instance."""

    log.debug("Creating FastAPI application instance.")
    app = FastAPI(
        title="Dependency Cache Visualizer API",
        description="API endpoints for interacting with and visualizing the dependency cache.",
        version="1.0.0", # API version, distinct from package version
        lifespan=lifespan # Use lifespan manager
    )

    # --- Dependency Override ---
    # Replace the placeholder dependency with the live one
    app.dependency_overrides[get_cache_instance] = get_live_cache_instance
    log.debug("Overrode get_cache_instance dependency.")

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Allow all origins for development convenience
        # In production, restrict this to the specific frontend origin:
        # allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Example Vite default port
        allow_credentials=True,
        allow_methods=["*"], # Allow all methods (GET, POST, etc.)
        allow_headers=["*"], # Allow all headers
    )
    log.debug("CORS middleware added.")

    # --- API Router ---
    app.include_router(api_router, prefix="/api") # Prefix API routes
    log.debug("API router included with prefix /api.")

    # --- Static Files (Frontend Build) ---
    # Determine the path to the frontend build directory relative to this file
    # __file__ is the path to app.py
    # Path(__file__).parent gives the visualizer directory
    # .parent gives the dependency_cache_visualizer directory
    # then navigate to visualizer/frontend_build
    frontend_build_dir = Path(__file__).parent / "frontend_build"
    log.info(f"Attempting to serve static files from: {frontend_build_dir.resolve()}")

    if frontend_build_dir.is_dir() and (frontend_build_dir / "index.html").is_file():
        log.info("Frontend build directory found. Mounting StaticFiles.")
        # Mount static files AFTER API routes to avoid conflicts
        app.mount(
            "/",
            StaticFiles(directory=frontend_build_dir, html=True),
            name="static_frontend"
        )

        # Add a catch-all route to serve index.html for SPA routing
        # This should come after the StaticFiles mount
        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            log.debug(f"Catch-all route triggered for path: {full_path}. Serving index.html.")
            index_path = frontend_build_dir / "index.html"
            if index_path.is_file():
                return FileResponse(index_path)
            else:
                # Should not happen if StaticFiles mounted correctly
                log.error("index.html not found in catch-all route!")
                raise HTTPException(status_code=404, detail="Frontend not found.")

    else:
        log.warning(
            f"Frontend build directory '{frontend_build_dir}' not found or "
            f"'index.html' missing. Static file serving disabled."
        )
        # Add a root endpoint to indicate the API is running without the frontend
        @app.get("/", include_in_schema=False)
        async def root():
            return {"message": "Dependency Cache Visualizer API running. Frontend not found."}

    return app
