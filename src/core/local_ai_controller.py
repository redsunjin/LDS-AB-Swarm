import numpy as np
import time
from typing import List, Dict, Tuple
from src.simulator.drone import Drone

class LocalAINeuralPolicy:
    """
    Lightweight Edge Neural Network Policy for distributed swarm control.
    Executes in < 2ms per step without external network/C2 dependencies.
    """
    def __init__(self, input_dim: int = 12, hidden_dim: int = 24, output_dim: int = 3, seed: int = 42):
        np.random.seed(seed)
        # Xavier/He initialization of neural weights
        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, hidden_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(hidden_dim)
        self.W3 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2.0 / hidden_dim)
        self.b3 = np.zeros(output_dim)

    def relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, x)

    def forward(self, state: np.ndarray) -> np.ndarray:
        """Forward pass for 1D state vector or 2D batch of states."""
        h1 = self.relu(np.dot(state, self.W1) + self.b1)
        h2 = self.relu(np.dot(h1, self.W2) + self.b2)
        out = np.dot(h2, self.W3) + self.b3
        return out


class LocalAISwarmController:
    """
    Local AI Edge Controller for ultra-fast autonomous drone swarm control (< 5ms reaction).
    Combines edge neural policy inference with UWB local repulsion safety.
    """
    def __init__(self, 
                 k_att: float = 6.5, 
                 k_rep: float = 15.0, 
                 d_rep: float = 6.0, 
                 k_damp: float = 2.0):
        self.policy = LocalAINeuralPolicy()
        self.k_att = k_att
        self.k_rep = k_rep
        self.d_rep = d_rep
        self.k_damp = k_damp

        self.drone_target_map: Dict[int, int] = {}
        self.last_inference_time_ms: float = 0.0

    def compute_control_signals(self, drones: List[Drone], target_nodes: np.ndarray) -> Tuple[Dict[int, np.ndarray], float]:
        """
        Executes Local AI forward inference and outputs desired acceleration vectors for active drones.
        Returns: (control_signals_map, inference_time_ms)
        """
        start_time = time.perf_counter()
        control_signals = {}
        active_drones = [d for d in drones if d.status == "active"]

        if not active_drones or len(target_nodes) == 0:
            return control_signals, 0.0

        num_drones = len(active_drones)
        num_nodes = len(target_nodes)

        # 1. Fast Greedy / Nearest Target Allocation
        unassigned_nodes = set(range(num_nodes))
        assigned_targets = {}

        for drone in active_drones:
            # Find closest unassigned node
            dists = np.linalg.norm(target_nodes - drone.position, axis=1)
            sorted_indices = np.argsort(dists)
            chosen_node_idx = None
            for idx in sorted_indices:
                if idx in unassigned_nodes:
                    chosen_node_idx = idx
                    unassigned_nodes.remove(idx)
                    break
            
            if chosen_node_idx is not None:
                drone.target_position = target_nodes[chosen_node_idx]
                assigned_targets[drone.id] = target_nodes[chosen_node_idx]
            else:
                drone.target_position = target_nodes[sorted_indices[0]]
                assigned_targets[drone.id] = target_nodes[sorted_indices[0]]

        # 2. Local AI Policy + APF Safety Hybrid Acceleration Computation
        for drone in active_drones:
            target_pos = drone.target_position if drone.target_position is not None else drone.position
            target_err = target_pos - drone.position

            # Construct 12-dimensional state vector for local AI
            # [dx, dy, dz, vx, vy, vz, nearest_neighbor_dx, dy, dz, target_dist, 0, 0]
            nearest_neighbor_vec = np.zeros(3)
            min_neighbor_dist = 999.0
            for other in active_drones:
                if other.id == drone.id:
                    continue
                d = drone.distance_to(other.position)
                if d < min_neighbor_dist:
                    min_neighbor_dist = d
                    nearest_neighbor_vec = drone.position - other.position

            state_vec = np.concatenate([
                target_err,
                drone.velocity,
                nearest_neighbor_vec,
                [np.linalg.norm(target_err), min_neighbor_dist, 0.0]
            ])

            # Local AI Neural Forward Inference
            ai_accel_bias = self.policy.forward(state_vec)

            # Heuristic Target Attraction & APF Repulsion
            accel = self.k_att * target_err + 0.3 * ai_accel_bias

            # Inter-drone UWB Repulsion Safety
            for other in active_drones:
                if other.id == drone.id:
                    continue
                vec = drone.position - other.position
                dist = np.linalg.norm(vec)
                if 0.01 < dist < self.d_rep:
                    rep_mag = self.k_rep * (1.0 / dist - 1.0 / self.d_rep) / (dist ** 2)
                    accel += (vec / dist) * rep_mag

            # Damping
            accel -= self.k_damp * drone.velocity
            control_signals[drone.id] = accel

        end_time = time.perf_counter()
        self.last_inference_time_ms = (end_time - start_time) * 1000.0
        return control_signals, self.last_inference_time_ms
