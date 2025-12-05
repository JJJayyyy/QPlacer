class Inst(object):
    def __init__(self, ins, qargs, cargs, int_freq, gt):
        self.ins = ins
        self.name = ins.name
        self.qargs = qargs
        self.cargs = cargs
        self.int_freq = int_freq
        self.gate_time = gt
    def qasm(self):
        return self.ins.qasm()
    
    def __str__(self):
        return f'gate time ({self.name}): {self.gate_time}, qargs: {self.qargs}'



class IR(object):
    def __init__(self):
        self.data = list()
        self.active_qubits = list()
        self.active_edges = list()
        self.depth = 0
        self.width = 0
        self.t_act = None
        self.t_2q = None
        self.num_1qg = 0
        self.num_2qg = 0
        self.total_time = .0

    def append_layer(self, layer):
        self.data.append(layer)
        self.depth += 1


    def append_layer_from_insts(self, insts):
        active = []
        gt = 0

        for inst in insts:
            int_freq = inst.int_freq
            for i in range(len(inst.qargs)):
                if inst.qargs[i] in active:
                    raise Exception("Warning: Qubit " + str(inst.qargs[i]) + " cannot be used twice in one time step.")
                else:
                   active.append(inst.qargs[i])

            if int_freq == None:
                self.num_1qg += 1
            else:
                self.num_2qg += 1
            if inst.gate_time >= gt:
                gt = inst.gate_time
        self.data.append((insts, gt))
    

    def __str__(self):
        print("\nIR attributes : ")
        ir_info = []
        for attr, value in self.__dict__.items():
            if attr == 'data':
                data_info = [f"\t({', '.join(str(d) for d in data_item[0])}, {data_item[1]})" for data_item in value]
                ir_info.append(f'{attr}: \n' + "\n".join(data_info))
            else:
                ir_info.append(f"{attr}: {value}")
        return "\n".join(ir_info)