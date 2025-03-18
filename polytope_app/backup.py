import os
import shutil
import tempfile

__all__ = [
    'create_backup',
    'reset_session',
]

backup_folder = None

def create_backup(console):
    """
    Creates backups of files/directories that might be modified during the session.
    """
    global backup_folder
    backup_folder = tempfile.mkdtemp(prefix="polytope_backup_")
    console.print(f"[blue]Creating backup in {backup_folder}[/blue]")

    # Backup the Edge_Data directory.
    edge_data_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    if os.path.isdir(edge_data_dir):
        backup_edge_dir = os.path.join(backup_folder, "Edge_Data")
        shutil.copytree(edge_data_dir, backup_edge_dir)

    # Backup the CSV database file.
    csv_file = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    if os.path.isfile(csv_file):
        shutil.copy(csv_file, backup_folder)

    # Backup the properties file.
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    if os.path.isfile(properties_file):
        shutil.copy(properties_file, backup_folder)

def reset_session(console):
    """
    Restores the backed-up files/directories, deleting any changes or new files created.
    """
    global backup_folder
    if backup_folder is None:
        console.print("[red]No backup available. Cannot reset session.[/red]")
        return

    console.print("[yellow]Resetting session...[/yellow]")

    # Restore the Edge_Data directory.
    edge_data_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    backup_edge_dir = os.path.join(backup_folder, "Edge_Data")
    if os.path.isdir(edge_data_dir):
        shutil.rmtree(edge_data_dir)
    if os.path.isdir(backup_edge_dir):
        shutil.copytree(backup_edge_dir, edge_data_dir)

    # Restore the CSV database file.
    csv_file = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    backup_csv_file = os.path.join(backup_folder, "simple_polytope_properties.csv")
    if os.path.isfile(csv_file):
        os.remove(csv_file)
    if os.path.isfile(backup_csv_file):
        shutil.copy(backup_csv_file, csv_file)

    # Restore the properties file.
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    backup_properties_file = os.path.join(backup_folder, "polytope_properties.txt")
    if os.path.isfile(properties_file):
        os.remove(properties_file)
    if os.path.isfile(backup_properties_file):
        shutil.copy(backup_properties_file, properties_file)

    console.print("[green]Session has been reset to its original state.[/green]")
