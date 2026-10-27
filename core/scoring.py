from utils.helpers import get_scoring_rubric


def evaluate_project(metrics: dict) -> dict:
    scores = {}
    # ------------------------------------------------------------------ #
    # 1. USER INTERFACE COMPLEXITY  (max 4)
    # ------------------------------------------------------------------ #
    ui_score = 0
    notes = []
    tc = metrics["total_components"]
    sc = metrics["screen_count"]
    at = metrics["assets_total"]

    if tc >= 3:
        ui_score += 1
        notes.append(f"{tc} component(s)")
    if tc >= 6:
        ui_score += 1
        notes.append("6+ components")

    has_multi_screen = sc >= 2
    has_assets = at >= 1

    if has_multi_screen or has_assets:
        ui_score += 1
        if has_multi_screen and has_assets:
            notes.append("multi-screen + media assets")
        elif has_multi_screen:
            notes.append("multi-screen")
        else:  # has_assets only
            notes.append("media assets")

    if has_multi_screen and has_assets:
        ui_score += 1

    scores["User Interface Complexity"] = {
        "score": min(4, ui_score),
        "max": 4,
        "note": ", ".join(notes) if notes else "Minimal user interface",
    }
    # ------------------------------------------------------------------ #
    # 2. USER INTERACTIVITY  (max 4)
    # ------------------------------------------------------------------ #
    ev = metrics["event_driven_count"]
    if ev == 0:
        inter_score, note = 0, "No event handlers"
    elif ev == 1:
        inter_score, note = 1, f"{ev} event – basic"
    elif ev <= 3:
        inter_score, note = 2, f"{ev} events – moderate"
    elif ev <= 6:
        inter_score, note = 3, f"{ev} events – active"
    else:
        inter_score, note = 4, f"{ev} events – highly interactive"
    scores["User Interactivity"] = {"score": inter_score, "max": 4, "note": note}

    # ------------------------------------------------------------------ #
    # 3. EVENT DIVERSITY  (max 4)
    # ------------------------------------------------------------------ #
    n_et = len(metrics["event_types"])
    if n_et == 0:
        ed_score, note = 0, "No event types"
    elif n_et == 1:
        ed_score, note = 1, "1 event type"
    elif n_et == 2:
        ed_score, note = 2, f"{n_et} event types"
    elif n_et == 3:
        ed_score, note = 3, f"{n_et} event types"
    else:
        ed_score, note = 4, f"{n_et} different event types"
    scores["Event Diversity"] = {"score": ed_score, "max": 4, "note": note}

    # ------------------------------------------------------------------ #
    # 4. LOGIC / CONDITIONALS  (max 4)
    # ------------------------------------------------------------------ #
    logic_score = 0
    notes = []
    sel = metrics["selection_structures"]
    if sel >= 1:
        logic_score += 1
        notes.append(f"{sel} condition(s)")
    if metrics["has_else"]:
        logic_score += 1
        notes.append("if-else used")
    if metrics["complex_conditions"] >= 1:
        logic_score += 1
        notes.append("complex condition (AND/OR/NOT)")
    if metrics["nested_conditions"] >= 1:
        logic_score += 1
        notes.append("nested conditions")
    scores["Logic"] = {
        "score": min(4, logic_score),
        "max": 4,
        "note": ", ".join(notes) if notes else "No conditions used",
    }
    # ------------------------------------------------------------------ #
    # 5. VARIABLES  (max 3)
    # ------------------------------------------------------------------ #
    var_score = 0
    notes = []

    used_globals = metrics["used_global_variables"] & metrics["global_variables"]
    used_locals = metrics["used_local_variables"] & metrics["local_variables"]
    used_vars = used_globals | used_locals
    n_used = len(used_vars)

    good_used = {v for v in used_vars if v in metrics["good_variable_names"]}
    good_ratio = len(good_used) / n_used if n_used > 0 else 0.0

    if n_used >= 1:
        var_score += 1
        notes.append(f"{n_used} used variable(s)")
    if n_used >= 2:
        var_score += 1
        notes.append("multiple used variables")
    if n_used >= 2 and good_ratio >= 0.5:
        var_score += 1
        notes.append("meaningful names")

    scores["Variables"] = {
        "score": min(3, var_score),
        "max": 3,
        "note": ", ".join(notes) if notes else "No used variables",
    }

    # ------------------------------------------------------------------ #
    # 6. PROCEDURES (max 3)
    # ------------------------------------------------------------------ #
    proc_score = 0
    notes = []
    defined_procs = metrics["procedures_defined"]
    reachable = metrics.get("reachable_procedures", set())
    live_procs = {k: v for k, v in defined_procs.items() if k in reachable}
    n_live = len(live_procs)

    if n_live >= 1:
        proc_score += 1
        notes.append(f"{n_live} procedure(s)")
    if any(p["has_parameters"] for p in live_procs.values()):
        proc_score += 1
        notes.append("with parameters")
    if any(p["returns_value"] for p in live_procs.values()):
        proc_score += 1
        notes.append("returns value")

    scores["Procedures"] = {
        "score": min(3, proc_score),
        "max": 3,
        "note": ", ".join(notes) if notes else "No procedures defined",
    }

    # ------------------------------------------------------------------ #
    # 7. LOOPS  (max 3)
    # ------------------------------------------------------------------ #
    loop_score = 0
    notes = []
    loops = metrics["iteration_structures"]
    if loops >= 1:
        loop_score += 1
        notes.append(f"{loops} loop(s)")
    if len(metrics["loop_types"]) >= 2:
        loop_score += 1
        notes.append("different loop types")
    if metrics["nested_loops"] >= 1:
        loop_score += 1
        notes.append("nested loops")
    scores["Loops"] = {
        "score": min(3, loop_score),
        "max": 3,
        "note": ", ".join(notes) if notes else "No loops used",
    }
    # ------------------------------------------------------------------ #
    # 8. COMPOSITE DATA TYPES  (max 2)
    # ------------------------------------------------------------------ #
    list_created = metrics["list_creation_blocks"]
    has_dict = metrics["dictionary_blocks"] > 0
    has_matrix = metrics.get("matrix_blocks", 0) > 0

    if list_created == 0 and not has_dict and not has_matrix:
        data_score, note = 0, "No composite data used"
    elif list_created >= 2 or has_dict or has_matrix:
        data_score = 2
        parts = []
        if list_created >= 2:
            parts.append(f"{list_created} lists")
        elif list_created == 1:
            parts.append("1 list")
        if has_dict:
            parts.append("dictionary")
        if has_matrix:
            parts.append("matrix/2D list")
        note = " + ".join(parts)
    else:
        data_score = 1
        note = f"{list_created} list(s)"
    scores["Composite Data Types"] = {"score": data_score, "max": 2, "note": note}

    # ------------------------------------------------------------------ #
    # 9. DATA PERSISTENCE   (max 2)
    # ------------------------------------------------------------------ #
    clouddb = metrics.get("clouddb_operations", 0)
    tinydb = metrics.get("tinydb_operations", 0)
    cloud_adv = metrics.get("cloud_advanced_operations", 0)
    local_file = metrics.get("local_file_operations", 0)

    if clouddb > 0 or cloud_adv > 0:
        dp_score = 2
        parts = []
        if clouddb:
            parts.append("CloudDB")
        if cloud_adv:
            parts.append("Spreadsheet/TinyWebDB")
        dp_note = " + ".join(parts) + " – cloud storage"
    elif tinydb > 0 or local_file > 0:
        dp_score = 1
        parts = []
        if tinydb:
            parts.append("TinyDB")
        if local_file:
            parts.append("File")
        dp_note = " + ".join(parts) + " – local storage"
    else:
        dp_score, dp_note = 0, "No persistent data storage used"

    scores["Data Persistence"] = {"score": dp_score, "max": 2, "note": dp_note}
    # ------------------------------------------------------------------ #
    # 10. DEAD CODE  (max 1)
    # ------------------------------------------------------------------ #
    # All three types of unreachable / unused code must be absent for 1 point
    dead_procs = len(metrics["dead_procedures"])
    floating = metrics.get("floating_block_count", 0)
    unused_vars = len(metrics.get("unused_variables", set()))

    if dead_procs == 0 and floating == 0 and unused_vars == 0:
        dc_score = 1
        dc_note = "No dead code detected"
    else:
        dc_score = 0
        parts = []
        if dead_procs: parts.append(f"{dead_procs} dead procedure(s)")
        if floating:   parts.append(f"{floating} floating block(s)")
        if unused_vars: parts.append(f"{unused_vars} unused variable(s)")
        dc_note = " · ".join(parts)
    scores["Dead Code"] = {"score": dc_score, "max": 1, "note": dc_note}
    return scores
