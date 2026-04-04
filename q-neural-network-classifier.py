"""
Quantum Neural Network (QNN) Binary Classifier
===============================================
Task    : Classify 2D points as Class 0 or Class 1 (two Gaussian clusters)
Encoding: Amplitude encoding — x1→RY, x2→RZ on 1 qubit
Ansatz  : 2 trainable layers: RY(θ)→RZ(φ) × 2
Decision: P(|0⟩) > 0.5 → Class 0, else Class 1
Loss    : Binary cross-entropy
Gradient: Parameter Shift Rule
Optimizer: Adam

Speed Design:
  - 1 qubit, 4 trainable params → 8 PSR evals per gradient
  - Dataset: 24 points (small but learnable)
  - SHOTS = 128 (low noise, fast)
  - 40 epochs
  Estimated runtime: ~20–35 seconds
"""

from microqiskit import QuantumCircuit, simulate
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math, random

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
SHOTS   = 128
EPOCHS  = 40
LR      = 0.20
SEED    = 42
random.seed(SEED)

# ─────────────────────────────────────────
# DATASET  — two Gaussian blobs in 2D, normalised to [0, π]
# Class 0: centred bottom-left  Class 1: centred top-right
# ─────────────────────────────────────────
def gauss(mu, sigma):
    # Box-Muller (no numpy)
    u1 = max(random.random(), 1e-12)
    u2 = random.random()
    z  = math.sqrt(-2*math.log(u1)) * math.cos(2*math.pi*u2)
    return mu + sigma * z

def make_dataset(n_per_class=12, sigma=0.18):
    data = []
    for _ in range(n_per_class):   # Class 0 — bottom-left
        data.append((gauss(0.25, sigma), gauss(0.25, sigma), 0))
    for _ in range(n_per_class):   # Class 1 — top-right
        data.append((gauss(0.75, sigma), gauss(0.75, sigma), 1))
    random.shuffle(data)
    return data

def scale(x, lo=0.0, hi=1.0):
    """Scale raw feature x ∈ [lo,hi] → angle ∈ [0, π]."""
    return max(0.0, min(math.pi, (x - lo) / (hi - lo) * math.pi))

dataset = make_dataset()
# Raw coordinate range for plotting
raw_range = (0.0, 1.0)

# ─────────────────────────────────────────
# QNN CIRCUIT
# ─────────────────────────────────────────
def build_qnn(x1, x2, params):
    """
    Input encoding:  RY(π·x1) RZ(π·x2)
    Trainable layer: RY(θ0) RZ(θ1) RY(θ2) RZ(θ3)
    """
    qc = QuantumCircuit(1, 1)
    # Encode features
    qc.ry(scale(x1) , 0)
    qc.rz(scale(x2) , 0)
    # Trainable params
    qc.ry(params[0], 0)
    qc.rz(params[1], 0)
    qc.ry(params[2], 0)
    qc.rz(params[3], 0)
    qc.measure(0, 0)
    return qc

def predict_prob(x1, x2, params, shots=SHOTS):
    """Returns P(class=1) = P(measure |1⟩)."""
    qc = build_qnn(x1, x2, params)
    counts = simulate(qc, shots=shots, get='counts')
    return counts.get('1', 0) / shots

# ─────────────────────────────────────────
# LOSS  — Binary Cross-Entropy
# ─────────────────────────────────────────
def bce(p, y, eps=1e-7):
    p = max(eps, min(1-eps, p))
    return -(y * math.log(p) + (1-y) * math.log(1-p))

def dataset_loss(params, data):
    return sum(bce(predict_prob(x1,x2,params), y) for x1,x2,y in data) / len(data)

# ─────────────────────────────────────────
# PARAMETER SHIFT RULE  (∂ BCE / ∂ θᵢ)
# ─────────────────────────────────────────
def psr_gradient(x1, x2, label, params):
    """Exact gradient for one sample via PSR."""
    shift = math.pi / 2
    grads = []
    p0 = predict_prob(x1, x2, params)
    p0 = max(1e-7, min(1-1e-7, p0))
    for i in range(len(params)):
        pp = params[:]; pm = params[:]
        pp[i] += shift; pm[i] -= shift
        p_plus  = predict_prob(x1, x2, pp)
        p_minus = predict_prob(x1, x2, pm)
        dp_dtheta = (p_plus - p_minus) / 2.0
        # Chain rule through BCE
        d_bce = -label/p0 + (1-label)/(1-p0)
        grads.append(d_bce * dp_dtheta)
    return grads

