# polytope_app/database.py

import os
import ast
import re
import pandas as pd
import networkx as nx
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress
from rich.progress import track
import subprocess
import graphcalc as gc
# from polytope_app import utils

__all__ = [
    'get_property_names',
    'compute_properties',
    'compute_properties_from_edge_file',
    'recompute_csv_database',
    'compute_new_property_from_csv_row',
    'update_csv_with_new_function',
    'append_new_function_to_properties_file',
    'add_new_function',
    'display_properties_of_entry',
    'remove_property',
    'run_pytests',
]

def get_property_names():
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    with open(properties_file, "r") as f:
        properties = [line.strip() for line in f if line.strip()]
    return properties

def compute_properties(graph):
    property_names = get_property_names()
    props = {"edgelist": list(graph.edges()), "adjacency_matrix": gc.adjacency_matrix(graph).tolist()}
    for prop in property_names:
        try:
            result = getattr(gc, prop)(graph)
        except Exception:
            try:
                result = getattr(nx, prop)(graph)
            except Exception:
                result = None
        props[prop] = result
    return props

def compute_properties_from_edge_file(name, console):
    file_path = os.path.join("Simple_Polytope_Data", "Edge_Data", name)
    try:
        G = nx.read_edgelist(file_path, nodetype=int)
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return {}
    if G.number_of_nodes() == 0:
        return {}
    props = compute_properties(G)
    props['name'] = name[:-4]  # Remove the .txt extension.
    return props


def recompute_csv_database(console):
    """
    Recomputes the entire CSV database from all edge list files.
    """
    confirm = Prompt.ask(
        "[bold yellow]WARNING: This will recompute the entire CSV database and overwrite any existing file. Proceed? (y/n)[/bold yellow]",
        choices=["y", "n"],
        default="n",
    )
    if confirm != 'y':
        console.print("[red]Operation cancelled.[/red]")
        return
    property_names = get_property_names()
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    files = [f for f in os.listdir(edge_dir) if f.endswith(".txt")]
    all_data = []
    for filename in track(files, description="Processing edge files..."):
        props = compute_properties_from_edge_file(filename, property_names)
        all_data.append(props)
    df = pd.DataFrame(all_data)
    output_csv = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    df.to_csv(output_csv, index=False)
    console.print(f"\n[bold green]CSV file '{output_csv}' saved with {len(df)} records.[/bold green]")

# ------------------------------
# New Helper Functions for Efficiency
# ------------------------------

def compute_new_property_from_csv_row(row, new_func, console):
    """
    Given a row from the CSV file, extracts the 'edgelist' column,
    converts it to a list of edges, builds a graph, and computes the property
    specified by new_func.
    """
    edgelist_str = row.get('edgelist', None)
    if not edgelist_str:
        return None
    try:
        edges = ast.literal_eval(edgelist_str)
    except Exception as e:
        console.print(f"[red]Error evaluating edgelist for polytope '{row.get('name', 'unknown')}': {e}[/red]")
        return None
    if not edges:
        return None
    G = nx.Graph()
    G.add_edges_from(edges)
    try:
        result = getattr(gc, new_func)(G)
    except Exception:
        try:
            result = getattr(nx, new_func)(G)
        except Exception:
            result = None
    return result

def update_csv_with_new_function(new_func, console):
    """
    Loads the existing CSV database, computes the new function's value for each polytope
    using the edgelist stored in the CSV, adds these values as a new column, and saves the CSV.
    """
    csv_path = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if not os.path.exists(csv_path):
        console.print("[red]CSV database file not found. Please run a full recompute first.[/red]")
        return
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        console.print(f"[red]Error reading CSV file: {e}[/red]")
        return
    for index, row in df.iterrows():
        value = compute_new_property_from_csv_row(row, new_func)
        df.at[index, new_func] = value
    try:
        df.to_csv(csv_path, index=False)
        console.print(f"[green]CSV database updated with new function '{new_func}'.[/green]")
    except Exception as e:
        console.print(f"[red]Error writing CSV file: {e}[/red]")

