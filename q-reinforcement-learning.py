"""
Quantum Reinforcement Learning (QRL) — REINFORCE with Quantum Policy Network
=============================================================================
Environment : 1D Corridor  (6 cells, leftmost = trap, rightmost = goal)
              [ TRAP | 0 | 1 | 2 | 3 | GOAL ]
              Agent starts at cell 2, picks LEFT or RIGHT each step.
              Reward: +1.0 at goal, -1.0 at trap, -0.05 step penalty.

Quantum Policy Network:
  - 1 qubit per decision
  - State is angle-encoded → RY(s_angle)
  - 3 trainable params: RZ(θ₀) → RY(θ₁) → RZ(θ₂)
  - P(action=RIGHT) = P(measure |0⟩)

Gradient Method : Parameter Shift Rule on log-probability
Optimizer       : Adam
Algorithm       : REINFORCE with reward-to-go baseline

Speed Design    : Gradient computed once per BATCH (not per step).
                  Trajectory sampling uses 1 shot (no wasted simulation).
                  Only 3 params → 6 PSR circuit evals per gradient.
                  Total runtime: ~15–30 seconds.
"""

from microqiskit import QuantumCircuit, simulate
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math, random

# ──────────────────────────────────────────────
# CONFIG  (tuned for speed + quality)
# ──────────────────────────────────────────────
SHOTS        = 256    # For probability estimation (gradient evals)
N_CELLS      = 6      # Grid cells: indices 0..5
GOAL         = 5
TRAP         = 0
START        = 2
MAX_STEPS    = 12     # Max steps per episode before timeout
N_EPOCHS     = 35     # Training epochs (each = one gradient update)
EPISODES_PER_EPOCH = 8   # Trajectories sampled per epoch
GAMMA        = 0.95   # Discount factor
SEED         = 7

random.seed(SEED)

# ──────────────────────────────────────────────
# ENVIRONMENT
# ──────────────────────────────────────────────
def state_to_angle(state):
    """Encode discrete state as rotation angle in [0, π]."""
    return (state / (N_CELLS - 1)) * math.pi

def step_env(state, action):
    """action: 0=RIGHT(+1), 1=LEFT(-1). Returns (next_state, reward, done)."""
    next_state = state + (1 if action == 0 else -1)
    if next_state >= N_CELLS:   # Overshot goal — clip to goal
        next_state = GOAL
    if next_state == GOAL:
        return next_state, +1.0, True
    if next_state <= TRAP:
        return TRAP, -1.0, True
    return next_state, -0.05, False   # Small step penalty

# ──────────────────────────────────────────────
# QUANTUM POLICY NETWORK
# ──────────────────────────────────────────────
def build_policy_circuit(state, params):
    """
    Circuit:
      RY(state_angle)  — encode state
      RZ(params[0])    — trainable rotation
      RY(params[1])    — trainable rotation
      RZ(params[2])    — trainable rotation
      measure
    """
    qc = QuantumCircuit(1, 1)
    qc.ry(state_to_angle(state), 0)
    qc.rz(params[0], 0)
    qc.ry(params[1], 0)
    qc.rz(params[2], 0)
    qc.measure(0, 0)
    return qc

def get_prob_right(state, params, shots=SHOTS):
    """P(action=RIGHT) = P(measure 0)."""
    qc = build_policy_circuit(state, params)
    counts = simulate(qc, shots=shots, get='counts')
    return counts.get('0', 0) / shots

def sample_action(state, params):
    """Sample action from policy (1 shot = fast)."""
    qc = build_policy_circuit(state, params)
    counts = simulate(qc, shots=1, get='counts')
    return 0 if '0' in counts else 1   # 0=RIGHT, 1=LEFT

# ──────────────────────────────────────────────
# PARAMETER SHIFT RULE — on log π(a|s)
# For action a=0 (RIGHT): log π = log P(0|s,θ)
# For action a=1 (LEFT):  log π = log(1 - P(0|s,θ))
# ──────────────────────────────────────────────
def log_prob_grad(state, action, params):
    """
    ∂ log π(a|s) / ∂θᵢ via PSR.
    Returns list of gradients, one per param.
    """
    shift = math.pi / 2
    grads = []
    p_base = get_prob_right(state, params)
    p_base = max(p_base, 1e-6)   # Avoid log(0)

    for i in range(len(params)):
        p_plus_params  = params[:]
        p_minus_params = params[:]
        p_plus_params[i]  += shift
        p_minus_params[i] -= shift

        dp = (get_prob_right(state, p_plus_params) -
              get_prob_right(state, p_minus_params)) / 2.0

        # Chain rule: d/dθ log π(a|s)
        if action == 0:   # RIGHT → π = P(0)
            grads.append(dp / p_base)
        else:             # LEFT  → π = 1 - P(0)
            p_left = max(1 - p_base, 1e-6)
            grads.append(-dp / p_left)

    return grads

