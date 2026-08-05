import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

@dataclass
class Threat360Vector:
    threat_id: int
    azimuth_deg: float      # 0° to 360° around base
    elevation_deg: float    # -90° (dive) to +90°
    distance_m: float
    approach_velocity: np.ndarray

class OmnidirectionalBarrierEngine:
    """
    360-Degree Omnidirectional Defense & Morphing Barrier Net Geometry Engine.
    Morphs barrier mesh topology into:
      1. OMNI_CYLINDRICAL_PERIMETER (360° Cylindrical Surround Net)
      2. TOP_COVER_UMBRELLA (Top Plunging Umbrella Dome Net)
      3. MULTI_SECTOR_V_SHAPE (V-Shaped Flank Intercept Net)
      4. DIRECTIONAL_STAGGERED_WALL (Single Sector Staggered Wall)
    """
    def __init__(self, base_center: Optional[np.ndarray] = None):
        self.base_center = base_center if base_center is not None else np.array([20.0, 0.0, 20.0])

    def generate_360_morphing_barrier(self, 
                                     threat_vectors: List[Threat360Vector], 
                                     net_mode: str = "AUTO", 
                                     num_drones: int = 50,
                                     radius_m: float = 25.0,
                                     height_m: float = 30.0) -> Tuple[np.ndarray, str]:
        """
        Generates 3D target coordinates for 50 drones morphing into 360° barrier net shapes.
        """
        if net_mode == "AUTO":
            if not threat_vectors:
                net_mode = "OMNI_CYLINDRICAL_PERIMETER"
            else:
                has_top_dive = any(t.elevation_deg < -30.0 for t in threat_vectors)
                azimuths = [t.azimuth_deg % 360 for t in threat_vectors]
                spread = max(azimuths) - min(azimuths) if azimuths else 0

                if has_top_dive:
                    net_mode = "TOP_COVER_UMBRELLA"
                elif spread > 120.0 or len(threat_vectors) >= 3:
                    net_mode = "OMNI_CYLINDRICAL_PERIMETER"
                elif spread > 45.0:
                    net_mode = "MULTI_SECTOR_V_SHAPE"
                else:
                    net_mode = "DIRECTIONAL_STAGGERED_WALL"

        nodes = np.zeros((num_drones, 3))

        if net_mode == "OMNI_CYLINDRICAL_PERIMETER":
            # 360-Degree Cylindrical Ring Perimeter Mesh surrounding Base (X=20m)
            rings = 3
            drones_per_ring = num_drones // rings
            for r in range(rings):
                r_height = 10.0 + r * 12.0
                r_radius = radius_m + (r * 2.0)
                for i in range(drones_per_ring):
                    idx = r * drones_per_ring + i
                    angle = (2.0 * np.pi / drones_per_ring) * i + (r * 0.2)  # Staggered angle
                    nodes[idx] = self.base_center + np.array([
                        r_radius * np.cos(angle),
                        r_radius * np.sin(angle),
                        r_height - self.base_center[2]
                    ])

        elif net_mode == "TOP_COVER_UMBRELLA":
            # Horizontal Umbrella Dome Mesh at Z=40m for plunging dive threats
            drones_per_ring = num_drones // 3
            for r in range(3):
                ring_rad = (r + 1) * 8.0
                for i in range(drones_per_ring):
                    idx = r * drones_per_ring + i
                    angle = (2.0 * np.pi / drones_per_ring) * i
                    nodes[idx] = self.base_center + np.array([
                        ring_rad * np.cos(angle),
                        ring_rad * np.sin(angle),
                        20.0 - (r * 2.0)  # High umbrella dome top cover
                    ])

        elif net_mode == "MULTI_SECTOR_V_SHAPE":
            # V-Shaped Wedge Net for flank & multi-axis interception
            arm_len = num_drones // 2
            v_angle = np.radians(45.0)
            for i in range(arm_len):
                # Left Arm
                nodes[i] = self.base_center + np.array([
                    i * 3.0 * np.cos(v_angle),
                    i * 3.0 * np.sin(v_angle),
                    (i % 5) * 5.0
                ])
                # Right Arm
                nodes[arm_len + i] = self.base_center + np.array([
                    i * 3.0 * np.cos(-v_angle),
                    i * 3.0 * np.sin(-v_angle),
                    (i % 5) * 5.0
                ])

        else:  # DIRECTIONAL_STAGGERED_WALL
            # Planar 2-Layer Staggered Grid Wall facing primary threat azimuth
            primary_azimuth = threat_vectors[0].azimuth_deg if threat_vectors else 0.0
            az_rad = np.radians(primary_azimuth)
            normal = np.array([np.cos(az_rad), np.sin(az_rad), 0.0])
            u = np.array([-np.sin(az_rad), np.cos(az_rad), 0.0])
            v = np.array([0.0, 0.0, 1.0])

            rows, cols = 5, 5
            for layer in range(2):
                l_offset = layer * (-6.0)
                stagger = 3.5 if layer == 1 else 0.0
                for r in range(rows):
                    for c in range(cols):
                        idx = layer * (rows * cols) + r * cols + c
                        if idx < num_drones:
                            nodes[idx] = self.base_center + normal * (radius_m + l_offset) + u * ((c - 2) * 7.0 + stagger) + v * ((r - 2) * 7.0)

        return nodes, net_mode
