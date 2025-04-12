import hashlib
import re
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import date, datetime

log = logging.getLogger(__name__)

# --- Hashing Logic ---

def _generate_hash(*args: Any) -> str:
    """
    Generates a stable SHA256 hash for any number of arguments.

    Uses repr() for consistent serialization of various types before hashing.
    Handles nested structures reasonably well due to repr().

    Args:
        *args: Variable length argument list to be included in the hash.

    Returns:
        A string representing the SHA256 hash of the arguments.
    """
    hasher = hashlib.sha256()
    try:
        # Use repr for stable serialization and handle different types
        # The repr of a tuple includes the repr of its elements recursively
        serialized_args = repr(args)
        hasher.update(serialized_args.encode('utf-8'))
        return hasher.hexdigest()
    except Exception as e:
        log.error(f"Error generating hash for args: {args}. Error: {e}", exc_info=True)
        # Fallback or re-raise depending on desired robustness
        # Returning a constant error hash might hide issues but prevents crashes
        return "hashing_error"


def hash_params(params: Optional[Union[Dict[str, Any], List[Any]]]) -> str:
    """
    Generates a stable SHA256 hash for a dictionary or list of parameters.

    Handles None and empty structures distinctly. Uses _generate_hash internally.
    Sorts dictionary keys for stability.

    Args:
        params: A dictionary or list of parameters. Can be None.

    Returns:
        A string representing the SHA256 hash of the parameters.
    """
    if params is None:
        # Return a specific hash for None to distinguish from empty structures
        return _generate_hash("NoneType_param") # Slightly more specific
    if not params:
        # Return a specific hash for empty structures (dict or list)
        return _generate_hash("empty_structure_param")

    # Ensure dictionary keys are sorted for consistent hashing
    if isinstance(params, dict):
        # Create a sorted representation (list of key-value tuples)
        # This handles nested dicts/lists via repr() in _generate_hash
        sorted_params_repr = sorted(params.items())
        return _generate_hash(sorted_params_repr)
    elif isinstance(params, list):
         # For lists, order matters, so hash directly
        return _generate_hash(params)
    else:
        # Handle other types if necessary, or raise error
        log.warning(f"Hashing unexpected parameter type: {type(params)}. Using direct hash.")
        return _generate_hash(params)


# --- Date Formatting ---

def _format_date(d: Optional[Union[str, date, datetime]]) -> str:
    """Helper to format dates consistently for paths."""
    if isinstance(d, datetime):
        # Use ISO 8601 format with UTC offset handling if present, otherwise naive.
        # Replace colons in offset for filesystem compatibility if needed, though not strictly necessary for list paths.
        return d.isoformat() # Example: '2023-10-27T10:30:00+00:00' or '2023-10-27T10:30:00'
        # Alternative: return d.strftime('%Y%m%d_%H%M%S%z') # Example: '20231027_103000+0000'
    elif isinstance(d, date):
        return d.isoformat() # Example: '2023-10-27'
        # Alternative: return d.strftime('%Y%m%d') # Example: '20231027'
    elif isinstance(d, str):
        # Attempt to parse common formats for consistency, otherwise sanitize
        try:
            dt = datetime.fromisoformat(d.replace('Z', '+00:00'))
            return dt.isoformat()
        except ValueError:
            try:
                dt = datetime.strptime(d, '%Y-%m-%d')
                return dt.date().isoformat()
            except ValueError:
                try:
                    # Handle YYYYMMDD format
                    dt = datetime.strptime(d, '%Y%m%d')
                    return dt.date().isoformat()
                except ValueError:
                    # Basic sanitization for other string formats
                    log.debug(f"Could not parse date string '{d}', using sanitized version.")
                    sanitized = re.sub(r'[^\w\-]+', '_', d) # Replace non-alphanumeric/- with _
                    return sanitized if sanitized else "invalid_date_str"
    elif d is None:
        return "None"
    else:
        # Fallback for other types
        log.warning(f"Formatting unexpected date type: {type(d)}. Using str().")
        return str(d)

