import sys
import questionary
import pyfiglet
from rich.console import Console
from polytope_app.backup import create_backup, reset_session
from polytope_app import database, edge_list, conjecture, git_interface, utils
from polytope_app.utils import view_conjectures
from graffitiai import GraffitiAI

console = Console()

def main_menu():
    # Automatically create a backup when the app starts.
    create_backup(console)

    # Initialize the GraffitiAI object
    graffiti = GraffitiAI()

    # Load the database
    graffiti.read_csv("Simple_Polytope_Data/simple_polytope_properties.csv")

    # Add properties to the knowledge table.
    graffiti.vectorize(['p_vector'])
    graffiti.add_statistics(['p_vector'])
    graffiti.knowledge_table['p_3'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[0])
    graffiti.knowledge_table['p_4'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[1] if len(x) > 1 else 0)
    graffiti.knowledge_table['p_5'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[2] if len(x) > 2 else 0)
    graffiti.knowledge_table['p_6'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[3] if len(x) > 3 else 0)
    graffiti.knowledge_table['p_7'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[4] if len(x) > 4 else 0)
    graffiti.knowledge_table['sum(p_vector)'] = graffiti.knowledge_table['p_vector'].apply(lambda x: sum(x))

    # drop the columns that are not needed
    graffiti.drop_columns(['p_vector', 'adjacency_matrix', 'size'])

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
                "9: Make Conjectures",
                "10: View Conjectures",
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
            view_conjectures(graffiti, numerical_columns, console)
        elif option == 11:
            console.print("[bold red]Exiting. Goodbye![/bold red]")
            sys.exit(0)
        else:
            console.print("[red]Invalid option. Please choose a valid option.[/red]")

if __name__ == "__main__":
    main_menu()
