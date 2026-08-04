import numpy as np
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Drone:
    id: int
    position: np.ndarray  # shape (3,) [x, y, z] in meters
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))  # shape (3,) [vx, vy, vz]
    target_position: Optional[np.ndarray] = None  # Assigned grid node target
    max_speed: float = 35.0  # m/s (High thrust FPV style)
    max_accel: float = 20.0  # m/s^2
    status: str = "active"   # "active", "destroyed", "intercepted"
    uwb_range: float = 60.0  # UWB communication limit in meters

    def update_physics(self, desired_accel: np.ndarray, dt: float):
        """Updates drone position and velocity based on desired acceleration and kinematic constraints."""
        if self.status != "active":
            self.velocity = np.zeros(3)
            return

        # Cap acceleration
        accel_mag = np.linalg.norm(desired_accel)
        if accel_mag > self.max_accel and accel_mag > 1e-6:
            desired_accel = (desired_accel / accel_mag) * self.max_accel

        # Velocity update
        self.velocity += desired_accel * dt
        
        # Cap speed
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed and speed > 1e-6:
            self.velocity = (self.velocity / speed) * self.max_speed

        # Position update
        self.position += self.velocity * dt

    def distance_to(self, other_pos: np.ndarray) -> float:
        """Returns Euclidean distance to a target position vector."""
        return float(np.linalg.norm(self.position - other_pos))