# --- Path Building Functions ---

def build_raw_data_path(
    source: str,
    symbol: str,
    start_date: Optional[Union[str, date, datetime]],
    end_date: Optional[Union[str, date, datetime]],
    interval: str
) -> List[str]:
    """Builds the cache path components for raw market data."""
    if not all([source, symbol, interval]):
        raise ValueError("Source, symbol, and interval cannot be empty.")
    # Sanitize symbol: uppercase and replace non-alphanumeric with underscore
    sanitized_symbol = re.sub(r'\W+', '_', symbol).upper()
    return [
        "raw_data",
        str(source).lower(),
        sanitized_symbol,
        f"start_{_format_date(start_date)}",
        f"end_{_format_date(end_date)}",
        f"interval_{str(interval).lower()}"
    ]

def build_transformed_data_path(
    raw_data_path: List[str],
    steps_config: Optional[Union[Dict[str, Any], List[Any]]] # Configuration for transformation steps
) -> List[str]:
    """Builds the cache path components for transformed data, based on raw data and steps."""
    if not raw_data_path or raw_data_path[0] != "raw_data":
         raise ValueError("Invalid raw_data_path provided for transformation.")
    transform_hash = hash_params(steps_config)
    return raw_data_path + ["transformed", f"config_{transform_hash}"]

def build_indicator_path(
    transformed_data_path: List[str],
    indicator_name: str,
    indicator_params: Optional[Dict[str, Any]]
) -> List[str]:
    """Builds the cache path components for a specific indicator calculated on transformed data."""
    if not transformed_data_path or "transformed" not in transformed_data_path:
         raise ValueError("Invalid transformed_data_path provided for indicator.")
    if not indicator_name:
        raise ValueError("Indicator name cannot be empty.")

    indicator_name_safe = re.sub(r'\s+', '_', indicator_name).lower() # Replace spaces with _
    params_hash = hash_params(indicator_params)
    return transformed_data_path + ["indicators", f"{indicator_name_safe}_{params_hash}"]

def build_portfolio_analysis_path(
    trade_source_info: str, # e.g., csv_filename_hash or db_query_hash or label
    market_data_symbols: List[str],
    start_date: Optional[Union[str, date, datetime]],
    end_date: Optional[Union[str, date, datetime]],
    interval: str,
    analysis_params: Optional[Dict[str, Any]]
) -> List[str]:
    """Builds the base cache path components for a portfolio analysis result."""
    if not trade_source_info or not market_data_symbols or not interval:
         raise ValueError("Trade source info, market data symbols, and interval are required.")

    # Sanitize symbols before joining, ensure consistent order
    sanitized_symbols = sorted([re.sub(r'\W+', '_', s).upper() for s in market_data_symbols])
    symbols_str = "_".join(sanitized_symbols) if sanitized_symbols else "no_symbols"
    params_hash = hash_params(analysis_params)
    return [
        "portfolio_analysis",
        f"trades_{str(trade_source_info)}", # Keep trade source info separate
        f"market_{symbols_str}",
        f"start_{_format_date(start_date)}",
        f"end_{_format_date(end_date)}",
        f"interval_{str(interval).lower()}",
        f"params_{params_hash}" # Hash of analysis-specific parameters
    ]

