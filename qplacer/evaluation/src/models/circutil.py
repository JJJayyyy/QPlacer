from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.transpiler import CouplingMap
from qiskit.compiler import transpile
import logging
logging.getLogger('qiskit').setLevel(logging.WARNING)


def get_map_circuit(circuit, coupling_list, initial_layout, seed=0, verbose=0):
    coupling_map = CouplingMap(couplinglist=coupling_list)
    basis_gates = ['cz', 'id', 'rz', 'sx', 'x']

    optimized_circuit = transpile(circuit,
                                  basis_gates=basis_gates,
                                  coupling_map=coupling_map,
                                  initial_layout=initial_layout,
                                  seed_transpiler=seed,
                                  optimization_level=3)
    if verbose:
        print("================================")
        print(f"\nTranspiled:\n{optimized_circuit}")
        print("================================")
    return optimized_circuit


def get_layer_circuits(circuit):
    """Returns a list of circuits representing each simultaneous layer of circuit."""
    dagcircuit = circuit_to_dag(circuit)
    layer_circuits = []
    for layer in dagcircuit.layers():
        layer_circuits.append(dag_to_circuit(layer['graph']))
    return layer_circuits