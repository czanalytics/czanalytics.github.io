"""
D-Wave-Style QUBO Portfolio Optimizer via QAOA
===============================================
Emulates the D-Wave quantum annealing approach to portfolio selection
using a gate-based QAOA (Quantum Approximate Optimization Algorithm),
which solves the same Ising/QUBO problem on a circuit-based quantum computer.

Problem : Select which assets to hold (binary: 0=exclude, 1=include)
          to maximize risk-adjusted return.

QUBO formulation (minimization):
  E(x) = -Σᵢ returnᵢ · xᵢ                 (reward term)
        + λ · Σᵢⱼ covᵢⱼ · xᵢ · xⱼ          (risk/correlation penalty)
        + μ · (Σᵢ xᵢ - K)²                  (cardinality constraint: hold K assets)

Ising mapping: xᵢ = (1 - sᵢ)/2,  sᵢ ∈ {-1,+1}
  → h  (linear bias)  and  J  (quadratic coupling) coefficients

QAOA Circuit (p=1 layer):
  1. H⊗ⁿ — equal superposition of all portfolios
  2. Phase separator  exp(-iγ H_cost)  — encodes the QUBO
  3. Mixer            exp(-iβ H_mixer) — explores solution space
  4. Measure — sample candidate portfolios

Classical comparisons:
  • Brute force  (exact,  2⁴ = 16 portfolios enumerated)
  • Simulated annealing  (classical heuristic, D-Wave analogy)

Speed design:
  4 assets → 4 qubits → 16-state space
  p=1 QAOA → 2 params (γ, β) → 4 PSR evals/gradient
  30 epochs → ~100 circuit evals total
  Estimated runtime: ~10–20 seconds
"""

from microqiskit import QuantumCircuit, simulate
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math, random

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
SHOTS   = 256
EPOCHS  = 30
LR      = 0.20
LAMBDA  = 0.8   # Risk aversion (higher = more risk-averse)
MU      = 1.5   # Cardinality penalty strength
K       = 2     # Target: hold exactly 2 assets
SEED    = 7
random.seed(SEED)

# ─────────────────────────────────────────
# PORTFOLIO DATA  (4 assets, realistic-ish)
# ─────────────────────────────────────────
ASSETS = ["Tech", "Energy", "Finance", "Health"]
N      = len(ASSETS)

# Annualised expected returns
RETURNS = [0.18, 0.10, 0.12, 0.14]

# Covariance matrix (symmetric, positive-definite)
COV = [
    [ 0.050,  0.010,  0.015,  0.005],
    [ 0.010,  0.030, -0.005,  0.002],
    [ 0.015, -0.005,  0.025,  0.008],
    [ 0.005,  0.002,  0.008,  0.020],
]

# ─────────────────────────────────────────
# QUBO ENERGY  E(x) for a bitstring
# ─────────────────────────────────────────
def qubo_energy(bits):
    """
    bits: list of 0/1 of length N (asset selection vector).
    Returns QUBO energy (lower = better portfolio).
    """
    x = list(bits)
    # Return term (maximise → negative sign)
    ret  = -sum(RETURNS[i] * x[i] for i in range(N))
    # Risk term
    risk = LAMBDA * sum(COV[i][j] * x[i] * x[j]
                        for i in range(N) for j in range(N))
    # Cardinality penalty
    card = MU * (sum(x) - K) ** 2
    return ret + risk + card

def bits_from_str(s):
    """'0101' → [0,1,0,1] (microqiskit bit order: s[0]=qubit0)."""
    return [int(c) for c in s]

# ─────────────────────────────────────────
# BRUTE FORCE  (exact solution, 2^N states)
# ─────────────────────────────────────────
def brute_force():
    best_e, best_b = float('inf'), None
    results = []
    for mask in range(1 << N):
        b = [(mask >> i) & 1 for i in range(N)]
        e = qubo_energy(b)
        results.append((e, b))
        if e < best_e:
            best_e, best_b = e, b
    results.sort()
    return best_e, best_b, results

# ─────────────────────────────────────────
# ISING COEFFICIENTS  (QUBO → Ising)
# xᵢ = (1 - sᵢ)/2  →  derive h and J
# ─────────────────────────────────────────
def qubo_to_ising():
    """
    Returns h[i] (bias) and J[i][j] (coupling) for the Ising Hamiltonian.
    """
    h = [0.0] * N
    J = [[0.0]*N for _ in range(N)]

    # Linear terms from return + diagonal risk + cardinality
    for i in range(N):
        h[i] += -RETURNS[i] / 2.0
        h[i] +=  LAMBDA * COV[i][i] / 2.0
        h[i] += -MU * K            # from expanding (Σxᵢ - K)²

    # Quadratic terms from off-diagonal risk + cardinality
    for i in range(N):
        for j in range(i+1, N):
            J[i][j] = LAMBDA * COV[i][j] / 2.0 + MU / 2.0

    # Constant offset doesn't affect optimisation — skip it
    return h, J

