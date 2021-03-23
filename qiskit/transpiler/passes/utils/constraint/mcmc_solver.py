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

""" Monte Carlo Markow Chain Solver based on 'A Markov Chain Monte Carlo Sampler
for Mixed Boolean/Integer Constraints' by N. Kitchen and A. Kuehlmann """

import random
import numpy as np

from .solver import Solver


class MonteCarloMarkowChainSolver(Solver):
    """ A MCMC Solver for mixed integer problems """

    def __init__(self, seed, sampling_limit=None, iteration_limit=None, constraint_to_objective_callback=None):
        """
        """
        self.seed = seed
        self.sampling_limit = sampling_limit or 10
        self.iteration_limit = iteration_limit or 1000
        self.decision_probability = 0.5
        self.initial_temp = 100.0

        self.constraint_to_objective_callback = constraint_to_objective_callback or \
                                             self.default_constraint_to_objective_callback

        self.rnd_gen = random.Random(self.seed)

        super().__init__()

    def getSolution(self,
                    domains, constraints, vconstraints):
        """
        """
        solution = self.mcmc_sampler(domains, constraints, vconstraints)
        return solution 

    def mcmc_sampler(self,  # pylint: disable=invalid-name
                     domains, constraints, vconstraints):
        """ Run the central MCMC Sampler """
        best_assign = {}
        best_obj = float('inf')
        # loop over candidates
        for _ in range(self.sampling_limit):
            assignment, objective = self.mcmc_iteration(domains, constraints, vconstraints)
            # choose new best value -> improved solution
            if objective < best_obj:
                best_assign = assignment
                best_obj = objective
            # break if all constraint satisfied -> true solution
            if np.isclose(best_obj, 0.0):
                break
        return best_assign

    def mcmc_iteration(self, domains, constraints, vconstraints):
        """
        """
        variables = list(domains.keys())
        assignment = {}
        current_temp = self.initial_temp
        # initialize randomly
        for var in variables:
            assignment[var] = self.rnd_gen.choice(domains[var])
        for _ in range(self.iteration_limit):
            if self.rnd_gen.random() < self.decision_probability:
                assignment = self.metropolis_move(domains, constraints, assignment, current_temp)
            else:
                assignment = self.local_move(domains, constraints, assignment)
            objective = self.calculate_objective(domains, constraints, assignment)
            if np.isclose(objective, 0.0):
                break
            current_temp = current_temp - self.initial_temp / self.iteration_limit
        return assignment, objective

    def metropolis_move(self, domains, constraints, assignment, temperature):
        """
        """
        variables = list(domains.keys())
        var = self.rnd_gen.choice(variables)
        new_assignment = assignment.copy()
        new_assignment[var] = self.rnd_gen.choice(domains[var])

        old_obj = self.calculate_objective(domains, constraints, assignment)
        new_obj = self.calculate_objective(domains, constraints, new_assignment)

        if np.log(self.rnd_gen.random()) < -(new_obj - old_obj) / temperature:
            return new_assignment
        else:
            return assignment

    def local_move(self, domains, constraints, assignment):
        """
        """
        broken_constraints = self.get_broken_constraints(domains, constraints, assignment)
        if broken_constraints:
            (_, chosen_variables) = self.rnd_gen.choice(broken_constraints)
            objective = float('inf')
            for var in chosen_variables:
                new_assignment = assignment.copy()
                new_assignment[var] = self.rnd_gen.choice(domains[var])
                new_objective = self.calculate_objective(domains, constraints, assignment)
                if new_objective < objective:
                    assignment = new_assignment
                    objective = new_objective
        return assignment

    def get_broken_constraints(self, domains, constraints, assignment):
        """
        """
        broken_constraints = [(None, None)] * len(constraints)
        for idx, (constraint, variables) in enumerate(constraints):
            if not constraint(variables, domains, assignment):
                broken_constraints[idx] = (constraint, variables)
        return list(filter(lambda sub: not all(ele == None for ele in sub), broken_constraints))
        
    def calculate_objective(self, domains, constraints, assignment):
        """
            Maybe find more efficient way
        """
        objective = 0
        for constraint, variables in constraints:
            objective += self.constraint_to_objective_callback(domains, constraint, variables, assignment)
        return objective

    def default_constraint_to_objective_callback(self, domains, constraint, variables, assignment):
        """ Default Function for setting an objective by a constraint """
        return 1.0 * int(not constraint(variables, domains, assignment))
