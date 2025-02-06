import numpy as np
import networkx as nx
import pandas as pd

# compute the p vector of an instance
def p_k_vector(graph):
  # returns p-vector of polytope associated to planar, 3-connected graph
  # inputs:
  # graph (numpy array)   Adjacency Matrix of the graph
  # outputs:
  # p_vector (list)   p vector (p_3, p_4, p_5,...) of a polytope whose graph is the given graph

    num_i_sides = {} # keys are 3 (triangle), 4 (quadrilateral), 5 (pentagon), etc., values are how many of each kind of face.
    G_nx = nx.Graph(graph)

    # Check if the graph is planar and get the planar embedding
    is_planar, embedding_nx = nx.check_planarity(G_nx)

    # Construct poset of 1-skeleton
    # add vertices
    vert_elms = [] # a list 1,...,n

    for i in range(1, len(graph[0]) + 1):
        vert_elms = vert_elms + [i]

    # add edges
    edge_elms = []
    edge_dict = {} # keys are edge indices, values are the indicestwo vertices it contains

    # and relations
    relations = []

    for vert in vert_elms:
        vert_mat_index = vert - 1

        neighbors = [] # poset indices of neighbors
        for j in range(len(graph[0])):
            if graph[vert_mat_index][j] == 1:
                neighbors = neighbors + [j + 1]

        for buddy in neighbors:
            if vert < buddy:
                if len(edge_elms) == 0:
                    edge_elms = edge_elms + [vert_elms[-1] + 1]
                    edge_dict[edge_elms[-1]] = [vert, buddy]
                    relations = relations + [[vert, edge_elms[-1]]] + [[buddy, edge_elms[-1]]]
                else:
                    edge_elms = edge_elms + [edge_elms[-1] + 1]
                    edge_dict[edge_elms[-1]] = [vert, buddy]
                    relations = relations + [[vert, edge_elms[-1]]] + [[buddy, edge_elms[-1]]]

    # add faces
    face_elms = []
    face_dict = {} # key is the index of a face (in the poset lattice), feature is the first nx vertex list we find

    for edge in edge_dict:
        # Take in an edge, traverse its face to see which vertices are contained.
        two_vert_indices = edge_dict[edge]
        two_verts = []
        for i in two_vert_indices:
            two_verts = two_verts + [i-1]

        # first half-edge
        f1_vert_list = list(embedding_nx.traverse_face(v=two_verts[0], w=two_verts[1]))

        # test if this face has been accounted for yet
        test_face1 = []
        for face in face_dict:
            already_found_face = face_dict[face]
            if sorted(f1_vert_list) == sorted(already_found_face):
                test_face1 = test_face1 + [1]
                # if this face has already been acknowledged, take its index and add a relation
                relations = relations + [ [edge, face] ]

        # if this face has not been accounted for yet, add it to the dict / poset element list
        if len(test_face1) == 0:
            if len(face_elms) == 0:
                face_elms = face_elms + [edge_elms[-1] + 1]
                face_dict[face_elms[-1]] = f1_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]
            else:
                face_elms = face_elms + [face_elms[-1] + 1]
                face_dict[face_elms[-1]] = f1_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]

        # second half-edge
        f2_vert_list = list(embedding_nx.traverse_face(v=two_verts[1], w=two_verts[0]))

        # test if this face has been accounted for yet
        test_face2 = []
        for face in face_dict:
            already_found_face = face_dict[face]
            if sorted(f2_vert_list) == sorted(already_found_face):
                test_face2 = test_face2 + [1]
                # if this face has already been acknowledged, take its index and add a relation
                relations = relations + [ [edge, face] ]

        # if this face has not been accounted for yet, add it to the dict / poset element list
        if len(test_face2) == 0:
            if len(face_elms) == 0:
                face_elms = face_elms + [edge_elms[-1] + 1]
                face_dict[face_elms[-1]] = f2_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]
            else:
                face_elms = face_elms + [face_elms[-1] + 1]
                face_dict[face_elms[-1]] = f2_vert_list
                relations = relations + [ [edge, face_elms[-1]] ]

    for face in face_dict:
        if len(face_dict[face]) in num_i_sides:
            num_i_sides[len(face_dict[face])] += 1
        else:
            num_i_sides[len(face_dict[face])] = 1

    # get a vector of keys so we can sort it
    key_list = []
    for key in  num_i_sides:
        key_list += [key]
    key_list = sorted(key_list)
    max_k = key_list[-1]

    p_vector = []
    for i in range(3, max_k +1):
        if i in num_i_sides:
            p_vector += [num_i_sides[i]]
        else:
            p_vector += [0]

    return(p_vector)