def batch_gradient(params, data):
    """Average PSR gradient over full dataset."""
    total = [0.0] * len(params)
    for x1, x2, y in data:
        g = psr_gradient(x1, x2, y, params)
        for i in range(len(params)):
            total[i] += g[i]
    return [g / len(data) for g in total]

# ─────────────────────────────────────────
# ADAM OPTIMIZER
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
            out[i] -= self.lr * mh / (math.sqrt(vh) + self.eps)  # descent
        return out

# ─────────────────────────────────────────
# TRAINING
# ─────────────────────────────────────────
params    = [random.uniform(-0.5, 0.5) for _ in range(4)]
optimizer = Adam(4, lr=LR)

def accuracy(params, data):
    correct = sum(
        1 for x1,x2,y in data
        if (predict_prob(x1,x2,params,shots=128) > 0.5) == bool(y)
    )
    return correct / len(data)

print("=" * 58)
print("  Quantum Neural Network  —  Binary Classifier")
print("=" * 58)
print(f"  Dataset: {len(dataset)} points (2 Gaussian clusters)")
print(f"  Circuit: 1 qubit | 4 params | PSR gradients | Adam")
print(f"  Loss: Binary Cross-Entropy  |  Epochs: {EPOCHS}")
print("=" * 58)

hist_loss, hist_acc = [], []

for epoch in range(EPOCHS):
    loss = dataset_loss(params, dataset)
    acc  = accuracy(params, dataset)
    hist_loss.append(loss)
    hist_acc.append(acc * 100)

    grads  = batch_gradient(params, dataset)
    params = optimizer.step(params, grads)

    if epoch % 8 == 0 or epoch == EPOCHS - 1:
        print(f"  Epoch {epoch:>3} | Loss: {loss:.4f} | Accuracy: {acc*100:.1f}%")

print()
print(f"  Final Accuracy : {hist_acc[-1]:.1f}%")
print(f"  Final Loss     : {hist_loss[-1]:.4f}")
print(f"  Params         : {[round(p,3) for p in params]}")
print("=" * 58)

# ─────────────────────────────────────────
# DECISION BOUNDARY  (coarse grid, fast)
# ─────────────────────────────────────────
GRID_RES = 18   # Keep low for speed
xs = [i / (GRID_RES-1) for i in range(GRID_RES)]
grid_probs = []
for gx2 in xs:
    row = []
    for gx1 in xs:
        row.append(predict_prob(gx1, gx2, params, shots=64))
    grid_probs.append(row)

# ─────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────
fig = plt.figure(figsize=(14, 9), facecolor='#0d1117')
fig.suptitle('Quantum Neural Network — Binary Classification Dashboard',
             fontsize=14, color='white', fontweight='bold', y=0.98)

gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.48, wspace=0.38)
BG  = '#161b22'; FG  = '#c9d1d9'; GR  = '#21262d'
ex  = list(range(EPOCHS))

