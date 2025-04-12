# examples/run_dev_example.py

import asyncio
import logging
from datetime import date
import time

# --- Configure logging for the example ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# --- Import Core Components ---
from dependency_cache_visualizer.core import DataCache

# --- Import Path Utilities ---
from dependency_cache_visualizer.path_utils import (
    build_raw_data_path,
    build_transformed_data_path,
    build_indicator_path,
)

# --- Import the Visualizer Starter ---
try:
    from dependency_cache_visualizer.visualizer import start_visualizer
except ImportError:
    log.warning("Visualizer module not found, defining placeholder start_visualizer.")
    async def start_visualizer(*args, **kwargs):
        print("Placeholder start_visualizer called. Implement the real one!")
        await asyncio.sleep(0)

# --- Global Cache Instance ---
app_cache = DataCache()

# --- Example Application Logic ---
async def simulate_data_processing():
    """Simulates fetching, transforming, and analyzing data using the cache."""
    log.info("=============================================")
    log.info("Starting simulated data processing pipeline (Multi-Branch)...")
    log.info("=============================================")

    # 1. Define parameters
    source = "yahoo"
    symbols = ["AAPL", "MSFT"] # Multiple symbols
    start = date(2023, 1, 1)
    end = date(2023, 6, 30)
    interval = "1d"

    # AAPL specific configs
    transform_config_aapl = [{"step": "normalize", "columns": ["Open", "Close"]}]
    indicator_config_rsi = {"timeperiod": 14}
    indicator_config_macd = {"fastperiod": 12, "slowperiod": 26, "signalperiod": 9} # Example MACD params

    # --- Stage 1: Raw Data (Multiple Symbols) ---
    log.info("\n--- Stage: Raw Data (Multiple Symbols) ---")
    raw_data_store = {} # Store fetched data for later use

    for symbol in symbols:
        log.info(f"\nProcessing Raw Data for: {symbol}")
        raw_path = build_raw_data_path(source, symbol, start, end, interval)
        log.info(f"Built Raw Path ({symbol}): {raw_path}")

        # 1a. Check cache (expect MISS)
        log.info(f"Getting raw data for {symbol} (expecting MISS)...")
        raw_data = await app_cache.get_data(raw_path)
        if raw_data is None:
            log.info(f"Raw data MISS confirmed ({symbol}). Simulating fetch...")
            await asyncio.sleep(0.4) # Simulate network delay
            # Simulate slightly different data per symbol
            simulated_raw_data = {
                "price_data": [170.0 + (ord(symbol[0]) % 5), 171.5, 171.0],
                "volume": [1e6, 1.1e6, 0.9e6],
                "fetch_time": time.time()
            }
            await app_cache.add_or_update_data(raw_path, simulated_raw_data)
            log.info(f"Raw data ADDED to cache ({symbol}).")
            raw_data_store[symbol] = simulated_raw_data # Store fetched data
        else:
            log.error(f"UNEXPECTED HIT for raw data ({symbol})!")

        # 1b. Check cache again (expect HIT)
        log.info(f"Getting raw data for {symbol} again (expecting HIT)...")
        raw_data_again = await app_cache.get_data(raw_path)
        if raw_data_again is not None:
            log.info(f"Raw data HIT confirmed ({symbol}).")
        else:
            log.error(f"ERROR: Expected cache hit for raw path ({symbol}) but got miss!")

    # --- Stage 2: Transformed Data (Only for AAPL in this example) ---
    log.info("\n--- Stage: Transformed Data (AAPL) ---")
    symbol_to_transform = "AAPL"
    raw_path_aapl = build_raw_data_path(source, symbol_to_transform, start, end, interval)
    transformed_path_aapl = build_transformed_data_path(raw_path_aapl, transform_config_aapl)
    log.info(f"Built Transformed Path (AAPL): {transformed_path_aapl}")

    # 2a. Check cache (expect MISS)
    log.info(f"Getting transformed data for {symbol_to_transform} (expecting MISS)...")
    transformed_data_aapl = await app_cache.get_data(transformed_path_aapl)
    if transformed_data_aapl is None:
        log.info(f"Transformed data MISS confirmed ({symbol_to_transform}). Simulating transform...")
        await asyncio.sleep(0.3) # Simulate computation
        raw_data_for_transform = raw_data_store.get(symbol_to_transform)
        if raw_data_for_transform:
            simulated_transformed_data = {"normalized_prices": [0.99, 1.0, 0.995], "based_on_fetch_time": raw_data_for_transform.get("fetch_time")}
            await app_cache.add_or_update_data(transformed_path_aapl, simulated_transformed_data)
            log.info(f"Transformed data ADDED to cache ({symbol_to_transform}).")
            transformed_data_aapl = simulated_transformed_data
        else:
             log.error(f"Could not find raw data for {symbol_to_transform} to perform transformation!")
    else:
        log.error(f"UNEXPECTED HIT for transformed data ({symbol_to_transform})!")

    # 2b. Check cache again (expect HIT)
    log.info(f"Getting transformed data for {symbol_to_transform} again (expecting HIT)...")
    transformed_data_again = await app_cache.get_data(transformed_path_aapl)
    if transformed_data_again is not None:
        log.info(f"Transformed data HIT confirmed ({symbol_to_transform}).")
    else:
        log.error(f"ERROR: Expected cache hit for transformed path ({symbol_to_transform}) but got miss!")

    # --- Stage 3: Indicator Calculation (Multiple Indicators for AAPL) ---
    log.info("\n--- Stage: Indicator Calculation (AAPL - RSI & MACD) ---")
    indicators_to_calc = {
        "RSI": indicator_config_rsi,
        "MACD": indicator_config_macd
    }

    for indicator_name, indicator_config in indicators_to_calc.items():
        log.info(f"\nProcessing Indicator: {indicator_name} for {symbol_to_transform}")
        indicator_path = build_indicator_path(transformed_path_aapl, indicator_name, indicator_config)
        log.info(f"Built {indicator_name} Path (AAPL): {indicator_path}")

        # 3a. Check cache (expect MISS)
        log.info(f"Getting {indicator_name} indicator for {symbol_to_transform} (expecting MISS)...")
        indicator_result = await app_cache.get_data(indicator_path)
        if indicator_result is None:
            log.info(f"{indicator_name} indicator MISS confirmed. Simulating calculation...")
            await asyncio.sleep(0.2) # Simulate computation
            # Simulate different results per indicator
            simulated_indicator_result = {f"{indicator_name.lower()}_values": [55.0 + len(indicator_name), 60.0, 58.0]}
            await app_cache.add_or_update_data(indicator_path, simulated_indicator_result)
            log.info(f"{indicator_name} indicator ADDED to cache.")
        else:
            log.error(f"UNEXPECTED HIT for {indicator_name} indicator!")

        # 3b. Check cache again (expect HIT)
        log.info(f"Getting {indicator_name} indicator for {symbol_to_transform} again (expecting HIT)...")
        indicator_result_again = await app_cache.get_data(indicator_path)
        if indicator_result_again is not None:
            log.info(f"{indicator_name} indicator HIT confirmed.")
        else:
            log.error(f"ERROR: Expected cache hit for {indicator_name} path but got miss!")

    # --- Stage 4: Data Update (AAPL Raw Data) ---
    log.info("\n--- Stage: Data Update (AAPL Raw Data) ---")
    log.info(f"Simulating an update to the raw data for {symbol_to_transform}...")
    await asyncio.sleep(0.5) # Simulate delay before update
    updated_simulated_raw_data = {"price_data": [170.1, 171.6, 171.1], "volume": [1e6, 1.1e6, 0.9e6], "fetch_time": time.time()}
    await app_cache.add_or_update_data(raw_path_aapl, updated_simulated_raw_data) # Use AAPL's raw path
    log.info(f"Raw data UPDATED in cache ({symbol_to_transform}).")

    # --- Stage 5: Invalidation (AAPL Transformed Data) ---
    log.info("\n--- Stage: Invalidation (AAPL Transformed Data) ---")
    log.info(f"Simulating invalidation of TRANSFORMED data path for {symbol_to_transform}...")
    await asyncio.sleep(1)
    await app_cache.invalidate(transformed_path_aapl)
    log.info(f"Invalidated path: {transformed_path_aapl}")
    log.info(f"(Note: This also implicitly invalidates downstream paths like RSI and MACD for AAPL)")

    # --- Stage 6: Post-Invalidation Checks ---
    log.info("\n--- Stage: Post-Invalidation Checks ---")
    # 6a. Check AAPL transformed (expect MISS)
    log.info(f"Getting TRANSFORMED data for {symbol_to_transform} after invalidation (expecting MISS)...")
    transformed_data_after_invalidate = await app_cache.get_data(transformed_path_aapl)
    if transformed_data_after_invalidate is None:
        log.info(f"Transformed data ({symbol_to_transform}) is correctly MISSING.")
    else:
        log.error(f"ERROR: Transformed data ({symbol_to_transform}) still present after invalidation!")

    # 6b. Check AAPL indicators (expect MISS)
    for indicator_name, indicator_config in indicators_to_calc.items():
        indicator_path = build_indicator_path(transformed_path_aapl, indicator_name, indicator_config)
        log.info(f"Getting {indicator_name} indicator for {symbol_to_transform} after invalidation (expecting MISS)...")
        indicator_result_after_invalidate = await app_cache.get_data(indicator_path)
        if indicator_result_after_invalidate is None:
            log.info(f"{indicator_name} indicator ({symbol_to_transform}) is correctly MISSING.")
        else:
            log.error(f"ERROR: {indicator_name} indicator ({symbol_to_transform}) still present after invalidation!")

    # 6c. Check AAPL raw data (expect HIT - updated version)
    log.info(f"Getting raw data for {symbol_to_transform} again after unrelated invalidation (expecting HIT)...")
    raw_data_final_check_aapl = await app_cache.get_data(raw_path_aapl)
    if raw_data_final_check_aapl is not None:
        log.info(f"Raw data HIT confirmed ({symbol_to_transform}).")
        if raw_data_final_check_aapl.get("fetch_time") == updated_simulated_raw_data.get("fetch_time"):
             log.info(f"Raw data ({symbol_to_transform}) reflects the previous UPDATE operation.")
        else:
             log.warning(f"Raw data ({symbol_to_transform}) does not seem to be the updated version?")
    else:
        log.error(f"ERROR: Expected cache hit for raw path ({symbol_to_transform}) but got miss!")

    # 6d. Check MSFT raw data (expect HIT - unaffected)
    symbol_unaffected = "MSFT"
    raw_path_msft = build_raw_data_path(source, symbol_unaffected, start, end, interval)
    log.info(f"Getting raw data for {symbol_unaffected} again after unrelated invalidation (expecting HIT)...")
    raw_data_final_check_msft = await app_cache.get_data(raw_path_msft)
    if raw_data_final_check_msft is not None:
        log.info(f"Raw data HIT confirmed ({symbol_unaffected} - unaffected by AAPL invalidation).")
    else:
        log.error(f"ERROR: Expected cache hit for raw path ({symbol_unaffected}) but got miss!")


    log.info("\n=============================================")
    log.info("Simulated data processing pipeline finished.")
    log.info("Check the Visualizer UI for final cache state and stats.")
    log.info("=============================================")


# --- Main Development Runner ---
async def main_dev():
    """Sets up the app and starts the visualizer."""
    log.info("Development environment starting...")

    # --- Start the Dependency Cache Visualizer ---
    log.info("Starting Dependency Cache Visualizer...")
    visualizer_port = 8001
    visualizer_task = asyncio.create_task(
        start_visualizer(
            cache_instance=app_cache,
            host="127.0.0.1",
            port=visualizer_port
        )
    )
    log.info(f"Visualizer UI should be available at http://127.0.0.1:{visualizer_port}")
    await asyncio.sleep(1) # Give visualizer a moment to start up

    # --- Run example application logic ---
    log.info("Running example application simulation...")
    app_task = asyncio.create_task(simulate_data_processing())

    # Wait for the simulation task to complete before stopping (or wait indefinitely)
    await app_task
    log.info("Example simulation task completed.")

    # Keep the script alive to allow inspecting the final state in the visualizer
    log.info("Visualizer running with final cache state. Press Ctrl+C to stop.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main_dev())
    except KeyboardInterrupt:
        log.info("\nShutting down development environment.")
    except Exception as e:
        log.exception(f"An unexpected error occurred: {e}")