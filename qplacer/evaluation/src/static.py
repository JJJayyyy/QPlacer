from qiskit.converters import circuit_to_dag, dag_to_circuit
from qiskit.transpiler import CouplingMap
from qiskit.compiler import transpile
from .models import IR, Inst
import networkx as nx
import numpy as np
import math


def get_max_time(gt, taus):
    tmax = gt
    for t in taus.values():
        if t > tmax: tmax = t
    return tmax



def static_coloring(device, circ_layers, verbose):
    device_q_num = device.num_qubits
    ir = IR()
    t_act = np.zeros(device_q_num)
    t_2q = np.zeros(device_q_num)
    active_list = [False for i in range(device_q_num)]
    active_edges = list()
    total_time = 0.0 # in ns
    
    for idx, layer in enumerate(circ_layers):
        insts = []
        taus = {}   # For storing couplings that needed sqrt iswaps
        gate_time = 0.0
        layer_time = 0.0 # ns
        barrier = False

        for gate, qargs, cargs in layer.data:
            if gate.name == "barrier": 
                barrier = True
            elif gate.name == "measure": 
                continue
            else:
                if verbose: 
                    print(gate.qasm(), qargs)

            if len(qargs) == 1:
                device_idx = qargs[0].index     # convert to qubit idx on device 
                active_list[device_idx] = True
                gate_time = device.gate_times[gate.name]
                if gate_time > layer_time: 
                    layer_time = gate_time
                insts.append(Inst(gate, qargs, cargs, None, gate_time))

            elif len(qargs) == 2:
                q1, q2 = qargs[0].index, qargs[1].index     # convert to qubit idx on device 
                assert q1 < q2, 'q1: {}, q2: {}'.format(q1, q2)
                active_list[q1], active_list[q2] = True, True
                active_edges.append((q1, q2))

                if (gate.name == 'cz'):    # g.name == 'cp'
                    q1_f, q2_f = device.q_01freqs[q1], device.q_01freqs[q2]
                    coupler_f = device.edge_freqs[(q1, q2)]
                    f_diff = np.sqrt(np.abs(coupler_f-q1_f) * np.abs(coupler_f-q2_f))
                    epsilon_R = 315e6
                    Delta = 40e6  
                    g = 0.08 
                    chi = (g * 1e9)**2 / (f_diff * 1e9)
                    theta = (epsilon_R**2 * chi**2)/ ((8 * Delta) * (2*chi + Delta) * (4*chi + Delta))
                    gate_time = round((math.pi/(4*theta))/1e-9, 3)   # in ns
                    taus[(q1, q2)] = gate_time
                    if verbose:
                        print(f'{q1_f}, {q2_f} - {coupler_f} | J: {g} Ghz, diff: {f_diff:.4f} Ghz, chi : {chi/1e6:.4f} Mhz, gt: {gate_time:.4f} ns')
                else:
                    raise Exception(f"Gate ({gate.name}) not recognized.")
                t_2q[q1] += taus[(q1,q2)]
                t_2q[q2] += taus[(q1,q2)]
                insts.append(Inst(gate, qargs, cargs, [q1_f, q2_f], taus[(q1,q2)]))

        if not barrier:
            ir.append_layer_from_insts(insts)
            gate_time = get_max_time(gate_time, taus)
            if gate_time > layer_time: 
                layer_time = gate_time
            total_time += layer_time
            for qubit in range(device_q_num):
                if active_list[qubit]:
                    t_act[qubit] += layer_time

    ir.depth = len(circ_layers)
    ir.total_time = total_time
    ir.t_act = t_act
    ir.t_2q = t_2q

    ir.active_qubits = list()
    for idx, active in enumerate(active_list):
        if active:
            ir.active_qubits.append(idx)
    ir.active_edges = active_edges
    ir.width = len(ir.active_qubits)

    if verbose:
        print(ir)

    return ir 