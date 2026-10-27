import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
from typing import Optional
from core.pipeline import run_analysis

class DrAppInventorApp:
    COLOURS = {
        "background":            "#F5F5F5",
        "header_background":     "#2C3E50",
        "card_background":       "#FFFFFF",
        "card_border":           "#E0E0E0",
        "accent":                "#3498DB",
        "accent_dark":           "#2980B9",
        "success":               "#27AE60",
        "warning":               "#E67E22",
        "danger":                "#E74C3C",
        "info":                  "#3498DB",
        "text_primary":          "#2C3E50",
        "text_secondary":        "#7F8C8D",
        "row_even":              "#FFFFFF",
        "row_odd":               "#F9F9F9",
        "header_row":            "#ECF0F1",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.project_path: Optional[Path] = None
        self.progress_frame: Optional[tk.Frame] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self._setup_window()
        self._build_interface()

    def _setup_window(self):
        self.root.title("Dr. AppInventor – MIT App Inventor 2 Project Analyzer")
        self.root.minsize(980, 700)
        self.root.configure(bg=self.COLOURS["background"])

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = min(int(screen_width * 0.9), 1400)
        height = min(int(screen_height * 0.9), 900)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")
    def _build_interface(self):
        self._build_header()
        main_body = tk.Frame(self.root, bg=self.COLOURS["background"])
        main_body.pack(fill="both", expand=True, padx=15, pady=12)

        # Left sidebar
        self.sidebar = tk.Frame(main_body, bg=self.COLOURS["background"], width=300)
        self.sidebar.pack(side="left", fill="y", padx=(0, 12))
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main content area
        self.content = tk.Frame(main_body, bg=self.COLOURS["background"])
        self.content.pack(side="right", fill="both", expand=True)
        self._show_empty_state()

    def _build_header(self):
        header = tk.Frame(self.root, bg=self.COLOURS["header_background"], height=55)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Dr. AppInventor", font=("Segoe UI", 18, "bold"),
                 bg=self.COLOURS["header_background"], fg="white").pack(side="left", padx=15, pady=12)
        tk.Label(header, text="Static analysis tool for MIT App Inventor 2 projects",
                 font=("Segoe UI", 10), bg=self.COLOURS["header_background"], fg="#BDC3C7").pack(side="left", padx=10)

    def _build_sidebar(self):
        file_card = self._create_card(self.sidebar, "Project Selection")
        self.file_label = tk.Label(file_card, text="No file selected",
                                   font=("Segoe UI", 9), wraplength=250,
                                   justify="left", bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"])
        self.file_label.pack(anchor="w", pady=(0, 8))
        self._create_button(file_card, "Open .aia File", self._select_project)
        self._create_button(file_card, "Analyze Project", self._start_analysis, bg=self.COLOURS["accent"])
        self.status_label = tk.Label(file_card, text="", font=("Segoe UI", 9, "italic"),
                                     bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"])
        self.status_label.pack(anchor="w", pady=(5, 0))

        self.score_card_area = tk.Frame(self.sidebar, bg=self.COLOURS["background"])
        self.score_card_area.pack(fill="x")
        self.export_card_area = tk.Frame(self.sidebar, bg=self.COLOURS["background"])
        self.export_card_area.pack(fill="x")

    def _show_empty_state(self):
        self._clear_content()
        empty_frame = tk.Frame(self.content, bg=self.COLOURS["background"])
        empty_frame.pack(fill="both", expand=True)
        tk.Label(empty_frame, text="Select a .aia project file and click Analyse",
                 font=("Segoe UI", 14, "bold"), bg=self.COLOURS["background"], fg=self.COLOURS["text_primary"]).pack(pady=(100, 10))
        tk.Label(empty_frame, text="Analysis results will appear here",
                 font=("Segoe UI", 10), bg=self.COLOURS["background"], fg=self.COLOURS["text_secondary"]).pack()

    def _select_project(self):
        file_path = filedialog.askopenfilename(
            title="Select MIT App Inventor project (.aia)",
            filetypes=[("App Inventor Project", "*.aia"), ("All Files", "*.*")]
        )
        if file_path:
            self.project_path = Path(file_path)
            self.file_label.configure(text=self.project_path.name, fg=self.COLOURS["text_primary"])
            self._set_status("Project file loaded", self.COLOURS["success"])

    def _start_analysis(self):
        if not self.project_path:
            messagebox.showwarning("No project selected", "Please open a .aia file first.")
            return
        self._set_status("Analysing...", self.COLOURS["accent"])
        self._show_progress_indicator()
        self.root.update()

        def progress_step():
            if self.progress_bar:
                self.progress_bar.step(1)
                self.root.update_idletasks()

        try:
            metrics, scores, score_table, bad_habits, warnings = run_analysis(
                self.project_path, progress_callback=progress_step
            )
            self._hide_progress_indicator()
            self._display_results(metrics, scores, score_table, bad_habits, warnings)
            self._set_status("Analysis complete", self.COLOURS["success"])
        except Exception as error:
            self._hide_progress_indicator()
            messagebox.showerror("Analysis error", f"Could not analyse the project:\n{error}")
            self._set_status("Analysis failed", self.COLOURS["danger"])

    def _show_progress_indicator(self):
        if self.progress_bar is not None:
            return
        self._clear_content()
        self.progress_frame = tk.Frame(self.content, bg=self.COLOURS["background"])
        self.progress_frame.pack(expand=True)
        tk.Label(self.progress_frame, text="Analysing project – please wait",
                 font=("Segoe UI", 12, "bold"), bg=self.COLOURS["background"], fg=self.COLOURS["accent"]).pack(pady=(100, 10))
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=260)
        self.progress_bar.pack()
        self.progress_bar.start(10)

    def _hide_progress_indicator(self):
        if self.progress_bar is not None:
            self.progress_bar.stop()
            self.progress_bar = None
        if self.progress_frame is not None:
            self.progress_frame.destroy()
            self.progress_frame = None

    def _display_results(self, metrics, scores, score_table, bad_habits, warnings):
        self._clear_content()

        canvas = tk.Canvas(self.content, bg=self.COLOURS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLOURS["background"])

        scrollable_frame.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda event: canvas.itemconfig(canvas.find_all()[0], width=event.width))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.root.bind_all("<MouseWheel>", on_mousewheel)

        self._draw_score_table(scrollable_frame, scores)
        self._draw_metrics_grid(scrollable_frame, metrics)
        self._draw_components_analysis(scrollable_frame, metrics)
        self._draw_variable_analysis(scrollable_frame, metrics)
        self._draw_procedure_analysis(scrollable_frame, metrics)
        self._draw_multimedia_assets(scrollable_frame, metrics)
        self._draw_unknown_block_statistics(scrollable_frame, metrics)
        self._draw_quality_issues(scrollable_frame, bad_habits)
        if warnings:
            self._draw_warnings(scrollable_frame, warnings)

        self._update_score_card(scores)
        self._update_export_controls(score_table, metrics)

    def _draw_score_table(self, parent, scores):
        self._section_title(parent, "Category Scores")
        table_frame = tk.Frame(parent, bg=self.COLOURS["card_background"],
                               highlightbackground=self.COLOURS["card_border"],
                               highlightthickness=1)
        table_frame.pack(fill="x", pady=(0, 12))

        header_row = tk.Frame(table_frame, bg=self.COLOURS["header_row"])
        header_row.pack(fill="x")
        columns = [("Category", 200), ("Score", 80), ("Notes", 420), ("", 40)]
        for col_index, (col_text, width) in enumerate(columns):
            tk.Label(header_row, text=col_text, font=("Segoe UI", 10, "bold"),
                     bg=self.COLOURS["header_row"], fg=self.COLOURS["text_primary"],
                     width=width // 8, anchor="w" if col_index < 2 else "center",
                     padx=10, pady=8).grid(row=0, column=col_index, sticky="ew")

        for idx, (category, data) in enumerate(scores.items()):
            bg = self.COLOURS["row_even"] if idx % 2 == 0 else self.COLOURS["row_odd"]
            row = tk.Frame(table_frame, bg=bg)
            row.pack(fill="x")

            tk.Label(row, text=category, anchor="w", font=("Segoe UI", 10),
                     bg=bg, fg=self.COLOURS["text_primary"],
                     padx=10, pady=8, width=28).grid(row=0, column=0, sticky="ew")

            self._draw_score_cell(row, data["score"], data["max"], bg)

            tk.Label(row, text=data["note"], anchor="w", font=("Segoe UI", 9),
                     bg=bg, fg=self.COLOURS["text_secondary"],
                     padx=10, pady=8, justify="left", wraplength=550).grid(row=0, column=2, sticky="ew")

            info_button = tk.Button(row, text="i", font=("Segoe UI", 9, "bold"),
                                    bg=bg, fg=self.COLOURS["info"], bd=0, cursor="hand2",
                                    activebackground=bg, command=lambda c=category: self._show_scoring_info(c))
            info_button.grid(row=0, column=3, padx=5, pady=5)

            row.grid_columnconfigure(0, minsize=200)
            row.grid_columnconfigure(1, minsize=80)
            row.grid_columnconfigure(2, weight=1)
            row.grid_columnconfigure(3, minsize=40)

    def _draw_score_cell(self, parent, score, maximum, background):
        cell = tk.Frame(parent, bg=background, padx=10, pady=8)
        cell.grid(row=0, column=1, sticky="ew")
        tk.Label(cell, text=f"{score} / {maximum}",
                 font=("Segoe UI", 9, "bold"), bg=background, fg=self.COLOURS["text_primary"]).pack()

    def _draw_metrics_grid(self, parent, metrics):
        self._section_title(parent, "Detailed Metrics")
        grid = tk.Frame(parent, bg=self.COLOURS["background"])
        grid.pack(fill="x", pady=(0, 10))

        composite_data = (metrics["list_creation_blocks"]
                          + metrics.get("dictionary_blocks", 0)
                          + metrics.get("matrix_blocks", 0))
        tiles = [
            # UI & Components (zodpovedá User Interface Complexity)
            ("Screens", metrics["screen_count"], False),
            ("Components", metrics["total_components"], False),
            ("Component Types", metrics["unique_component_types"], False),
            ("Assets", metrics["assets_total"], False),
            # Events (zodpovedá User Interactivity + Event Diversity)
            ("Event Handlers", metrics["event_driven_count"], False),
            ("Event Types", len(metrics["event_types"]), False),
            # Logic
            ("Conditions", metrics["selection_structures"], False),
            ("Nesting Depth", metrics.get("nesting_complexity", 0), False),
            # Variables
            ("Global Variables", len(metrics.get("global_variables", set())), False),
            ("Local Variables", len(metrics.get("local_variables", set())), False),
            ("Unused Variables", len(metrics["unused_variables"]), True),
            # Procedures
            ("Procedures", len(metrics["procedures_defined"]), False),
            ("Reachable Procedures", len(metrics["reachable_procedures"]), False),
            ("Dead Procedures", len(metrics["dead_procedures"]), True),
            # Loops
            ("Loops", metrics["iteration_structures"], False),
            # Composite Data + Persistence
            ("Composite Data Blocks", composite_data, False),
            ("Data Persistence Blocks", metrics.get("data_persistence_blocks", 0), False),
            # Dead code
            ("Floating Blocks", metrics.get("floating_block_count", 0), True),
            # Block stats
            ("Block Count", metrics["block_count"], False),
            ("Method Calls", metrics.get("component_method_calls", 0), False),
            ("Property Sets", metrics.get("component_property_sets", 0), False),
            ("Property Gets", metrics.get("component_property_gets", 0), False),
        ]

        columns = 4
        for idx, (label, value, is_warning) in enumerate(tiles):
            row, col = divmod(idx, columns)
            tile = tk.Frame(grid, bg=self.COLOURS["card_background"],
                            highlightbackground=self.COLOURS["card_border"],
                            highlightthickness=1, padx=10, pady=8)
            tile.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            colour = self.COLOURS["danger"] if is_warning and value > 0 else self.COLOURS["accent_dark"]
            tk.Label(tile, text=str(value), font=("Segoe UI", 18, "bold"),
                     bg=self.COLOURS["card_background"], fg=colour).pack()
            tk.Label(tile, text=label, font=("Segoe UI", 8),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack()
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1)

    def _draw_components_analysis(self, parent, metrics):
        self._section_title(parent, "Components Analysis")
        card = self._create_inline_card(parent, "Components")

        # Časť 1: Typy komponentov a ich počty
        comp_types = metrics.get("component_type_counts")
        if comp_types and isinstance(comp_types, dict):
            tk.Label(card, text="Component types used:", font=("Segoe UI", 9, "bold"),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["accent_dark"]).pack(anchor="w", pady=(0, 2))
            text = " | ".join(f"{ctype} ({count})" for ctype, count in sorted(comp_types.items()))
            tk.Label(card, text=text, font=("Segoe UI", 9), bg=self.COLOURS["card_background"],
                     fg=self.COLOURS["text_secondary"], wraplength=850, justify="left").pack(anchor="w", pady=(0, 8))

        # Časť 2: Názvy komponentov (custom vs default)
        custom = metrics.get("custom_component_names", set())
        default = metrics.get("default_component_names", set())

        if custom:
            shown = sorted(custom)[:20]
            tk.Label(card, text="Custom names (good):", font=("Segoe UI", 9, "bold"),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["success"]).pack(anchor="w", pady=(0, 2))
            tk.Label(card, text="  ·  ".join(shown), font=("Segoe UI", 9),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["success"],
                     wraplength=850, justify="left").pack(anchor="w", pady=(0, 2))
            if len(custom) > 20:
                tk.Label(card, text=f"... and {len(custom) - 20} more", font=("Segoe UI", 9, "italic"),
                         bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w",
                                                                                                     pady=(0, 4))

        if default:
            shown = sorted(default)[:20]
            tk.Label(card, text="Default names (rename):", font=("Segoe UI", 9, "bold"),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["danger"]).pack(anchor="w", pady=(0, 2))
            tk.Label(card, text="  ·  ".join(shown), font=("Segoe UI", 9),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["danger"],
                     wraplength=850, justify="left").pack(anchor="w", pady=(0, 2))
            if len(default) > 20:
                tk.Label(card, text=f"... and {len(default) - 20} more", font=("Segoe UI", 9, "italic"),
                         bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w",
                                                                                                     pady=(0, 4))

        if not custom and not default:
            tk.Label(card, text="No components detected.", font=("Segoe UI", 9),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")

        # Pomer vlastných názvov
        total_named = len(custom) + len(default)
        if total_named > 0:
            ratio_percent = round(len(custom) / total_named * 100)
            tk.Label(card, text=f"Custom naming ratio: {ratio_percent}%  ({len(custom)} / {total_named})",
                     font=("Segoe UI", 9, "italic"), bg=self.COLOURS["card_background"],
                     fg=self.COLOURS["text_secondary"]).pack(anchor="w", pady=(6, 0))
    def _draw_variable_analysis(self, parent, metrics):
        self._section_title(parent, "Variable Analysis")
        card = self._create_inline_card(parent, "Variables")

        global_vars   = metrics.get("global_variables", set())
        local_vars    = metrics.get("local_variables", set())
        unused_global = metrics.get("unused_global_variables", set())
        unused_local  = metrics.get("unused_local_variables", set())

        sections = [
            (f"Global variables ({len(global_vars)}):", global_vars, self.COLOURS["text_primary"]),
            (f"Local variables ({len(local_vars)}):", local_vars, self.COLOURS["text_secondary"]),
            ("Good names (meaningful):", metrics["good_variable_names"], self.COLOURS["success"]),
            ("Poor names (needs improvement):", metrics["bad_variable_names"], self.COLOURS["danger"]),
            (f"Unused global variables ({len(unused_global)}):", unused_global, self.COLOURS["danger"]),
            (f"Unused local variables ({len(unused_local)})", unused_local, self.COLOURS["danger"]),
        ]
        any_shown = False
        for label, names, colour in sections:
            if names:
                tk.Label(card, text=label + "  " + "  ·  ".join(sorted(names)),
                         font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=colour,
                         wraplength=850, justify="left").pack(anchor="w", pady=2)
                any_shown = True
        if not any_shown:
            tk.Label(card, text="No variables detected.",
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")

    def _draw_procedure_analysis(self, parent, metrics):
        self._section_title(parent, "Procedure Analysis")
        if not metrics["procedures_defined"]:
            card = self._create_inline_card(parent, "Procedures")
            tk.Label(card, text="No procedures defined.",
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")
            return

        card = self._create_inline_card(parent, "Procedures Defined")
        for proc_name, info in sorted(metrics["procedures_defined"].items()):
            param_text = f"({info['parameter_count']} parameter{'s' if info['parameter_count'] != 1 else ''})" if info["has_parameters"] else "(no parameters)"
            return_text = " -> returns value" if info["returns_value"] else ""
            if proc_name in metrics["dead_procedures"]:
                status = "  DEAD CODE"
                colour = self.COLOURS["danger"]
            elif proc_name in metrics.get("reachable_procedures", set()):
                status = "  reachable"
                colour = self.COLOURS["success"]
            else:
                status = ""
                colour = self.COLOURS["text_primary"]
            tk.Label(card, text=f"  • {proc_name}  {param_text}{return_text}{status}",
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=colour,
                     justify="left").pack(anchor="w", pady=1)

    def _draw_component_naming(self, parent, metrics):
        self._section_title(parent, "Component Naming Analysis")
        card = self._create_inline_card(parent, "Component Names")

        if metrics.get("custom_component_names"):
            shown = sorted(metrics["custom_component_names"])[:20]
            tk.Label(card, text="Custom (good):   " + "  ·  ".join(shown),
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["success"],
                     wraplength=750, justify="left").pack(anchor="w", pady=2)
            if len(metrics["custom_component_names"]) > 20:
                tk.Label(card, text=f"... and {len(metrics['custom_component_names']) - 20} more",
                         font=("Segoe UI", 9, "italic"), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")

        if metrics.get("default_component_names"):
            shown = sorted(metrics["default_component_names"])[:20]
            tk.Label(card, text="Default (rename): " + "  ·  ".join(shown),
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["danger"],
                     wraplength=750, justify="left").pack(anchor="w", pady=2)
            if len(metrics["default_component_names"]) > 20:
                tk.Label(card, text=f"... and {len(metrics['default_component_names']) - 20} more",
                         font=("Segoe UI", 9, "italic"), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")

        if not metrics.get("custom_component_names") and not metrics.get("default_component_names"):
            tk.Label(card, text="No components detected.",
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")

        ratio_percent = round(metrics["custom_naming_ratio"] * 100)
        total_named = len(metrics.get("custom_component_names", set())) + len(metrics.get("default_component_names", set()))
        tk.Label(card, text=f"Custom naming ratio: {ratio_percent}%  ({len(metrics.get('custom_component_names', set()))} / {total_named})",
                 font=("Segoe UI", 9, "italic"), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w", pady=(6, 0))

    def _draw_multimedia_assets(self, parent, metrics):
        self._section_title(parent, "Multimedia Assets")
        card = self._create_inline_card(parent, "Assets")
        tk.Label(card,
                 text=f"Total: {metrics['assets_total']}     Images: {metrics['assets_images']}     Audio: {metrics['assets_audio']}     Video: {metrics['assets_video']}     Other: {metrics['assets_other']}",
                 font=("Segoe UI", 10), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_primary"],
                 wraplength=850, justify="left").pack(anchor="w")

        def add_file_row(label, files, colour):
            if files:
                shown = sorted(files)[:12]
                tk.Label(card, text=f"{label}   " + "  ·  ".join(shown),
                         font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=colour,
                         wraplength=850, justify="left").pack(anchor="w", pady=2)
                if len(files) > 12:
                    tk.Label(card, text=f"... and {len(files) - 12} more", font=("Segoe UI", 9, "italic"),
                             bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")

        add_file_row("Image files:", metrics.get("image_filenames", []), self.COLOURS["info"])
        add_file_row("Audio files:", metrics.get("audio_filenames", []), self.COLOURS["success"])
        add_file_row("Video files:", metrics.get("video_filenames", []), self.COLOURS["accent"])

        if metrics["assets_total"] == 0:
            tk.Label(card, text="No multimedia files found in the assets folder.",
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w", pady=4)

    def _draw_unknown_block_statistics(self, parent, metrics):
        self._section_title(parent, "Supplementary Block Types (Do Not Affect Score)")

        total_counts = metrics.get("human_readable_unknown_types", {})
        per_screen = metrics.get("unknown_block_types_per_screen", {})

        if not total_counts:
            card = self._create_inline_card(parent, "Other Blocks")
            tk.Label(card, text="No non‑core block types were found.",
                     font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["success"]).pack(
                anchor="w")
            return

        card = self._create_inline_card(parent, "Other Block Types Used")
        explanation = tk.Label(card,
                               text="The blocks listed below are not directly used for the computational thinking score.\n"
                                    "Click the 'i' button next to each block type to see on which screens it appears.",
                               font=("Segoe UI", 9), bg=self.COLOURS["card_background"],
                               fg=self.COLOURS["text_secondary"],
                               wraplength=850, justify="left")
        explanation.pack(anchor="w", pady=(0, 6))

        for block_desc, total_count in sorted(total_counts.items(), key=lambda x: -x[1]):
            frame = tk.Frame(card, bg=self.COLOURS["card_background"])
            frame.pack(anchor="w", fill="x", pady=1)

            label = tk.Label(frame, text=f"{block_desc}: {total_count}",
                             font=("Segoe UI", 9), bg=self.COLOURS["card_background"], fg=self.COLOURS["warning"],
                             justify="left")
            label.pack(side="left", padx=(0, 10))

            btn = tk.Button(frame, text="i", font=("Segoe UI", 9, "bold"),
                            bg=self.COLOURS["card_background"], fg=self.COLOURS["info"],
                            bd=0, cursor="hand2",
                            command=lambda desc=block_desc: self._show_unknown_block_details(desc, per_screen,
                                                                                             total_counts))
            btn.pack(side="left")

        if len(total_counts) > 15:
            tk.Label(card, text=f"... and {len(total_counts) - 15} more types",
                     font=("Segoe UI", 9, "italic"), bg=self.COLOURS["card_background"],
                     fg=self.COLOURS["text_secondary"]).pack(anchor="w")

    def _draw_quality_issues(self, parent, bad_habits):
        self._section_title(parent, "Code Quality Issues Summary")
        container = tk.Frame(parent, bg=self.COLOURS["card_background"],
                             highlightbackground=self.COLOURS["card_border"],
                             highlightthickness=1, padx=15, pady=12)
        container.pack(fill="x", pady=(0, 15))

        def has_items(item):
            if isinstance(item, dict):
                return item.get("count", 0) > 0
            elif isinstance(item, list):
                return len(item) > 0
            return False

        has_any = any(has_items(items) for items in bad_habits.values())
        if not has_any:
            tk.Label(container, text="No major quality issues detected.",
                     font=("Segoe UI", 10, "bold"), bg=self.COLOURS["card_background"],
                     fg=self.COLOURS["success"]).pack(anchor="w")
            return

        for habit, items in bad_habits.items():
            # Špeciálne spracovanie pre Floating blocks
            if habit == "Floating blocks" and isinstance(items, dict):
                count = items.get("count", 0)
                details = items.get("details", [])
                if count == 0:
                    continue
                colour = self.COLOURS["danger"]
                frame = tk.Frame(container, bg=self.COLOURS["card_background"])
                frame.pack(anchor="w", fill="x", pady=2)
                lbl = tk.Label(frame, text=f"{count}  {habit}", font=("Segoe UI", 10),
                               bg=self.COLOURS["card_background"], fg=colour, justify="left")
                lbl.pack(side="left")
                if details:
                    btn = tk.Button(frame, text="i", font=("Segoe UI", 9, "bold"),
                                    bg=self.COLOURS["card_background"], fg=self.COLOURS["info"],
                                    bd=0, cursor="hand2",
                                    command=lambda d=details: self._show_floating_warnings(d))
                    btn.pack(side="left", padx=(10, 0))
                continue

            if not isinstance(items, list) or len(items) == 0:
                continue
            count = len(items)
            colour = self.COLOURS["danger"] if count > 0 else self.COLOURS["success"]
            line = f"{count}  {habit}"
            if items:
                shown_items = ", ".join(str(item) for item in items[:8])
                if len(items) > 8:
                    shown_items += f" (+{len(items) - 8} more)"
                line += f":   {shown_items}"
            tk.Label(container, text=line, font=("Segoe UI", 10),
                     bg=self.COLOURS["card_background"], fg=colour,
                     justify="left", wraplength=750).pack(anchor="w", pady=2)
    def _draw_warnings(self, parent, warnings_list):
        self._section_title(parent, "Analysis Warnings")
        container = tk.Frame(parent, bg=self.COLOURS["card_background"],
                             highlightbackground=self.COLOURS["card_border"],
                             highlightthickness=1, padx=15, pady=12)
        container.pack(fill="x", pady=(0, 15))

        for warning in warnings_list[:10]:
            label = tk.Label(container, text=f"• {warning}", font=("Segoe UI", 9),
                             bg=self.COLOURS["card_background"], fg=self.COLOURS["warning"],
                             justify="left", wraplength=750, anchor="w")
            label.pack(anchor="w", fill="x", pady=2)
    def _show_scoring_info(self, category):
        info_texts = {
            "Logic": (
                "SCORING: LOGIC\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates conditionals and complex logic.\n\n"
                "0 points → no conditions\n"
                "1 point → at least 1 condition (if)\n"
                "2 points → if-else used\n"
                "3 points → any complex condition (AND/OR/NOT)\n"
                "4 points → nested conditions or (5+ conditions with 2+ AND/OR)\n\n"
            ),
            "Loops": (
                "SCORING: LOOPS\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates iteration structures.\n\n"
                "0 points → no loops\n"
                "1 point → at least 1 loop\n"
                "2 points → at least 2 different loop types\n"
                "3 points → nested loops\n\n"
            ),
            "Variables": (
                "SCORING: VARIABLES\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates variable declarations and naming quality.\n"
                "Both global and local variables are counted.\n\n"
                "0 points → no variables\n"
                "1 point → at least 1 used  variable (global or local)\n"
                "2 points → at least 2 used  variables\n"
                "3 points → at least 2 used variables and 50%+ meaningful names\n\n"
            ),
            "Procedures": (
                "SCORING: PROCEDURES\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates user-defined procedures (abstraction).\n"
                "Only reachable (non-dead) procedures are counted.\n\n"
                "0 points → no procedure\n"
                "1 point → at least 1 reachable procedure\n"
                "2 points → procedure with parameters\n"
                "3 points → procedure that returns a value\n\n"
            ),
            "User Interactivity": (
                "SCORING: USER INTERACTIVITY\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates the number of event handlers.\n\n"
                "0 points → no events\n"
                "1 point  → 1 event\n"
                "2 points → 2–3 events\n"
                "3 points → 4–6 events\n"
                "4 points → 7+ events\n\n"
            ),
            "Event Diversity": (
                "SCORING: EVENT DIVERSITY\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates the diversity of event types used by the project.\n\n"
                "0 points → no event types\n"
                "1 point  → 1 event type\n"
                "2 points → 2 event types\n"
                "3 points → 3 event types\n"
                "4 points → 4+ event types\n\n"
            ),
            "Composite Data Types": (
                "SCORING: COMPOSITE DATA TYPES\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates use of lists, dictionaries, and matrices (2D lists).\n"
                "0 points → none\n"
                "1 point  → 1 list used\n"
                "2 points → 2+ lists used or 1 dictionary or 1 matrix\n\n"
            ),
            "Data Persistence": (
                "SCORING: DATA PERSISTENCE\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates the use of persistent data storage (databases).\n"
                "Data survives app restart.\n\n"
                "0 points → no database blocks\n"
                "1 point  → TinyDB or File(local storage)\n"
                "2 points → CloudDB, TinyWebDB, Spreadsheet or FirebaseDB (cloud storage, more advanced)\n\n"
            ),
            "User Interface Complexity": (
                "SCORING: USER INTERFACE COM"
                "PLEXITY\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates the complexity of the visible user interface.\n"
                "Note: only visible components count toward UI complexity.\n\n"
                "1 point → 3+ components\n"
                "2 points → 6+ components\n"
                "3 points → 2+ screens or at least 1 media asset\n"
                "4 points → 2+ screens and at least 1 media asset\n\n"
            ),
            "Dead Code": (
                "SCORING: DEAD CODE\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Evaluates the absence of all types of unreachable or unused code.\n\n"
                "1 point → no dead procedures and no floating blocks and no unused variables\n"
                "0 points → any of the above issues are present\n\n"
                "Dead procedures: defined but never called from any event handler.\n"
                "Floating blocks: placed on the canvas but not connected to any event or procedure.\n"
                "Unused variables: declared but never read or written after declaration.\n"
            ),
        }
        text = info_texts.get(category, f"No detailed information available for {category}.")
        messagebox.showinfo(f"Scoring details: {category}", text)

    def _show_unknown_block_details(self, block_description, per_screen, total_counts):
        lines = [f"Block type: {block_description}", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", ""]

        screen_info = []
        for screen, blocks in per_screen.items():
            if block_description in blocks:
                count = blocks[block_description]
                screen_info.append(f"• {screen}: {count}")

        if not screen_info:
            lines.append("This block type does not appear in any screen.")
        else:
            lines.extend(screen_info)

        total = total_counts.get(block_description, 0)
        lines.append(f"\nTotal occurrences: {total}")

        messagebox.showinfo(f"Details: {block_description}", "\n".join(lines))
    def _show_floating_warnings(self, details_list):
        if not details_list:
            messagebox.showinfo("Floating blocks", "No floating blocks detected.")
            return
        msg = "Floating blocks (disconnected blocks) per screen:\n\n" + "\n".join(details_list)
        messagebox.showinfo("Floating blocks details", msg)

    def _update_score_card(self, scores):
        for widget in self.score_card_area.winfo_children():
            widget.destroy()
        total = sum(data["score"] for data in scores.values())
        maximum = sum(data["max"] for data in scores.values())
        ratio = total / maximum if maximum else 0

        if ratio >= 0.83:
            level, colour, msg = "Advanced", self.COLOURS["success"], "Excellent work!"
        elif ratio >= 0.61:
            level, colour, msg = "Proficient", self.COLOURS["info"], "You are doing great!"
        elif ratio >= 0.39:
            level, colour, msg = "Developing", self.COLOURS["warning"], "Keep practising!"
        else:
            level, colour, msg = "Basic", self.COLOURS["danger"], "Room to grow."

        outer_frame = tk.Frame(self.score_card_area, bg=self.COLOURS["card_border"])
        outer_frame.pack(fill="x", pady=(8, 5))
        inner_frame = tk.Frame(outer_frame, bg=self.COLOURS["card_background"], padx=12, pady=12)
        inner_frame.pack(fill="x", padx=1, pady=1)

        banner = tk.Frame(inner_frame, bg=self.COLOURS["header_row"], padx=8, pady=8)
        banner.pack(fill="x", pady=(0, 8))
        tk.Label(banner, text="Total Score:", font=("Segoe UI", 11, "bold"),
                 bg=self.COLOURS["header_row"], fg=self.COLOURS["text_primary"]).pack(side="left")
        tk.Label(banner, text=f"{total} / {maximum}", font=("Segoe UI", 18, "bold"),
                 bg=self.COLOURS["header_row"], fg=self.COLOURS["accent"]).pack(side="right")

        tk.Label(inner_frame, text="Level:", font=("Segoe UI", 9),
                 bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w")
        tk.Label(inner_frame, text=level, font=("Segoe UI", 14, "bold"),
                 bg=self.COLOURS["card_background"], fg=colour).pack(anchor="w")
        tk.Label(inner_frame, text=msg, font=("Segoe UI", 9, "italic"),
                 bg=self.COLOURS["card_background"], fg=self.COLOURS["text_secondary"]).pack(anchor="w", pady=(2, 0))

    def _update_export_controls(self, score_table, metrics):
        for widget in self.export_card_area.winfo_children():
            widget.destroy()
        outer_frame = tk.Frame(self.export_card_area, bg=self.COLOURS["card_border"])
        outer_frame.pack(fill="x", pady=(0, 8))
        inner_frame = tk.Frame(outer_frame, bg=self.COLOURS["card_background"], padx=12, pady=10)
        inner_frame.pack(fill="x", padx=1, pady=1)
        self._create_button(inner_frame, "Export Results to CSV",
                            lambda: self._export_results(score_table, metrics), bg=self.COLOURS["success"])

    def _export_results(self, score_table, metrics):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("All Files", "*.*")],
            title="Save Analysis Results"
        )
        if not file_path:
            return
        try:
            score_table.to_csv(file_path, index=False)
            metrics_path = Path(file_path).with_name(Path(file_path).stem + "_metrics.csv")
            pd.DataFrame([{
                "block_count": metrics["block_count"],
                "nesting_complexity": metrics["nesting_complexity"],
                "total_variables": metrics["total_variables"],
                "good_variable_names_count": len(metrics["good_variable_names"]),
                "bad_variable_names_count": len(metrics["bad_variable_names"]),
                "unused_variables_count": len(metrics["unused_variables"]),
                "selection_structures": metrics["selection_structures"],
                "has_else": int(metrics["has_else"]),
                "complex_conditions": metrics["complex_conditions"],
                "iteration_structures": metrics["iteration_structures"],
                "nested_loops": metrics["nested_loops"],
                "event_driven_count": metrics["event_driven_count"],
                "event_types_count": len(metrics["event_types"]),
                "procedures_defined_count": len(metrics["procedures_defined"]),
                "procedures_with_parameters": metrics["procedures_with_parameters"],
                "procedures_with_return": metrics["procedures_with_return"],
                "reachable_procedures_count": len(metrics["reachable_procedures"]),
                "dead_procedures_count": len(metrics["dead_procedures"]),
                "list_creation_blocks": metrics["list_creation_blocks"],
                "list_operation_blocks": metrics["list_operation_blocks"],
                "dictionary_blocks": metrics["dictionary_blocks"],
                "composite_data_total": metrics["composite_data_total"],
                "screens_count": metrics["screen_count"],
                "total_components": metrics["total_components"],
                "unique_component_types": metrics["unique_component_types"],
                "default_component_names_count": len(metrics["default_component_names"]),
                "custom_component_names_count": len(metrics["custom_component_names"]),
                "custom_naming_ratio": round(metrics["custom_naming_ratio"], 3),
                "assets_total": metrics["assets_total"],
                "assets_images": metrics["assets_images"],
                "assets_audio": metrics["assets_audio"],
                "assets_video": metrics["assets_video"],
                "component_method_calls": metrics["component_method_calls"],
                "component_property_sets": metrics["component_property_sets"],
                "component_property_gets": metrics["component_property_gets"],
            }]).to_csv(metrics_path, index=False)
            messagebox.showinfo("Export completed", f"Results saved to:\n{file_path}\nand\n{metrics_path}")
        except Exception as error:
            messagebox.showerror("Export error", str(error))

    def _clear_content(self):
        try:
            self.root.unbind_all("<MouseWheel>")
        except Exception:
            pass
        for widget in self.content.winfo_children():
            widget.destroy()

    def _set_status(self, text, colour):
        self.status_label.configure(text=text, fg=colour)

    def _section_title(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 12, "bold"),
                 bg=self.COLOURS["background"], fg=self.COLOURS["text_primary"]).pack(anchor="w", pady=(8, 5))

    def _create_card(self, parent, title=None, padding_vertical=6):
        outer = tk.Frame(parent, bg=self.COLOURS["card_border"])
        outer.pack(fill="x", pady=padding_vertical)
        inner = tk.Frame(outer, bg=self.COLOURS["card_background"], padx=12, pady=10)
        inner.pack(fill="x", padx=1, pady=1)
        if title:
            tk.Label(inner, text=title, font=("Segoe UI", 10, "bold"),
                     bg=self.COLOURS["card_background"], fg=self.COLOURS["accent"]).pack(anchor="w", pady=(0, 6))
        return inner

    def _create_inline_card(self, parent, title):
        outer = tk.Frame(parent, bg=self.COLOURS["card_border"],
                         highlightbackground=self.COLOURS["card_border"],
                         highlightthickness=1)
        outer.pack(fill="x", pady=4)
        inner = tk.Frame(outer, bg=self.COLOURS["card_background"], padx=12, pady=10)
        inner.pack(fill="x", padx=1, pady=1)
        tk.Label(inner, text=title, font=("Segoe UI", 10, "bold"),
                 bg=self.COLOURS["card_background"], fg=self.COLOURS["accent_dark"]).pack(anchor="w", pady=(0, 5))
        return inner

    def _create_button(self, parent, label, command, bg=None):
        bg_colour = bg or self.COLOURS["accent_dark"]
        button = tk.Button(parent, text=label, command=command,
                           font=("Segoe UI", 9, "bold"),
                           bg=bg_colour, fg="white", relief="flat",
                           cursor="hand2", padx=12, pady=5, bd=0)
        button.pack(fill="x", pady=2)
        darker = self._darken_colour(bg_colour)
        button.bind("<Enter>", lambda e: button.configure(bg=darker))
        button.bind("<Leave>", lambda e: button.configure(bg=bg_colour))
        return button

    @staticmethod
    def _darken_colour(hex_colour, factor=0.85):
        hex_colour = hex_colour.lstrip("#")
        r, g, b = int(hex_colour[0:2], 16), int(hex_colour[2:4], 16), int(hex_colour[4:6], 16)
        return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"