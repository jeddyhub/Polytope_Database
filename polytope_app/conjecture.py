from graffitiai import GraffitiAI
from pyfiglet import Figlet
from rich.panel import Panel
from rich.prompt import Prompt
from questionary import select
import questionary

from polytope_app.utils import custom_style

__all__ = [
    'write_on_the_wall',
    'probability_distribution',
    'conjecture_mode',
]

def convert_hypothesis(hypothesis):

    if hypothesis == "simple_polytope_graph":
        return "simple polytope graph"
    elif hypothesis == "connected_and_bipartite":
        return "simple polytope graph without odd cycles"
    elif hypothesis == "simple_polytope_graph_with_p6_greater_than_zero":
        return "simple polytope graph with p_6 > 0"
    elif hypothesis == "is_at_free":
        return "simple asteroidal triple free polytope graph"
    elif hypothesis == "simple_polytope_graph_with_p6_zero":
        return "simple polytope graph with p_6 = 0"
    elif hypothesis == "zeros_clustered(p_vector)":
        return "simple polytope graph with clustered zeros in p_vector"
    else:
        return hypothesis

def view_conjectures(agent, target_invariants=None, search=True, console=None):
    """
    Interactively view conjectures for the given target invariant(s).

    The user first selects a target invariant, then scrolls through the conjecture
    summaries (for equal, upper, and lower conjectures). Upon selection, detailed
    information is displayed in a Rich Panel with bold magenta and green formatting.

    Args:
        agent: The object containing conjectures and, optionally, the knowledge_table.
        target_invariants (list, optional): A list of target invariants to display. If None,
            all keys from agent.conjectures are used.
        search (bool): Whether to show additional details from the agent's knowledge table.
        console: A Rich Console instance for output.
    """


    # Helper to format sharp instances into columns.
    def format_sharp_instances(instances, num_columns=4, indent="    "):
        items = sorted(str(item) for item in instances)
        if not items:
            return ""
        max_width = max(len(item) for item in items)
        rows = (len(items) + num_columns - 1) // num_columns
        formatted_rows = []
        for row in range(rows):
            row_items = []
            for col in range(num_columns):
                idx = col * rows + row
                if idx < len(items):
                    row_items.append(items[idx].ljust(max_width))
            formatted_rows.append(indent + "   ".join(row_items))
        return "\n".join(formatted_rows)

    # Select a target invariant if more than one is provided.
    if target_invariants is None:
        target_invariants = list(agent.conjectures.keys())
    if len(target_invariants) > 1:
        target = select("Select a target invariant:", choices=target_invariants).ask()
    else:
        target = target_invariants[0]

    conj_data = agent.conjectures.get(target, {})
    equal_conj = conj_data.get("equals", [])
    upper_conj = conj_data.get("upper", [])
    lower_conj = conj_data.get("lower", [])

    # Build a list of conjecture entries with summary labels.
    entries = []
    def add_entries(conj_list, conj_type):
        for i, conj in enumerate(conj_list, start=1):
            hypothesis = convert_hypothesis(conj.hypothesis)
            conclusion = conj._set_conclusion()
            statement = f"For any {hypothesis}, {conclusion}."
            label = f"[bold]{conj_type} Conjecture {i}:[/bold] {statement}"
            entries.append({
                "label": label,
                "conj": conj,
                "type": conj_type,
                "index": i
            })
    if equal_conj:
        add_entries(equal_conj, "Equal")
    if upper_conj:
        add_entries(upper_conj, "Upper")
    if lower_conj:
        add_entries(lower_conj, "Lower")

    if not entries:
        console.print("[bold red]No conjectures generated for this target invariant.[/bold red]")
        return

    # Let the user select a conjecture to view in detail.
    choices = [entry["label"] for entry in entries]
    selected_label = select("Select a conjecture to view details:", choices=choices + ["Exit"]).ask()
    if selected_label == "Exit":
        return

    selected_entry = next((entry for entry in entries if entry["label"] == selected_label), None)
    if not selected_entry:
        console.print("[red]Invalid selection.[/red]")
        return

    conj = selected_entry["conj"]
    # Build detailed information.
    hypothesis = convert_hypothesis(conj.hypothesis)
    conclusion = conj._set_conclusion()
    details_lines = []
    details_lines.append(f"[bold magenta]Statement:[/bold magenta] For any [bold green]{hypothesis}[/bold green], [bold green]{conclusion}[/bold green].")
    details_lines.append(f"[bold magenta]Target Invariant:[/bold magenta] {conj.target}")
    details_lines.append(f"[bold magenta]Bound Type:[/bold magenta] {conj.bound_type}")
    if hasattr(conj, 'complexity') and conj.complexity is not None:
        details_lines.append(f"[bold magenta]Complexity:[/bold magenta] {conj.complexity}")
    if conj.touch > 0:
        if conj.touch > 1:
            details_lines.append(f"[bold magenta]Sharp on:[/bold magenta] {conj.touch} objects.")
        else:
            details_lines.append(f"[bold magenta]Sharp on:[/bold magenta] 1 object.")
    else:
        details_lines.append(f"[bold magenta]Inequality is strict.[/bold magenta]")
    if hasattr(conj, 'sharp_instances') and conj.sharp_instances:
        details_lines.append(f"[bold magenta]Sharp Instances:[/bold magenta]")
        details_lines.append(format_sharp_instances(conj.sharp_instances))
    # Optionally, include percentage info from the knowledge table.
    if hasattr(agent, 'knowledge_table') and conj.hypothesis in agent.knowledge_table.columns:
        hyp_df = agent.knowledge_table[agent.knowledge_table[conj.hypothesis] == True]
        total_hyp = len(hyp_df)
        if total_hyp > 0:
            percent_sharp = 100 * conj.touch / total_hyp
            details_lines.append(f"[bold magenta]Percentage of hypothesis objects that are sharp:[/bold magenta] {percent_sharp:.1f}%")
        else:
            details_lines.append(f"[bold magenta]No objects satisfy the hypothesis.[/bold magenta]")
    details = "\n".join(details_lines)

    # Display details in a Panel.
    panel = Panel(details,
                  title=f"[bold magenta]{selected_entry['type']} Conjecture {selected_entry['index']} Details[/bold magenta]",
                  style="magenta")
    console.print(panel)

    # Wait for user input before returning to the list.
    Prompt.ask("Press Enter to return to the conjecture list")
    # Recursively show the list again for the same target invariant.
    view_conjectures(agent, target_invariants=[target], search=search, console=console)


