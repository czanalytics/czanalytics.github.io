"""
Quantum Vehicle Routing Problem — Steel Roll Transport Across Europe
=====================================================================
Problem:
  2 steel mill sources in Europe ship heavy steel rolls to 5 customer sites.
  Two trucks with different capacities are available each day.
  Find optimal delivery assignment & routing to minimise total travel distance
  subject to capacity and coverage constraints.

Geography (real European coordinates):
  Source S1: Duisburg, Germany    — major steel hub (ThyssenKrupp)
  Source S2: Kraków, Poland       — ArcelorMittal plant

  T1: Paris,     France           (auto industry customer)
  T2: Milan,     Italy            (manufacturing)
  T3: Vienna,    Austria          (machinery)
  T4: Amsterdam, Netherlands      (port logistics)
  T5: Prague,    Czech Republic   (engineering)

Trucks:
  Truck A (small,  cap=1): single-roll trips, starts from either source
  Truck B (large,  cap=2): combined 2-roll trip, starts from either source

Since 5 deliveries exceed one round's combined capacity (1+2=3),
Truck A makes 3 single trips and Truck B makes one double trip per day.

QUBO encoding (5 qubits):
  xᵢ ∈ {0,1} : delivery i assigned to Truck B (1) or Truck A (0)
  Constraint : exactly 2 deliveries must go to Truck B  →  Σxᵢ = 2

Energy:
  E(x) = α · distance_cost(x)
        + β · (Σxᵢ - 2)²          ← cardinality constraint
        + γ · urgency_cost(x)      ← scenario-specific penalties
        + δ · fuel_cost(x)         ← scenario-specific fuel weights

Three Scenarios:
  1. EFFICIENCY   : minimise total km (α=1.0, β=4.0, γ=0.0, δ=0.0)
  2. PRIORITY     : urgent deliveries to Paris & Milan first (γ=2.5)
  3. FUEL SAVING  : penalise long solo trips, reward truck B use (δ=1.5)

Algorithm:
  QAOA p=1 (γ_qaoa, β_qaoa) trained via PSR + Adam
  Brute-force comparison (2⁵=32 states, instant)
  Simulated Annealing comparison

Speed:
  5 qubits → 32 states, QAOA p=1 → 2 params → 4 PSR evals/step
  25 epochs per scenario → ~100 circuit evals per scenario
  Total: ~15-25 seconds for 3 scenarios
"""

from microqiskit import QuantumCircuit, simulate
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import math, random

# ─────────────────────────────────────────────────────────
# GEOGRAPHY  (longitude, latitude)
# ─────────────────────────────────────────────────────────
SOURCES = {
    "Duisburg": (6.76,  51.43),
    "Kraków":   (19.94, 50.06),
}
TARGETS = {
    "Paris":     (2.35,  48.85),
    "Milan":     (9.19,  45.46),
    "Vienna":    (16.37, 48.21),
    "Amsterdam": (4.90,  52.37),
    "Prague":    (14.42, 50.07),
}
S_NAMES = list(SOURCES.keys())
T_NAMES = list(TARGETS.keys())
N       = len(T_NAMES)   # 5 deliveries = 5 qubits

S_COORD = [SOURCES[s]  for s in S_NAMES]
T_COORD = [TARGETS[t]  for t in T_NAMES]

# Approximate km distance (Haversine lite at 50°N)
def dist_km(p1, p2):
    lon1,lat1 = p1; lon2,lat2 = p2
    dlat = (lat2 - lat1) * 111.0
    dlon = (lon2 - lon1) * math.cos(math.radians((lat1+lat2)/2)) * 111.0
    return math.sqrt(dlat**2 + dlon**2)

# Precompute source→target distance matrix
D = [[dist_km(S_COORD[s], T_COORD[t])
      for t in range(N)] for s in range(2)]

def nearest_source(delivery_idx):
    """Index of closer source for a given delivery."""
    return 0 if D[0][delivery_idx] <= D[1][delivery_idx] else 1