def append_new_function_to_properties_file(properties_file, new_func):
    """
    Appends new_func to the properties_file, ensuring that it is placed on its own line.
    """
    # Open the file in binary mode for reading/writing.
    with open(properties_file, "rb+") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            # Go back one character.
            f.seek(-1, os.SEEK_END)
            last_char = f.read(1)
            if last_char != b'\n':
                f.write(b'\n')
        # Now write the new function name followed by a newline.
        f.write((new_func + "\n").encode())

def add_new_function(console):
    """
    Prompts the user to enter the name of a new function (e.g. 'fullerene') to compute on each polytope.
    The function name is appended to polytope_properties.txt (on its own line), and then the CSV database is updated
    by computing the new property for each polytope using the existing 'edgelist' column.
    """
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    new_func = Prompt.ask("[bold cyan]Enter the name of the new function to add (e.g. 'fullerene')[/bold cyan]").strip()
    if not new_func:
        console.print("[red]No function name entered. Aborting.[/red]")
        return
    properties = get_property_names()
    if new_func in properties:
        console.print(f"[yellow]The function '{new_func}' already exists in polytope_properties.txt[/yellow]")
        return
    try:
        append_new_function_to_properties_file(properties_file, new_func)
        console.print(f"[green]Function '{new_func}' added successfully to polytope_properties.txt[/green]")
    except Exception as e:
        console.print(f"[red]Error updating properties file: {e}[/red]")
        return

    # Instead of recomputing the entire database, update only the new function in the existing CSV.
    update_csv_with_new_function(new_func)

def display_properties_of_entry(console):
    """
    Displays available edge list files sorted by their numerical tag,
    prompts the user to select one by entering the numerical tag,
    computes the properties for that file, and then shows the computed properties.
    """
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    files = [f for f in os.listdir(edge_dir) if f.endswith(".txt")]
    if not files:
        console.print("[red]No edge list files found.[/red]")
        return

    # Build a dictionary mapping the numerical tag to the filename.
    file_dict = {}
    for f in files:
        if f.startswith("simple_polytope_") and f.endswith(".txt"):
            try:
                num_str = f[len("simple_polytope_"):-len(".txt")]
                num = int(num_str)
                file_dict[num] = f
            except ValueError:
                console.print(f"[yellow]Skipping file with invalid number: {f}[/yellow]")

    if not file_dict:
        console.print("[red]No valid edge list files found.[/red]")
        return

    sorted_numbers = sorted(file_dict.keys())
    console.print(Panel("Available edge list files (by numerical tag):", style="cyan"))
    for num in sorted_numbers:
        console.print(f"[bold blue]{num}[/bold blue]: {file_dict[num]}")

    num_str = Prompt.ask("Enter the numerical tag of the edge list to compute properties for")
    try:
        selected_num = int(num_str)
    except ValueError:
        console.print("[red]Invalid number.[/red]")
        return

    if selected_num not in file_dict:
        console.print("[red]No edge list with that numerical tag.[/red]")
        return

    selected_file = file_dict[selected_num]
    property_names = get_property_names()
    props = compute_properties_from_edge_file(selected_file, property_names)
    console.print(Panel(f"Computed properties for [bold green]{selected_file}[/bold green]:", style="magenta"))
    for key, value in props.items():
        if key not in ['name', 'edgelist', 'adjacency_matrix'] and value is not None:
            console.print(f"[bold]{key}:[/bold] {value}")