# ──────────────────────────────────────────────
# ADAM OPTIMIZER
# ──────────────────────────────────────────────
class Adam:
    def __init__(self, n, lr=0.18, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps = lr, b1, b2, eps
        self.m, self.v, self.t = [0.]*n, [0.]*n, 0

    def step(self, params, grads):
        self.t += 1
        new = params[:]
        for i in range(len(params)):
            self.m[i] = self.b1*self.m[i] + (1-self.b1)*grads[i]
            self.v[i] = self.b2*self.v[i] + (1-self.b2)*grads[i]**2
            mh = self.m[i] / (1 - self.b1**self.t)
            vh = self.v[i] / (1 - self.b2**self.t)
            new[i] += self.lr * mh / (math.sqrt(vh) + self.eps)  # ascent (maximize)
        return new

# ──────────────────────────────────────────────
# COLLECT TRAJECTORIES
# ──────────────────────────────────────────────
def collect_trajectories(params, n_episodes):
    """
    Returns list of episodes.
    Each episode: list of (state, action, reward).
    """
    episodes = []
    for _ in range(n_episodes):
        state = START
        ep = []
        for _ in range(MAX_STEPS):
            action = sample_action(state, params)
            next_state, reward, done = step_env(state, action)
            ep.append((state, action, reward))
            state = next_state
            if done:
                break
        episodes.append(ep)
    return episodes

def compute_returns(episode, gamma=GAMMA):
    """Reward-to-go (discounted return from each timestep onward)."""
    returns = []
    G = 0.0
    for _, _, r in reversed(episode):
        G = r + gamma * G
        returns.insert(0, G)
    return returns

# ──────────────────────────────────────────────
# TRAINING LOOP
# ──────────────────────────────────────────────
params    = [random.uniform(-0.5, 0.5) for _ in range(3)]
optimizer = Adam(3, lr=0.18)

print("=" * 62)
print("  Quantum Reinforcement Learning — 1D Corridor Navigation")
print("=" * 62)
print(f"  Grid: [ TRAP | {'  '.join(str(i) for i in range(1, N_CELLS-1))} | GOAL ]")
print(f"  Start: cell {START}  |  Policy: 1-qubit quantum circuit")
print(f"  Gradient: PSR on log π  |  Optimizer: Adam")
print("=" * 62)

history_reward   = []
history_success  = []
history_steps    = []
history_entropy  = []
policy_snapshots = {}   # epoch → P(RIGHT) per state

for epoch in range(N_EPOCHS):
    # 1. Sample trajectories (cheap: 1 shot per step)
    episodes = collect_trajectories(params, EPISODES_PER_EPOCH)

    # 2. Compute per-episode stats
    ep_rewards = [sum(r for _,_,r in ep) for ep in episodes]
    ep_steps   = [len(ep) for ep in episodes]
    ep_success = [ep[-1][2] > 0.5 for ep in episodes]  # ended at goal

    avg_reward  = sum(ep_rewards) / len(ep_rewards)
    avg_steps   = sum(ep_steps)   / len(ep_steps)
    success_rate = sum(ep_success) / len(ep_success)

    # 3. REINFORCE policy gradient (batch average)
    batch_grads = [0.0] * 3
    total_weight = 0

    for episode in episodes:
        returns = compute_returns(episode)
        baseline = sum(returns) / len(returns)  # per-episode baseline
        for (state, action, _), G in zip(episode, returns):
            advantage = G - baseline
            if abs(advantage) < 1e-6:
                continue
            g = log_prob_grad(state, action, params)
            for i in range(3):
                batch_grads[i] += advantage * g[i]
            total_weight += 1

    if total_weight > 0:
        batch_grads = [g / total_weight for g in batch_grads]

    # 4. Adam update (gradient ASCENT → maximize returns)
    params = optimizer.step(params, batch_grads)

    # 5. Policy entropy (exploration measure)
    probs = [get_prob_right(s, params) for s in range(1, N_CELLS-1)]
    entropy = -sum(p*math.log(p+1e-9) + (1-p)*math.log(1-p+1e-9)
                   for p in probs) / len(probs)

    history_reward.append(avg_reward)
    history_success.append(success_rate * 100)
    history_steps.append(avg_steps)
    history_entropy.append(entropy)

    # Snapshot policy at key epochs
    if epoch in (0, N_EPOCHS//4, N_EPOCHS//2, N_EPOCHS-1):
        policy_snapshots[epoch] = [
            get_prob_right(s, params) for s in range(N_CELLS)
        ]

    if epoch % 5 == 0 or epoch == N_EPOCHS - 1:
        print(f"  Epoch {epoch:>3} | AvgReturn: {avg_reward:+.3f} | "
              f"Success: {success_rate*100:.0f}% | Steps: {avg_steps:.1f} | "
              f"Entropy: {entropy:.3f}")

print()
print("  Final Policy (P(RIGHT) per state):")
for s in range(N_CELLS):
    p = get_prob_right(s, params)
    label = " ← TRAP" if s == TRAP else " ← GOAL" if s == GOAL else ""
    bar = "█" * int(p * 20)
    print(f"    State {s}: {p:.3f}  |{bar:<20}|{label}")
print("=" * 62)

# ──────────────────────────────────────────────
# VISUALIZATION
# ──────────────────────────────────────────────
fig = plt.figure(figsize=(15, 10), facecolor='#0d1117')
fig.suptitle('Quantum RL Dashboard — 1D Corridor Navigation (REINFORCE + PSR)',
             fontsize=14, color='white', fontweight='bold', y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.38)

BG   = '#161b22'
FG   = '#c9d1d9'
GRID = '#21262d'

def style(ax, title, xlabel, ylabel):
    ax.set_facecolor(BG)
    ax.set_title(title, color=FG, fontsize=10, pad=7)
    ax.set_xlabel(xlabel, color=FG, fontsize=8)
    ax.set_ylabel(ylabel, color=FG, fontsize=8)
    ax.tick_params(colors=FG, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(GRID)
    ax.grid(True, linestyle='--', alpha=0.35, color=GRID)

epochs_x = list(range(N_EPOCHS))

# Panel 1: Average return
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(epochs_x, history_reward, color='#3fb950', lw=2)
ax1.fill_between(epochs_x, history_reward, alpha=0.15, color='#3fb950')
ax1.axhline(y=0, color='#8b949e', lw=0.8, linestyle='--')
style(ax1, 'Average Episode Return', 'Epoch', 'Return')

# Panel 2: Success rate
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(epochs_x, history_success, color='#58a6ff', lw=2)
ax2.fill_between(epochs_x, history_success, alpha=0.15, color='#58a6ff')
ax2.set_ylim(0, 105)
style(ax2, 'Goal Success Rate (%)', 'Epoch', 'Success %')

# Panel 3: Policy entropy
ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(epochs_x, history_entropy, color='#e3b341', lw=2)
ax3.fill_between(epochs_x, history_entropy, alpha=0.15, color='#e3b341')
style(ax3, 'Policy Entropy (Exploration)', 'Epoch', 'Entropy')

# Panel 4: Average steps per episode
ax4 = fig.add_subplot(gs[1, 0])
ax4.plot(epochs_x, history_steps, color='#d2a8ff', lw=2)
ax4.fill_between(epochs_x, history_steps, alpha=0.15, color='#d2a8ff')
ax4.axhline(y=N_CELLS - START, color='#f85149', lw=1, linestyle='--',
            label=f'Optimal = {N_CELLS-1-START} steps')
ax4.legend(facecolor=BG, labelcolor=FG, fontsize=7)
style(ax4, 'Avg Steps to Termination', 'Epoch', 'Steps')

# Panel 5: Policy heatmap evolution (P(RIGHT) per state over snapshots)
ax5 = fig.add_subplot(gs[1, 1])
snap_epochs = sorted(policy_snapshots.keys())
snap_labels = [f'E{e}' for e in snap_epochs]
data = [[policy_snapshots[e][s] for s in range(N_CELLS)] for e in snap_epochs]
im = ax5.imshow(data, aspect='auto', cmap='RdYlGn', vmin=0, vmax=1,
                origin='upper')
ax5.set_xticks(range(N_CELLS))
ax5.set_xticklabels(['TRAP','1','2','3','4','GOAL'], color=FG, fontsize=8)
ax5.set_yticks(range(len(snap_epochs)))
ax5.set_yticklabels(snap_labels, color=FG, fontsize=8)
ax5.set_title('Policy Evolution  P(RIGHT|state)\nGreen=prefer right, Red=prefer left',
              color=FG, fontsize=9, pad=7)
for sp in ax5.spines.values(): sp.set_edgecolor(GRID)
plt.colorbar(im, ax=ax5, fraction=0.046, pad=0.04).ax.tick_params(colors=FG)

# Panel 6: Final policy bar chart
ax6 = fig.add_subplot(gs[1, 2])
final_probs = policy_snapshots[N_EPOCHS - 1]
colors = ['#f85149', '#58a6ff', '#58a6ff', '#58a6ff', '#58a6ff', '#3fb950']
bars = ax6.bar(range(N_CELLS), final_probs, color=colors, edgecolor=GRID, linewidth=0.8)
ax6.axhline(y=0.5, color='#8b949e', lw=1, linestyle='--', label='Random = 0.5')
ax6.set_xticks(range(N_CELLS))
ax6.set_xticklabels(['TRAP','1','2','3','4','GOAL'], color=FG, fontsize=8)
ax6.set_ylim(0, 1.1)
ax6.legend(facecolor=BG, labelcolor=FG, fontsize=7)
style(ax6, 'Final Learned Policy P(RIGHT|state)', 'State', 'P(action=RIGHT)')

plt.savefig('/mnt/user-data/outputs/qrl_dashboard.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
print("\n  Dashboard saved → qrl_dashboard.png")
plt.show()
