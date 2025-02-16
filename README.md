# Polytope Database Manager

This repository contains an interactive Python tool for managing a database of simple polytope edge lists and their computed properties. The tool can:

- **Recompute the entire CSV database**: Process all existing edge list files, compute their properties using custom `graphcalc` functions (with a `networkx` fallback), and generate a CSV file.
- **Add a new edge list**: Interactively prompt you to input a new polytope edge list. The file name is auto-generated (in sequential order), properties are computed and displayed for your verification, and the CSV database is updated.
- **Exit the program**

## Prerequisites

- Python 3.9 or higher
- [pip](https://pip.pypa.io/en/stable/)

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/jeddyhub/Polytope_Database
cd Polytope_Database
```

2. **Create a virtual environment (optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
```

3. **Install dependencies:**
A `requirements.txt` file has been generated using `pip freeze`. To install the required packages, run:

```bash
pip install -r requirements.txt
```

## Usage

To run the interactive polytope manager, simply execute:

```bash
python simple_polytope_manager.py
```

When the script runs, you'll be presented with a menu:

A: Recompute the entire CSV database
B: Add a new edge list to the database
C: Exit

Selecting this option A will prompt you for confirmation (warning that the existing CSV file will be overwritten). Process all edge list files from Simple_Polytope_Data/Edge_Data with a progress bar. Generate/update the CSV file (simple_polytope_properties.csv).

Selecting this option B will Automatically generate the next available file name (e.g., simple_polytope_2.txt). Prompt you to enter edges (one per line, either as "source target" or "source, target"). Type done to finish entering edges or restart at any time to cancel and return to the main menu. After saving, the script computes the properties for the new edge list and displays them. You'll then be asked to confirm whether the computed properties are correct before updating the CSV database.
