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

from constraint import RecursiveBacktrackingSolver


class RecursiveBacktrackingSolver(RecursiveBacktrackingSolver):
    """ A wrap to RecursiveBacktrackingSolver to support ``call_limit, time_limit, solution_limit`` """

    def __init__(self, call_limit=None, time_limit=None, solution_limit=None):

        self.call_limit = call_limit
        self.time_limit = time_limit
        self.solution_limit = solution_limit

        self.call_current = None
        self.time_start = None
        self.time_current = None
        self.solution_current = None

        super().__init__()

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

    def solutionLimitReached(self, solutions):
        """ Check if the solution_limit is reached """
        if self.solution_current is not None:
            self.solution_current = len(solutions)
            if self.solution_current >= self.solution_limit:
                return True

        return False

    def getSolution(self,
                    domains, constraints, vconstraints):
        """Wrap RecursiveBacktrackingSolver.getSolution to add the limits."""
        if self.call_limit is not None:
            self.call_current = 0
        if self.time_limit is not None:
            self.time_start = time()
        if self.solution_limit is not None:
            self.solution_current = 0
        return super().getSolution(domains, constraints, vconstraints)

    def getSolutions(self,
                     domains, constraints, vconstraints):
        """ Wrap RecursiveBacktrackingSolver.getSolutions to add the limits."""
        if self.call_limit is not None:
            self.call_current = 0
        if self.time_limit is not None:
            self.time_start = time()
        if self.solution_limit is not None:
            self.solution_current = 0
        return super().getSolutions(domains, constraints, vconstraints)

    def recursiveBacktracking(self,  # pylint: disable=invalid-name
                              solutions, domains, vconstraints, assignments, single):
        """Like ``constraint.RecursiveBacktrackingSolver.recursiveBacktracking`` but
        limited to the introduced limits """
        if (
            self.callLimitReached() or
            self.timeLimitReached() or
            self.solutionLimitReached(solutions)
        ):
            return solutions
        return super().recursiveBacktracking(solutions, domains, vconstraints, assignments, single)
