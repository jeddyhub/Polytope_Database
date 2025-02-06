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
