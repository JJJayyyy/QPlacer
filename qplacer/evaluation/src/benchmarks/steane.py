import qiskit

def get_steane_circuit():
    # Create quantum and classical registers
    qr = qiskit.QuantumRegister(7, name='q')
    cr = qiskit.ClassicalRegister(7, name='c')
    steane_circuit = qiskit.QuantumCircuit(qr, cr)
    
    # Prepare ancilla qubits in superposition
    steane_circuit.h(qr[1])
    steane_circuit.h(qr[2])
    steane_circuit.h(qr[3])
    
    # Entangle qubits based on parity checks
    steane_circuit.cx(qr[0], qr[4])
    steane_circuit.cx(qr[0], qr[5])
    steane_circuit.cx(qr[0], qr[6])
    
    steane_circuit.cx(qr[1], qr[4])
    steane_circuit.cx(qr[1], qr[5])
    
    steane_circuit.cx(qr[2], qr[4])
    steane_circuit.cx(qr[2], qr[6])
    
    steane_circuit.cx(qr[3], qr[5])
    steane_circuit.cx(qr[3], qr[6])
    
    steane_circuit.barrier()
    
    return steane_circuit