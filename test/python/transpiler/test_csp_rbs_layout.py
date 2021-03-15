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

"""Test the CspRbsLayout pass"""

import unittest
from time import process_time
from math import pi

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.passes import CspRbsLayout
from qiskit.converters import circuit_to_dag
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeBogota


class TestCspRbsLayout(QiskitTestCase):
    """Tests the CspRbsLayout pass"""
    seed = 42

    def test_2q_circuit_5q_coupling(self):
        """ 2 linear qubits in Bogota, without noise
            solution limit set to one
            iteration limit set to one
            0 - 1 - 2 - qr1 - qr2
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[1], qr[0])  # qr1 -> qr0
        dag = circuit_to_dag(circuit)

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)

        pass_ = CspRbsLayout(coupling_map, seed=self.seed)

        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 3)
        self.assertEqual(layout[qr[1]], 2)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'solution found')

    def test_2q_circuit_5q_coupling_solution(self):
        """ 2 linear qubits in Bogota, without noise
            solution limit set to two
            iteration limit set to one
            0 - 1 - 2 - qr1 - qr2
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[1], qr[0])  # qr1 -> qr0
        dag = circuit_to_dag(circuit)

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)

        pass_ = CspRbsLayout(coupling_map,
                             seed=self.seed,
                             solution_limit=2)

        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 3)
        self.assertEqual(layout[qr[1]], 4)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'solution found')

    def test_3q_circuit_5q_coupling_iteration(self):
        """ 3 fully-connected qubits in Bogota without noise
            iteration limit set to two
            solution limit set to one
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

        pass_ = CspRbsLayout(coupling_map,
                             seed=self.seed,
                             iteration_limit=2,
                             solution_limit=1)

        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 3)
        self.assertEqual(layout[qr[1]], 1)
        self.assertEqual(layout[qr[2]], 2)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'solution found')

    def test_3q_circuit_5q_coupling_solution_iteration(self):
        """ 3 fully-connected qubits in Bogota with noise
            iteration limit set to two
            solution limit set to five
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

        pass_ = CspRbsLayout(coupling_map,
                             seed=self.seed,
                             iteration_limit=2,
                             solution_limit=5,
                             backend_prop=backend_prop)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 3)
        self.assertEqual(layout[qr[1]], 2)
        self.assertEqual(layout[qr[2]], 4)
        self.assertEqual(pass_.property_set['CSPLayout_stop_reason'], 'solution found')


if __name__ == '__main__':
    unittest.main()
