def graph_features(A):
    # input: A (numpy array) - the adjacency matrix of the graph
    # output: invariants (list of invariants in the order below (alphabetical-ish))
    # 'is_simple' (boolean entry, note that we mean simple in the sense of polytopes. In graph-ese this translates to vertex degree-regular)
    # 'adjacency_matrix, 'edge_list',
    # 'algebraic_connectivity', 'average_degree', 'clique_number', 'density', 
    # 'diameter', 'girth', 'independence_number', 'index', 
    # 'laplacian_largest_eigenvalue', 'length_of_longest_path',
    # 'matching_number', 'maximum_degree', 'minimum_degree', 'number_of_edges', 
    # 'number_of_spanning_trees', 'number_of_triangles', 'number_of_vertices', 
    # 'number_of_zero_eigenvalues', 'radius', 'second_largest_eigenvalue', 
    # 'smallest_eigenvalue', 'vertex_connectivity', 'vertex_cover_number'

    invariants = []
    num_verts = len(A[0])

    edges = []
    n = len(A[0])
    for i in range(n):
      for j in range(i,n):
        if A[i][j] == 1:
          edges += [[i,j]]

    # construct networkx graph object 
    G = nx.from_numpy_array(A)
    
    invariants += [nx.is_regular(G)]
    invariants += [A]
    invariants += [edges]


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
    algebraic_connectivity = L_eigenvals[1]
    invariants += [algebraic_connectivity]
    
    # average degree
    total_degree = sum(ones_vector @ A)
    average_degree = total_degree / num_verts
    average_degree_decimal = float(average_degree)
    invariants += [average_degree_decimal]
    
    # clique number
    clique_number = nx.algorithms.approximation.clique.large_clique_size(G)
    invariants += [clique_number]
    
    # density (number of edges / total possible edges = n choose 2)
    num_edges = total_degree / 2
    possible_edges = (num_verts * (num_verts - 1))/2
    density = num_edges / possible_edges
    density_decimal = float(density)
    invariants += [density_decimal]
    
    # diameter
    diameter = nx.diameter(G)
    invariants += [diameter]
    
    # girth
    girth = nx.girth(G)
    invariants += [girth]
    
    # independence number
    max_set = nx.maximal_independent_set(G)
    independence_number = len(max_set)
    invariants += [independence_number]
    
    # index
    # in other words: spectral radius
    sorted_A_eigenvals = sorted(A_eigenvals, reverse=True, key=lambda x: abs(x))
    index = abs(sorted_A_eigenvals[0])
    invariants += [index]
    
    # laplacian largest eigenvalue
    sorted_L_eigenvals = sorted(L_eigenvals, reverse=True, key=lambda x: abs(x))
    largest_L_eigenval = abs(sorted_L_eigenvals[0])
    invariants += [largest_L_eigenval]
    
    # length of longest path
    # also np hard...
    length_longest_path = False
    invariants += [length_longest_path]
    
    # matching number 
    matching = nx.maximal_matching(G)
    matching_number = len(matching)
    invariants += [matching_number]
    
    # maximum degree
    degrees = ones_vector @ A
    sorted_degree = degrees.copy()
    sorted_degree = np.sort(sorted_degree)
    maximum_degree = sorted_degree[-1]
    invariants += [maximum_degree]
    
    # minimum degree
    minimum_degree = sorted_degree[0]
    invariants += [minimum_degree]
    
    # number of edges
    invariants += [num_edges]
    
    # number of spanning trees
    # using kirchhoff's theorem
    chopped_L1 = np.delete(L, 1, axis=0) 
    chopped_L2 = np.delete(chopped_L1, 1, axis=1)
    number_spanning_trees = np.linalg.det(chopped_L2)
    invariants += [round(number_spanning_trees)]
    
    # number of triangles
    number_triangles = len(nx.triangles(G))
    invariants += [number_triangles - 1]
    
    # number of vertices
    invariants += [num_verts]
    
    # number of zero eigenvalues of adjacency matrix
    zero_eigenvals = sum(1 for e in A_eigenvals if e == 0)
    invariants += [zero_eigenvals]
    
    # radius
    radius = nx.radius(G)
    invariants += [radius]
    
    # second largest eigenvalue
    second_largest_eigenval = sorted_A_eigenvals[1]
    invariants += [second_largest_eigenval]
    
    # smallest eigenvalue
    A_eigenvals.sort()
    smallest_eigenval = A_eigenvals[0]
    invariants += [smallest_eigenval]
    
    # vertex connectivity
    vertex_connectivity = nx.node_connectivity(G)
    invariants += [vertex_connectivity]

    # vertex cover number
    vertex_cover_number = len(nx.algorithms.approximation.vertex_cover.min_weighted_vertex_cover(G))
    invariants += [vertex_cover_number]

    return invariants
