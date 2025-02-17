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

console = Console()

def get_property_names():
    """
    Reads property names (one per line) from polytope_properties.txt.
    """
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    with open(properties_file, "r") as f:
        properties = [line.strip() for line in f if line.strip()]
    return properties

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
    props = {
        'name': name[:-4],
        'edgelist': [e for e in G.edges()],
        'adjacency_matrix': gc.adjacency_matrix(G).tolist(),
    }
    for prop in property_names:
        try:
            result = getattr(gc, prop)(G)
        except Exception:
            try:
                result = getattr(nx, prop)(G)
            except Exception:
                result = None
        props[prop] = result
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

    # -----------------------------
    # SAVE THE EDGE LIST TO A FILE
    # -----------------------------
    try:
        with open(new_file_path, "w") as f:
            for u, v in edges:
                f.write(f"{u} {v}\n")
        console.print(f"[green]New edge list saved to {new_file_path}.[/green]")
    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")
        return

    # Compute properties for the new edge list.
    property_names = get_property_names()
    new_props = compute_properties_from_edge_file(new_file_name, property_names)

    # Display computed properties for user verification.
    console.print(Panel("[bold blue]Computed properties for the new edge list:[/bold blue]", style="magenta"))
    for key, value in new_props.items():
        console.print(f"[bold]{key}:[/bold] {value}")
    confirm = Prompt.ask("\n[bold yellow]Do these properties look correct? (y/n)[/bold yellow]", choices=["y", "n"], default="y")
    if confirm != 'y':
        console.print("[red]Aborting update. Removing new edge list file.[/red]")
        try:
            os.remove(new_file_path)
        except Exception as e:
            console.print(f"[red]Error removing file: {e}[/red]")
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

    df = df.append(new_props, ignore_index=True)
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
    Runs pytests on each test file in the 'Simple_Polytope_Data/tests' directory,
    displaying a progress bar that updates as each test script is run.
    Aggregates the output and displays it in a panel.
    """
    console.print("[bold cyan]Running pytests on the test directory...[/bold cyan]")
    test_dir = os.path.join("Simple_Polytope_Data", "tests")
    test_files = [os.path.join(test_dir, f) for f in os.listdir(test_dir)
                  if f.startswith("test_") and f.endswith(".py")]
    if not test_files:
        console.print("[red]No test files found.[/red]")
        return

    from rich.progress import Progress
    all_output = ""
    all_success = True
    with Progress() as progress:
        task = progress.add_task("Running tests...", total=len(test_files))
        for test_file in test_files:
            result = subprocess.run(["pytest", test_file], capture_output=True, text=True)
            header = f"\n{'='*10} Output for {os.path.basename(test_file)} {'='*10}\n"
            all_output += header + result.stdout + "\n"
            if result.returncode != 0:
                all_success = False
            progress.update(task, advance=1)
    panel_style = "green" if all_success else "red"
    console.print(Panel(all_output, title="Pytest Output", style=panel_style))

def main():
    """
    Presents a menu with the following options:
      1: Recompute the entire CSV database
      2: Add a new edge list
      3: Display properties
      4: Run tests
      5: Add property (must be callable from GraphCalc or NetworkX)
      6: Remove property
      7: Exit
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
                "5: Add property (must be callable from GraphCalc or NetworkX)",
                "6: Remove property",
                "7: Exit",
            ],
            style=custom_style,
        ).ask()

        if choice.startswith("1"):
            recompute_csv_database()
            print()
        elif choice.startswith("2"):
            add_new_edge_list()
            print()
        elif choice.startswith("3"):
            display_properties_of_entry()
            print()
        elif choice.startswith("4"):
            run_pytests()
            print()
        elif choice.startswith("5"):
            add_new_function()
            print()
        elif choice.startswith("6"):
            remove_property()
            print()
        elif choice.startswith("7"):
            console.print("[bold red]Exiting. Goodbye![/bold red]")
            sys.exit(0)
        else:
            console.print("[red]Invalid option. Please choose a valid option.[/red]")

if __name__ == "__main__":
    main()
