# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

""" Subgraph Isomorphism with artificial edges
A pass for choosing a Layout of a circuit onto a Coupling graph, as a Subgraph Isomorphism Problem. 
To make the two graphs isomorphic, artifical edges are introduced. As of this behaviour it always finds
a solution. But this may not be a good one. 
"""
import random
import warnings
from time import time
from networkx.generators.community import stochastic_block_model
import numpy as np
import retworkx as rx

from qiskit.transpiler.layout import Layout
from qiskit.transpiler.basepasses import AnalysisPass

from .layout_scorer import LayoutScorer


class VF2RSLayout(AnalysisPass):
    """If possible, chooses a Layout as a CSP, using backtracking."""

    def __init__(
        self, 
        coupling_map,
        call_limit=100
    ):
        """
        **Todo rework parameters**
        
        Args:
            coupling_map (Coupling): Directed graph representing a coupling map.
            strict_direction (bool): If True, considers the direction of the coupling map.
                                     Default is False.
            seed (int): Sets the seed of the PRNG.
            call_limit (int): Amount of times that
                ``constraint.RecursiveBacktrackingSolver.recursiveBacktracking`` will be called.
                None means no call limit. Default: 1000.
            time_limit (int): Amount of seconds that the pass will try to find a solution.
                None means no time limit. Default: 10 seconds.
            solution_limit (int): Limit the number of solutions, which should be obtained 
                by the solver. Default: 1.
            backend_properties (BackendProperties): The properties of the backend, needed if 
                solution_limit is greater one and a solution needs to be picked from the bunch. 
                Default: None.
        Raises:
            Warning: "Can only check multiple solutions when backend properties are given. \
                      Defaulting to limiting solutions!"
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.call_limit = call_limit
        
    def run(self, dag):
        """run the layout method"""
        ig = self.dag_to_ig(dag)
        cg = self.cm_to_cg(self.coupling_map)

        mapping = rx.graph_vf2_mapping(cg, ig, subgraph=True, id_order=False, induced=False)
        if not mapping:
            mapping = self.binsearch_edges(ig, cg)

        if mapping:
            stop_reason = "solution found"
            layout = Layout({dag.qubits[im_i]: cg.node_indexes()[cm_i] for cm_i, im_i in mapping.items()})
            self.property_set["layout"] = layout
            for reg in dag.qregs.values():
                self.property_set["layout"].add_register(reg)
        else:
            stop_reason = "nonexistent solution"

        self.property_set["VF2Layout_stop_reason"] = stop_reason

    def binsearch_edges(self, ig, cg):
        num_nodes = cg.num_nodes()
        num_logi_edges = ig.num_edges()
        num_real_edges = cg.num_edges()
        num_virt_edges = (num_nodes * (num_nodes - 1)) // 2 - num_real_edges

        dm = self.distmatrix_from_graph(cg)
        edge_list = [(row, col, dm[row][col]) for row in range(num_nodes) for col in range(row+1, num_nodes)]
        edge_weights = [weight for _, _, weight in edge_list]
        edge_weights_idx = np.argsort(edge_weights)[::-1]
        edge_weights_level = [idx for idx in range(num_real_edges + num_virt_edges) \
                              if edge_weights[edge_weights_idx[idx]] != edge_weights[edge_weights_idx[idx - 1]]]
        
        # calculate total mapping
        cg_t = rx.PyGraph()
        cg_t.add_nodes_from(cg.nodes())
        cg_t.add_edges_from(edge_list)
        
        level_idx = 0
        
        for c in range(self.call_limit):
            map_t = rx.graph_vf2_mapping(cg_t, ig, subgraph=True, id_order=False, induced=False)

            if map_t:
                mapping = map_t

                for idx in range(edge_weights_level[level_idx], edge_weights_level[level_idx+1]):
                    e1, e2, w = edge_list[edge_weights_idx[idx]]
                    cg_t.remove_edge(e1, e2)
                level_idx += 1
            else:
                break
        
        return mapping

    def distmatrix_from_graph(self, graph):
        dist_dict = rx.all_pairs_dijkstra_shortest_paths(graph, lambda x: x)
        N = len(graph.nodes())
        matrix = [[0] * N for i in range(N)]
        for n1, n1_vals in dist_dict.items():
            for n2, n2_vals in n1_vals.items():
                    if n2 > n1:
                        matrix[n1][n2] = len(n2_vals) - 1
                        matrix[n2][n1] = matrix[n1][n2]
        return matrix
    
    def graph_from_matrix(self, matrix):
        graph = rx.PyGraph()
        N = len(matrix)
        # nodes
        for row in range(N):
            graph.add_node(row)
        # edges
        for row in range(N):
            for col in range(row, N):
                if matrix[row][col] != 0 and not graph.has_edge(row, col):
                    graph.add_edge(row, col, matrix[row][col])
        return graph

    def dag_to_ig(self, dag):
        """ Creates a interaction graph (ig) from the dag 
            Input:
                dag (PyDiGraph): The dag
            Returns:
                im (PyDiGraph): The interaction map
        """
        ig = rx.PyGraph()
        
        for qb in dag.qubits:
            ig.add_node(qb)

        # two qubit gates as edges
        for gate in dag.two_qubit_ops():
            qb1, qb2 = sorted([dag.qubits.index(gate.qargs[0]),
                               dag.qubits.index(gate.qargs[1])])
            
            if ig.has_edge(qb1, qb2):
                ig.update_edge(qb1, qb2, ig.get_edge_data(qb1, qb2) + 1)
            else:
                ig.add_edge(qb1, qb2, 1)

        return ig

    def cm_to_cg(self, cm):
        cg = rx.PyGraph()

        cg.add_nodes_from(cm.graph.nodes())

        for edge in cm.get_edges():
            qb1, qb2 = sorted(edge)
            if not cg.has_edge(qb1, qb2):
                cg.add_edge(qb1, qb2, 1)
        
        return cg