def route_distance_truck_B(b_deliveries):
    """
    Truck B carries 2 rolls: optimal order from best source.
    Tour: source → stop1 → stop2 → return source.
    Both orderings evaluated; best chosen.
    """
    if len(b_deliveries) != 2:
        return 0.0
    i, j = b_deliveries
    # Try both sources
    best = float('inf')
    for s in range(2):
        src = S_COORD[s]
        # Order 1: src→i→j→src
        d1 = (dist_km(src, T_COORD[i]) +
              dist_km(T_COORD[i], T_COORD[j]) +
              dist_km(T_COORD[j], src))
        # Order 2: src→j→i→src
        d2 = (dist_km(src, T_COORD[j]) +
              dist_km(T_COORD[j], T_COORD[i]) +
              dist_km(T_COORD[i], src))
        best = min(best, d1, d2)
    return best

def route_distance_truck_A(a_deliveries):
    """
    Truck A makes one round-trip per delivery from nearest source.
    Total = Σ 2·dist(nearest_source, delivery)
    """
    total = 0.0
    for i in a_deliveries:
        s = nearest_source(i)
        total += 2.0 * D[s][i]
    return total

# ─────────────────────────────────────────────────────────
# QUBO ENERGY  (lower = better)
# ─────────────────────────────────────────────────────────
def qubo_energy(bits, alpha, beta, gamma, delta, urgency, fuel_penalty):
    """
    bits     : list of 0/1, length N
    alpha    : distance weight
    beta     : cardinality penalty weight
    gamma    : urgency weight
    delta    : fuel-saving weight
    urgency  : list of per-delivery urgency bonus costs (scenario 2)
    fuel_penalty: per-delivery fuel cost for solo trips (scenario 3)
    """
    x  = list(bits)
    b_del = [i for i in range(N) if x[i] == 1]   # Truck B deliveries
    a_del = [i for i in range(N) if x[i] == 0]   # Truck A deliveries

    # Distance
    dist  = route_distance_truck_B(b_del) + route_distance_truck_A(a_del)

    # Cardinality: must assign exactly 2 to Truck B
    card  = (sum(x) - 2) ** 2

    # Urgency: penalise urgent deliveries NOT in Truck B (slower solo trips)
    urg   = sum(urgency[i] * (1 - x[i]) for i in range(N))

    # Fuel: reward Truck B combined trips (penalise long solo trips)
    fuel  = sum(fuel_penalty[i] * (1 - x[i]) for i in range(N))

    return alpha * dist + beta * card + gamma * urg + delta * fuel

# ─────────────────────────────────────────────────────────
# BRUTE FORCE
# ─────────────────────────────────────────────────────────
def brute_force(alpha, beta, gamma, delta, urgency, fuel_penalty):
    best_e, best_b = float('inf'), None
    all_results = []
    for mask in range(1 << N):
        b = [(mask >> i) & 1 for i in range(N)]
        e = qubo_energy(b, alpha, beta, gamma, delta, urgency, fuel_penalty)
        all_results.append((e, b[:]))
        if e < best_e:
            best_e, best_b = e, b[:]
    all_results.sort(key=lambda x: x[0])
    return best_e, best_b, all_results

# ─────────────────────────────────────────────────────────
# QAOA CIRCUIT  (p=1, 5 qubits)
# ─────────────────────────────────────────────────────────
def ising_coefficients(alpha, beta, gamma, delta, urgency, fuel_penalty):
    """
    Convert QUBO Q-matrix to Ising h, J coefficients.
    xᵢ = (1 - sᵢ)/2
    """
    # Build Q matrix by numerical differentiation over bits
    h = [0.0] * N
    J = [[0.0]*N for _ in range(N)]

    def E(b): return qubo_energy(b, alpha, beta, gamma, delta, urgency, fuel_penalty)

    # h[i] = (E[eᵢ=1] - E[eᵢ=0]) / 2  — with all others 0
    for i in range(N):
        b1 = [1 if j==i else 0 for j in range(N)]
        b0 = [0]*N
        # Approximate linear term
        h[i] = (E(b1) - E(b0)) / 2.0

    # J[i][j] from cross-terms
    for i in range(N):
        for j in range(i+1, N):
            b11 = [1 if k in (i,j) else 0 for k in range(N)]
            b10 = [1 if k==i else 0 for k in range(N)]
            b01 = [1 if k==j else 0 for k in range(N)]
            b00 = [0]*N
            J[i][j] = (E(b11) - E(b10) - E(b01) + E(b00)) / 4.0

    return h, J

