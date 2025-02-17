import os
import pandas as pd
import pytest

def get_property_names():
    """
    Reads property names (one per line) from polytope_properties.txt.
    """
    properties_file = os.path.join("Simple_Polytope_Data", "polytope_properties.txt")
    with open(properties_file, "r") as f:
        properties = [line.strip() for line in f if line.strip()]
    return properties

def test_csv_columns_match_properties():
    """
    Checks that the CSV file has exactly the columns:
    "name", "edgelist", "adjacency_matrix", plus all property names in polytope_properties.txt.
    """
    csv_path = os.path.join("Simple_Polytope_Data", "simple_polytope_properties.csv")
    assert os.path.exists(csv_path), f"CSV file not found at {csv_path}"

    # Read the CSV file
    df = pd.read_csv(csv_path)
    csv_columns = list(df.columns)

    # Base columns that are always expected
    base_columns = ["name", "edgelist", "adjacency_matrix"]

    # Remove the base columns
    csv_columns = [x for x in csv_columns if x not in base_columns]

    # Get the property names from the text file
    property_columns = get_property_names()



    # Check if the sorted lists match (order may not matter)
    assert sorted(csv_columns) == sorted(property_columns), (
        f"CSV columns {csv_columns} do not match expected columns {property_columns}"
    )
