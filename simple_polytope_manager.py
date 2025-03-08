import os
import sys
import subprocess
import datetime
import ast
import networkx as nx
import graphcalc as gc
import pandas as pd
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import track
import questionary
import shutil
import tempfile
from prompt_toolkit.styles import Style
import pyfiglet

custom_style = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'bold'),
    ('answer', 'fg:cyan bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:cyan'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', 'fg:#a3a3a3 italic'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])


git_custom_style = Style([
    ('qmark', 'fg:magenta bold'),
    ('question', 'bold fg:magenta'),
    ('answer', 'fg:magenta bold'),
    ('pointer', 'fg:magenta bold'),
    ('highlighted', 'fg:magenta bold'),
    ('selected', 'fg:magenta'),
    ('separator', 'fg:#6C6C6C'),
    ('instruction', 'fg:#a3a3a3 italic'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

console = Console()

def get_property_names():
    """
    Reads property names (one per line) from polytope_properties.txt.
    """
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    with open(properties_file, "r") as f:
        properties = [line.strip() for line in f if line.strip()]
    return properties

def compute_properties(graph):
    """
    Computes the specified properties for a given NetworkX graph.
    """
    property_names = get_property_names()
    props = {}
    props['edgelist'] = [e for e in graph.edges()]
    props['adjacency_matrix'] = gc.adjacency_matrix(graph).tolist()
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

def compute_properties_from_edge_file(name, property_names):
    """
    Reads a graph from an edgelist file and computes properties.
    (This function is used when initially creating the CSV database.)
    """
    file_path = os.path.join("Simple_Polytope_Data", "Edge_Data", name)
    try:
        G = nx.read_edgelist(file_path, nodetype=int)
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return {}
    if G.number_of_nodes() == 0:
        return {}
    props = compute_properties(G, property_names)
    props['name'] = name[:-4]  # Remove the .txt extension.
    return props

def recompute_csv_database():
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

def compute_new_property_from_csv_row(row, new_func):
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

def update_csv_with_new_function(new_func):
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

def add_new_function():
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

def parse_edge_list(input_str):
    # Try to use ast.literal_eval after ensuring the input is wrapped as a list
    try:
        # If the input doesn't start with '[' assume it's a comma-separated series and add brackets
        trimmed = input_str.strip()
        if not trimmed.startswith('['):
            trimmed = '[' + trimmed + ']'
        # Safely evaluate the string as a Python literal
        edge_list = ast.literal_eval(trimmed)
        # Validate that we have a list of pairs (either tuples or lists)
        if (isinstance(edge_list, list) and
            all(isinstance(edge, (list, tuple)) and len(edge) == 2 for edge in edge_list)):
            # Normalize: convert any lists to tuples
            return [tuple(edge) for edge in edge_list]
    except Exception:
        # Fall through to regex approach if literal_eval fails
        pass

    # Fallback: use regex to extract pairs of numbers (handles negatives and extra spaces)
    pattern = r'\(?\s*(-?\d+)\s*,\s*(-?\d+)\s*\)?'
    matches = re.findall(pattern, input_str)
    if matches:
        return [ (int(a), int(b)) for a, b in matches ]

    # If no valid edge is found, raise an error
    raise ValueError("Could not parse edge list from the provided input.")

def add_new_edge_list():
    """
    Prompts the user to input a new edge list interactively and then updates the CSV database.
    The file name is automatically generated in the form simple_polytope_N.txt (N being next in sequence).
    After computing the properties, the script displays them and asks for confirmation before updating.
    If the user does not accept the computed properties, the new edge list file is removed.
    The user can type 'restart' at any prompt to cancel and return to the main menu.
    """
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    existing_files = [f for f in os.listdir(edge_dir) if f.startswith("simple_polytope_") and f.endswith(".txt")]
    numbers = []
    for f in existing_files:
        try:
            num = int(f[len("simple_polytope_"):-len(".txt")])
            numbers.append(num)
        except ValueError:
            pass
    next_number = max(numbers) + 1 if numbers else 0
    new_file_name = f"simple_polytope_{next_number}.txt"
    new_file_path = os.path.join(edge_dir, new_file_name)

    console.print(Panel(f"[bold green]New edge list will be saved as: {new_file_name}[/bold green]", style="blue"))
    console.print("[bold cyan]Enter edges one per line in the format 'source target' or 'source, target'.[/bold cyan]")
    console.print("[bold cyan]Type 'done' when finished, or 'restart' at any time to cancel and return to the main menu.[/bold cyan]")

    edges = []
    while True:
        line = Prompt.ask("[bold magenta]Edge[/bold magenta]").strip()
        if line.lower() == "done":
            break
        if line.lower() == "restart":
            console.print("[red]Restarting edge entry process. Returning to main menu.[/red]")
            return
        if ',' in line:
            parts = line.split(',')
        else:
            parts = line.split()
        if len(parts) != 2:
            console.print("[red]Invalid format. Please enter two numbers separated by a space or comma.[/red]")
            continue
        try:
            u = int(parts[0].strip())
            v = int(parts[1].strip())
        except ValueError:
            console.print("[red]Invalid numbers. Please enter valid integers.[/red]")
            continue
        edges.append((u, v))

    if not edges:
        console.print("[red]No edges were entered. Aborting.[/red]")
        return

    # -----------------------------
    # VALIDATE SIMPLE POLYTOPE GRAPH
    # -----------------------------
    # Build a NetworkX graph from the entered edges.
    try:
        G = nx.Graph()
        G.add_edges_from(edges)
        # Use graphcalc to check that the graph is a simple polytope graph.
        spg = gc.simple_polytope_graph(G)
    except Exception as e:
        console.print(f"[red]Error computing simple polytope graph: {e}[/red]")
        return
    # If the returned result is not truthy, the edge list is not valid.
    if not spg:
        console.print("[red]The entered edge list does not form a valid simple polytope graph. Please check your input and try again.[/red]")
        return

    # Compute properties for the new edge list.
    new_props = compute_properties(G)
    new_props['name'] = new_file_name[:-4]  # Remove the .txt extension.

    # Display computed properties for user verification. If user agrees the information is correct, proceed
    # and save the new edge list to a file and update the CSV database.
    console.print(Panel("[bold blue]Computed properties for the new edge list:[/bold blue]", style="magenta"))
    for key, value in new_props.items():
        console.print(f"[bold]{key}:[/bold] {value}")

    confirm = Prompt.ask("\n[bold yellow]Do these properties look correct? (y/n)[/bold yellow]", choices=["y", "n"], default="y")
    if confirm != 'y':
        console.print("[red]Aborting update. No edge list was saved and no changes were made to the CSV database.[/red]")
        return

    # Save the edge list to a file
    try:
        with open(new_file_path, "w") as f:
            for u, v in edges:
                f.write(f"{u} {v}\n")
        console.print(f"[green]New edge list saved to {new_file_path}.[/green]")
    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")
        return

    # Update the CSV database.
    csv_path = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            console.print(f"[red]Error reading CSV file: {e}[/red]")
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    polytope_name = new_file_name[:-4]  # Remove .txt extension.
    if 'name' in df.columns and polytope_name in df['name'].values:
        console.print(f"[yellow]Polytope '{polytope_name}' already exists in the CSV database. Overwriting the record.[/yellow]")
        df = df[df['name'] != polytope_name]

    # df = df.append(new_props, ignore_index=True)
    df = pd.concat([df, pd.DataFrame([new_props])], ignore_index=True)
    try:
        df.to_csv(csv_path, index=False)
        console.print(f"[bold green]CSV database updated. It now contains {len(df)} records.[/bold green]")
    except Exception as e:
        console.print(f"[red]Error writing CSV file: {e}[/red]")

def add_new_edge_list_from_paste():
    """
    Prompts the user to paste an entire edge list (copy-paste) and then updates the CSV database.
    The pasted edge list can be in various formats, for example:
      - [[0,1],[0,2],[2,3]]
      - [(0, 1), (0, 2), (2, 3)]
      - (0, 1), (0, 2), (2, 3)
    The file name is automatically generated in the form simple_polytope_N.txt (N being next in sequence).
    After computing the properties, the script displays them and asks for confirmation before updating.
    If the user does not accept the computed properties, no changes are made.
    The user can type 'restart' at any prompt to cancel and return to the main menu.
    """
    # Assume gc and compute_properties are imported from your project.

    # Determine the file name based on existing files.
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    existing_files = [f for f in os.listdir(edge_dir) if f.startswith("simple_polytope_") and f.endswith(".txt")]
    numbers = []
    for f in existing_files:
        try:
            num = int(f[len("simple_polytope_"):-len(".txt")])
            numbers.append(num)
        except ValueError:
            pass
    next_number = max(numbers) + 1 if numbers else 0
    new_file_name = f"simple_polytope_{next_number}.txt"
    new_file_path = os.path.join(edge_dir, new_file_name)

    console.print(Panel(f"[bold green]New edge list will be saved as: {new_file_name}[/bold green]", style="blue"))
    console.print("[bold cyan]Paste your entire edge list in any of the following formats:[/bold cyan]")
    console.print("  - [[0,1],[0,2],[2,3]]")
    console.print("  - [(0, 1), (0, 2), (2, 3)]")
    console.print("  - (0, 1), (0, 2), (2, 3)")
    console.print("[bold cyan]Type 'restart' to cancel and return to the main menu.[/bold cyan]")

    user_input = Prompt.ask("[bold magenta]Edge List[/bold magenta]").strip()
    if user_input.lower() == "restart":
        console.print("[red]Restarting edge entry process. Returning to main menu.[/red]")
        return

    # Use the parse_edge_list function to handle different input formats.
    try:
        edges = parse_edge_list(user_input)
    except ValueError as e:
        console.print(f"[red]Error parsing edge list: {e}[/red]")
        return

    if not edges:
        console.print("[red]No edges were parsed. Aborting.[/red]")
        return

    # -----------------------------
    # VALIDATE SIMPLE POLYTOPE GRAPH
    # -----------------------------
    try:
        G = nx.Graph()
        G.add_edges_from(edges)
        # Validate that the graph is a simple polytope graph using your custom checker.
        spg = gc.simple_polytope_graph(G)
    except Exception as e:
        console.print(f"[red]Error computing simple polytope graph: {e}[/red]")
        return
    if not spg:
        console.print("[red]The entered edge list does not form a valid simple polytope graph. Please check your input and try again.[/red]")
        return

    # Compute properties for the new edge list.
    new_props = compute_properties(G)
    new_props['name'] = new_file_name[:-4]  # Remove the .txt extension.

    # Display computed properties for user verification.
    console.print(Panel("[bold blue]Computed properties for the new edge list:[/bold blue]", style="magenta"))
    for key, value in new_props.items():
        console.print(f"[bold]{key}:[/bold] {value}")

    confirm = Prompt.ask("\n[bold yellow]Do these properties look correct? (y/n)[/bold yellow]", choices=["y", "n"], default="y")
    if confirm != 'y':
        console.print("[red]Aborting update. No edge list was saved and no changes were made to the CSV database.[/red]")
        return

    # Save the edge list to a file.
    try:
        with open(new_file_path, "w") as f:
            for u, v in edges:
                f.write(f"{u} {v}\n")
        console.print(f"[green]New edge list saved to {new_file_path}.[/green]")
    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")
        return

    # -----------------------------
    # UPDATE THE CSV DATABASE
    # -----------------------------
    csv_path = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            console.print(f"[red]Error reading CSV file: {e}[/red]")
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    polytope_name = new_file_name[:-4]  # Remove .txt extension.
    if 'name' in df.columns and polytope_name in df['name'].values:
        console.print(f"[yellow]Polytope '{polytope_name}' already exists in the CSV database. Overwriting the record.[/yellow]")
        df = df[df['name'] != polytope_name]

    df = pd.concat([df, pd.DataFrame([new_props])], ignore_index=True)
    try:
        df.to_csv(csv_path, index=False)
        console.print(f"[bold green]CSV database updated. It now contains {len(df)} records.[/bold green]")
    except Exception as e:
        console.print(f"[red]Error writing CSV file: {e}[/red]")



def display_properties_of_entry():
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


def remove_property():
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



def run_pytests():

    """
    Runs pytests on the test directory, displaying a progress bar that updates in real-time
    as each test finishes. It captures and aggregates output (filtering out lines that are
    just progress dots), then displays it in a panel.
    """
    from rich.progress import Progress
    from rich.panel import Panel
    import os
    import re
    import subprocess
    import time

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




# console = Console()

# Global variable to store backup location.
backup_folder = None

def create_backup():
    """
    Creates backups of files/directories that might be modified during the session.
    """
    global backup_folder
    backup_folder = tempfile.mkdtemp(prefix="polytope_backup_")
    console.print(f"[blue]Creating backup in {backup_folder}[/blue]")

    # Backup the Edge_Data directory.
    edge_data_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    if os.path.isdir(edge_data_dir):
        backup_edge_dir = os.path.join(backup_folder, "Edge_Data")
        shutil.copytree(edge_data_dir, backup_edge_dir)

    # Backup the CSV database file.
    csv_file = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if os.path.isfile(csv_file):
        shutil.copy(csv_file, backup_folder)

    # Backup the properties file.
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    if os.path.isfile(properties_file):
        shutil.copy(properties_file, backup_folder)

def reset_session():
    """
    Restores the backed-up files/directories, deleting any changes or new files created.
    """
    global backup_folder
    if backup_folder is None:
        console.print("[red]No backup available. Cannot reset session.[/red]")
        return

    console.print("[yellow]Resetting session...[/yellow]")

    # Restore the Edge_Data directory.
    edge_data_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    backup_edge_dir = os.path.join(backup_folder, "Edge_Data")
    if os.path.isdir(edge_data_dir):
        shutil.rmtree(edge_data_dir)
    if os.path.isdir(backup_edge_dir):
        shutil.copytree(backup_edge_dir, edge_data_dir)

    # Restore the CSV database file.
    csv_file = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    backup_csv_file = os.path.join(backup_folder, "simple_polytope_properties.csv")
    if os.path.isfile(csv_file):
        os.remove(csv_file)
    if os.path.isfile(backup_csv_file):
        shutil.copy(backup_csv_file, csv_file)

    # Restore the properties file.
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    backup_properties_file = os.path.join(backup_folder, "polytope_properties.txt")
    if os.path.isfile(properties_file):
        os.remove(properties_file)
    if os.path.isfile(backup_properties_file):
        shutil.copy(backup_properties_file, properties_file)

    console.print("[green]Session has been reset to its original state.[/green]")

def switch_branch():
    """
    Lists all branches and prompts the user to select one.
    After selection, the function checks out the chosen branch.
    """
    # Get list of branches. The current branch is prefixed with '*'
    result = subprocess.run(["git", "branch"], capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Error listing branches: {result.stderr}[/red]")
        return

    # Process the output to extract branch names and indicate the current branch.
    branches = []
    for line in result.stdout.splitlines():
        # Remove any asterisks and whitespace.
        branch = line.strip().lstrip("* ").strip()
        branches.append(branch)

    # Use Questionary to let the user scroll through and select a branch.
    selected_branch = questionary.select(
        "Select a branch to switch to:",
        choices=branches,
        style=git_custom_style,
    ).ask()

    if not selected_branch:
        console.print("[yellow]No branch selected. Returning to Git menu.[/yellow]")
        return

    # Checkout the selected branch.
    checkout = subprocess.run(["git", "checkout", selected_branch], capture_output=True, text=True)
    if checkout.returncode == 0:
        console.print(Panel(f"[bold magenta]Switched to branch:[/bold magenta] {selected_branch}", style="blue"))
    else:
        console.print(f"[red]Error switching branch: {checkout.stderr}[/red]")

# Example integration in the Git interface:
def git_github_interface():
    """
    A minimal Git/GitHub interface with interactive branch selection.
    Options include:
      1. Create branch
      2. Switch branch
      3. Add and commit changes
      4. Push to GitHub
      5. Show Git status
      6. Show current branch
      7. Return to main menu
    """
    committed = False
    branch_created = False

    while True:
        title_text = pyfiglet.figlet_format("Git Manager", font="slant")
        console.print(title_text, style="bold cyan")
        choice = questionary.select(
            "Select a Git/GitHub action:",
            choices=[
                "1: Create branch",
                "2: Switch branch",
                "3: Add and commit changes",
                "4: Push to GitHub",
                "5: Show Git status",
                "6: Show current branch",
                "7: Return to main menu",
            ],
            style=git_custom_style,
        ).ask()

        if choice.startswith("1"):
            # Create branch: allow user to cancel by typing "cancel"
            branch_name = questionary.text(
                "Enter branch name (e.g., feature/new-feature) (or type 'cancel' to abort):"
            ).ask()
            if branch_name.lower() == "cancel":
                console.print("[yellow]Branch creation canceled.[/yellow]")
                continue
            if not branch_name or " " in branch_name:
                console.print("[red]Invalid branch name. Please try again.[/red]")
                continue

            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                console.print(f"[green]Branch '{branch_name}' created successfully.[/green]")
                branch_created = True
            else:
                console.print(f"[red]Error creating branch: {result.stderr}[/red]")

        elif choice.startswith("2"):
            switch_branch()

        elif choice.startswith("3"):
            # Add and commit changes: allow user to cancel by typing "cancel"
            commit_message = questionary.text(
                "Enter commit message (or type 'cancel' to abort):"
            ).ask()
            if commit_message.lower() == "cancel":
                console.print("[yellow]Add and commit canceled.[/yellow]")
                continue
            if not commit_message:
                console.print("[red]Commit message cannot be empty.[/red]")
                continue

            result_add = subprocess.run(
                ["git", "add", "."],
                capture_output=True, text=True
            )
            if result_add.returncode != 0:
                console.print(f"[red]Error adding files: {result_add.stderr}[/red]")
                continue

            result_commit = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True, text=True
            )
            if result_commit.returncode == 0:
                console.print("[green]Changes committed successfully.[/green]")
                committed = True
            else:
                console.print(f"[red]Error committing changes: {result_commit.stderr}[/red]")
        elif choice.startswith("4"):
            if not committed:
                console.print("[red]No committed changes to push. Please add and commit changes first.[/red]")
                continue

            push_confirm = questionary.confirm(
                "Are you sure you want to push the changes to GitHub?"
            ).ask()
            if not push_confirm:
                continue

            # Get the current branch name.
            result_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True
            )
            if result_branch.returncode != 0:
                console.print(f"[red]Error determining current branch: {result_branch.stderr}[/red]")
                continue

            current_branch = result_branch.stdout.strip()

            # Check if the branch has an upstream.
            result_upstream = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                capture_output=True, text=True
            )

            if result_upstream.returncode != 0:
                # No upstream branch set; push with --set-upstream.
                result_push = subprocess.run(
                    ["git", "push", "--set-upstream", "origin", current_branch],
                    capture_output=True, text=True
                )
            else:
                # Upstream branch exists; do a normal push.
                result_push = subprocess.run(
                    ["git", "push"],
                    capture_output=True, text=True
                )

            if result_push.returncode == 0:
                console.print("[green]Pushed to GitHub successfully.[/green]")
            else:
                console.print(f"[red]Error pushing to GitHub: {result_push.stderr}[/red]")

        elif choice.startswith("5"):
            result_status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True
            )
            if result_status.returncode != 0:
                console.print(f"[red]Error getting git status: {result_status.stderr}[/red]")
                continue

            lines = result_status.stdout.splitlines()
            staged_files = []
            unstaged_files = []
            for line in lines:
                if len(line) < 3:
                    continue
                staged_indicator = line[0]
                unstaged_indicator = line[1]
                filename = line[3:].strip()
                if staged_indicator != " ":
                    staged_files.append(filename)
                if unstaged_indicator != " ":
                    unstaged_files.append(filename)

            console.print("[bold green]Staged Files:[/bold green]")
            if staged_files:
                for f in staged_files:
                    console.print(f"[green]{f}[/green]")
            else:
                console.print("[green]No staged changes.[/green]")

            console.print("\n[bold red]Unstaged Files:[/bold red]")
            if unstaged_files:
                for f in unstaged_files:
                    console.print(f"[red]{f}[/red]")
            else:
                console.print("[red]No unstaged changes.[/red]")

        elif choice.startswith("6"):
            result_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True
            )
            if result_branch.returncode == 0:
                current_branch = result_branch.stdout.strip()
                console.print(Panel(f"[bold magenta]{current_branch}[/bold magenta]", title="Current Branch", style="blue"))
            else:
                console.print(f"[red]Error getting current branch: {result_branch.stderr}[/red]")

        elif choice.startswith("7"):
            console.print("[cyan]Returning to main menu.[/cyan]")
            break

