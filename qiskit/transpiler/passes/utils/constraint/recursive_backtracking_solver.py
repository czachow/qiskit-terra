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

""" RecursiveBacktrackingSolver based on python-constraint package """
import random
from time import time


class RecursiveBacktrackingSolver():
    """ Recursive problem solver with backtracking capabilities
    Examples:
    >>> result = [[('a', 1), ('b', 2)],
    ...           [('a', 1), ('b', 3)],
    ...           [('a', 2), ('b', 3)]]
    >>> problem = Problem(RecursiveBacktrackingSolver())
    >>> problem.addVariables(["a", "b"], [1, 2, 3])
    >>> problem.addConstraint(lambda a, b: b > a, ["a", "b"])
    >>> solution = problem.getSolution()
    >>> sorted(solution.items()) in result
    True
    >>> for solution in problem.getSolutions():
    ...     sorted(solution.items()) in result
    True
    True
    True
    >>> problem.getSolutionIter()
    Traceback (most recent call last):
       ...
    NotImplementedError: RecursiveBacktrackingSolver doesn't provide iteration
    """

    def __init__(self, forwardcheck=True, call_limit=None, time_limit=None):
        """
        @param forwardcheck: If false forward checking will not be requested
                             to constraints while looking for solutions
                             (default is true)
        @type  forwardcheck: bool
        """
        self._forwardcheck = forwardcheck

        self.call_limit = call_limit
        self.call_current = None

        self.time_limit = time_limit
        self.time_start = None
        self.time_current = None

    def limit_reached(self):
        """Checks if a limit is reached."""
        if self.call_current is not None:
            self.call_current += 1
            if self.call_current > self.call_limit:
                return True
        if self.time_start is not None:
            self.time_current = time() - self.time_start
            if self.time_current > self.time_limit:
                return True
        return False

    def recursive_backtracking(self, solutions, domains, vconstraints, assignments, single):
        """ Run the recursive backtracking algorithm """

        # check limits
        if self.limit_reached():
            return None

        # Mix the Degree and Minimum Remaining Values (MRV) heuristics
        lst = [
            (-len(vconstraints[variable]), len(domains[variable]), variable)
            for variable in domains
        ]
        lst.sort()
        for item in lst:
            if item[-1] not in assignments:
                # Found an unassigned variable. Let's go.
                break
        else:
            # No unassigned variables. We've got a solution.
            solutions.append(assignments.copy())
            return solutions

        variable = item[-1]
        assignments[variable] = None

        forwardcheck = self._forwardcheck
        if forwardcheck:
            pushdomains = [domains[x] for x in domains if x not in assignments]
        else:
            pushdomains = None

        for value in domains[variable]:
            assignments[variable] = value
            if pushdomains:
                for domain in pushdomains:
                    domain.push_state()
            for constraint, variables in vconstraints[variable]:
                if not constraint(variables, domains, assignments, pushdomains):
                    # Value is not good.
                    break
            else:
                # Value is good. Recurse and get next variable.
                self.recursive_backtracking(
                    solutions, domains, vconstraints, assignments, single
                )
                if solutions and single:
                    return solutions
            if pushdomains:
                for domain in pushdomains:
                    domain.pop_state()
        del assignments[variable]
        return solutions

    def get_solution(self, domains, constraints, vconstraints):
        """ Get single solution """
        if self.call_limit is not None:
            self.call_current = 0
        if self.time_limit is not None:
            self.time_start = time()
        solutions = self.recursive_backtracking([], domains, vconstraints, {}, True)
        return solutions and solutions[0] or None

    def get_solutions(self, domains, constraints, vconstraints):
        """ Get all solutions """
        if self.call_limit is not None:
            self.call_current = 0
        if self.time_limit is not None:
            self.time_start = time()
        return self.recursive_backtracking([], domains, vconstraints, {}, False)
