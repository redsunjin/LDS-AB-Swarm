import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Callable, Optional, Union

@dataclass
class ThreatTrajectory:
    """
    Represents an incoming threat trajectory in 3D space.
    Supports linear, curved/sinusoidal, and evasive maneuvering trajectories.
    """
    initial_position: np.ndarray
    velocity_func: Callable[[float], np.ndarray]
    position_func: Optional[Callable[[float], np.ndarray]] = None

    @classmethod
    def create_linear(cls, start_pos: Union[List[float], np.ndarray], velocity: Union[List[float], np.ndarray]) -> "ThreatTrajectory":
        """Creates a high-speed linear trajectory (e.g. Cruise Missile)."""
        pos_arr = np.array(start_pos, dtype=np.float64)
        vel_arr = np.array(velocity, dtype=np.float64)
        return cls(
            initial_position=pos_arr,
            velocity_func=lambda t: vel_arr,
            position_func=lambda t: pos_arr + vel_arr * t
        )

    @classmethod
    def create_weaving_sinusoidal(cls, start_pos: Union[List[float], np.ndarray], 
                                  base_velocity: Union[List[float], np.ndarray], 
                                  amplitude: float = 8.0, 
                                  freq: float = 1.5) -> "ThreatTrajectory":
        """Creates an evasive S-curve / weaving trajectory (e.g. Kamikaze Drone)."""
        pos_arr = np.array(start_pos, dtype=np.float64)
        v_base = np.array(base_velocity, dtype=np.float64)

        def pos_f(t: float) -> np.ndarray:
            # Weaving motion along Y and Z axis perpendicular to main direction
            offset_y = amplitude * np.sin(freq * t)
            offset_z = amplitude * 0.5 * np.cos(freq * t * 0.7)
            return pos_arr + v_base * t + np.array([0.0, offset_y, offset_z])

        def vel_f(t: float) -> np.ndarray:
            vel_y = amplitude * freq * np.cos(freq * t)
            vel_z = -amplitude * 0.5 * freq * 0.7 * np.sin(freq * t * 0.7)
            return v_base + np.array([0.0, vel_y, vel_z])

        return cls(
            initial_position=pos_arr,
            velocity_func=vel_f,
            position_func=pos_f
        )

    def get_position(self, t: float) -> np.ndarray:
        if self.position_func is not None:
            return self.position_func(t)
        return self.initial_position + self.velocity_func(t) * t

    def get_velocity(self, t: float) -> np.ndarray:
        return self.velocity_func(t)


class MeshGenerator:
    """
    Enhanced Multi-Layer & Multi-Angle 3D Grid Mesh Generator.
    Supports pitch/yaw orientation adjustments and staggered multi-layer grid formations.
    """
    def __init__(self, default_spacing: float = 5.0):
        self.default_spacing = default_spacing

    @staticmethod
    def compute_tilted_plane_basis(velocity_vector: np.ndarray, 
                                    pitch_offset_deg: float = 0.0, 
                                    yaw_offset_deg: float = 0.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes normal vector and orthonormal plane basis (u, v) with optional pitch/yaw tilt angles.
        """
        speed = np.linalg.norm(velocity_vector)
        if speed < 1e-6:
            base_normal = np.array([1.0, 0.0, 0.0])
        else:
            base_normal = -velocity_vector / speed  # Facing threat origin

        # Base arbitrary orthogonal vector
        if abs(base_normal[0]) < 0.9:
            arbitrary = np.array([1.0, 0.0, 0.0])
        else:
            arbitrary = np.array([0.0, 1.0, 0.0])

        u = np.cross(base_normal, arbitrary)
        u /= np.linalg.norm(u)
        v = np.cross(base_normal, u)
        v /= np.linalg.norm(v)

        # Apply Pitch & Yaw angle rotations if specified
        if abs(pitch_offset_deg) > 1e-3 or abs(yaw_offset_deg) > 1e-3:
            pitch_rad = np.radians(pitch_offset_deg)
            yaw_rad = np.radians(yaw_offset_deg)

            # Rotate basis vectors around u (pitch) and v (yaw)
            u_rot = u * np.cos(yaw_rad) + base_normal * np.sin(yaw_rad)
            v_rot = v * np.cos(pitch_rad) + base_normal * np.sin(pitch_rad)
            
            u = u_rot / np.linalg.norm(u_rot)
            v = v_rot / np.linalg.norm(v_rot)
            normal = np.cross(u, v)
            normal /= np.linalg.norm(normal)
        else:
            normal = base_normal

        return normal, u, v

    def generate_mesh(self, 
                      trajectory: ThreatTrajectory, 
                      time_to_intercept: float, 
                      grid_shape: Tuple[int, int] = (5, 5), 
                      spacing: Optional[float] = None, 
                      depth_layers: int = 1,
                      layer_depth_spacing: float = 4.0,
                      layer_stagger: bool = True,
                      pitch_offset_deg: float = 0.0,
                      yaw_offset_deg: float = 0.0) -> np.ndarray:
        """
        Generates 3D coordinates array for multi-layer, multi-angle defensive barrier grid.

        Parameters:
        - trajectory: ThreatTrajectory object
        - time_to_intercept: Intercept prediction horizon (sec)
        - grid_shape: (rows, cols) nodes per layer plane
        - spacing: Distance between nodes (meters)
        - depth_layers: Number of defense layers (1 = single plane, 2+ = multi-layer)
        - layer_depth_spacing: Depth distance between layers
        - layer_stagger: If True, offsets rear layer nodes by half-spacing to cover gaps (Staggered Grid)
        - pitch_offset_deg: Pitch tilt angle in degrees
        - yaw_offset_deg: Yaw tilt angle in degrees
        """
        if spacing is None:
            spacing = self.default_spacing

        intercept_pos = trajectory.get_position(time_to_intercept)
        threat_vel = trajectory.get_velocity(time_to_intercept)

        normal, u, v = self.compute_tilted_plane_basis(threat_vel, pitch_offset_deg, yaw_offset_deg)

        rows, cols = grid_shape
        row_offset = (rows - 1) / 2.0
        col_offset = (cols - 1) / 2.0

        nodes = []
        for layer in range(depth_layers):
            # Depth position along normal vector
            depth_pos = (layer - (depth_layers - 1) / 2.0) * layer_depth_spacing
            layer_center = intercept_pos + depth_pos * normal

            # Half-spacing stagger shift for secondary/rear layers
            stagger_u = (spacing * 0.5) if (layer_stagger and layer % 2 == 1) else 0.0
            stagger_v = (spacing * 0.5) if (layer_stagger and layer % 2 == 1) else 0.0

            for r in range(rows):
                for c in range(cols):
                    offset_u = (r - row_offset) * spacing + stagger_u
                    offset_v = (c - col_offset) * spacing + stagger_v
                    node_pos = layer_center + offset_u * u + offset_v * v
                    nodes.append(node_pos)

        return np.array(nodes, dtype=np.float64)
