import os
import networkx as nx
import graphcalc as gc

def test_simple_polytope_graph_for_all_edge_lists():
    """
    For every edgelist file in Simple_Polytope_Data/Edge_Data,
    read the graph and compute gc.simple_polytope_graph(G).
    Assert that a valid value is returned.
    """
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    files = [f for f in os.listdir(edge_dir) if f.endswith(".txt")]

    # Ensure there is at least one edgelist file.
    assert files, "No edgelist files found in Simple_Polytope_Data/Edge_Data"

    for filename in files:
        file_path = os.path.join(edge_dir, filename)
        try:
            G = nx.read_edgelist(file_path, nodetype=int)
        except Exception as e:
            assert False, f"Error reading {filename}: {e}"

        result = gc.simple_polytope_graph(G)
        assert result, f"gc.simple_polytope_graph returned a falsy value for '{filename}': {result}"
