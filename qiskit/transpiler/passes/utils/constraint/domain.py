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

""" Domain based on python-constraint package """


class Domain(list):
    """ Class used to control possible values for variables
    When list or tuples are used as domains, they are automatically
    converted to an instance of that class.
    """

    def __init__(self, set):
        """
        @param set: Set of values that the given variables may assume
        @type  set: set of objects comparable by equality
        """
        list.__init__(self, set)
        self._hidden = []
        self._states = []

    def reset_state(self):
        """ Reset to the original domain state, including all possible values """
        self.extend(self._hidden)
        del self._hidden[:]
        del self._states[:]

    def push_state(self):
        """ Save current domain state
        Variables hidden after that call are restored when that state
        is popped from the stack.
        """
        self._states.append(len(self))

    def pop_state(self):
        """ Restore domain state from the top of the stack
        Variables hidden since the last popped state are then available
        again.
        """
        diff = self._states.pop() - len(self)
        if diff:
            self.extend(self._hidden[-diff:])
            del self._hidden[-diff:]

    def hide_value(self, value):
        """ Hide the given value from the domain
        After that call the given value won't be seen as a possible value
        on that domain anymore. The hidden value will be restored when the
        previous saved state is popped.
        @param value: Object currently available in the domain
        """
        list.remove(self, value)
        self._hidden.append(value)
