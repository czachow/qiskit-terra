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
    Problem based on python-constraint package
"""
import copy
from .domain import Domain
from .constraint import Constraint
from .function_constraint import FunctionConstraint
from .recursive_backtracking_solver import RecursiveBacktrackingSolver


class Problem():
    """
    Class used to define a problem
    """

    def __init__(self, solver=None):
        """
            Initialize the problem
        """
        self._solver = solver or RecursiveBacktrackingSolver()
        self._constraints = []
        self._variables = {}

    def reset(self):
        """
            Reset the current problem definition
            Example:
            >>> problem = Problem()
            >>> problem.addVariable("a", [1, 2])
            >>> problem.reset()
            >>> problem.getSolution()
            >>>
        """
        del self._constraints[:]
        self._variables.clear()

    def add_variable(self, variable, domain):
        """
            Add a variable to the problem
            Example:
            >>> problem = Problem()
            >>> problem.addVariable("a", [1, 2])
            >>> problem.getSolution() in ({'a': 1}, {'a': 2})
            True
            @param variable: Object representing a problem variable
            @type  variable: hashable object
            @param domain: Set of items defining the possible values that
                        the given variable may assume
            @type  domain: list, tuple, or instance of C{Domain}
        """
        if variable in self._variables:
            msg = "Tried to insert duplicated variable %s" % repr(variable)
            raise ValueError(msg)
        if isinstance(domain, Domain):
            domain = copy.deepcopy(domain)
        elif hasattr(domain, "__getitem__"):
            domain = Domain(domain)
        else:
            msg = "Domains must be instances of subclasses of the Domain class"
            raise TypeError(msg)
        if not domain:
            raise ValueError("Domain is empty")
        self._variables[variable] = domain

    def add_variables(self, variables, domain):
        """
            Add one or more variables to the problem
            Example:
            >>> problem = Problem()
            >>> problem.addVariables(["a", "b"], [1, 2, 3])
            >>> solutions = problem.getSolutions()
            >>> len(solutions)
            9
            >>> {'a': 3, 'b': 1} in solutions
            True
            @param variables: Any object containing a sequence of objects
                            represeting problem variables
            @type  variables: sequence of hashable objects
            @param domain: Set of items defining the possible values that
                        the given variables may assume
            @type  domain: list, tuple, or instance of C{Domain}
        """
        for variable in variables:
            self.add_variable(variable, domain)

    def add_constraint(self, constraint, variables=None):
        """
            Add a constraint to the problem
            Example:
            >>> problem = Problem()
            >>> problem.addVariables(["a", "b"], [1, 2, 3])
            >>> problem.addConstraint(lambda a, b: b == a+1, ["a", "b"])
            >>>
            @param constraint: Constraint to be included in the problem
            @type  constraint: instance a L{Constraint} subclass or a
                            function to be wrapped by L{FunctionConstraint}
            @param variables: Variables affected by the constraint (default to
                            all variables). Depending on the constraint type
                            the order may be important.
            @type  variables: set or sequence of variables
        """
        if not isinstance(constraint, Constraint):
            if callable(constraint):
                constraint = FunctionConstraint(constraint)
            else:
                msg = "Constraints must be instances of subclasses " "of the Constraint class"
                raise ValueError(msg)
        self._constraints.append((constraint, variables))

    def set_solver(self, solver):
        """ Change the problem solver """
        self._solver = solver

    def get_solver(self):
        """ Get the problem solver """
        return self._solver

    def get_solution(self):
        """ Find and return a solution to the problem """
        domains, constraints, vconstraints = self._get_args()
        if not domains:
            return None
        return self._solver.get_solution(domains, constraints, vconstraints)

    def get_solutions(self):
        """ Find and return all solutions to the problem """
        domains, constraints, vconstraints = self._get_args()
        if not domains:
            return []
        return self._solver.get_solutions(domains, constraints, vconstraints)

    def _get_args(self):
        """ Get all arguments of the problem """
        domains = self._variables.copy()
        allvariables = domains.keys()
        constraints = []
        for constraint, variables in self._constraints:
            if not variables:
                variables = list(allvariables)
            constraints.append((constraint, variables))
        vconstraints = {}
        for variable in domains:
            vconstraints[variable] = []
        for constraint, variables in constraints:
            for variable in variables:
                vconstraints[variable].append((constraint, variables))
        for constraint, variables in constraints[:]:
            constraint.pre_process(variables, domains, constraints, vconstraints)
        for domain in domains.values():
            domain.reset_state()
            if not domain:
                return None, None, None
        return domains, constraints, vconstraints
