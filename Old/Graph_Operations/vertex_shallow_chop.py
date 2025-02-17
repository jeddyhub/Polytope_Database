import networkx as nx
import numpy as np

def chop_vertex(adj_matrix, vertex):
  # chop a specified vertex
  # inputs:
  # adj_matrix (numpy array) - Adjacency matrix of a graph
  # vertex (int) - index of vertex that we want to chop
  # outputs:
  # new_adj_matrix (numpy array) - Adjacency matrix of graph with vertex chopped
  
  G_nx = nx.Graph(adj_matrix)

  # Check if the graph is planar and get the planar embedding
  is_planar, embedding_nx = nx.check_planarity(G_nx)

  # for specified vertex, gather its neighbors
  neighbors = list(embedding_nx.neighbors_cw_order(vertex))

  n = adj_matrix.shape[0]
  num_neighbors = len(neighbors)

  # Create a new adjacency matrix for the modified graph
  new_size = n + num_neighbors - 1
  new_adj_matrix = np.zeros((new_size, new_size), dtype=int)

  # Copy the old edges except for the specified vertex
  for i in range(n):
    if i < vertex: # rows before vertex
      cols_before_i = adj_matrix[i, :vertex].tolist()
      cols_after_i = adj_matrix[i, vertex+1:].tolist()
      new_row = cols_before_i + cols_after_i + np.zeros(new_size - len(cols_before_i) - len(cols_after_i), dtype=int).tolist()
      new_adj_matrix[i] = new_row
    elif i > vertex: # rows after vertex
      cols_before_i = adj_matrix[i, :vertex].tolist()
      cols_after_i = adj_matrix[i, vertex+1:].tolist()
      new_adj_matrix[i-1] = cols_before_i + cols_after_i + np.zeros((new_size - len(cols_before_i) - len(cols_after_i)), dtype=int).tolist()

  # index of first new vertex = n - 1
  # index of last new vertex = new_size - 1
  # we will connect the first new vertex with the first neighbor in the list, and so on

  # Connect old neighbors to new vertices
  i = -1
  for x in neighbors:
    if x < vertex:
      new_adj_matrix[x][n + i] = 1
      new_adj_matrix[n + i][x] = 1
    if x > vertex:
      new_adj_matrix[x-1][n + i] = 1
      new_adj_matrix[n + i][x-1] = 1
    i += 1

  # Connect new vertices to one another

  for y in range(n-1, new_size - 1):
    new_adj_matrix[y][y+1] = 1
    new_adj_matrix[y+1][y] = 1

  # connect last new vertex to first one (complete the cycle)
  new_adj_matrix[n - 1][new_size - 1] = 1
  new_adj_matrix[new_size - 1][n - 1] = 1

  return new_adj_matrix
