import os
import sys
import subprocess
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
    Reads a graph from an edgelist file using networkx.read_edgelist,
    then computes each property using the corresponding function from graphcalc
    (with networkx as a fallback if needed).

    Returns a dictionary of property values.
    """
    file_path = os.path.join("Simple_Polytope_Data", "Edge_Data", name)
    try:
        # Read the graph; assume node labels are integers.
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
    A progress bar is shown during processing.
    """
    confirm = Prompt.ask(
        "[bold yellow]WARNING: This will recompute the entire CSV database and overwrite any existing file. Are you sure you want to proceed? (y/n)[/bold yellow]",
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
    A live table is shown with the edges added so far.
    If the computed properties are not accepted, the new edge list file is removed.
    """
    from rich.live import Live
    from rich.table import Table

    def build_edges_table(edges):
        table = Table(title="Edges Added So Far")
        table.add_column("Index", justify="right", style="cyan", no_wrap=True)
        table.add_column("Edge", style="magenta")
        for i, (u, v) in enumerate(edges, start=1):
            table.add_row(str(i), f"{u} {v}")
        return table

    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    existing_files = [
        f for f in os.listdir(edge_dir)
        if f.startswith("simple_polytope_") and f.endswith(".txt")
    ]
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

    console.print(
        Panel(
            f"[bold green]New edge list will be saved as: {new_file_name}[/bold green]",
            style="blue"
        )
    )
    console.print(
        "[bold cyan]Enter edges one per line in the format 'source target' or 'source, target'.[/bold cyan]"
    )
    console.print(
        "[bold cyan]Type 'done' when finished, or 'restart' to cancel and return to the main menu.[/bold cyan]"
    )

    edges = []
    # Use Live to display the table of edges as it updates.
    with Live(build_edges_table(edges), refresh_per_second=4, console=console) as live:
        while True:
            line = Prompt.ask("[bold magenta]Edge[/bold magenta]").strip()
            if line.lower() == "done":
                break
            if line.lower() == "restart":
                console.print("[red]Restarting edge entry process. Returning to main menu.[/red]")
                return
            parts = line.split(",") if "," in line else line.split()
            if len(parts) != 2:
                console.print(
                    "[red]Invalid format. Please enter two numbers separated by a space or comma.[/red]"
                )
                continue
            try:
                u = int(parts[0].strip())
                v = int(parts[1].strip())
            except ValueError:
                console.print("[red]Invalid numbers. Please enter valid integers.[/red]")
                continue
            edges.append((u, v))
            live.update(build_edges_table(edges))

    if not edges:
        console.print("[red]No edges were entered. Aborting.[/red]")
        return

    # Save the new edge list to a file.
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

    console.print(
        Panel("[bold blue]Computed properties for the new edge list:[/bold blue]", style="magenta")
    )
    for key, value in new_props.items():
        console.print(f"[bold]{key}:[/bold] {value}")
    confirm = Prompt.ask(
        "\n[bold yellow]Do these properties look correct? (y/n)[/bold yellow]",
        choices=["y", "n"],
        default="y"
    )
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
        console.print(
            f"[yellow]Polytope '{polytope_name}' already exists in the CSV database. Overwriting the record.[/yellow]"
        )
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


def run_pytests():
    """
    Runs pytests on the 'tests' directory and displays the output.
    If tests fail (nonzero return code), the panel will be red; otherwise, green.
    """
    console.print("[bold cyan]Running pytests on the test directory...[/bold cyan]")
    try:
        result = subprocess.run(["pytest", "Simple_Polytope_Data/tests/"], capture_output=True, text=True)
        # If return code is non-zero, some tests failed.
        panel_style = "green" if result.returncode == 0 else "red"
        console.print(Panel(result.stdout, title="Pytest Output", style=panel_style))
        if result.returncode != 0:
            console.print("[red]Some tests failed.[/red]")
    except Exception as e:
        console.print(f"[red]Error running pytest: {e}[/red]")




# Define a custom style for the selection prompt
custom_style = Style([
    ('qmark', 'fg:cyan bold'),      # Use bold cyan for the question mark
    ('question', 'bold'),
    ('answer', 'fg:cyan bold'),      # Use bold cyan for answers as well
    ('pointer', 'fg:cyan bold'),     # Use bold cyan for the pointer
    ('highlighted', 'fg:cyan bold'), # Use bold cyan when highlighted
    ('selected', 'fg:cyan'),         # Use cyan for selected items
    ('separator', 'fg:#6C6C6C'),
    ('instruction', 'fg:#a3a3a3 italic'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])



def main():
    """
    Presents a menu using Questionary with a custom style for arrow-key navigation,
    while still keeping the aesthetic output from Rich in the rest of the interface.
    """
    while True:
        console = Console()
        title_text = pyfiglet.figlet_format("Polytope Database Manager", font="slant")
        console.print(title_text, style="bold cyan")
        choice = questionary.select(
            "Please select an option:",
            choices=[
                "A: Recompute the entire CSV database",
                "B: Add a new edge list to the database",
                "C: Display properties for a chosen edge list",
                "D: Run simple polytope tests",
                "E: Exit",
            ],
            style=custom_style,
        ).ask()

        if choice.startswith("A"):
            recompute_csv_database()
            print()
        elif choice.startswith("B"):
            add_new_edge_list()
            print()
        elif choice.startswith("C"):
            display_properties_of_entry()
            print()
        elif choice.startswith("D"):
            run_pytests()
            print()
        elif choice.startswith("E"):
            console.print("[bold red]Exiting. Goodbye![/bold red]")
            sys.exit(0)
        else:
            console.print("[red]Invalid option. Please choose a valid option.[/red]")


if __name__ == "__main__":
    main()
