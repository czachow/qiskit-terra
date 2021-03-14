from qiskit.test.mock.backends import FakeManhattan
from generate_circuits import generate_circuit_sub_coupling_map
from evaluate import evaluate, tvd_on_result
from write_csv_row import write_csv_row

shots = 8192
backend = FakeManhattan()
circuit = generate_circuit_sub_coupling_map(backend.configuration().coupling_map,
                                            [0, 1, 2, 3, 4, 10, 11, 13, 14, 15, 16, 17])

for seed in range(10):
    ideal_result = evaluate(circuit, 'csplayout', backend=backend, ideal=True,
                            routing=False, shots=shots, seed=seed)
    noise_result = evaluate(circuit, 'csplayout', backend=backend, ideal=False,
                            routing=False, shots=shots, seed=seed)
    write_csv_row('exp1_csplayout.csv', {'seed': seed,
                                         'tvd': tvd_on_result(ideal_result, noise_result)})