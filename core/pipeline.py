from pathlib import Path
from core.project_extractor import extract_project
from core.scm_parser import parse_scm, extract_screen_information
from core.bky_parser import parse_bky
from core.block_analyzer import analyze_blocks
from core.assets_analyzer import analyse_assets
from core.metrics_aggregator import aggregate_project_metrics
from core.scoring import evaluate_project
import pandas as pd
import shutil
from utils.helpers import describe_block_type

def run_analysis(project_file_path: Path, progress_callback=None) -> tuple:
    """Complete analysis: extract, scan, compute metrics, score."""
    temp_dir = extract_project(project_file_path)
    warnings = []

    try:
        screens = []
        bky_roots = []

        for file_path in temp_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix == ".scm":
                content = file_path.read_text(encoding="utf-8", errors="replace")
                scm_data = parse_scm(content)
                if scm_data:
                    screens.append(extract_screen_information(scm_data))
            elif file_path.suffix == ".bky":
                content = file_path.read_text(encoding="utf-8", errors="replace")
                root = parse_bky(content)
                if root is not None:
                    screen_name = file_path.stem
                    bky_roots.append((root, screen_name))
            if progress_callback:
                progress_callback()

        blocks_data = []
        unknown_by_screen = {}

        for root, screen_name in bky_roots:
            block_metrics = analyze_blocks(root, screen_name, warnings)
            blocks_data.append(block_metrics)

            if block_metrics.get("unknown_block_types"):
                screen_unknown = {}
                for bt, cnt in block_metrics["unknown_block_types"].items():
                    desc = describe_block_type(bt)
                    screen_unknown[desc] = screen_unknown.get(desc, 0) + cnt
                unknown_by_screen[screen_name] = screen_unknown

        assets = analyse_assets(temp_dir)
        aggregated = aggregate_project_metrics(screens, blocks_data, assets, unknown_by_screen)

        aggregated["unknown_block_types_per_screen"] = unknown_by_screen

        scores = evaluate_project(aggregated)

        rows = []
        for category, data in scores.items():
            rows.append({
                "Category": category,
                "Score": data["score"],
                "Maximum": data["max"],
                "Level": f"{data['score']}/{data['max']}",
                "Description": "",
                "Note": data["note"],
            })
        score_table = pd.DataFrame(rows)

        floating_count = aggregated.get("floating_block_count", 0)
        # Zoznam podrobných varovaní o plávajúcich blokoch (zoznam reťazcov)
        floating_warnings_list = warnings.copy()  # warnings obsahuje hlásenia z analyze_blocks
        warnings.clear()
        bad_habits = {
            "Dead procedures": sorted(aggregated["dead_procedures"]),
            "Floating blocks": {
                "count": floating_count,
                "details": floating_warnings_list
            },
            "Unused variables": sorted([f"{var} (global)" for var in aggregated["unused_global_variables"]] +
                               [f"{var} (local)" for var in aggregated["unused_local_variables"]]),
            "Poor variable names": sorted(aggregated["bad_variable_names"]),
            "Default component names": sorted(aggregated["default_component_names"]),
        }

        aggregated["human_readable_unknown_types"] = {
            describe_block_type(bt): count for bt, count in aggregated["unknown_block_type_counts"].items()
        }

        return aggregated, scores, score_table, bad_habits, warnings

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)