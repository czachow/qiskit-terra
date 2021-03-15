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

""" LeastConflictSolver based on python-constraint package """

import random
from constraint import Solver


class LeastConflictsSolver(Solver):

    """
    Problem solver based on the minimum conflicts theory.
    With this solver - you will always get an assignment -
    the one with the minimum conflicts that the algorithm found.
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

    def __init__(self, call_limit=None, time_limit=None, seed=None):
        """
        BLA
        """
        self.call_limit = call_limit
        self.time_limit = time_limit

        self.call_current = None
        self.time_start = None
        self.time_current = None

        self.seed = seed
        random.seed(self.seed)

    def callLimitReached(self):
        """ Check if the call_limit is reached """
        if self.call_current is not None:
            self.call_current += 1
            if self.call_current > self.call_limit:
                return True

        return False

    def timeLimitReached(self):
        """ Check if the time_limit is reached """
        if self.time_start is not None:
            self.time_current = time() - self.time_start
            if self.time_current > self.time_limit:
                return True

        return False

    def getSolution(self,
                    domains, constraints, vconstraints):
        if self.if self.call_limit is not None:
            self.call_current = 0
        if self.time_limit is not None:
            self.time_start = time()
        solutions = self.leastConflictFinder([], domains, vconstraints, {})
        return solutions and solutions[0] or None

    def leastConflictFinder(self,
                            solutions, domains, vconstraints, assignments):
        """
        """
        if (
            self.callLimitReached() or
            self.timeLimitReached() or
        ):
            return solutions

        best_conflicted = float('inf')
        # Initial assignment
        for variable in domains:
            if variable not in assignments.keys():
                assignments[variable] = random.choice(domains[variable])

        for _ in range(self.steps):
            conflicted = 0
            lst = list(domains.keys())
            random.shuffle(lst)
            conflicted_var = None
            for variable in lst:
                # Check if variable is not in conflict
                for constraint, variables in vconstraints[variable]:
                    if not constraint(variables, domains, assignments):
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
            assignments[conflicted_var] = random.choice(minvalues)
        return best_assign

    

