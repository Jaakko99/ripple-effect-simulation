import numpy as np
import matplotlib.pyplot as plt
import time

# --- parameters ---
G_t = 0.3
EXPANSION = 0.0005
DT = 1.0
MERGE_DIST = 10
EVENT_T = 1945.0  # when the time travel happens in the prime timeline
RIPPLE_T = 1743.0 # where the new timeline begins
spawned = False
COLORS = {1: "deepskyblue", -1: "tomato"}

# --- initial state ---
positions = [np.array([1000.0, 0.0])]  # original timeline starts at (1000,0) and expands outward, with Δt=0 at the center as initial timeline
velocities = [np.zeros(2)]
directions = [1]  # 0=original, ±1=ripples
energy = [5.0]
# each timeline has its own delta time (Δt)
delta_t = [0.0]  # starts at 0s for original
paths = [[] for _ in range(len(positions))] # initialize paths list for each timeline

# --- spawn helper ---
last_spawn_time = None

def spawn_one(i):
    global positions, velocities, directions, energy, delta_t # spawn a new timeline from timeline i
    angle = np.random.uniform(0, 2*np.pi) # random angle
    dist = np.random.uniform(20, 60) # random distance from parent timeline
    new_pos = positions[i] + dist * np.array([np.cos(angle), np.sin(angle)]) # random position around parent
    new_vel = np.random.randn(2) * 0.2 # small random velocity
    new_dir = np.random.choice([1, -1])  # forward/backward
    new_energy = max(energy[i] * np.random.uniform(0.5, 0.9), 0.1) # inherit some energy from parent
    new_dt = 0.0  # start new timeline at 0 relative to parent 
    positions.append(new_pos) # add new timeline to simulation
    velocities.append(new_vel) # add velocity
    directions.append(new_dir) # add direction
    energy.append(new_energy) # add energy
    delta_t.append(new_dt) # add delta time

# --- update simulation ---
def update():
    n = len(positions)
    forces = [np.zeros(2, dtype=float) for _ in range(n)]

    # --- interactions ---
    for i in range(n):
        for j in range(i+1, n):
            r = positions[j] - positions[i]
            dist = np.linalg.norm(r) + 1e-5

            if dist < MERGE_DIST:
                # merge j into i
                positions[i] = (positions[i] + positions[j]) / 2.0
                energy[i] += energy[j]
                energy[j] = 0.0
                velocities[j] = np.zeros(2, dtype=float)
                continue

            F = G_t * energy[i] * energy[j] / dist**2
            f_vec = F * (r / dist)

            forces[i] += f_vec
            forces[j] -= f_vec

    # --- integrate motion ---
    for k in range(n):
        if energy[k] <= 0:
            continue

        velocities[k] += forces[k] * DT
        positions[k] += velocities[k] * DT
        positions[k] *= (1.0 + EXPANSION)

        # leave trail
        paths[k].append(positions[k].copy())

        # update internal timeline
        if directions[k] != 0:
            delta_t[k] += directions[k] * DT

# --- visualization loop ---
plt.ion()
fig, ax = plt.subplots(figsize=(7,7))

for step in range(1200):

    # advance universe
    update()

    # trigger first time travel ripple
    if not spawned and delta_t[0] >= EVENT_T:
        spawn_one(0)
        delta_t[-1] = RIPPLE_T   # newborn timeline starts in the past
        spawned = True

    # --- draw ---
    ax.clear()
    ax.set_xlim(0, 2000)
    ax.set_ylim(-1000, 1000)
    ax.set_title("Timeline Ripple Simulation")

    for s in [0, 1, -1]:
        idx = [i for i, d in enumerate(directions) if d == s and energy[i] > 0]
        if idx:
            p = np.array([positions[i] for i in idx])
            ax.scatter(
                p[:,0], p[:,1],
                s=40 if s==0 else 20,
                color=COLORS[s],
                label=("Original" if s==0 else ("> Forward" if s==1 else "< Backward"))
            )

            for i in idx:
                ax.text(
                    positions[i][0] + 5,
                    positions[i][1] + 5,
                    f"Year {int(delta_t[i])}",
                    fontsize=7,
                    color=COLORS[s]
                )

    ax.legend()
    plt.pause(0.03)

plt.ioff()
plt.show()