def probability_distribution(target, df, num_features=4):
    import random
    import numpy as np
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df = df[numeric_cols]

    # Ensure the target exists in the dataframe
    if target not in df.columns:
        raise ValueError(f"Target {target} not in numeric columns!")

    df = df.fillna(0)

    # Split features and target
    X = df.drop(columns=[target])
    y = df[target]

    # Compute absolute Pearson correlation
    correlations = X.corrwith(y).abs()

    # Convert correlations into a probability distribution
    prob_dist = correlations / correlations.sum()

    # Remove problematic entries
    prob_dist = prob_dist.replace([np.inf, -np.inf], np.nan).dropna()

    # Renormalize
    prob_dist /= prob_dist.sum()

    # Now sample safely:
    return list(set(random.choices(
        population=prob_dist.index,
        weights=prob_dist.values,
        k=num_features,
    )))

def write_on_the_wall2(agent, target_invariants=None, search=True, console=None):
    """
    Interactively view conjectures for a target invariant.

    First, the user selects the target invariant (if multiple exist) and then
    chooses from three categories: Equals, Upper Bound, or Lower Bound.
    The user scrolls through a numbered list for the chosen category, and then
    selects one to view detailed information in a Rich Panel with bold magenta
    and green formatting.

    Args:
        agent: The object that contains the conjectures (and optionally a knowledge_table).
        target_invariants (list, optional): A list of target invariants to consider. If None,
            all keys from agent.conjectures are used.
        search (bool): If True, additional search/percentage details are displayed.
        console: A Rich Console instance for output.
    """
    # Ensure we have a console.
    if console is None:
        from rich.console import Console
        console = Console()

    # Display a fancy header.
    fig = Figlet(font='slant')
    console.print(fig.renderText("Graffiti AI"), style="bold cyan")
    console.print("Author: Randy R. Davila, PhD")
    console.print("Automated Conjecturing since 2017")
    console.print("=" * 80)

    # If no target invariants were passed, use all available.
    if target_invariants is None:
        target_invariants = list(agent.conjectures.keys())

    # Prompt for target invariant selection if more than one exists.
    if len(target_invariants) > 1:
        selected_target = select("Select a target invariant:", choices=target_invariants).ask()
    else:
        selected_target = target_invariants[0]

    # Get conjecture data for the chosen target.
    target_data = agent.conjectures.get(selected_target, {})

    # Prompt the user to select a conjecture category.
    category_choice = select(
        "Select a conjecture category:",
        choices=["Equals", "Upper Bounds", "Lower Bounds", "Exit"],
        style=custom_style,
    ).ask()

    # Map the user's choice to the key used in agent.conjectures.
    if category_choice.lower().startswith("equal"):
        category_key = "equals"
    elif category_choice.lower().startswith("upper"):
        category_key = "upper"
    elif category_choice.lower().startswith("lower"):
        category_key = "lower"
    elif category_choice.lower().startswith("exit"):
        return

    # Retrieve the list of conjectures for the selected category.
    conj_list = target_data.get(category_key, [])
    if not conj_list:
        console.print(f"[red]No {category_choice} conjectures available for target invariant {selected_target}.[/red]")
        return

    # Build a numbered list of conjecture summaries.
    choices = []
    for i, conj in enumerate(conj_list[:10], start=1):
        # For a simple summary, convert the hypothesis (replacing underscores) and build a statement.
        hypothesis = convert_hypothesis(conj.hypothesis)
        conclusion = conj._set_conclusion()
        statement = f"For any {hypothesis}, {conclusion}."
        summary = f"{i}: {statement}"
        choices.append(summary)
    choices.append("Exit")

    # Let the user select a conjecture summary.
    selected_summary = select("Select a conjecture to view details:", choices=choices).ask()
    if selected_summary == "Exit":
        return

    # Extract the index from the selected summary.
    try:
        index = int(selected_summary.split(":")[0]) - 1
    except (ValueError, IndexError):
        console.print("[red]Error processing your selection.[/red]")
        return

    # Get the selected conjecture.
    selected_conj = conj_list[index]

    # Build detailed information.
    details = []
    hypothesis = convert_hypothesis(selected_conj.hypothesis)
    conclusion = selected_conj._set_conclusion()
    details.append(f"[bold magenta]Statement:[/bold magenta] For any [bold green]{hypothesis}[/bold green], [bold green]{conclusion}[/bold green].")
    details.append(f"[bold magenta]Target Invariant:[/bold magenta] {selected_conj.target}")
    details.append(f"[bold magenta]Bound Type:[/bold magenta] {selected_conj.bound_type}")
    if hasattr(selected_conj, 'complexity') and selected_conj.complexity is not None:
        details.append(f"[bold magenta]Complexity:[/bold magenta] {selected_conj.complexity}")
    if selected_conj.touch > 0:
        if selected_conj.touch > 1:
            details.append(f"[bold magenta]Sharp on:[/bold magenta] {selected_conj.touch} objects.")
        else:
            details.append(f"[bold magenta]Sharp on:[/bold magenta] 1 object.")
    else:
        details.append(f"[bold magenta]Inequality is strict.[/bold magenta]")

    # Helper to format a list of sharp instances into columns.
    def format_sharp_instances(instances, num_columns=4, indent="    "):
        items = sorted(str(item) for item in instances)
        if not items:
            return ""
        max_width = max(len(item) for item in items)
        rows = (len(items) + num_columns - 1) // num_columns
        formatted_rows = []
        for row in range(rows):
            row_items = []
            for col in range(num_columns):
                idx = col * rows + row
                if idx < len(items):
                    row_items.append(items[idx].ljust(max_width))
            formatted_rows.append(indent + "   ".join(row_items))
        return "\n".join(formatted_rows)

    if hasattr(selected_conj, 'sharp_instances') and selected_conj.sharp_instances:
        details.append(f"[bold magenta]Sharp Instances:[/bold magenta]")
        details.append(format_sharp_instances(selected_conj.sharp_instances))

    # Optionally, include percentage info from the agent's knowledge table.
    if search and hasattr(agent, 'knowledge_table') and selected_conj.hypothesis in agent.knowledge_table.columns:
        hyp_df = agent.knowledge_table[agent.knowledge_table[selected_conj.hypothesis] == True]
        total_hyp = len(hyp_df)
        if total_hyp > 0:
            percent_sharp = 100 * selected_conj.touch / total_hyp
            details.append(f"[bold magenta]Percentage of hypothesis objects that are sharp:[/bold magenta] {percent_sharp:.1f}%")
        else:
            details.append(f"[bold magenta]No objects satisfy the hypothesis.[/bold magenta]")

    # Combine the details into a single text block.
    details_text = "\n".join(details)

    # Display the details in a Panel.
    panel = Panel(details_text,
                  title=f"[bold magenta]{category_choice} Conjecture Details[/bold magenta]",
                  style="magenta")
    console.print(panel)

    # Wait for the user to continue.
    Prompt.ask("Press Enter to return to the conjecture menu")

    # Re-show the conjecture selection menu for the same target invariant.
    write_on_the_wall2(agent, target_invariants=[selected_target], search=search, console=console)