def build_qaoa(g_param, b_param, h, J):
    """QAOA p=1 circuit."""
    qc = QuantumCircuit(N, N)
    # Equal superposition
    for i in range(N):
        qc.h(i)
    # Phase separator: ZZ couplings + Z biases
    for i in range(N):
        for j in range(i+1, N):
            if abs(J[i][j]) > 1e-9:
                qc.cx(i, j)
                qc.rz(2.0 * g_param * J[i][j], j)
                qc.cx(i, j)
    for i in range(N):
        if abs(h[i]) > 1e-9:
            qc.rz(2.0 * g_param * h[i], i)
    # Mixer: RX on each qubit
    for i in range(N):
        qc.rx(2.0 * b_param, i)
    for i in range(N):
        qc.measure(i, i)
    return qc

def expected_energy_qaoa(g_param, b_param, h, J,
                          alpha, beta, gamma, delta, urgency, fuel_penalty,
                          shots=256):
    qc     = build_qaoa(g_param, b_param, h, J)
    counts = simulate(qc, shots=shots, get='counts')
    total  = 0.0
    for bitstr, cnt in counts.items():
        b = [int(c) for c in bitstr.zfill(N)]
        total += qubo_energy(b, alpha, beta, gamma, delta, urgency, fuel_penalty) * cnt
    return total / shots, counts

def psr_gradient(g_param, b_param, h, J,
                 alpha, beta, gamma, delta, urgency, fuel_penalty):
    shift = math.pi / 2
    eg_p,_ = expected_energy_qaoa(g_param+shift, b_param, h, J,
                                   alpha, beta, gamma, delta, urgency, fuel_penalty)
    eg_m,_ = expected_energy_qaoa(g_param-shift, b_param, h, J,
                                   alpha, beta, gamma, delta, urgency, fuel_penalty)
    eb_p,_ = expected_energy_qaoa(g_param, b_param+shift, h, J,
                                   alpha, beta, gamma, delta, urgency, fuel_penalty)
    eb_m,_ = expected_energy_qaoa(g_param, b_param-shift, h, J,
                                   alpha, beta, gamma, delta, urgency, fuel_penalty)
    return (eg_p-eg_m)/2.0, (eb_p-eb_m)/2.0

# ─────────────────────────────────────────────────────────
# SIMULATED ANNEALING
# ─────────────────────────────────────────────────────────
def simulated_annealing(alpha, beta, gamma, delta, urgency, fuel_penalty,
                         n_steps=1500, T0=3.0, T_min=0.01, seed=42):
    random.seed(seed)
    x    = [random.randint(0,1) for _ in range(N)]
    e    = qubo_energy(x, alpha, beta, gamma, delta, urgency, fuel_penalty)
    best_x, best_e = x[:], e
    T    = T0
    alpha_cool = (T_min/T0)**(1.0/n_steps)
    for _ in range(n_steps):
        i     = random.randint(0, N-1)
        xn    = x[:]
        xn[i] ^= 1
        en    = qubo_energy(xn, alpha, beta, gamma, delta, urgency, fuel_penalty)
        if en < e or random.random() < math.exp(-(en-e)/T):
            x, e = xn, en
            if e < best_e:
                best_e, best_x = e, x[:]
        T *= alpha_cool
    return best_e, best_x