# function to add a new row
def add_some_rows(og_file_path, new_adj_mats, new_file_path):
  # new_file_path

  # inputs:
  # og_file_path (string) must be a csv file, must contain the following columns:
    # 'name' (indexing the instances, P{i} for instance i)
    # 'is_simple' (boolean entry, True for all instances in this dataset)
    # 'adjacency_matrix, 'edge_list',
    # 'algebraic_connectivity', 'average_degree', 'clique_number', 'density', 
    # 'diameter', 'girth', 'independence_number', 'index', 
    # 'laplacian_largest_eigenvalue', 'matching_number', 'maximum_degree', 
    # 'minimum_degree', 'number_of_edges', 'number_of_spanning_trees', 
    # 'number_of_triangles', 'number_of_vertices', 'number_of_zero_eigenvalues', 
    # 'radius', 'second_largest_eigenvalue', 'smallest_eigenvalue', 
    # 'vertex_connectivity', 'vertex_cover_number'
    # followed by f'number_of_{k}_gons' for sufficient k
  # new_adj_mats (list) a list of adjacency matrices (instances) you want to add to the data
  # new_file_path (string) the name you want the new csv to be saved as

  # returns: 
  # df_new (pandas dataframe) 
  # and writes the new csv to your specified place

  df_og = pd.read_csv(og_file_path)
  # note: i'm assuming we have checked to ensure the additional graphs are not isomorphic
  # to any graphs already in the dataset.

  num_old_instances = df_og.shape[0]
  num_new_instances = len(new_adj_mats)

  new_names = []
  for i in range(num_new_instances):
    new_names += [f'P{num_old_instances + i}']

  new_data = {}
  new_data['name'] = new_names

  # define columns for graph-theoretical features
  is_simple = []
  adjacency_matrix = []
  edge_list = []
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
  number_of_edges = []
  number_of_spanning_trees = []
  number_of_triangles = [] 
  number_of_vertices = []
  number_of_zero_eigenvalues = [] 
  radius = []
  second_largest_eigenvalue = []
  smallest_eigenvalue = []
  vertex_connectivity = []
  vertex_cover_number = []

  for A in new_adj_mats:
    A = np.array(A)
    num_verts = len(A[0])

    edges = []
    n = len(A[0])
    for i in range(n):
      for j in range(i,n):
        if A[i][j] == 1:
          edges += [[i,j]]

    # construct networkx graph object 
    G = nx.from_numpy_array(A)
    
    is_simple += [nx.is_regular(G)]
    adjacency_matrix += [A]
    edge_list += [edges]

    # construct Laplacian
    ones_vector = np.ones(A[0].size)
    Degree = np.diag(ones_vector @ A)
    L = Degree - A
    
    # eigenvalues of adjacency and laplacian matrices
    A_eigenvals = np.linalg.eigvals(A)
    L_eigenvals = np.linalg.eigvals(L)
    A_eigenvals.sort()
    L_eigenvals.sort()

    # algebraic connectivity (2nd largest eigenvalue of Laplacian)
    algebraic_connectivity += [L_eigenvals[1]]
    
    # average degree
    total_degree = sum(ones_vector @ A)
    avg_degree = total_degree / num_verts
    avg_degree_decimal = float(avg_degree)
    average_degree += [avg_degree_decimal]
    
    # clique number
    clique_number += [nx.algorithms.approximation.clique.large_clique_size(G)]
    
    # density (number of edges / total possible edges = n choose 2)
    num_edges = total_degree / 2
    possible_edges = (num_verts * (num_verts - 1))/2
    dens = num_edges / possible_edges
    dens_decimal = float(dens)
    density += [dens_decimal]
    
    # diameter
    diameter += [nx.diameter(G)]
    
    # girth
    girth += [nx.girth(G)]
    
    # independence number
    max_set = nx.maximal_independent_set(G)
    ind_number = len(max_set)
    independence_number += [ind_number]
    
    # index
    # in other words: spectral radius
    sorted_A_eigenvals = sorted(A_eigenvals, reverse=True, key=lambda x: abs(x))
    index += [abs(sorted_A_eigenvals[0])]
    
    # laplacian largest eigenvalue
    sorted_L_eigenvals = sorted(L_eigenvals, reverse=True, key=lambda x: abs(x))
    laplacian_largest_eigenvalue += [sorted_L_eigenvals[0]]
    
    # matching number 
    matching = nx.maximal_matching(G)
    matching_number += [len(matching)]
    
    # maximum degree
    degrees = ones_vector @ A
    sorted_degree = degrees.copy()
    sorted_degree = np.sort(sorted_degree)
    maximum_degree += [sorted_degree[-1]]
    
    # minimum degree
    minimum_degree += [sorted_degree[0]]
    
    # number of edges
    number_of_edges += [num_edges]
    
    # number of spanning trees
    # using kirchhoff's theorem
    chopped_L1 = np.delete(L, 1, axis=0) 
    chopped_L2 = np.delete(chopped_L1, 1, axis=1)
    number_of_spanning_trees += [np.linalg.det(chopped_L2)]
    
    # number of triangles
    number_of_triangles += [len(nx.triangles(G))]
    
    # number of vertices
    number_of_vertices += [num_verts]
    
    # number of zero eigenvalues of adjacency matrix
    zero_eigenvals = sum(1 for e in A_eigenvals if e == 0)
    number_of_zero_eigenvalues += [zero_eigenvals]
    
    # radius
    radius += [nx.radius(G)]
    
    # second largest eigenvalue
    second_largest_eigenvalue += [sorted_A_eigenvals[1]]
    
    # smallest eigenvalue
    A_eigenvals.sort()
    smallest_eigenvalue += [A_eigenvals[0]]
    
    # vertex connectivity
    vertex_connectivity += [nx.node_connectivity(G)]

    # vertex cover number
    vertex_cover_number += [len(nx.algorithms.approximation.vertex_cover.min_weighted_vertex_cover(G))]

  new_data['is_simple'] = is_simple
  new_data['adjacency_matrix'] = adjacency_matrix
  new_data['edge_list'] = edge_list
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
  new_data['number_of_edges'] = number_of_edges
  new_data['number_of_spanning_trees'] = number_of_spanning_trees
  new_data['number_of_triangles'] = number_of_triangles
  new_data['number_of_vertices'] = number_of_vertices
  new_data['number_of_zero_eigenvalues'] = number_of_zero_eigenvalues
  new_data['radius'] = radius
  new_data['second_largest_eigenvalue'] = second_largest_eigenvalue
  new_data['smallest_eigenvalue'] = smallest_eigenvalue
  new_data['vertex_connectivity'] = vertex_connectivity
  new_data['vertex_cover_number'] = vertex_cover_number

  # now time for the p-vectors
  pk_vec_col = []

  for graph in new_data['adjacency_matrix']:
    A = np.array(graph)
    pvec = p_k_vector(A)
    pk_vec_col += [pvec]

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
        p_k_cols[f'number_of_{i}_gons'] += [v[i-3]]
      else: p_k_cols[f'number_of_{i}_gons'] += [0]
  
  # make a dataframe out of these
  together = merged_dict = {**new_data, **p_k_cols}
  print(together)
  new_rows = pd.DataFrame.from_dict(together)

  # what was the max k in the original dataset?
  og_max_k = len(list(df_og)) - 26 # there are 26 columns besides number_of_k_gons

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