def sty(ax, title, xl, yl):
    ax.set_facecolor(BG)
    ax.set_title(title, color=FG, fontsize=10, pad=7)
    ax.set_xlabel(xl, color=FG, fontsize=8)
    ax.set_ylabel(yl, color=FG, fontsize=8)
    ax.tick_params(colors=FG, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(GR)
    ax.grid(True, linestyle='--', alpha=0.35, color=GR)

# Panel 1: Loss curve
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(ex, hist_loss, color='#f85149', lw=2, label='BCE Loss')
ax1.fill_between(ex, hist_loss, alpha=0.15, color='#f85149')
sty(ax1, 'Training Loss (BCE)', 'Epoch', 'Loss')
ax1.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# Panel 2: Accuracy curve
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(ex, hist_acc, color='#3fb950', lw=2, label='Accuracy')
ax2.axhline(y=100, color='#8b949e', lw=0.8, linestyle='--')
ax2.set_ylim(0, 108)
sty(ax2, 'Training Accuracy (%)', 'Epoch', 'Accuracy %')
ax2.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# Panel 3: Decision boundary heatmap
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor(BG)
im = ax3.imshow(grid_probs, origin='lower', extent=[0,1,0,1],
                aspect='auto', cmap='RdYlGn', vmin=0, vmax=1, alpha=0.75)
c0 = [(x1,x2) for x1,x2,y in dataset if y==0]
c1 = [(x1,x2) for x1,x2,y in dataset if y==1]
ax3.scatter([p[0] for p in c0],[p[1] for p in c0],
            c='#f85149', edgecolors='white', s=55, zorder=3, label='Class 0')
ax3.scatter([p[0] for p in c1],[p[1] for p in c1],
            c='#3fb950', edgecolors='white', s=55, zorder=3, label='Class 1')
ax3.contour([[grid_probs[j][i] for i in range(GRID_RES)] for j in range(GRID_RES)],
             levels=[0.5], colors='#e3b341', linewidths=1.5,
             extent=[0,1,0,1])
ax3.set_title('Decision Boundary  (yellow = boundary)', color=FG, fontsize=10, pad=7)
ax3.set_xlabel('Feature x₁', color=FG, fontsize=8)
ax3.set_ylabel('Feature x₂', color=FG, fontsize=8)
ax3.tick_params(colors=FG, labelsize=8)
for sp in ax3.spines.values(): sp.set_edgecolor(GR)
ax3.legend(facecolor=BG, labelcolor=FG, fontsize=8, loc='upper left')
plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04, label='P(Class 1)'
             ).ax.tick_params(colors=FG, labelsize=7)

# Panel 4: Per-sample predicted probability (final model)
ax4 = fig.add_subplot(gs[1, 0:2])
final_probs = [predict_prob(x1,x2,params,shots=256) for x1,x2,_ in dataset]
labels      = [y for _,_,y in dataset]
colors_dot  = ['#3fb950' if p>0.5 and y==1 or p<=0.5 and y==0
               else '#f85149' for p,y in zip(final_probs,labels)]
ax4.bar(range(len(dataset)), final_probs,
        color=colors_dot, edgecolor=BG, linewidth=0.5)
ax4.axhline(y=0.5, color='#e3b341', lw=1.5, linestyle='--', label='Decision threshold')
ax4.scatter([i for i,y in enumerate(labels) if y==1],
            [-0.03]*sum(labels), marker='^', color='#3fb950', s=30, zorder=5, label='True class 1')
ax4.scatter([i for i,y in enumerate(labels) if y==0],
            [-0.03]*(len(labels)-sum(labels)), marker='v', color='#f85149',
            s=30, zorder=5, label='True class 0')
ax4.set_ylim(-0.1, 1.1)
sty(ax4, 'Per-Sample P(Class 1) — Green=correct, Red=misclassified', 'Sample', 'P(Class 1)')
ax4.legend(facecolor=BG, labelcolor=FG, fontsize=8)

# Panel 5: Param evolution proxy (show final learned params as bar chart)
ax5 = fig.add_subplot(gs[1, 2])
param_names = ['θ₀ (RY)', 'θ₁ (RZ)', 'θ₂ (RY)', 'θ₃ (RZ)']
bar_colors  = ['#58a6ff','#d2a8ff','#58a6ff','#d2a8ff']
ax5.bar(param_names, params, color=bar_colors, edgecolor=BG, linewidth=0.5)
ax5.axhline(y=0, color='#8b949e', lw=0.8)
sty(ax5, 'Final Learned Parameters (radians)', 'Param', 'Value (rad)')
for tick in ax5.get_xticklabels():
    tick.set_color(FG); tick.set_fontsize(8)

plt.savefig('/mnt/user-data/outputs/qnn_dashboard.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
print("\n  Dashboard saved → qnn_dashboard.png")
plt.show()
