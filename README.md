## Noise reduction with the help of padding with U and V gates.

Testing the effect of padding of unitaries $U$ and $V$ on every qubit. 

circuit will look like this:

![UV pading](./images/circuit-type.png)

Parameters which are variable for a given circuit is $\theta_1$ and $\theta_2$

and those parameters are varied for circuits with gates $U,V \in \{R_x,R_y,R_z\}$

And fidelity is calculated and plotted against the baseline (without padding with unitaries)

## Results

### For 5 qubits

![UV pading](./images/5-qubit.png)

And

![UV pading](./images/5-qubit-theta.png)


### For 6 qubits

![UV pading](./images/6-qubit.png)

And

![UV pading](./images/6-qubit-theta.png)

### For 7 qubits

![UV pading](./images/7-qubit.png)

And


![UV pading](./images/7-qubit-theta.png)

### For 10 qubits

![UV pading](./images/10-qubit.png)

And


![UV pading](./images/10-qubit-theta.png)


## For 5 qubits with different $\theta$ parameters

Here we have 5 different parameters for $U$, they are $\theta_{1},\theta_{2},\theta_{3},\theta_{4}$ and $\theta_{5}$.

And the circuit $V$ is just $U^{†}$. 

![UV pading](./images/circuit-type-different-theta.png)

## Delay vs fidelity

![UV pading](./images/5-qubit-different-theta.png)

