import numpy
from qiskit.circuit.library import GraphState
from qiskit.circuit.quantumcircuit import QuantumCircuit


def graphstate_ring(num_qubits=12):
    """
    x - x - x - x
    |           |
    x           x
    |           |
    x           x
    |           |
    x - x - x - x
    """
    def cpl_map(size):
        for j in range(size):
            yield [j, (j+1) % size]
            yield [(j+1) % size, j]

    coupling_map = list(cpl_map(num_qubits))
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

def graphstate_ring_corners(num_qubits=12):
    """
    x - x - x - x
    | /       \ |
    x           x
    |           |
    x           x
    | \       / |
    x - x - x - x
    """
    def cpl_map(size):
        for j in range(size):
            yield [j, (j+1) % size]
            yield [(j+1) % size, j]
            if j % 3 == 2:
                yield [j, (j+2) % size]
                yield [(j+2) % size, j]
    coupling_map = list(cpl_map(num_qubits))

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


def graphstate_complete(num_qubits):

    matrix = numpy.ones((num_qubits, num_qubits))
    
    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            if matrix[i][j] == 1:
                qc.cz(i, j)

    return qc


def circuit_add_meas(circuit, meas_type):

    # half measurement
    if meas_type == "hm":
        creg = circuit._create_creg(int(circuit.num_qubits / 2), 'meas')
        circuit.add_register(creg)
        circuit.barrier()
        for j in range(circuit.num_qubits):
            if j % 2 == 0:
                circuit.measure(j, int(j / 2))

    elif meas_type == "fm":
        circuit.measure_all()
    
    return circuit
