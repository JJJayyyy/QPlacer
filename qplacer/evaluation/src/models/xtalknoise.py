import numpy as np


def edge_swap_channel(edge_freq, tau, Cqq, C1=800, C2=800, verbose=0):
    assert len(edge_freq) == 2
    res = []
    f1 = edge_freq[0]
    f2 = edge_freq[1]
    delta_omega = np.abs(f1 - f2)
    g = 0.5 * np.sqrt(f1 * f2) * (Cqq / (np.sqrt(C1+Cqq) * np.sqrt(C2+Cqq)))

    if delta_omega/g > 5:
        g_eff = g**2 / (delta_omega * 4 * np.pi)
    else:
        g_eff = g

    res = np.sin(g_eff * tau)**2
    
    if verbose:
        print(f'ef: {f1}, {f2}|{delta_omega/g} t: {tau}, Cqq: {Cqq}, g: {g:.6f}, g_eff: {g_eff:.6}, g_eff*tau: {g_eff * tau:.6}, sin^2: {np.sin(g_eff*tau)**2:.6}')
        print(f'res : {res}')
    return res


def swap_channel(coupling, qubit_freqs, tau, Cqq, C1=80, C2=80, verbose=0):
    # return prob of rabi oscillation between 01 and 10 (i.e. iswap)
    # for each pair of coupled qubits
    # taus is list of hold durations: max swap happens at 2pi/g
    res = []
    for (q1,q2), Cqq in coupling.items():
        f1 = qubit_freqs[q1]
        f2 = qubit_freqs[q2]
        delta_omega = np.abs(f1 - f2)
        g = 0.5 * np.sqrt(f1 * f2) * (Cqq / (np.sqrt(C1+Cqq) * np.sqrt(C2+Cqq)))

        if delta_omega/g > 5:
            g_eff = g**2 / (delta_omega * 4 * np.pi)
        else:
            g_eff = g

        res.append(np.sin(g_eff * tau)**2)

        if verbose:
            print(f'nswap - qf: {f1}, {f2}|{delta_omega/g} t: {tau}, Cqq: {Cqq}, g: {g:.6f}, g_eff: {g_eff:.6}, g_eff*tau: {g_eff * tau:.6}, sin^2: {np.sin(g_eff*tau)**2:.6}')
    if verbose:
        print(f'res : {res}')
    return res


def leak_channel(coupling, qubit_01freqs, qubit_12freqs, tau, Cqq, C1=80, C2=80, verbose=0):
    # return prob of rabi oscillation between 11 and (20+02)/sqrt(2) (i.e. leakage)
    # for each pair of coupled qubits
    # taus is list of hold durations
    res = []
    for (q1,q2), Cqq in coupling.items():
        f1 = qubit_01freqs[q1]
        f2 = qubit_12freqs[q2]
        delta_omega = np.abs(f1 - f2)
        g = 0.5 * np.sqrt(f1 * f2) * (Cqq / (np.sqrt(C1+Cqq) * np.sqrt(C2+Cqq)))

        if delta_omega/g > 5:
            g_eff = (np.sqrt(2)*g)**2 / (delta_omega * 4 * np.pi)
        else:
            g_eff = np.sqrt(2) * g

        res.append(np.sin(g_eff * tau)**2)

        if verbose:
            print(f'leak - qf: {f1}, {f2}|{delta_omega/g} t: {tau}, Cqq: {Cqq}, g: {g:.6}, g_eff: {g_eff:.6}, g_eff*tau: {g_eff*tau:.6}, sin^2: {np.sin(g_eff*tau)**2:.6}')
    if verbose:
        print(f'res : {res}')
    return res