# ─────────────────────────────────────────────────────────
# ADAM
# ─────────────────────────────────────────────────────────
class Adam:
    def __init__(self, lr=0.20, b1=0.9, b2=0.999, eps=1e-8):
        self.lr,self.b1,self.b2,self.eps = lr,b1,b2,eps
        self.m,self.v,self.t = [0.,0.],[0.,0.],0

    def reset(self):
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

# ─────────────────────────────────────────────────────────
# SCENARIO DEFINITIONS
# ─────────────────────────────────────────────────────────
# Urgency[i]: extra penalty if delivery i not in Truck B (slower)
# Paris(0), Milan(1) are urgent in scenario 2
# Fuel[i]: fuel penalty for long solo Truck A trips
AVG_DIST = sum(min(D[0][i], D[1][i]) for i in range(N)) / N

SCENARIOS = [
    {
        "name":    "1 · Efficiency",
        "desc":    "Minimise total km — pure distance optimisation",
        "alpha":   1.0 / 300.0,  # normalise distances
        "beta":    4.0,
        "gamma":   0.0,
        "delta":   0.0,
        "urgency": [0.0]*N,
        "fuel":    [0.0]*N,
        "color":   "#58a6ff",
    },
    {
        "name":    "2 · Priority Rush",
        "desc":    "Paris & Milan need same-day delivery — load Truck B with urgents",
        "alpha":   0.5 / 300.0,
        "beta":    4.0,
        "gamma":   2.5,
        "delta":   0.0,
        "urgency": [3.0, 3.0, 0.0, 0.0, 0.0],   # Paris, Milan urgent
        "fuel":    [0.0]*N,
        "color":   "#f85149",
    },
    {
        "name":    "3 · Fuel Saving",
        "desc":    "Penalise long solo trips — reward Truck B combined routes",
        "alpha":   0.6 / 300.0,
        "beta":    4.0,
        "gamma":   0.0,
        "delta":   1.5,
        "urgency": [0.0]*N,
        "fuel":    [D[0][i]/300.0 for i in range(N)],   # proportional to distance
        "color":   "#3fb950",
    },
]

EPOCHS = 25

# ─────────────────────────────────────────────────────────
# RUN ALL SCENARIOS
# ─────────────────────────────────────────────────────────
random.seed(7)
optimizer = Adam(lr=0.22)
results   = []

print("=" * 70)
print("  Quantum VRP — Steel Roll Transport  |  Europe  |  QAOA p=1")
print("=" * 70)
print(f"  Sources : {S_NAMES}")
print(f"  Targets : {T_NAMES}")
print(f"  Truck A (cap=1): single-roll solo trips from nearest source")
print(f"  Truck B (cap=2): combined 2-roll trip, optimal TSP order")
print("=" * 70)

