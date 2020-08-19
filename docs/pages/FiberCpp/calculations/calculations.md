---
title: Calculations
parent: FiberCpp
has_children: false
nav_order: 4
---

# Calculations

FiberSim is a spatially-explicit model of a half-sarcomere. It describes a compliant network of protein filaments, which is detailed below.

![FiberSim myofilaments](Filaments.png)

## Actin filaments

Thin filaments are composed of nodes joined by linear springs of stiffness $k_{a}$ with a resting length $a_{rl}$. If the position of the $i^{th}$ node along an x-axis is noted $a_i$, then the force-balance equations for the thin filament can be written as:

$$ 2 \, k_a \, a_1 - k_a \, a_2 = 0$$

$$ -  k_a \, a_{i-1} + 2 \, k_a \, a_i - k_a \, a_{i+1} = 0 \,\,\, \text{for} \, 1 \lt i \lt n$$

$$ -k_a \, a_{n-1} + k_a \, a_n = k_a \, a_{rl}$$

## Myosin filaments

Thick filaments are composed of nodes joined by linear springs of stiffness $k_{m}$ with a resting length $m_{rl}$. A rigid link of length $\lambda$ connects the thick filament to the M-line. If the position of the $i^{th}$ node along an x-axis is noted $m_i$, and the half-sarcomere length is noted $l_{hs}$, then the force-balance equations for the thick filament can be written as:

$$ 2 \, k_m \, m_1 - k_m \, m_2 = k_m \, (l_{hs}- \lambda)$$

$$ -  k_m \, m_{i-1} + 2 \, k_m \, m_i - k_m \, m_{i+1} = 0 \,\,\, \text{for} \, 1 \lt i \lt n$$

$$ k_m \, m_{n-1} - k_m \, m_n = k_m \, m_{rl}$$

The system of equations for the thin and thick filament can be written in matrix form:

$$ K x = F$$

where $K$ is a matrix containing the springs stiffness, $x$ is a vector containing the positions of the actin and myosin nodes ($a_i$ and $m_i$, respectively) and $F$ is a vector containing the constant terms (independent of nodes positions). $K$ is a tridiagonal matrix:

\begin{eqnarray}
K = \begin{pmatrix}
\unicode{x23} & \unicode{x23} & & 0 \\\
\unicode{x23} & \ddots & \ddots &  \\\
& \ddots & \ddots &  \unicode{x23} \\\
0 &  & \unicode{x23} & \unicode{x23}
\end{pmatrix}
\end{eqnarray}

and numerical methods exist to solve $$ K x = F$$ for $x$.


## Crossbridge links 

Myosin heads located at the thick filament nodes can attach to neighboring binding sites at the thin filament nodes, thus affecting the filament lattice framework. 

<p align="center">
  <img alt="cb_link" src="cb_link.png">
</p>

A crossbridge located at the $j^{th}$ thick filament node which attaches to the $i^{th}$ node of the thin filament generates a force $f_{cb}$ given by:

$$f_{cb} = k_{cb} \, (m_j - a_i + x_{ps})$$

where  $k_{cb}$ is the crossbridge spring stiffness and $x_{ps}$ is the crossbridge extension when deploying the power stroke.

This additional force on the filaments should be added to the force-balance equations :

$$-  k_a \, a_{i-1} + 2 \, k_a \, a_i - k_a \, a_{i+1} \, \color{red}{- \, k_{cb} \, a_i + k_{cb} \, m_j} = \color{blue}{f_{cb} \, x_{ps}}$$

$$-  k_m \, m_{j-1} + 2 \, k_m \, m_j - k_m \, m_{j+1} \, \color{red}{+ \, k_{cb} \, a_i - k_{cb} \, m_j} = \color{blue}{-f_{cb} \, x_{ps}}$$ 

The terms in red will add non-tridiagonal, opposite elements to the $K$ matrix: 

\begin{eqnarray}
K = \begin{pmatrix}
\unicode{x23} & \unicode{x23} & \color{red}{\unicode{x23}} & 0 \\\
\unicode{x23} & \ddots & \ddots &  \\\
\color{red}{-\unicode{x23}} & \ddots & \ddots &  \unicode{x23} \\\
0 &  & \unicode{x23} & \unicode{x23}
\end{pmatrix}
\end{eqnarray}

while the blue terms will contribute to the $F$ vector. 

Crossbridge linking toughens the numerical solving of $$K x = F$$, which notably requires an iterative procedure to find a solution $x$ that satisfies a certain precision. 

## Titin 

Titin is responsible for the passive force developing within the half-sarcomere when it is streched, and for the recoil force when it is shortened. In the model, it is assumed that titin is a linear spring of stiffness $k_t$ and rest length $t_{rl}$. This spring is attached at both ends, on a particular thick and thin filament node respectively. Similar to crossbridge links, titin adds some force contribution $f_{t}$ to the force-balance equations:

$$f_{t} = k_{t} \, (m_l - a_k - t_{rl})$$

![Titin](titin.png)

## Myosin-binding Protein C

(yet to be written)


