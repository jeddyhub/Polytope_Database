import os
import networkx as nx
import graphcalc as gc
import pytest

def get_edgelist_files():
    """
    Returns a list of full paths to all .txt edgelist files in the directory.
    """
    edge_dir = os.path.join("Simple_Polytope_Data", "Edge_Data")
    return [os.path.join(edge_dir, f) for f in os.listdir(edge_dir) if f.endswith(".txt")]

@pytest.mark.parametrize("file_path", get_edgelist_files())
def test_simple_polytope_graph(file_path):
    """
    For the given edgelist file, read the graph and compute gc.simple_polytope_graph(G).
    Assert that a valid (truthy) value is returned.
    """
    filename = os.path.basename(file_path)
    try:
        G = nx.read_edgelist(file_path, nodetype=int)
    except Exception as e:
        pytest.fail(f"Error reading {filename}: {e}")

    result = gc.simple_polytope_graph(G)
    assert result, f"gc.simple_polytope_graph returned a false value for '{filename}': {result}"