for sc in SCENARIOS:
    a,b_,g,d = sc["alpha"], sc["beta"], sc["gamma"], sc["delta"]
    urg, fuel = sc["urgency"], sc["fuel"]

    print(f"\n  ── Scenario {sc['name']} ──")
    print(f"     {sc['desc']}")

    # Ising coefficients
    h_is, J_is = ising_coefficients(a, b_, g, d, urg, fuel)

    # Brute force
    bf_e, bf_bits, bf_all = brute_force(a, b_, g, d, urg, fuel)
    bf_B = [T_NAMES[i] for i in range(N) if bf_bits[i]==1]
    bf_A = [T_NAMES[i] for i in range(N) if bf_bits[i]==0]

    # Simulated annealing
    sa_e, sa_bits = simulated_annealing(a, b_, g, d, urg, fuel)
    sa_B = [T_NAMES[i] for i in range(N) if sa_bits[i]==1]
    sa_A = [T_NAMES[i] for i in range(N) if sa_bits[i]==0]

    # QAOA
    optimizer.reset()
    gp = random.uniform(0.1, 0.5)
    bp = random.uniform(0.1, 0.5)
    hist_e = []

    for epoch in range(EPOCHS):
        e_avg, counts = expected_energy_qaoa(gp, bp, h_is, J_is,
                                              a, b_, g, d, urg, fuel)
        hist_e.append(e_avg)
        dg, db = psr_gradient(gp, bp, h_is, J_is, a, b_, g, d, urg, fuel)
        gp, bp = optimizer.step([gp, bp], [dg, db])

    # Best QAOA sample
    _, final_counts = expected_energy_qaoa(gp, bp, h_is, J_is,
                                            a, b_, g, d, urg, fuel,
                                            shots=512)
    qa_e  = float('inf')
    qa_bits = None
    for bitstr, cnt in final_counts.items():
        bits = [int(c) for c in bitstr.zfill(N)]
        e    = qubo_energy(bits, a, b_, g, d, urg, fuel)
        if e < qa_e:
            qa_e, qa_bits = e, bits

    qa_B = [T_NAMES[i] for i in range(N) if qa_bits[i]==1]
    qa_A = [T_NAMES[i] for i in range(N) if qa_bits[i]==0]

    # Compute actual km for best solution
    bf_km = (route_distance_truck_B([i for i in range(N) if bf_bits[i]==1]) +
             route_distance_truck_A([i for i in range(N) if bf_bits[i]==0]))

    print(f"     Brute Force → B:{bf_B} | A:{bf_A}  | E={bf_e:.3f} | {bf_km:.0f}km")
    print(f"     Sim. Anneal → B:{sa_B} | A:{sa_A}  | E={sa_e:.3f}")
    print(f"     QAOA        → B:{qa_B} | A:{qa_A}  | E={qa_e:.3f}")
    match = "✓ MATCH" if qa_bits == bf_bits or qa_e <= bf_e + 0.01 else "~ NEAR"
    print(f"     Quantum result: {match}")

    results.append({
        **sc,
        "bf_bits": bf_bits, "bf_e": bf_e, "bf_B": bf_B, "bf_A": bf_A,
        "sa_bits": sa_bits, "sa_e": sa_e,
        "qa_bits": qa_bits, "qa_e": qa_e, "qa_B": qa_B, "qa_A": qa_A,
        "hist_e": hist_e,
        "bf_all": bf_all,
        "bf_km":  bf_km,
        "h_is": h_is, "J_is": J_is,
    })

# ─────────────────────────────────────────────────────────
# ROUTE DRAWING HELPER
# ─────────────────────────────────────────────────────────
def draw_route(ax, bits, color_A, color_B, alpha_line=0.85, lw=1.8):
    """Draw truck routes on the map axes."""
    b_del = [i for i in range(N) if bits[i]==1]
    a_del = [i for i in range(N) if bits[i]==0]

    # Truck B route
    if len(b_del) == 2:
        i, j = b_del
        # Choose best source
        best_src = 0
        best_d = float('inf')
        for s in range(2):
            src = S_COORD[s]
            d1 = (dist_km(src, T_COORD[i]) + dist_km(T_COORD[i], T_COORD[j])
                  + dist_km(T_COORD[j], src))
            d2 = (dist_km(src, T_COORD[j]) + dist_km(T_COORD[j], T_COORD[i])
                  + dist_km(T_COORD[i], src))
            if min(d1,d2) < best_d:
                best_d = min(d1,d2)
                best_src = s
                best_order = (i,j) if d1 <= d2 else (j,i)
        sx, sy = S_COORD[best_src]
        route = [best_src] + list(best_order)
        coords = [S_COORD[best_src]] + [T_COORD[k] for k in best_order] + [S_COORD[best_src]]
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        ax.plot(xs, ys, '-', color=color_B, lw=lw, alpha=alpha_line, zorder=2)
        ax.plot(xs, ys, 'o', color=color_B, ms=4, alpha=0.6, zorder=2)

    # Truck A routes (separate trips)
    for i in a_del:
        s = nearest_source(i)
        sx, sy = S_COORD[s]
        tx, ty = T_COORD[i]
        ax.annotate('', xy=(tx, ty), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color=color_A,
                                   lw=lw*0.9, alpha=alpha_line))
        ax.plot([tx, sx], [ty, sy], '--', color=color_A,
                lw=lw*0.7, alpha=alpha_line*0.5, zorder=2)

