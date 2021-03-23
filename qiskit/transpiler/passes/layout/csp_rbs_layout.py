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

"""A pass for choosing a Layout of a circuit onto a Coupling graph, as a
Constraint Satisfaction Problem. It tries to find a solution that fully
satisfy the circuit, i.e. no further swap is needed. If no solution is
found, no ``property_set['layout']`` is set.
"""
import warnings
import numpy as np
from itertools import chain
from copy import deepcopy
from random import Random

from qiskit.transpiler.passes.utils.constraint import Problem, AllDifferentConstraint, RecursiveBacktrackingSolver
from qiskit.transpiler.layout import Layout
from qiskit.transpiler.basepasses import AnalysisPass
from .layout_scorer import LayoutScorer


class CspRbsLayout(AnalysisPass):
    """If possible, chooses a Layout as a CSP, using backtracking."""

    def __init__(self, coupling_map, strict_direction=False, seed=None, call_limit=1000,
                 time_limit=10, solution_limit=1, backend_prop=None):
        """If possible, chooses a Layout as a CSP, using backtracking.
        If not possible, does not set the layout property. In all the cases,
        the property `CSPLayout_stop_reason` will be added with one of the
        following values:
        * solution found: If a perfect layout was found.
        * call limit reached: If no perfect layout was found and the call limit was reached.
        * time limit reached: If no perfect layout was found and the time limit was reached.
        * iteration limit reached: If no perfect layout was found and the iteration limit was reached.

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
            iteration_limit (int): Amount of iterations to do with introduction of virtual edges
            solution_limit (int): Limit the number of solution to the given number. Default: 10.
            backend_prop (BackendProp): The properties of the backend, needed if solution_limit
                or iteration_limit exist and a solution needs to be picked from the bunch. 
                Default: None.
        Raises:
            Warning: "Can only check multiple solutions when backend properties are given. \
                      Defaulting to limiting solutions!"
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.strict_direction = strict_direction

        self.call_limit = call_limit
        self.time_limit = time_limit
        self.solution_limit = solution_limit

        self.backend_prop = backend_prop
        self.seed = seed
        
        self.iteration_limit = self._calc_iteration_limit()

        # init scorer and solver
        self.layout_scorer = LayoutScorer(self.coupling_map,
                                          backend_prop=self.backend_prop)
        self.csp_solver = RecursiveBacktrackingSolver(call_limit=self.call_limit,
                                                      time_limit=self.time_limit,
                                                      solution_limit=self.solution_limit)

    def run(self, dag):
        # copy required as map will be manipulated
        coupling_map = deepcopy(self.coupling_map)
        logical_qubits = dag.qubits

        # iterate of different level
        for it_level in range(self.iteration_limit):
            if it_level > 0:
                coupling_map = self._extend_coupling_map(coupling_map)
            problem = self._get_csp_problem(dag, coupling_map)

            solution_list = problem.getSolutions()

            # solution_list is empty
            if not any(solution_list):
                stop_reason = 'iteration limit reached'
                if (
                    self.csp_solver.time_current is not None and
                    self.csp_solver.time_current >= self.time_limit
                ):
                    stop_reason = 'time limit reached'
                elif (
                    self.csp_solver.call_current is not None and
                    self.csp_solver.call_current >= self.call_limit
                ):
                    stop_reason = 'call limit reached'

            # solution_list has entries
            else:
                stop_reason = 'solution found'
                if self.solution_limit == 1:
                    solution = solution_list[0]
                else:
                    sol_layouts = [Layout({v: logical_qubits[k] for k, v in solution.items()})
                                                                for solution in solution_list]
                    layout_fidelities = [self.layout_scorer.evaluate(dag, layout) for layout in sol_layouts]
                    max_fid_idx = np.argsort(layout_fidelities)[-1]
                    solution = solution_list[max_fid_idx]

                self.property_set['layout'] = Layout({v: logical_qubits[k] for k, v in solution.items()})
                self.property_set['CSPLayout_stop_reason'] = stop_reason
                break

    def _get_csp_problem(self, dag, coupling_map):
        """ Create a CSP Problem """
        logical_edges = self._get_logical_edges(dag)
        physical_edges = set(coupling_map.get_edges())

        problem = Problem(self.csp_solver)

        variables = list(range(len(dag.qubits)))
        variable_domains = list(self.coupling_map.physical_qubits).copy()
        Random(self.seed).shuffle(variable_domains)

        problem.addVariables(variables, variable_domains)
        problem.addConstraint(AllDifferentConstraint())  # each wire is map to a single qbit

        if self.strict_direction:
            def constraint(control, target):
                return (control, target) in physical_edges
        else:
            def constraint(control, target):
                return (control, target) in physical_edges or (target, control) in physical_edges

        for edge in logical_edges:
            problem.addConstraint(constraint, [edge[0], edge[1]])

        return problem

    def _extend_coupling_map(self, coupling_map):
        """
        Extend the coupling_map
        By each iteration extend the map by new edges in distance 1
        """
        qubits = coupling_map.physical_qubits

        new_cpls = set()

        for q1 in qubits:
            q1_nextneighbors = chain(*[list(coupling_map.neighbors(q)) for q in coupling_map.neighbors(q1)])
            for q2 in q1_nextneighbors:
                if coupling_map.distance(q1, q2) == 2:
                    new_cpls.add((q1, q2))

        for q1, q2 in new_cpls:
            coupling_map.add_edge(q1, q2)
            coupling_map.add_edge(q2, q1)

        return coupling_map

    def _get_logical_edges(self, dag):
        """Extract the logical edges from the CNOT interactions"""
        logical_edges = set()
        for gate in dag.two_qubit_ops():
            logical_edges.add((dag.qubits.index(gate.qargs[0]),
                               dag.qubits.index(gate.qargs[1])))
        return logical_edges

    def _calc_iteration_limit(self):
        """ Calculate the iteration limit """
        # calculate graph degrees
        graph_degree = [0] * self.coupling_map.size()
        for idx, node in enumerate(self.coupling_map.graph.node_indexes()):
            graph_degree[idx] = min(self.coupling_map.graph.in_degree(node), 
                                    self.coupling_map.graph.out_degree(node))
        
        return self.coupling_map.size() - 1 - min(graph_degree)
