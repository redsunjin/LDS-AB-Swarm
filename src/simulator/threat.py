import numpy as np
from dataclasses import dataclass, field

@dataclass
class Threat:
    id: int
    position: np.ndarray  # shape (3,) [x, y, z]
    velocity: np.ndarray  # shape (3,) [vx, vy, vz]
    radius: float = 1.0   # Physical/Lethal interaction radius in meters
    status: str = "approaching"  # "approaching", "intercepted", "escaped"

    def update_physics(self, dt: float):
        """Simple kinematic update for the threat."""
        if self.status == "approaching":
            self.position += self.velocity * dt

    def get_predicted_position(self, time_ahead: float) -> np.ndarray:
        """Linear extrapolation of threat position."""
        return self.position + self.velocity * time_ahead