def build_portfolio_metric_path(
    portfolio_analysis_path: List[str],
    metric_name: str,
    metric_params: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Builds the cache path components for a specific core portfolio metric."""
    if not portfolio_analysis_path or portfolio_analysis_path[0] != "portfolio_analysis":
        raise ValueError("Invalid portfolio_analysis_path provided for metric.")
    if not metric_name:
        raise ValueError("Metric name cannot be empty.")

    metric_name_safe = re.sub(r'\s+', '_', metric_name).lower()
    params_hash = hash_params(metric_params)
    # Path structure: base_analysis_path / metrics / metric_name_params_hash
    return portfolio_analysis_path + ["metrics", f"{metric_name_safe}_{params_hash}"]

def build_portfolio_benchmark_metric_path(
    portfolio_analysis_path: List[str],
    benchmark_symbol: str,
    metric_name: str,
    metric_params: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Builds the cache path components for a benchmark-specific portfolio metric."""
    if not portfolio_analysis_path or portfolio_analysis_path[0] != "portfolio_analysis":
        raise ValueError("Invalid portfolio_analysis_path provided for benchmark metric.")
    if not benchmark_symbol or not metric_name:
        raise ValueError("Benchmark symbol and metric name cannot be empty.")

    metric_name_safe = re.sub(r'\s+', '_', metric_name).lower()
    # Sanitize benchmark symbol for path inclusion
    sanitized_benchmark = re.sub(r'\W+', '_', benchmark_symbol).upper()
    params_hash = hash_params(metric_params)
    # Path structure: base_analysis_path / benchmark_metrics / benchmark_symbol / metric_name_params_hash
    return portfolio_analysis_path + ["benchmark_metrics", sanitized_benchmark, f"{metric_name_safe}_{params_hash}"]


# Example Usage (updated for demonstration) - Keep this for testing the module directly
if __name__ == '__main__':
    print("--- Hashing Examples ---")
    print(f"Hash for None: {hash_params(None)}")
    print(f"Hash for {{}}: {hash_params({})}")
    print(f"Hash for []: {hash_params([])}")
    dict_param = {"b": 2, "a": 1, "nested": {"y": 99, "x": 98}}
    print(f"Hash for {dict_param}: {hash_params(dict_param)}")
    list_param = [1, 'hello', None, {'c': 3}]
    print(f"Hash for {list_param}: {hash_params(list_param)}")
    print(f"Direct _generate_hash('a', 1, None): {_generate_hash('a', 1, None)}")


    print("\n--- Path Building Examples ---")
    raw_path = build_raw_data_path("NSE", "RELIANCE^", "2023-01-01", date(2023, 12, 31), "1d")
    print(f"Raw Path: {raw_path}")

    transform_steps = [{'name': 'fillna', 'method': 'ffill'}, {'name': 'scale', 'columns': ['Close']}]
    transformed_path = build_transformed_data_path(raw_path, transform_steps)
    print(f"Transformed Path: {transformed_path}")

    indicator_params_sma = {"timeperiod": 20}
    sma_path = build_indicator_path(transformed_path, "SMA", indicator_params_sma)
    print(f"SMA Indicator Path: {sma_path}")

    portfolio_params = {"risk_free_rate": 0.01, "mode": "quantstats"}
    analysis_path = build_portfolio_analysis_path(
        trade_source_info="trades_hash_123abc",
        market_data_symbols=["AAPL", "GOOGL", "MSFT"],
        start_date="2023-01-01",
        end_date="2023-12-31",
        interval="1d",
        analysis_params=portfolio_params
    )
    print(f"Portfolio Analysis Path: {analysis_path}")

    sharpe_path = build_portfolio_metric_path(analysis_path, "Sharpe Ratio")
    print(f"Core Sharpe Metric Path: {sharpe_path}")

    equity_path = build_portfolio_metric_path(analysis_path, "Equity Curve")
    print(f"Core Equity Curve Path: {equity_path}")

    # Benchmark paths
    benchmark_alpha_path = build_portfolio_benchmark_metric_path(
        analysis_path,
        benchmark_symbol="SPY",
        metric_name="Alpha"
    )
    print(f"Benchmark Alpha (SPY) Path: {benchmark_alpha_path}")

    benchmark_equity_path = build_portfolio_benchmark_metric_path(
        analysis_path,
        benchmark_symbol="^IXIC", # Example with special char
        metric_name="Benchmark Equity"
    )
    print(f"Benchmark Equity (^IXIC) Path: {benchmark_equity_path}")

    benchmark_beta_path_params = build_portfolio_benchmark_metric_path(
        analysis_path,
        benchmark_symbol="SPY",
        metric_name="Rolling Beta",
        metric_params={"window": 60}
    )
    print(f"Benchmark Rolling Beta (SPY, 60d) Path: {benchmark_beta_path_params}")