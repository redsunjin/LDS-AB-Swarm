import numpy as np
from typing import List, Dict
from src.simulator.drone import Drone

try:
    from scipy.optimize import linear_sum_assignment
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

class SwarmController:
    def __init__(self, 
                 k_att: float = 2.5, 
                 k_rep: float = 15.0, 
                 d_rep: float = 6.0, 
                 k_damp: float = 1.2):
        self.k_att = k_att      # Target attraction gain
        self.k_rep = k_rep      # Inter-drone repulsion gain
        self.d_rep = d_rep      # Repulsion safety threshold (meters)
        self.k_damp = k_damp    # Velocity damping gain

        self.drone_target_map: Dict[int, int] = {}  # drone_id -> target_node_index
        self.last_reallocation_time = 0.0

    def solve_target_allocation(self, drones: List[Drone], target_nodes: List[np.ndarray]):
        """
        Optimal 1-to-1 matching between active drones and target 3D grid nodes using Hungarian Algorithm.
        Fills grid holes instantly upon drone loss (Self-Healing).
        """
        active_drones = [d for d in drones if d.status == "active"]
        if not active_drones or len(target_nodes) == 0:
            self.drone_target_map.clear()
            return

        num_drones = len(active_drones)
        num_nodes = len(target_nodes)

        # Build distance cost matrix (shape: num_drones x num_nodes)
        cost_matrix = np.zeros((num_drones, num_nodes))
        for i, drone in enumerate(active_drones):
            for j, node in enumerate(target_nodes):
                cost_matrix[i, j] = drone.distance_to(node)

        if HAS_SCIPY:
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
        else:
            # Greedy allocation fallback
            row_ind, col_ind = [], []
            available_nodes = set(range(num_nodes))
            for i in range(num_drones):
                costs = cost_matrix[i]
                sorted_nodes = np.argsort(costs)
                for node_idx in sorted_nodes:
                    if node_idx in available_nodes:
                        row_ind.append(i)
                        col_ind.append(node_idx)
                        available_nodes.remove(node_idx)
                        break

        # Update drone targets
        self.drone_target_map.clear()
        for r, c in zip(row_ind, col_ind):
            drone = active_drones[r]
            node_pos = target_nodes[c]
            drone.target_position = node_pos
            self.drone_target_map[drone.id] = c

    def compute_control_forces(self, drones: List[Drone]) -> Dict[int, np.ndarray]:
        """
        Computes Artificial Potential Field (APF) desired acceleration vectors for active drones.
        """
        control_signals = {}
        active_drones = [d for d in drones if d.status == "active"]

        for drone in active_drones:
            accel = np.zeros(3)

            # 1. Attractive force towards assigned target node
            if drone.target_position is not None:
                pos_err = drone.target_position - drone.position
                accel += self.k_att * pos_err

            # 2. Repulsive force from nearby active drones
            for other in active_drones:
                if other.id == drone.id:
                    continue
                vec = drone.position - other.position
                dist = np.linalg.norm(vec)

                if 0.01 < dist < self.d_rep:
                    rep_mag = self.k_rep * (1.0 / dist - 1.0 / self.d_rep) / (dist ** 2)
                    accel += (vec / dist) * rep_mag

            # 3. Damping force against high velocities
            accel -= self.k_damp * drone.velocity

            control_signals[drone.id] = accel

        return control_signals
