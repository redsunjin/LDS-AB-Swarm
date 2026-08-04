import numpy as np
from typing import List, Tuple
from src.simulator.threat import Threat
from src.core.mesh_generator import ThreatTrajectory

class ThreatFactory:
    """
    Factory for constructing diverse threat types and multi-threat saturation scenarios.
    """
    @staticmethod
    def create_cruise_missile(threat_id: int = 101, 
                              start_pos: Tuple[float, float, float] = (180.0, 0.0, 30.0), 
                              speed: float = 40.0) -> Tuple[Threat, ThreatTrajectory]:
        """Creates a high-speed linear Cruise Missile threat."""
        pos_arr = np.array(start_pos, dtype=np.float64)
        vel_arr = np.array([-speed, 0.0, 0.0], dtype=np.float64)
        
        trajectory = ThreatTrajectory.create_linear(pos_arr, vel_arr)
        threat = Threat(id=threat_id, position=pos_arr, velocity=vel_arr, radius=2.5)
        return threat, trajectory

    @staticmethod
    def create_weaving_kamikaze(threat_id: int = 102, 
                                start_pos: Tuple[float, float, float] = (180.0, 0.0, 35.0), 
                                speed: float = 30.0, 
                                amplitude: float = 12.0) -> Tuple[Threat, ThreatTrajectory]:
        """Creates an evasive S-curve weaving Kamikaze Drone threat."""
        pos_arr = np.array(start_pos, dtype=np.float64)
        v_base = np.array([-speed, 0.0, 0.0], dtype=np.float64)

        trajectory = ThreatTrajectory.create_weaving_sinusoidal(pos_arr, v_base, amplitude=amplitude, freq=1.2)
        threat = Threat(id=threat_id, position=pos_arr, velocity=v_base, radius=2.5)
        return threat, trajectory

    @staticmethod
    def create_saturation_attack() -> List[Tuple[Threat, ThreatTrajectory]]:
        """
        Creates a Multi-Threat Saturation Attack scenario with 3 threats approaching simultaneously
        from different angles and trajectories.
        """
        threats = []

        # Threat 1: High speed Cruise Missile from East
        t1, traj1 = ThreatFactory.create_cruise_missile(
            threat_id=101, start_pos=(180.0, -25.0, 25.0), speed=35.0
        )

        # Threat 2: Weaving Kamikaze Drone from East-North
        t2, traj2 = ThreatFactory.create_weaving_kamikaze(
            threat_id=102, start_pos=(180.0, 25.0, 35.0), speed=28.0, amplitude=10.0
        )

        # Threat 3: Angled Low-Altitude Attack Drone
        pos3 = np.array([160.0, 0.0, 15.0])
        vel3 = np.array([-30.0, 0.0, 0.0])
        traj3 = ThreatTrajectory.create_linear(pos3, vel3)
        t3 = Threat(id=103, position=pos3, velocity=vel3, radius=2.5)

        threats.append((t1, traj1))
        threats.append((t2, traj2))
        threats.append((t3, traj3))

        return threats