def draw_map_base(ax, title):
    """Draw base map with nodes."""
    ax.set_facecolor('#0a1628')
    ax.set_title(title, color='#c9d1d9', fontsize=9, pad=6)

    # Rough Europe boundary (simplified polygon)
    europe_lon = [-10, 40, 40, -10, -10]
    europe_lat = [35,  35,  60,  60, 35]
    ax.set_xlim(-6, 24)
    ax.set_ylim(43, 55)

    # Light grid
    for lon in range(-5, 25, 5):
        ax.axvline(lon, color='#1c2a3a', lw=0.5, alpha=0.5)
    for lat in range(44, 56, 2):
        ax.axhline(lat, color='#1c2a3a', lw=0.5, alpha=0.5)

    # Sources
    for name, (lon, lat) in SOURCES.items():
        ax.plot(lon, lat, 's', ms=10, color='#e3b341',
                markeredgecolor='white', markeredgewidth=0.8, zorder=5)
        ax.annotate(f'⚙ {name}', (lon, lat),
                    textcoords='offset points', xytext=(5, 4),
                    color='#e3b341', fontsize=7, fontweight='bold')

    # Targets
    for name, (lon, lat) in TARGETS.items():
        ax.plot(lon, lat, 'o', ms=8, color='#d2a8ff',
                markeredgecolor='white', markeredgewidth=0.7, zorder=5)
        ax.annotate(name, (lon, lat),
                    textcoords='offset points', xytext=(4, -9),
                    color='#c9d1d9', fontsize=6.5)

    ax.tick_params(colors='#8b949e', labelsize=6)
    for sp in ax.spines.values(): sp.set_edgecolor('#21262d')
    ax.set_xlabel('Longitude', color='#8b949e', fontsize=7)
    ax.set_ylabel('Latitude',  color='#8b949e', fontsize=7)

# ─────────────────────────────────────────────────────────
# VISUALISATION  — 3×3 dashboard
# ─────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 14), facecolor='#0d1117')
fig.suptitle(
    'Quantum VRP — Steel Roll Transport Optimization  |  Europe  |  3 Scenarios',
    fontsize=15, color='white', fontweight='bold', y=0.99)

# Layout: rows per scenario, 3 cols: map | QAOA convergence | energy landscape
outer = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.35,
                          top=0.95, bottom=0.04, left=0.05, right=0.97)

BG = '#161b22'; FG = '#c9d1d9'; GR = '#21262d'

def sty(ax, title, xl, yl, small=False):
    ax.set_facecolor(BG)
    ax.set_title(title, color=FG, fontsize=8 if small else 9, pad=5)
    ax.set_xlabel(xl, color=FG, fontsize=7)
    ax.set_ylabel(yl, color=FG, fontsize=7)
    ax.tick_params(colors=FG, labelsize=7)
    for sp in ax.spines.values(): sp.set_edgecolor(GR)
    ax.grid(True, linestyle='--', alpha=0.30, color=GR)