H_ISING, J_ISING = qubo_to_ising()

# ─────────────────────────────────────────
# QAOA CIRCUIT  (p = 1 layer)
# ─────────────────────────────────────────
def build_qaoa(gamma, beta):
    qc = QuantumCircuit(N, N)

    # Equal superposition
    for i in range(N):
        qc.h(i)

    # ── Phase separator: exp(-iγ H_cost) ──
    # ZZ coupling terms: CNOT → RZ(2γ Jᵢⱼ) → CNOT
    for i in range(N):
        for j in range(i+1, N):
            if abs(J_ISING[i][j]) > 1e-9:
                qc.cx(i, j)
                qc.rz(2.0 * gamma * J_ISING[i][j], j)
                qc.cx(i, j)
    # Z bias terms: RZ(2γ hᵢ)
    for i in range(N):
        if abs(H_ISING[i]) > 1e-9:
            qc.rz(2.0 * gamma * H_ISING[i], i)

    # ── Mixer: exp(-iβ H_mixer) = Π RX(2β) ──
    for i in range(N):
        qc.rx(2.0 * beta, i)

    for i in range(N):
        qc.measure(i, i)
    return qc

def expected_energy(gamma, beta, shots=SHOTS):
    """Sample the QAOA circuit, evaluate QUBO cost per sample → ⟨E⟩."""
    qc     = build_qaoa(gamma, beta)
    counts = simulate(qc, shots=shots, get='counts')
    total  = 0.0
    for bitstr, count in counts.items():
        b = bits_from_str(bitstr.zfill(N))
        total += qubo_energy(b) * count
    return total / shots, counts

# ─────────────────────────────────────────
# PSR GRADIENT  ∂⟨E⟩/∂γ  and  ∂⟨E⟩/∂β
# ─────────────────────────────────────────
def psr_gradient(gamma, beta):
    shift = math.pi / 2
    e_gp, _ = expected_energy(gamma + shift, beta)
    e_gm, _ = expected_energy(gamma - shift, beta)
    e_bp, _ = expected_energy(gamma, beta + shift)
    e_bm, _ = expected_energy(gamma, beta - shift)
    dg = (e_gp - e_gm) / 2.0
    db = (e_bp - e_bm) / 2.0
    return dg, db

# ─────────────────────────────────────────
# ADAM OPTIMIZER
# ─────────────────────────────────────────
class Adam:
    def __init__(self, lr=LR, b1=0.9, b2=0.999, eps=1e-8):
        self.lr,self.b1,self.b2,self.eps = lr,b1,b2,eps
        self.m,self.v,self.t = [0.,0.],[0.,0.],0

    def step(self, params, grads):
        self.t += 1
        out = params[:]
        for i in range(2):
            self.m[i] = self.b1*self.m[i] + (1-self.b1)*grads[i]
            self.v[i] = self.b2*self.v[i] + (1-self.b2)*grads[i]**2
            mh = self.m[i] / (1 - self.b1**self.t)
            vh = self.v[i] / (1 - self.b2**self.t)
            out[i] -= self.lr * mh / (math.sqrt(vh) + self.eps)
        return out