def remove_property(console):
    """
    Lists current properties from polytope_properties.txt, lets the user select one to remove,
    then confirms the removal. If the user cancels (by typing "restart" at the selection prompt
    or answering 'n' at the confirmation prompt), the function returns without making changes.
    If confirmed, the function removes that property from the file and, if present,
    drops the corresponding column from the CSV file.
    """
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    properties = get_property_names()
    if not properties:
        console.print("[red]No properties found in polytope_properties.txt[/red]")
        return

    console.print(Panel("Available properties:", style="cyan"))
    for i, prop in enumerate(properties, start=1):
        console.print(f"[bold blue]{i}[/bold blue]: {prop}")

    choice = Prompt.ask(
        "[bold cyan]Enter the number of the property to remove (or type 'restart' to cancel)[/bold cyan]"
    ).strip()

    if choice.lower() == "restart":
        console.print("[yellow]Operation cancelled. Returning to main menu.[/yellow]")
        return

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(properties):
            console.print("[red]Invalid selection.[/red]")
            return
        prop_to_remove = properties[index]
    except ValueError:
        console.print("[red]Please enter a valid number.[/red]")
        return

    # Confirm removal before proceeding.
    confirm = Prompt.ask(
        f"[bold yellow]Are you sure you want to remove property '{prop_to_remove}'? (y/n)[/bold yellow]",
        choices=["y", "n"],
        default="n"
    )
    if confirm.lower() != "y":
        console.print("[yellow]Removal cancelled. Returning to main menu.[/yellow]")
        return

    # Remove the property from the text file.
    try:
        with open(properties_file, "r") as f:
            lines = f.readlines()
        with open(properties_file, "w") as f:
            for line in lines:
                if line.strip() != prop_to_remove:
                    if not line.endswith("\n"):
                        line += "\n"
                    f.write(line)
        console.print(f"[green]Property '{prop_to_remove}' removed from {properties_file}.[/green]")
    except Exception as e:
        console.print(f"[red]Error updating properties file: {e}[/red]")
        return

    # Remove the column from the CSV database.
    csv_path = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if not os.path.exists(csv_path):
        console.print("[yellow]CSV database not found. No column to remove.[/yellow]")
        return
    try:
        df = pd.read_csv(csv_path)
        if prop_to_remove in df.columns:
            df.drop(columns=[prop_to_remove], inplace=True)
            df.to_csv(csv_path, index=False)
            console.print(f"[green]Column '{prop_to_remove}' removed from CSV database.[/green]")
        else:
            console.print(f"[yellow]Column '{prop_to_remove}' not found in CSV database.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error updating CSV file: {e}[/red]")


def run_pytests(console):

    """
    Runs pytests on the test directory, displaying a progress bar that updates in real-time
    as each test finishes. It captures and aggregates output (filtering out lines that are
    just progress dots), then displays it in a panel.
    """


    console.print("[bold cyan]Running pytests on the test directory...[/bold cyan]")
    test_dir = os.path.join("Simple_Polytope_Data", "tests")

    def count_tests(test_dir):
        """
        Runs pytest in collection-only mode to count the number of test items.
        """
        try:
            result = subprocess.run(
                ["pytest", "--collect-only", test_dir],
                capture_output=True, text=True
            )
            # Look for a line like "collected 440 items"
            m = re.search(r"collected (\d+) items", result.stdout)
            if m:
                return int(m.group(1))
        except Exception:
            pass
        return None

    total_tests = count_tests(test_dir)
    if total_tests is None:
        total_tests = 1  # Fallback if count fails

    process = subprocess.Popen(
        ["pytest", test_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # line-buffered
    )

    all_output = ""
    with Progress() as progress:
        task = progress.add_task("Running tests...", total=total_tests)
        while True:
            line = process.stdout.readline()
            if not line:
                break

            # Update progress if marker found and remove the marker.
            if "[PROGRESS]" in line:
                marker_count = line.count("[PROGRESS]")
                progress.advance(task, advance=marker_count)
                line = line.replace("[PROGRESS]", "")

            # Filter out lines that consist solely of dots (and whitespace).
            clean_line = line.strip("\n")
            if re.fullmatch(r"[.\s]+", clean_line):
                continue

            all_output += line
        process.wait()

    panel_style = "green" if process.returncode == 0 else "red"
    console.print(Panel(all_output, title="Pytest Output", style=panel_style))