console = Console()

# Example of integrating into your main function:
def main():
    """
    Main menu for the Polytope Database Manager.
    Now includes a Git/GitHub option.
    """

    while True:
        title_text = pyfiglet.figlet_format("Polytope Database Manager", font="slant")
        console.print(title_text, style="bold cyan")
        choice = questionary.select(
            "Please select an option:",
            choices=[
                "1: Recompute database",
                "2: Add a new edge list",
                "3: Display properties",
                "4: Run tests",
                "5: Add property (callable from GraphCalc or NetworkX)",
                "6: Remove property",
                "7: Git/GitHub interface",
                "8: Exit",
            ],
            style=custom_style,
        ).ask()

        if choice.startswith("1"):
            # recompute_csv_database() – your existing function
            console.print("[cyan]Recomputing database...[/cyan]")
        elif choice.startswith("2"):
            # Your edge list functions (manual or paste)
            console.print("[cyan]Adding a new edge list...[/cyan]")
        elif choice.startswith("3"):
            # display_properties_of_entry() – your existing function
            console.print("[cyan]Displaying properties...[/cyan]")
        elif choice.startswith("4"):
            # run_pytests() – your existing function
            console.print("[cyan]Running tests...[/cyan]")
        elif choice.startswith("5"):
            # add_new_function() – your existing function
            console.print("[cyan]Adding property function...[/cyan]")
        elif choice.startswith("6"):
            # remove_property() – your existing function
            console.print("[cyan]Removing property...[/cyan]")
        elif choice.startswith("7"):
            # Call the Git/GitHub interface
            git_github_interface()
        elif choice.startswith("8"):
            console.print("[bold red]Exiting. Goodbye![/bold red]")
            break
        else:
            console.print("[red]Invalid option. Please choose a valid option.[/red]")

if __name__ == "__main__":
    main()