# ─────────────────────────────────────────
# SIMULATED ANNEALING  (classical baseline)
# ─────────────────────────────────────────
def simulated_annealing(n_steps=2000, T0=2.0, T_min=0.01):
    x     = [random.randint(0,1) for _ in range(N)]
    e     = qubo_energy(x)
    best_x, best_e = x[:], e
    T     = T0
    alpha = (T_min / T0) ** (1.0 / n_steps)
    sa_hist = [e]

    for step in range(n_steps):
        i      = random.randint(0, N-1)
        x_new  = x[:]
        x_new[i] ^= 1
        e_new  = qubo_energy(x_new)
        delta  = e_new - e
        if delta < 0 or random.random() < math.exp(-delta / T):
            x, e = x_new, e_new
            if e < best_e:
                best_e, best_x = e, x[:]
        T *= alpha
        if step % (n_steps // 50) == 0:
            sa_hist.append(e)

    return best_e, best_x, sa_hist

# ─────────────────────────────────────────
# RUN ALL SOLVERS
# ─────────────────────────────────────────
print("=" * 64)
print("  D-Wave-Style QUBO Portfolio Optimizer")
print("  QAOA (gate-based) vs Simulated Annealing vs Brute Force")
print("=" * 64)
print(f"  Assets : {ASSETS}")
print(f"  Returns: {RETURNS}")
print(f"  Goal   : Select {K} assets, maximise return, minimise risk")
print("=" * 64)

# 1. Brute force
bf_energy, bf_bits, bf_all = brute_force()
bf_assets = [ASSETS[i] for i in range(N) if bf_bits[i]]
print(f"\n  [Brute Force]  Best: {bf_assets}  |  Energy: {bf_energy:.4f}")

# 2. Simulated annealing
sa_energy, sa_bits, sa_hist = simulated_annealing()
sa_assets = [ASSETS[i] for i in range(N) if sa_bits[i]]
print(f"  [Sim Anneal]   Best: {sa_assets}  |  Energy: {sa_energy:.4f}")

# 3. QAOA training
gamma = random.uniform(0.1, 0.5)
beta  = random.uniform(0.1, 0.5)
opt   = Adam(lr=LR)

hist_energy = []
hist_gamma  = []
hist_beta   = []

print(f"\n  [QAOA Training]  γ₀={gamma:.3f}  β₀={beta:.3f}")
print(f"  {'Epoch':>6}  {'⟨E⟩':>8}  {'γ':>8}  {'β':>8}")

for epoch in range(EPOCHS):
    e_avg, counts = expected_energy(gamma, beta)
    hist_energy.append(e_avg)
    hist_gamma.append(gamma)
    hist_beta.append(beta)

    dg, db = psr_gradient(gamma, beta)
    gamma, beta = opt.step([gamma, beta], [dg, db])

    if epoch % 6 == 0 or epoch == EPOCHS - 1:
        print(f"  {epoch:>6}  {e_avg:>8.4f}  {gamma:>8.4f}  {beta:>8.4f}")

# Extract QAOA best sample (most frequent low-energy bitstring)
_, final_counts = expected_energy(gamma, beta, shots=1024)
best_qaoa_e = float('inf')
best_qaoa_b = None
for bitstr, cnt in final_counts.items():
    b = bits_from_str(bitstr.zfill(N))
    e = qubo_energy(b)
    if e < best_qaoa_e:
        best_qaoa_e, best_qaoa_b = e, b
qaoa_assets = [ASSETS[i] for i in range(N) if best_qaoa_b[i]]
print(f"\n  [QAOA Final]   Best sample: {qaoa_assets}  |  Energy: {best_qaoa_e:.4f}")

# Summary
print("\n" + "=" * 64)
print(f"  {'Method':<22} {'Portfolio':<22} {'Energy':>8}")
print(f"  {'-'*22} {'-'*22} {'-'*8}")
print(f"  {'Brute Force (exact)':<22} {str(bf_assets):<22} {bf_energy:>8.4f}")
print(f"  {'Simul. Annealing':<22} {str(sa_assets):<22} {sa_energy:>8.4f}")
print(f"  {'QAOA (quantum)':<22} {str(qaoa_assets):<22} {best_qaoa_e:>8.4f}")
print("=" * 64)

# ─────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────
fig = plt.figure(figsize=(16, 11), facecolor='#0d1117')
fig.suptitle('D-Wave-Style QUBO Portfolio Optimizer  |  QAOA vs SA vs Brute Force',
             fontsize=14, color='white', fontweight='bold', y=0.98)

gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.40)
BG  = '#161b22'; FG = '#c9d1d9'; GR = '#21262d'
ex  = list(range(EPOCHS))

