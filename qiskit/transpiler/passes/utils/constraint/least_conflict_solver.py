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


import random
from .solver import Solver


class LeastConflictsSolver(Solver):
    """
    Problem solver based on the minimum conflicts theory.
    With this solver - you will always get an assignment -
    the one with the minimum coflicts that the algorithm found.
    Examples:
    >>> result = [[('a', 1), ('b', 2), ('c', 1)],
    ...           [('a', 2), ('b', 1), ('c', 1)]]
    >>> problem = Problem(LeastConflictsSolver())
    >>> problem.addVariables(["a", "b"], [1, 2])
    >>> problem.addVariable("c", [1])
    >>> problem.addConstraint(lambda a, b: b != a, ["a", "b"])
    >>> problem.addConstraint(lambda a, b: b != a, ["a", "c"])
    >>> problem.addConstraint(lambda a, b: b != a, ["b", "c"])
    >>> solution = problem.getSolution()
    >>> sorted(solution.items()) in result
    True
    >>> problem.getSolutions()
    Traceback (most recent call last):
       ...
    NotImplementedError: LeastConflictsSolver provides only a single solution
    >>> problem.getSolutionIter()
    Traceback (most recent call last):
       ...
    NotImplementedError: LeastConflictsSolver doesn't provide iteration
    """

    def __init__(self, steps=1000, seed=None):
        """
        @param steps: Maximum number of steps to perform before giving up
                      when looking for a solution (default is 1000)
        @type  steps: int
        """
        self._steps = steps
        self._seed = seed

    def getSolution(self, domains, constraints, vconstraints):
        assignments = {}
        best_assign = {}
        best_conflicted = float('inf')
        rd_gen = random.Random(self._seed)
        # Initial assignment
        for variable in domains:
            assignments[variable] = rd_gen.choice(domains[variable])
        for _ in range(self._steps):
            conflicted = 0
            lst = list(domains.keys())
            rd_gen.shuffle(lst)
            conflicted_var = None
            for variable in lst:
                # Check if variable is not in conflict
                for constraint, variables in vconstraints[variable]:
                    if not constraint(variables, domains, assignments):
                        if constraint.hard:
                            conflicted = float('inf')
                        else:
                            conflicted += 1
                # Variable has conflicts. Save it:
                if conflicted > 0 and conflicted_var is None:
                    conflicted_var = variable
            if conflicted == 0:
                return assignments
            if best_conflicted > conflicted:
                best_assign = assignments
                best_conflicted = conflicted
            # Find values with less conflicts.
            mincount = len(vconstraints[conflicted_var])
            minvalues = []
            for value in domains[conflicted_var]:
                assignments[conflicted_var] = value
                count = 0
                for constraint, variables in vconstraints[conflicted_var]:
                    if not constraint(variables, domains, assignments):
                        count += 1
                if count == mincount:
                    minvalues.append(value)
                elif count < mincount:
                    mincount = count
                    del minvalues[:]
                    minvalues.append(value)
            # Pick a random one from these values.
            assignments[conflicted_var] = rd_gen.choice(minvalues)
        return best_assign