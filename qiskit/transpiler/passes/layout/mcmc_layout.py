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

"""
"""
from random import Random

from qiskit.transpiler.passes.utils.constraint import Problem, AllDifferentConstraint, \
                                                      MonteCarloMarkowChainSolver
from qiskit.transpiler.layout import Layout
from qiskit.transpiler.basepasses import AnalysisPass


class MCMCLayout(AnalysisPass):
    """If possible, chooses a Layout as a CSP, using backtracking."""

    def __init__(self, coupling_map, strict_direction=False, seed=None,
                 sampling_limit=None, iteration_limit=None):
        """
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.strict_direction = strict_direction

        self.sampling_limit = sampling_limit
        self.iteration_limit = iteration_limit

        self.seed = seed

        # init scorer and solver
        self.csp_solver = MonteCarloMarkowChainSolver(self.seed,
                                                      self.sampling_limit,
                                                      self.iteration_limit,
                                                      self._constraint_to_objective_callback)

    def run(self, dag):
        # copy required as map will be manipulated
        logical_qubits = dag.qubits

        problem = self._get_csp_problem(dag, self.coupling_map)

        solution = problem.getSolution()

        # solution_list is empty
        if not any(solution):
            stop_reason = 'iteration limit reached'

        # solution_list has entries
        else:
            stop_reason = 'solution found'
            self.property_set['layout'] = Layout({v: logical_qubits[k] for k, v in solution.items()})
            self.property_set['MCMCLayout_stop_reason'] = stop_reason

    def _constraint_to_objective_callback(self, domains, constraint, variables, assignment):
        """
        """
        # check type of constraint
        if isinstance(constraint, AllDifferentConstraint):
            factor = 100.0
        else:
            factor = 1.0
        # check constraint
        return factor * int(not constraint(variables, domains, assignment))

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

    def _get_logical_edges(self, dag):
        """Extract the logical edges from the CNOT interactions"""
        logical_edges = set()
        for gate in dag.two_qubit_ops():
            logical_edges.add((dag.qubits.index(gate.qargs[0]),
                               dag.qubits.index(gate.qargs[1])))
        return logical_edges
