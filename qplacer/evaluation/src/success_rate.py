from .models import swap_channel, leak_channel, edge_swap_channel
import numpy as np
import math


def compute_decoherence(device, ir):
    decoh = 1.
    t_act = ir.t_act
    t_2q = ir.t_2q
    T1 = device.T1
    T2 = device.T2

    for i in ir.active_qubits:
        T1_tilde = T1*np.random.normal(0.7,0.1)
        T2_tilde = T2*np.random.normal(0.5,0.1)
        t1 = t_act[i]-t_2q[i]
        t2 = t_2q[i] # time spent on 2q gates
        decoh *= math.exp(-1.*t1/T1-t1/T2)
        decoh *= math.exp(-1.*t2/T1_tilde-t2/T2_tilde)
    return 1.0 - decoh


def compute_crosstalk_by_layer(device, ir, cqq, verbose=1):
    success = 1.0
    swap_success = 1.0
    leak_success = 1.0
    q_success = 1.0
    e_success = 1.0
    error_1q_gate = device.error_1q_gate
    error_2q_gate = device.error_2q_gate

    q_xtalk_net = device.q_xtalk_net
    edge_xtalk_net = device.edge_xtalk_net
    
    active_q_in_xtalk_net = dict()  # the device qubits are active and has crosstalk potentails
    for (q1, q2), cqq in q_xtalk_net.items():
        if q1 in ir.active_qubits or q2 in ir.active_qubits:
            active_q_in_xtalk_net[(q1, q2)] = cqq
    
    num_coupling = len(active_q_in_xtalk_net)

    active_edges_in_extalk_net = list()
    for e, v in edge_xtalk_net.items():
        if e in ir.active_edges:
            active_edges_in_extalk_net.append(e)
    
    if verbose:
        print(f'active_q in xtalk: {active_q_in_xtalk_net}')
        print(f'active_e in extalk: {active_edges_in_extalk_net}')
    
    # one complete swap: tau = pi/2g
    for idx, (insts, gt) in enumerate(ir.data):
        prob_swap = swap_channel(active_q_in_xtalk_net, device.q_01freqs, gt, Cqq=cqq)
        prob_leak = leak_channel(active_q_in_xtalk_net, device.q_01freqs, device.q_12freqs, gt, Cqq=cqq)

        edge_xtalks = []
        for ins in insts:
            if len(ins.qargs)==2:
                cur_edge = (ins.qargs[0].index, ins.qargs[1].index)
                if cur_edge in active_edges_in_extalk_net:
                    potential_xtalk_edges = edge_xtalk_net[cur_edge]
                    if verbose:
                        print(f'ins : {ins.name}, {cur_edge} potential_xtalk_edges: {potential_xtalk_edges}')
                    for e2 in potential_xtalk_edges:   # e2: [edge, collision_length]
                        assert isinstance(e2[0], tuple) and isinstance(e2[1], float)
                        if e2[0][0] in ir.active_qubits or e2[0][1] in ir.active_qubits:
                            e_f1 = device.edge_freqs[cur_edge]
                            e_f2 = device.edge_freqs[e2[0]]
                            res = edge_swap_channel([e_f1, e_f2], gt, Cqq=e2[1], C1=800, C2=800)
                            edge_xtalks.append(res)
        if len(edge_xtalks) > 0:
            if verbose:
                print('edge_xtalks:', edge_xtalks)

        # Edge Xtalk
        layer_e_swap_suc = 0.0
        for edge_prob_swap in edge_xtalks:
            layer_e_swap_suc += 1 - edge_prob_swap

        # qubit Xtalk
        layer_q_swap_suc, layer_leak_suc = 0.0, 0.0
        for (i, (q1,q2)) in enumerate(active_q_in_xtalk_net):
            layer_q_swap_suc += 1 - prob_swap[i]
            layer_leak_suc += 1 - prob_leak[i]

        if num_coupling > 0:
            swap_num = num_coupling+len(edge_xtalks)
            layer_avg_swap_suc = (layer_e_swap_suc + layer_q_swap_suc) / swap_num
            layer_avg_leak_suc = layer_leak_suc / num_coupling
            q_xtalk_suc = (layer_q_swap_suc/num_coupling)*layer_avg_leak_suc
            e_xtalk_suc = layer_e_swap_suc/len(edge_xtalks) if len(edge_xtalks) > 0 else 1.0
        else:
            layer_avg_swap_suc = 1.
            layer_avg_leak_suc = 1.
            e_xtalk_suc = 1.
            q_xtalk_suc = 1.

        swap_success *= layer_avg_swap_suc
        leak_success *= layer_avg_leak_suc
        # xtalk suc
        e_success *= e_xtalk_suc
        q_success *= q_xtalk_suc

    success = swap_success * leak_success
    success *= (1 - error_1q_gate) ** ir.num_1qg
    success *= (1 - error_2q_gate) ** ir.num_2qg

    return (1-success, 
            1-swap_success, 
            1-leak_success, 
            1-(1-error_1q_gate) ** ir.num_1qg * (1 - error_2q_gate) ** ir.num_2qg, 
            1-q_success, 
            1-e_success)