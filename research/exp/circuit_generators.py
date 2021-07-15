import numpy
from qiskit.circuit.library import GraphState
from qiskit.circuit.quantumcircuit import QuantumCircuit


def graphstate_manhatten_ring(num_qubits=12):
    def ring_map(size):
        for j in range(size):
            yield [j, (j+1) % size]
            yield [(j+1) % size, j]

    coupling_map = list(ring_map(num_qubits))
    rows, cols = zip(*coupling_map)

    matrix = numpy.zeros((num_qubits, num_qubits))
    matrix[rows, cols] = 1

    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            if matrix[i][j] == 1:
                qc.cz(i, j)

    return qc


def graphstate_manhatten_ring_fm(num_qubits=12):
    qc = graphstate_manhatten_ring(num_qubits)
    qc.measure_all()
    return qc


def graphstate_manhatten_ring_hm(num_qubits=12):
    qc = graphstate_manhatten_ring(num_qubits)

    creg = qc._create_creg(int(num_qubits / 2), 'meas')
    qc.add_register(creg)
    qc.barrier()
    for j in range(num_qubits):
        if j % 2 == 0:
            qc.measure(j, int(j / 2))

    return qc


def graphstate_complete(num_qubits):

    matrix = numpy.ones((num_qubits, num_qubits))
    
    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            if matrix[i][j] == 1:
                qc.cz(i, j)

    return qc


def graphstate_complete_fm(num_qubits):
    qc = graphstate_complete(num_qubits)
    qc.measure_all()
    return qc


def graphstate_complete_hm(num_qubits):
    qc = graphstate_complete(num_qubits)

    creg = qc._create_creg(int(num_qubits / 2), 'meas')
    qc.add_register(creg)
    qc.barrier()
    for j in range(num_qubits):
        if j % 2 == 0:
            qc.measure(j, int(j / 2))

    return qc