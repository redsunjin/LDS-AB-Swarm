import numpy as np
from typing import List, Tuple

class DynamicBarrierGeometry:
    @staticmethod
    def calculate_intercept_plane(threat_pos: np.ndarray, 
                                  threat_vel: np.ndarray, 
                                  time_to_intercept: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculates the center point and orthogonal basis vectors for the intercept plane.
        """
        speed = np.linalg.norm(threat_vel)
        if speed < 1e-3:
            normal = np.array([1.0, 0.0, 0.0])
        else:
            normal = -threat_vel / speed  # Normal faces against the threat trajectory

        center_point = threat_pos + threat_vel * time_to_intercept

        # Find two orthogonal vectors u and v on the plane perpendicular to 'normal'
        if abs(normal[0]) < 0.9:
            arbitrary = np.array([1.0, 0.0, 0.0])
        else:
            arbitrary = np.array([0.0, 1.0, 0.0])

        u = np.cross(normal, arbitrary)
        u /= np.linalg.norm(u)
        v = np.cross(normal, u)
        v /= np.linalg.norm(v)

        return center_point, u, v

    @classmethod
    def generate_3d_grid_nodes(cls, 
                               threat_pos: np.ndarray, 
                               threat_vel: np.ndarray, 
                               time_to_intercept: float, 
                               grid_size: Tuple[int, int] = (5, 5), 
                               spacing: float = 8.0) -> List[np.ndarray]:
        """
        Generates 3D coordinates for a 2D barrier grid plane facing the incoming threat.
        grid_size: (rows, cols)
        spacing: distance between adjacent nodes in meters
        """
        center, u, v = cls.calculate_intercept_plane(threat_pos, threat_vel, time_to_intercept)
        rows, cols = grid_size
        nodes = []

        row_offset = (rows - 1) / 2.0
        col_offset = (cols - 1) / 2.0

        for r in range(rows):
            for c in range(cols):
                offset_u = (r - row_offset) * spacing
                offset_v = (c - col_offset) * spacing
                node_pos = center + offset_u * u + offset_v * v
                nodes.append(node_pos)

        return nodes
