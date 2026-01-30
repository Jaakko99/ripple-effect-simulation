import numpy as np
import matplotlib.pyplot as plt
import time

# --- parameters ---
G_t = 0.3
EXPANSION = 0.0005
DT = 1.0
MERGE_DIST = 10.0
SPAWN_INTERVAL = 3.0  # seconds between spawning new timelines

COLORS = {1: "deepskyblue", -1: "tomato", 0: "limegreen"}

# --- initial state ---
positions = [np.array([500.0, 500.0])]  # original timeline
velocities = [np.zeros(2)]
directions = [0]  # 0=original, ±1=ripples
energy = [5.0]
# each timeline has its own delta time (Δt)
delta_t = [0.0]  # starts at 0s for original

# --- spawn helper ---
last_spawn_time = None

def spawn_one(i):
    global positions, velocities, directions, energy, delta_t
    angle = np.random.uniform(0, 2*np.pi)
    dist = np.random.uniform(20, 60)
    new_pos = positions[i] + dist * np.array([np.cos(angle), np.sin(angle)])
    new_vel = np.random.randn(2) * 0.2
    new_dir = np.random.choice([1, -1])  # forward/backward
    new_energy = max(energy[i] * np.random.uniform(0.5, 0.9), 0.1)
    new_dt = 0.0  # start new timeline at 0 relative to parent
    positions.append(new_pos)
    velocities.append(new_vel)
    directions.append(new_dir)
    energy.append(new_energy)
    delta_t.append(new_dt)

# --- update simulation ---
def update():
    n = len(positions)
    forces = [np.zeros(2) for _ in range(n)]

    for i in range(n):
        for j in range(i+1, n):
            r = positions[j] - positions[i]
            dist = np.linalg.norm(r) + 1e-5
            if dist < MERGE_DIST:
                # merge
                positions[i] = (positions[i] + positions[j]) / 2
                energy[i] += energy[j]
                energy[j] = 0
                velocities[j] = np.zeros(2)
                continue
            F = G_t * energy[i] * energy[j] / dist**2
            f_vec = F * (r / dist)
            forces[i] += f_vec
            forces[j] -= f_vec

    # update velocities & positions
    for k in range(n):
        velocities[k] += forces[k] * DT
        positions[k] += velocities[k] * DT
        positions[k] *= (1 + EXPANSION)
        # update Δt based on direction
        if directions[k] != 0:
            delta_t[k] += directions[k] * DT

# --- visualization loop ---
plt.ion()
fig, ax = plt.subplots(figsize=(7,7))
start_time = time.time()
last_spawn_time = start_time

for step in range(1200):
    now = time.time()
    t_elapsed = now - start_time

    # spawn one timeline every SPAWN_INTERVAL seconds
    if t_elapsed > 10 and now - last_spawn_time > SPAWN_INTERVAL:
        spawn_one(0)
        last_spawn_time = now

    update()
    ax.clear()
    ax.set_xlim(0,1000)
    ax.set_ylim(0,1000)
    ax.set_title(f"Timeline Ripple Simulation — t={t_elapsed:5.1f}s")

    # draw dots by type
    for s in [0,1,-1]:
        idx = [i for i,d in enumerate(directions) if d==s and energy[i]>0]
        if idx:
            p = np.array([positions[i] for i in idx])
            ax.scatter(p[:,0], p[:,1], s=40 if s==0 else 20,
                       color=COLORS[s],
                       label=("Original" if s==0 else ("> Forward" if s==1 else "< Backward")))
            # add Δt label next to dot
            for i in idx:
                ax.text(positions[i][0]+5, positions[i][1]+5, f"{delta_t[i]:.1f}s", fontsize=7, color=COLORS[s])

    ax.legend()
    plt.pause(0.03)

plt.ioff()
plt.show()