def sty(ax, title, xl, yl):
    ax.set_facecolor(BG)
    ax.set_title(title, color=FG, fontsize=10, pad=7)
    ax.set_xlabel(xl, color=FG, fontsize=8)
    ax.set_ylabel(yl, color=FG, fontsize=8)
    ax.tick_params(colors=FG, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(GR)
    ax.grid(True, linestyle='--', alpha=0.35, color=GR)

# ── Panel 1: QAOA ⟨E⟩ convergence ──────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(ex, hist_energy, color='#58a6ff', lw=2, label='QAOA ⟨E⟩')
ax1.axhline(y=bf_energy, color='#3fb950', lw=1.5, linestyle='--', label=f'Optimal E={bf_energy:.3f}')
ax1.fill_between(ex, hist_energy, alpha=0.15, color='#58a6ff')
sty(ax1, 'QAOA Expected Energy Convergence', 'Epoch', '⟨E⟩')
ax1.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# ── Panel 2: γ and β parameter evolution ────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(ex, hist_gamma, color='#e3b341', lw=2, label='γ (phase)')
ax2.plot(ex, hist_beta,  color='#d2a8ff', lw=2, label='β (mixer)')
sty(ax2, 'QAOA Parameter Evolution (γ, β)', 'Epoch', 'Radians')
ax2.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# ── Panel 3: All 16 portfolios energy landscape ──────────────
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor(BG)
energies_all = [e for e, _ in bf_all]
labels_all   = [''.join(str(b) for b in bits) for _, bits in bf_all]
bar_colors   = []
for e, bits in bf_all:
    if bits == bf_bits:
        bar_colors.append('#3fb950')   # optimal = green
    elif e <= bf_energy + 0.05:
        bar_colors.append('#e3b341')   # near-optimal = yellow
    else:
        bar_colors.append('#30363d')   # rest = grey
ax3.bar(range(len(energies_all)), energies_all,
        color=bar_colors, edgecolor=BG, linewidth=0.3)
ax3.axhline(y=bf_energy, color='#3fb950', lw=1, linestyle='--', alpha=0.7)
ax3.set_xticks(range(len(labels_all)))
ax3.set_xticklabels(labels_all, color=FG, fontsize=5.5, rotation=90)
sty(ax3, 'Full QUBO Landscape  (green=optimal)', 'Portfolio (bitstring)', 'Energy')

# ── Panel 4: Simulated annealing cooling curve ───────────────
ax4 = fig.add_subplot(gs[1, 0])
sa_x = [i * (2000 // 50) for i in range(len(sa_hist))]
ax4.plot(sa_x, sa_hist, color='#f85149', lw=2, label='SA Energy')
ax4.axhline(y=bf_energy, color='#3fb950', lw=1.5, linestyle='--',
            label=f'Optimal={bf_energy:.3f}')
ax4.fill_between(sa_x, sa_hist, alpha=0.15, color='#f85149')
sty(ax4, 'Simulated Annealing Cooling Curve', 'Step', 'Energy')
ax4.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# ── Panel 5: QAOA final probability distribution ─────────────
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor(BG)
sorted_counts = sorted(final_counts.items(),
                       key=lambda kv: qubo_energy(bits_from_str(kv[0].zfill(N))))
top_states  = sorted_counts[:8]   # top 8 by energy
ts_labels   = [s.zfill(N) for s, _ in top_states]
ts_probs    = [c/1024 for _, c in top_states]
ts_energies = [qubo_energy(bits_from_str(s.zfill(N))) for s, _ in top_states]
ts_colors   = ['#3fb950' if s.zfill(N) == ''.join(str(b) for b in bf_bits)
               else '#58a6ff' for s, _ in top_states]
bars = ax5.bar(range(len(ts_labels)), ts_probs,
               color=ts_colors, edgecolor=BG, linewidth=0.4)
ax5.set_xticks(range(len(ts_labels)))
ax5.set_xticklabels(ts_labels, color=FG, fontsize=7.5, rotation=45)
sty(ax5, 'QAOA Sampling Distribution\n(green=optimal state)', 'Portfolio', 'Probability')

# ── Panel 6: Return vs Risk scatter for all portfolios ───────
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor(BG)
for mask in range(1 << N):
    bits = [(mask >> i) & 1 for i in range(N)]
    if sum(bits) == 0:
        continue
    ret  =  sum(RETURNS[i] * bits[i] for i in range(N))
    risk = math.sqrt(sum(COV[i][j] * bits[i] * bits[j]
                         for i in range(N) for j in range(N)))
    e    = qubo_energy(bits)
    color = '#3fb950' if bits == bf_bits else \
            '#e3b341' if e <= bf_energy + 0.1 else '#30363d'
    size  = 90 if bits == bf_bits else 35
    ax6.scatter(risk, ret, color=color, s=size, zorder=3,
                edgecolors='white' if bits == bf_bits else 'none', linewidths=0.8)

# Mark QAOA result
if best_qaoa_b:
    r = sum(RETURNS[i] * best_qaoa_b[i] for i in range(N))
    v = math.sqrt(sum(COV[i][j]*best_qaoa_b[i]*best_qaoa_b[j]
                      for i in range(N) for j in range(N)))
    ax6.scatter(v, r, color='#58a6ff', s=100, marker='D',
                zorder=4, edgecolors='white', linewidths=0.8, label='QAOA result')

from matplotlib.lines import Line2D
legend_els = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor='#3fb950', markersize=8, label='Optimal'),
    Line2D([0],[0], marker='o', color='w', markerfacecolor='#e3b341', markersize=8, label='Near-optimal'),
    Line2D([0],[0], marker='D', color='w', markerfacecolor='#58a6ff', markersize=8, label='QAOA pick'),
]
ax6.legend(handles=legend_els, facecolor=BG, labelcolor=FG, fontsize=8)
sty(ax6, 'Risk–Return Landscape  (all portfolios)', 'Portfolio Risk (σ)', 'Expected Return')

plt.savefig('/mnt/user-data/outputs/qubo_portfolio.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
print("\n  Dashboard saved → qubo_portfolio.png")
plt.show()
