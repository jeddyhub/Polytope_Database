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

        assert gc.simple_polytope_graph(G)
        # except Exception as e:
        #     assert False, f"gc.simple_polytope_graph raised an exception for {filename}: {e}"

        # # Assert that the function returned a non-None value.
        # assert spg is not None, f"gc.simple_polytope_graph returned None for {filename}"

        # # Optionally, check that the return type is as expected (e.g., a string or list)
        # assert isinstance(spg, (str, list)), (
        #     f"Unexpected type ({type(spg)}) returned from gc.simple_polytope_graph for {filename}"
        # )
