"""
Tests for the path utility functions in path_utils.builders.
"""

import pytest
import os
from dependency_cache_visualizer.path_utils import builders

# --- Test hash_params ---

def test_hash_params_empty():
    """Tests hashing None or empty dict."""
    assert builders.hash_params(None) == "no_params"
    assert builders.hash_params({}) == "no_params"

def test_hash_params_simple():
    """Tests hashing a simple dictionary."""
    p1 = {"a": 1, "b": "hello"}
    h1 = builders.hash_params(p1)
    assert isinstance(h1, str)
    assert len(h1) == 8 # Default length

def test_hash_params_consistency():
    """Tests that hash is consistent regardless of key order."""
    p1 = {"a": 1, "b": "hello", "c": True}
    p2 = {"b": "hello", "c": True, "a": 1} # Same params, different order
    assert builders.hash_params(p1) == builders.hash_params(p2)

def test_hash_params_different():
    """Tests that different params produce different hashes."""
    p1 = {"a": 1, "b": "hello"}
    p3 = {"a": 1, "b": "world"}
    assert builders.hash_params(p1) != builders.hash_params(p3)

def test_hash_params_types():
    """Tests hashing with different basic types."""
    p4 = {"int": 10, "float": 3.14, "bool": False, "none": None, "str": "test"}
    h4 = builders.hash_params(p4)
    p5 = {"int": 10, "float": 3.14, "bool": False, "none": None, "str": "test"} # Identical
    assert h4 == builders.hash_params(p5)
    p6 = {"int": 11, "float": 3.14, "bool": False, "none": None, "str": "test"} # Different int
    assert h4 != builders.hash_params(p6)

def test_hash_params_length():
    """Tests custom hash length."""
    p1 = {"a": 1}
    h_short = builders.hash_params(p1, length=4)
    h_long = builders.hash_params(p1, length=16)
    assert len(h_short) == 4
    assert len(h_long) == 16
    assert h_long.startswith(h_short) # Should be prefix of longer hash

# --- Test build_structured_path ---

@pytest.fixture
def base_dir(tmp_path):
    """Provides a temporary directory for testing paths."""
    return str(tmp_path)

def test_build_structured_path_basic(base_dir):
    """Tests basic path construction."""
    path = builders.build_structured_path(
        base_dir=base_dir,
        category="data",
        node_name="My Node",
        file_extension=".dat"
    )
    parts = path.split(os.sep)
    assert parts[-4] == base_dir.split(os.sep)[-1] # Check base dir part
    assert parts[-3] == "data"
    assert parts[-2] == "My_Node" # Check sanitized name
    assert parts[-1].endswith(".dat")
    assert len(parts[-1]) == 8 + 4 # hash length + extension length

def test_build_structured_path_with_params(base_dir):
    """Tests path construction with parameters."""
    params = {"rate": 0.5, "label": "train"}
    param_hash = builders.hash_params(params)
    path = builders.build_structured_path(
        base_dir=base_dir,
        category="results",
        node_name="Model_Run",
        params=params,
        file_extension=".json"
    )
    assert path.endswith(f"{param_hash}.json")
    assert "results" in path
    assert "Model_Run" in path

def test_build_structured_path_with_version(base_dir):
    """Tests path construction with version."""
    path = builders.build_structured_path(
        base_dir=base_dir,
        category="compute",
        node_name="Step1",
        version="1.2.3",
        file_extension=".pkl"
    )
    assert os.path.join("compute", "Step1", "v1_2_3") in path

def test_build_structured_path_with_all(base_dir):
    """Tests path construction with version and params."""
    params = {"threshold": 10}
    param_hash = builders.hash_params(params)
    path = builders.build_structured_path(
        base_dir=base_dir,
        category="output",
        node_name="Final Output!", # Test sanitization
        params=params,
        version="exp-001",
        file_extension=".csv",
        param_hash_length=10 # Custom hash length
    )
    assert os.path.join("output", "Final_Output_", "vexp-001", f"{param_hash[:10]}.csv") in path


# --- Test build_raw_data_path ---

def test_build_raw_data_path_helper(base_dir):
    """Tests the raw data path helper function."""
    path = builders.build_raw_data_path(
        base_dir=base_dir,
        source_identifier="input/data.csv",
        params={"sampling": 100},
        version="orig",
        file_extension=".feather"
    )
    param_hash = builders.hash_params({"sampling": 100})
    # Note: source_identifier is used as node_name and might be sanitized
    safe_source_id = "input_data_csv"
    assert os.path.join(base_dir, "raw_data", safe_source_id, "vorig", f"{param_hash}.feather") == path

# --- Test build_computation_path ---

def test_build_computation_path_helper(base_dir):
    """Tests the computation path helper function."""
    params = {"alpha": 0.1}
    inputs = ["hash1", "hash2"]
    combined_params = params.copy()
    combined_params["__input_hashes__"] = sorted(inputs)
    combined_hash = builders.hash_params(combined_params)

    path = builders.build_computation_path(
        base_dir=base_dir,
        computation_name="TrainModel",
        params=params,
        input_hashes=inputs,
        version="v3",
        file_extension=".model"
    )
    assert os.path.join(base_dir, "computation", "TrainModel", "vv3", f"{combined_hash}.model") == path

def test_build_computation_path_no_inputs(base_dir):
    """Tests computation path without explicit input hashes."""
    params = {"config": "default.yaml"}
    param_hash = builders.hash_params(params) # No __input_hashes__ key
    path = builders.build_computation_path(
        base_dir=base_dir,
        computation_name="LoadConfig",
        params=params,
        input_hashes=None, # Explicitly None
        version="1.0"
    )
    assert os.path.join(base_dir, "computation", "LoadConfig", "v1_0", f"{param_hash}.pkl") == path

def test_build_computation_path_only_inputs(base_dir):
    """Tests computation path with only input hashes (no other params)."""
    inputs = ["input_hash_a"]
    combined_params = {"__input_hashes__": sorted(inputs)}
    combined_hash = builders.hash_params(combined_params)
    path = builders.build_computation_path(
        base_dir=base_dir,
        computation_name="Aggregate",
        params=None, # Explicitly None
        input_hashes=inputs,
        version="agg-1"
    )
    assert os.path.join(base_dir, "computation", "Aggregate", "vagg-1", f"{combined_hash}.pkl") == path