def write_on_the_wall(agent, target_invariants=None, search=True, console=None):
    """
    Interactively view conjectures for a target invariant.

    The user is first prompted to select a target invariant (if more than one exists)
    and then a conjecture category: Equals, Upper Bound, or Lower Bound.

    After that, the user scrolls through a numbered list of conjecture summaries.
    When a conjecture is selected, its detailed information is displayed in a Rich Panel.
    In addition to the basic details (statement, target invariant, bound type, etc.),
    if the conjecture has sharp instances and the agent's knowledge table is available,
    the common boolean and numeric properties among the sharp instances are computed
    and shown.

    Args:
        agent: An object containing an attribute `conjectures` (and optionally `knowledge_table`,
               `boolean_columns`, and `numerical_columns`).
        target_invariants (list, optional): List of target invariants to consider. If None,
            all keys in agent.conjectures are used.
        search (bool): If True, additional details (sharp instance percentages and common properties)
            are included.
        console: A Rich Console instance for output.
    """
    if console is None:
        from rich.console import Console
        console = Console()

    # Display header using Figlet.
    fig = Figlet(font='slant')
    console.print(fig.renderText("Graffiti AI"), style="bold cyan")
    console.print("Author: Randy R. Davila, PhD")
    console.print("Automated Conjecturing since 2017")
    console.print("=" * 80)

    # Use all available target invariants if none are provided.
    if target_invariants is None:
        target_invariants = list(agent.conjectures.keys())

    # Prompt for target invariant selection if more than one exists.
    if len(target_invariants) > 1:
        selected_target = select("Select a target invariant:", choices=target_invariants).ask()
    else:
        selected_target = target_invariants[0]

    # Prompt the user to select a conjecture category.
    category_choice = select(
        "Select a conjecture category:",
        choices=["Equals", "Upper Bound", "Lower Bound", "Exit"],
        style=custom_style,
    ).ask()
    if category_choice.lower().startswith("equal"):
        category_key = "equals"
    elif category_choice.lower().startswith("upper"):
        category_key = "upper"
    elif category_choice.lower().startswith("lower"):
        category_key = "lower"
    elif category_choice.lower().startswith("exit"):
        return
    else:
        console.print("[red]Invalid category selected.[/red]")
        return

    # Retrieve the list of conjectures for the selected target and category.
    conj_list = agent.conjectures.get(selected_target, {}).get(category_key, [])
    if not conj_list:
        console.print(f"[red]No {category_choice} conjectures available for target invariant {selected_target}.[/red]")
        return

    # Build a numbered list of conjecture summaries.
    choices_list = []
    for i, conj in enumerate(conj_list[:10], start=1):
        hypothesis = convert_hypothesis(conj.hypothesis)
        conclusion = conj._set_conclusion()
        statement = f"For any {hypothesis}, {conclusion}."
        summary = f"{i}: {statement}"
        choices_list.append(summary)
    choices_list.append("Exit")

    # Let the user select a conjecture summary.
    selected_summary = select("Select a conjecture to view details:", choices=choices_list, style=custom_style).ask()
    if selected_summary == "Exit":
        return

    try:
        index = int(selected_summary.split(":")[0]) - 1
    except (ValueError, IndexError):
        console.print("[red]Error processing your selection.[/red]")
        return
    selected_conj = conj_list[index]

    # Build detailed information.
    details_lines = []
    hypothesis = convert_hypothesis(selected_conj.hypothesis)
    conclusion = selected_conj._set_conclusion()
    details_lines.append(f"[bold magenta]Statement:[bold green] For any [bold green]{hypothesis}[/bold green], [bold green]{conclusion}[/bold green].")
    details_lines.append(f"[bold magenta]Target Invariant:[/bold magenta] {selected_conj.target}")
    details_lines.append(f"[bold magenta]Bound Type:[/bold magenta] {selected_conj.bound_type}")
    if hasattr(selected_conj, 'complexity') and selected_conj.complexity is not None:
        details_lines.append(f"[bold magenta]Complexity:[/bold magenta] {selected_conj.complexity}")
    if selected_conj.touch > 0:
        if selected_conj.touch > 1:
            details_lines.append(f"[bold magenta]Sharp on:[/bold magenta] {selected_conj.touch} objects.")
        else:
            details_lines.append(f"[bold magenta]Sharp on:[/bold magenta] 1 object.")
    else:
        details_lines.append(f"[bold magenta]Inequality is strict.[/bold magenta]")

    # --- Helper functions for formatting and common properties ---
    def get_sharp_subset(df, sharp_ids):
        if 'name' in df.columns:
            return df[df['name'].isin(sharp_ids)]
        else:
            return df.loc[sharp_ids]

    def format_sharp_instances(instances, num_columns=4, indent="    "):
        items = sorted(str(item) for item in instances)
        if not items:
            return ""
        max_width = max(len(item) for item in items)
        rows = (len(items) + num_columns - 1) // num_columns
        formatted_rows = []
        for row in range(rows):
            row_items = []
            for col in range(num_columns):
                idx = col * rows + row
                if idx < len(items):
                    row_items.append(items[idx].ljust(max_width))
            formatted_rows.append(indent + "   ".join(row_items))
        return "\n".join(formatted_rows)

    def find_common_boolean_properties(df, sharp_ids, boolean_columns):
        subset = get_sharp_subset(df, sharp_ids)
        common_props = {}
        for col in boolean_columns:
            unique_vals = subset[col].unique()
            if len(unique_vals) == 1:
                common_props[col] = unique_vals[0]
        return common_props

    def find_common_numeric_properties(df, sharp_ids, numeric_columns):
        subset = get_sharp_subset(df, sharp_ids)
        common_props = {}
        for col in numeric_columns:
            values = subset[col].dropna()
            props = []
            if (values == 0).all():
                props.append("all zero")
            common_props[col] = props
        return common_props
    # -----------------------------------------------------------------

    # If sharp instances exist, show them and compute common properties.
    if hasattr(selected_conj, 'sharp_instances') and selected_conj.sharp_instances:
        details_lines.append(f"[bold magenta]Sharp Instances:[/bold magenta]")
        details_lines.append(format_sharp_instances(selected_conj.sharp_instances))
        if search and hasattr(agent, 'knowledge_table'):
            sharp_ids = list(selected_conj.sharp_instances)
            common_bool = {}
            common_numeric = {}
            if hasattr(agent, 'boolean_columns'):
                common_bool = find_common_boolean_properties(agent.knowledge_table, sharp_ids, agent.boolean_columns)
            if hasattr(agent, 'numerical_columns'):
                common_numeric = find_common_numeric_properties(agent.knowledge_table, sharp_ids, agent.numerical_columns)
            if common_bool or common_numeric:
                details_lines.append(f"[bold magenta]Common properties among sharp instances:[/bold magenta]")
                if common_bool:
                    details_lines.append("[bold magenta]Constant boolean columns:[/bold magenta]")
                    for col, val in common_bool.items():
                        details_lines.append(f"   {col} == {val}")
                if common_numeric:
                    details_lines.append("[bold magenta]Common numeric properties:[/bold magenta]")
                    for col, props in common_numeric.items():
                        if props:
                            details_lines.append(f"   {col}: {', '.join(props)}")
                        else:
                            details_lines.append(f"   {col}: None")
            else:
                details_lines.append(f"[bold magenta]No common properties found among sharp instances.[/bold magenta]")

    # Optionally, include percentage info from the knowledge table.
    if search and hasattr(agent, 'knowledge_table') and selected_conj.hypothesis in agent.knowledge_table.columns:
        hyp_df = agent.knowledge_table[agent.knowledge_table[selected_conj.hypothesis] == True]
        total_hyp = len(hyp_df)
        if total_hyp > 0:
            percent_sharp = 100 * selected_conj.touch / total_hyp
            details_lines.append(f"[bold magenta]Percentage of hypothesis objects that are sharp:[/bold magenta] {percent_sharp:.1f}%")
        else:
            details_lines.append(f"[bold magenta]No objects satisfy the hypothesis.[/bold magenta]")

    details_text = "\n".join(details_lines)

    # Display the details in a Rich Panel.
    panel = Panel(details_text,
                  title=f"[bold magenta]{category_choice} Conjecture Details[/bold magenta]",
                  style="magenta")
    console.print(panel)

    # Wait for the user and then return to the conjecture menu.
    Prompt.ask("Press Enter to return to the conjecture menu")
    write_on_the_wall(agent, target_invariants=[selected_target], search=search, console=console)

