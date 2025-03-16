import sys
import questionary
import pyfiglet
from rich.console import Console
from polytope_app.backup import create_backup, reset_session
from polytope_app import database, edge_list, conjecture, git_interface, utils

console = Console()

def main_menu():
    # Automatically create a backup when the app starts.
    create_backup(console)

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
                "9: Polytope Conjecture",
                "10: Exit",
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
            conjecture.conjecture_mode(console)
        elif option == 10:
            console.print("[bold red]Exiting. Goodbye![/bold red]")
            sys.exit(0)
        else:
            console.print("[red]Invalid option. Please choose a valid option.[/red]")

if __name__ == "__main__":
    main_menu()
