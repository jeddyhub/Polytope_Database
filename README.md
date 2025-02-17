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
git clone https://github.com/jeddyhub/Polytope_Database.git
```

2. **Create a virtual environment (optional but recommended):**
```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**
A `requirements.txt` file has been generated using `pip freeze`. To install the required packages, run:
```bash
pip install -r requirements.txt
```

4. Run the main database script.
```bash
python simple_polytope_manager.py
```

## Home Display
```bash
    ____        __      __
   / __ \____  / /_  __/ /_____  ____  ___
  / /_/ / __ \/ / / / / __/ __ \/ __ \/ _ \
 / ____/ /_/ / / /_/ / /_/ /_/ / /_/ /  __/
/_/    \____/_/\__, /\__/\____/ .___/\___/
              /____/         /_/
    ____        __        __
   / __ \____ _/ /_____ _/ /_  ____ _________
  / / / / __ `/ __/ __ `/ __ \/ __ `/ ___/ _ \
 / /_/ / /_/ / /_/ /_/ / /_/ / /_/ (__  )  __/
/_____/\__,_/\__/\__,_/_.___/\__,_/____/\___/

    __  ___
   /  |/  /___ _____  ____ _____ ____  _____
  / /|_/ / __ `/ __ \/ __ `/ __ `/ _ \/ ___/
 / /  / / /_/ / / / / /_/ / /_/ /  __/ /
/_/  /_/\__,_/_/ /_/\__,_/\__, /\___/_/
                         /____/

? Please select an option: (Use arrow keys)
 » A: Recompute the entire CSV database
   B: Add a new edge list to the database
   C: Display properties for a chosen edge list
   D: Run simple polytope tests directory
   E: Exit

```

When the script runs, you'll be presented with a menu:
- **A: Recompute the entire CSV database**

Selecting this option will:
Prompt you for confirmation (warning that the existing CSV file will be overwritten).
Process all edge list files from Simple_Polytope_Data/Edge_Data with a progress bar.
Generate/update the CSV file (simple_polytope_properties.csv).

- **B: Add a new edge list to the database**

Selecting this option will:
Automatically generate the next available file name (e.g., simple_polytope_2.txt).
Prompt you to enter edges (one per line, either as "source target" or "source, target").
Type done to finish entering edges or restart at any time to cancel and return to the main menu. After saving, the script computes the properties for the new edge list and displays them. You'll then be asked to confirm whether the computed properties are correct before updating the CSV database.

- **C: Display properties for a chosen edge list**

Selecting this option will:
Display the edge list file names for each known polytope. The user will be prompted to enter in the numerical identifier for a polytope. Thereafter, the program computes all properties of the polytope that are currently being stored.

- **D: Run simple polytope tests directory**

Selecting this option will:
Run all tests in the `Simple_Polytope_Data` directory. Currently, this consists of checking if all edge lists being stored belong to simple polytope graphs.

- **E: Exit**

This option terminates the program.