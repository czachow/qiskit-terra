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
from time import process_time

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.passes.layout import MCMCLayout
from qiskit.converters import circuit_to_dag
from qiskit.test import QiskitTestCase
from qiskit.test.mock import FakeTenerife, FakeRueschlikon, FakeTokyo, FakeBogota


class TestMCMCLayout(QiskitTestCase):
    """Tests the CSPLayout pass"""
    seed = 42

    def test_2q_circuit_2q_coupling(self):
        """ A simple example, without considering the direction
          0 - 1
        qr1 - qr0
        """
        qr = QuantumRegister(2, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[1], qr[0])  # qr1 -> qr0

        dag = circuit_to_dag(circuit)
        pass_ = MCMCLayout(CouplingMap([[0, 1]]), strict_direction=False, seed=self.seed)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 0)
        self.assertEqual(layout[qr[1]], 1)
        self.assertEqual(pass_.property_set['MCMCLayout_stop_reason'], 'solution found')

    def test_3q_circuit_5q_coupling(self):
        """ 3 qubits in Tenerife, without considering the direction
            qr1
           /  |
        qr0 - qr2 - 3
              |   /
               4
        """
        cmap5 = FakeTenerife().configuration().coupling_map

        qr = QuantumRegister(3, 'qr')
        circuit = QuantumCircuit(qr)
        circuit.cx(qr[1], qr[0])  # qr1 -> qr0
        circuit.cx(qr[0], qr[2])  # qr0 -> qr2
        circuit.cx(qr[1], qr[2])  # qr1 -> qr2

        dag = circuit_to_dag(circuit)
        pass_ = MCMCLayout(CouplingMap(cmap5), strict_direction=False, seed=self.seed)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 2)
        self.assertEqual(layout[qr[1]], 1)
        self.assertEqual(layout[qr[2]], 0)
        self.assertEqual(pass_.property_set['MCMCLayout_stop_reason'], 'solution found')

    def test_9q_circuit_16q_coupling(self):
        """ 9 qubits in Rueschlikon, without considering the direction
        q0[1] - q0[0] - q1[3] - q0[3] - q1[0] - q1[1] - q1[2] - 8
          |       |       |       |       |       |       |     |
        q0[2] - q1[4] -- 14 ---- 13 ---- 12 ---- 11 ---- 10 --- 9
        """
        cmap16 = FakeRueschlikon().configuration().coupling_map

        qr0 = QuantumRegister(4, 'q0')
        qr1 = QuantumRegister(5, 'q1')
        circuit = QuantumCircuit(qr0, qr1)
        circuit.cx(qr0[1], qr0[2])  # q0[1] -> q0[2]
        circuit.cx(qr0[0], qr1[3])  # q0[0] -> q1[3]
        circuit.cx(qr1[4], qr0[2])  # q1[4] -> q0[2]

        dag = circuit_to_dag(circuit)
        pass_ = MCMCLayout(CouplingMap(cmap16), strict_direction=False, seed=self.seed)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr0[0]], 13)
        self.assertEqual(layout[qr0[1]], 6)
        self.assertEqual(layout[qr0[2]], 7)
        self.assertEqual(layout[qr0[3]], 12)
        self.assertEqual(layout[qr1[0]], 2)
        self.assertEqual(layout[qr1[1]], 1)
        self.assertEqual(layout[qr1[2]], 9)
        self.assertEqual(layout[qr1[3]], 4)
        self.assertEqual(layout[qr1[4]], 10)
        self.assertEqual(pass_.property_set['MCMCLayout_stop_reason'], 'solution found')
        
    def test_3q_circuit_5q_coupling_broken(self):
        """ 3 fully-connected qubits in Bogota
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

        pass_ = MCMCLayout(coupling_map,
                           seed=self.seed)
        pass_.run(dag)
        layout = pass_.property_set['layout']

        self.assertEqual(layout[qr[0]], 4)
        self.assertEqual(layout[qr[1]], 3)
        self.assertEqual(layout[qr[2]], 2)
        self.assertEqual(pass_.property_set['MCMCLayout_stop_reason'], 'solution found')

if __name__ == '__main__':
    unittest.main()