for row, res in enumerate(results):
    sc_color = res["color"]
    ex       = list(range(EPOCHS))

    # ── Col 0: Route map ──────────────────────────────────
    ax_map = fig.add_subplot(outer[row, 0])
    draw_map_base(ax_map, f"{res['name']}\n{res['desc']}")
    draw_route(ax_map, res["qa_bits"],
               color_A='#f85149', color_B='#3fb950')

    # Legend on map
    leg_els = [
        Line2D([0],[0], color='#f85149', lw=1.8, linestyle='--',
               label=f"Truck A (cap=1): {', '.join(res['qa_A'])}"),
        Line2D([0],[0], color='#3fb950', lw=1.8,
               label=f"Truck B (cap=2): {', '.join(res['qa_B'])}"),
        mpatches.Patch(color='#e3b341', label='Steel Source'),
        mpatches.Patch(color='#d2a8ff', label='Customer'),
    ]
    ax_map.legend(handles=leg_els, facecolor='#0d1117', labelcolor=FG,
                  fontsize=5.5, loc='lower left', framealpha=0.85)

    km = (route_distance_truck_B([i for i in range(N) if res['qa_bits'][i]==1]) +
          route_distance_truck_A([i for i in range(N) if res['qa_bits'][i]==0]))
    ax_map.text(0.02, 0.97, f"QAOA total: {km:.0f} km",
                transform=ax_map.transAxes, color='white',
                fontsize=7, va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#0d1117', alpha=0.8))

    # ── Col 1: QAOA ⟨E⟩ convergence ──────────────────────
    ax_conv = fig.add_subplot(outer[row, 1])
    ax_conv.plot(ex, res["hist_e"], color=sc_color, lw=2, label='QAOA ⟨E⟩')
    ax_conv.axhline(y=res["bf_e"], color='#8b949e', lw=1.2, linestyle='--',
                    label=f'Optimal={res["bf_e"]:.3f}')
    ax_conv.fill_between(ex, res["hist_e"], alpha=0.15, color=sc_color)
    sty(ax_conv, 'QAOA Convergence  ⟨E(γ,β)⟩', 'Epoch', '⟨E⟩')
    ax_conv.legend(facecolor=BG, labelcolor=FG, fontsize=7)

    # ── Col 2: Energy landscape (all 32 assignments) ──────
    ax_land = fig.add_subplot(outer[row, 2])
    ax_land.set_facecolor(BG)
    energies = [e for e, _ in res["bf_all"]]
    bits_all = [b for _, b in res["bf_all"]]
    bar_cols = []
    for e, b in res["bf_all"]:
        if b == res["bf_bits"]:
            bar_cols.append('#3fb950')       # optimal
        elif b == res["qa_bits"]:
            bar_cols.append(sc_color)        # QAOA result
        elif e <= res["bf_e"] + abs(res["bf_e"]) * 0.15 + 0.05:
            bar_cols.append('#e3b341')       # near-optimal
        else:
            bar_cols.append('#21262d')       # rest

    ax_land.bar(range(len(energies)), energies,
                color=bar_cols, edgecolor='#0d1117', linewidth=0.2)
    ax_land.axhline(y=res["bf_e"], color='#3fb950', lw=1, linestyle='--', alpha=0.7)
    sty(ax_land, 'Full QUBO Landscape  (32 assignments)\n'
                 '■ Optimal  ■ QAOA  ■ Near-opt',
        'Assignment index (sorted by energy)', 'QUBO Energy', small=True)
    for sp in ax_land.spines.values(): sp.set_edgecolor(GR)

    # Colour legend
    leg2 = [mpatches.Patch(color='#3fb950', label='Optimal'),
            mpatches.Patch(color=sc_color,  label='QAOA pick'),
            mpatches.Patch(color='#e3b341', label='Near-optimal')]
    ax_land.legend(handles=leg2, facecolor=BG, labelcolor=FG,
                   fontsize=6, loc='upper left')

# ── Bottom summary text ───────────────────────────────────
summary_lines = ["  Scenario Results Summary:"]
for res in results:
    match = "✓" if res["qa_e"] <= res["bf_e"] + 0.02 else "~"
    summary_lines.append(
        f"  {res['name']:<22}  "
        f"Truck B→{res['bf_B']}  Truck A→{res['bf_A']}  "
        f"Optimal:{res['bf_e']:.3f}  QAOA:{res['qa_e']:.3f}  {match}"
    )
fig.text(0.02, 0.01, '\n'.join(summary_lines),
         color='#8b949e', fontsize=7, family='monospace',
         va='bottom', transform=fig.transFigure)

plt.savefig('/mnt/user-data/outputs/quantum_vrp_steel.png', dpi=150,
            bbox_inches='tight', facecolor='#0d1117')
print("\n  Dashboard saved → quantum_vrp_steel.png")
plt.show()
