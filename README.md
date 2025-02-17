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
