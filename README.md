# Polytope-Curvature
Hello! Here we store code and generated data from our Summer 2024 project.

# File Descriptions
## Data
### final_data_1.csv
This data includes the House of Graph data found in HoG_data.csv, described below (2,407 rows). It also includes graphs of randomly generated 3D polytopes. We compute the effective resistance curvature (Steinerberger) and Forman Ricci curvature of these polytopes. We also store the number of n-gons of the corresponding polytope, up to n=12. 
### HoG_data.csv
This is data originating from the online graph database House of Graphs. We took 3-connected, planar graphs (graphs of 3D polytopes, by a theorem of Steinitz) and computed their discrete curvatures. We used effective resistance curvature (Steinerberger) and Forman Ricci curvature of a combinatorial polytope whose 1-skeleton is isomorphic to the given graph (found via a planar embedding). We also store the number of n-gons of the corresponding polytope, up to n=7. 
## Code
### forman-curv-from-planar-graph
Code in python, used in the situation where there we have the adjacency matrix of a planar, 3-connected graph (i.e. the graph of a 3D polytope) and we wish to know the forman ricci curvature of the edges of this polytope.
### forman-curvature-sage
### Resistance-Curvatures

