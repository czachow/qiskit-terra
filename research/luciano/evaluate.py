from qiskit import assemble
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.passes import CSPLayout, TrivialLayout, DenseLayout, NoiseAdaptiveLayout, \
    SabreLayout
from qiskit.providers.aer import QasmSimulator
from custom_passmanager import custom_pass_manager


def evaluate(circuit, layout_method, backend, ideal=True, shots=1, seed=None):
    """
    layout_method:
      - csplayout:
    """
    coupling_map = CouplingMap(backend.configuration().coupling_map)
    backend_properties = backend.properties()

    if layout_method == 'csplayout':
        layout = CSPLayout(coupling_map, seed=seed, call_limit=None, time_limit=None)
    elif layout_method == 'trivial':
        layout = TrivialLayout(coupling_map)
    elif layout_method == 'dense':
        layout = DenseLayout(coupling_map, backend_properties)
    elif layout_method == 'noise_adaptive':
        layout = NoiseAdaptiveLayout(backend_properties)
    elif layout_method == 'sabre':
        layout = SabreLayout(coupling_map, max_iterations=1, seed=seed)
    else:
        raise Exception('layout_method unknown %s' % layout_method)

    if ideal:
        simulator = QasmSimulator()
    else:
        simulator = QasmSimulator.from_backend(backend)

    passmanager = custom_pass_manager(backend, layout, seed=seed)
    qobj = assemble(passmanager.run(circuit), backend, shots=shots, seed=seed)

    return simulator.run(qobj, seed=seed).result()


from qiskit.test.mock.backends import FakeManhattan
from generate_circuits import generate_circuit_sub_coupling_map

backend = FakeManhattan()
circuit = generate_circuit_sub_coupling_map(backend.configuration().coupling_map,
                                            [0, 1, 2, 3, 4, 10, 11, 13, 14, 15, 16, 17])

noise_result = evaluate(circuit, 'csplayout', backend=backend, shots=1, seed=42)
print(noise_result.get_counts())
