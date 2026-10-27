import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Any

def parse_scm(scm_content: str) -> dict:
    """Parse a .scm file (JSON wrapped in #| $JSON ... |#)."""
    json_match = re.search(r"\$JSON\s*(\{.*\})\s*\|#", scm_content, re.DOTALL)
    json_string = json_match.group(1) if json_match else scm_content.strip()
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return {}

def extract_screen_information(scm_data: dict) -> dict:
    """Extract screen name, component counts and component names from .scm data."""
    properties = scm_data.get("Properties", {})
    screen_name = properties.get("$Name", "Unknown")

    component_type_counts = defaultdict(int)
    component_names_and_types = []

    def traverse_components(node: dict):
        if not isinstance(node, dict):
            return
        comp_type = node.get("$Type", "")
        comp_name = node.get("$Name", "")
        if comp_type:
            component_type_counts[comp_type] += 1
        if comp_name and comp_type != "Form":
            component_names_and_types.append((comp_name, comp_type))
        for child in node.get("$Components", []):
            traverse_components(child)

    traverse_components(properties)
    component_type_counts.pop("Form", None)

    return {
        "screen_name": screen_name,
        "component_type_counts": dict(component_type_counts),
        "component_names_and_types": component_names_and_types,
        "total_components": sum(component_type_counts.values()),
    }