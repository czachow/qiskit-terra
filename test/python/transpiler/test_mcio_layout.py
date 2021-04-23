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
from qiskit.transpiler.passes.layout import MCIOLayout
from qiskit.converters import circuit_to_dag
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeBogota, FakeManhattan


class TestMCIOLayout(QiskitTestCase):
    """Tests the CSPLayout pass"""
    seed = 42

    def test_3q_circuit_5q_coupling(self):

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_props = backend.properties()

        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[1], qr[0])  # qr1 -> qr0
        circuit.cx(qr[0], qr[2])  # qr0 -> qr2
        circuit.cx(qr[1], qr[2])  # qr1 -> qr2
        circuit.cx(qr[0], qr[1])  # qr0 -> qr1

        dag = circuit_to_dag(circuit)
        pass_ = MCIOLayout(coupling_map, strict_direction=False, seed=self.seed, backend_properties=backend_props)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 3)
        self.assertEqual(layout[qr[1]], 2)
        self.assertEqual(layout[qr[2]], 4)
        self.assertEqual(pass_.property_set['MCIOLayout_stop_reason'], 'solution found')

    def test_3q_circuit_5q_coupling_advanced(self):

        backend = FakeBogota()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_props = backend.properties()

        matrix = [[0, 1, 0, 0, 1],
                  [1, 0, 1, 1, 0], 
                  [0, 1, 0, 1, 0],
                  [0, 1, 1, 0, 1],
                  [1, 0, 0, 1, 0]]

        circuit = GraphState(matrix)
        dag = circuit_to_dag(circuit)

        pass_ = MCIOLayout(coupling_map, strict_direction=False, seed=self.seed, backend_properties=backend_props)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[circuit.qubits[0]], 2)
        self.assertEqual(layout[circuit.qubits[1]], 4)
        self.assertEqual(layout[circuit.qubits[2]], 3)
        self.assertEqual(layout[circuit.qubits[3]], 1)
        self.assertEqual(layout[circuit.qubits[4]], 0)
        self.assertEqual(pass_.property_set['MCIOLayout_stop_reason'], 'solution found')

    def test_12q_circuit_65q_coupling(self):

        backend = FakeManhattan()
        coupling_map = CouplingMap(backend.configuration().coupling_map)
        backend_props = backend.properties()

        matrix = np.diag([1]*11, +1) + np.diag([1] * 11, -1)
        matrix[0, 11] = 1
        matrix[11, 0] = 1

        circuit = GraphState(matrix)
        dag = circuit_to_dag(circuit)

        pass_ = MCIOLayout(coupling_map, iteration_limit=1000, strict_direction=False, seed=self.seed, backend_properties=backend_props)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        print(layout)
        self.assertEqual(pass_.property_set['MCIOLayout_stop_reason'], 'solution found')

if __name__ == '__main__':
    unittest.main()