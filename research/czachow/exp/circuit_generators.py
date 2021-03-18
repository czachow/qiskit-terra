import numpy
from qiskit.circuit.library import GraphState


def graphstate_manhatten_ring(ring_size=12):
    def ring_map(size):
        for j in range(size):
            yield [j, (j+1) % ring_size]
            yield [(j+1) % ring_size, j]

    coupling_map = list(ring_map(ring_size))

    rows, cols = zip(*coupling_map)

    matrix = numpy.zeros((ring_size, ring_size))
    matrix[rows, cols] = 1

    qc = GraphState(matrix)
    qc.measure_all()

    return qc


def graphstate_complete(num_qubits):

    matrix = numpy.ones((num_qubits, num_qubits))
    qc = GraphState(matrix)
    qc.measure_all()

    return qc
