"""
Quantum Boltzmann Machine (QBM)
================================
Task    : Learn to reproduce a target 2-bit probability distribution.

Fixes vs v1:
  - KL gradient now uses proper chain rule:
      ∂KL/∂θᵢ = -Σ p_target(s)/q(s;θ) * (q(θ+π/2) - q(θ-π/2))/2
  - Panels 4 & 5: completely rewritten bar chart positioning
  - Lower LR + higher SHOTS for stable convergence
"""

from microqiskit import QuantumCircuit, simulate
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math, random

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
SHOTS_TRAIN = 512
SHOTS_EVAL  = 256
SHOTS_FINAL = 1024
EPOCHS      = 50
LR          = 0.08
SEED        = 13
TARGET      = "biased"   # "biased" | "majority" | "uniform"
random.seed(SEED)

TARGETS = {
    "biased"  : {"00": 0.55, "01": 0.10, "10": 0.10, "11": 0.25},
    "majority": {"00": 0.60, "01": 0.05, "10": 0.05, "11": 0.30},
    "uniform" : {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25},
}
STATES      = ["00", "01", "10", "11"]
target_dist = TARGETS[TARGET]

# ─────────────────────────────────────────
# QBM CIRCUIT
# ─────────────────────────────────────────
def build_qbm(params):
    qc = QuantumCircuit(2, 2)
    qc.ry(params[0], 0)
    qc.ry(params[1], 1)
    qc.cx(0, 1)
    qc.rz(params[2], 1)
    qc.cx(0, 1)
    qc.ry(params[3], 0)
    qc.ry(params[4], 1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc

def get_model_dist(params, shots=SHOTS_EVAL):
    qc     = build_qbm(params)
    counts = simulate(qc, shots=shots, get='counts')
    return {s: counts.get(s, 0) / shots for s in STATES}

# ─────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────
def kl_divergence(target, model, eps=1e-7):
    return sum(target[s] * math.log((target[s]+eps) / (model[s]+eps))
               for s in STATES)

def total_variation(target, model):
    return 0.5 * sum(abs(target[s] - model[s]) for s in STATES)

# ─────────────────────────────────────────
# CORRECT KL GRADIENT via PSR + chain rule
# ∂KL/∂θᵢ = -Σ P(s)/Q(s;θ) * ∂Q(s;θ)/∂θᵢ
# ─────────────────────────────────────────
def kl_gradient(params):
    shift = math.pi / 2
    q     = get_model_dist(params, shots=SHOTS_TRAIN)
    grads = []
    for i in range(len(params)):
        pp = params[:]; pm = params[:]
        pp[i] += shift; pm[i] -= shift
        q_plus  = get_model_dist(pp,  shots=SHOTS_TRAIN)
        q_minus = get_model_dist(pm,  shots=SHOTS_TRAIN)
        grad = 0.0
        for s in STATES:
            dq   = (q_plus[s] - q_minus[s]) / 2.0
            denom = max(q[s], 1e-7)
            grad -= target_dist[s] * dq / denom
        grads.append(grad)
    return grads

# ─────────────────────────────────────────
# ADAM
# ─────────────────────────────────────────
class Adam:
    def __init__(self, n, lr=LR, b1=0.9, b2=0.999, eps=1e-8):
        self.lr,self.b1,self.b2,self.eps = lr,b1,b2,eps
        self.m,self.v,self.t = [0.]*n,[0.]*n,0

    def step(self, params, grads):
        self.t += 1
        out = params[:]
        for i in range(len(params)):
            self.m[i] = self.b1*self.m[i] + (1-self.b1)*grads[i]
            self.v[i] = self.b2*self.v[i] + (1-self.b2)*grads[i]**2
            mh = self.m[i] / (1 - self.b1**self.t)
            vh = self.v[i] / (1 - self.b2**self.t)
            out[i] -= self.lr * mh / (math.sqrt(vh) + self.eps)
        return out

# ─────────────────────────────────────────
# TRAINING
# ─────────────────────────────────────────
params    = [random.uniform(-math.pi, math.pi) for _ in range(5)]
optimizer = Adam(5, lr=LR)

print("=" * 62)
print("  Quantum Boltzmann Machine  —  Distribution Learning")
print("=" * 62)
print(f"  Target '{TARGET}': " + "  ".join(f"P({s})={target_dist[s]:.2f}" for s in STATES))
print(f"  Circuit: 2 qubits | 5 params | ZZ coupling | PSR | Adam")
print(f"  Epochs: {EPOCHS}  |  LR: {LR}  |  Train shots: {SHOTS_TRAIN}")
print("=" * 62)

hist_kl   = []
hist_tv   = []
hist_dist = {s: [] for s in STATES}
snap_epochs = [0, EPOCHS//4, EPOCHS//2, 3*EPOCHS//4, EPOCHS-1]
snapshots   = {}

for epoch in range(EPOCHS):
    model_dist = get_model_dist(params, shots=SHOTS_EVAL)
    kl  = kl_divergence(target_dist, model_dist)
    tv  = total_variation(target_dist, model_dist)

    hist_kl.append(kl)
    hist_tv.append(tv)
    for s in STATES:
        hist_dist[s].append(model_dist[s])

    if epoch in snap_epochs:
        snapshots[epoch] = dict(model_dist)

    grads  = kl_gradient(params)
    params = optimizer.step(params, grads)

    if epoch % 10 == 0 or epoch == EPOCHS - 1:
        dist_str = "  ".join(f"P({s})={model_dist[s]:.3f}" for s in STATES)
        print(f"  Epoch {epoch:>3} | KL:{kl:.4f} | TV:{tv:.4f} | {dist_str}")

final_dist = get_model_dist(params, shots=SHOTS_FINAL)
print()
print("  Final comparison (1024 shots):")
print(f"  {'State':<8} {'Target':>8} {'Learned':>8} {'Error':>8}")
for s in STATES:
    err = abs(target_dist[s] - final_dist[s])
    print(f"  {s:<8} {target_dist[s]:>8.3f} {final_dist[s]:>8.3f} {err:>8.4f}")
print(f"\n  Final KL : {kl_divergence(target_dist, final_dist):.4f}  (ideal = 0.0)")
print(f"  Final TV : {total_variation(target_dist, final_dist):.4f}  (ideal = 0.0)")
print("=" * 62)

# ─────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────
fig = plt.figure(figsize=(15, 10), facecolor='#0d1117')
fig.suptitle(f"Quantum Boltzmann Machine  —  Target: '{TARGET}' distribution",
             fontsize=14, color='white', fontweight='bold', y=0.98)

gs     = gridspec.GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.40)
BG     = '#161b22'; FG = '#c9d1d9'; GR = '#21262d'
ex     = list(range(EPOCHS))
COLORS = {'00': '#58a6ff', '01': '#3fb950', '10': '#e3b341', '11': '#d2a8ff'}

def sty(ax, title, xl, yl):
    ax.set_facecolor(BG)
    ax.set_title(title, color=FG, fontsize=10, pad=7)
    ax.set_xlabel(xl, color=FG, fontsize=8)
    ax.set_ylabel(yl, color=FG, fontsize=8)
    ax.tick_params(colors=FG, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(GR)
    ax.grid(True, linestyle='--', alpha=0.35, color=GR)

# Panel 1: KL curve
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(ex, hist_kl, color='#f85149', lw=2, label='KL Divergence')
ax1.fill_between(ex, hist_kl, alpha=0.15, color='#f85149')
ax1.axhline(y=0, color='#8b949e', lw=0.8, linestyle='--')
sty(ax1, 'KL Divergence  KL(target ‖ model)', 'Epoch', 'KL')
ax1.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# Panel 2: Total variation
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(ex, hist_tv, color='#e3b341', lw=2, label='Total Variation')
ax2.fill_between(ex, hist_tv, alpha=0.15, color='#e3b341')
ax2.set_ylim(0, max(hist_tv) * 1.25 + 0.01)
sty(ax2, 'Total Variation Distance', 'Epoch', 'TV Distance')
ax2.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# Panel 3: Per-state probability curves
ax3 = fig.add_subplot(gs[0, 2])
for s in STATES:
    ax3.plot(ex, hist_dist[s], color=COLORS[s], lw=2, label=f'P({s})')
    ax3.axhline(y=target_dist[s], color=COLORS[s], lw=1, linestyle=':', alpha=0.65)
ax3.set_ylim(-0.02, 0.80)
sty(ax3, 'Probability Convergence  (dotted=target)', 'Epoch', 'Probability')
ax3.legend(facecolor=BG, labelcolor=FG, fontsize=8, loc='upper right')

# ── Panel 4: Grouped snapshot bars ────────────────────────
ax4 = fig.add_subplot(gs[1, 0:2])
ax4.set_facecolor(BG)

snap_keys    = sorted(snapshots.keys())
group_labels = ['Target'] + [f'Ep {e}' for e in snap_keys]
n_groups     = len(group_labels)   # 6
n_states     = len(STATES)         # 4
bar_w        = 0.14
group_span   = n_states * bar_w    # width of one full group of bars

# Centre each group at integer x positions 0,1,2,...
for gi, label in enumerate(group_labels):
    for si, s in enumerate(STATES):
        x = gi + (si - (n_states - 1) / 2.0) * bar_w
        val = target_dist[s] if gi == 0 else snapshots[snap_keys[gi-1]][s]
        ax4.bar(x, val, width=bar_w * 0.88,
                color=COLORS[s], alpha=0.85,
                edgecolor=BG, linewidth=0.4,
                label=f'|{s}⟩' if gi == 0 else None)

ax4.set_xticks(list(range(n_groups)))
ax4.set_xticklabels(group_labels, color=FG, fontsize=8)
ax4.set_ylim(0, 0.80)
ax4.set_title('Distribution Snapshots vs Target', color=FG, fontsize=10, pad=7)
ax4.set_xlabel('Snapshot', color=FG, fontsize=8)
ax4.set_ylabel('Probability', color=FG, fontsize=8)
ax4.tick_params(colors=FG, labelsize=8)
for sp in ax4.spines.values(): sp.set_edgecolor(GR)
ax4.grid(True, linestyle='--', alpha=0.35, color=GR, axis='y')
ax4.legend(facecolor=BG, labelcolor=FG, fontsize=8, loc='upper right')

# ── Panel 5: Final target vs learned ──────────────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor(BG)

bw       = 0.32
state_xs = list(range(len(STATES)))

ax5.bar([x - bw/2 for x in state_xs],
        [target_dist[s] for s in STATES],
        width=bw, color='#58a6ff', alpha=0.85,
        label='Target', edgecolor=BG)
ax5.bar([x + bw/2 for x in state_xs],
        [final_dist[s] for s in STATES],
        width=bw, color='#3fb950', alpha=0.85,
        label='Learned', edgecolor=BG)

ax5.set_xticks(state_xs)
ax5.set_xticklabels([f'|{s}⟩' for s in STATES], color=FG, fontsize=9)
ax5.set_ylim(0, 0.80)
sty(ax5, 'Final: Target vs Learned', 'State', 'Probability')
ax5.legend(facecolor=BG, labelcolor=FG, fontsize=9)

plt.savefig('/mnt/user-data/outputs/qbm_dashboard.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
print("\n  Dashboard saved → qbm_dashboard.png")
plt.show()
