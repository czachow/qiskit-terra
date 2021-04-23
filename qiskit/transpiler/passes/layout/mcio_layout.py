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
import random
from math import log

from qiskit.transpiler.passes.layout.layout_scorer import LayoutScorer
from qiskit.transpiler.layout import Layout
from qiskit.transpiler.basepasses import AnalysisPass


class MCIOLayout(AnalysisPass):
    """ Choose a layout by Monte Carlo Integer Optimization.
        Use a custom solution process which only swaps valid configurations.
    """

    def __init__(self, coupling_map, strict_direction=False, seed=None,
                 sampling_limit=10, iteration_limit=100, backend_properties=None):
        """
        """
        super().__init__()
        self.coupling_map = coupling_map
        self.strict_direction = strict_direction # currently not supported

        self.sampling_limit = sampling_limit
        self.iteration_limit = iteration_limit
        self.backend_properties = backend_properties

        self.seed = seed
        self.rnd_gen = random.Random(self.seed)

        self.initial_temperature = 100.0
        self.layout_scorer = LayoutScorer(self.coupling_map, self.backend_properties)

    def run(self, dag):
        num_wires = len(dag.qubits)
        assignment = self.mcio_sampler(dag)

        # solution_list is empty
        if not any(assignment):
            stop_reason = 'iteration limit reached'

        # solution_list has entries
        else:
            stop_reason = 'solution found'
            self.property_set['layout'] = Layout({v: dag.qubits[k] for k, v in assignment.items() if k < num_wires})
            self.property_set['MCIOLayout_stop_reason'] = stop_reason

    def mcio_sampler(self, dag):
        """ Sample a number of assignments and check for best one """
        best_assign = {}
        best_obj = float('inf')
        # loop over candidates
        for _ in range(self.sampling_limit):
            assignment, objective = self.mcio_iteration(dag)
            print(assignment, objective)
            # choose new best value -> improved solution
            if objective < best_obj:
                best_assign = assignment
                best_obj = objective
        return best_assign

    def mcio_iteration(self, dag):
        """ Run a mcio iteration eg run loop that creates new states """
        num_wires = len(dag.qubits)
        num_ancil = self.coupling_map.size() - num_wires
        num_qubits = self.coupling_map.size()

        # initial state
        qubit_list = list(self.coupling_map.physical_qubits).copy()
        #self.rnd_gen.shuffle(qubit_list)
        assignment = {idx: qubit_list[idx] for idx in range(num_wires + num_ancil)}
    
        # mcio iteration
        objective = float('inf')
        current_temperature = self.initial_temperature
        for _ in range(self.iteration_limit):
            
            # choose randomly new assignment
            var1 = self.rnd_gen.randint(0, num_wires - 1)
            var2 = self.rnd_gen.randint(0, num_wires + num_ancil - 1)

            tmp = assignment[var1]
            assignment[var1] = assignment[var2]
            assignment[var2] = tmp
            new_objective = self.mcio_objective(dag, assignment)

            if log(self.rnd_gen.random()) < -(new_objective - objective) / current_temperature:
                objective = new_objective
            else:
                tmp = assignment[var1]
                assignment[var1] = assignment[var2]
                assignment[var2] = tmp

            current_temperature = current_temperature - self.initial_temperature / self.iteration_limit

        return assignment, objective

    def mcio_objective(self, dag, assignment):
        num_wires = len(dag.qubits)
        layout = Layout({v: dag.qubits[k] for k, v in assignment.items() if k < num_wires})
        score = self.layout_scorer.evaluate(dag, layout)        
        return 1 - score
