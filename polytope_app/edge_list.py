from rich.panel import Panel
from rich.prompt import Prompt
import os
import networkx as nx
import pandas as pd
import graphcalc as gc
import ast
import re

from polytope_app.database import compute_properties


__all__ = ['parse_edge_list', 'add_new_edge_list', 'add_new_edge_list_from_paste']

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

def add_new_edge_list(console):
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

def add_new_edge_list_from_paste(console):
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
