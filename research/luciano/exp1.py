import sys
from generate_circuits import generate_circuit_sub_coupling_map
from generate_circuits import generate_circuit_complete_GraphState
from evaluate import evaluate, tvd_on_result
from write_csv_row import write_csv_row
from qiskit import IBMQ

import argparse
parser = argparse.ArgumentParser(description='run experiment.')
parser.add_argument('exp_name', metavar='EXP',
                    help='experiemnt name (exp1, exp2)')
parser.add_argument('layout', metavar='LAYOUT',
                    help='layout method (csplayout, dense, noise_adaptive, sabre' )

args = parser.parse_args()


IBMQ.load_account()
provider = IBMQ.get_provider(hub='ibm-q-internal', group='deployed', project='default')
backend = provider.get_backend('ibmq_manhattan')

shots = 2048
samples = 10

if args.exp_name == 'exp1':
    circuit = generate_circuit_sub_coupling_map(backend.configuration().coupling_map,
                                                [0, 1, 2, 3, 4, 10, 11, 13, 14, 15, 16, 17])
elif args.exp_name == 'exp2':
    circuit = generate_circuit_complete_GraphState(65)
else:
    sys.exit('%s is not a valid experiment' % args.exp_name)

def exp1(layout_method, exp_name):
    for seed in range(samples):
        ideal_result, ideal_time, swaps_needed_ideal = evaluate(
            circuit, layout_method, backend=backend, ideal=True, shots=shots, seed=seed)
        noise_result, noise_time, swaps_needed_noise = evaluate(
            circuit, layout_method, backend=backend, ideal=False, shots=shots, seed=seed)
        write_csv_row(f'{exp_name}_{layout_method}.csv',
                      {'seed': seed,
                       # 'tvd': tvd_on_result(ideal_result, noise_result),
                       'ideal_result': ideal_result.get_counts(),
                       'noise_result': noise_result.get_counts(),
                       'ideal_time': ideal_time,
                       'noise_time': noise_time,
                       'swaps_needed_ideal': swaps_needed_ideal,
                       'swaps_needed_noise': swaps_needed_noise })
        print(f'result in {exp_name}_{layout_method}.csv')

exp1(args.layout, args.exp_name)
