from collections import defaultdict
import re
from typing import List, Dict, Set, Any, Optional
from core.reachable_procedures import compute_reachable_procedures

def aggregate_project_metrics(
    screens_data: list,
    blocks_data: list,
    assets_data: dict,
    unknown_by_screen: Optional[dict] = None
) -> dict:
    """Combine screen and block data, subtract dead procedure contributions."""
    # UI aggregation
    total_components = sum(screen["total_components"] for screen in screens_data)
    all_component_type_counts = defaultdict(int)
    all_component_names = []
    for screen in screens_data:
        for comp_type, count in screen["component_type_counts"].items():
            all_component_type_counts[comp_type] += count
        all_component_names.extend(screen.get("component_names_and_types", []))

    # Block metrics aggregation (initial)
    declared_global_vars = set()
    declared_local_vars = set()
    used_global_vars = set()
    used_local_vars = set()
    all_procedures_defined = {}
    all_procedures_called = set()

    total_blocks = total_conditions = total_complex = total_loops = 0
    total_events = total_list_creations = total_list_ops = total_dict_blocks = 0
    total_matrix_blocks = total_persistence_blocks = 0
    total_clouddb = total_tinydb = total_cloud_advanced = total_local_file = 0
    total_nested_cond = total_nested_loop = max_depth_overall = 0
    all_loop_types = set()
    all_event_types = set()
    has_else = False

    total_component_methods = total_property_sets = total_property_gets = 0
    all_unknown_types = defaultdict(int)
    call_graph = defaultdict(set)
    event_called_procedures = set()
    per_procedure_metrics = {}

    total_floating_blocks = 0

    for block_data in blocks_data:
        total_floating_blocks += block_data.get("floating_block_count", 0)
        declared_global_vars.update(block_data.get("declared_global_variables", set()))
        declared_local_vars.update(block_data.get("declared_local_variables", set()))
        used_global_vars.update(block_data.get("used_global_variables", set()))
        used_local_vars.update(block_data.get("used_local_variables", set()))

        all_procedures_defined.update(block_data["procedures_defined"])
        all_procedures_called.update(block_data["procedures_called"])

        total_blocks         += block_data["total_blocks"]
        total_conditions     += block_data["condition_blocks"]
        has_else             = has_else or block_data["has_else"]
        total_complex        += block_data["complex_conditions"]
        total_loops          += block_data["loops"]
        all_loop_types.update(block_data["loop_types"])
        total_events         += block_data["event_handlers"]
        all_event_types.update(block_data["event_types"])
        total_list_creations += block_data["list_creation_blocks"]
        total_list_ops       += block_data["list_operation_blocks"]
        total_dict_blocks    += block_data.get("dictionary_blocks", 0)
        total_matrix_blocks  += block_data.get("matrix_blocks", 0)
        total_persistence_blocks += block_data.get("data_persistence_blocks", 0)
        total_clouddb += block_data.get("clouddb_operations", 0)
        total_tinydb += block_data.get("tinydb_operations", 0)
        total_cloud_advanced += block_data.get("cloud_advanced_operations", 0)
        total_local_file += block_data.get("local_file_operations", 0)
        total_nested_cond    += block_data["nested_conditions"]
        total_nested_loop    += block_data["nested_loops"]
        max_depth_overall     = max(max_depth_overall, block_data.get("max_nesting_depth", 0))
        total_component_methods += block_data.get("component_method_calls", 0)
        total_property_sets  += block_data.get("component_property_sets", 0)
        total_property_gets  += block_data.get("component_property_gets", 0)

        for bt, cnt in block_data.get("unknown_block_types", {}).items():
            all_unknown_types[bt] += cnt

        for caller, callees in block_data.get("procedure_calls_map", {}).items():
            call_graph[caller].update(callees)

        event_called_procedures.update(block_data.get("event_called_procedures", set()))
        per_procedure_metrics.update(block_data.get("procedure_block_metrics", {}))

    # Dead procedure detection
    all_defined_names = set(all_procedures_defined.keys())
    reachable = compute_reachable_procedures(call_graph, event_called_procedures, all_defined_names)
    dead_procedures = all_defined_names - reachable

    # Subtract dead procedure contributions
    for dead_proc in dead_procedures:
        sub = per_procedure_metrics.get(dead_proc, {})
        total_blocks     -= sub.get("blocks", 0)
        total_conditions -= sub.get("conditions", 0)
        total_loops      -= sub.get("loops", 0)
        total_list_creations -= sub.get("list_creations", 0)
        total_list_ops   -= sub.get("list_operations", 0)
        total_dict_blocks-= sub.get("dict_blocks", 0)
        total_complex    -= sub.get("complex_conds", 0)
        total_nested_cond     -= sub.get("nested_conditions", 0)
        total_nested_loop     -= sub.get("nested_loops", 0)

    # Clamp to zero
    total_blocks     = max(0, total_blocks)
    total_conditions = max(0, total_conditions)
    total_loops      = max(0, total_loops)
    total_list_creations = max(0, total_list_creations)
    total_list_ops   = max(0, total_list_ops)
    total_dict_blocks= max(0, total_dict_blocks)
    total_complex    = max(0, total_complex)
    total_nested_cond = max(0, total_nested_cond)
    total_nested_loop = max(0, total_nested_loop)

    # Unused variables
    unused_global = declared_global_vars - used_global_vars
    unused_local  = declared_local_vars  - used_local_vars
    unused_vars   = unused_global | unused_local

    # Variable name quality — check names across both scopes
    # global and local variables are counted SEPARATELY even when they share the same name (different scopes).
    all_declared_vars = declared_global_vars | declared_local_vars
    BAD_NAME_PATTERN = re.compile(
        r"^(x\d*|y\d*|z\d*|temp\d*|var\d*|data\d*|num\d*|str\d*"
        r"|test\d*|foo|bar|baz|global\d*|result\d*|tmp\d*|abc|xyz"
        r"|a\d*|b\d*|n\d*)$",
        re.IGNORECASE,
    )
    bad_var_names = {v for v in all_declared_vars if BAD_NAME_PATTERN.match(v) or len(v) < 2}
    good_var_names = all_declared_vars - bad_var_names

    # Component naming: default vs custom
    def is_default_name(name: str, comp_type: str) -> bool:
        return bool(re.match(r"^" + re.escape(comp_type) + r"\d+$", name, re.IGNORECASE))

    default_comp_names = set()
    custom_comp_names = set()
    for name, comp_type in all_component_names:
        if name and comp_type:
            if is_default_name(name, comp_type):
                default_comp_names.add(name)
            else:
                custom_comp_names.add(name)

    total_named = len(default_comp_names) + len(custom_comp_names)
    custom_ratio = len(custom_comp_names) / total_named if total_named > 0 else 0.0

    result = {
        "screen_count": len(screens_data),
        "screen_names": [screen["screen_name"] for screen in screens_data],

        "total_components": total_components,
        "component_type_counts": dict(all_component_type_counts),
        "unique_component_types": len(all_component_type_counts),
        "component_names": all_component_names,

        "block_count": total_blocks,
        "nesting_complexity": max_depth_overall,

        "global_variables": declared_global_vars,
        "local_variables": declared_local_vars,
        "used_global_variables": used_global_vars,
        "used_local_variables": used_local_vars,
        "unused_variables": unused_vars,
        "unused_global_variables": unused_global,
        "unused_local_variables": unused_local,
        "bad_variable_names": bad_var_names,
        "good_variable_names": good_var_names,
        "total_variables": len(declared_global_vars) + len(declared_local_vars),

        "procedures_defined": all_procedures_defined,
        "procedures_called": all_procedures_called,
        "call_graph": dict(call_graph),
        "entry_procedures": event_called_procedures,
        "reachable_procedures": reachable,
        "dead_procedures": dead_procedures,
        "procedures_with_parameters": sum(1 for p in all_procedures_defined.values() if p["has_parameters"]),
        "procedures_with_return": sum(1 for p in all_procedures_defined.values() if p["returns_value"]),

        "selection_structures": total_conditions,
        "has_else": has_else,
        "complex_conditions": total_complex,
        "nested_conditions": total_nested_cond,

        "iteration_structures": total_loops,
        "loop_types": all_loop_types,
        "nested_loops": total_nested_loop,

        "event_driven_count": total_events,
        "event_types": all_event_types,

        "list_creation_blocks": total_list_creations,
        "list_operation_blocks": total_list_ops,
        "dictionary_blocks": total_dict_blocks,
        "matrix_blocks": total_matrix_blocks,
        "data_persistence_blocks": total_persistence_blocks,
        "clouddb_operations": total_clouddb,
        "tinydb_operations": total_tinydb,
        "cloud_advanced_operations": total_cloud_advanced,
        "local_file_operations": total_local_file,
        "composite_data_total": total_list_creations + total_list_ops + total_dict_blocks + total_matrix_blocks,

        "default_component_names": default_comp_names,
        "custom_component_names": custom_comp_names,
        "custom_naming_ratio": custom_ratio,

        "component_method_calls": total_component_methods,
        "component_property_sets": total_property_sets,
        "component_property_gets": total_property_gets,

        "unknown_block_type_counts": dict(sorted(all_unknown_types.items(), key=lambda x: (-x[1], x[0]))),

        "floating_block_count": total_floating_blocks,

        "assets_total": assets_data["total_assets"],
        "assets_images": assets_data["image_assets"],
        "assets_audio": assets_data["audio_assets"],
        "assets_video": assets_data["video_assets"],
        "assets_other": assets_data["other_assets"],
        "asset_filenames": assets_data["asset_file_names"],
        "image_filenames": assets_data["image_filenames"],
        "audio_filenames": assets_data["audio_filenames"],
        "video_filenames": assets_data["video_filenames"],
    }

    if unknown_by_screen is not None:
        result["unknown_block_types_per_screen"] = unknown_by_screen
    else:
        result["unknown_block_types_per_screen"] = {}

    return result