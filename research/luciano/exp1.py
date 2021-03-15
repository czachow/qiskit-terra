from qiskit.test.mock.backends import FakeManhattan
from generate_circuits import generate_circuit_sub_coupling_map
from evaluate import evaluate, tvd_on_result
from write_csv_row import write_csv_row

shots = 8192
samples = 10
backend = FakeManhattan()
circuit = generate_circuit_sub_coupling_map(backend.configuration().coupling_map,
                                            [0, 1, 2, 3, 4, 10, 11, 13, 14, 15, 16, 17])
def exp1(layout_method):
    for seed in range(samples):
        ideal_result, ideal_time = evaluate(circuit, layout_method, backend=backend, ideal=True,
                                            routing=False, shots=shots, seed=seed)
        noise_result, noise_time = evaluate(circuit, layout_method, backend=backend, ideal=False,
                                            routing=False, shots=shots, seed=seed)
        write_csv_row(f'exp1_{layout_method}.csv', {'seed': seed,
                                             'tvd': tvd_on_result(ideal_result, noise_result),
                                             'ideal_time': ideal_time,
                                             'noise_time': noise_time})

exp1('advance_csplayout')
exp1('csplayout')
exp1('dense')
exp1('noise_adaptive')
exp1('sabre')