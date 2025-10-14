import numpy as np
import matplotlib.pyplot as plt

# --- parameters you can play with ---
NUM_TIMELINES = 50
G_t = 0.3          # temporal gravity strength
EXPANSION = 0.0005 # dark‑energy‑like expansion
DT = 1.0           # time step
MERGE_DIST = 10.0  # distance at which two timelines merge
COLORS = {1: "deepskyblue", -1: "tomato"}

# --- initial state ---
np.random.seed(42)
positions = np.random.rand(NUM_TIMELINES, 2) * 500
velocities = np.zeros((NUM_TIMELINES, 2))
directions = np.random.choice([1, -1], NUM_TIMELINES)   # forward/backward
energy = np.ones(NUM_TIMELINES)

# --- simulation update ---
def update():
    global positions, velocities, energy
    forces = np.zeros_like(positions)

    for i in range(NUM_TIMELINES):
        for j in range(i + 1, NUM_TIMELINES):
            r = positions[j] - positions[i]
            dist = np.linalg.norm(r) + 1e-5
            if dist < MERGE_DIST:
                # merge: conserve "energy" and set midpoint
                positions[i] = (positions[i] + positions[j]) / 2
                energy[i] += energy[j]
                energy[j] = 0
                velocities[j] = 0
                continue

            # temporal‑gravity force
            F = G_t * energy[i] * energy[j] / dist**2
            f_vec = F * (r / dist)
            forces[i] += f_vec
            forces[j] -= f_vec

    velocities += forces * DT
    positions += velocities * DT
    positions *= (1 + EXPANSION)        # dark‑energy expansion

# --- visualize with matplotlib animation ---
plt.ion()
fig, ax = plt.subplots(figsize=(6, 6))

for step in range(1000):
    update()
    ax.clear()
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)
    ax.set_title("Timeline Ripple Simulation")
    alive = energy > 0
    for s in [1, -1]:
        idx = np.where((directions == s) & alive)[0]
        ax.scatter(
            positions[idx, 0],
            positions[idx, 1],
            s=20,
            color=COLORS[s],
            label=">" if s == 1 else "<"
        )
    ax.legend()
    plt.pause(0.01)

plt.ioff()
plt.show()