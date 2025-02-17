import numpy as np
import networkx as nx
import pandas as pd

def add_some_rows(og_file_path, new_adj_mats, new_file_path):

  # inputs:
  # og_file_path (string) must be a csv file, must contain the following columns:
    # 'name' (indexing the instances, P{i} for instance i)
    # 'is_simple' (boolean entry, True for all instances in this dataset)
    # 'adjacency_matrix, 'edge_list', 'number_of_vertices', 'number_of_edges',
    # 'number_of_2faces', 'algebraic_connectivity', 'average_degree',
    # 'clique_number', 'density', 'diameter', 'girth', 'independence_number',
    # 'index', 'laplacian_largest_eigenvalue', 'matching_number', 'maximum_degree',
    # 'minimum_degree', 'number_of_spanning_trees', 'number_of_zero_eigenvalues',
    # 'radius', 'second_largest_eigenvalue', 'smallest_eigenvalue',
    # 'vertex_connectivity', 'vertex_cover_number'
    # followed by f'number_of_{k}_gons' for sufficient k
  # new_adj_mats (list) a list of adjacency matrices (instances) you want to add to the data
  # new_file_path (string) the path you want the new csv to be saved as

  # returns:
  # df_new (pandas dataframe)
  # and writes the new csv to your specified place

  df_og = pd.read_csv(og_file_path)
  # note: i'm assuming we have checked to ensure the additional graphs are not isomorphic
  # to any graphs already in the dataset.

  num_old_instances = df_og.shape[0]
  num_new_instances = len(new_adj_mats)

  new_names = [f'P{num_old_instances + i}' for i in range(num_new_instances)]

  new_data = {}
  new_data['name'] = new_names

  # identifying features
  is_simple = []
  adjacency_matrix = []
  edge_list = []
  number_of_vertices = []
  number_of_edges = []
  number_of_2faces = []

  # graph theoretic features
  algebraic_connectivity = []
  average_degree = []
  clique_number = []
  density = []
  diameter = []
  girth = []
  independence_number = []
  index = []
  laplacian_largest_eigenvalue = []
  matching_number = []
  maximum_degree = []
  minimum_degree = []
  number_of_spanning_trees = []
  number_of_zero_eigenvalues = []
  radius = []
  second_largest_eigenvalue = []
  smallest_eigenvalue = []
  vertex_connectivity = []
  vertex_cover_number = []

  # and pks
  pk_vec_col = []

  for A in new_adj_mats:
    A = np.array(A)
    num_verts = len(A[0])
    total_degree = sum(A@np.ones(num_verts))
    num_edges = total_degree / 2

    edges = []
    n = len(A[0])
    for i in range(n):
      for j in range(i,n):
        if A[i][j] == 1:
          edges += [(i,j)]

    # construct networkx graph object
    G = nx.from_numpy_array(A)
    L = gc.laplacian_matrix(G)

    # compute p vector
    pvec = gc.p_vector(G)
    pk_vec_col.append(pvec)

    is_simple.append(gc.connected_and_regular(G))
    adjacency_matrix.append(A.tolist())
    edge_list.append(edges)
    # number of vertices
    number_of_vertices.append(num_verts)
    # number of edges
    number_of_edges.append(num_edges)
    # number of 2 faces
    number_of_2faces.append(sum(pvec))


    # eigenvalues of adjacency and laplacian matrices
    # sorted smallest to largest
    A_eigenvals = gc.adjacency_eigenvalues(G)
    L_eigenvals = gc.laplacian_eigenvalues(G)

    # algebraic connectivity (2nd largest eigenvalue of Laplacian)
    algebraic_connectivity.append(L_eigenvals[1])

    # average degree
    average_degree.append(gc.average_degree(G))

    # clique number
    clique_number.append(gc.clique_number(G))

    # density (number of edges / total possible edges = n choose 2)
    possible_edges = (num_verts * (num_verts - 1))/2
    density.append(num_edges / possible_edges)

    # diameter
    diameter.append(gc.diameter(G))

    # girth
    girth.append(nx.girth(G))

    # independence number
    independence_number.append(gc.independence_number(G))

    # index
    # in other words: spectral radius
    index.append(gc.spectral_radius(G))

    # laplacian largest eigenvalue
    laplacian_largest_eigenvalue.append(L_eigenvals[-1])

    # matching number
    matching_number.append(gc.matching_number(G))

    # maximum degree
    maximum_degree.append(gc.maximum_degree(G))

    # minimum degree
    minimum_degree.append(gc.minimum_degree(G))

    # number of spanning trees
    # using kirchhoff's theorem
    chopped_L1 = np.delete(L, 1, axis=0)
    chopped_L2 = np.delete(chopped_L1, 1, axis=1)
    number_of_spanning_trees.append(np.linalg.det(chopped_L2))

    # number of zero eigenvalues of adjacency matrix
    zero_eigenvals = sum(1 for e in A_eigenvals if e == 0)
    number_of_zero_eigenvalues.append(zero_eigenvals)

    # radius
    radius.append(gc.radius(G))

    # second largest eigenvalue of the adjacency matrix
    second_largest_eigenvalue.append(A_eigenvals[-2])

    # smallest eigenvalue of the adjacency matrix
    smallest_eigenvalue.append(A_eigenvals[0])

    # vertex connectivity
    vertex_connectivity.append(nx.node_connectivity(G))

    # vertex cover number
    vertex_cover_number.append(gc.vertex_cover_number(G))

  # add this information to the dictionary of data
  # identifying features
  new_data['is_simple'] = is_simple
  new_data['adjacency_matrix'] = adjacency_matrix
  new_data['edge_list'] = edge_list
  new_data['number_of_vertices'] = number_of_vertices
  new_data['number_of_edges'] = number_of_edges
  new_data['number_of_2faces'] = number_of_2faces

  # invariants
  new_data['algebraic_connectivity'] = algebraic_connectivity
  new_data['average_degree'] = average_degree
  new_data['clique_number'] = clique_number
  new_data['density'] = density
  new_data['diameter'] = diameter
  new_data['girth'] = girth
  new_data['independence_number'] = independence_number
  new_data['index'] = index
  new_data['laplacian_largest_eigenvalue'] = laplacian_largest_eigenvalue
  new_data['matching_number'] = matching_number
  new_data['maximum_degree'] = maximum_degree
  new_data['minimum_degree'] = minimum_degree
  new_data['number_of_spanning_trees'] = number_of_spanning_trees
  new_data['number_of_zero_eigenvalues'] = number_of_zero_eigenvalues
  new_data['radius'] = radius
  new_data['second_largest_eigenvalue'] = second_largest_eigenvalue
  new_data['smallest_eigenvalue'] = smallest_eigenvalue
  new_data['vertex_connectivity'] = vertex_connectivity
  new_data['vertex_cover_number'] = vertex_cover_number

  # what is the largest k present in our dataset?
  max_k = 0
  for v in pk_vec_col:
    if len(v) + 2 > max_k:
      max_k = len(v) + 2

  p_k_cols = {}

  for i in range(3, max_k + 1):
    p_k_cols[f'number_of_{i}_gons'] = []

  for v in pk_vec_col:
    for i in range(3, max_k + 1):
      if (i-2) <= len(v):
        p_k_cols[f'number_of_{i}_gons'].append(v[i-3])
      else: p_k_cols[f'number_of_{i}_gons'].append(0)

  # make a dataframe out of these
  together = {**new_data, **p_k_cols}
  new_rows = pd.DataFrame.from_dict(together)

  # what was the max k in the original dataset?
  og_max_k = len(list(df_og)) - 25 # there are 25 columns besides number_of_k_gons

  if og_max_k < max_k:
    z1 = np.zeros(df_og.shape[0])
    for i in range(og_max_k + 1, max_k + 1):
      df_og[f'number_of_{i}_gons'] = z1

  if og_max_k > max_k:
    z2 = np.zeros(new_data.shape[0])
    for i in range(max_k + 1, og_max_k + 1):
      new_rows[f'number_of_{i}_gons'] = z2

  # put it all together
  df_new = pd.concat([df_og, new_rows])

  # write to csv in the specified location
  df_new.to_csv(new_file_path, index=False)

  return df_new
