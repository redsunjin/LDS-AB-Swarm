import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class HighValueAsset:
    asset_id: str
    name: str
    tier: int              # Tier 1 (Critical C2 Bunker), Tier 2 (Radar), Tier 3 (Supply Yard)
    position: np.ndarray   # 3D position [X, Y, Z]
    priority_weight: float # Tier 1 = 1.0, Tier 2 = 0.8, Tier 3 = 0.5
    defense_radius_m: float = 25.0

@dataclass
class LauncherBattery:
    battery_id: str
    battery_type: str      # "FIXED_CANISTER", "MOBILE_TACTICAL_VEHICLE"
    position: np.ndarray   # 3D Position [X, Y, Z]
    canister_capacity: int = 25
    canisters_remaining: int = 25
    ejection_velocity: float = 22.0  # m/s

class TacticalAssetProtectionEngine:
    """
    Tactical Asset Protection & Operational Geometry Engine.
    Handles:
      1. HVA Asset Priority Tiers (Tier 1/2/3)
      2. Launcher Battery Deployment Coords
      3. Swarm Transit Kinematics (Launch -> Barrier Mesh Transit Time)
      4. Topographic Threat Vector Geometry (Plunging Dive vs Valley Lateral Corridor)
    """
    def __init__(self):
        # 1. Define High-Value Protected Assets (HVA Tiers)
        self.hva_list: List[HighValueAsset] = [
            HighValueAsset("HVA-01", "Tier 1 Command Underground Bunker", tier=1, position=np.array([10.0, 0.0, 2.0]), priority_weight=1.0, defense_radius_m=30.0),
            HighValueAsset("HVA-02", "Tier 2 Strategic C2 Radar Array", tier=2, position=np.array([15.0, 12.0, 4.0]), priority_weight=0.8, defense_radius_m=20.0),
            HighValueAsset("HVA-03", "Tier 3 Tactical Ammunition Depot", tier=3, position=np.array([18.0, -15.0, 2.0]), priority_weight=0.5, defense_radius_m=15.0)
        ]

        # 2. Define Launcher Battery Locations
        self.launcher_batteries: List[LauncherBattery] = [
            LauncherBattery("BATTERY-ALPHA", "FIXED_CANISTER", position=np.array([25.0, -10.0, 1.0]), canister_capacity=25),
            LauncherBattery("BATTERY-BRAVO", "MOBILE_TACTICAL_VEHICLE", position=np.array([25.0, 10.0, 1.0]), canister_capacity=25)
        ]

    def compute_asset_biased_barrier_center(self, threat_position: np.ndarray) -> np.ndarray:
        """
        Biases barrier center location based on HVA Tier priorities to protect Tier 1 assets first.
        """
        total_weight = sum(hva.priority_weight for hva in self.hva_list)
        weighted_center = np.zeros(3)
        for hva in self.hva_list:
            weighted_center += hva.position * hva.priority_weight
        weighted_center /= total_weight

        # Offset barrier center toward incoming threat relative to HVA weighted center
        threat_direction = threat_position - weighted_center
        dist = np.linalg.norm(threat_direction)
        if dist > 1e-3:
            threat_direction /= dist

        return weighted_center + threat_direction * 25.0

    def classify_threat_approach_geometry(self, threat_pos: np.ndarray, threat_vel: np.ndarray) -> str:
        """
        Classifies threat approach vector based on terrain topography:
          - "STEEP_DIVE_PLUNGING": High altitude mountain dive-bombing -> Horizontal Top-Cover Umbrella
          - "VALLEY_LOW_CORRIDOR": Low altitude mountain valley corridor -> Vertical Lateral Wall
          - "STANDARD_HORIZONTAL": Direct horizontal approach -> Standard Multi-Layer Mesh
        """
        speed = np.linalg.norm(threat_vel)
        if speed < 1e-3:
            return "STANDARD_HORIZONTAL"

        v_unit = threat_vel / speed
        pitch_angle_deg = np.degrees(np.arcsin(v_unit[2]))

        if pitch_angle_deg < -25.0:
            return "STEEP_DIVE_PLUNGING"
        elif threat_pos[2] < 15.0:
            return "VALLEY_LOW_CORRIDOR"
        else:
            return "STANDARD_HORIZONTAL"

    def calculate_swarm_transit_time(self, drone_pos: np.ndarray, target_node: np.ndarray, max_speed: float = 40.0) -> float:
        """
        Calculates physical transit time for drone from launch pad / current position to assigned 3D mesh node.
        """
        dist = np.linalg.norm(target_node - drone_pos)
        return dist / max(1.0, max_speed)
