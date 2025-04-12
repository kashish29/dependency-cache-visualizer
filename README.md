```markdown
# Dependency Cache Visualizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/dependency-cache-visualizer.svg)](https://badge.fury.io/py/dependency-cache-visualizer)

A development tool to visualize and interact with a Python dependency-aware cache (`DataCache` built upon `DependencyTree`).

**Purpose:** Provides observability into your application's caching behavior during development. Run the visualizer alongside your application and watch how the cache structure and statistics change.

**Note:** This tool is intended for **development environments only** and should not be deployed to production.

## Features

*   Cache Tree Visualization (Expand/Collapse)
*   Manual & Auto-Refreshing (5s, 10s, 30s intervals)
*   Node Details Panel (Path, Metadata, Basic Data Preview)
*   Interactive Operations (Get, Add/Update, Invalidate) via UI
*   Cache Statistics Panel (Global & Path Counts) with Reset
*   Click-to-Populate Path for Operations


## Installation (as a library)

If you only want to *use* the visualizer with your existing application:

```bash
pip install dependency-cache-visualizer
```
*(Requires Python 3.8+)*

Then follow the "Quick Start" guide below.

## Quick Start (Using the library)

1.  **Instantiate `DataCache`:** Ensure your application uses an instance of `DataCache` from `dependency_cache_visualizer.core`.

    ```python
    # In your application's setup
    from dependency_cache_visualizer.core import DataCache
    my_app_cache = DataCache()
    ```

2.  **Start the Visualizer:** In your development startup script, import and run `start_visualizer`, passing your cache instance.

    ```python
    # In your run_dev.py or similar
    import asyncio
    from dependency_cache_visualizer import start_visualizer
    # Assuming my_app_cache is your application's cache instance

    async def main_dev():
        # Your application setup...

        print("Starting Dependency Cache Visualizer...")
        # Run the visualizer server as a background task
        asyncio.create_task(
            start_visualizer(
                cache_instance=my_app_cache,
                port=8001 # Optional port
            )
        )
        print(f"Visualizer UI available at http://127.0.0.1:8001")

        # Keep your main application running
        print("Main application running...")
        await asyncio.Event().wait() # Example: wait indefinitely

    if __name__ == "__main__":
        try:
            asyncio.run(main_dev())
        except KeyboardInterrupt:
            print("\nShutting down.")
    ```

3.  **Access UI:** Run your development script and open `http://127.0.0.1:8001` (or the configured port) in your browser.

## Development Setup (Working on the Visualizer itself)

Follow these steps if you want to modify the visualizer code (backend or frontend) or run the included example.

**Prerequisites:**

*   Python 3.8+ and pip
*   Node.js (v18 or later recommended) and npm (or yarn/pnpm)

**Steps:**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/[your-username]/dependency-cache-visualizer.git # Replace with actual URL
    cd dependency-cache-visualizer
    ```

2.  **Set up Python Environment:**
    *   Create and activate a virtual environment:
        ```bash
        python -m venv .venv
        source .venv/bin/activate  # Linux/macOS
        # .\.venv\Scripts\activate # Windows
        ```
    *   Install Python dependencies (including development tools):
        ```bash
        pip install -e .[dev] # Or pip install -e . if you don't have dev extras defined yet
        # The '-e .' installs the package in editable mode
        ```

3.  **Set up Frontend Environment:**
    *   Navigate to the frontend directory:
        ```bash
        cd frontend
        ```
    *   Install Node.js dependencies:
        ```bash
        npm install # or yarn install or pnpm install
        ```

4.  **Build Initial Frontend:**
    *   While still in the `frontend/` directory, run the build script. This compiles the React code and places the static assets (HTML, JS, CSS) into the location the Python backend expects (`src/dependency_cache_visualizer/visualizer/frontend_build/`).
        ```bash
        npm run build
        ```
    *   Go back to the project root directory:
        ```bash
        cd ..
        ```

You are now set up to run the example or start developing the visualizer components.

## Running the Example

The `examples/run_dev_example.py` script demonstrates how to integrate and run the visualizer. It:
*   Creates a `DataCache` instance.
*   Starts the visualizer backend server, passing the cache instance.
*   Simulates some basic cache operations (adding data, getting data, invalidating).

**To run the example:**

1.  **Ensure you have completed the "Development Setup" steps above.** (Virtual env activated, dependencies installed, frontend built).
2.  **Run the script from the project root directory:**
    ```bash
    python examples/run_dev_example.py
    ```
3.  **Observe the Output:** You should see log messages indicating:
    *   The visualizer server starting.
    *   The URL where the UI is available (e.g., `http://127.0.0.1:8001`).
    *   The example simulation performing cache operations (hits, misses, adds, invalidations).
4.  **Access the UI:** Open the provided URL (e.g., `http://127.0.0.1:8001`) in your web browser. You should see the visualizer interface reflecting the cache state from the example script.
5.  **Interact:** Use the refresh buttons, click nodes, try the operations panel. If you let the example run, you might see the cache change over time (especially after the simulated invalidation).
6.  **Stop the Example:** Press `Ctrl+C` in the terminal where the script is running.

## Frontend Development Workflow

If you are actively developing the **frontend UI**:

1.  **Start the Backend:** Run the Python backend using the example script (or your own application integrated with the visualizer):
    ```bash
    python examples/run_dev_example.py
    ```
    *(Keep this running in one terminal)*
2.  **Start the Frontend Dev Server:** In a *separate terminal*, navigate to the `frontend` directory and run the Vite development server:
    ```bash
    cd frontend
    npm run dev
    ```
3.  **Access Dev UI:** Open the URL provided by the Vite dev server (usually `http://localhost:5173`).
4.  **Develop:** Make changes to the React components (`frontend/src/**/*.jsx`). Vite provides Hot Module Replacement (HMR) for fast updates in the browser without full page reloads. API calls from the dev server will be proxied to the running Python backend (as configured in `vite.config.js`).
5.  **Build:** Once finished with frontend changes, run `npm run build` (in `frontend/`) to update the static assets used by the Python backend.

## Documentation

*(Link to more detailed documentation if available)*

## Contributing

Contributions are welcome! Please open an issue or submit a pull request. Ensure code is formatted (e.g., using Black for Python, Prettier for JS/React) and consider adding tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```