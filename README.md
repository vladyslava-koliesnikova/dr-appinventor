# Dr. AppInventor

### Automated Static Analysis Tool for MIT App Inventor 2 Projects

Dr. AppInventor is a Python desktop application developed as part of my Bachelor's thesis at **Pavol Jozef Šafárik University in Košice, Slovakia**.

The tool performs automated static analysis of projects created in **MIT App Inventor 2**, helping educators examine students' block-based programs, identify potential issues, and evaluate selected aspects of computational thinking.

## Overview

Dr. AppInventor analyzes MIT App Inventor 2 project files (`.aia`) without executing the applications.

It extracts the project archive, processes the user interface structure (`.scm` files in JSON format) and block-based programming logic (`.bky` files in XML format), calculates structural metrics, and assigns scores based on a configurable evaluation rubric.

The results are displayed through a graphical user interface and can be exported to CSV.

The application was inspired by **Dr. Scratch**, a static analysis tool for Scratch projects, and adapts a similar approach to MIT App Inventor 2.

## Features

- **Automated project analysis** – processes `.aia` project archives
- **Computational thinking assessment** – evaluates projects across 10 categories using a 30-point scoring rubric
- **Block-based code analysis** – examines events, conditions, loops, variables, procedures, and data structures
- **Dead code detection** – identifies unreachable procedures, disconnected blocks, and unused variables
- **User interface analysis** – examines screens, UI components, and component naming
- **Data persistence analysis** – detects the use of local and cloud storage components
- **Multimedia analysis** – identifies images, audio, and video assets
- **Detailed feedback** – displays category scores, metrics, and potential issues
- **CSV export** – saves analysis results for further processing

## Technologies Used

- **Python 3.11+**
- **Tkinter** – desktop graphical user interface
- **XML parsing** – analysis of block-based program structures
- **JSON processing** – analysis of UI components and configuration
- **ZIP archive processing** – extraction of `.aia` project files
- **Pandas** – CSV export
- **Breadth-First Search (BFS)** – reachability analysis of procedures

## Requirements

- Python 3.11 or newer
- Pandas 2.0 or newer
- Tkinter (typically included with standard Python installations)

## Installation & Run

### 1. Clone the repository

```bash
git clone https://github.com/vladyslava-koliesnikova/dr-appinventor.git
cd dr-appinventor
```

### 2. Install dependencies

```bash
pip install "pandas>=2.0"
```

### 3. Run the application

```bash
python main.py
```

The desktop application will open in a new window.

## How to Use

1. Click **Open .aia File** and select an MIT App Inventor 2 project.
2. Click **Analyze Project** to start the static analysis.
3. Review the results displayed in the application:
   - **Category Scores** – scores and explanations for each evaluation category
   - **Detailed Metrics** – quantitative indicators grouped by topic
   - **Component Naming Analysis** – default and custom component names
   - **Variable Analysis** – global and local variables, unused variables, and naming issues
   - **Procedure Analysis** – defined, reachable, and unreachable procedures
   - **Multimedia Assets** – images, audio, and video
   - **Supplementary Block Types** – additional blocks not directly affecting the score
   - **Code Quality Issues Summary** – dead code, naming issues, and disconnected blocks
   - **Analysis Warnings** – other detected issues
4. Click **Export Results to CSV** to save the analysis results.

## Scoring Rubric

The tool evaluates projects across **10 categories**, with a maximum total score of **30 points**.

| Category | Max Points | What Is Measured |
|---|---:|---|
| User Interface Complexity | 4 | Screens, visible components, multimedia assets |
| User Interactivity | 4 | Number of event handlers |
| Event Diversity | 4 | Variety of event types |
| Logic | 4 | Conditional statements, branches, and nesting |
| Variables | 3 | Used global and local variables, meaningful names |
| Procedures | 3 | Reachable procedures, parameters, and return values |
| Loops | 3 | Loop count, variety, and nesting |
| Composite Data Types | 2 | Lists, dictionaries, and matrices |
| Data Persistence | 2 | Local and cloud storage components |
| Dead Code | 1 | Unused procedures, disconnected blocks, and unused variables |
| **Total** | **30** | |

