import sys
import os
from collections import defaultdict
import pickle
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evaluation.src.static import static_coloring
from evaluation.src.success_rate import compute_decoherence, compute_crosstalk_by_layer
from evaluation.src.models import Device, get_map_circuit, get_layer_circuits
from evaluation.src.benchmarks import get_circuit


DATA_PATH = 'device_data.pkl'
RESULT_DIR = "simulation_result"
os.makedirs(RESULT_DIR, exist_ok=True)

CLASSIC_FILE = os.path.join(RESULT_DIR, "result_classic.pkl")
QPLACER_FILE = os.path.join(RESULT_DIR, "result_qplacer.pkl")
HUMAN_FILE = os.path.join(RESULT_DIR, "result_human.pkl")

SEED = 0
VERBOSE = 0
NUM_MAPPING = 1

TOPOLOGY = ["grid-25"]
CIRCUITS = [(4, 'bv'), (9, 'bv')]


def simulate(device, circuit, mapping, seed=0, verbose=0):
    initial_layout = {circuit.qubits[i]: mapping[i] for i in range(circuit.num_qubits)}
    circ_mapped = get_map_circuit(circuit, device.coupling,
                                  initial_layout=initial_layout,
                                  seed=seed,
                                  verbose=verbose)
    circ_layers = get_layer_circuits(circ_mapped)
    ir = static_coloring(device=device, circ_layers=circ_layers, verbose=verbose)
    err, swap_err, leak_err, gate_err, q_xtalk_err, e_xtalk_err = \
        compute_crosstalk_by_layer(device, ir, device.cqq, verbose)
    qde_err = compute_decoherence(device, ir)

    success = (1. - err) * (1. - qde_err)
    not_x_suc = (1. - gate_err) * (1. - qde_err)

    print("-----------------------------")
    print("Final success rate : %12.10f" % success)
    print("Swap error         : %12.10f" % swap_err)
    print("Leakage error      : %12.10f" % leak_err)
    print("Qubit gate error   : %12.10f" % gate_err)
    print("Qubit xtalk error  : %12.10f" % q_xtalk_err)
    print("Edge xtalk error   : %12.10f" % e_xtalk_err)
    print("Decoherence error  : %12.10f" % qde_err)
    print("Human success rate : %12.10f" % not_x_suc)
    print("-----------------------------")
    return success, not_x_suc


def main():
    with open(DATA_PATH, 'rb') as f:
        device_data = pickle.load(f)
        print(f"Loaded data from {DATA_PATH}")

    np.random.seed(SEED)

    classic_result = defaultdict(dict)
    qplacer_result = defaultdict(dict)
    human_result = defaultdict(dict)

    for topology in TOPOLOGY:
        qplacer_device_data = device_data[topology]["wp_wf_03"]
        qplacer_device = Device(
            g_connect=qplacer_device_data['db'].c_graph,
            q_xtalk=qplacer_device_data['qubit_adjacency_map'],
            e_xtalk=qplacer_device_data["edge_collision_map"],
            qubits_frequency=qplacer_device_data['db'].qubit_to_freq_map,
            edges_frequency=qplacer_device_data['db'].edge_to_freq_map,
            name='QPlacer'
        )

        classic_device_data = device_data[topology]["classical"]
        classic_device = Device(
            g_connect=classic_device_data['db'].c_graph,
            q_xtalk=classic_device_data['qubit_adjacency_map'],
            e_xtalk=classic_device_data["edge_collision_map"],
            qubits_frequency=classic_device_data['db'].qubit_to_freq_map,
            edges_frequency=classic_device_data['db'].edge_to_freq_map,
            name='Classic'
        )

        permuted_indices = [np.random.permutation(qplacer_device.num_qubits)
                           for _ in range(NUM_MAPPING)]

        for num_qubits, circuit_name in CIRCUITS:
            print(f'\nCircuit: {circuit_name}, #Qubit: {num_qubits}')

            if circuit_name == 'qrng':
                circuit_path = "evaluation/qrng_9qubit.qasm"
                circuit = get_circuit(num_qubits, circuit_name, path=circuit_path)
            else:
                circuit = get_circuit(num_qubits, circuit_name)

            print("================================")
            print(f"Benchmark Circuit:\n{circuit}")

            tmp_qplacer_result = []
            tmp_classic_result = []
            tmp_human_result = []

            for mapping in permuted_indices:
                print("\n================================")
                print(f'Mapping: {mapping}')

                classic_success, _ = simulate(classic_device, circuit, mapping,
                                          seed=SEED, verbose=VERBOSE)
                tmp_classic_result.append(classic_success)
                print("Classic DONE\n")

                qplacer_success, human_success = simulate(qplacer_device, circuit, mapping,
                                                         seed=SEED, verbose=VERBOSE)
                tmp_qplacer_result.append(qplacer_success)
                tmp_human_result.append(human_success)
                print("QPlacer DONE\n")

            avg_qplacer = np.average(tmp_qplacer_result)
            avg_classic = np.average(tmp_classic_result)
            avg_human = np.average(tmp_human_result)

            print(f'QPlacer: {avg_qplacer:.10f}, Classic: {avg_classic:.10f}, Human: {avg_human:.10f}')

            circuit_key = f'{circuit_name}_{num_qubits}'
            qplacer_result[topology][circuit_key] = avg_qplacer
            classic_result[topology][circuit_key] = avg_classic
            human_result[topology][circuit_key] = avg_human

        for result, file_path in zip([classic_result, qplacer_result, human_result],
                                     [CLASSIC_FILE, QPLACER_FILE, HUMAN_FILE]):
            with open(file_path, 'wb') as f:
                pickle.dump(result, f)
                print(f"Saved data to {file_path}")

    print(f'\nClassic result: {classic_result}')
    print(f'QPlacer result: {qplacer_result}')
    print(f'Human result: {human_result}')


if __name__ == '__main__':
    main()
