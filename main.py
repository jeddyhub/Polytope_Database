import sys
import questionary
import pyfiglet
from rich.console import Console
from polytope_app.backup import create_backup, reset_session
from polytope_app import database, edge_list, conjecture, git_interface, utils
from polytope_app.utils import view_conjectures, write_on_the_wall
from graffitiai import GraffitiAI

console = Console()

def main_menu():
    # Automatically create a backup when the app starts.
    create_backup(console)

    # Initialize the GraffitiAI object
    graffiti = GraffitiAI()

    # Load the database
    graffiti.read_csv("Simple_Polytope_Data/simple_polytope_properties.csv")

    # Rename the 'p_vector' column
    graffiti.knowledge_table.rename(columns={'p_vector': '[p₃, p₄, ..., pₙ]'}, inplace=True)
    # Add properties to the knowledge table.
    graffiti.vectorize(['[p₃, p₄, ..., pₙ]'])
    graffiti.add_statistics(['[p₃, p₄, ..., pₙ]'])
    graffiti.knowledge_table.rename(columns={'order': 'V'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'size': 'E'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'mostly_zeros([p₃, p₄, ..., pₙ])': 'simple polytope graph with at least 70% of [p₃, p₄, ..., pₙ] equal to zero'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'first_index_half_cumsum([p₃, p₄, ..., pₙ])': 'min{k : p₃ + ... + pₖ ≥ ½ (p₃ + ... + pₙ)}'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'variance([p₃, p₄, ..., pₙ])': 'σ²(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'std_dev([p₃, p₄, ..., pₙ])': 'σ(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'max([p₃, p₄, ..., pₙ])': 'max(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'min([p₃, p₄, ..., pₙ])': 'min(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'mean([p₃, p₄, ..., pₙ])': 'μ(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'median_absolute_deviation([p₃, p₄, ..., pₙ])': 'MAD(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'count_even([p₃, p₄, ..., pₙ])': 'count_even(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'count_odd([p₃, p₄, ..., pₙ])': 'count_odd(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'count_zero([p₃, p₄, ..., pₙ])': 'count_zero(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'count_non_zero([p₃, p₄, ..., pₙ])': 'count_non_zero(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'unique_count([p₃, p₄, ..., pₙ])': '|{pₖ : 3 ≤ k ≤ n}|'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'range([p₃, p₄, ..., pₙ])': '(max{pₖ : 3 ≤ k ≤ n} - min{pₖ : 3 ≤ k ≤ n})'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'median([p₃, p₄, ..., pₙ])': 'median(p₃, p₄, ..., pₙ)'}, inplace=True)
    graffiti.knowledge_table.rename(columns={'zeros_clustered([p₃, p₄, ..., pₙ])': 'simple polytope graph with at least 50% of zero values in the p-vector clustered contiguously'}, inplace=True)
    graffiti.knowledge_table['p₃'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: x[0])
    graffiti.knowledge_table['p₄'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: x[1] if len(x) > 1 else 0)
    graffiti.knowledge_table['p₅'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: x[2] if len(x) > 2 else 0)
    graffiti.knowledge_table['p₆'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: x[3] if len(x) > 3 else 0)
    graffiti.knowledge_table['p₇'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: x[4] if len(x) > 4 else 0)
    graffiti.knowledge_table['(p₃ + ... + pₙ)'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: sum(x))
    graffiti.knowledge_table['n'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: len(x) + 2)
    graffiti.knowledge_table['simple polytope graph with p₃ > 0'] = graffiti.knowledge_table['p₃'] > 0
    graffiti.knowledge_table['simple polytope graph with p₄ > 0'] = graffiti.knowledge_table['p₄'] > 0
    graffiti.knowledge_table['simple polytope graph with p₅ > 0'] = graffiti.knowledge_table['p₅'] > 0
    graffiti.knowledge_table['simple polytope graph with p₆ > 0'] = graffiti.knowledge_table['p₆'] > 0
    graffiti.knowledge_table['simple polytope graph with p₇ > 0'] = graffiti.knowledge_table['p₇'] > 0

    # graffiti.knowledge_table['k with pk > 0'] = graffiti.knowledge_table['[p₃, p₄, ..., pₙ]'].apply(lambda x: [k for k in range(3, len(x) + 3) if x[k - 3] > 0])

    # fullerene's only have p5 and p6 faces. To check this, we check the length of the p-vector is 4 and
    # the first two entries are zero and the last two entries are non-zero.
    graffiti.knowledge_table['fullerene'] = (graffiti.knowledge_table['n'] == 6) & (graffiti.knowledge_table['p₃'] == 0) & (graffiti.knowledge_table['p₄'] == 0) & (graffiti.knowledge_table['p₅'] > 0) & (graffiti.knowledge_table['p₆'] > 0)



    # drop the columns that are not needed
    graffiti.drop_columns(['[p₃, p₄, ..., pₙ]', 'length([p₃, p₄, ..., pₙ])', 'adjacency_matrix', 'E', 'simple_polytope_graph_with_p6_greater_than_zero'])

    # Get numerical columns of the knowledge_table.
    numerical_columns = graffiti.knowledge_table.select_dtypes(include=['number']).columns.tolist()

    while True:
        title_text = pyfiglet.figlet_format("Polytope AI", font="slant")
        console.print(title_text, style="bold cyan")
        choice = questionary.select(
            "Please select an option:",
            choices=[
                "1: Reset Session",
                "2: Recompute Database",
                "3: Update Database Polytopes",
                "4: Display Properties",
                "5: Run Tests",
                "6: Add Database Property",
                "7: Remove Database Property",
                "8: Git/GitHub",
                "9: Write on the Wall",
                "10: View the Wall",
                "11: Exit",
            ],
            style=utils.custom_style,
        ).ask()

        # Extract the numeric option from the choice
        try:
            option = int(choice.split(":")[0])
        except (ValueError, IndexError):
            console.print("[red]Invalid option format.[/red]")
            continue

        if option == 1:
            reset_session(console)
        elif option == 2:
            database.recompute_csv_database(console)
        elif option == 3:
            entry_choice = questionary.select(
                "How would you like to enter the edge list?",
                choices=[
                    "Manual entry (one edge per line)",
                    "Paste entire edge list",
                ],
                style=utils.custom_style,
            ).ask()
            if entry_choice.startswith("Manual"):
                edge_list.add_new_edge_list(console)
            elif entry_choice.startswith("Paste"):
                edge_list.add_new_edge_list_from_paste(console)
        elif option == 4:
            database.display_properties_of_entry(console)
        elif option == 5:
            database.run_pytests(console)
        elif option == 6:
            database.add_new_function(console)
        elif option == 7:
            database.remove_property(console)
        elif option == 8:
            git_interface.git_github_interface(console)
        elif option == 9:
            conjecture.conjecture_mode(graffiti, numerical_columns, console)
        elif option == 10:
            write_on_the_wall(graffiti, numerical_columns, search=True, console=console)
            # view_conjectures(graffiti, numerical_columns, console)
        elif option == 11:
            console.print("[bold red]Exiting. Goodbye![/bold red]")
            sys.exit(0)
        else:
            console.print("[red]Invalid option. Please choose a valid option.[/red]")

if __name__ == "__main__":
    main_menu()
