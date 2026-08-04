from typing import List
import numpy as np
from src.simulator.drone import Drone
from src.simulator.threat import Threat

class SimulationEnvironment:
    def __init__(self, time_step: float = 0.05):
        self.dt = time_step
        self.current_time = 0.0
        self.drones: List[Drone] = []
        self.threats: List[Threat] = []
        self.kill_log: List[dict] = []

    def add_drone(self, drone: Drone):
        self.drones.append(drone)

    def add_threat(self, threat: Threat):
        self.threats.append(threat)

    def kill_drone(self, drone_id: int):
        """Simulate drone failure or destruction by external factor/threat."""
        for d in self.drones:
            if d.id == drone_id and d.status == "active":
                d.status = "destroyed"
                self.kill_log.append({
                    "time": self.current_time,
                    "drone_id": drone_id,
                    "position": d.position.copy()
                })
                break

    def step(self, drone_control_signals: dict):
        """
        Advances physics by self.dt.
        drone_control_signals: dict mapping drone.id -> desired_accel (np.ndarray of shape (3,))
        """
        # 1. Update threat physics
        for threat in self.threats:
            threat.update_physics(self.dt)

        # 2. Update active drones physics
        for drone in self.drones:
            if drone.status == "active":
                accel = drone_control_signals.get(drone.id, np.zeros(3))
                drone.update_physics(accel, self.dt)

        # 3. Check collision / interception between active drones and threats
        for threat in self.threats:
            if threat.status != "approaching":
                continue
            for drone in self.drones:
                if drone.status == "active":
                    dist = drone.distance_to(threat.position)
                    if dist <= threat.radius:
                        threat.status = "intercepted"
                        drone.status = "intercepted"
                        self.kill_log.append({
                            "time": self.current_time,
                            "event": "INTERCEPTION",
                            "drone_id": drone.id,
                            "threat_id": threat.id,
                            "position": drone.position.copy()
                        })

        self.current_time += self.dt
