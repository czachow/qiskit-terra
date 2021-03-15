import numpy
import qiskit
from itertools import permutations


def generate_circuit_complete_GraphState(n_qubits):
    A = numpy.ones((n_qubits, n_qubits))
    return qiskit.circuit.library.GraphState(A)


def generate_circuit_complete_cnot(n_qubits):
    # TODO only once CNOT per pair
    qc = qiskit.QuantumCircuit(n_qubits)
    perm = permutations(range(n_qubits), 2)
    for i in perm:
        qc.cx(i[0], i[1])
    return qc


def generate_circuit_sub_coupling_map(coupling_map, list_of_physical_qubits):
    def elected_edges(edge):
        if edge[0] not in list_of_physical_qubits:
            return False
        if edge[1] not in list_of_physical_qubits:
            return False
        return True

    rows = [list_of_physical_qubits.index(x[0]) for x in filter(elected_edges, coupling_map)]
    cols = [list_of_physical_qubits.index(x[1]) for x in filter(elected_edges, coupling_map)]

    n_qubits = len(list_of_physical_qubits)
    A = numpy.zeros((n_qubits, n_qubits))
    A[rows, cols] = 1

    qc = qiskit.circuit.library.GraphState(A)

    qc.measure_all()
    return qc
