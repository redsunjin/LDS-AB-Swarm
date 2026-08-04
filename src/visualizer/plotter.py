import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Tuple, Optional
from src.simulator.drone import Drone
from src.simulator.threat import Threat

class SwarmVisualizer:
    def __init__(self, title: str = "LDS-AB Swarm Multi-Layer Barrier & Local AI Simulation"):
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(11, 8.5))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title(title, color='cyan', fontsize=13, fontweight='bold')
        self.ax.set_xlabel('X: Distance to Defense Base (m)')
        self.ax.set_ylabel('Y: Lateral Width (m)')
        self.ax.set_zlabel('Z: Altitude (m)')
        # Camera view: Looking from right (+X) towards defense station at X=20m
        self.ax.view_init(elev=22, azim=135)

    def render(self, 
               drones: List[Drone], 
               threats: List[Threat], 
               target_nodes: np.ndarray, 
               sim_time: float, 
               grid_shape: Tuple[int, int] = (5, 5),
               depth_layers: int = 1,
               local_ai_latency_ms: Optional[float] = None):
        """Renders 3D frame with proper 3D quiver arrows for incoming threat orientation."""
        self.ax.cla()
        
        ai_text = f" | Local AI Latency: {local_ai_latency_ms:.2f}ms" if local_ai_latency_ms is not None else ""
        self.ax.set_title(f"LDS-AB Autonomous Defense | Time: {sim_time:.2f}s{ai_text}", color='cyan', fontsize=11)
        self.ax.set_xlabel('X: Distance to Base (m)')
        self.ax.set_ylabel('Y: Lateral Width (m)')
        self.ax.set_zlabel('Z: Altitude (m)')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.view_init(elev=22, azim=135)

        # Ground Defense Base Marker at X=20m
        self.ax.plot([20, 20], [-20, 20], [0, 0], color='#00ffcc', linestyle='-', linewidth=2.5, alpha=0.7, label='Defense Base Ground (X=20m)')

        # 1. Render Multi-Layer Target Grid Nodes & Wireframe Mesh
        if target_nodes is not None and len(target_nodes) > 0:
            nodes_arr = np.array(target_nodes)
            rows, cols = grid_shape
            nodes_per_layer = rows * cols

            for l in range(depth_layers):
                start_idx = l * nodes_per_layer
                end_idx = (l + 1) * nodes_per_layer
                if end_idx <= len(nodes_arr):
                    layer_nodes = nodes_arr[start_idx:end_idx]
                    grid_matrix = layer_nodes.reshape((rows, cols, 3))

                    color_code = '#00ffcc' if l == 0 else '#ffd700'
                    label_str = f'Layer {l+1} Barrier Net'
                    self.ax.scatter(layer_nodes[:, 0], layer_nodes[:, 1], layer_nodes[:, 2], 
                                    color=color_code, s=18, alpha=0.6, label=label_str)

                    # Wireframe
                    for r in range(rows):
                        self.ax.plot(grid_matrix[r, :, 0], grid_matrix[r, :, 1], grid_matrix[r, :, 2], 
                                     color=color_code, linestyle=':', alpha=0.4)
                    for c in range(cols):
                        self.ax.plot(grid_matrix[:, c, 0], grid_matrix[:, c, 1], grid_matrix[:, c, 2], 
                                     color=color_code, linestyle=':', alpha=0.4)

        # 2. Render Active and Destroyed Drones
        active_pos = np.array([d.position for d in drones if d.status == "active"])
        destroyed_pos = np.array([d.position for d in drones if d.status in ("destroyed", "intercepted")])

        if len(active_pos) > 0:
            self.ax.scatter(active_pos[:, 0], active_pos[:, 1], active_pos[:, 2], 
                            color='#4ade80', s=45, depthshade=True, label=f'Active Swarm ({len(active_pos)})')

        if len(destroyed_pos) > 0:
            self.ax.scatter(destroyed_pos[:, 0], destroyed_pos[:, 1], destroyed_pos[:, 2], 
                            color='#ef4444', marker='x', s=75, label=f'Destroyed ({len(destroyed_pos)})')

        # Draw target vector lines
        for d in drones:
            if d.status == "active" and d.target_position is not None:
                self.ax.plot([d.position[0], d.target_position[0]],
                             [d.position[1], d.target_position[1]],
                             [d.position[2], d.target_position[2]],
                             color='#4ade80', linestyle='--', alpha=0.25)

        # 3. Render Multiple Threat Missile Vectors with 3D Quiver Arrow
        for idx, t in enumerate(threats):
            t_color = '#ff3333' if t.status == "approaching" else 'orange'
            label_text = f'Threat {t.id} [{t.status}]' if idx == 0 else None
            
            # Position dot
            self.ax.scatter(t.position[0], t.position[1], t.position[2], 
                            color=t_color, s=80, label=label_text)
            
            # 3D Directional Quiver Arrow pointing in velocity direction (towards X=20m)
            vel_norm = np.linalg.norm(t.velocity)
            if vel_norm > 1e-3:
                v_dir = t.velocity / vel_norm
                arrow_length = 20.0
                self.ax.quiver(
                    t.position[0], t.position[1], t.position[2],
                    v_dir[0] * arrow_length, v_dir[1] * arrow_length, v_dir[2] * arrow_length,
                    color='#ff3333', linewidth=2.5, arrow_length_ratio=0.3
                )

        # Set clear intuitive X-axis display: Threat coming from +X=200m on right down to X=0m on left
        self.ax.set_xlim(200, -20)
        self.ax.set_ylim(-35, 35)
        self.ax.set_zlim(0, 60)

        self.ax.legend(loc='upper left', facecolor='black', edgecolor='cyan', fontsize=8.5)
        plt.draw()
        plt.pause(0.001)

    def close(self):
        plt.close(self.fig)
