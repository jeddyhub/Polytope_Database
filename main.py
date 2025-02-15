import os
import networkx as nx
import graphcalc as gc
import pandas as pd

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
    (via getattr) except for 'girth' which is computed here directly.

    Returns a dictionary of property values.
    """
    file_path = os.path.join("Simple_Polytope_Data", "Edge_Data", name)
    try:
        # Read the graph; assume node labels are integers.
        G = nx.read_edgelist(file_path, nodetype=int)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

    if G.number_of_nodes() == 0:
        return {}

    # Remove the file extension (assuming '.txt')
    props = {
        'name': name[:-4],
        'edgelist' : [e for e in G.edges()],
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

def process_all_edge_files_and_save_csv():
    """
    Reads every simple_polytope edgelist file in Simple_Polytope_Data/Edge_Data,
    computes the properties using functions from graphcalc (and networkx as fallback),
    and saves all the results as rows in a CSV file.
    """
    property_names = get_property_names()
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")

    # Get all .txt edgelist files.
    files = [f for f in os.listdir(edge_dir) if f.endswith(".txt")]

    all_data = []
    for name in files:
        props = compute_properties_from_edge_file(name, property_names)
        all_data.append(props)

    df = pd.DataFrame(all_data)
    num_rows = df.shape[0]  # Correct way to get the number of rows.
    output_directory = "Simple_Polytope_Data"
    output_csv = os.path.join(output_directory, f"simple_polytope_properties_{num_rows}.csv")
    df.to_csv(output_csv, index=False)
    print(f"CSV file '{output_csv}' saved.")

if __name__ == "__main__":
    process_all_edge_files_and_save_csv()
