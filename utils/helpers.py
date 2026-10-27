import json
import re
from pathlib import Path
from typing import Dict, Set, Any

_CONFIG = None

def load_config():
    """Load configuration from config.json"""
    global _CONFIG
    if _CONFIG is None:
        config_path = Path(__file__).parent.parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # Convert lists to sets where appropriate
        raw["loop_types"] = set(raw["loop_types"])
        raw["condition_types"] = set(raw["condition_types"])
        raw["event_types"] = set(raw["event_types"])
        raw["list_creators"] = set(raw["list_creators"])
        raw["list_operations"] = set(raw["list_operations"])
        raw["dictionary_operations"] = set(raw["dictionary_operations"])
        raw["variable_block_types"] = set(raw["variable_block_types"])
        raw["image_extensions"] = set(raw["image_extensions"])
        raw["audio_extensions"] = set(raw["audio_extensions"])
        raw["video_extensions"] = set(raw["video_extensions"])
        _CONFIG = raw
    return _CONFIG

def get_config():
    """Return the loaded configuration (loads it if not already loaded)."""
    return load_config()

def get_loop_types() -> Set[str]:
    return get_config()["loop_types"]

def get_condition_types() -> Set[str]:
    return get_config()["condition_types"]

def get_event_types() -> Set[str]:
    return get_config()["event_types"]

def get_list_creators() -> Set[str]:
    return get_config()["list_creators"]

def get_list_operations() -> Set[str]:
    return get_config()["list_operations"]

def get_dictionary_operations() -> Set[str]:
    return get_config()["dictionary_operations"]

def get_variable_block_types() -> Set[str]:
    return get_config()["variable_block_types"]

def get_matrix_operations() -> Set[str]:
    return set(get_config().get("matrix_operations", []))

def get_data_persistence_operations() -> Set[str]:
    return set(get_config().get("data_persistence_operations", []))

def get_scoring_rubric() -> Dict:
    return get_config()["scoring_rubric"]

def get_max_score() -> int:
    return sum(cat["max"] for cat in get_scoring_rubric().values())

def get_block_type_descriptions() -> Dict[str, str]:
    return get_config()["block_type_descriptions"]

def describe_block_type(block_type: str) -> str:
    descriptions = get_block_type_descriptions()
    return descriptions.get(block_type, f"Other block: {block_type}")

def get_image_extensions() -> Set[str]:
    return get_config()["image_extensions"]

def get_audio_extensions() -> Set[str]:
    return get_config()["audio_extensions"]

def get_video_extensions() -> Set[str]:
    return get_config()["video_extensions"]

def get_colours() -> Dict[str, str]:
    # This function is provided for consistency.
    return {}