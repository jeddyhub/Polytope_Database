# Polytope-Curvature
Hello! Here we store code and generated data from our Summer 2024 project.

# File Descriptions
## Data
### final_data_k.csv
This data includes the House of Graph data found in HoG_data.csv, described below (2,407 rows). It also includes graphs of randomly generated 3D polytopes. We compute the effective resistance curvature (Steinerberger) and Forman Ricci curvature of these polytopes. We also store the number of n-gons of the corresponding polytope, up to n=12. 
### HoG_data.csv
This is data originating from the online graph database House of Graphs. We took 3-connected, planar graphs (graphs of 3D polytopes, by a theorem of Steinitz) and computed their discrete curvatures. We used effective resistance curvature (Steinerberger) and Forman Ricci curvature of a combinatorial polytope whose 1-skeleton is isomorphic to the given graph (found via a planar embedding). We also store the number of n-gons of the corresponding polytope, up to n=7. 
### new_unique_graphs.csv
## Code
### forman-curv-from-planar-graph
Code in python, used in the situation where there we have the adjacency matrix of a planar, 3-connected graph (i.e. the graph of a 3D polytope) and we wish to know the forman ricci curvature of the edges of this polytope.
### forman-curvature-sage
Code in SageMath, utilizing the Polytope object, to compute its Forman Ricci curvature. Can be a polytope of any dimension! Also has code to compute the polytope diameter bound presented in Forman's original paper. 
### Resistance-Curvatures
Compute effective resistance curvature (steinerberger), node resistance curvature, and link resistance curvature of a given graph. Also draw that graph with its vertices labeled with their curvatures.
### NewPyramidMatrices.ipynb
Notebook containing a pyramiding operation. Given the graph of a 3-polytope, alters the graph to simulate the following polyhedral operation: takes a facet of the polytope and adds a vertex beyond the facet (see Ziegler - Lectures on Polytopes). 
### vertex_chop_operation.py
Given a graph of a polytope, alters the graph to simulate the following polyhedral operation: performs a shallow chop of a vertex of the polytope. 
### y_delta_operation.py
Given a graph of a polytope, alters the graph to simulate the following polyhedral operation: a Y-Delta operation is performed to a degree 3 vertex.
### saliencyanalysis_13307 (1).py
Neural network modeling binary classification on our original (unclean) dataset. Feature analysis on the model. 
