import numpy as np
import matplotlib.pyplot as plt

## This simulation models a dynamic "timeline field" where multiple timelines (particles) 
## interact under a temporal gravity-like force, with the added complexity of quantum fluctuations that can spawn new timelines.
## The simulation includes collision detection for timeline merging and annihilation, as well as visual effects to represent these interactions.

# --- parameters ---
G_t = 0.3
EXPANSION = 0.0005
DT = 1.0
MERGE_DIST = 15.0  # Increased slightly for better collision detection
COLORS = {1: "deepskyblue", -1: "tomato", 0: "gold"}

# Quantum Fluctuation Settings
VACUUM_SPAWN_CHANCE = 0.08  # Probability per step that a quantum pair spawns
FLUCTUATION_LIFETIME = 150  # Max steps a virtual timeline pairs can exist without merging

# --- initial state arrays ---
# Switching to dynamic list structures that support easy appending/removal
positions = [np.array([1000.0, 0.0])]
velocities = [np.zeros(2)]
directions = [0]  # 0 = Prime Master Timeline, 1 = Forward, -1 = Backward
energy = [10.0]   # Higher initial energy for prime timeline
delta_t = [0.0]
paths = [[]]
lifetimes = [99999]  # Prime timeline lives indefinitely

# Data tracking metrics
annihilation_events = [] # Stores coordinates of timeline collapses for visual flashes

# --- Spawn a Virtual Quantum Pair ---
def spawn_quantum_pair():
    global positions, velocities, directions, energy, delta_t, paths, lifetimes
    if len(positions) == 0: return
    
    # Pick a random existing active timeline to spawn near
    parent_idx = np.random.choice([i for i in range(len(positions)) if energy[i] > 0])
    base_pos = positions[parent_idx]
    
    # Generate an electron-positron analogue pair (Forward +1 and Backward -1)
    for t_dir in [1, -1]:
        angle = np.random.uniform(0, 2*np.pi)
        dist = np.random.uniform(30, 80)
        
        new_pos = base_pos + dist * np.array([np.cos(angle), np.sin(angle)])
        # Fast, erratic quantum movements
        new_vel = np.random.randn(2) * 2.5 
        new_energy = np.random.uniform(1.5, 3.0)
        
        positions.append(new_pos)
        velocities.append(new_vel)
        directions.append(t_dir)
        energy.append(new_energy)
        delta_t.append(delta_t[parent_idx]) # Sync initial time to current neighborhood time
        paths.append([])
        lifetimes.append(FLUCTUATION_LIFETIME)

# --- update simulation ---
def update():
    global positions, velocities, directions, energy, delta_t, paths, lifetimes, annihilation_events
    n = len(positions)
    forces = [np.zeros(2, dtype=float) for _ in range(n)]

    # 1. Quantum Fluctuation Spawning (Krauss Analogue)
    if np.random.rand() < VACUUM_SPAWN_CHANCE:
        spawn_quantum_pair()
        n = len(positions) # Update count for new particles
        forces = [np.zeros(2, dtype=float) for _ in range(n)]

    # 2. Multi-body Interaction Loops
    for i in range(n):
        if energy[i] <= 0: continue
        for j in range(i+1, n):
            if energy[j] <= 0: continue
            
            r = positions[j] - positions[i]
            dist = np.linalg.norm(r) + 1e-5

            # Collision & Annihilation Logic
            if dist < MERGE_DIST:
                # If a forward (1) and backward (-1) timeline collide: Total Annihilation!
                if directions[i] * directions[j] == -1:
                    annihilation_events.append(( (positions[i] + positions[j])/2.0, 30 )) # Trigger a flash
                    energy[i] = 0.0
                    energy[j] = 0.0
                else:
                    # Constructive merging of matching directions
                    positions[i] = (positions[i] + positions[j]) / 2.0
                    energy[i] += energy[j]
                    energy[j] = 0.0
                    velocities[i] = (velocities[i] + velocities[j]) / 2.0
                continue

            # Temporal Gravity calculation
            F = G_t * energy[i] * energy[j] / dist**2
            
            # Interference/Directional adjustment: 
            # Opposite moving timelines slightly repel until they drop into close capture range
            if directions[i] * directions[j] == -1:
                F *= -0.5 
                
            f_vec = F * (r / dist)
            forces[i] += f_vec
            forces[j] -= f_vec

    # 3. Integrate Motion & Enforce Decay
    for k in range(n):
        if energy[k] <= 0: continue

        velocities[k] += forces[k] * DT
        positions[k] += velocities[k] * DT
        positions[k] *= (1.0 + EXPANSION)

        paths[k].append(positions[k].copy())
        delta_t[k] += directions[k] * DT
        
        # Virtual particles decay over time if they don't stabilize/merge
        lifetimes[k] -= 1
        if lifetimes[k] <= 0:
            energy[k] = 0.0 # Fade out safely

# --- visualization loop ---
plt.ion()
fig, ax = plt.subplots(figsize=(8,8))

for step in range(1500):
    update()

    ax.clear()
    ax.set_facecolor('#0f111a')  # Dark space background
    ax.set_xlim(500, 1500)
    ax.set_ylim(-500, 500)
    ax.set_title(f"Timeline Field | Quantum Fluctuations | Step {step}", color='white', fontsize=10)
    ax.grid(True, color='#23283d', linestyle='--', alpha=0.5)

    # A. Draw Annihilation Flashes (Data Points)
    remaining_flashes = []
    for flash_pos, radius in annihilation_events:
        ax.scatter(flash_pos[0], flash_pos[1], s=radius*10, color='white', alpha=0.6, zorder=4)
        ax.scatter(flash_pos[0], flash_pos[1], s=radius*20, color='gold', alpha=0.2, zorder=1)
        if radius > 5:
            remaining_flashes.append((flash_pos, radius - 4)) # Fade the flash over frames
    annihilation_events = remaining_flashes

    # B. Draw Timelines
    for k in range(len(positions)):
        if energy[k] <= 0: continue
        
        # Scale line thickness with current energy levels
        linewidth = min(max(energy[k] * 0.5, 0.8), 4.0)
        color = COLORS.get(directions[k], "gray")
        
        # Draw Historical Path
        if len(paths[k]) > 2:
            path_data = np.array(paths[k])
            ax.plot(path_data[:, 0], path_data[:, 1], color=color, alpha=0.5, linewidth=linewidth)

        # Draw Present Particle Node
        pulse = (25 + 10 * np.sin(step * 0.2)) * (energy[k]/3.0)
        ax.scatter(positions[k][0], positions[k][1], s=pulse, color=color, edgecolors='white', linewidths=0.5, zorder=3)
        
        # Track relative time state as text data labels
        ax.text(positions[k][0]+12, positions[k][1]+12, f"t: {int(delta_t[k])}", fontsize=7, color='white', alpha=0.7)

    plt.pause(0.001)

plt.ioff()
plt.show()