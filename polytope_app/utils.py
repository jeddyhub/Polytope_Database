from prompt_toolkit.styles import Style
from questionary import select
from rich.panel import Panel
from rich.prompt import Prompt
from pyfiglet import Figlet
import questionary

__all__ = [
    'custom_style',
    'git_custom_style',
    'convert_hypothesis',
    'view_conjectures',
    'write_on_the_wall',
]

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

def convert_hypothesis(hypothesis):

    if hypothesis == "simple_polytope_graph":
        return "simple polytope graph"
    elif hypothesis == "connected_and_bipartite":
        return "simple polytope graph without odd cycles"
    # elif hypothesis == "simple_polytope_graph_with_p6_greater_than_zero":
    #     return "simple polytope graph with p_6 > 0"
    # elif hypothesis == "is_at_free":
    #     return "simple asteroidal triple free polytope graph"
    elif hypothesis == "simple_polytope_graph_with_p6_zero":
        return "simple polytope graph with p_6 = 0"
    # elif hypothesis == "zeros_clustered(p_vector)":
    #     return "simple polytope graph with clustered zeros in p_vector"
    else:
        return hypothesis

def write_on_the_wall(agent, numerical_columns, target_invariants=None, search=True, console=None):
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

    conjectures = agent.conjectures
    if not conjectures:
        console.print("[yellow]No conjectures to display.[/yellow] Use the 'Make Conjectures' option to add a new conjecture.")
        return

    if console is None:
        from rich.console import Console
        console = Console()

    # Display header using Figlet.
    fig = Figlet(font='slant')
    console.print(fig.renderText("Polytope AI"), style="bold cyan")
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
        choices=["Equalities", "Upper Bounds", "Lower Bounds", "Exit"],
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

    if selected_conj.touch > 0:
        statement = f"\n For any {hypothesis}, \n  \n        {conclusion}, \n  \n  and this bound is sharp on at least {selected_conj.touch} simple polytopes. \n"
    else:
        statement = f"\n For any {hypothesis}, \n  \n        {conclusion}. \n"
    details_lines.append(f"[bold magenta]Statement: [bold green]{statement}")
    details_lines.append(f"[bold magenta]Target Invariant:[/bold magenta] {selected_conj.target}")
    # other invariants
    if hasattr(selected_conj, 'other_invariants') and selected_conj.other_invariants:
        details_lines.append(f"[bold magenta]Other Invariants:[/bold magenta] {', '.join(selected_conj.other_invariants)}")
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
        # Check if all properties are the same numeric value.
        for col in numeric_columns:
            values = subset[col].dropna()
            if len(values.unique()) == 1:
                common_props[col] = [f"all {values.iloc[0]}"]
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
                common_numeric = find_common_numeric_properties(agent.knowledge_table, sharp_ids, numerical_columns)
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
                  style="cyan")
    console.print(panel)

    # Wait for the user and then return to the conjecture menu.
    Prompt.ask("Press Enter to return to the conjecture menu")
    write_on_the_wall(agent, numerical_columns, target_invariants=[selected_target], search=search, console=console)

def view_conjectures(graffiti, numerical_columns, console):
    """
    View the current conjectures and their status.
    """
    conjectures = graffiti.conjectures
    if not conjectures:
        console.print("[yellow]No conjectures to display.[/yellow] Use the 'Make Conjectures' option to add a new conjecture.")
        return

    # Write on the wall
    write_on_the_wall(graffiti, numerical_columns, search=True, console=console)
