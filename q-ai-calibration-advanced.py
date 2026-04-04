"""
Advanced Hybrid AI-Quantum Calibration Loop (VQA)
==================================================
Goal: Prepare a 2-qubit Bell State |Φ+⟩ = (|00⟩ + |11⟩)/√2
      using a parameterized ansatz circuit optimized by a
      classical Adam optimizer with the Parameter Shift Rule.

Key upgrades over the basic version:
  - Multi-qubit (2-qubit) parameterized ansatz
  - Real quantum gradient estimation via Parameter Shift Rule
  - Adam optimizer (adaptive learning rates + momentum)
  - Multi-layer ansatz (hardware-efficient circuit)
  - Fidelity metric + entanglement proxy tracking
  - Rich multi-panel learning dashboard
"""

from microqiskit import QuantumCircuit, simulate
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math
import random

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SHOTS       = 1024   # Measurement shots per circuit evaluation
EPOCHS      = 60     # Training epochs
LAYERS      = 2      # Ansatz depth (more layers = more expressive circuit)
SEED        = 42     # Reproducibility

random.seed(SEED)

# ─────────────────────────────────────────────
# ANSATZ BUILDER
# ─────────────────────────────────────────────
def build_ansatz(params, n_qubits=2, layers=2):
    """
    Hardware-efficient ansatz:
      For each layer:
        - RY(θ) on each qubit
        - RZ(φ) on each qubit
        - CNOT entangling gates between adjacent qubits
    Final: RY on each qubit
    Params layout: [layer][qubit][ry, rz] + final RY
    Total params = layers * n_qubits * 2 + n_qubits
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    idx = 0
    for _ in range(layers):
        for q in range(n_qubits):
            qc.ry(params[idx], q);     idx += 1
            qc.rz(params[idx], q);     idx += 1
        for q in range(n_qubits - 1):
            qc.cx(q, q + 1)            # Entangling CNOT
    for q in range(n_qubits):         # Final rotation layer
        qc.ry(params[idx], q);         idx += 1
    for q in range(n_qubits):
        qc.measure(q, q)
    return qc

def num_params(n_qubits=2, layers=2):
    return layers * n_qubits * 2 + n_qubits

# ─────────────────────────────────────────────
# COST FUNCTION  (Bell state fidelity proxy)
# ─────────────────────────────────────────────
def cost_fn(params):
    """
    Bell state |Φ+⟩ has equal probability of |00⟩ and |11⟩.
    Cost = 1 - (P('00') + P('11'))   ∈ [0, 1]
    Global minimum = 0 when circuit perfectly prepares Bell state.
    """
    qc = build_ansatz(params)
    counts = simulate(qc, shots=SHOTS, get='counts')
    p00 = counts.get('00', 0) / SHOTS
    p11 = counts.get('11', 0) / SHOTS
    return 1.0 - (p00 + p11), counts

# ─────────────────────────────────────────────
# PARAMETER SHIFT RULE  (exact quantum gradient)
# ─────────────────────────────────────────────
def parameter_shift_gradient(params):
    """
    For each parameter θ_i:
      ∂f/∂θ_i ≈ [f(θ_i + π/2) - f(θ_i - π/2)] / 2
    This is the *exact* gradient for gates of the form e^{-iθP/2}
    and is more accurate than finite differences.
    """
    grads = []
    shift = math.pi / 2
    for i in range(len(params)):
        p_plus  = params[:]
        p_minus = params[:]
        p_plus[i]  += shift
        p_minus[i] -= shift
        cost_plus,  _ = cost_fn(p_plus)
        cost_minus, _ = cost_fn(p_minus)
        grads.append((cost_plus - cost_minus) / 2.0)
    return grads

# ─────────────────────────────────────────────
# ADAM OPTIMIZER
# ─────────────────────────────────────────────
class Adam:
    def __init__(self, n_params, lr=0.15, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr    = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps   = eps
        self.m     = [0.0] * n_params   # 1st moment (momentum)
        self.v     = [0.0] * n_params   # 2nd moment (adaptive LR)
        self.t     = 0

    def step(self, params, grads):
        self.t += 1
        new_params = params[:]
        for i in range(len(params)):
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grads[i]
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * grads[i]**2
            m_hat = self.m[i] / (1 - self.beta1**self.t)
            v_hat = self.v[i] / (1 - self.beta2**self.t)
            new_params[i] -= self.lr * m_hat / (math.sqrt(v_hat) + self.eps)
        return new_params

# ─────────────────────────────────────────────
# TRAINING LOOP
# ─────────────────────────────────────────────
N_PARAMS = num_params(n_qubits=2, layers=LAYERS)
params   = [random.uniform(-math.pi, math.pi) for _ in range(N_PARAMS)]
optimizer = Adam(N_PARAMS, lr=0.15)

print("=" * 60)
print("  Advanced Hybrid AI-Quantum VQA  |  Bell State Prep")
print("=" * 60)
print(f"  Qubits: 2  |  Ansatz Layers: {LAYERS}  |  Params: {N_PARAMS}")
print(f"  Optimizer: Adam  |  Gradient: Parameter Shift Rule")
print(f"  Target: |Φ+⟩ = (|00⟩ + |11⟩)/√2  |  Ideal fidelity: 1.0")
print("=" * 60)

history_cost      = []
history_p00       = []
history_p11       = []
history_fidelity  = []
history_grad_norm = []

for epoch in range(EPOCHS):
    # Forward pass
    cost, counts = cost_fn(params)
    p00 = counts.get('00', 0) / SHOTS
    p11 = counts.get('11', 0) / SHOTS
    p01 = counts.get('01', 0) / SHOTS
    p10 = counts.get('10', 0) / SHOTS

    # Bell state fidelity proxy: should be ~1.0 at optimum
    fidelity = p00 + p11

    # Gradient via Parameter Shift Rule
    grads = parameter_shift_gradient(params)
    grad_norm = math.sqrt(sum(g**2 for g in grads))

    # Adam update
    params = optimizer.step(params, grads)

    history_cost.append(cost)
    history_p00.append(p00)
    history_p11.append(p11)
    history_fidelity.append(fidelity)
    history_grad_norm.append(grad_norm)

    if epoch % 10 == 0 or epoch == EPOCHS - 1:
        print(f"  Epoch {epoch:>3} | Cost: {cost:.4f} | Fidelity: {fidelity:.3f} "
              f"| P(00):{p00:.3f} P(11):{p11:.3f} | ‖∇‖:{grad_norm:.4f}")

print()
print(f"  ✓ Final Bell Fidelity : {history_fidelity[-1]:.4f}  (ideal = 1.0)")
print(f"  ✓ Final Cost          : {history_cost[-1]:.4f}  (ideal = 0.0)")
print(f"  ✓ Optimized Params    : {[round(p,3) for p in params]}")
print("=" * 60)

# ─────────────────────────────────────────────
# VISUALIZATION  (4-panel dashboard)
# ─────────────────────────────────────────────
fig = plt.figure(figsize=(14, 10), facecolor='#0d1117')
fig.suptitle('Advanced VQA Training Dashboard — Bell State Preparation',
             fontsize=15, color='white', fontweight='bold', y=0.98)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)
epochs_x = list(range(EPOCHS))

PANEL_BG   = '#161b22'
TEXT_COLOR = '#c9d1d9'
GRID_COLOR = '#21262d'

def style_ax(ax, title, xlabel, ylabel):
    ax.set_facecolor(PANEL_BG)
    ax.set_title(title, color=TEXT_COLOR, fontsize=11, pad=8)
    ax.set_xlabel(xlabel, color=TEXT_COLOR, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT_COLOR, fontsize=9)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.grid(True, linestyle='--', alpha=0.4, color=GRID_COLOR)

# Panel 1: Cost reduction
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(epochs_x, history_cost, color='#f85149', linewidth=2, label='Cost (MSE)')
ax1.fill_between(epochs_x, history_cost, alpha=0.15, color='#f85149')
style_ax(ax1, 'Cost Reduction (Adam + PSR)', 'Epoch', 'Cost')
ax1.legend(facecolor=PANEL_BG, labelcolor=TEXT_COLOR, fontsize=8)

# Panel 2: Bell fidelity
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(epochs_x, history_fidelity, color='#3fb950', linewidth=2, label='Bell Fidelity')
ax2.axhline(y=1.0, color='#58a6ff', linestyle='--', linewidth=1, alpha=0.7, label='Ideal = 1.0')
ax2.fill_between(epochs_x, history_fidelity, alpha=0.15, color='#3fb950')
ax2.set_ylim(0, 1.1)
style_ax(ax2, 'Bell State Fidelity  P(|00⟩) + P(|11⟩)', 'Epoch', 'Fidelity')
ax2.legend(facecolor=PANEL_BG, labelcolor=TEXT_COLOR, fontsize=8)

# Panel 3: Probability breakdown
ax3 = fig.add_subplot(gs[1, 0])
ax3.plot(epochs_x, history_p00, color='#58a6ff', linewidth=2, label='P(|00⟩)')
ax3.plot(epochs_x, history_p11, color='#d2a8ff', linewidth=2, label='P(|11⟩)')
ax3.axhline(y=0.5, color='#e3b341', linestyle='--', linewidth=1, alpha=0.7, label='Ideal = 0.5 each')
ax3.set_ylim(0, 1.0)
style_ax(ax3, 'Measurement Probability Convergence', 'Epoch', 'Probability')
ax3.legend(facecolor=PANEL_BG, labelcolor=TEXT_COLOR, fontsize=8)

# Panel 4: Gradient norm (optimizer health)
ax4 = fig.add_subplot(gs[1, 1])
ax4.plot(epochs_x, history_grad_norm, color='#e3b341', linewidth=2, label='‖∇‖ Gradient Norm')
ax4.fill_between(epochs_x, history_grad_norm, alpha=0.15, color='#e3b341')
style_ax(ax4, 'Gradient Norm (Parameter Shift Rule)', 'Epoch', '‖∇θ‖')
ax4.legend(facecolor=PANEL_BG, labelcolor=TEXT_COLOR, fontsize=8)

plt.savefig('/mnt/user-data/outputs/vqa_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor='#0d1117')
print("\n  Dashboard saved → vqa_dashboard.png")
plt.show()
