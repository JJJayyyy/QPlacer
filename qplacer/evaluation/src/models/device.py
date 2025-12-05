from collections import defaultdict

GATETIMES = {
             'rz': 30, 
             'x': 30, 
             'sx': 30,   
             'id': 30,  
             'z':30, 
             'rx': 30, 
             'ry': 30, 
             'y': 30, 
             'u1': 30, 
             'u2': 30, 
             'u3': 30, 
             's': 30, 
             't': 30, 
             'h': 30, 
             'unitary': 55,
             'measure': 0.0, 
             'barrier': 0.0} # all in ns


def name_to_idx(name, prefix_len=1):
    return int(name[prefix_len:])

def sfreq_to_float(freq_str):
    return float(freq_str.lower().replace('ghz', '').strip())



class Device(object):
    """
        Define attributes in the device
    """
    def __init__(self, 
                 g_connect, 
                 q_xtalk,
                 e_xtalk,
                 qubits_frequency,
                 edges_frequency,
                 cqq=1.5, 
                 alpha=-0.31,  
                 error_1q_gate=2.141e-4, # X, ID, SX = 2.141e-4 ibm_sherbrooke
                 error_2q_gate=7.340e-3,
                 crr=8,
                 name=''
                ):
        self.device_name = name
        self.g_connect = g_connect
        self.num_qubits = len(self.g_connect.nodes())

        coupling_list = self.g_connect.edges()
        self.coupling = [(name_to_idx(q1), name_to_idx(q2)) for q1, q2 in coupling_list]

        self.q_xtalk_net = {(name_to_idx(q1), name_to_idx(q2)): round(v/1000*cqq, 3) for (q1, q2), v in q_xtalk.items()}
        self.edge_xtalk_net = defaultdict(list)
        for (e1, e2), v in e_xtalk.items():
            c_couple = v/1000 * crr
            rename_e1 = (name_to_idx(e1[0]), name_to_idx(e1[1]))
            rename_e2 = (name_to_idx(e2[0]), name_to_idx(e2[1]))
            self.edge_xtalk_net[rename_e1].append([rename_e2, c_couple])
            self.edge_xtalk_net[rename_e2].append([rename_e1, c_couple])
        
        self.cqq = cqq
        self.alpha = alpha
        self.gate_times = GATETIMES
        self.error_1q_gate = error_1q_gate
        self.error_2q_gate = error_2q_gate
        # ibm_sherbrooke: T1=273.61us, T2=176.86us
        self.T1 = 273.61e3
        self.T2 = 176.86e3

        self.q_01freqs = {name_to_idx(k): sfreq_to_float(v) for k, v in qubits_frequency.items()}
        self.q_12freqs = {k: round(v+self.alpha, 3) for k, v in self.q_01freqs.items()}
        self.edge_freqs = {(name_to_idx(q1), name_to_idx(q2)): sfreq_to_float(v) for (q1, q2), v in edges_frequency.items()}


    def info(self):
        print(f'Device: {self.device_name}')
        print(f'g_connect : {self.g_connect}')
        print(f'coupling  : {self.coupling}')
        print(f'totalxtalk: {list(self.q_xtalk_net.keys())+list(self.edge_xtalk_net.keys())}')
        print(f'q_xtalk   : {self.q_xtalk_net}')
        print(f'e_xtalk   : {self.edge_xtalk_net}')
        print(f'q_01freq  : {self.q_01freqs}')
        print(f'q_12freq  : {self.q_12freqs}')
        print(f'edge_freq : {self.edge_freqs}')
        print()