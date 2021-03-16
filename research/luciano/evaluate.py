from qiskit import assemble
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.passes import CSPLayout, DenseLayout, NoiseAdaptiveLayout, \
    SabreLayout
from qiskit.providers.aer import QasmSimulator
from qiskit.providers.aer.noise import NoiseModel

from custom_passmanager import custom_pass_manager


def evaluate(circuit, layout_method, backend, ideal=True, shots=1, seed=None):
    coupling_map = CouplingMap(backend.configuration().coupling_map)
    backend_properties = backend.properties()

    if layout_method == 'csplayout':
        layout = CSPLayout(coupling_map, seed=seed, call_limit=None, time_limit=None)
    elif layout_method == 'dense':
        layout = DenseLayout(coupling_map, None if ideal else backend_properties)
    elif layout_method == 'noise_adaptive':
        layout = NoiseAdaptiveLayout(backend_properties)
    elif layout_method == 'sabre':
        layout = SabreLayout(coupling_map, max_iterations=1, seed=seed)
    else:
        raise Exception('layout_method unknown %s' % layout_method)

    if ideal:
        simulator = QasmSimulator(configuration=backend.configuration(), method='stabilizer')
    else:
        noise_model = NoiseModel.from_backend(backend, thermal_relaxation=False)
        simulator = QasmSimulator(configuration=backend.configuration(),
                                  noise_model=noise_model,
                                  method='stabilizer')

    passmanager = custom_pass_manager(backend, layout, seed=seed)

    times = {}
    count_ops_after_map = {}
    def callback(**kwargs):
        times[kwargs['pass_'].__class__.__name__] = kwargs['time']
        if kwargs['pass_'].__class__.__name__ == 'StochasticSwap':
            count_ops_after_map.update(kwargs['dag'].count_ops())

    transpiled = passmanager.run(circuit, callback=callback)

    needed_swaps = 0 if passmanager.property_set['is_swap_mapped'] else count_ops_after_map['swap']

    qobj = assemble(transpiled, backend, shots=shots, seed_simulator=seed)

    return simulator.run(qobj).result(), times[layout.__class__.__name__], needed_swaps


def tvd_on_result(ideal_result, noise_result):
    ideal_counts = ideal_result.get_counts()
    for noise_count in noise_result.get_counts():
        if noise_count not in ideal_counts:
            ideal_counts[noise_count] = 0

    noise_counts = noise_result.get_counts()
    for ideal_count in ideal_result.get_counts():
        if ideal_count not in noise_counts:
            noise_counts[ideal_count] = 0

    return tvd(ideal_counts, noise_counts)


def tvd(p, q):
    """total variation distance"""
    list_of_diffs = []
    for bit_string in p:
        p_i = p[bit_string]
        q_i = q[bit_string]
        list_of_diffs.append(abs(p_i - q_i))
    return sum(list_of_diffs) / 2
