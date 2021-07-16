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

"""A pass for choosing a Layout of a circuit onto a Coupling graph,
as a subgraph isomorphism problem, solved by VF2++. It tries to find
a solution that satisfies the circuit as much as possible, i.e. only 
few further swap are needed. It is implemented such that the method 
will always find a solution. 
"""
import random
import retworkx as rx

from qiskit.transpiler.layout import Layout
from qiskit.transpiler.basepasses import AnalysisPass


class ExVF2Layout(AnalysisPass):
    """If possible, chooses a Layout as a Subgraph Isomorphism Probrem, using VF2."""

    def __init__(self, coupling_map, strict_direction=False, seed=None, id_order=False):
        """If possible, chooses a Layout as a Subgraph Isomorphism Probrem, using VF2.
        If not possible, does not set the layout property. In all the cases,
        the property `VF2Layout_stop_reason` will be added with one of the
        following values:
        * solution found: If a perfect layout was found.
        * nonexistent solution: If no perfect layout was found.
        Args:
            coupling_map (CouplingMap): Directed graph representing a coupling map.
            strict_direction (bool): If True, considers the direction of the coupling map.
                                     Default is False.
            seed (int): Sets the seed of the PRNG. -1 Means no node shuffling.
            id_order (bool or None): Forces the id_order parameter.
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.strict_direction = strict_direction
        self.seed = seed
        self.id_order = id_order 

        if self.strict_direction:
            raise ValueError("This Algorithm does not check for Direction!")

    def run(self, dag):
        """run the layout method"""
        qubits = dag.qubits
        qubit_indices = {qubit: index for index, qubit in enumerate(qubits)}
        interactions = [
            (qubit_indices[gate.qargs[0]], qubit_indices[gate.qargs[1]])
            for gate in dag.two_qubit_ops()
        ]

        cm_graph = self.coupling_map.graph.to_undirected()
        cm_nodes = cm_graph.node_indexes()
        im_graph = rx.PyGraph()
        im_graph.add_nodes_from(range(len(qubits)))
        im_graph.add_edges_from_no_data(interactions)

        opt_k = self.binsearch(cm_graph, im_graph)

        dist = rx.graph_all_pairs_dijkstra_path_lengths(cm_graph, lambda _: 1)
        cm_graph_ext, perm = self._build_distk_graph(cm_graph, dist, opt_k)
        perm = {new: old for old, new in perm.items()}

        vf2 = rx.graph_vf2_mapping(cm_graph_ext, im_graph, 
                                   subgraph=True, id_order=False, induced=False)
        mapping = {perm[k]: v for k, v in next(vf2).items()}

        stop_reason = "solution found"
        layout = Layout({qubits[im_i]: cm_nodes[cm_i] for cm_i, im_i in mapping.items()})
        self.property_set["layout"] = layout
        for reg in dag.qregs.values():
            self.property_set["layout"].add_register(reg)
        self.property_set["VF2Layout_stop_reason"] = stop_reason

    def _build_distk_graph(self, graph, dist=None, k=1):
        """ Create the extended graph:
        connect every pair of nodes at distance below or equal than k.
        """
        if dist is None:
            dist = rx.graph_all_pairs_dijkstra_path_lengths(graph, lambda _: 1)

        nodes = graph.node_indexes()
        perm = {v: i for i, v in enumerate(nodes)}

        graph_k = rx.PyGraph(multigraph=False)
        graph_k.add_nodes_from(
            list(range(len(nodes)))
        )
        for v in nodes:
            for w, dval in dist[v].items():
                if dval <= k:
                    graph_k.add_edge(perm[v], perm[w], None)
        
        return graph_k, perm

    def binsearch(self, first, second):
        """ Binary search over the "distance" threshold.
        This is equivalent to find the optimal value such that all "logical" qubits 
        that interact in the circuit are mapped to physical qubits whose distance 
        is below this value.
        """
        L = 1
        R = len(first) - 1
        
        dist = rx.graph_all_pairs_dijkstra_path_lengths(first, lambda _: 1)
        
        while L < R:
            mid = (L + R) // 2
            graph, _ = self._build_distk_graph(first, dist, mid)
            res = rx.is_subgraph_isomorphic(graph, second,
                                            id_order=False, induced=False)
            
            if not res:
                L = mid + 1
            else:
                R = mid

        return L
