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

"""Test the CSPLayout pass"""

import unittest
import numpy as np
from time import process_time

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit.library import GraphState
from qiskit.transpiler import CouplingMap, Layout
from qiskit.transpiler.passes.layout import CSPWCRLayout
from qiskit.converters import circuit_to_dag
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeBogota, FakeManhattan


class TestCSPWCRLayout(QiskitTestCase):
    """Tests the CSPWCRLayout pass"""
    seed = 42

    # def test_3q_circuit_5q_coupling(self):

    #     backend = FakeBogota()
    #     coupling_map = CouplingMap(backend.configuration().coupling_map)
    #     backend_props = backend.properties()

    #     qr = QuantumRegister(3, 'qr')
    #     circuit = QuantumCircuit(qr)
    #     circuit.cx(qr[0], qr[1])  # qr1 -> qr0
    #     circuit.cx(qr[1], qr[2])  # qr0 -> qr2

    #     dag = circuit_to_dag(circuit)
    #     pass_ = CSPWCRLayout(coupling_map, strict_direction=False, seed=self.seed)
    #     pass_.run(dag)
    #     layout = pass_.property_set['layout']

    #     self.assertEqual(layout[qr[0]], 3)
    #     self.assertEqual(layout[qr[1]], 2)
    #     self.assertEqual(layout[qr[2]], 4)
    #     self.assertEqual(pass_.property_set['CSPWCRLayout_stop_reason'], 'solution found')

    def test_3q_circuit_5q_coupling_advanced(self):

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_props = backend.properties()

        matrix = [[0, 1, 0, 0, 1],
                  [1, 0, 1, 0, 0],
                  [0, 1, 0, 1, 0],
                  [0, 0, 1, 0, 1],
                  [1, 0, 0, 1, 0]]

        circuit = GraphState(matrix)
        dag = circuit_to_dag(circuit)

        pass_ = CSPWCRLayout(coupling_map, strict_direction=False, seed=self.seed, relaxation_limit=2)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[circuit.qubits[0]], 0)
        self.assertEqual(layout[circuit.qubits[1]], 4)
        self.assertEqual(layout[circuit.qubits[2]], 3)
        self.assertEqual(layout[circuit.qubits[3]], 2)
        self.assertEqual(layout[circuit.qubits[4]], 1)
        self.assertEqual(pass_.property_set['CSPWCRLayout_stop_reason'], 'solution found')

    def test_12q_circuit_65q_coupling(self):

        backend = FakeManhattan()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_props = backend.properties()

        matrix = np.diag([1]*11, +1) + np.diag([1] * 11, -1)
        matrix[0, 11] = 1
        matrix[11, 0] = 1

        circuit = GraphState(matrix)
        dag = circuit_to_dag(circuit)

        pass_ = CSPWCRLayout(coupling_map, strict_direction=False, seed=self.seed, relaxation_limit=1)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[circuit.qubits[0]], 44)
        self.assertEqual(layout[circuit.qubits[1]], 45)
        self.assertEqual(layout[circuit.qubits[2]], 46)
        self.assertEqual(layout[circuit.qubits[3]], 47)
        self.assertEqual(layout[circuit.qubits[4]], 53)
        self.assertEqual(layout[circuit.qubits[5]], 60)
        self.assertEqual(layout[circuit.qubits[6]], 59)
        self.assertEqual(layout[circuit.qubits[7]], 58)
        self.assertEqual(layout[circuit.qubits[8]], 57)
        self.assertEqual(layout[circuit.qubits[9]], 56)
        self.assertEqual(layout[circuit.qubits[10]], 52)
        self.assertEqual(layout[circuit.qubits[11]], 43)
        self.assertEqual(pass_.property_set['CSPWCRLayout_stop_reason'], 'solution found')

    def test_12q_circuit_65q_coupling_full(self):

        backend = FakeManhattan()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_props = backend.properties()

        matrix = np.ones((12, 12))

        circuit = GraphState(matrix)
        dag = circuit_to_dag(circuit)

        pass_ = CSPWCRLayout(coupling_map, strict_direction=False, seed=self.seed, relaxation_limit=66)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[circuit.qubits[0]], 35)
        self.assertEqual(layout[circuit.qubits[1]], 34)
        self.assertEqual(layout[circuit.qubits[2]], 21)
        self.assertEqual(layout[circuit.qubits[3]], 42)
        self.assertEqual(layout[circuit.qubits[4]], 23)
        self.assertEqual(layout[circuit.qubits[5]], 41)
        self.assertEqual(layout[circuit.qubits[6]], 22)
        self.assertEqual(layout[circuit.qubits[7]], 24)
        self.assertEqual(layout[circuit.qubits[8]], 33)
        self.assertEqual(layout[circuit.qubits[9]], 37)
        self.assertEqual(layout[circuit.qubits[10]], 36)
        self.assertEqual(layout[circuit.qubits[11]], 32)
        self.assertEqual(pass_.property_set['CSPWCRLayout_stop_reason'], 'solution found')

if __name__ == '__main__':
    unittest.main()