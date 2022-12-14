
import numpy as np

# Importing standard Qiskit libraries
from qiskit.tools.jupyter import *
from qiskit.visualization import *
from qiskit.visualization import plot_histogram
from qiskit.algorithms.optimizers import COBYLA

from qiskit import *
import qiskit.quantum_info as qi
from qiskit.tools.visualization import plot_histogram
from qiskit.providers.aer import AerSimulator
from qiskit.providers.aer.noise import *
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
pi = math.pi


def getError(ckt_info):
    return ckt_info['error']


def U_prep(n_qubits, theta):
    qc = QuantumCircuit(n_qubits)
    qc.ry(theta, 0)
    for qubit in range(n_qubits-1):
        qc.cx(qubit, qubit+1)
    qc.barrier()
    # for qubit in range(n_qubits):
    #     qc.h(qubit)
    # qc.barrier()
    return qc


# If state is not in the set of valid states, ouput is erroneous
def cost(counts):
    invalid_states_count = 0
    diff = 0
    counts = dict(counts)
    for state in counts.keys():
        if (state != '0000') and (state != '1111'):
            invalid_states_count += counts[state]
        # probability of getting the other 8 valid states is 5000/10000
        else:
            if (counts[state]-5000 >= 0):
                # we got a valid state but how far is it from the ideal value? i.e deviation from correct value
                diff += (counts[state]-5000)
    total_error = round((invalid_states_count + diff)/10000, 4)
    return {'invalid_states_count': invalid_states_count, 'deviation': diff, 'error': total_error}


def padded_circuit(n_qubits, theta, delay):
    qc = U_prep(n_qubits, theta)

    for qubit in range(n_qubits):
        qc.h(qubit)
    qc.delay(delay, unit='ns')
    for qubit in range(n_qubits):
        qc.h(qubit)
    qc.measure_all()
    return qc


def pad_circuits_with_gates(n_qubits, theta, delay):
    qc = U_prep(n_qubits, theta)
    range_low, increment = 0, pi/32
    range_high = 2*pi - increment
    circuits = []
    angle1 = range_low
    while (angle1 <= range_high):  # u = rx, v = rx
        angle2 = range_low
        while (angle2 <= range_high):

            qc_pad = qc.copy()

            for qubit in range(n_qubits):     # u = rx
                qc_pad.rx(angle1, qubit)

            qc_pad.delay(delay, unit='ns')

            for qubit in range(n_qubits):     # v = rx
                qc_pad.rx(angle2, qubit)

            qc_pad.measure_all()
            circuits.append((qc_pad, angle1, angle2))
            angle2 += increment
        angle1 += increment

    angle1 = range_low
    while (angle1 <= range_high):  # u = rx, v = ry
        angle2 = range_low
        while (angle2 <= range_high):

            qc_pad = qc.copy()

            for qubit in range(n_qubits):     # u = rx
                qc_pad.rx(angle1, qubit)

            qc_pad.delay(delay, unit='ns')

            for qubit in range(n_qubits):     # v = ry
                qc_pad.ry(angle2, qubit)

            qc_pad.measure_all()
            circuits.append((qc_pad, angle1, angle2))
            angle2 += increment
        angle1 += increment

    angle1 = range_low
    while (angle1 <= range_high):  # u = ry, v = rx
        angle2 = range_low
        while (angle2 <= range_high):

            qc_pad = qc.copy()

            for qubit in range(n_qubits):     # u = ry
                qc_pad.ry(angle1, qubit)

            qc_pad.delay(delay, unit='ns')

            for qubit in range(n_qubits):     # v = rx
                qc_pad.rx(angle2, qubit)

            qc_pad.measure_all()
            circuits.append((qc_pad, angle1, angle2))

            angle2 += increment
        angle1 += increment

    angle1 = range_low
    while (angle1 <= range_high):  # u = ry, v = ry
        angle2 = range_low
        while (angle2 <= range_high):

            qc_pad = qc.copy()

            for qubit in range(n_qubits):     # u = ry
                qc_pad.ry(angle1, qubit)

            qc_pad.delay(delay, unit='ns')

            for qubit in range(n_qubits):     # v = ry
                qc_pad.ry(angle2, qubit)

            qc_pad.measure_all()
            circuits.append((qc_pad, angle1, angle2))
            angle2 += increment
        angle1 += increment

    return circuits


def thermal_relaxation(T1, delay_time):

    # T1 = 100000  # in ns
    # T2 = 100000  # considering T2 = T1
    T2 = T1
    noise_model = NoiseModel()

    err = thermal_relaxation_error(T1, T2, delay_time)
    noise_model.add_all_qubit_quantum_error(err, 'delay')
    backend = AerSimulator(noise_model=noise_model)

    qc_without_hadamard = U_prep(4, pi/2)
    qc_without_hadamard.delay(delay_time, unit='ns')
    qc_without_hadamard.measure_all()

    results_ideal = AerSimulator().run(qc_without_hadamard, shots=10000).result()
    counts_ideal = results_ideal.get_counts()

    counts_without_hadamard = backend.run(
        qc_without_hadamard, shots=10000).result().get_counts()

    qc_with_hadamard = padded_circuit(4, pi/2, delay_time)

    counts_with_hadamard = backend.run(
        qc_with_hadamard, shots=10000).result().get_counts()

    ckts = pad_circuits_with_gates(4, pi/2, delay_time)

    # ### Measuring error for all the circuits and finding the circuit with least error
    min_error = 999999
    min_err_info = None
    min_ckt = None

    for ckt in tqdm(range(len(ckts))):
        qc = ckts[ckt][0]
        counts = backend.run(qc, shots=10000).result().get_counts()
        err = cost(counts)
        err['index'] = ckt
        if (err['error'] < min_error):
            min_error = err['error']
            min_ckt = qc
            min_err_info = err
    return min_ckt, min_err_info, min_error

    # error.append(err)
    # error.sort(key=getError)
    # opt_idx = error[0]['index']
    # min_err_ckt = ckts[opt_idx][0]

    # errors = []
    # for i in range(len(ckts)):
    #     errors.append(error[i]['error'])
    # Seprrating angles of U and V
    # x = np.array([ckt[:][1] for ckt in ckts])  # U angle
    # x = np.array_split(x, len(x) / 4096)

    # y = np.array([ckt[:][2] for ckt in ckts])  # V angle
    # y = np.array_split(y, len(y) / 4096)
    # z = np.array_split(np.array(errors), len(error)/4096)

    # return  ckts, error, opt_idx, min_err_ckt


if __name__ == '__main__':
    min_ckt, min_err_info, min_error = thermal_relaxation(
        T1=10000, delay_time=500)
    print(min_error, min_err_info)
    min_ckt.draw('mpl')
