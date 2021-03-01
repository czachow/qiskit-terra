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

"""Test the CSPLayoutAdvancedpass"""

import unittest
from time import process_time
from math import pi

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.passes import CSPLayoutAdvanced
from qiskit.converters import circuit_to_dag
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeTenerife, FakeRueschlikon, FakeTokyo, FakeBogota, FakeMelbourne


class TestCSPLayoutAdvanced(QiskitTestCase):
    """Tests the CSPLayoutAdvanced pass"""
    seed = 42

    def test_2q_circuit_5q_coupling_noise(self):
        """ 2 qubits in Bogota, with noise ie. no solution limit
            0 - 1 - 2 - qr1 - qr2
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[1], qr[0])  # qr1 -> qr0
        dag = circuit_to_dag(circuit)

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_prop = backend.properties()

        pass_ = CSPLayoutAdvanced(coupling_map,
                                  strict_direction=True,
                                  seed=self.seed,
                                  solution_limit=False,
                                  backend_prop=backend_prop)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 4)
        self.assertEqual(layout[qr[1]], 3)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'solution found')

    def test_3q_circuit_5q_coupling_iteration(self):
        """ 3 qubits in Bogota, with iteration
            0 - 1 - qr1 - qr2 - qr3
        """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[0], qr[1])  # qr0 -> qr1
        circuit.cx(qr[1], qr[2])  # qr1 -> qr2
        circuit.cx(qr[0], qr[2])  # qr0 -> qr2
        dag = circuit_to_dag(circuit)

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_prop = backend.properties()

        pass_ = CSPLayoutAdvanced(coupling_map,
                                  strict_direction=True,
                                  seed=self.seed,
                                  iteration_limit=2,
                                  solution_limit=True,
                                  backend_prop=backend_prop)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 0)
        self.assertEqual(layout[qr[1]], 1)
        self.assertEqual(layout[qr[2]], 2)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'solution found')

    def test_3q_circuit_5q_coupling_noise_iteration(self):
        """ 3 qubits in Bogota, with noise and iteration
            0 - 1 - qr1 - qr2 - qr3
        """
        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[0], qr[1])  # qr0 -> qr1
        circuit.cx(qr[1], qr[2])  # qr1 -> qr2
        circuit.cx(qr[0], qr[2])  # qr0 -> qr2
        dag = circuit_to_dag(circuit)

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_prop = backend.properties()

        pass_ = CSPLayoutAdvanced(coupling_map,
                                  strict_direction=True,
                                  seed=self.seed,
                                  iteration_limit=2,
                                  solution_limit=False,
                                  backend_prop=backend_prop)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 4)
        self.assertEqual(layout[qr[1]], 2)
        self.assertEqual(layout[qr[2]], 3)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'solution found')

    @staticmethod
    def create_hard_dag():
        """Creates a particularly hard circuit (returns its dag) for Tokyo"""
        circuit = QuantumCircuit(20)
        circuit.cx(13, 12)
        circuit.cx(6, 0)
        circuit.cx(5, 10)
        circuit.cx(10, 7)
        circuit.cx(5, 12)
        circuit.cx(2, 15)
        circuit.cx(16, 18)
        circuit.cx(6, 4)
        circuit.cx(10, 3)
        circuit.cx(11, 10)
        circuit.cx(18, 16)
        circuit.cx(5, 12)
        circuit.cx(4, 0)
        circuit.cx(18, 16)
        circuit.cx(2, 15)
        circuit.cx(7, 8)
        circuit.cx(9, 6)
        circuit.cx(16, 17)
        circuit.cx(9, 3)
        circuit.cx(14, 12)
        circuit.cx(2, 15)
        circuit.cx(1, 16)
        circuit.cx(5, 3)
        circuit.cx(8, 12)
        circuit.cx(2, 1)
        circuit.cx(5, 3)
        circuit.cx(13, 5)
        circuit.cx(12, 14)
        circuit.cx(12, 13)
        circuit.cx(6, 4)
        circuit.cx(15, 18)
        circuit.cx(15, 18)
        return circuit_to_dag(circuit)

    def test_time_limit(self):
        """Hard to solve situations hit the time limit"""
        dag = TestCSPLayoutAdvanced.create_hard_dag()
        coupling_map = CouplingMap(FakeTokyo().configuration().coupling_map)
        pass_ = CSPLayoutAdvanced(coupling_map, call_limit=None, time_limit=1)

        start = process_time()
        pass_.run(dag)
        runtime = process_time() - start

        self.assertLess(runtime, 3)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'time limit reached')

    def test_call_limit(self):
        """Hard to solve situations hit the call limit"""
        dag = TestCSPLayoutAdvanced.create_hard_dag()
        coupling_map = CouplingMap(FakeTokyo().configuration().coupling_map)
        pass_ = CSPLayoutAdvanced(coupling_map, call_limit=1, time_limit=None)

        start = process_time()
        pass_.run(dag)
        runtime = process_time() - start

        self.assertLess(runtime, 1)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'call limit reached')


if __name__ == '__main__':
    unittest.main()
