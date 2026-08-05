import numpy as np
from typing import Dict, Any, List
from src.core.mesh_generator import MeshGenerator, ThreatTrajectory
from src.core.dsp_protocol import DefensiveSwarmProtocol

class DSDOSKernelSyscalls:
    """
    DSD-OS Kernel System Call (Syscall) Interface.
    Provides standard system calls for Swarm Defense Apps running on DSD-OS.
    """
    def __init__(self, num_drones: int = 50):
        self.num_drones = num_drones
        self.active_mesh_params = {"shape": "saturation", "depth_layers": 2, "pitch_deg": 0.0}

    def sys_deploy_mesh(self, shape_type: str = "saturation", depth_layers: int = 2, pitch_deg: float = 0.0) -> np.ndarray:
        """
        [Syscall 0x01] Deploys dynamic 3D multi-layer barrier mesh grid nodes.
        """
        self.active_mesh_params = {"shape": shape_type, "depth_layers": depth_layers, "pitch_deg": pitch_deg}
        traj = ThreatTrajectory.create_linear(start_pos=np.array([180.0, 0.0, 25.0]), velocity=np.array([-28.0, 0.0, 0.0]))
        generator = MeshGenerator(default_spacing=7.0)
        nodes = generator.generate_mesh(
            trajectory=traj, time_to_intercept=1.5, grid_shape=(5, 5), spacing=7.0,
            depth_layers=depth_layers, layer_depth_spacing=6.0, pitch_offset_deg=pitch_deg
        )
        return nodes

    def sys_get_neighbor_telemetry(self, drone_id: int, drone_positions: Dict[int, np.ndarray]) -> List[Dict[str, Any]]:
        """
        [Syscall 0x02] Retrieves peer-to-peer UWB 100Hz neighbor telemetry list.
        """
        neighbors = []
        if drone_id not in drone_positions:
            return neighbors

        my_pos = drone_positions[drone_id]
        for other_id, other_pos in drone_positions.items():
            if other_id != drone_id:
                dist = np.linalg.norm(my_pos - other_pos)
                if dist <= 30.0:  # UWB RF Range 30m
                    neighbors.append({"drone_id": other_id, "distance": dist, "pos": other_pos})
        return neighbors

    def sys_execute_interception(self, target_vector: np.ndarray) -> bytes:
        """
        [Syscall 0x03] Triggers terminal proportional navigation (PN) interception thrust.
        """
        accel_setpoint = target_vector * 35.0  # Max acceleration thrust 35m/s^2
        return DefensiveSwarmProtocol.encode_thrust_vector(seq=99, sender_id=1, accel=accel_setpoint)