### Evaluation Levels

| Score | Level |
|---|---|
| 25–30 | Advanced |
| 19–24 | Proficient |
| 12–18 | Developing |
| 0–11 | Basic |

These levels provide a simplified overview of selected structural and programming characteristics. They are not intended to represent a complete assessment of software quality.

## Dead Code Detection

Dr. AppInventor identifies several types of potentially unused code.

**Unreachable Procedures**

The tool analyzes procedure calls using a graph-based approach. Breadth-First Search (BFS) is used to determine which procedures are reachable from event handlers.

**Disconnected Blocks**

Blocks that are not connected to executable event or procedure structures are identified as floating blocks.

**Unused Variables**

Variables declared but not referenced in the analyzed program are reported.

This information can help educators identify unnecessary code and discuss programming practices with students.

## Project Structure

```text
DrAppInventor/
├── main.py                     # Application entry point
├── config.json                 # Block definitions and scoring configuration
├── core/
│   ├── pipeline.py             # Coordinates the analysis process
│   ├── project_extractor.py    # Extracts .aia archives
│   ├── scm_parser.py           # Parses UI structure (.scm / JSON)
│   ├── bky_parser.py           # Parses block logic (.bky / XML)
│   ├── block_analyzer.py       # Analyzes blocks and program structures
│   ├── assets_analyzer.py      # Detects multimedia assets
│   ├── metrics_aggregator.py   # Aggregates metrics across screens
│   ├── reachable_procedures.py # Procedure reachability analysis
│   └── scoring.py              # Applies the evaluation rubric
├── gui/
│   └── app_gui.py              # Tkinter graphical user interface
└── utils/
    └── helpers.py              # Configuration and utility functions
```

## Evaluation and Results

The application was evaluated using **16 real student projects** developed in MIT App Inventor 2.

Three projects of different complexity levels were examined in greater detail:

| Project | Blocks | Score | Level |
|---|---:|---:|---|
| Pripomienkovač | 11 | 6/30 | Basic |
| Spoznaj vedu | 324 | 13/30 | Developing |
| Digitálny herbár | 59 | 21/30 | Proficient |

The evaluation demonstrated that the number of programming blocks alone does not necessarily indicate a higher level of programming complexity.

The tool provided different scores for projects with different structural characteristics, supporting its usefulness for preliminary quantitative assessment.

## Limitations

Dr. AppInventor performs **static analysis only** and does not execute the analyzed applications.

Consequently:

- It cannot verify whether an application behaves correctly at runtime.
- Its evaluation focuses primarily on quantitative and structural properties.
- It does not fully recognize recursive algorithms or hierarchical decomposition through procedure calls.
- It cannot comprehensively assess code readability, algorithmic correctness, or overall software quality.

The tool is intended to **support educators**, not replace human evaluation.

## Bachelor's Thesis

**Original title:** *Automatický nástroj na analýzu projektov vytvorených v MIT App Inventor 2*

**English title:** *Automated Tool for Analyzing Projects Created in MIT App Inventor 2*

**Author:** Vladyslava Koliesnikova

**University:** Pavol Jozef Šafárik University in Košice, Slovakia

**Faculty:** Faculty of Science

**Thesis supervisor:** RNDr. Dominika Kotlárová

The Bachelor's thesis focused on three main objectives:

1. Reviewing existing tools for analyzing projects developed in block-based programming environments.
2. Designing and implementing an automated analysis tool for MIT App Inventor 2 projects.
3. Evaluating the tool using real student projects.

The resulting application provides a foundation for further development, including more advanced code quality analysis, improved detection of programming patterns, and batch processing of student projects.


Developed as a Bachelor's thesis project at **Pavol Jozef Šafárik University in Košice**.
