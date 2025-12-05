import sys
from .bv import get_bv_circuit
from .qaoa import get_qaoa_circuit
from .qgan import get_qgan_circuit
from .ising import get_ising_circuit
from .shor import get_shor_circuit
from .steane import get_steane_circuit
from qiskit import QuantumCircuit

def get_circuit(numQ, circ_name, dep=0, path=''):
    if circ_name=='bv':
        hs = '00101'*(numQ//5 + 1)
        return get_bv_circuit(numQ, hs[:numQ])
    elif circ_name == 'qaoa':
        return get_qaoa_circuit(numQ, 0.5, 1)
    elif circ_name == 'qgan':
        return get_qgan_circuit(numQ)
    elif circ_name == 'ising':
        return get_ising_circuit(numQ)
    elif circ_name == 'qrng':
        print(f'path: {path}')
        return QuantumCircuit.from_qasm_file(path)
    elif circ_name == 'shor':
        return get_shor_circuit()
    elif circ_name == 'steane':
        return get_steane_circuit()
    else:
        print("Circuit name %s not recognized." % circ_name)
        sys.exit()