def conjecture_mode(console):
    """
    Runs the Graffiti AI in conjecture mode, allowing the user to enter a graph
    and then ask the AI to conjecture on a property of the polytope database.
    """
    graffiti = GraffitiAI()
    console.print("[bold cyan]Welcome to Graffiti AI Conjecture Mode![/bold cyan]")

    graffiti.read_csv("Simple_Polytope_Data/simple_polytope_properties.csv")
    graffiti.vectorize(['p_vector'])
    graffiti.add_statistics(['p_vector'])
    graffiti.knowledge_table['p_3'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[0])
    graffiti.knowledge_table['p_4'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[1] if len(x) > 1 else 0)
    graffiti.knowledge_table['p_5'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[2] if len(x) > 2 else 0)
    graffiti.knowledge_table['p_6'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[3] if len(x) > 3 else 0)
    graffiti.knowledge_table['p_7'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[4] if len(x) > 4 else 0)
    graffiti.knowledge_table['sum(p_vector)'] = graffiti.knowledge_table['p_vector'].apply(lambda x: sum(x))

    # reset all numerical columns of the knowledge_table
    numerical_columns = graffiti.knowledge_table.select_dtypes(include=['number']).columns.tolist()

    # drop the columns that are not needed
    graffiti.drop_columns(['p_vector', 'adjacency_matrix', 'size'])

    while True:
        # prompy the user to select a numerical property to conjecture on for them to scroll through and select.
        numerical_properties = numerical_columns
        target_property = questionary.select(
            "Select a numerical property to conjecture on:",
            choices=numerical_properties,
            style=custom_style,
        ).ask()
        target_property = [target_property]

        # prompt the user to increase complexity (if they want) from complexity 1 to 3.
        yes_no = questionary.select(
            "Would you like to increase the complexity level?",
            choices=["Yes", "No"],
            style=custom_style,
        ).ask()
        if yes_no == "Yes":
            graffiti.set_complexity(avoid_columns=target_property, max_complexity=1)
            console.print(f"[bold cyan]Complexity level increased.[/bold cyan]")

        boolean_properties = graffiti.boolean_columns

        # prompt the user to conjecture, to start over, or to exit back to the main menu.
        while True:
            perform_conjecture = questionary.select(
                "Select an option:",
                choices=[
                    f"Conjecture on {target_property[0]}",
                    "Start over",
                    "Exit to main menu"
                ],
                style=custom_style,
            ).ask()

            if perform_conjecture == f"Conjecture on {target_property[0]}":
                # prompt the user to select the number of searches to perform.
                num_searches = questionary.text(
                    "Enter the number of searches to perform:",
                    style=custom_style,
                ).ask()
                num_searches = int(num_searches)

                for _ in range(num_searches):
                    print(f"Searching stage {_ + 1} of {num_searches} search processes....")
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=3,
                        lower_b_min=-3,
                        upper_b_max=3,
                        upper_b_min=-3,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=2,
                        lower_b_min=-2,
                        upper_b_max=2,
                        upper_b_min=-2,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=None,
                        lower_b_min=None,
                        upper_b_max=None,
                        upper_b_min=None,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 2),
                        lower_b_max=3,
                        lower_b_min=-3,
                        upper_b_max=3,
                        upper_b_min=-3,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 2),
                        lower_b_max=2,
                        lower_b_min=-2,
                        upper_b_max=2,
                        upper_b_min=-2,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 2),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 2),
                        lower_b_max=None,
                        lower_b_min=None,
                        upper_b_max=None,
                        upper_b_min=None,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 3),
                        lower_b_max=3,
                        lower_b_min=-3,
                        upper_b_max=3,
                        upper_b_min=-3,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 3),
                        lower_b_max=2,
                        lower_b_min=-2,
                        upper_b_max=2,
                        upper_b_min=-2,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 3),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 3),
                        lower_b_max=None,
                        lower_b_min=None,
                        upper_b_max=None,
                        upper_b_min=None,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                console.print("[bold cyan]Conjecture complete![/bold cyan]")
                # Display the conjecture results using write on the wall with search = True
                # write_on_the_wall(graffiti, target_invariants=target_property, search=True)
                # view_conjectures(graffiti, target_invariants=target_property, search=True, console=console)
                write_on_the_wall(graffiti, target_invariants=target_property, search=True, console=console)

            elif perform_conjecture == "Start over":
                break
            else:
                return

