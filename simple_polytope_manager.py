import os
import sys
import subprocess
import datetime
import networkx as nx
import graphcalc as gc
import pandas as pd
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import track
from rich.table import Table
import questionary
from prompt_toolkit.styles import Style

console = Console()

# Custom style for questionary (using bold cyan)
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
    Reads a graph from an edgelist file using networkx.read_edgelist,
    then computes each property using the corresponding function from graphcalc
    (with networkx as a fallback if needed).

    Returns a dictionary of property values.
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
    for prop in get_property_names():
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
    A progress bar is shown during processing.
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

def add_new_edge_list():
    """
    Prompts the user to input a new edge list interactively and then updates the CSV database.
    If the computed properties are not accepted, the new edge list file is removed.
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
    console.print("[bold cyan]Type 'done' when finished, or 'restart' to cancel and return to the main menu.[/bold cyan]")

    edges = []
    while True:
        line = Prompt.ask("[bold magenta]Edge[/bold magenta]").strip()
        if line.lower() == "done":
            break
        if line.lower() == "restart":
            console.print("[red]Restarting edge entry process. Returning to main menu.[/red]")
            return
        parts = line.split(',') if ',' in line else line.split()
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

    try:
        with open(new_file_path, "w") as f:
            for u, v in edges:
                f.write(f"{u} {v}\n")
        console.print(f"[green]New edge list saved to {new_file_path}.[/green]")
    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")
        return

    property_names = get_property_names()
    new_props = compute_properties_from_edge_file(new_file_name, property_names)

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

    csv_path = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            console.print(f"[red]Error reading CSV file: {e}[/red]")
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    polytope_name = new_file_name[:-4]
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
    prompts the user to select one, computes its properties, and shows them.
    """
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    files = [f for f in os.listdir(edge_dir) if f.endswith(".txt")]
    if not files:
        console.print("[red]No edge list files found.[/red]")
        return

    file_dict = {}
    for f in files:
        if f.startswith("simple_polytope_") and f.endswith(".txt"):
            try:
                num = int(f[len("simple_polytope_"):-len(".txt")])
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

def run_pytests():
    """
    Runs pytests on the 'tests' directory and displays the output.
    If tests fail (nonzero return code), the panel is red; otherwise, green.
    """
    console.print("[bold cyan]Running pytests on the test directory...[/bold cyan]")
    try:
        result = subprocess.run(["pytest", "tests/"], capture_output=True, text=True)
        panel_style = "green" if result.returncode == 0 else "red"
        console.print(Panel(result.stdout, title="Pytest Output", style=panel_style))
        if result.returncode != 0:
            console.print("[red]Some tests failed.[/red]")
    except Exception as e:
        console.print(f"[red]Error running pytest: {e}[/red]")

def automate_pull_request():
    """
    Automates branch creation, committing changes, pushing the branch, and creating a pull request.
    Assumes the GitHub CLI is authenticated and configured.
    """
    branch_name = f"edge-list-update-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    commit_message = "Add new edge list"

    console.print(f"[bold cyan]Creating new branch:[/bold cyan] {branch_name}")
    result = subprocess.run(["git", "checkout", "-b", branch_name], capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Failed to create branch: {result.stderr}[/red]")
        return

    console.print("[bold cyan]Staging changes...[/bold cyan]")
    result = subprocess.run(["git", "add", "."], capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Failed to stage changes: {result.stderr}[/red]")
        return

    console.print(f"[bold cyan]Committing changes with message:[/bold cyan] {commit_message}")
    result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Failed to commit changes: {result.stderr}[/red]")
        return

    console.print(f"[bold cyan]Pushing branch {branch_name} to origin...[/bold cyan]")
    result = subprocess.run(["git", "push", "-u", "origin", branch_name], capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Failed to push branch: {result.stderr}[/red]")
        return

    console.print("[bold cyan]Creating pull request...[/bold cyan]")
    result = subprocess.run(
        ["gh", "pr", "create", "--title", commit_message, "--body", "Automated PR created by simple_polytope_manager."],
        capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]Failed to create pull request: {result.stderr}[/red]")
    else:
        console.print(f"[green]Pull request created successfully![/green]")

def database_summary():
    """
    Reads the CSV database and prints a summary of its columns.
    Displays column names, data types, non-null counts, and number of unique values.
    """
    csv_path = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if not os.path.exists(csv_path):
        console.print("[red]CSV database file not found.[/red]")
        return
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        console.print(f"[red]Error reading CSV file: {e}[/red]")
        return

    table = Table(title="Database Summary")
    table.add_column("Column Name", style="cyan", no_wrap=True)
    table.add_column("Data Type", style="magenta")
    table.add_column("Non-null Count", style="green")
    table.add_column("Unique Values", style="yellow")

    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = str(df[col].count())
        unique = str(df[col].nunique())
        table.add_row(col, dtype, non_null, unique)

    console.print(table)

def main():
    """
    Presents a visually appealing menu with options:
      A: Recompute CSV database
      B: Add new edge list
      C: Display properties for a chosen edge list
      D: Run pytests on the test directory
      E: Exit
      F: Automate pull request creation
      G: Database Summary
    """
    while True:
        # Display a title with ASCII art using pyfiglet
        try:
            import pyfiglet
            title_text = pyfiglet.figlet_format("Polytope Database Manager", font="slant")
            console.print(title_text, style="bold bright_blue")
        except ImportError:
            console.print("[bold bright_blue]Polytope Database Manager[/bold bright_blue]")

        choice = questionary.select(
            "Please select an option:",
            choices=[
                "A: Recompute the entire CSV database",
                "B: Add a new edge list to the database",
                "C: Display properties for a chosen edge list",
                "D: Run pytests on the test directory",
                "E: Exit",
                "F: Automate pull request creation",
                "G: Database Summary",
            ],
            style=custom_style,
        ).ask()

        if choice.startswith("A"):
            recompute_csv_database()
        elif choice.startswith("B"):
            add_new_edge_list()
        elif choice.startswith("C"):
            display_properties_of_entry()
        elif choice.startswith("D"):
            run_pytests()
        elif choice.startswith("E"):
            console.print("[bold red]Exiting. Goodbye![/bold red]")
            sys.exit(0)
        elif choice.startswith("F"):
            automate_pull_request()
        elif choice.startswith("G"):
            database_summary()
        else:
            console.print("[red]Invalid option. Please choose a valid option.[/red]")

if __name__ == "__main__":
    main()
