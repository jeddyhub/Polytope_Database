import subprocess
import questionary
import pyfiglet

from polytope_app.utils import git_custom_style
from rich.panel import Panel

def switch_branch(console):
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
def git_github_interface(console):
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
            switch_branch(console)

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
