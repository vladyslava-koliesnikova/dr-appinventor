from collections import defaultdict
import re
from typing import Set, Dict, List, Any, Optional
import xml.etree.ElementTree as ET
from utils.helpers import (
    get_loop_types, get_condition_types, get_event_types,
    get_list_creators, get_list_operations, get_dictionary_operations,
    get_variable_block_types, describe_block_type,
    get_matrix_operations, get_data_persistence_operations
)

_PROCEDURE_DEF_TYPES = frozenset({"procedures_defnoreturn", "procedures_defreturn"})
_GLOBAL_DECL_TYPE    = "global_declaration"


def analyze_blocks(xml_root: ET.Element, screen_name: str = "Unknown", warnings_list=None) -> dict:
    """
    Analyse a single .bky file (one screen). Returns detailed metrics.

    """

    # ------------------------------------------------------------------ #
    # Default metrics structure
    # ------------------------------------------------------------------ #
    default_metrics = {
        "declared_global_variables": set(),
        "declared_local_variables":  set(),
        "used_global_variables":     set(),
        "used_local_variables":      set(),
        "total_blocks":              0,
        "floating_block_count":      0,
        "procedures_defined":        {},
        "procedures_called":         set(),
        "procedure_calls_map":       defaultdict(set),
        "event_called_procedures":   set(),
        "procedure_block_metrics":   {},
        "condition_blocks":          0,
        "has_else":                  False,
        "complex_conditions":        0,
        "loops":                     0,
        "loop_types":                set(),
        "event_handlers":            0,
        "event_types":               set(),
        "list_creation_blocks":      0,
        "list_operation_blocks":     0,
        "dictionary_blocks":         0,
        "matrix_blocks":             0,
        "data_persistence_blocks":   0,
        "nested_conditions":         0,
        "nested_loops":              0,
        "max_nesting_depth":         0,
        "component_method_calls":    0,
        "component_property_sets":   0,
        "component_property_gets":   0,
        "unknown_block_types":       defaultdict(int),
    }

    if xml_root is None:
        return default_metrics

    # Copy structure
    metrics = {}
    for key, value in default_metrics.items():
        if isinstance(value, set):
            metrics[key] = set()
        elif isinstance(value, list):
            metrics[key] = []
        elif isinstance(value, dict):
            metrics[key] = defaultdict(set) if key == "procedure_calls_map" \
                           else (defaultdict(int) if key == "unknown_block_types" \
                           else {})
        else:
            metrics[key] = value

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    namespace = xml_root.tag.split("}")[0] + "}" if xml_root.tag.startswith("{") else ""

    def remove_ns(tag: str) -> str:
        return tag.replace(namespace, "") if namespace else tag

    def get_field_text(element, field_name: str) -> str:
        for child in element:
            if remove_ns(child.tag) == "field" and child.get("name") == field_name:
                return (child.text or "").strip()
        return ""

    def get_mutation_attr(element, attribute: str) -> str:
        m = element.find(f"{namespace}mutation") if namespace else element.find("mutation")
        return m.get(attribute, "") if m is not None else ""

    def get_method_name(element) -> str:
        """Get method name from a component_method block."""
        m = element.find(f"{namespace}mutation") if namespace else element.find("mutation")
        if m is not None:
            method = m.get("method_name", "")
            if method:
                return method
        # Inak z poľa METHOD_NAME
        for child in element:
            if remove_ns(child.tag) == "field" and child.get("name") == "METHOD_NAME":
                return (child.text or "").strip()
        return ""

    def iter_blocks(subtree):
        """Yield all <block> elements in subtree (including root if it is one)."""
        for el in subtree.iter():
            if remove_ns(el.tag) == "block":
                yield el

    def find_called_procedures(subtree) -> set:
        called = set()
        for node in iter_blocks(subtree):
            bt = node.get("type", "")
            if bt in ("procedures_callnoreturn", "procedures_callreturn"):
                name = get_mutation_attr(node, "name") or get_field_text(node, "PROCNAME")
                if name:
                    called.add(name)
        return called

    def count_subtree_metrics(subtree) -> dict:
        sub = {
            "blocks": 0, "conditions": 0, "loops": 0,
            "list_creations": 0, "list_operations": 0,
            "dict_blocks": 0, "complex_conds": 0,
            "nested_conditions": 0,
            "nested_loops": 0,
        }

        def _nested_in_subtree(node, target_types):
            def has_nested(blk, depth):
                best = depth
                for child in blk:
                    tag = remove_ns(child.tag)
                    if tag in ("value", "statement", "next"):
                        for subblk in child:
                            if remove_ns(subblk.tag) == "block":
                                bt2 = subblk.get("type", "")
                                nd = depth + 1 if bt2 in target_types else depth
                                best = max(best, has_nested(subblk, nd))
                return best

            return has_nested(node, 0) >= 2

        for node in iter_blocks(subtree):
            sub["blocks"] += 1
            bt = node.get("type", "")
            if bt in get_condition_types():
                sub["conditions"] += 1
                if _nested_in_subtree(node, get_condition_types()):
                    sub["nested_conditions"] += 1
            elif bt in get_loop_types():
                sub["loops"] += 1
                if _nested_in_subtree(node, get_loop_types()):
                    sub["nested_loops"] += 1
            elif bt in get_list_creators():
                sub["list_creations"] += 1
            elif bt in get_list_operations():
                sub["list_operations"] += 1
            elif bt in get_dictionary_operations():
                sub["dict_blocks"] += 1
            elif bt in ("logic_operation", "logic_negate"):
                sub["complex_conds"] += 1
        return sub

    event_types_set = get_event_types()
    attached_roots  = []
    floating_roots  = []

    for child in xml_root:
        if remove_ns(child.tag) != "block":
            continue
        bt = child.get("type", "")
        if bt in event_types_set or bt in _PROCEDURE_DEF_TYPES or bt == _GLOBAL_DECL_TYPE:
            attached_roots.append(child)
        else:
            floating_roots.append(child)

    # Count floating blocks (the root + all their descendants)
    floating_total = sum(
        sum(1 for _ in iter_blocks(fb))
        for fb in floating_roots
    )
    metrics["floating_block_count"] = floating_total

    if warnings_list is not None and floating_total > 0:
        warnings_list.append(
            f"Screen '{screen_name}': {floating_total} disconnected block(s) found "
            f"(not attached to any event handler or procedure). "
            f"These blocks never execute and are excluded from all metrics."
        )

    # Collect only the blocks that will actually run
    all_blocks = [b for root in attached_roots for b in iter_blocks(root)]
    metrics["total_blocks"] = len(all_blocks)

    # ------------------------------------------------------------------ #
    # First pass – count structural block types
    # ------------------------------------------------------------------ #
    for block in all_blocks:
        bt = block.get("type", "")

        if bt in get_loop_types():
            metrics["loops"] += 1
            metrics["loop_types"].add(bt)

        elif bt in get_condition_types():
            metrics["condition_blocks"] += 1

        elif bt in ("logic_operation", "logic_negate"):
            metrics["complex_conditions"] += 1

        elif bt in get_list_creators():
            metrics["list_creation_blocks"] += 1

        elif bt in get_list_operations():
            metrics["list_operation_blocks"] += 1

        elif bt in get_dictionary_operations():
            metrics["dictionary_blocks"] += 1

        elif bt in get_matrix_operations():
            metrics["matrix_blocks"] += 1

        elif bt in get_data_persistence_operations():
            metrics["data_persistence_blocks"] += 1

        elif bt in ("logic_boolean", "logic_true", "logic_false"):
            metrics["unknown_block_types"]["logic_boolean"] += 1

        elif bt == "component_method":
            metrics["component_method_calls"] += 1
            _comp = get_mutation_attr(block, "component_type")
            _method = get_mutation_attr(block, "method_name")
            _LOCAL_PERSIST = {"TinyDB", "File"}
            _CLOUD_PERSIST = {"CloudDB", "Spreadsheet", "TinyWebDB", "FirebaseDB"}
            _PERSIST_COMPONENTS = _LOCAL_PERSIST | _CLOUD_PERSIST

            _PERSIST_METHODS = {
                # TinyDB
                "StoreValue", "GetValue", "ClearTag", "ClearAll", "GetTags", "GetEntries",
                # CloudDB
                "AppendValueToList", "RemoveFirstFromList", "GetTagList",
                # File
                "SaveFile", "ReadFrom", "AppendToFile", "Delete",
                # Spreadsheet
                "AddRow", "ReadRow", "WriteRow", "WriteCell", "ReadCell",
                "ReadColumn", "WriteColumn", "ReadSheet", "AddColumn",
                "ReadRange", "WriteRange",
                # FirebaseDB
                "RemoveFirst", "Unauthenticate",
            }

            if _comp in _PERSIST_COMPONENTS and _method in _PERSIST_METHODS:
                metrics["data_persistence_blocks"] += 1
                if _comp == "CloudDB":
                    metrics["clouddb_operations"] = metrics.get("clouddb_operations", 0) + 1
                elif _comp == "TinyDB":
                    metrics["tinydb_operations"] = metrics.get("tinydb_operations", 0) + 1
                elif _comp in _CLOUD_PERSIST:  # Spreadsheet, TinyWebDB
                    metrics["cloud_advanced_operations"] = metrics.get("cloud_advanced_operations", 0) + 1
                elif _comp in _LOCAL_PERSIST:  # File
                    metrics["local_file_operations"] = metrics.get("local_file_operations", 0) + 1

        elif bt == "component_set_get":
            mode = get_mutation_attr(block, "set_or_get")
            if mode == "set":
                metrics["component_property_sets"] += 1
            elif mode == "get":
                metrics["component_property_gets"] += 1

        elif bt in event_types_set:
            metrics["event_handlers"] += 1
            comp_type  = get_mutation_attr(block, "component_type") or get_field_text(block, "COMPONENT_SELECTOR")
            event_name = get_mutation_attr(block, "event_name")     or get_field_text(block, "EVENT_NAME")
            event_key  = f"{comp_type}.{event_name}" if comp_type and event_name else (comp_type or event_name)
            if event_key:
                metrics["event_types"].add(event_key)
            metrics["event_called_procedures"].update(find_called_procedures(block))

        elif bt in get_variable_block_types() or bt.startswith("procedures_"):
            pass

        else:
            metrics["unknown_block_types"][bt] += 1

    # ------------------------------------------------------------------ #
    # Second pass – variables, procedures, if-else
    # ------------------------------------------------------------------ #
    for block in all_blocks:
        bt = block.get("type", "")

        if bt == _GLOBAL_DECL_TYPE:
            name = get_field_text(block, "NAME").strip()
            if name:
                metrics["declared_global_variables"].add(name)

        elif bt in ("local_declaration_statement", "local_declaration_expression"):
            # App Inventor may store multiple local vars in one block using VAR0, VAR1 …
            # Fall back to single "VAR" / "NAME" for older format.
            found_any = False
            for child in block:
                if remove_ns(child.tag) == "field" and child.get("name", "").startswith("VAR"):
                    raw = (child.text or "").strip()
                    if raw:
                        metrics["declared_local_variables"].add(raw)
                        found_any = True
            if not found_any:
                name = (get_field_text(block, "VAR") or get_field_text(block, "NAME")).strip()
                if name:
                    metrics["declared_local_variables"].add(name)

        elif bt in ("lexical_variable_get", "lexical_variable_set"):
            raw = (get_field_text(block, "VAR") or get_field_text(block, "NAME")).strip()
            if raw.startswith("global "):
                clean = raw[len("global "):].strip()
                if clean:
                    metrics["used_global_variables"].add(clean)
            elif raw:
                metrics["used_local_variables"].add(raw)

        elif bt in _PROCEDURE_DEF_TYPES:
            proc_name = get_field_text(block, "NAME")
            m_el = block.find(f"{namespace}mutation") if namespace else block.find("mutation")
            param_count = len(m_el.findall(f"{namespace}arg" if namespace else "arg")) \
                          if m_el is not None else 0
            if proc_name:
                metrics["procedures_defined"][proc_name] = {
                    "has_parameters": param_count > 0,
                    "parameter_count": param_count,
                    "returns_value":   bt == "procedures_defreturn",
                }
                metrics["procedure_calls_map"][proc_name].update(find_called_procedures(block))
                metrics["procedure_block_metrics"][proc_name] = count_subtree_metrics(block)

        elif bt in ("procedures_callnoreturn", "procedures_callreturn"):
            name = get_mutation_attr(block, "name") or get_field_text(block, "PROCNAME")
            if name:
                metrics["procedures_called"].add(name)

        elif bt == "controls_if":
            m_el = block.find(f"{namespace}mutation") if namespace else block.find("mutation")
            if m_el is not None and int(m_el.get("else", 0)) > 0:
                metrics["has_else"] = True

    def _ctrl_nesting(block_el, depth: int) -> int:

        best = depth
        for child in block_el:
            tag = remove_ns(child.tag)
            if tag == "statement":
                for sub in child:
                    if remove_ns(sub.tag) == "block":
                        best = max(best, _ctrl_nesting(sub, depth + 1))
            elif tag in ("value", "next"):
                for sub in child:
                    if remove_ns(sub.tag) == "block":
                        best = max(best, _ctrl_nesting(sub, depth))
        return best

    def _nested_target(block_el, target_types: set, depth: int) -> int:
        best = depth
        for child in block_el:
            tag = remove_ns(child.tag)
            if tag in ("value", "statement"):
                for sub in child:
                    if remove_ns(sub.tag) == "block":
                        nd = depth + 1 if sub.get("type", "") in target_types else depth
                        best = max(best, _nested_target(sub, target_types, nd))
            elif tag == "next":
                for sub in child:
                    if remove_ns(sub.tag) == "block":
                        best = max(best, _nested_target(sub, target_types, depth))
        return best

    # Nested conditions / loops
    for block in all_blocks:
        bt = block.get("type", "")
        if bt in get_condition_types():
            if _nested_target(block, get_condition_types(), 1) >= 2:
                metrics["nested_conditions"] += 1
        if bt in get_loop_types():
            if _nested_target(block, get_loop_types(), 1) >= 2:
                metrics["nested_loops"] += 1

    # Overall nesting depth: start each attached root at depth 1
    metrics["max_nesting_depth"] = max(
        (_ctrl_nesting(root, 1) for root in attached_roots),
        default=0
    )

    return metrics
