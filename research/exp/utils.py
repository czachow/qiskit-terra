from qiskit.transpiler import CouplingMap
from qiskit.visualization import plot_circuit_layout

def run_layout_selector_on_circuit(circuit, layout_selector, backend, **kwargs):
    backend_config = backend.configuration()
    coupling_map = CouplingMap(backend_config.coupling_map)
    pass_ = layout_selector(coupling_map, **kwargs)
    property_set = {}
    pass_(circuit, property_set)
    circuit._layout = property_set['layout']
    return circuit

def layout_on_circuit(circuit, layout_selector, backend, **kwargs):
    circuit = run_layout_selector_on_circuit(circuit, layout_selector, backend, **kwargs)
    return plot_circuit_layout(circuit, backend)