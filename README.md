# Dr. AppInventor
### Static Analysis Tool for MIT App Inventor 2 Projects

---

## Overview
Dr. AppInventor is a desktop application that performs **static analysis** of MIT App Inventor 2 projects (`.aia` files). It extracts the project archive, parses the UI structure (`.scm`) and block-based logic (`.bky`), computes metrics, and evaluates computational thinking using a scoring rubric. Results are displayed in a GUI with CSV export.

Since the tool performs only **static analysis**, it cannot verify the runtime behaviour of the application. Testing whether the app works correctly remains the teacher's responsibility.
Dr. AppInventor is inspired by Dr. Scratch, a static analysis tool for Scratch projects. While Dr. Scratch focuses on block‑based programming in Scratch, Dr. AppInventor brings a similar approach to MIT App Inventor 2.
---

## Requirements
- Python 3.11+
- `pandas` 2.0+ → `pip install pandas`
- `tkinter` (included with standard Python)

---

## Installation & Run
```bash
pip install pandas
python main.py
```

---

## How to Use
1. Click **Open .aia File** and select your project.
2. Click **Analyze Project**.
3. Results appear in the right panel:
   - **Category Scores** – points per category with notes and info buttons.
   - **Detailed Metrics** – numeric indicators grouped by topic.
   - **Component Naming Analysis** – custom, default names.
   - **Variable Analysis** – global/local variables, unused, poor names.
   - **Procedure Analysis** – defined procedures, dead/reachable status.
   - **Multimedia Assets** – images, audio, video.
   - **Supplementary Block Types** – blocks not affecting score.
   - **Code Quality Issues Summary** – all dead code, naming issues, disconnected blocks.
   - **Analysis Warnings** – other issues.
4. Use **Export Results to CSV** to save scores and metrics.

---

## Scoring Rubric (10 categories, max 30 points)

| Category | Max | What is measured                                            |
|---|---|-------------------------------------------------------------|
| User Interface Complexity | 4 | Screens, visible components, media assets                   |
| User Interactivity | 4 | Number of event handlers                                    |
| Event Diversity | 4 | Number of distinct event types                              |
| Logic | 4 | Conditions, if-else, complex logic, nesting                 |
| Variables | 3 | Used variables (global + local), meaningful names           |
| Procedures | 3 | Reachable procedures, parameters, return values             |
| Loops | 3 | Loop count, variety, nesting                                |
| Composite Data Types | 2 | Lists, dictionaries, matrices                               |
| Data Persistence | 2 | TinyDB/File(local), CloudDB/Spreadsheet/TinyWebDB/FirebaseDB (cloud)  |
| Dead Code | 1 | No dead procedures, no floating blocks, no unused variables |

### Levels
| Score | Level |
|---|---|
| 25–30 | Advanced |
| 19–24 | Proficient |
| 12–18 | Developing |
| 0–11 | Basic |

---

## Dead Code Detection
- **Dead procedures** – defined but never called from any event handler (BFS on call graph)
- **Floating blocks** – placed on canvas but not connected to any event or procedure
- **Unused variables** – declared but never used in the program

---

## Code Structure
```
DrAppInventor/
├── main.py                    # Entry point
├── config.json                # Block type lists, rubric config
├── core/
│   ├── pipeline.py            # Orchestrates full analysis
│   ├── project_extractor.py   # Unzips .aia
│   ├── scm_parser.py          # Parses UI (.scm JSON)
│   ├── bky_parser.py          # Loads .bky XML
│   ├── block_analyzer.py      # Block-level analysis per screen
│   ├── assets_analyzer.py     # Multimedia asset detection
│   ├── metrics_aggregator.py  # Combines all screen metrics
│   ├── reachable_procedures.py# BFS dead code detection
│   └── scoring.py             # Applies scoring rubric
├── gui/
│   └── app_gui.py             # tkinter GUI
└── utils/
    └── helpers.py             # Config loader helpers
```